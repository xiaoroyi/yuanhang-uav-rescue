import copy
import json
import pytest

from shared.contracts import content_hash, validate_outcome
from solver.public_api import solve, validate
from solver.engines import (
    checked_expression,
    evaluate,
    read_policy,
    policy_store,
    catalog,
)


def test_optional_engine_keeps_legacy_shape_and_validates_real_routes(case):
    snap, options = case
    original = copy.deepcopy(snap)
    legacy = solve(snap, options)
    assert legacy["plan"] and "engine" not in legacy["plan"]
    enhanced = solve(
        snap,
        {
            **options,
            "plan_id": "PLAN-EOH",
            "engine_type": "eoh",
            "objective_policy": "tradeoff_v2",
        },
    )
    validate_outcome(enhanced, snap)
    p = enhanced["plan"]
    assert p and p["engine"]["ranking_evaluations"] > 0
    assert p["engine"]["origin"] == "rule_initialization"
    assert p["engine"]["sha256"] == read_policy()[1]
    assert validate(snap, p)["status"] == "passed"
    assert snap == original and content_hash(snap["scenario"]) == snap["content_hash"]


@pytest.mark.parametrize(
    "expression",
    [
        "__import__('os')",
        "base_score.__class__",
        "[1] * 999999",
        "(lambda: 2)()",
        "base_score ** 99999",
        "True",
        "1e309",
        "sum([1])",
    ],
)
def test_deployed_expression_cannot_execute_general_python(expression):
    with pytest.raises((ValueError, SyntaxError)):
        checked_expression(expression)


def test_policy_identity_and_pinned_hash(case, tmp_path):
    with pytest.raises(ValueError):
        read_policy("../bad")
    p = json.loads(
        (__import__("pathlib").Path("solver/policies/eoh-seed-v1.json")).read_text(
            encoding="utf-8"
        )
    )
    p["policy_id"] = "custom-v1"
    (tmp_path / "custom-v1.json").write_text(json.dumps(p), encoding="utf-8")
    with policy_store(tmp_path):
        assert {p["policy_id"] for p in catalog()} == {"eoh-seed-v1", "custom-v1"}
        snap, options = case
        with pytest.raises(ValueError, match="指纹"):
            solve(
                snap,
                {
                    **options,
                    "engine_type": "eoh",
                    "heuristic_policy_id": "custom-v1",
                    "heuristic_policy_sha256": "0" * 64,
                },
            )


def test_nonfinite_scores_are_rejected():
    code = checked_expression("base_score / (cargo_count - 1)")
    with pytest.raises(ZeroDivisionError):
        evaluate(
            code,
            dict(base_score=1, finish_s=1, energy_kwh=1, cargo_count=1, load_ratio=1),
        )
