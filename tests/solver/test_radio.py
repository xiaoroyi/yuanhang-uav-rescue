import copy
import math
import json

import numpy as np
import pytest
from shapely.geometry import LineString, Polygon

from shared.contracts import content_hash, validate_outcome
from solver.adapters.contest import compact_scenario, contest_communication
from solver.public_api import solve, validate
from solver.radio import Radio, bad_intervals
from solver.errors import InputNotReady


def synthetic_radio():
    radio = object.__new__(Radio)
    radio.deadline, radio.cache = math.inf, {}
    radio.radii = {"direct": (2, 100)}
    radio.domain = Polygon([[-100, -100], [100, -100], [100, 100], [-100, 100]])
    vertices = np.array([[[4, 0.1], [6, 0.1], [6, -0.1], [4, -0.1]]], dtype=float)
    radio.cells = lambda a, p0, p1: (vertices, np.array([10.0]))
    return radio, vertices[0]


def test_continuous_obstruction_detects_gap_between_good_endpoints():
    radio, vertices = synthetic_radio()
    anchor, a, b = (
        np.array([0.0, 0.0, 5.0]),
        np.array([10.0, -10.0, 5.0]),
        np.array([10.0, 10.0, 5.0]),
    )
    profile = radio.profile(anchor, a, b, "direct")
    assert profile["pieces"][0][2] and profile["pieces"][-1][2]
    assert bad_intervals(profile, 0, 100)
    # Cross-check many arbitrary instants against an independent polygon LOS test.
    obstacle = Polygon(vertices)
    for u in np.linspace(0.001, 0.999, 101):
        point = a + u * (b - a)
        expected = not LineString([anchor[:2], point[:2]]).intersects(obstacle)
        actual = next(ok for lo, hi, ok in profile["pieces"] if lo <= u <= hi)
        assert actual == expected


def test_worst_obstruction_radius_and_point_contacts_are_checked():
    radio, _ = synthetic_radio()
    anchor = np.array([0.0, 0.0, 5.0])
    point = np.array([1.0, 0.0, 5.0])
    assert not bad_intervals(radio.profile(anchor, point, point, "direct"), 0, 1)
    point = np.array([10.0, 0.0, 5.0])
    assert bad_intervals(radio.profile(anchor, point, point, "direct"), 0, 1) == [
        [0.0, 1.0]
    ]
    point = np.array([101.0, 0.0, 5.0])
    assert bad_intervals(radio.profile(anchor, point, point, "direct"), 0, 1) == [
        [0.0, 1.0]
    ]
    radio.domain = Polygon([[-5, -5], [5, -5], [5, 5], [-5, 5]])
    point = np.array([9.0, 0.0, 5.0])
    with pytest.raises(InputNotReady, match="DEM"):
        radio.profile(anchor, point, point, "direct")


@pytest.fixture(scope="module")
def joint_case():
    s = compact_scenario()
    s["communication"] = contest_communication(s)
    s["policy"]["requires_communication"] = True
    snap = {
        "schema_version": s["schema_version"],
        "snapshot_id": "SNAP-JOINT-TEST",
        "scenario_id": s["scenario_id"],
        "scenario_state_version": s["state_version"],
        "content_hash": content_hash(s),
        "created_at": s["start_time"],
        "scenario": s,
    }
    options = {
        "schema_version": s["schema_version"],
        "snapshot_id": snap["snapshot_id"],
        "plan_id": "PLAN-JOINT-TEST",
        "objective": "time",
        "mode": "quick",
        "time_limit_s": 45,
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
            "communication",
        ],
        "allow_partial_service": False,
    }
    result = solve(snap, options)
    assert result["plan"], json.dumps(result, ensure_ascii=False, indent=2)
    return snap, result


def test_real_joint_plan_reconstructs_coverage_resources_and_metrics(joint_case):
    snap, result = joint_case
    validate_outcome(result, snap)
    plan = result["plan"]
    assert plan["relay_sorties"]
    assert plan["communication_report"]["coverage_gap_s"] == 0
    assert plan["communication_report"]["relay_s"] > 0
    assert plan["joint_metrics"]["joint_energy_kwh"] > plan["metrics"]["energy_kwh"]
    assert validate(snap, plan)["status"] == "passed"
    assert "通信未评估" not in "".join(plan["solver_notes"])


@pytest.mark.parametrize("objective", ["time", "energy", "balanced"])
def test_v2_joint_policies_publish_only_independently_validated_joint_plans(
    case, objective
):
    snap, options = case
    s = snap["scenario"]
    s["communication"] = contest_communication(s)
    s["policy"]["requires_communication"] = True
    snap["content_hash"] = content_hash(s)
    opts = {
        **options,
        "objective": objective,
        "objective_policy": "tradeoff_v2",
        "time_limit_s": 60,
    }
    opts["requested_model_scope"] = [*options["requested_model_scope"], "communication"]
    result = solve(snap, opts)
    validate_outcome(result, snap)
    p = result["plan"]
    assert p, result["diagnostics"]
    assert p["objective_policy"] == "tradeoff_v2"
    assert validate(snap, p)["status"] == "passed"
    assert p["communication_report"]["coverage_gap_s"] == 0
    assert p["joint_metrics"]["joint_energy_kwh"] > p["metrics"]["energy_kwh"]
    assert p["joint_search"]["stages"][0]["stage"] == "joint_objective"


