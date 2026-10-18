"""Real soft-deadline tradeoffs, legacy meaning and refinement safety."""

import copy

from solver.metrics import delivery_analysis, objective_score
from solver.public_api import solve, validate


def test_v2_real_tradeoffs_keep_original_soft_deadlines_and_all_hard_checks(case):
    snapshot, options = case
    before = copy.deepcopy(snapshot)
    outcomes = {
        objective: solve(
            snapshot,
            {
                **options,
                "objective": objective,
                "plan_id": "PLAN-V2-" + objective,
                "time_limit_s": 20,
                "objective_policy": "tradeoff_v2",
            },
        )
        for objective in ("time", "energy", "balanced")
    }
    assert snapshot == before
    plans = {k: o["plan"] for k, o in outcomes.items()}
    assert len({o["candidate_count"] for o in outcomes.values()}) == 1
    for o in outcomes.values():
        assert o["stop_reason"] == "finished"
        p = o["plan"]
        assert p and p["objective_policy"] == "tradeoff_v2"
        assert validate(snapshot, p)["status"] == "passed"
        assert delivery_analysis(snapshot["scenario"], p)["hard_violation_count"] == 0
        assert sum(len(r["cargo_ids"]) for r in p["sorties"]) == 32
    t, e, b = [plans[k]["metrics"] for k in ("time", "energy", "balanced")]
    assert t["makespan_s"] < b["makespan_s"] < e["makespan_s"]
    assert e["energy_kwh"] < b["energy_kwh"] < t["energy_kwh"]
    # Legacy policy remains strict soft-lateness first, even on these routes.
    timed = plans["time"]
    old = copy.deepcopy(timed)
    old.pop("objective_policy")
    late = delivery_analysis(snapshot["scenario"], old)["weighted_box_delay_s"]
    assert objective_score(snapshot["scenario"], old, "time")[0] == late
    assert objective_score(snapshot["scenario"], timed, "time")[0] == t["makespan_s"]


def test_v2_deep_refinement_and_policy_mismatch(case):
    snapshot, options = case
    opts = {**options, "objective_policy": "tradeoff_v2", "objective": "energy"}
    base = solve(snapshot, opts)["plan"]
    assert base
    refined = solve(
        snapshot,
        {**opts, "mode": "improve", "time_limit_s": 8, "plan_id": "PLAN-V2-IMPROVE"},
        initial_plan=base,
    )
    assert refined["plan"] and validate(snapshot, refined["plan"])["status"] == "passed"
    assert objective_score(
        snapshot["scenario"], refined["plan"], "energy"
    ) <= objective_score(snapshot["scenario"], base, "energy")
    mismatch = solve(snapshot, {**options, "mode": "improve"}, initial_plan=base)
    assert mismatch["solver_status"] == "UNKNOWN"
    assert mismatch["stop_reason"] == "input_not_ready"
