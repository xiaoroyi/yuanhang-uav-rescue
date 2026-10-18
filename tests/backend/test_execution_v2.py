"""Actual worker + persistent simulation + commitment repair integration tests."""

import copy
from datetime import datetime, timedelta, timezone
import time

from fastapi.testclient import TestClient
import pytest

from backend.app.main import create_app


def post(c, path, data, status=200):
    r = c.post("/api/v1" + path, json=data)
    assert r.status_code == status, r.text
    return r.json()


def await_job(c, job):
    for _ in range(350):
        job = c.get("/api/v1/solve-jobs/" + job["job_id"]).json()
        if job["job_state"] not in ("queued", "running"):
            return job
        time.sleep(0.05)
    raise AssertionError(job)


def setup(c, configure=None):
    m = post(
        c,
        "/missions",
        {
            "name": "Execution contract test",
            "template": "compact",
            "idempotency_key": "create",
        },
        201,
    )
    s = c.get("/api/v1/scenarios/" + m["current_scenario_id"]).json()
    # Keep one available entity at the base for the in-flight future-failure scenario.
    s["drones"][-1]["available_after_s"] = 20000
    if configure:
        configure(s)
    r = c.put(
        "/api/v1/scenarios/" + s["scenario_id"],
        json={"expected_state_version": 1, "scenario": s},
    )
    assert r.status_code == 200, r.text
    s = r.json()
    snap = post(
        c,
        f"/scenarios/{s['scenario_id']}/snapshots",
        {"expected_state_version": 2},
        201,
    )
    job = await_job(
        c,
        post(
            c,
            "/solve-jobs",
            {
                "snapshot_id": snap["snapshot_id"],
                "time_limit_s": 5,
                "objective_policy": "tradeoff_v2",
            },
            202,
        ),
    )
    assert job["has_validated_plan"], job
    p = c.get("/api/v1/plans/" + job["plan_id"]).json()
    post(
        c,
        f"/plans/{p['plan_id']}/confirm",
        {"expected_state_version": 2, "idempotency_key": "confirm"},
    )
    e = post(
        c,
        "/executions",
        {
            "mission_id": m["mission_id"],
            "confirmed_plan_id": p["plan_id"],
            "expected_revision": 1,
            "idempotency_key": "exec",
        },
        201,
    )
    return m, s, p, e


def act(c, e, kind, **options):
    return post(
        c,
        f"/executions/{e['execution_id']}/simulation/actions",
        {
            "action": kind,
            "expected_revision": e["revision"],
            "idempotency_key": f"{kind}-{e['revision']}",
            **options,
        },
    )


