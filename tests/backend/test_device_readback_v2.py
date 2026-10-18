"""Device command completion needs persistent simulation state, not elapsed time alone."""

from datetime import datetime, timedelta, timezone
import copy
import time

from fastapi.testclient import TestClient

from backend.app.main import create_app
from backend.app.execution_archive import seal, validate_bundle
from backend.app.operation_models import ExecutionBundle
import pytest
from test_execution_v2 import setup, act, post, await_job


def command(execution, device, plan, kind, key, fault="none"):
    return {
        "execution_id": execution["execution_id"],
        "device_id": device,
        "desired_plan_id": plan,
        "command_type": kind,
        "expected_execution_revision": execution["revision"],
        "idempotency_key": key,
        "expires_at": (datetime.now(timezone.utc) + timedelta(seconds=60)).isoformat(),
        "simulation_fault": fault,
    }


def terminal(client, cmd):
    for _ in range(80):
        cmd = client.get("/api/v1/commands/" + cmd["command_id"]).json()
        if cmd["status"] in ("succeeded", "rejected", "expired", "indeterminate"):
            return cmd
        time.sleep(0.05)
    raise AssertionError(cmd)


def test_successful_state_query_has_owned_persisted_readback(tmp_path):
    with TestClient(create_app(tmp_path / "runtime")) as c:
        m, s, p, e = setup(c)
        body = command(
            e, s["drones"][0]["drone_id"], p["plan_id"], "state.query", "readback"
        )
        queued = post(c, "/commands", body, 202)
        result = terminal(c, queued)
        assert result["status"] == "succeeded"
        state = result.get("observed_state")
        assert state is not None, "A timer is not device state evidence"
        assert (
            state["device_id"] == body["device_id"]
            and state["execution_id"] == e["execution_id"]
        )
        assert (
            state["active_plan_id"] == e["desired_plan_id"]
            and state["mode"] == "simulation"
        )
        assert state["real_device_connected"] is False
        assert post(c, "/commands", body, 202)["command_id"] == queued["command_id"]
        exported = c.get(
            f"/api/v1/executions/{e['execution_id']}/export?version=2"
        )
        assert exported.status_code == 200, exported.text
        bundle = exported.json()
        validate_bundle(ExecutionBundle.model_validate(bundle))
        for field, wrong in (
            ("execution_id", "OTHER-EXECUTION"),
            ("device_id", "OTHER-DRONE"),
            ("active_plan_id", "MISSING-PLAN"),
            ("uploaded_plan_id", "MISSING-PLAN"),
        ):
            altered = copy.deepcopy(bundle)
            altered["commands"][0]["observed_state"][field] = wrong
            with pytest.raises(ValueError):
                validate_bundle(ExecutionBundle.model_validate(seal(altered)))


def test_owned_but_unapproved_repair_candidate_cannot_be_directly_activated(tmp_path):
    with TestClient(create_app(tmp_path / "runtime")) as c:
        m, s, p, e = setup(c)
        e = act(c, e, "advance", target_time_s=1)
        post(
            c,
            f"/executions/{e['execution_id']}/events",
            {
                "event_id": "future-failure",
                "expected_revision": e["revision"],
                "event_type": "drone.unavailable",
                "object_id": s["drones"][-1]["drone_id"],
                "reason": "Future unavailable entity",
            },
            201,
        )
        e = c.get("/api/v1/executions/" + e["execution_id"]).json()
        change = post(
            c,
            f"/executions/{e['execution_id']}/replan-jobs",
            {
                "expected_revision": e["revision"],
                "idempotency_key": "candidate",
                "time_limit_s": 5,
            },
            202,
        )
        job = await_job(c, change["job"])
        assert job["has_validated_plan"], job
        candidate = job["plan_id"]
        assert (
            c.get(
                f"/api/v1/executions/{e['execution_id']}/plan-changes/{change['change_id']}"
            ).json()["status"]
            == "ready"
        )
        response = c.post(
            "/api/v1/commands",
            json=command(
                e,
                s["drones"][0]["drone_id"],
                candidate,
                "mission.activate",
                "unapproved",
            ),
        )
        assert response.status_code == 409, response.text
        assert response.json()["error"]["code"] == "ACTIVATION_APPROVAL_REQUIRED"
        same = c.get("/api/v1/executions/" + e["execution_id"]).json()
        assert same["desired_plan_id"] == p["plan_id"] and same["facts"] == e["facts"]


