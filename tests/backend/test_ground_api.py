import time

from fastapi.testclient import TestClient
from sqlalchemy import select

from backend.app.main import create_app
from backend.app.storage import ReservationRow
from shared.contracts import content_hash


def test_finite_ground_worker_analysis_confirm_export_and_old_snapshot(tmp_path):
    app = create_app(tmp_path / "runtime")
    with TestClient(app) as client:
        s = client.post(
            "/api/v1/scenarios/examples", json={"example": "compact"}
        ).json()
        old = client.post(
            f"/api/v1/scenarios/{s['scenario_id']}/snapshots",
            json={"expected_state_version": 1},
        ).json()
        s["resource_limits"] = {"prep_slots": 1, "charging_ports": 1}
        s["batteries"][0]["soc"] = 0.6
        for demand in s["demands"]:
            if demand["hard_deadline_s"] is not None:
                demand["hard_deadline_s"] = 100000.0
        saved = client.put(
            f"/api/v1/scenarios/{s['scenario_id']}",
            json={"expected_state_version": 1, "scenario": s},
        )
        assert saved.status_code == 200, saved.text
        s = saved.json()
        snap = client.post(
            f"/api/v1/scenarios/{s['scenario_id']}/snapshots",
            json={"expected_state_version": 2},
        ).json()
        assert snap["content_hash"] == content_hash(s)
        job = client.post(
            "/api/v1/solve-jobs",
            json={"snapshot_id": snap["snapshot_id"], "time_limit_s": 10},
        ).json()
        for _ in range(220):
            job = client.get(f"/api/v1/solve-jobs/{job['job_id']}").json()
            if job["job_state"] not in ["queued", "running"]:
                break
            time.sleep(0.05)
        assert job["job_state"] == "completed" and job["has_validated_plan"], job
        plan = client.get(f"/api/v1/plans/{job['plan_id']}").json()
        assert (
            "ground_resource" in plan["model_scope"]
            and len(plan["initial_charges"]) == 1
        )
        analysis = client.get(f"/api/v1/plans/{job['plan_id']}/analysis").json()
        assert analysis["resource_limits"] == s["resource_limits"]
        assert (
            analysis["charge_peak"] <= 1
            and analysis["prep_peak"] <= 1
            and analysis["charge_wait_s"] > 0
        )
        assert all(r["utilization"] <= 1 + 1e-9 for r in analysis["resources"])
        confirmed = client.post(
            f"/api/v1/plans/{job['plan_id']}/confirm",
            json={"expected_state_version": 2, "idempotency_key": "GROUND-CONFIRM"},
        )
        assert confirmed.status_code == 200, confirmed.text
        with app.state.database.session() as session:
            rows = list(session.scalars(select(ReservationRow)))
            assert any(r.kind == "charging_port" for r in rows)
            assert any(r.kind == "prep_slot" for r in rows)
            assert sum(r.kind == "battery" for r in rows) == len(plan["sorties"]) + 1
        exported = client.get(f"/api/v1/plans/{job['plan_id']}/export?format=csv")
        assert (
            "charge_start_s" in exported.text and "battery_released_s" in exported.text
        )
        report = client.get(f"/api/v1/plans/{job['plan_id']}/report")
        assert (
            report.status_code == 200
            and "初始补能与排队" in report.text
            and "准备工位1个" in report.text
        )
        assert client.get(f"/api/v1/snapshots/{old['snapshot_id']}").json() == old
        template = client.get(
            f"/api/v1/scenarios/{s['scenario_id']}/template?format=xlsx"
        )
        preview = client.post(
            f"/api/v1/scenarios/import-file?scenario_id={s['scenario_id']}",
            files={
                "file": (
                    "scene.xlsx",
                    template.content,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            },
        )
        assert preview.status_code == 200, preview.text
        assert preview.json()["scenario"]["resource_limits"] == s["resource_limits"]
