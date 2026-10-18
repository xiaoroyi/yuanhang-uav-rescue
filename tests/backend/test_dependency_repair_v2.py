"""Dependency repair uses real frozen sources, then independently checks the full suffix."""

import copy
import hashlib
import json
import time

from fastapi.testclient import TestClient

from backend.app.execution_archive import seal
from backend.app.main import create_app
from backend.app.storage import OperationRecordRow, JobRow, PlanRow, SnapshotRow
from solver.public_api import repair_remaining, validate
from test_execution_v2 import setup, post, act, await_job


def change(c, execution, key, policy="dependency", budget=8):
    result = post(
        c,
        f"/executions/{execution['execution_id']}/replan-jobs",
        {
            "expected_revision": execution["revision"],
            "idempotency_key": key,
            "time_limit_s": budget,
            "repair_policy": policy,
        },
        202,
    )
    if result["job"]:
        job = await_job(c, result["job"])
        assert job["has_validated_plan"], job
    return c.get(
        f"/api/v1/executions/{execution['execution_id']}/plan-changes/{result['change_id']}"
    ).json()


def wait_applied(c, e, item):
    post(
        c,
        f"/executions/{e['execution_id']}/plan-changes/{item['change_id']}/apply",
        {
            "expected_revision": e["revision"],
            "idempotency_key": "apply-" + item["change_id"],
        },
    )
    for _ in range(100):
        result = c.get(
            f"/api/v1/executions/{e['execution_id']}/plan-changes/{item['change_id']}"
        ).json()
        if result["status"] != "applying":
            return result
        time.sleep(0.05)
    raise AssertionError(result)


def test_local_suffix_retains_future_rows_and_same_snapshot_full_baseline_is_real(
    tmp_path,
):
    app = create_app(tmp_path / "runtime")
    with TestClient(app) as c:
        _, s, p, e = setup(c)
        e = act(c, e, "advance", target_time_s=1)
        post(
            c,
            f"/executions/{e['execution_id']}/events",
            {
                "event_id": "idle-exit",
                "expected_revision": e["revision"],
                "event_type": "drone.unavailable",
                "object_id": s["drones"][-1]["drone_id"],
                "reason": "Unused future fleet entity exits",
            },
            201,
        )
        e = c.get("/api/v1/executions/" + e["execution_id"]).json()
        local = change(c, e, "local")
        assert local["calculation_method"] == "dependency_local" and local["diff"]
        expected = [r for r in p["sorties"] if r["prepare_start_s"] > 1]
        assert local["diff"]["retained_future_sortie_count"] == len(expected)
        assert local["diff"]["drone_reassigned_quantity"] == 0
        assert local["diff"]["time_shifted_quantity"] == 0
        assert local["diff"]["unchanged_future_quantity"] == sum(
            len(r["cargo_ids"]) for r in expected
        )
        with app.state.database.session() as session:
            reference = copy.deepcopy(
                session.get(
                    OperationRecordRow,
                    ("solver.repair.reference", local["repair_reference_id"]),
                ).content
            )
            snap = copy.deepcopy(
                session.get(SnapshotRow, local["job"]["snapshot_id"]).content
            )
            options = copy.deepcopy(session.get(JobRow, local["job"]["job_id"]).options)
            raw_plan = copy.deepcopy(session.get(PlanRow, p["plan_id"]).content)
        original_doc = next(
            d
            for d in reference["documents"]
            if d["kind"] == "plan" and d["document_id"] == p["plan_id"]
        )
        assert json.loads(original_doc["payload_json"]) == raw_plan
        assert (
            raw_plan["scenario_id"] != snap["scenario_id"]
        ), "Do not forge the old plan identity for a residual input"
        malformed = copy.deepcopy(reference)
        malformed["documents"][0]["payload_json"] += " "
        rejected = repair_remaining(snap, malformed, options)
        assert rejected["plan"] is None and rejected["stop_reason"] == "input_not_ready"
        fabricated = copy.deepcopy(reference)
        fabricated["committed_cargo_ids"].append("NEVER-IN-SOURCE-PLAN")
        assert repair_remaining(snap, fabricated, options)["plan"] is None
        baseline_job = await_job(
            c,
            post(
                c,
                "/solve-jobs",
                {
                    "snapshot_id": snap["snapshot_id"],
                    "objective_policy": "tradeoff_v2",
                    "time_limit_s": 8,
                    "seed": 42,
                },
                202,
            ),
        )
        assert baseline_job["has_validated_plan"], baseline_job
        baseline = c.get("/api/v1/plans/" + baseline_job["plan_id"]).json()
        assert baseline["snapshot_id"] == local["job"]["snapshot_id"]
        assert validate(snap, baseline)["status"] == "passed"
        assert wait_applied(c, e, local)["status"] == "applied"
        after = c.get("/api/v1/executions/" + e["execution_id"]).json()
        assert after["facts"] == e["facts"]
        endpoint = f"/api/v1/executions/{e['execution_id']}/export?version=2"
        bundle = c.get(endpoint)
        assert bundle.status_code == 200, bundle.text
        bundle = bundle.json()
        assert any(d["kind"] == "repair_reference" for d in bundle["documents"])

        def upload(value):
            return c.post(
                "/api/v1/execution-archives/import",
                files={
                    "file": (
                        "bundle.json",
                        json.dumps(value).encode(),
                        "application/json",
                    )
                },
            )

        assert upload(bundle).status_code == 201
        tampered_graph = copy.deepcopy(bundle)
        tampered_graph["events"][0]["impact"]["nodes"][0]["committed"] = (
            not tampered_graph["events"][0]["impact"]["nodes"][0]["committed"]
        )
        assert upload(seal(tampered_graph)).status_code == 422
        damaged = copy.deepcopy(bundle)
        damaged["changes"][0]["diff"]["rows"][0]["candidate_drone_id"] = "FORGED-DRONE"
        assert upload(seal(damaged)).status_code == 422
        missing = copy.deepcopy(bundle)
        missing["documents"] = [
            d for d in missing["documents"] if d["kind"] != "repair_reference"
        ]
        assert upload(seal(missing)).status_code == 422