def test_ack_is_not_completion_and_lost_completion_is_resolved_by_separate_query(
    tmp_path, monkeypatch
):
    import backend.app.executions as routes
    import backend.app.device_state as state_store

    with TestClient(create_app(tmp_path / "runtime")) as c:
        m, s, p, e = setup(c)
        base = datetime.now(timezone.utc)
        tick = [0.0]
        clock = lambda: (base + timedelta(seconds=tick[0])).isoformat()
        monkeypatch.setattr(routes, "now", clock)
        monkeypatch.setattr(state_store, "now", clock)
        device = s["drones"][0]["drone_id"]
        first = post(
            c,
            "/commands",
            command(e, device, p["plan_id"], "mission.upload", "upload"),
            202,
        )
        tick[0] = 0.5
        acknowledged = c.get("/api/v1/commands/" + first["command_id"]).json()
        assert (
            acknowledged["status"] == "acknowledged"
            and acknowledged["completed_at"] is None
            and acknowledged.get("observed_state") is None
        )
        tick[0] = 1.3
        completed = c.get("/api/v1/commands/" + first["command_id"]).json()
        assert (
            completed["status"] == "succeeded"
            and completed["observed_state"]["uploaded_plan_id"] == p["plan_id"]
        )
        assert completed["observed_state"]["uploaded_content_sha256"]
        tick[0] = 2
        lost = post(
            c,
            "/commands",
            command(
                e,
                device,
                p["plan_id"],
                "mission.upload",
                "lost-completion",
                "completion_timeout",
            ),
            202,
        )
        tick[0] = 3.3
        unknown = c.get("/api/v1/commands/" + lost["command_id"]).json()
        assert (
            unknown["status"] == "indeterminate"
            and unknown["completed_at"] is None
            and unknown.get("observed_state") is None
        )
        query = post(
            c,
            "/commands",
            command(e, device, p["plan_id"], "state.query", "resolve-by-query"),
            202,
        )
        tick[0] = 4.7
        observed = c.get("/api/v1/commands/" + query["command_id"]).json()
        assert observed["status"] == "succeeded"
        assert (
            observed["observed_state"]["last_upload_command_id"] == lost["command_id"]
        )
        version = observed["observed_state"]["revision"]
        for _ in range(3):
            assert (
                c.get("/api/v1/commands/" + lost["command_id"]).json()["status"]
                == "indeterminate"
            )
        actual = c.get(
            f"/api/v1/executions/{e['execution_id']}/devices/{device}/mission-state"
        ).json()
        assert (
            actual["revision"] == version
        ), "Reading an uncertain command must not repeat its action"


def test_command_dispatch_does_not_depend_on_http_polling_and_device_state_survives_restart(
    tmp_path,
):
    from backend.app.storage import OperationRecordRow

    directory = tmp_path / "runtime"
    app = create_app(directory)
    with TestClient(app) as c:
        m, s, p, e = setup(c)
        device = s["drones"][0]["drone_id"]
        queued = post(
            c,
            "/commands",
            command(e, device, p["plan_id"], "mission.upload", "background-upload"),
            202,
        )
        for _ in range(100):
            with app.state.database.session() as session:
                result = session.get(
                    OperationRecordRow, ("command", queued["command_id"])
                ).content
            if result["status"] == "succeeded":
                break
            time.sleep(0.05)
        assert (
            result["status"] == "succeeded"
            and result["observed_state"]["uploaded_plan_id"] == p["plan_id"]
        )
        saved = result["observed_state"]
    with TestClient(create_app(directory)) as c:
        restored = c.get(
            f"/api/v1/executions/{e['execution_id']}/devices/{device}/mission-state"
        ).json()
        assert (
            restored["uploaded_content_sha256"] == saved["uploaded_content_sha256"]
            and restored["revision"] == saved["revision"]
        )


def test_expired_queued_upload_and_disconnected_query_do_not_claim_device_completion(
    tmp_path, monkeypatch
):
    import backend.app.executions as routes
    import backend.app.device_state as state_store

    app = create_app(tmp_path / "runtime")
    with TestClient(app) as c:
        m, s, p, e = setup(c)
        device = s["drones"][0]["drone_id"]
        monkeypatch.setattr(app.state.simulation, "command_tick", None)
        base = datetime.now(timezone.utc)
        tick = [0.0]
        clock = lambda: (base + timedelta(seconds=tick[0])).isoformat()
        monkeypatch.setattr(routes, "now", clock)
        monkeypatch.setattr(state_store, "now", clock)
        body = {
            **command(e, device, p["plan_id"], "mission.upload", "expires"),
            "expires_at": (base + timedelta(seconds=1)).isoformat(),
        }
        queued = post(c, "/commands", body, 202)
        tick[0] = 2
        expired = c.get("/api/v1/commands/" + queued["command_id"]).json()
        assert (
            expired["status"] == "expired"
            and expired["completed_at"] is None
            and expired.get("observed_state") is None
        )
        state = c.get(
            f"/api/v1/executions/{e['execution_id']}/devices/{device}/mission-state"
        ).json()
        assert state["uploaded_plan_id"] is None
        e = act(c, e, "disconnect")
        query = post(
            c,
            "/commands",
            command(e, device, p["plan_id"], "state.query", "disconnected"),
            202,
        )
        tick[0] = 3
        unknown = c.get("/api/v1/commands/" + query["command_id"]).json()
        assert (
            unknown["status"] == "indeterminate"
            and unknown["acknowledged_at"] is None
            and unknown.get("observed_state") is None
        )
        assert (
            c.get(
                f"/api/v1/executions/{e['execution_id']}/devices/{device}/mission-state"
            ).status_code
            == 422
        )
