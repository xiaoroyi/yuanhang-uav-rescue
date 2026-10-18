import time

from fastapi.testclient import TestClient

from backend.app.main import create_app
from shared.contracts import content_hash


def test_real_80_box_partition_uses_frozen_snapshot_after_current_scene_changes(
    tmp_path,
):
    with TestClient(create_app(tmp_path / "runtime")) as client:
        s = client.post(
            "/api/v1/scenarios/examples", json={"example": "contest"}
        ).json()
        sid = s["scenario_id"]
        s["communication"] = client.get(
            f"/api/v1/scenarios/{sid}/communication-template"
        ).json()
        s["policy"]["requires_communication"] = True
        saved = client.put(
            f"/api/v1/scenarios/{sid}",
            json={"expected_state_version": 1, "scenario": s},
        )
        assert saved.status_code == 200, saved.text
        s = saved.json()
        snap = client.post(
            f"/api/v1/scenarios/{sid}/snapshots", json={"expected_state_version": 2}
        ).json()
        job = client.post(
            "/api/v1/solve-jobs",
            json={"snapshot_id": snap["snapshot_id"], "time_limit_s": 60},
        ).json()
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline:
            job = client.get(f"/api/v1/solve-jobs/{job['job_id']}").json()
            if job["job_state"] not in ["queued", "running"]:
                break
            time.sleep(0.1)
        assert job["has_validated_plan"], job
        pid = job["plan_id"]
        plan = client.get(f"/api/v1/plans/{pid}").json()
        first = client.get(f"/api/v1/plans/{pid}/partition")
        assert first.status_code == 200, first.text
        report = first.json()
        assert report["status"] == "ready" and len(report["atoms"]) == 3
        assert report["snapshot_content_hash"] == snap["content_hash"]
        assert report["source_plan_hash"] == content_hash(plan)
        for drone in s["drones"]:
            if drone["type_id"] == "C":
                drone["status"] = "unavailable"
        updated = client.put(
            f"/api/v1/scenarios/{sid}",
            json={"expected_state_version": 2, "scenario": s},
        )
        assert updated.status_code == 200, updated.text
        second = client.get(f"/api/v1/plans/{pid}/partition")
        assert second.status_code == 200 and second.json() == report
        assert (
            next(r for r in report["resource_classes"] if r["key"] == "drone:C")[
                "inventory"
            ]
            == 2
        )
        assert client.get(f"/api/v1/plans/{pid}").json() == plan
