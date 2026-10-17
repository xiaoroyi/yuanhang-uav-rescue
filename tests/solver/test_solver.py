import copy

import pytest

from shared.contracts import content_hash, validate_outcome
from solver.adapters.contest import contest_scenario
from solver.physics import charge_seconds, supercover_cells
from solver.public_api import replan, solve, validate
from solver.dependencies import affected_closure


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


@pytest.mark.parametrize("kind", ["cargo", "drone", "battery"])
@pytest.mark.parametrize("communication", [False, True])
def test_initial_solve_cannot_silently_replace_execution_facts(
    case, kind, communication
):
    from solver.adapters.contest import contest_communication

    snapshot, options = case
    s = snapshot["scenario"]
    if communication:
        s["communication"] = contest_communication(s)
        s["policy"]["requires_communication"] = True
        options["requested_model_scope"].append("communication")
    if kind == "cargo":
        s["cargo_items"][0]["status"] = "delivered"
    elif kind == "drone":
        s["drones"][0]["status"] = "in_flight"
    else:
        s["batteries"][0]["status"] = "in_use"
    snapshot["content_hash"] = content_hash(s)
    before = copy.deepcopy(snapshot)
    outcome = solve(snapshot, options)
    assert outcome["solver_status"] == "UNKNOWN" and outcome["plan"] is None
    assert outcome["diagnostics"][0]["code"] == "UNSUPPORTED_EXECUTION_STATE"
    assert snapshot == before


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


def test_extra_inventory_can_replace_an_oversized_first_id(case):
    snapshot, options = case
    s = snapshot["scenario"]
    oversized = s["cargo_items"][0]
    replacement = {**oversized, "cargo_id": "ZZZ-FITTING-ALTERNATIVE"}
    oversized["mass_kg"] = 1000
    s["cargo_items"].append(replacement)
    snapshot["content_hash"] = content_hash(s)
    result = solve(snapshot, options)
    assert result["plan"], result
    loaded = {cid for r in result["plan"]["sorties"] for cid in r["cargo_ids"]}
    assert replacement["cargo_id"] in loaded
    assert oversized["cargo_id"] not in loaded
    validate_outcome(result, snapshot)


def test_completed_strategy_portfolio_keeps_common_priority_goal(case):
    from solver.metrics import objective_score

    snapshot, options = case
    options = {**options, "time_limit_s": 20}
    timed = solve(snapshot, options)
    energy = solve(snapshot, {**options, "objective": "energy"})
    assert timed["stop_reason"] == energy["stop_reason"] == "finished"
    assert timed["candidate_count"] == energy["candidate_count"]
    tscore = objective_score(snapshot["scenario"], timed["plan"], "energy")
    escore = objective_score(snapshot["scenario"], energy["plan"], "energy")
    assert escore[0] == pytest.approx(tscore[0])
    assert escore[1] <= tscore[1] + 1e-7


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


def test_explicit_requested_scope_is_never_silently_dropped(case):
    snap, options = case
    options["requested_model_scope"].append("communication")
    result = solve(snap, options)
    assert result["solver_status"] == "UNKNOWN" and result["plan"] is None
    assert result["stop_reason"] == "unsupported_scope"


def test_closed_base_is_infeasible_and_forged_plan_cannot_validate(case):
    snap, options = case
    plan = solve(snap, options)["plan"]
    assert plan
    snap["scenario"]["base"]["available"] = False
    snap["content_hash"] = content_hash(snap["scenario"])
    assert solve(snap, options)["solver_status"] == "INFEASIBLE"
    assert validate(snap, plan)["status"] == "failed"


def test_dependency_closure_crosses_shared_battery_then_aircraft():
    def r(identity, u, b, start):
        return {
            "sortie_id": identity,
            "drone_id": u,
            "battery_id": b,
            "prepare_start_s": start,
        }

    closure, edges = affected_closure(
        [
            r("R1", "U1", "B1", 0),
            r("R2", "U2", "B1", 100),
            r("R3", "U2", "B2", 200),
            r("R4", "U3", "B3", 300),
        ],
        {"R1"},
    )
    assert closure == {"R1", "R2", "R3"}
    assert {edge["resource_kind"] for edge in edges} == {"drone", "battery"}


def test_local_repair_retains_unaffected_reservations_when_deadlines_have_slack(case):
    snap, options = case
    for d in snap["scenario"]["demands"]:
        d.update(expected_deadline_s=None, hard_deadline_s=None)
    snap["content_hash"] = content_hash(snap["scenario"])
    options["time_limit_s"] = 10
    old = solve(snap, options)["plan"]
    assert old
    failed = "U01"
    assert any(r["drone_id"] == failed for r in old["sorties"])
    previous = copy.deepcopy(old)
    next(d for d in snap["scenario"]["drones"] if d["drone_id"] == failed)[
        "status"
    ] = "unavailable"
    snap["scenario"]["state_version"] = 2
    snap.update(
        snapshot_id="SNAP-REPAIR",
        scenario_state_version=2,
        content_hash=content_hash(snap["scenario"]),
    )
    options.update(
        mode="replan",
        snapshot_id=snap["snapshot_id"],
        plan_id="PLAN-REPAIR",
        parent_plan_id=old["plan_id"],
        event_id="EVT-REPAIR",
    )
    result = replan(
        snap,
        old,
        {"event_id": "EVT-REPAIR", "event_type": "drone.unavailable"},
        options,
    )
    assert result["plan"], result
    validate_outcome(result, snap)
    expected = {r["sortie_id"] for r in old["sorties"] if r["drone_id"] != failed}
    assert expected <= set(result["plan"]["change_summary"]["preserved_sortie_ids"])
    assert any("依赖图局部修复" in note for note in result["plan"]["solver_notes"])
    assert old == previous


def test_partial_initial_soc_uses_verified_full_fallback(case):
    snap, options = case
    for b in snap["scenario"]["batteries"]:
        b["soc"] = 0.98
    snap["content_hash"] = content_hash(snap["scenario"])
    options["time_limit_s"] = 10
    old = solve(snap, options)["plan"]
    assert old
    next(d for d in snap["scenario"]["drones"] if d["drone_id"] == "U01")[
        "status"
    ] = "unavailable"
    snap["scenario"]["state_version"] = 2
    snap.update(
        snapshot_id="SNAP-FALLBACK",
        scenario_state_version=2,
        content_hash=content_hash(snap["scenario"]),
    )
    options.update(
        mode="replan",
        snapshot_id=snap["snapshot_id"],
        plan_id="PLAN-FALLBACK",
        parent_plan_id=old["plan_id"],
        event_id="EVT-FALLBACK",
    )
    result = replan(
        snap,
        old,
        {"event_id": "EVT-FALLBACK", "event_type": "drone.unavailable"},
        options,
    )
    assert result["plan"], result
    assert any("全量回退" in note for note in result["plan"]["solver_notes"])
    validate_outcome(result, snap)