def test_simulation_clock_refresh_idempotence_reconnect_and_commands(tmp_path):
    directory = tmp_path / "runtime"
    with TestClient(create_app(directory)) as c:
        m, s, p, e = setup(c)
        assert c.get("/api/v1/executions/" + e["execution_id"]).json()["facts"] == []
        e = act(c, e, "start")
        time.sleep(0.1)
        e = act(c, e, "pause")
        first = (
            min(v["delivery_complete_s"] for r in p["sorties"] for v in r["visits"]) + 1
        )
        e = act(c, e, "advance", target_time_s=first)
        assert e["delivered_cargo_ids"]
        paused = c.get("/api/v1/executions/" + e["execution_id"]).json()
        time.sleep(0.1)
        same = c.get("/api/v1/executions/" + e["execution_id"]).json()
        assert paused["time_s"] == same["time_s"] and paused["facts"] == same["facts"]
        assert (
            same["telemetry"][0]["device_sequence"]
            > paused["telemetry"][0]["device_sequence"]
        )
        assert len({f["fact_id"] for f in same["facts"]}) == same["facts_cursor"]
        old_position = {x["device_id"]: x["coordinates"] for x in e["telemetry"]}
        e = act(c, e, "disconnect")
        e = act(c, e, "advance", target_time_s=first + 100)
        assert all(
            x["quality"] == "stale" and x["coordinates"] == old_position[x["device_id"]]
            for x in e["telemetry"]
        )
        old_session = e["telemetry"][0]["device_session_id"]
        e = act(c, e, "reconnect")
        assert e["telemetry"][0]["device_session_id"] != old_session
        expires = (datetime.now(timezone.utc) + timedelta(seconds=30)).isoformat()
        command = {
            "execution_id": e["execution_id"],
            "device_id": s["drones"][0]["drone_id"],
            "command_type": "mission.upload",
            "desired_plan_id": p["plan_id"],
            "expected_execution_revision": e["revision"],
            "idempotency_key": "cmd-1",
            "expires_at": expires,
            "simulation_fault": "ack_timeout",
        }
        cmd = post(c, "/commands", command, 202)
        assert cmd["status"] == "queued" and cmd["completed_at"] is None
        assert post(c, "/commands", command, 202) == cmd
        assert (
            c.post(
                "/api/v1/commands", json={**command, "device_id": "UNKNOWN"}
            ).status_code
            == 409
        )
        time.sleep(0.9)
        unknown = c.get("/api/v1/commands/" + cmd["command_id"]).json()
        assert unknown["status"] == "indeterminate" and unknown["completed_at"] is None
        completion = post(
            c,
            "/commands",
            {
                **command,
                "idempotency_key": "completion-timeout",
                "simulation_fault": "completion_timeout",
            },
            202,
        )
        rejected = post(
            c,
            "/commands",
            {**command, "idempotency_key": "rejected", "simulation_fault": "reject"},
            202,
        )
        expired = post(
            c,
            "/commands",
            {
                **command,
                "idempotency_key": "short-ttl",
                "simulation_fault": "none",
                "expires_at": (
                    datetime.now(timezone.utc) + timedelta(seconds=0.2)
                ).isoformat(),
            },
            202,
        )
        assert (
            c.post(
                "/api/v1/commands",
                json={**command, "idempotency_key": "actor", "actor": "administrator"},
            ).status_code
            == 422
        )
        assert (
            c.post(
                "/api/v1/commands",
                json={
                    **command,
                    "idempotency_key": "foreign",
                    "device_id": "FOREIGN-DEVICE",
                },
            ).status_code
            == 403
        )
        time.sleep(0.9)
        state = c.get("/api/v1/commands/" + completion["command_id"]).json()
        assert (
            state["status"] in ("acknowledged", "indeterminate")
            and state["acknowledged_at"] is not None
            and state["completed_at"] is None
        )
        time.sleep(0.5)
        state = c.get("/api/v1/commands/" + completion["command_id"]).json()
        assert (
            state["status"] == "indeterminate"
            and state["acknowledged_at"] is not None
            and state["completed_at"] is None
        )
        assert (
            c.get("/api/v1/commands/" + rejected["command_id"]).json()["status"]
            == "rejected"
        )
        expiry = c.get("/api/v1/commands/" + expired["command_id"]).json()
        assert (
            expiry["status"] in ("expired", "indeterminate")
            and expiry["completed_at"] is None
        )
        bad = {
            **command,
            "idempotency_key": "cmd-bad",
            "expected_execution_revision": e["revision"] - 1,
        }
        assert c.post("/api/v1/commands", json=bad).status_code == 409
        assert (
            c.post(
                "/api/v1/commands",
                json={**command, "idempotency_key": "cmd-real", "mode": "real"},
            ).status_code
            == 422
        )
        saved = c.get("/api/v1/executions/" + e["execution_id"]).json()
    with TestClient(create_app(directory)) as c:
        restored = c.get("/api/v1/executions/" + e["execution_id"]).json()
        assert (
            restored["time_s"] == saved["time_s"]
            and restored["facts"] == saved["facts"]
        )


