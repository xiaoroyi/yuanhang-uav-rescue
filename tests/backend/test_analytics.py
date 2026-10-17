import time

from fastapi.testclient import TestClient
import pytest

from backend.app.main import create_app
from shared.contracts import content_hash
from solver.analysis import interval_peak


def real_plan(client, scene):
    snap = client.post(
        f"/api/v1/scenarios/{scene['scenario_id']}/snapshots",
        json={"expected_state_version": scene["state_version"]},
    ).json()
    response = client.post(
        "/api/v1/solve-jobs",
        json={"snapshot_id": snap["snapshot_id"], "time_limit_s": 8},
    )
    assert response.status_code == 202, response.text
    jid = response.json()["job_id"]
    for _ in range(250):
        job = client.get("/api/v1/solve-jobs/" + jid).json()
        if job["job_state"] not in ("queued", "running"):
            break
        time.sleep(0.05)
    assert job["job_state"] == "completed" and job["has_validated_plan"], job
    return client.get("/api/v1/plans/" + job["plan_id"]).json(), snap


def test_plan_analysis_is_snapshot_bound_and_peak_is_half_open(tmp_path):
    assert interval_peak([(0, 1), (1, 2)]) == 1
    assert interval_peak([(0, 2), (1, 3), (2, 2)]) == 2
    with TestClient(create_app(tmp_path / "runtime")) as client:
        scene = client.post(
            "/api/v1/scenarios/examples", json={"example": "compact"}
        ).json()
        plan, snap = real_plan(client, scene)
        response = client.get(f"/api/v1/plans/{plan['plan_id']}/analysis")
        assert response.status_code == 200, response.text
        a = response.json()
        assert a["snapshot_id"] == plan["snapshot_id"]
        assert a["delivery"]["hard_violation_count"] == 0
        assert len(a["resources"]) == len(scene["drones"]) + len(scene["batteries"])
        assert all(0 <= r["utilization"] <= 1 + 1e-9 for r in a["resources"])
        windows = a["charge_windows"]
        assert a["charge_peak"] == max(
            sum(w["start_s"] <= t < w["end_s"] for w in windows)
            for t in [w["start_s"] for w in windows]
        )
        assert client.get("/api/v1/plans/" + plan["plan_id"]).json() == plan
        changed = scene.copy()
        changed["name"] = "更新后的当前场景"
        assert (
            client.put(
                "/api/v1/scenarios/" + scene["scenario_id"],
                json={"expected_state_version": 1, "scenario": changed},
            ).status_code
            == 200
        )
        assert client.get(f"/api/v1/plans/{plan['plan_id']}/analysis").json() == a
        assert client.get("/api/v1/snapshots/" + snap["snapshot_id"]).json() == snap


def test_what_if_records_lineage_preserves_baseline_and_really_solves(tmp_path):
    directory = tmp_path / "runtime"
    with TestClient(create_app(directory)) as client:
        scene = client.post(
            "/api/v1/scenarios/examples", json={"example": "compact"}
        ).json()
        baseline, _ = real_plan(client, scene)
        body = {
            "expected_state_version": 1,
            "source_plan_id": baseline["plan_id"],
            "name": "增配与压力验证",
            "additions": [{"type_id": "C", "drones": 1, "batteries": 1}],
            "energy_multiplier": 1.1,
            "flight_time_multiplier": 1.05,
            "battery_soh_multiplier": 0.9,
            "min_return_soc": 0.25,
            "noncritical_deadline_multiplier": 1.2,
        }
        response = client.post(
            f"/api/v1/scenarios/{scene['scenario_id']}/what-if", json=body
        )
        assert response.status_code == 201, response.text
        receipt = response.json()
        derived = receipt["scenario"]
        assert (
            derived["scenario_id"] != scene["scenario_id"]
            and derived["state_version"] == 1
        )
        assert derived["data_origin"] == "user_input"
        assert len(derived["drones"]) == len(scene["drones"]) + 1
        assert len(derived["batteries"]) == len(scene["batteries"]) + 1
        assert all(b["soh"] == pytest.approx(0.9) for b in derived["batteries"])
        assert derived["policy"]["min_return_soc"] == 0.25
        for old, new in zip(scene["demands"], derived["demands"]):
            assert old["hard_deadline_s"] == new["hard_deadline_s"]
            expected = old["expected_deadline_s"] * (
                1.2 if old["hard_deadline_s"] is None else 1
            )
            assert new["expected_deadline_s"] == pytest.approx(expected)
        assert receipt["origin"]["source_content_hash"] == content_hash(scene)
        assert client.get("/api/v1/scenarios/" + scene["scenario_id"]).json() == scene
        plan, _ = real_plan(client, derived)
        assert (
            plan["data_origin"] == "solver" and plan["validation"]["status"] == "passed"
        )
        assert plan["snapshot_id"] != baseline["snapshot_id"]
    with TestClient(create_app(directory)) as client:
        assert (
            client.get(f"/api/v1/scenarios/{derived['scenario_id']}/origin").json()
            == receipt["origin"]
        )
        history = client.get(f"/api/v1/scenarios/{scene['scenario_id']}/what-if")
        assert history.status_code == 200, history.text
        assert history.json()[0]["plan"]["plan_id"] == plan["plan_id"]
        assert history.json()[0]["origin"] == receipt["origin"]
        changed = {**derived, "name": "已经编辑的试算场景"}
        assert (
            client.put(
                "/api/v1/scenarios/" + derived["scenario_id"],
                json={"expected_state_version": 1, "scenario": changed},
            ).status_code
            == 200
        )
        record = client.get(f"/api/v1/scenarios/{scene['scenario_id']}/what-if").json()[
            0
        ]
        assert record["scenario_state_version"] == 2
        assert record["plan"]["scenario_state_version"] == 1
        assert record["plan"]["plan_id"] == plan["plan_id"]


def test_what_if_rejects_stale_version_and_missing_resources_without_side_effects(
    tmp_path,
):
    with TestClient(create_app(tmp_path / "runtime")) as client:
        s = client.post(
            "/api/v1/scenarios/examples", json={"example": "compact"}
        ).json()
        assert (
            client.post(
                f"/api/v1/scenarios/{s['scenario_id']}/what-if",
                json={"expected_state_version": 2},
            ).status_code
            == 409
        )
        invalid = client.post(
            f"/api/v1/scenarios/{s['scenario_id']}/what-if",
            json={
                "expected_state_version": 1,
                "additions": [{"type_id": "MISSING", "drones": 1}],
            },
        )
        assert invalid.status_code == 422
        assert len(client.get("/api/v1/scenarios").json()) == 1
