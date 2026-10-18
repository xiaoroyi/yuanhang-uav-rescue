"""Re-verify a saved joint candidate, then simulate real model stages and ledger."""

import copy
import json
from pathlib import Path

from fastapi.testclient import TestClient
import pytest

from backend.app.main import create_app
from backend.app.storage import ScenarioRow, VersionRow, SnapshotRow, PlanRow
from backend.app.jobs import now
from shared.contracts import content_hash
from solver.public_api import validate
from solver.stages import stage_analysis


def test_joint_stages_and_persistent_relay_execution(tmp_path):
    root = Path(__file__).resolve().parents[2]
    source = json.loads(
        (root / "evidence/solver/joint-compact.json").read_text(encoding="utf-8")
    )
    snap = source["snapshot"]
    plan = source["outcome"]["plan"]
    scenario = snap["scenario"]
    # Historical evidence is only an input candidate. Independently rebuild it now.
    assert validate(snap, plan)["status"] == "passed"
    original = copy.deepcopy(plan)
    stages = stage_analysis(snap, plan)
    for relay in plan["relay_sorties"]:
        rows = [
            r
            for r in stages["trajectory_segments"]
            if r["sortie_id"] == relay["relay_sortie_id"]
        ]
        assert sum(r["energy_kwh"] for r in rows) == pytest.approx(relay["energy_kwh"])
        assert rows[-1]["soc_end"] == pytest.approx(relay["return_soc"])
        assert rows[0]["start_s"] == relay["prepare_start_s"]
        assert rows[-1]["end_s"] == pytest.approx(relay["drone_released_s"])
        assert any(r["phase"] == "relay_service" for r in rows)
    assert plan == original
    app = create_app(tmp_path / "runtime")
    with TestClient(app) as client:
        with app.state.database.session(immediate=True) as session:
            session.add(
                ScenarioRow(
                    id=scenario["scenario_id"],
                    name=scenario["name"],
                    version=scenario["state_version"],
                    content=scenario,
                    active_plan_id=None,
                    updated_at=now(),
                )
            )
            session.add(
                VersionRow(
                    scenario_id=scenario["scenario_id"],
                    version=scenario["state_version"],
                    content=scenario,
                    content_hash=content_hash(scenario),
                )
            )
            session.add(
                SnapshotRow(
                    id=snap["snapshot_id"],
                    scenario_id=scenario["scenario_id"],
                    version=scenario["state_version"],
                    content=snap,
                )
            )
            session.add(
                PlanRow(
                    id=plan["plan_id"],
                    scenario_id=scenario["scenario_id"],
                    snapshot_id=snap["snapshot_id"],
                    version=scenario["state_version"],
                    content=plan,
                    confirmed_at=None,
                )
            )
        response = client.post(
            "/api/v1/missions",
            json={
                "name": "Verified joint simulation regression",
                "scenario_id": scenario["scenario_id"],
                "idempotency_key": "joint-create",
            },
        )
        assert response.status_code == 201, response.text
        m = response.json()
        response = client.post(
            f"/api/v1/plans/{plan['plan_id']}/confirm",
            json={
                "expected_state_version": scenario["state_version"],
                "idempotency_key": "joint-confirm",
            },
        )
        assert response.status_code == 200, response.text
        response = client.post(
            "/api/v1/executions",
            json={
                "mission_id": m["mission_id"],
                "confirmed_plan_id": plan["plan_id"],
                "expected_revision": 1,
                "idempotency_key": "joint-execution",
            },
        )
        assert response.status_code == 201, response.text
        e = response.json()
        eid = e["execution_id"]
        relay = next(
            r
            for r in plan["relay_sorties"]
            if r["service_end_s"] > r["service_start_s"]
        )
        middle = (relay["service_start_s"] + relay["service_end_s"]) / 2
        response = client.post(
            f"/api/v1/executions/{eid}/simulation/actions",
            json={
                "action": "advance",
                "target_time_s": middle,
                "expected_revision": e["revision"],
                "idempotency_key": "middle",
            },
        )
        assert response.status_code == 200, response.text
        e = response.json()
        observed = next(
            t for t in e["telemetry"] if t["device_id"] == relay["drone_id"]
        )
        assert observed["phase"] == "relay_service" and observed["battery_id"] is None
        assert observed["component_id"] == relay["component_id"]
        assert observed["coordinates"] == pytest.approx(relay["station_coordinates"])
        assert any(
            f["kind"] == "relay_service_started"
            and f["component_id"] == relay["component_id"]
            for f in e["facts"]
        )
        end = (
            max(
                [r["battery_released_s"] for r in plan["sorties"]]
                + [r["component_released_s"] for r in plan["relay_sorties"]]
            )
            + 1
        )
        response = client.post(
            f"/api/v1/executions/{eid}/simulation/actions",
            json={
                "action": "advance",
                "target_time_s": end,
                "expected_revision": e["revision"],
                "idempotency_key": "end",
            },
        )
        assert response.status_code == 200, response.text
        e = response.json()
        assert e["status"] == "completed" and len(e["delivered_cargo_ids"]) == 32
        assert len([f for f in e["facts"] if f["kind"] == "relay_energy_ready"]) == len(
            plan["relay_sorties"]
        )
        assert client.get(f"/api/v1/executions/{eid}").json()["facts"] == e["facts"]
        with app.state.database.session() as session:
            assert session.get(PlanRow, plan["plan_id"]).content == original
