"""Execution reads must not turn a planned boundary into an executed commitment."""

import time

from fastapi.testclient import TestClient

from backend.app.main import create_app
from backend.app.storage import ExecutionRow
from test_execution_v2 import setup, act, post, await_job


def test_ready_zero_time_failure_is_not_loaded_and_repair_has_no_phantom_commitments(tmp_path):
    app = create_app(tmp_path / "runtime")
    with TestClient(app) as c:
        def without_deadlines(scene):
            # This case verifies the start boundary, with sufficient time for the surviving fleet.
            # The original urgent case remains unchanged in all existing regressions.
            for demand in scene["demands"]:
                demand["hard_deadline_s"] = None
                demand["expected_deadline_s"] = None

        m, s, p, e = setup(c, without_deadlines)
        endpoint = "/executions/" + e["execution_id"]
        e = c.get("/api/v1" + endpoint).json()
        standby = next(t for t in e["telemetry"] if t["device_id"] == s["drones"][-1]["drone_id"])
        assert standby["phase"] == "not_ready", "A future release is not ready now"
        device = min(p["sorties"], key=lambda r: r["prepare_start_s"])["drone_id"]

        def failure(key):
            current = c.get("/api/v1" + endpoint).json()
            return post(c, endpoint + "/events", {
                "event_id": key, "expected_revision": current["revision"],
                "event_type": "drone.unavailable", "object_id": device,
                "reason": "Reported unavailable before any loading begins",
            }, 201)

        event = failure("before-start")
        assert event["status"] == "recorded" and event["committed_sortie_ids"] == []
        e = c.get("/api/v1" + endpoint).json()
        failed = next(t for t in e["telemetry"] if t["device_id"] == device)
        assert failed["phase"] == "unavailable" and failed["cargo_ids"] == []
        post(c, endpoint + "/events/before-start/resolve", {
            "expected_revision": e["revision"], "idempotency_key": "withdraw",
            "action": "withdraw_misreport", "reason": "Operator inspected this simulation device and confirmed the report was false",
        })
        e = c.get("/api/v1" + endpoint).json()
        assert next(t for t in e["telemetry"] if t["device_id"] == device)["phase"] == "ready"
        failure("verified-failure")
        e = c.get("/api/v1" + endpoint).json()
        change = post(c, endpoint + "/replan-jobs", {
            "expected_revision": e["revision"], "idempotency_key": "repair", "time_limit_s": 5,
        }, 202)
        assert change["committed_cargo_ids"] == []
        job = await_job(c, change["job"])
        assert job["has_validated_plan"], job
        candidate = c.get("/api/v1/plans/" + job["plan_id"]).json()
        assert all(r["drone_id"] != device for r in candidate["sorties"])
        assert min(r["prepare_start_s"] for r in candidate["sorties"]) == 0
        path = endpoint + "/plan-changes/" + change["change_id"]
        assert c.get("/api/v1" + path).json()["status"] == "ready"
        post(c, path + "/apply", {"expected_revision": e["revision"], "idempotency_key": "apply"})
        for _ in range(100):
            state = c.get("/api/v1" + path).json()
            if state["status"] != "applying":
                break
            time.sleep(0.05)
        assert state["status"] == "applied", state
        for _ in range(3):
            e = c.get("/api/v1" + endpoint).json()
            assert e["facts"] == [] and e["time_s"] == 0
            assert not any(t["cargo_ids"] for t in e["telemetry"])
        e = act(c, e, "advance", target_time_s=0)
        assert any(f["kind"] == "loaded" for f in e["facts"])
        assert all(f["plan_id"] == candidate["plan_id"] for f in e["facts"])


def test_paused_read_does_not_start_a_new_boundary_without_explicit_advancement(tmp_path):
    app = create_app(tmp_path / "runtime")
    with TestClient(app) as c:
        _, _, p, e = setup(c)
        # The paused future program may begin exactly at the frozen time (e.g. after adoption).
        # Reading that boundary must remain observational until resume/explicit advance.
        with app.state.database.session(immediate=True) as session:
            row = session.get(ExecutionRow, e["execution_id"])
            row.content = {**row.content, "status": "paused"}
        for _ in range(3):
            frozen = c.get("/api/v1/executions/" + e["execution_id"]).json()
            assert frozen["facts"] == []
            assert not any(t["cargo_ids"] or t["sortie_id"] for t in frozen["telemetry"])
        stepped = act(c, frozen, "advance", target_time_s=0)
        assert stepped["facts"] and stepped["time_s"] == 0
        assert all(f["kind"] == "loaded" for f in stepped["facts"])
        assert c.get("/api/v1/executions/" + e["execution_id"]).json()["facts"] == stepped["facts"]
