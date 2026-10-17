import copy
import time

from fastapi.testclient import TestClient
import pytest

from backend.app.main import create_app
from shared.contracts import content_hash, validate_job, validate_plan


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(tmp_path / "runtime")) as c:
        yield c


def example(client):
    response = client.post("/api/v1/scenarios/examples", json={"example": "compact"})
    assert response.status_code == 201, response.text
    return response.json()


def snapshot(client, s):
    response = client.post(
        f"/api/v1/scenarios/{s['scenario_id']}/snapshots",
        json={"expected_state_version": s["state_version"]},
    )
    assert response.status_code == 201, response.text
    return response.json()


def solve(client, snap, **kwargs):
    response = client.post(
        "/api/v1/solve-jobs",
        json={"snapshot_id": snap["snapshot_id"], "time_limit_s": 5, **kwargs},
    )
    assert response.status_code == 202, response.text
    job = response.json()
    validate_job(job)
    for _ in range(250):
        job = client.get("/api/v1/solve-jobs/" + job["job_id"]).json()
        if job["job_state"] not in ("queued", "running"):
            break
        time.sleep(0.05)
    assert job["job_state"] == "completed", job
    assert job["has_validated_plan"], client.get(
        "/api/v1/solve-jobs/" + job["job_id"] + "/diagnostics"
    ).json()
    plan = client.get("/api/v1/plans/" + job["plan_id"]).json()
    validate_job(job, plan)
    validate_plan(plan, snap)
    return job, plan


def test_true_subprocess_pipeline_and_exports(client):
    s = example(client)
    snap = snapshot(client, s)
    job, plan = solve(client, snap)
    assert plan["data_origin"] == "solver" and plan["validation"]["status"] == "passed"
    for format in ("json", "csv", "geojson"):
        response = client.get(f"/api/v1/plans/{plan['plan_id']}/export?format={format}")
        assert response.status_code == 200 and len(response.content) > 100
        assert plan["plan_id"].encode() in response.content
    confirmed = client.post(
        f"/api/v1/plans/{plan['plan_id']}/confirm",
        json={"expected_state_version": 1, "idempotency_key": "CONFIRM-TEST"},
    )
    assert confirmed.status_code == 200, confirmed.text
    again = client.post(
        f"/api/v1/plans/{plan['plan_id']}/confirm",
        json={"expected_state_version": 1, "idempotency_key": "CONFIRM-TEST"},
    )
    assert again.json() == confirmed.json()
    replay = client.get(f"/api/v1/plans/{plan['plan_id']}/playback").json()
    assert replay["is_execution_fact"] is False
    assert replay["snapshot_id"] == snap["snapshot_id"]
    for r in plan["sorties"]:
        phases = sorted(
            [p for p in replay["phases"] if p["sortie_id"] == r["sortie_id"]],
            key=lambda p: p["start_s"],
        )
        assert (
            phases[0]["start_s"] == r["prepare_start_s"]
            and phases[-1]["end_s"] == r["return_s"]
        )
        assert all(
            a["end_s"] == pytest.approx(b["start_s"])
            for a, b in zip(phases, phases[1:])
        )


def test_versioning_preserves_snapshot_and_rejects_old_confirm(client):
    s = example(client)
    snap = snapshot(client, s)
    _, plan = solve(client, snap)
    changed = copy.deepcopy(s)
    changed["cargo_items"][0]["mass_kg"] += 0.5
    response = client.put(
        "/api/v1/scenarios/" + s["scenario_id"],
        json={"expected_state_version": 1, "scenario": changed},
    )
    assert response.status_code == 200, response.text
    assert response.json()["state_version"] == 2
    saved = client.get("/api/v1/snapshots/" + snap["snapshot_id"]).json()
    assert saved == snap and saved["content_hash"] == content_hash(saved["scenario"])
    old = client.post(
        f"/api/v1/plans/{plan['plan_id']}/confirm",
        json={"expected_state_version": 2, "idempotency_key": "STALE"},
    )
    assert old.status_code == 409
    conflict = client.put(
        "/api/v1/scenarios/" + s["scenario_id"],
        json={"expected_state_version": 1, "scenario": changed},
    )
    assert conflict.status_code == 409


