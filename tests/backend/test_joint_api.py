import time

from fastapi.testclient import TestClient
from sqlalchemy import select

from backend.app.main import create_app
from backend.app.storage import ReservationRow
from shared.contracts import content_hash


def test_relay_fault_is_versioned_idempotent_and_rejects_future_execution(tmp_path):
    app = create_app(tmp_path / "runtime")
    with TestClient(app) as client:
        s = client.post(
            "/api/v1/scenarios/examples", json={"example": "compact"}
        ).json()
        sid = s["scenario_id"]
        s["communication"] = client.get(
            f"/api/v1/scenarios/{sid}/communication-template"
        ).json()
        s["policy"]["requires_communication"] = True
        s = client.put(
            f"/api/v1/scenarios/{sid}",
            json={"expected_state_version": 1, "scenario": s},
        ).json()
        event = dict(
            schema_version=s["schema_version"],
            event_id="EVT-RELAY-FAULT",
            scenario_id=sid,
            expected_state_version=2,
            event_type="drone.unavailable",
            occurred_at=s["start_time"],
            received_at=s["start_time"],
            effective_time_s=30,
            actor="simulation",
            reason="中继机未起飞退出",
            payload={"drone_id": "R01"},
        )
        rejected = client.post("/api/v1/events", json=event)
        assert rejected.status_code == 422
        assert client.get(f"/api/v1/scenarios/{sid}").json() == s
        event["effective_time_s"] = 0
        accepted = client.post("/api/v1/events", json=event)
        assert accepted.status_code == 200, accepted.text
        assert accepted.json()["state_version_after"] == 3
        current = client.get(f"/api/v1/scenarios/{sid}").json()
        assert current["communication"]["relay_drones"][0]["status"] == "unavailable"
        assert current["drones"] == s["drones"]
        duplicate = client.post("/api/v1/events", json=event)
        assert duplicate.status_code == 200 and not duplicate.json()["applied"]
        assert client.get(f"/api/v1/scenarios/{sid}").json() == current


def test_real_joint_worker_shared_ground_confirmation_and_roundtrip(tmp_path):
    app = create_app(tmp_path / "runtime")
    with TestClient(app) as client:
        s = client.post(
            "/api/v1/scenarios/examples", json={"example": "compact"}
        ).json()
        sid = s["scenario_id"]
        template = client.get(f"/api/v1/scenarios/{sid}/communication-template")
        assert template.status_code == 200, template.text
        assert client.get(f"/api/v1/scenarios/{sid}").json() == s
        assert template.json()["gateway"]["antenna_height_m"] == 20
        s["communication"] = template.json()
        s["policy"]["requires_communication"] = True
        s["resource_limits"] = {"prep_slots": 1, "charging_ports": 2}
        saved = client.put(
            f"/api/v1/scenarios/{sid}",
            json={"expected_state_version": 1, "scenario": s},
        )
        assert saved.status_code == 200, saved.text
        s = saved.json()
        snap = client.post(
            f"/api/v1/scenarios/{sid}/snapshots", json={"expected_state_version": 2}
        ).json()
        assert snap["content_hash"] == content_hash(s)
        receipt = client.post(
            "/api/v1/solve-jobs",
            json={"snapshot_id": snap["snapshot_id"], "time_limit_s": 60},
        )
        assert receipt.status_code == 202, receipt.text
        job = receipt.json()
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline:
            job = client.get(f"/api/v1/solve-jobs/{job['job_id']}").json()
            if job["job_state"] not in ["queued", "running"]:
                break
            time.sleep(0.1)
        assert job["has_validated_plan"], job
        plan = client.get(f"/api/v1/plans/{job['plan_id']}").json()
        assert (
            plan["relay_sorties"]
            and plan["communication_report"]["coverage_gap_s"] == 0
        )
        analysis = client.get(f"/api/v1/plans/{plan['plan_id']}/analysis")
        assert analysis.status_code == 200, analysis.text
        a = analysis.json()
        assert a["prep_peak"] <= 1 and a["charge_peak"] <= 2
        assert {"relay_drone", "relay_energy"} <= {r["kind"] for r in a["resources"]}
        confirmed = client.post(
            f"/api/v1/plans/{plan['plan_id']}/confirm",
            json={"expected_state_version": 2, "idempotency_key": "CONF-JOINT"},
        )
        assert confirmed.status_code == 200, confirmed.text
        with app.state.database.session() as session:
            reservations = list(session.scalars(select(ReservationRow)))
            assert sum(r.kind == "relay_drone" for r in reservations) == len(
                plan["relay_sorties"]
            )
            assert sum(r.kind == "relay_energy" for r in reservations) == len(
                plan["relay_sorties"]
            )
        exported = client.get(
            f"/api/v1/plans/{plan['plan_id']}/export?format=relay_csv"
        )
        assert exported.status_code == 200 and "component_id" in exported.text
        geo = client.get(
            f"/api/v1/plans/{plan['plan_id']}/export?format=geojson"
        ).json()
        assert sum(
            f["properties"].get("kind") == "relay" for f in geo["features"]
        ) == len(plan["relay_sorties"])
        xlsx = client.get(f"/api/v1/scenarios/{sid}/template?format=xlsx")
        preview = client.post(
            f"/api/v1/scenarios/import-file?scenario_id={sid}",
            files={"file": ("joint.xlsx", xlsx.content)},
        )
        assert preview.status_code == 200, preview.text
        assert preview.json()["scenario"]["communication"] == s["communication"]
