import copy
import math

import numpy as np
import pytest
from shapely.geometry import LineString, Polygon

from shared.contracts import content_hash, validate_outcome
from solver.adapters.contest import compact_scenario, contest_communication
from solver.public_api import solve, validate
from solver.radio import Radio, bad_intervals


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
    with pytest.raises(Exception, match="DEM"):
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
    assert result["plan"], result
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
