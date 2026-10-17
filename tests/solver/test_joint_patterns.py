import copy
import hashlib
import json
from pathlib import Path
import pytest

from shared.contracts import content_hash, validate_outcome, validate_scenario
from solver.adapters.contest import contest_scenario, contest_communication
from solver.adapters.joint_patterns import transport_pattern
from solver.public_api import solve, validate


def case():
    s = contest_scenario()
    s["communication"] = contest_communication(s)
    s["policy"]["requires_communication"] = True
    return s


def test_grouping_provenance_and_fresh_physics_do_not_copy_old_results():
    root = Path(__file__).resolve().parents[2]
    asset = json.loads(
        (root / "solver/data/contest_joint_patterns.json").read_text(encoding="utf-8")
    )
    for source in asset["sources"]:
        assert (
            hashlib.sha256((root / source["path"]).read_bytes()).hexdigest()
            == source["sha256"]
        )
    s = case()
    validate_scenario(s)
    ids = [c["cargo_id"] for c in s["cargo_items"]]
    original, _ = transport_pattern(s, ids)
    changed = copy.deepcopy(s)
    for typ in changed["drone_types"]:
        typ["energy_model"]["parameters"]["energy_scale"] = 0.9
    rebuilt, _ = transport_pattern(changed, ids)
    assert sum(r["energy_kwh"] for r in rebuilt["sorties"]) < sum(
        r["energy_kwh"] for r in original["sorties"]
    )
    assert original["pattern_only"]
    assert transport_pattern(s, ids[:-1]) is None
    changed = copy.deepcopy(s)
    changed["communication"]["candidate_stations"] = []
    assert transport_pattern(changed, ids) is None


def test_original_80_box_joint_plan_is_recomputed_and_independently_checked():
    s = case()
    snapshot = dict(
        schema_version=s["schema_version"],
        snapshot_id="SNAP-80-JOINT",
        scenario_id=s["scenario_id"],
        scenario_state_version=s["state_version"],
        content_hash=content_hash(s),
        created_at=s["start_time"],
        scenario=s,
    )
    options = dict(
        schema_version=s["schema_version"],
        snapshot_id=snapshot["snapshot_id"],
        plan_id="PLAN-80-JOINT",
        objective="time",
        mode="quick",
        time_limit_s=60,
        seed=42,
        parent_plan_id=None,
        event_id=None,
        allow_partial_service=False,
        requested_model_scope=[
            "cargo_unique",
            "capacity",
            "inventory",
            "aircraft",
            "battery",
            "time_window",
            "energy",
            "terrain",
            "communication",
        ],
    )
    before = copy.deepcopy(snapshot)
    outcome = solve(snapshot, options)
    assert snapshot == before
    assert outcome["plan"], outcome
    validate_outcome(outcome, snapshot)
    plan = outcome["plan"]
    assert len([c for r in plan["sorties"] for c in r["cargo_ids"]]) == 80
    assert plan["relay_sorties"] and plan["communication_report"]["coverage_gap_s"] == 0
    assert validate(snapshot, plan)["status"] == "passed"
    assert any("历史分组仅作候选" in note for note in plan["solver_notes"])


@pytest.mark.parametrize(
    "problem,status",
    [
        ("mock", "UNKNOWN"),
        ("closed_base", "INFEASIBLE"),
        ("no_aircraft", "INFEASIBLE"),
        ("no_energy", "INFEASIBLE"),
        ("unknown_scope", "UNKNOWN"),
        ("unconfigured_ground", "UNKNOWN"),
    ],
)
def test_archived_pattern_cannot_bypass_common_input_guards(
    monkeypatch, problem, status
):
    import solver.joint

    s = case()
    if problem == "mock":
        s["data_origin"] = "mock"
    elif problem == "closed_base":
        s["base"]["available"] = False
    elif problem == "no_aircraft":
        for drone in s["drones"]:
            drone["status"] = "unavailable"
    elif problem == "no_energy":
        for battery in s["batteries"]:
            battery["status"] = "unavailable"
    snapshot = dict(
        schema_version=s["schema_version"],
        snapshot_id="SNAP-GUARD",
        scenario_id=s["scenario_id"],
        scenario_state_version=1,
        content_hash=content_hash(s),
        created_at=s["start_time"],
        scenario=s,
    )
    scope = [
        "cargo_unique",
        "capacity",
        "inventory",
        "aircraft",
        "battery",
        "time_window",
        "energy",
        "terrain",
        "communication",
    ]
    if problem == "unknown_scope":
        scope.append("future_model")
    elif problem == "unconfigured_ground":
        scope.append("ground_resource")
    options = dict(
        schema_version=s["schema_version"],
        snapshot_id=snapshot["snapshot_id"],
        plan_id="PLAN-GUARD",
        objective="time",
        mode="quick",
        time_limit_s=60,
        seed=42,
        parent_plan_id=None,
        event_id=None,
        allow_partial_service=False,
        requested_model_scope=scope,
    )

    def forbidden(*args, **kwargs):
        raise AssertionError("Invalid input reached joint candidate scheduling.")

    monkeypatch.setattr(solver.joint, "schedule", forbidden)
    result = solve(snapshot, options)
    assert result["plan"] is None and result["solver_status"] == status
