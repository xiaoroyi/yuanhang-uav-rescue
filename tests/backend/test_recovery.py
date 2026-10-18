from fastapi.testclient import TestClient

from backend.app.main import create_app


def test_restart_marks_queued_jobs_failed_and_lists_them_for_client_recovery(
    tmp_path, monkeypatch
):
    directory = tmp_path / "runtime"
    app = create_app(directory)
    with TestClient(app) as client:
        scene = client.post(
            "/api/v1/scenarios/examples", json={"example": "compact"}
        ).json()
        snapshot = client.post(
            f"/api/v1/scenarios/{scene['scenario_id']}/snapshots",
            json={"expected_state_version": 1},
        ).json()
        # Simulate a service exit after persisting a queue entry but before starting its worker.
        monkeypatch.setattr(app.state.jobs, "submit", lambda *_args: None)
        response = client.post(
            "/api/v1/solve-jobs",
            json={"snapshot_id": snapshot["snapshot_id"], "time_limit_s": 5},
        )
        assert response.status_code == 202
        job = response.json()
        assert job["job_state"] == "queued"
    with TestClient(create_app(directory)) as client:
        response = client.get(f"/api/v1/scenarios/{scene['scenario_id']}/solve-jobs")
        assert response.status_code == 200, response.text
        recovered = response.json()
        assert len(recovered) == 1 and recovered[0]["job_id"] == job["job_id"]
        assert recovered[0]["job_state"] == "failed"
        assert recovered[0]["plan_id"] is None and recovered[0]["error"]
        assert (
            client.get(f"/api/v1/scenarios/{scene['scenario_id']}/plans").json() == []
        )
