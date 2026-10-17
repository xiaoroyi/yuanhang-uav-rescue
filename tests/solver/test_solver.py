import copy

import pytest

from shared.contracts import content_hash, validate_outcome
from solver.adapters.contest import compact_scenario, contest_scenario
from solver.physics import charge_seconds, supercover_cells
from solver.public_api import replan, solve, validate


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


def test_original_resources_come_from_tables():
    s = contest_scenario()
    assert len(s["cargo_items"]) == 80 and len(s["sites"]) == 15
    assert [d["type_id"] for d in s["drones"]].count("A") == 4
    assert [d["type_id"] for d in s["drones"]].count("B") == 2
    assert [b["compatible_type_id"] for b in s["batteries"]].count("A") == 6
    assert (
        sum(t["charge_model"]["parameters"]["full_charge_s"] for t in s["drone_types"])
        == 7200
    )


def test_real_plan_and_input_immutability(case):
    snapshot, options = case
    before = copy.deepcopy(snapshot)
    result = solve(snapshot, options)
    assert result["solver_status"] == "FEASIBLE", result
    assert result["plan"]["validation"]["status"] == "passed"
    assert sum(len(r["cargo_ids"]) for r in result["plan"]["sorties"]) == len(
        snapshot["scenario"]["cargo_items"]
    )
    validate_outcome(result, snapshot)
    assert snapshot == before


def test_no_drone_is_proved_infeasible(case):
    snapshot, options = case
    snapshot["scenario"]["drones"] = []
    snapshot["content_hash"] = content_hash(snapshot["scenario"])
    result = solve(snapshot, options)
    assert result["solver_status"] == "INFEASIBLE" and result["plan"] is None


def test_missing_communication_is_not_success(case):
    snapshot, options = case
    snapshot["scenario"]["policy"]["requires_communication"] = True
    snapshot["content_hash"] = content_hash(snapshot["scenario"])
    options["requested_model_scope"].append("communication")
    result = solve(snapshot, options)
    assert (
        result["solver_status"] == "UNKNOWN"
        and result["stop_reason"] == "unsupported_scope"
    )


def test_mutations_rejected_by_independent_rebuild(case):
    snapshot, options = case
    result = solve(snapshot, options)
    plan = result["plan"]
    assert plan
    for field, value in [
        ("energy_kwh", 0),
        ("return_soc", 1),
        ("return_s", 1),
        ("battery_released_s", 1),
    ]:
        changed = copy.deepcopy(plan)
        changed["sorties"][0][field] = value
        assert validate(snapshot, changed)["status"] == "failed", field
    changed = copy.deepcopy(plan)
    changed["sorties"].append(copy.deepcopy(changed["sorties"][0]))
    changed["sorties"][-1]["sortie_id"] = "DUPLICATE"
    assert validate(snapshot, changed)["status"] == "failed"


def test_two_objectives_compute_independently(case):
    snapshot, options = case
    time_result = solve(snapshot, options)
    options = {**options, "objective": "energy", "plan_id": "PLAN-ENERGY"}
    energy_result = solve(snapshot, options)
    assert time_result["plan"] and energy_result["plan"]
    assert energy_result["plan"]["objective"] == "energy"
    validate_outcome(energy_result, snapshot)


def test_unstarted_drone_failure_replans_new_version(case):
    snapshot, options = case
    old = solve(snapshot, options)["plan"]
    assert old
    failed = old["sorties"][0]["drone_id"]
    before = copy.deepcopy(old)
    s = snapshot["scenario"]
    next(d for d in s["drones"] if d["drone_id"] == failed)["status"] = "unavailable"
    s["state_version"] = 2
    snapshot.update(
        snapshot_id="SNAP-TEST-002",
        scenario_state_version=2,
        content_hash=content_hash(s),
    )
    event = {"event_id": "EVT-TEST", "event_type": "drone.unavailable"}
    options.update(
        mode="replan",
        plan_id="PLAN-REPLAN",
        snapshot_id=snapshot["snapshot_id"],
        parent_plan_id=old["plan_id"],
        event_id=event["event_id"],
    )
    result = replan(snapshot, old, event, options)
    assert result["plan"], result
    assert all(r["drone_id"] != failed for r in result["plan"]["sorties"])
    assert result["plan"]["scenario_state_version"] == 2 and old == before


def test_charge_and_closed_cell_boundaries(case):
    typ = case[0]["scenario"]["drone_types"][0]
    assert charge_seconds(typ, 1) == 0
    assert charge_seconds(typ, 0) == pytest.approx(1800)
    assert charge_seconds(typ, 0.9) == pytest.approx(630)
    assert {(0, 0), (0, 1), (1, 0), (1, 1)} <= supercover_cells(1, 1, 1.5, 1.5)


def test_charging_batteries_finish_initial_charge_before_assignment(case):
    snap, options = case
    for b in snap["scenario"]["batteries"]:
        b.update(status="charging", soc=0.9)
    snap["content_hash"] = content_hash(snap["scenario"])
    result = solve(snap, options)
    assert result["plan"], result
    validate_outcome(result, snap)
    types = {t["type_id"]: t for t in snap["scenario"]["drone_types"]}
    for b in snap["scenario"]["batteries"]:
        uses = [
            r for r in result["plan"]["sorties"] if r["battery_id"] == b["battery_id"]
        ]
        if uses:
            assert (
                min(r["prepare_start_s"] for r in uses)
                >= charge_seconds(types[b["compatible_type_id"]], 0.9) - 1e-7
            )