def test_actual_inflight_battery_exit_changes_future_assignment_and_preserves_live_cargo(
    tmp_path,
):
    app = create_app(tmp_path / "runtime")
    with TestClient(app) as c:

        def two_full_boxes(scene):
            scene["demands"] = scene["demands"][:2]
            demand_ids = {d["demand_id"] for d in scene["demands"]}
            scene["cargo_items"] = [
                box for box in scene["cargo_items"] if box["demand_id"] in demand_ids
            ]
            for d in scene["demands"]:
                d.update(expected_deadline_s=None, hard_deadline_s=None)
            # Two user-input full-size boxes force two flights under the unchanged type-A limits.
            for box in scene["cargo_items"]:
                box.update(mass_kg=25, volume_l=60)
            scene["drones"] = [scene["drones"][0]]
            scene["batteries"] = [
                b for b in scene["batteries"] if b["compatible_type_id"] == "A"
            ]

        _, s, p, e = setup(c, two_full_boxes)
        first = min(p["sorties"], key=lambda r: r["prepare_start_s"])
        assert len(p["sorties"]) == 2
        e = act(c, e, "advance", target_time_s=first["takeoff_s"] + 1)
        future = next(r for r in p["sorties"] if r["prepare_start_s"] > e["time_s"])
        assert future["battery_id"] != first["battery_id"]
        state = copy.deepcopy(e["telemetry"][0])
        event = post(
            c,
            f"/executions/{e['execution_id']}/events",
            {
                "event_id": "future-battery-exit",
                "event_type": "battery.unavailable",
                "object_id": future["battery_id"],
                "expected_revision": e["revision"],
                "reason": "Future spare battery unavailable while first aircraft is in flight",
            },
            201,
        )
        assert event["status"] == "recorded"
        impact = event["impact"]
        assert impact["facts_cursor"] == e["facts_cursor"]
        assert {n["sortie_id"] for n in impact["nodes"] if n["direct"]} == {
            future["sortie_id"]
        }
        assert {n["sortie_id"] for n in impact["nodes"] if n["committed"]} == {
            first["sortie_id"]
        }
        e = c.get("/api/v1/executions/" + e["execution_id"]).json()
        fixed_facts = copy.deepcopy(e["facts"])
        result = change(c, e, "battery-local")
        assert result["calculation_method"] == "dependency_local", result
        assert result["diff"]["battery_reassigned_quantity"] == 1
        assert result["diff"]["time_shifted_quantity"] == 1
        assert result["diff"]["drone_reassigned_quantity"] == 0
        candidate = c.get("/api/v1/plans/" + result["candidate_plan_id"]).json()
        assert all(
            r["battery_id"] != future["battery_id"] for r in candidate["sorties"]
        )
        assert wait_applied(c, e, result)["status"] == "applied"
        after = c.get("/api/v1/executions/" + e["execution_id"]).json()
        assert after["facts"] == fixed_facts
        persisted_event = c.get(
            f"/api/v1/executions/{e['execution_id']}/events"
        ).json()[0]
        assert (
            persisted_event["impact"] == impact
        ), "Adoption must not rewrite event-time graph"
        for field in (
            "coordinates",
            "cargo_ids",
            "soc",
            "soc_sample_time_s",
            "sortie_id",
            "active_plan_id",
        ):
            assert after["telemetry"][0][field] == state[field]
        finished = act(
            c,
            after,
            "advance",
            target_time_s=max(r["battery_released_s"] for r in candidate["sorties"])
            + 1,
        )
        assert (
            finished["status"] == "completed"
            and len(finished["delivered_cargo_ids"]) == 2
        )
        assert len([f for f in finished["facts"] if f["kind"] == "delivered"]) == 2


def test_busy_repair_job_records_failure_and_idempotency_instead_of_eternal_computing(
    tmp_path,
):
    app = create_app(tmp_path / "runtime")
    with TestClient(app) as c:
        _, s, p, e = setup(c)
        e = act(c, e, "advance", target_time_s=1)
        post(
            c,
            f"/executions/{e['execution_id']}/events",
            {
                "event_id": "idle-exit",
                "event_type": "drone.unavailable",
                "object_id": s["drones"][-1]["drone_id"],
                "expected_revision": e["revision"],
                "reason": "Future availability change",
            },
            201,
        )
        e = c.get("/api/v1/executions/" + e["execution_id"]).json()
        app.state.jobs.limit.acquire()
        queued = []
        try:
            for _ in range(4):
                queued.append(
                    post(
                        c,
                        "/solve-jobs",
                        {"snapshot_id": p["snapshot_id"], "time_limit_s": 5},
                        202,
                    )
                )
            body = {
                "expected_revision": e["revision"],
                "idempotency_key": "busy-repair",
                "repair_policy": "dependency",
                "time_limit_s": 8,
            }
            failed = post(c, f"/executions/{e['execution_id']}/replan-jobs", body, 202)
            assert (
                failed["status"] == "failed"
                and failed["job"] is None
                and "4" in failed["message"]
            )
            again = post(c, f"/executions/{e['execution_id']}/replan-jobs", body, 202)
            assert again["change_id"] == failed["change_id"]
        finally:
            for job in queued:
                post(c, f"/solve-jobs/{job['job_id']}/cancel", {}, 202)
            app.state.jobs.limit.release()
        retry = change(c, e, "after-busy")
        assert retry["status"] == "ready"
