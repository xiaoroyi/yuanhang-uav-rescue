import time

from fastapi.testclient import TestClient

from backend.app.analytics import PlanAnalysis
from backend.app.main import create_app


def test_analysis_capacity_bound_uses_plan_snapshot_and_old_view_json_remains_valid(
    tmp_path,
):
    with TestClient(create_app(tmp_path / "runtime")) as client:
        scene = client.post(
            "/api/v1/scenarios/examples", json={"example": "compact"}
        ).json()
        sid = scene["scenario_id"]
        snap = client.post(
            f"/api/v1/scenarios/{sid}/snapshots", json={"expected_state_version": 1}
        ).json()
        receipt = client.post(
            "/api/v1/solve-jobs",
            json={"snapshot_id": snap["snapshot_id"], "time_limit_s": 10},
        ).json()
        until = time.monotonic() + 25
        while time.monotonic() < until:
            job = client.get(f"/api/v1/solve-jobs/{receipt['job_id']}").json()
            if job["job_state"] not in ["queued", "running"]:
                break
            time.sleep(0.05)
        assert job["has_validated_plan"], job
        url = f"/api/v1/plans/{job['plan_id']}/analysis"
        response = client.get(url)
        assert response.status_code == 200, response.text
        report = response.json()
        bound = report["capacity_bound"]
        assert bound["status"] == "ready" and bound["sortie_lower_bound"] == 4
        assert bound["snapshot_content_hash"] == snap["content_hash"]
        for drone in scene["drones"]:
            if drone["type_id"] == "C":
                drone["status"] = "unavailable"
        saved = client.put(
            f"/api/v1/scenarios/{sid}",
            json={"expected_state_version": 1, "scenario": scene},
        )
        assert saved.status_code == 200, saved.text
        assert client.get(url).json()["capacity_bound"] == bound
        legacy = {
            key: value for key, value in report.items() if key != "capacity_bound"
        }
        assert "capacity_bound" not in PlanAnalysis.model_validate(legacy).model_dump(
            exclude_unset=True
        )
