import copy
from datetime import datetime
import json
from pathlib import Path
import time

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import select

from backend.app.generated.domain import Event
from backend.app.main import create_app
from backend.app.storage import ReservationRow, ScenarioRow
from shared.contracts import ContractError, validate_schema


def event_for(s, battery_id):
    return dict(
        schema_version=s["schema_version"],
        event_id="EVT-API-BATTERY",
        scenario_id=s["scenario_id"],
        expected_state_version=s["state_version"],
        event_type="battery.unavailable",
        occurred_at="2026-10-17T08:00:00+08:00",
        received_at="2000-01-01T00:00:00Z",
        effective_time_s=0,
        actor="simulation",
        reason="Battery withdrawal exercise",
        payload={"battery_id": battery_id},
    )


def real_plan(client, snap, **kwargs):
    receipt = client.post(
        "/api/v1/solve-jobs",
        json={"snapshot_id": snap["snapshot_id"], "time_limit_s": 10, **kwargs},
    )
    assert receipt.status_code == 202, receipt.text
    job = receipt.json()
    until = time.monotonic() + 30
    while time.monotonic() < until:
        job = client.get(f"/api/v1/solve-jobs/{job['job_id']}").json()
        if job["job_state"] not in ["queued", "running"]:
            break
        time.sleep(0.05)
    assert job["has_validated_plan"], job
    return client.get(f"/api/v1/plans/{job['plan_id']}").json()


def test_real_battery_event_is_atomic_idempotent_and_has_a_new_executable_plan(
    tmp_path,
):
    app = create_app(tmp_path / "runtime")
    with TestClient(app) as client:
        s = client.post(
            "/api/v1/scenarios/examples", json={"example": "compact"}
        ).json()
        sid = s["scenario_id"]
        before_snap = client.post(
            f"/api/v1/scenarios/{sid}/snapshots", json={"expected_state_version": 1}
        ).json()
        old = real_plan(client, before_snap)
        assert (
            client.post(
                f"/api/v1/plans/{old['plan_id']}/confirm",
                json={
                    "expected_state_version": 1,
                    "idempotency_key": "CONFIRM-BEFORE-BATTERY",
                },
            ).status_code
            == 200
        )
        target = old["sorties"][0]["battery_id"]
        request = event_for(s, target)
        receipt = client.post("/api/v1/events", json=request)
        assert receipt.status_code == 200, receipt.text
        recorded = receipt.json()["event"]
        assert "root" not in recorded
        assert datetime.fromisoformat(
            recorded["received_at"].replace("Z", "+00:00")
        ) >= datetime.fromisoformat(recorded["occurred_at"].replace("Z", "+00:00"))
        again = client.post(
            "/api/v1/events", json=dict(request, received_at="2099-01-01T00:00:00Z")
        )
        assert again.status_code == 200 and not again.json()["applied"]
        assert again.json()["event"] == recorded
        assert (
            client.post(
                "/api/v1/events", json=dict(request, reason="Different request")
            ).status_code
            == 409
        )
        current = client.get(f"/api/v1/scenarios/{sid}").json()
        expected = copy.deepcopy(s)
        expected["state_version"] = 2
        next(b for b in expected["batteries"] if b["battery_id"] == target)[
            "status"
        ] = "unavailable"
        assert current == expected
        assert client.get(f"/api/v1/plans/{old['plan_id']}").json() == old
        assert (
            client.get(f"/api/v1/snapshots/{before_snap['snapshot_id']}").json()
            == before_snap
        )
        with app.state.database.session() as session:
            assert session.get(ScenarioRow, sid).active_plan_id is None
            assert (
                list(
                    session.scalars(
                        select(ReservationRow).where(ReservationRow.scenario_id == sid)
                    )
                )
                == []
            )
        snap = client.post(
            f"/api/v1/scenarios/{sid}/snapshots", json={"expected_state_version": 2}
        ).json()
        plan = real_plan(
            client,
            snap,
            mode="replan",
            parent_plan_id=old["plan_id"],
            event_id=recorded["event_id"],
        )
        assert all(r["battery_id"] != target for r in plan["sorties"])
        assert len({c for r in plan["sorties"] for c in r["cargo_ids"]}) == 32
        assert (
            plan["event_id"] == recorded["event_id"]
            and plan["parent_plan_id"] == old["plan_id"]
        )
        assert (
            client.post(
                f"/api/v1/plans/{plan['plan_id']}/confirm",
                json={
                    "expected_state_version": 2,
                    "idempotency_key": "CONFIRM-AFTER-BATTERY",
                },
            ).status_code
            == 200
        )
        duplicate_new = dict(
            request, event_id="EVT-ALREADY-OUT", expected_state_version=2
        )
        assert client.post("/api/v1/events", json=duplicate_new).status_code == 422
        assert (
            "battery.unavailable"
            in client.get("/api/v1/meta/capabilities").json()["supported_events"]
        )


