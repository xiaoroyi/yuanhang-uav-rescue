import pytest
from shared.contracts import content_hash
from solver.adapters.contest import compact_scenario


@pytest.fixture
def case():
    s = compact_scenario()
    snapshot = {
        "schema_version": s["schema_version"],
        "snapshot_id": "SNAP-TEST-001",
        "scenario_id": s["scenario_id"],
        "scenario_state_version": 1,
        "content_hash": content_hash(s),
        "created_at": s["start_time"],
        "scenario": s,
    }
    options = {
        "schema_version": s["schema_version"],
        "plan_id": "PLAN-TEST-001",
        "snapshot_id": snapshot["snapshot_id"],
        "objective": "time",
        "mode": "quick",
        "time_limit_s": 5,
        "seed": 42,
        "parent_plan_id": None,
        "event_id": None,
        "requested_model_scope": [
            "cargo_unique",
            "capacity",
            "inventory",
            "aircraft",
            "battery",
            "time_window",
            "energy",
            "terrain",
        ],
        "allow_partial_service": False,
    }
    return snapshot, options