def test_events_idempotent_and_true_replan(client):
    s = example(client)
    snap = snapshot(client, s)
    _, old = solve(client, snap)
    uid = old["sorties"][0]["drone_id"]
    event = {
        "schema_version": s["schema_version"],
        "event_id": "EVT-API-001",
        "scenario_id": s["scenario_id"],
        "expected_state_version": 1,
        "event_type": "drone.unavailable",
        "occurred_at": "2026-10-17T08:00:00+08:00",
        "received_at": "2026-10-17T08:00:01+08:00",
        "effective_time_s": 0,
        "actor": "simulation",
        "reason": "未起飞机体故障测试",
        "payload": {"drone_id": uid},
    }
    first = client.post("/api/v1/events", json=event)
    assert first.status_code == 200, first.text
    duplicate = client.post("/api/v1/events", json=event)
    assert (
        duplicate.status_code == 200
        and duplicate.json()["state_version_after"] == 2
        and not duplicate.json()["applied"]
    )
    changed = {**event, "reason": "不同内容"}
    assert client.post("/api/v1/events", json=changed).status_code == 409
    new_s = client.get("/api/v1/scenarios/" + s["scenario_id"]).json()
    new_snap = snapshot(client, new_s)
    _, new = solve(
        client,
        new_snap,
        mode="replan",
        parent_plan_id=old["plan_id"],
        event_id=event["event_id"],
    )
    assert all(r["drone_id"] != uid for r in new["sorties"])
    assert client.get("/api/v1/plans/" + old["plan_id"]).json() == old
    comparison = client.get(
        f"/api/v1/plans/{old['plan_id']}/comparison?other_plan_id={new['plan_id']}"
    ).json()
    assert not comparison["same_snapshot"] and comparison["warnings"]


def test_cancel_is_real_and_idempotent(client):
    s = example(client)
    snap = snapshot(client, s)
    response = client.post(
        "/api/v1/solve-jobs",
        json={"snapshot_id": snap["snapshot_id"], "time_limit_s": 30},
    )
    jid = response.json()["job_id"]
    canceled = client.post("/api/v1/solve-jobs/" + jid + "/cancel")
    assert canceled.status_code == 202 and canceled.json()["job_state"] == "canceled"
    time.sleep(0.15)
    assert client.get("/api/v1/solve-jobs/" + jid).json()["job_state"] == "canceled"
    assert (
        client.post("/api/v1/solve-jobs/" + jid + "/cancel").json()["job_state"]
        == "canceled"
    )


def test_invalid_body_and_reference_are_structured(client):
    response = client.post("/api/v1/scenarios/import", json={"name": "broken"})
    assert (
        response.status_code == 422
        and response.json()["error"]["code"] == "SCHEMA_INVALID"
    )
    assert client.get("/api/v1/plans/NO-SUCH-PLAN").status_code == 404


def test_import_does_not_self_certify_verified_origin(client):
    source = example(client)
    imported = client.post("/api/v1/scenarios/import", json=source)
    assert imported.status_code == 201
    assert imported.json()["data_origin"] == "user_input"


def test_worker_launch_failure_is_terminal(client, monkeypatch):
    s = example(client)
    snap = snapshot(client, s)

    def fail(*args, **kwargs):
        raise OSError("simulated process launch failure")

    monkeypatch.setattr("backend.app.jobs.subprocess.Popen", fail)
    response = client.post(
        "/api/v1/solve-jobs",
        json={"snapshot_id": snap["snapshot_id"], "time_limit_s": 5},
    )
    jid = response.json()["job_id"]
    for _ in range(50):
        job = client.get("/api/v1/solve-jobs/" + jid).json()
        if job["job_state"] == "failed":
            break
        time.sleep(0.02)
    assert job["job_state"] == "failed" and not job["has_validated_plan"]
    assert job["plan_id"] is None


def test_restart_keeps_scenarios_and_plan(tmp_path):
    app = create_app(tmp_path / "db")
    with TestClient(app) as client:
        s = example(client)
        snap = snapshot(client, s)
        _, plan = solve(client, snap)
    with TestClient(create_app(tmp_path / "db")) as client:
        assert client.get("/api/v1/scenarios/" + s["scenario_id"]).json() == s
        assert client.get("/api/v1/plans/" + plan["plan_id"]).json() == plan
