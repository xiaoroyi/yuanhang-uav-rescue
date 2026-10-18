import copy
import time

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import select

from backend.app.main import create_app
from backend.app.storage import ReservationRow, ScenarioRow
from shared.contracts import (
    ContractError,
    apply_event_to_scenario,
    validate_applied_event,
)
from solver.public_api import validate


def configured(client):
    s = client.post("/api/v1/scenarios/examples", json={"example": "compact"}).json()
    s["communication"] = client.get(
        f"/api/v1/scenarios/{s['scenario_id']}/communication-template"
    ).json()
    s["policy"]["requires_communication"] = True
    response = client.put(
        f"/api/v1/scenarios/{s['scenario_id']}",
        json={"expected_state_version": 1, "scenario": s},
    )
    assert response.status_code == 200, response.text
    return response.json()


def event_for(s, component=None):
    return dict(
        schema_version=s["schema_version"],
        event_id="EVT-RELAY-ENERGY-TEST",
        scenario_id=s["scenario_id"],
        expected_state_version=s["state_version"],
        event_type="relay_energy.unavailable",
        occurred_at=s["start_time"],
        received_at=s["start_time"],
        effective_time_s=0,
        actor="simulation",
        reason="Relay energy component withdrawal",
        payload={
            "component_id": component
            or s["communication"]["relay_energy"][0]["component_id"]
        },
    )


def real_plan(client, snapshot, **extra):
    response = client.post(
        "/api/v1/solve-jobs",
        json={"snapshot_id": snapshot["snapshot_id"], "time_limit_s": 120, **extra},
    )
    assert response.status_code == 202, response.text
    job = response.json()
    until = time.monotonic() + 180
    while time.monotonic() < until:
        job = client.get("/api/v1/solve-jobs/" + job["job_id"]).json()
        if job["job_state"] not in ["queued", "running"]:
            break
        time.sleep(0.1)
    assert job["has_validated_plan"], job
    return client.get("/api/v1/plans/" + job["plan_id"]).json()


def test_real_joint_relay_energy_withdrawal_preserves_history_and_reconfirms_new_resources(
    tmp_path,
):
    app = create_app(tmp_path / "runtime")
    with TestClient(app) as c:
        s = configured(c)
        sid = s["scenario_id"]
        snap = c.post(
            f"/api/v1/scenarios/{sid}/snapshots", json={"expected_state_version": 2}
        ).json()
        old = real_plan(c, snap)
        assert (
            c.post(
                f"/api/v1/plans/{old['plan_id']}/confirm",
                json={
                    "expected_state_version": 2,
                    "idempotency_key": "BEFORE-R-ENERGY",
                },
            ).status_code
            == 200
        )
        failed = old["relay_sorties"][0]["component_id"]
        e = event_for(s, failed)
        receipt = c.post("/api/v1/events", json=e)
        assert receipt.status_code == 200, receipt.text
        stored = receipt.json()["event"]
        assert receipt.json()["state_version_after"] == 3
        expected = copy.deepcopy(s)
        expected["state_version"] = 3
        next(
            b
            for b in expected["communication"]["relay_energy"]
            if b["component_id"] == failed
        )["status"] = "unavailable"
        assert c.get(f"/api/v1/scenarios/{sid}").json() == expected
        assert c.get(f"/api/v1/plans/{old['plan_id']}").json() == old
        assert c.get(f"/api/v1/snapshots/{snap['snapshot_id']}").json() == snap
        duplicate = c.post(
            "/api/v1/events", json=dict(e, received_at="2099-01-01T00:00:00Z")
        )
        assert (
            duplicate.status_code == 200
            and duplicate.json()["event"] == stored
            and not duplicate.json()["applied"]
        )
        assert (
            c.post("/api/v1/events", json=dict(e, reason="Conflict")).status_code == 409
        )
        with app.state.database.session() as db:
            assert db.get(ScenarioRow, sid).active_plan_id is None
            assert (
                list(
                    db.scalars(
                        select(ReservationRow).where(ReservationRow.scenario_id == sid)
                    )
                )
                == []
            )
        new_snap = c.post(
            f"/api/v1/scenarios/{sid}/snapshots", json={"expected_state_version": 3}
        ).json()
        new = real_plan(
            c,
            new_snap,
            mode="replan",
            parent_plan_id=old["plan_id"],
            event_id=stored["event_id"],
        )
        assert (
            new["parent_plan_id"] == old["plan_id"]
            and new["event_id"] == stored["event_id"]
        )
        assert all(r["component_id"] != failed for r in new["relay_sorties"])
        assert len({b for r in new["sorties"] for b in r["cargo_ids"]}) == 32
        assert new["communication_report"]["coverage_gap_s"] == 0
        corrupted = copy.deepcopy(new)
        corrupted["relay_sorties"][0]["component_id"] = failed
        assert validate(new_snap, corrupted)["status"] == "failed"
        confirmed = c.post(
            f"/api/v1/plans/{new['plan_id']}/confirm",
            json={"expected_state_version": 3, "idempotency_key": "AFTER-R-ENERGY"},
        )
        assert confirmed.status_code == 200, confirmed.text
        assert (
            c.post(
                "/api/v1/events",
                json=dict(
                    e, event_id="EVT-ALREADY-WITHDRAWN", expected_state_version=3
                ),
            ).status_code
            == 422
        )


