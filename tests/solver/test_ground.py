import copy

import pytest

from shared.contracts import content_hash, validate_outcome
from solver.ground import earliest_slot
from solver.public_api import solve, validate
from solver.metrics import objective_score


def limited(case, prep=1, ports=1, partial=False):
    snap, opts = copy.deepcopy(case)
    s = snap["scenario"]
    s["resource_limits"] = {"prep_slots": prep, "charging_ports": ports}
    if partial:
        for b in s["batteries"]:
            b["soc"] = 0.5
        s["batteries"][0]["status"] = "charging"
        for d in s["demands"]:
            if d["hard_deadline_s"] is not None:
                d["hard_deadline_s"] = 100000.0
    snap["content_hash"] = content_hash(s)
    opts["requested_model_scope"].append("ground_resource")
    return snap, opts


@pytest.mark.parametrize("partial", [False, True])
def test_real_finite_calendars_cover_initial_charging_and_keep_input(case, partial):
    snap, opts = limited(case, partial=partial)
    before = copy.deepcopy(snap)
    result = solve(snap, opts)
    assert result["plan"], result
    validate_outcome(result, snap)
    plan = result["plan"]
    assert all(r["charge_start_s"] >= r["return_s"] for r in plan["sorties"])
    assert any(r["charge_start_s"] > r["return_s"] + 1e-6 for r in plan["sorties"])
    if partial:
        assert len(plan["initial_charges"]) == len(snap["scenario"]["batteries"])
        forged = copy.deepcopy(plan)
        forged["initial_charges"] = []
        report = validate(snap, forged)
        assert report["status"] == "failed"
        assert any(
            c["code"] == "battery" and c["status"] == "failed" for c in report["checks"]
        )
    else:
        assert plan["initial_charges"] == []
    assert snap == before
    missing_scope = copy.deepcopy(plan)
    missing_scope["model_scope"].remove("ground_resource")
    assert validate(snap, missing_scope)["status"] == "failed"


@pytest.mark.parametrize("resource", ["prep_slots", "charging_ports"])
def test_independent_checker_rejects_reduced_capacity_even_with_self_passed_flags(
    case, resource
):
    snap, opts = limited(case, prep=3, ports=6)
    result = solve(snap, opts)
    assert result["plan"], result
    snap["scenario"]["resource_limits"][resource] = 1
    snap["content_hash"] = content_hash(snap["scenario"])
    report = validate(snap, result["plan"])
    assert report["status"] == "failed", report
    assert any(
        c["code"] == "ground_resource" and c["status"] == "failed"
        for c in report["checks"]
    )


def test_calendar_uses_half_open_windows_and_avoids_future_reservations():
    windows = [(0.0, 1.0), (1.0, 2.0), (10.0, 11.0)]
    assert earliest_slot(2.0, 8.0, windows, 1) == 2.0
    assert earliest_slot(2.0, 9.0, windows, 1) == 11.0
    assert earliest_slot(0.5, 1.0, windows, 2) == 0.5


def test_deep_mode_retains_or_improves_a_real_finite_capacity_incumbent(case):
    snap, opts = limited(case, prep=1, ports=2)
    old = solve(snap, opts)["plan"]
    assert old
    out = solve(
        snap,
        {
            **opts,
            "mode": "improve",
            "time_limit_s": 6,
            "plan_id": "PLAN-GROUND-DEEP-TEST",
        },
        initial_plan=old,
    )
    validate_outcome(out, snap)
    assert objective_score(snap["scenario"], out["plan"], "time") <= objective_score(
        snap["scenario"], old, "time"
    )
    assert not any(
        "MODEL_INVALID" in note or "未通过独立检查" in note
        for note in out["plan"]["solver_notes"]
    )