def test_removed_relays_cannot_keep_forged_passed_communication(joint_case):
    snap, result = joint_case
    plan = copy.deepcopy(result["plan"])
    plan["relay_sorties"] = []
    plan["joint_metrics"] = {
        "relay_energy_kwh": 0,
        "joint_energy_kwh": plan["metrics"]["energy_kwh"],
        "joint_makespan_s": plan["metrics"]["makespan_s"],
        "relay_sortie_count": 0,
    }
    report = validate(snap, plan)
    assert report["status"] == "failed"
    assert any(
        c["code"] == "communication"
        and c["status"] == "failed"
        and "缺口" in c["message"]
        for c in report["checks"]
    )


def test_relay_timing_energy_and_component_overlap_are_rejected(joint_case):
    snap, result = joint_case
    original = result["plan"]
    for key in ["return_soc", "service_end_s", "energy_kwh", "component_released_s"]:
        plan = copy.deepcopy(original)
        plan["relay_sorties"][0][key] = 0
        assert validate(snap, plan)["status"] == "failed", key
    plan = copy.deepcopy(original)
    duplicate = copy.deepcopy(plan["relay_sorties"][0])
    duplicate["relay_sortie_id"] += "-DUP"
    plan["relay_sorties"].append(duplicate)
    joint = plan["joint_metrics"]
    joint["relay_sortie_count"] += 1
    joint["relay_energy_kwh"] += duplicate["energy_kwh"]
    joint["joint_energy_kwh"] += duplicate["energy_kwh"]
    assert validate(snap, plan)["status"] == "failed"


def test_insufficient_relay_inventory_is_unknown_not_false_infeasible(joint_case):
    snap, _ = joint_case
    changed = copy.deepcopy(snap)
    changed["scenario"]["communication"]["relay_energy"] = []
    changed["content_hash"] = content_hash(changed["scenario"])
    options = {
        "schema_version": snap["schema_version"],
        "snapshot_id": snap["snapshot_id"],
        "plan_id": "PLAN-JOINT-NO-ENERGY",
        "objective": "time",
        "mode": "quick",
        "time_limit_s": 15,
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
            "communication",
        ],
        "allow_partial_service": False,
    }
    outcome = solve(changed, options)
    assert outcome["solver_status"] == "UNKNOWN" and outcome["plan"] is None
    validate_outcome(outcome, changed)


def test_bad_joint_optimizer_candidate_is_an_error_not_unknown(joint_case, monkeypatch):
    import solver.joint

    snap, result = joint_case
    bad = copy.deepcopy(result["plan"])
    bad["relay_sorties"][0]["energy_kwh"] = 0
    monkeypatch.setattr(
        solver.joint,
        "schedule",
        lambda *a, **kw: (
            bad["sorties"],
            bad["relay_sorties"],
            bad["communication_report"],
            {"status": "FEASIBLE"},
        ),
    )
    options = _options_for(snap, "PLAN-JOINT-BAD")
    outcome = solve(snap, options)
    assert outcome["solver_status"] == "ERROR" and outcome["plan"] is None
    assert outcome["stop_reason"] == "validation_failed"
    validate_outcome(outcome, snap)


def _options_for(snap, identity):
    return {
        "schema_version": snap["schema_version"],
        "snapshot_id": snap["snapshot_id"],
        "plan_id": identity,
        "objective": "time",
        "mode": "quick",
        "time_limit_s": 45,
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
            "communication",
        ],
        "allow_partial_service": False,
    }


def test_warm_joint_first_feasible_records_baseline_validation_time(joint_case):
    snap, result = joint_case
    options = {
        **_options_for(snap, "PLAN-JOINT-WARM"),
        "mode": "improve",
        "time_limit_s": 0.05,
    }
    progress = []
    outcome = solve(snap, options, progress.append, initial_plan=result["plan"])
    assert outcome["plan"] and outcome["plan"]["plan_id"] == options["plan_id"]
    assert outcome["first_feasible_s"] <= progress[0]["elapsed_s"]
    validate_outcome(outcome, snap)


def test_heterogeneous_relay_components_keep_individual_energy_physics(joint_case):
    snap, _ = joint_case
    changed = copy.deepcopy(snap)
    changed["scenario"]["communication"]["relay_energy"][0]["soh"] = 0.8
    changed["content_hash"] = content_hash(changed["scenario"])
    outcome = solve(changed, _options_for(changed, "PLAN-JOINT-HETERO"))
    assert outcome["plan"], outcome
    validate_outcome(outcome, changed)
    assert validate(changed, outcome["plan"])["status"] == "passed"


def test_transport_pools_keep_release_times_and_heterogeneous_batteries(joint_case):
    snap, _ = joint_case
    changed = copy.deepcopy(snap)
    changed["scenario"]["drones"][0]["available_after_s"] = 120
    changed["scenario"]["batteries"][0].update(soh=0.8, available_after_s=900)
    changed["content_hash"] = content_hash(changed["scenario"])
    outcome = solve(changed, _options_for(changed, "PLAN-JOINT-TRANSPORT-POOLS"))
    assert outcome["plan"], outcome
    validate_outcome(outcome, changed)
    assert validate(changed, outcome["plan"])["status"] == "passed"