def test_inflight_repair_preserves_facts_and_resource_release(tmp_path):
    with TestClient(create_app(tmp_path / "runtime")) as c:
        m, s, p, e = setup(c)
        first = (
            min(v["delivery_complete_s"] for r in p["sorties"] for v in r["visits"]) + 1
        )
        e = act(c, e, "advance", target_time_s=first)
        assert any(
            x["phase"] in ("climb", "cruise", "descent", "handover")
            for x in e["telemetry"]
        )
        delivered = list(e["delivered_cargo_ids"])
        facts = copy.deepcopy(e["facts"])
        failure = {
            "event_id": "future-failure",
            "expected_revision": e["revision"],
            "event_type": "drone.unavailable",
            "object_id": s["drones"][-1]["drone_id"],
            "reason": "future entity unavailable",
        }
        event = post(c, f"/executions/{e['execution_id']}/events", failure, 201)
        assert event["status"] == "recorded"
        assert post(c, f"/executions/{e['execution_id']}/events", failure, 201) == event
        assert (
            c.post(
                f"/api/v1/executions/{e['execution_id']}/events",
                json={**failure, "reason": "different"},
            ).status_code
            == 409
        )
        e = c.get("/api/v1/executions/" + e["execution_id"]).json()
        extra = {
            "demand_id": "DYNAMIC-1",
            "site_id": s["sites"][0]["id"],
            "cargo_type": "medical",
            "required_quantity": 1,
            "priority": 1,
            "expected_deadline_s": None,
            "hard_deadline_s": None,
            "mandatory": True,
        }
        cargo = {
            "cargo_id": "BOX-NEW",
            "demand_id": "DYNAMIC-1",
            "type": "medical",
            "mass_kg": 1,
            "volume_l": 1,
            "status": "available",
            "location_id": s["base"]["id"],
        }
        post(
            c,
            f"/executions/{e['execution_id']}/events",
            {
                "event_id": "urgent",
                "expected_revision": e["revision"],
                "event_type": "demand.added",
                "demand": extra,
                "cargo_items": [cargo],
                "reason": "explicit new stock",
            },
            201,
        )
        e = c.get("/api/v1/executions/" + e["execution_id"]).json()
        change = post(
            c,
            f"/executions/{e['execution_id']}/replan-jobs",
            {
                "expected_revision": e["revision"],
                "idempotency_key": "repair",
                "time_limit_s": 3,
            },
            202,
        )
        assert change["committed_cargo_ids"] and set(delivered) <= set(
            change["committed_cargo_ids"]
        )
        job = await_job(c, change["job"])
        assert job["has_validated_plan"], job
        change = c.get(
            f"/api/v1/executions/{e['execution_id']}/plan-changes/{change['change_id']}"
        ).json()
        assert change["status"] == "ready"
        candidate = c.get("/api/v1/plans/" + change["candidate_plan_id"]).json()
        assert all(
            r["prepare_start_s"] >= change["future_not_before_s"]
            for r in candidate["sorties"]
        )
        assert not set(change["committed_cargo_ids"]) & {
            x for r in candidate["sorties"] for x in r["cargo_ids"]
        }
        assert all(
            r["drone_id"] != s["drones"][-1]["drone_id"] for r in candidate["sorties"]
        )
        applied = post(
            c,
            f"/executions/{e['execution_id']}/plan-changes/{change['change_id']}/apply",
            {"expected_revision": e["revision"], "idempotency_key": "apply"},
        )
        assert applied["status"] == "applying" and all(
            a["activation_state"] == "not_started" for a in applied["applications"]
        )
        for _ in range(60):
            applied = c.get(
                f"/api/v1/executions/{e['execution_id']}/plan-changes/{change['change_id']}"
            ).json()
            if applied["status"] != "applying":
                break
            time.sleep(0.05)
        assert applied["status"] == "applied" and all(
            a["activation_state"] == "active" for a in applied["applications"]
        )
        after = c.get("/api/v1/executions/" + e["execution_id"]).json()
        assert after["facts"] == facts and set(delivered) <= set(
            after["delivered_cargo_ids"]
        )
        assert c.get("/api/v1/plans/" + p["plan_id"]).json() == p
        finish = max(r["battery_released_s"] for r in candidate["sorties"]) + 1
        after = act(c, after, "advance", target_time_s=finish)
        assert "BOX-NEW" in after["delivered_cargo_ids"]
        assert after["status"] == "completed"
        assert len(after["delivered_cargo_ids"]) == len(s["cargo_items"]) + 1
        summary = c.get(f"/api/v1/executions/{e['execution_id']}/analysis").json()
        assert summary["delivered_quantity"] == 33 and summary["unserved_quantity"] == 0
        bundle = c.get(f"/api/v1/executions/{e['execution_id']}/export?version=2")
        assert bundle.status_code == 200, bundle.text
        bundle = bundle.json()
        assert len([d for d in bundle["documents"] if d["kind"] == "plan"]) >= 2
        assert len([d for d in bundle["documents"] if d["kind"] == "snapshot"]) >= 2
        import json

        archive = c.post(
            "/api/v1/execution-archives/import",
            files={
                "file": (
                    "multi-source.json",
                    json.dumps(bundle).encode(),
                    "application/json",
                )
            },
        )
        assert archive.status_code == 201, archive.text
        saved = c.get(
            "/api/v1/execution-archives/" + archive.json()["archive_id"]
        ).json()
        assert saved["analysis"] == summary
        assert saved["bundle"]["execution"]["facts"] == after["facts"]
        assert (
            next(r for r in summary["deviation_rows"] if r["cargo_id"] == "BOX-NEW")[
                "difference_s"
            ]
            is None
        )


