import copy
import json
from pathlib import Path
import time

from fastapi.testclient import TestClient

from backend.app.main import create_app


def test_weather_is_versioned_checked_and_used_by_real_worker(tmp_path):
    root = Path(__file__).resolve().parents[2]
    weather = json.loads(
        (root / "fixtures/operations/weather-manual.json").read_text(encoding="utf-8")
    )["weather"]
    with TestClient(create_app(tmp_path / "runtime")) as c:
        m = c.post(
            "/api/v1/missions",
            json={
                "name": "Weather W1 test",
                "template": "compact",
                "idempotency_key": "weather-create",
            },
        ).json()
        s = c.get("/api/v1/scenarios/" + m["current_scenario_id"]).json()
        s["cargo_items"] = s["cargo_items"][:2]
        ids = {box["demand_id"] for box in s["cargo_items"]}
        s["demands"] = [d for d in s["demands"] if d["demand_id"] in ids]
        for d in s["demands"]:
            d.update(
                required_quantity=sum(
                    box["demand_id"] == d["demand_id"] for box in s["cargo_items"]
                ),
                expected_deadline_s=None,
                hard_deadline_s=None,
            )
        for box in s["cargo_items"]:
            box.update(mass_kg=1, volume_l=1)
        s["weather"] = weather
        response = c.put(
            "/api/v1/scenarios/" + s["scenario_id"],
            json={"expected_state_version": 1, "scenario": s},
        )
        assert response.status_code == 200, response.text
        s = response.json()
        assert s["state_version"] == 2
        report = c.post(
            f"/api/v1/missions/{m['mission_id']}/preflight",
            json={"expected_revision": 1},
        ).json()
        assert report["blocking_count"] == 0, report
        assert any(
            item["code"] == "WEATHER_TYPE:A" and item["status"] == "warning"
            for item in report["checks"]
        )
        snap = c.post(
            f"/api/v1/scenarios/{s['scenario_id']}/snapshots",
            json={"expected_state_version": 2},
        ).json()
        response = c.post(
            "/api/v1/solve-jobs",
            json={"snapshot_id": snap["snapshot_id"], "time_limit_s": 5},
        )
        assert response.status_code == 202, response.text
        job = response.json()
        for _ in range(250):
            job = c.get("/api/v1/solve-jobs/" + job["job_id"]).json()
            if job["job_state"] not in ("queued", "running"):
                break
            time.sleep(0.05)
        assert job["has_validated_plan"], job
        p = c.get("/api/v1/plans/" + job["plan_id"]).json()
        assert (
            "weather_window" in p["model_scope"]
            and p["validation"]["status"] == "passed"
        )
        assert all(r["takeoff_s"] >= 600 for r in p["sorties"])
        types = {d["drone_id"]: d["type_id"] for d in s["drones"]}
        assert all(types[r["drone_id"]] == "B" for r in p["sorties"])
        c.post(
            f"/api/v1/plans/{p['plan_id']}/confirm",
            json={"expected_state_version": 2, "idempotency_key": "confirm"},
        )
        # Unsafe new conditions make the old confirmed plan stale, without rewriting it.
        next_scene = copy.deepcopy(s)
        next_scene["weather"]["wind_speed_mps"] = 30
        response = c.put(
            "/api/v1/scenarios/" + s["scenario_id"],
            json={"expected_state_version": 2, "scenario": next_scene},
        )
        assert response.status_code == 200, response.text
        report = c.post(
            f"/api/v1/missions/{m['mission_id']}/preflight",
            json={"expected_revision": 1},
        ).json()
        assert report["blocking_count"] > 0
        mission = c.get(f"/api/v1/missions/{m['mission_id']}").json()
        assert mission["active_plan_id"] is None and mission["lifecycle"] != "ready"
        assert (
            c.post(
                f"/api/v1/plans/{p['plan_id']}/confirm",
                json={"expected_state_version": 3, "idempotency_key": "unsafe-confirm"},
            ).status_code
            == 409
        )
        assert c.get("/api/v1/plans/" + p["plan_id"]).json() == p