@pytest.mark.parametrize(
    "fault",
    [
        "future_occurrence",
        "mixed_payload",
        "wrong_payload",
        "missing_id",
        "nonzero_time",
    ],
)
def test_rejected_battery_event_leaves_no_version_or_event(tmp_path, fault):
    with TestClient(create_app(tmp_path / "runtime")) as client:
        s = client.post(
            "/api/v1/scenarios/examples", json={"example": "compact"}
        ).json()
        request = event_for(s, s["batteries"][0]["battery_id"])
        if fault == "future_occurrence":
            request.update(
                occurred_at="2099-01-01T00:00:00Z", received_at="2099-01-01T00:00:00Z"
            )
        elif fault == "mixed_payload":
            request["payload"]["drone_id"] = s["drones"][0]["drone_id"]
        elif fault == "wrong_payload":
            request["payload"] = {"drone_id": s["drones"][0]["drone_id"]}
        elif fault == "missing_id":
            request["payload"] = {"battery_id": "NO-SUCH-BATTERY"}
        else:
            request["effective_time_s"] = 1
        rejected = client.post("/api/v1/events", json=request)
        assert rejected.status_code == 422, rejected.text
        assert client.get(f"/api/v1/scenarios/{s['scenario_id']}").json() == s
        assert client.get(f"/api/v1/scenarios/{s['scenario_id']}/events").json() == []


def test_initial_charging_battery_can_exit_without_resetting_energy_or_location(
    tmp_path,
):
    with TestClient(create_app(tmp_path / "runtime")) as client:
        s = client.post(
            "/api/v1/scenarios/examples", json={"example": "compact"}
        ).json()
        s["batteries"][0].update(
            status="charging", soc=0.6, soh=0.9, available_after_s=75
        )
        response = client.put(
            f"/api/v1/scenarios/{s['scenario_id']}",
            json={"expected_state_version": 1, "scenario": s},
        )
        assert response.status_code == 200, response.text
        s = response.json()
        request = event_for(s, s["batteries"][0]["battery_id"])
        receipt = client.post("/api/v1/events", json=request)
        assert receipt.status_code == 200, receipt.text
        actual = client.get(f"/api/v1/scenarios/{s['scenario_id']}").json()
        expected = copy.deepcopy(s)
        expected["state_version"] = 3
        expected["batteries"][0]["status"] = "unavailable"
        assert actual == expected


@pytest.mark.parametrize(
    "group,status", [("cargo_items", "loaded"), ("batteries", "in_use")]
)
def test_battery_event_cannot_reset_other_recorded_execution_facts(
    tmp_path, group, status
):
    with TestClient(create_app(tmp_path / "runtime")) as client:
        scene = client.post(
            "/api/v1/scenarios/examples", json={"example": "compact"}
        ).json()
        # Use an unused second battery for the execution-fact probe, not the exit target.
        scene[group][1]["status"] = status
        sid = scene["scenario_id"]
        saved = client.put(
            f"/api/v1/scenarios/{sid}",
            json={"expected_state_version": 1, "scenario": scene},
        )
        assert saved.status_code == 200, saved.text
        scene = saved.json()
        request = event_for(scene, scene["batteries"][0]["battery_id"])
        assert client.post("/api/v1/events", json=request).status_code == 422
        assert client.get(f"/api/v1/scenarios/{sid}").json() == scene
        assert client.get(f"/api/v1/scenarios/{sid}/events").json() == []


def test_schema_and_generated_union_preserve_old_wire_shape_and_reject_cross_payloads():
    root = Path(__file__).resolve().parents[2]
    for name in ["event.json", "event-battery.json"]:
        value = json.loads((root / "fixtures/mock" / name).read_text(encoding="utf8"))
        validate_schema("event", value)
        normalized = Event.model_validate(value).model_dump(mode="json")
        assert "root" not in normalized and normalized["payload"] == value["payload"]
        other = (
            "battery.unavailable"
            if value["event_type"] == "drone.unavailable"
            else "drone.unavailable"
        )
        malformed = dict(value, event_type=other)
        with pytest.raises(ContractError):
            validate_schema("event", malformed)
        with pytest.raises(ValueError):
            Event.model_validate(malformed)
