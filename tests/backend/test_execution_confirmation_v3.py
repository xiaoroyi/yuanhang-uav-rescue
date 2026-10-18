"""A static confirmation must never replace an existing execution's reservations."""

import copy
import importlib.util
from pathlib import Path
from sqlalchemy import select
from fastapi.testclient import TestClient
import pytest
from backend.app.main import create_app
from backend.app.storage import ReservationRow

# Reuse the established actual worker setup, rather than stub a feasible plan.
spec = importlib.util.spec_from_file_location(
    "execution_setup_v3", Path(__file__).with_name("test_execution_v2.py")
)
execution_fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(execution_fixture)


@pytest.mark.parametrize("state", ["ready", "paused"])
def test_live_instance_rejects_new_confirmation_without_mutating_reservations(
    tmp_path, state
):
    app = create_app(tmp_path / "runtime")
    with TestClient(app) as c:
        m, s, p, e = execution_fixture.setup(c)
        if state == "paused":
            e = execution_fixture.act(
                c,
                e,
                "advance",
                target_time_s=min(r["takeoff_s"] for r in p["sorties"]) + 15,
            )

        def reservations():
            with app.state.database.session() as session:
                return sorted(
                    (r.plan_id, r.kind, r.resource_id, r.start_s, r.end_s)
                    for r in session.scalars(
                        select(ReservationRow).where(
                            ReservationRow.scenario_id == s["scenario_id"]
                        )
                    )
                )

        before = reservations()
        old_plan = copy.deepcopy(c.get("/api/v1/plans/" + p["plan_id"]).json())
        facts = c.get("/api/v1/executions/" + e["execution_id"]).json()["facts"]
        response = c.post(
            "/api/v1/plans/" + p["plan_id"] + "/confirm",
            json={
                "expected_state_version": s["state_version"],
                "idempotency_key": "new-confirm",
            },
        )
        assert response.status_code == 409, response.text
        assert response.json()["error"]["code"] == "RESOURCE_CONFLICT"
        assert reservations() == before
        assert c.get("/api/v1/plans/" + p["plan_id"]).json() == old_plan
        assert c.get("/api/v1/executions/" + e["execution_id"]).json()["facts"] == facts
        replay = c.post(
            "/api/v1/plans/" + p["plan_id"] + "/confirm",
            json={
                "expected_state_version": s["state_version"],
                "idempotency_key": "confirm",
            },
        )
        assert replay.status_code == 200, replay.text
        assert reservations() == before