def test_partial_device_apply_retains_schedule_and_stale_candidate_rejected(tmp_path):
    with TestClient(create_app(tmp_path / "runtime")) as c:
        m, s, p, e = setup(c)
        e = act(
            c,
            e,
            "advance",
            target_time_s=min(
                v["delivery_complete_s"] for r in p["sorties"] for v in r["visits"]
            )
            + 1,
        )
        event = {
            "event_id": "future",
            "expected_revision": e["revision"],
            "event_type": "drone.unavailable",
            "object_id": s["drones"][-1]["drone_id"],
            "reason": "do not dispatch future aircraft",
        }
        post(c, f"/executions/{e['execution_id']}/events", event, 201)
        e = c.get("/api/v1/executions/" + e["execution_id"]).json()
        before = copy.deepcopy(e["schedule_parts"])
        change = post(
            c,
            f"/executions/{e['execution_id']}/replan-jobs",
            {
                "expected_revision": e["revision"],
                "idempotency_key": "one",
                "time_limit_s": 3,
            },
            202,
        )
        assert await_job(c, change["job"])["has_validated_plan"]
        endpoint = f"/executions/{e['execution_id']}/plan-changes/{change['change_id']}"
        applied = post(
            c,
            endpoint + "/apply",
            {
                "expected_revision": e["revision"],
                "idempotency_key": "timeout",
                "ack_timeout_device_ids": [s["drones"][0]["drone_id"]],
            },
        )
        assert applied["status"] == "applying"
        time.sleep(1.3)
        partial = c.get("/api/v1" + endpoint).json()
        assert partial["status"] == "partially_applied"
        assert any(
            a["upload_state"] == "indeterminate" for a in partial["applications"]
        )
        assert not any(
            a["activation_state"] == "active" for a in partial["applications"]
        )
        unchanged = c.get("/api/v1/executions/" + e["execution_id"]).json()
        assert (
            unchanged["schedule_parts"] == before and unchanged["facts"] == e["facts"]
        )
        change = post(
            c,
            f"/executions/{e['execution_id']}/replan-jobs",
            {
                "expected_revision": e["revision"],
                "idempotency_key": "two",
                "time_limit_s": 3,
            },
            202,
        )
        assert await_job(c, change["job"])["has_validated_plan"]
        moved = act(c, e, "speed", speed=5)
        stale = c.post(
            f"/api/v1/executions/{e['execution_id']}/plan-changes/{change['change_id']}/apply",
            json={"expected_revision": moved["revision"], "idempotency_key": "stale"},
        )
        assert stale.status_code == 409


