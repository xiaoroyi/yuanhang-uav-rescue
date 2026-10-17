import copy

import pytest

from shared.contracts import validate_outcome
from solver.metrics import objective_score
from solver.public_api import solve


@pytest.mark.parametrize("objective", ["time", "energy"])
def test_deep_search_preserves_validated_incumbent_and_never_worsens_its_objective(
    case, objective
):
    snap, opts = case
    opts["objective"] = objective
    old = solve(snap, opts)["plan"]
    assert old
    before = copy.deepcopy(old)
    improved = {
        **opts,
        "mode": "improve",
        "time_limit_s": 4,
        "plan_id": "PLAN-DEEP-" + objective.upper(),
    }
    result = solve(snap, improved, initial_plan=old)
    assert result["plan"] and result["algorithm_mode"] == "improve", result
    validate_outcome(result, snap)
    assert objective_score(
        snap["scenario"], result["plan"], objective
    ) <= objective_score(snap["scenario"], old, objective)
    assert result["plan"]["plan_id"] == improved["plan_id"]
    assert old == before


@pytest.mark.parametrize("broken", ["bad_candidate", "exception"])
def test_optional_optimizer_failure_keeps_independently_valid_incumbent(
    case, monkeypatch, broken
):
    snap, opts = case
    old = solve(snap, opts)["plan"]
    assert old

    def invalid(*_args, **_kwargs):
        if broken == "exception":
            raise ValueError("simulated optional optimizer failure")
        routes = copy.deepcopy(old["sorties"])
        routes[0]["energy_kwh"] = 0
        return routes, {"pool_size": 1, "status": "FEASIBLE"}

    monkeypatch.setattr("solver.cp_pool.optimize", invalid)
    result = solve(
        snap,
        {**opts, "mode": "improve", "time_limit_s": 1, "plan_id": "PLAN-DEEP-FALLBACK"},
        initial_plan=old,
    )
    assert result["plan"] and result["plan"]["validation"]["status"] == "passed"
    validate_outcome(result, snap)
    assert result["plan"]["metrics"]["energy_kwh"] > 0


def test_mock_or_wrong_snapshot_is_not_accepted_as_deep_incumbent(case):
    snap, opts = case
    old = solve(snap, opts)["plan"]
    assert old
    for change in [
        {"snapshot_id": "SNAP-NOT-THE-INPUT"},
        {"data_origin": "mock", "has_validated_plan": False},
    ]:
        result = solve(
            snap, {**opts, "mode": "improve"}, initial_plan={**old, **change}
        )
        assert result["plan"] is None and result["stop_reason"] == "input_not_ready"