@pytest.mark.parametrize(
    "fault",
    [
        "unknown",
        "transport_id",
        "mixed_payload",
        "wrong_payload",
        "nonzero",
        "future",
        "execution",
        "missing_config",
    ],
)
def test_invalid_relay_energy_exit_has_no_partial_event_or_version(tmp_path, fault):
    with TestClient(create_app(tmp_path / "runtime")) as c:
        s = configured(c)
        e = event_for(s)
        sid = s["scenario_id"]
        if fault == "unknown":
            e["payload"]["component_id"] = "MISSING"
        elif fault == "transport_id":
            e["payload"]["component_id"] = s["batteries"][0]["battery_id"]
        elif fault == "mixed_payload":
            e["payload"]["battery_id"] = s["batteries"][0]["battery_id"]
        elif fault == "wrong_payload":
            e["payload"] = {"battery_id": s["batteries"][0]["battery_id"]}
        elif fault == "nonzero":
            e["effective_time_s"] = 10
        elif fault == "future":
            e.update(
                occurred_at="2099-01-01T00:00:00Z", received_at="2099-01-01T00:00:00Z"
            )
        elif fault == "execution":
            s["batteries"][0]["status"] = "in_use"
            saved = c.put(
                f"/api/v1/scenarios/{sid}",
                json={"expected_state_version": 2, "scenario": s},
            )
            assert saved.status_code == 200
            s = saved.json()
            e = event_for(s)
        else:
            s.pop("communication")
            s["policy"]["requires_communication"] = False
            saved = c.put(
                f"/api/v1/scenarios/{sid}",
                json={"expected_state_version": 2, "scenario": s},
            )
            assert saved.status_code == 200
            s = saved.json()
            e["expected_state_version"] = s["state_version"]
        response = c.post("/api/v1/events", json=e)
        assert response.status_code == 422, response.text
        assert c.get(f"/api/v1/scenarios/{sid}").json() == s
        assert c.get(f"/api/v1/scenarios/{sid}/events").json() == []


def test_initial_charging_relay_component_transition_keeps_energy_location_and_validates_applied_state(
    tmp_path,
):
    with TestClient(create_app(tmp_path / "runtime")) as c:
        s = configured(c)
        s["communication"]["relay_energy"][0].update(
            status="charging", soc=0.6, soh=0.9, available_after_s=75
        )
        e = event_for(s)
        before = copy.deepcopy(s)
        result = apply_event_to_scenario(e, s)
        expected = copy.deepcopy(s)
        expected["state_version"] += 1
        expected["communication"]["relay_energy"][0]["status"] = "unavailable"
        assert result == expected and s == before
        validate_applied_event(e, result)
        changed = copy.deepcopy(result)
        changed["communication"]["relay_energy"][0]["status"] = "available"
        with pytest.raises(ContractError):
            validate_applied_event(e, changed)