def test_missing_stock_and_committed_failure_are_not_silently_rewritten(tmp_path):
    with TestClient(create_app(tmp_path / "runtime")) as c:
        m, s, p, e = setup(c)
        e = act(c, e, "advance", target_time_s=1)
        loaded = next(r for r in p["sorties"] if r["prepare_start_s"] <= 1)
        ev = post(
            c,
            f"/executions/{e['execution_id']}/events",
            {
                "event_id": "loaded",
                "expected_revision": e["revision"],
                "event_type": "drone.unavailable",
                "object_id": loaded["drone_id"],
                "reason": "already loaded entity cannot teleport cargo",
            },
            201,
        )
        assert ev["status"] == "requires_manual"
        e = c.get("/api/v1/executions/" + e["execution_id"]).json()
        blocked = c.post(
            f"/api/v1/executions/{e['execution_id']}/replan-jobs",
            json={"expected_revision": e["revision"], "idempotency_key": "blocked"},
        )
        assert (
            blocked.status_code == 422
            and blocked.json()["error"]["code"] == "COMMITMENT_REQUIRES_MANUAL"
        )
        demand = {
            "demand_id": "NO-STOCK",
            "site_id": s["sites"][0]["id"],
            "cargo_type": "MED",
            "required_quantity": 2,
            "priority": 1,
            "expected_deadline_s": None,
            "hard_deadline_s": None,
            "mandatory": True,
        }
        ev = post(
            c,
            f"/executions/{e['execution_id']}/events",
            {
                "event_id": "no-stock",
                "expected_revision": e["revision"],
                "event_type": "demand.added",
                "demand": demand,
                "cargo_items": [],
                "reason": "new demand without stock",
            },
            201,
        )
        assert ev["missing_inventory"] == 2
        assert c.get("/api/v1/plans/" + p["plan_id"]).json() == p


def test_inflight_weather_event_uses_real_repair_and_protects_unsafe_commitments(
    tmp_path,
):
    from pathlib import Path
    import json

    weather = json.loads(
        (
            Path(__file__).resolve().parents[2]
            / "fixtures/operations/weather-manual.json"
        ).read_text(encoding="utf-8")
    )["weather"]
    with TestClient(create_app(tmp_path / "runtime")) as c:
        m, s, p, e = setup(c)
        first = (
            min(v["delivery_complete_s"] for r in p["sorties"] for v in r["visits"]) + 1
        )
        e = act(c, e, "advance", target_time_s=first)
        facts = copy.deepcopy(e["facts"])
        weather.update(valid_from_s=0, valid_until_s=100000, wind_speed_mps=1)
        template = copy.deepcopy(weather["rules"][0])
        weather["rules"] = [
            {**template, "type_id": t["type_id"], "max_wind_mps": 20}
            for t in s["drone_types"]
        ]
        body = {
            "event_id": "weather-safe",
            "expected_revision": e["revision"],
            "event_type": "weather.changed",
            "weather": weather,
            "reason": "Synthetic W1 exercise",
        }
        mixed = c.post(
            f"/api/v1/executions/{e['execution_id']}/events",
            json={**body, "object_id": s["drones"][0]["drone_id"]},
        )
        assert mixed.status_code == 422
        ev = post(c, f"/executions/{e['execution_id']}/events", body, 201)
        assert ev["status"] == "recorded" and ev["weather"] == weather
        e = c.get("/api/v1/executions/" + e["execution_id"]).json()
        assert e["facts"] == facts
        change = post(
            c,
            f"/executions/{e['execution_id']}/replan-jobs",
            {
                "expected_revision": e["revision"],
                "idempotency_key": "weather-repair",
                "time_limit_s": 5,
            },
            202,
        )
        job = await_job(c, change["job"])
        assert job["has_validated_plan"], job
        candidate = c.get("/api/v1/plans/" + job["plan_id"]).json()
        assert "weather_window" in candidate["model_scope"]
        assert not (
            set(change["committed_cargo_ids"])
            & {box for r in candidate["sorties"] for box in r["cargo_ids"]}
        )
        assert c.get("/api/v1/plans/" + p["plan_id"]).json() == p
        # A later update cannot teleport an already started aircraft through unsafe weather.
        unsafe = copy.deepcopy(weather)
        unsafe["wind_speed_mps"] = 30
        ev = post(
            c,
            f"/executions/{e['execution_id']}/events",
            {
                **body,
                "event_id": "weather-unsafe",
                "expected_revision": e["revision"],
                "weather": unsafe,
            },
            201,
        )
        assert ev["status"] == "requires_manual"
        e = c.get("/api/v1/executions/" + e["execution_id"]).json()
        assert e["facts"] == facts
        response = c.post(
            f"/api/v1/executions/{e['execution_id']}/replan-jobs",
            json={
                "expected_revision": e["revision"],
                "idempotency_key": "unsafe-repair",
            },
        )
        assert (
            response.status_code == 422
            and response.json()["error"]["code"] == "COMMITMENT_REQUIRES_MANUAL"
        )


