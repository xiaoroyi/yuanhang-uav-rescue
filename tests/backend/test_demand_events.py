import copy
import time

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from backend.app.generated.domain import Event
from backend.app.main import create_app
from backend.app.storage import ReservationRow, ScenarioRow


def event_for(s):
    d = dict(
        s["demands"][0],
        demand_id="URG-API",
        required_quantity=2,
        priority=7,
        mandatory=True,
        expected_deadline_s=5400,
        hard_deadline_s=18000,
    )
    return dict(
        schema_version=s["schema_version"],
        event_id="EVT-URG-API",
        scenario_id=s["scenario_id"],
        expected_state_version=s["state_version"],
        event_type="demand.added",
        occurred_at=s["start_time"],
        received_at="2000-01-01T00:00:00Z",
        effective_time_s=0,
        actor="simulation",
        reason="Urgent inventory received at base",
        payload={
            "demand": d,
            "cargo_items": [
                dict(
                    s["cargo_items"][0],
                    cargo_id=f"URG-API-BOX-{i}",
                    demand_id=d["demand_id"],
                    type=d["cargo_type"],
                    mass_kg=3,
                    volume_l=12,
                    status="available",
                    location_id=s["base"]["id"],
                )
                for i in range(2)
            ],
        },
    )


def real_plan(client, snapshot, **extra):
    r = client.post(
        "/api/v1/solve-jobs",
        json={"snapshot_id": snapshot["snapshot_id"], "time_limit_s": 10, **extra},
    )
    assert r.status_code == 202, r.text
    job = r.json()
    until = time.monotonic() + 30
    while time.monotonic() < until:
        job = client.get("/api/v1/solve-jobs/" + job["job_id"]).json()
        if job["job_state"] not in ["queued", "running"]:
            break
        time.sleep(0.05)
    assert job["has_validated_plan"], job
    return client.get("/api/v1/plans/" + job["plan_id"]).json()


def test_demand_event_real_worker_complete_coverage_immutable_history_and_atomic_reservations(
    tmp_path,
):
    app = create_app(tmp_path / "runtime")
    with TestClient(app) as c:
        s = c.post("/api/v1/scenarios/examples", json={"example": "compact"}).json()
        sid = s["scenario_id"]
        snap = c.post(
            f"/api/v1/scenarios/{sid}/snapshots", json={"expected_state_version": 1}
        ).json()
        old = real_plan(c, snap)
        assert (
            c.post(
                f"/api/v1/plans/{old['plan_id']}/confirm",
                json={"expected_state_version": 1, "idempotency_key": "BEFORE-URG"},
            ).status_code
            == 200
        )
        e = event_for(s)
        r = c.post("/api/v1/events", json=e)
        assert r.status_code == 200, r.text
        stored = r.json()["event"]
        assert (
            stored["received_at"] != e["received_at"]
            and r.json()["state_version_after"] == 2
        )
        assert Event.model_validate(stored).model_dump(mode="json") == stored
        expected = copy.deepcopy(s)
        expected.update(state_version=2, data_origin="user_input")
        expected["demands"].append(stored["payload"]["demand"])
        expected["cargo_items"].extend(stored["payload"]["cargo_items"])
        current = c.get(f"/api/v1/scenarios/{sid}").json()
        assert current == expected
        assert c.get(f"/api/v1/plans/{old['plan_id']}").json() == old
        assert c.get(f"/api/v1/snapshots/{snap['snapshot_id']}").json() == snap
        again = c.post(
            "/api/v1/events", json=dict(e, received_at="2099-01-01T00:00:00Z")
        )
        assert (
            again.status_code == 200
            and not again.json()["applied"]
            and again.json()["event"] == stored
        )
        assert (
            c.post("/api/v1/events", json=dict(e, reason="Changed request")).status_code
            == 409
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
        next_snap = c.post(
            f"/api/v1/scenarios/{sid}/snapshots", json={"expected_state_version": 2}
        ).json()
        plan = real_plan(
            c,
            next_snap,
            mode="replan",
            parent_plan_id=old["plan_id"],
            event_id=e["event_id"],
        )
        assert (
            len({box for route in plan["sorties"] for box in route["cargo_ids"]}) == 34
        )
        assert (
            plan["parent_plan_id"] == old["plan_id"]
            and plan["snapshot_id"] == next_snap["snapshot_id"]
        )
        assert (
            c.post(
                f"/api/v1/plans/{plan['plan_id']}/confirm",
                json={"expected_state_version": 2, "idempotency_key": "AFTER-URG"},
            ).status_code
            == 200
        )
        repeated_new = dict(
            e, event_id="EVT-DUPLICATE-ADDITION", expected_state_version=2
        )
        assert c.post("/api/v1/events", json=repeated_new).status_code == 422
        assert c.get(f"/api/v1/scenarios/{sid}").json() == current
        assert len(c.get(f"/api/v1/scenarios/{sid}/events").json()) == 1


@pytest.mark.parametrize(
    "fault",
    [
        "existing_demand",
        "existing_box",
        "quantity",
        "not_at_base",
        "loaded",
        "wrong_type",
        "missing_site",
        "nonzero",
        "future_occurrence",
        "existing_execution",
        "wrong_payload",
    ],
)
def test_rejected_addition_rolls_back_everything(tmp_path, fault):
    with TestClient(create_app(tmp_path / "runtime")) as c:
        s = c.post("/api/v1/scenarios/examples", json={"example": "compact"}).json()
        sid = s["scenario_id"]
        e = event_for(s)
        if fault == "existing_demand":
            e["payload"]["demand"]["demand_id"] = s["demands"][0]["demand_id"]
        elif fault == "existing_box":
            e["payload"]["cargo_items"][0]["cargo_id"] = s["cargo_items"][0]["cargo_id"]
        elif fault == "quantity":
            e["payload"]["demand"]["required_quantity"] = 3
        elif fault == "not_at_base":
            e["payload"]["cargo_items"][0]["location_id"] = s["sites"][0]["id"]
        elif fault == "loaded":
            e["payload"]["cargo_items"][0]["status"] = "loaded"
        elif fault == "wrong_type":
            e["payload"]["cargo_items"][0]["type"] = "WRONG"
        elif fault == "missing_site":
            e["payload"]["demand"]["site_id"] = "MISSING"
        elif fault == "nonzero":
            e["effective_time_s"] = 1
        elif fault == "future_occurrence":
            e.update(
                occurred_at="2099-01-01T00:00:00Z", received_at="2099-01-01T00:00:00Z"
            )
        elif fault == "existing_execution":
            s["cargo_items"][0]["status"] = "loaded"
            r = c.put(
                f"/api/v1/scenarios/{sid}",
                json={"expected_state_version": 1, "scenario": s},
            )
            assert r.status_code == 200
            s = r.json()
            e = event_for(s)
        else:
            e["payload"] = {"drone_id": s["drones"][0]["drone_id"]}
        r = c.post("/api/v1/events", json=e)
        assert r.status_code == 422, r.text
        assert c.get(f"/api/v1/scenarios/{sid}").json() == s
        assert c.get(f"/api/v1/scenarios/{sid}/events").json() == []