def test_misreport_resolution_preserves_event_input_and_facts_and_stream_cursor(
    tmp_path,
):
    import asyncio
    import json
    from backend.app.storage import OperationRecordRow

    app = create_app(tmp_path / "runtime")
    with TestClient(app) as c:
        m, s, p, e = setup(c)
        e = act(c, e, "advance", target_time_s=1)
        before = copy.deepcopy(e["facts"])
        row = next(r for r in p["sorties"] if r["prepare_start_s"] <= 1)
        raw = {
            "event_id": "misreport",
            "expected_revision": e["revision"],
            "event_type": "drone.unavailable",
            "object_id": row["drone_id"],
            "reason": "Mistaken exercise report",
        }
        event = post(c, f"/executions/{e['execution_id']}/events", raw, 201)
        assert event["status"] == "requires_manual"
        e = c.get("/api/v1/executions/" + e["execution_id"]).json()
        for action in ("advance", "resume"):
            response = c.post(
                f"/api/v1/executions/{e['execution_id']}/simulation/actions",
                json={
                    "action": action,
                    "expected_revision": e["revision"],
                    "idempotency_key": action,
                    "target_time_s": 100,
                },
            )
            assert (
                response.status_code == 409
                and response.json()["error"]["code"] == "PENDING_EVENTS"
            )
        endpoint = f"/executions/{e['execution_id']}/events/misreport/resolve"
        body = {
            "expected_revision": e["revision"],
            "idempotency_key": "resolve",
            "action": "withdraw_misreport",
            "reason": "Exercise operator rechecked that the device is functioning",
        }
        resolved = post(c, endpoint, body)
        assert resolved["status"] == "withdrawn"
        assert post(c, endpoint, body) == resolved
        assert (
            c.post(
                "/api/v1" + endpoint,
                json={**body, "reason": "Changed payload is not the same resolution"},
            ).status_code
            == 409
        )
        e = c.get("/api/v1/executions/" + e["execution_id"]).json()
        assert e["facts"] == before and e["revision"] == body["expected_revision"] + 1
        assert (
            c.get(f"/api/v1/executions/{e['execution_id']}/events").json()[0]["status"]
            == "withdrawn"
        )
        # The append-only original event record remains unchanged by the correction.
        with app.state.database.session() as session:
            stored = session.get(
                OperationRecordRow,
                ("execution.event", e["execution_id"] + ":misreport"),
            ).content
            assert (
                stored["status"] == "requires_manual"
                and stored["reason"] == raw["reason"]
            )
        e = act(c, e, "resume")
        e = act(c, e, "pause")
        e = act(c, e, "advance", target_time_s=2)
        # Exercise the real stream endpoint generator without an infinite HTTP client read.
        stream = next(
            route.endpoint
            for route in app.routes
            if getattr(route, "path", "") == "/api/v1/executions/{execution_id}/stream"
        )

        class Connection:
            query_params = {"cursor": "0"}
            headers = {}

            async def is_disconnected(self):
                return False

        async def packet(cursor):
            response = await stream(e["execution_id"], Connection(), cursor)
            generator = response.body_iterator
            item = await anext(generator)
            await generator.aclose()
            return json.loads(item.split("data: ", 1)[1])

        first = asyncio.run(packet(0))
        assert [v["cursor"] for v in first["facts"]] == list(
            range(1, e["facts_cursor"] + 1)
        )
        reconnect = asyncio.run(packet(first["facts_cursor"]))
        assert (
            reconnect["facts"] == []
            and reconnect["facts_cursor"] == first["facts_cursor"]
        )
        assert (
            c.get(
                f"/api/v1/executions/{e['execution_id']}/stream?cursor={e['facts_cursor']+1}"
            ).status_code
            == 409
        )
        assert (
            c.get(
                f"/api/v1/executions/{e['execution_id']}/stream?cursor=-1"
            ).status_code
            == 422
        )
