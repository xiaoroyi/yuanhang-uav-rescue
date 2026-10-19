"""Explicit opt-in EoH integration. Default/--describe never calls a model.

Official upstream: https://github.com/FeiLiu36/EoH (MIT, new BaseProblem API).
Install upstream in a separate research environment before --run. Online jobs do
not import it. Keep API credentials in environment variables, never in artifacts.
"""

from __future__ import annotations
import argparse
import ast
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from shared.contracts import content_hash, validate_outcome
from solver.engines import checked_expression, policy_store, read_policy
from solver.adapters.contest import compact_scenario
from solver.public_api import solve
from solver.validation import BASE_SCOPE

TEMPLATE = '''def priority(base_score: float, finish_s: float, energy_kwh: float,
             cargo_count: float, load_ratio: float) -> float:
    """Rank an already feasible sortie. Lower is preferred."""
    return base_score
'''
DESCRIPTION = (
    "Design a scalar UAV-rescue candidate ranking function. Use only base_score, "
    "finish_s, energy_kwh, cargo_count, load_ratio; numeric constants, + - * / and "
    "min/max/abs/sqrt/log1p. One return expression, no imports, loops, attributes, "
    "state or network. Feasibility and final objective are enforced independently."
)


def expression_from(program):
    tree = ast.parse(program)
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.FunctionDef):
        raise ValueError("部署产物必须只有一个priority函数。")
    f = tree.body[0]
    if (
        f.name != "priority"
        or f.decorator_list
        or f.args.vararg
        or f.args.kwarg
        or f.args.defaults
        or f.args.kwonlyargs
    ):
        raise ValueError("评分函数签名不合法。")
    if [a.arg for a in f.args.args] != [
        "base_score",
        "finish_s",
        "energy_kwh",
        "cargo_count",
        "load_ratio",
    ]:
        raise ValueError("评分函数必须接收约定的五个特征。")
    body = (
        f.body[1:]
        if (
            f.body
            and isinstance(f.body[0], ast.Expr)
            and isinstance(f.body[0].value, ast.Constant)
            and isinstance(f.body[0].value.value, str)
        )
        else f.body
    )
    if len(body) != 1 or not isinstance(body[0], ast.Return):
        raise ValueError("只允许一个返回表达式。")
    expression = ast.unparse(body[0].value)
    checked_expression(expression)
    return expression


def benchmark(expression, directory):
    """Three real finite-budget runs. A result is not a global-optimality claim."""
    directory.mkdir(parents=True, exist_ok=True)
    package = dict(
        format="yuanhang-scalar-v1",
        policy_id="candidate",
        name="离线候选",
        version="research",
        origin="eoh_offline",
        description="本地基准评估候选",
        expression=expression,
    )
    (directory / "candidate.json").write_text(
        json.dumps(package, ensure_ascii=False), encoding="utf-8"
    )
    rows = []
    with policy_store(directory):
        read_policy("candidate")
        for index, objective in enumerate(("time", "energy", "balanced")):
            s = compact_scenario()
            # The third instance is a resource condition variant, not a held-out benchmark claim.
            if index == 2:
                for battery in s["batteries"]:
                    battery["soh"] = 0.92
            snap = dict(
                schema_version=s["schema_version"],
                snapshot_id=f"EOH-SNAP-{index}",
                scenario_id=s["scenario_id"],
                scenario_state_version=s["state_version"],
                created_at=s["start_time"],
                content_hash=content_hash(s),
                scenario=s,
            )
            options = dict(
                schema_version=s["schema_version"],
                plan_id=f"EOH-PLAN-{index}",
                snapshot_id=snap["snapshot_id"],
                objective=objective,
                objective_policy="tradeoff_v2",
                mode="quick",
                time_limit_s=5,
                seed=42 + index,
                parent_plan_id=None,
                event_id=None,
                requested_model_scope=BASE_SCOPE + ["terrain"],
                allow_partial_service=False,
                engine_type="eoh",
                heuristic_policy_id="candidate",
            )
            result = solve(snap, options)
            validate_outcome(result, snap)
            if not result["plan"] or result["validation"]["status"] != "passed":
                return None, rows
            p = result["plan"]
            # Scale-aware training loss; never substitute it for the actual per-goal Plan metrics.
            loss = p["metrics"]["makespan_s"] / 10000 + p["metrics"]["energy_kwh"] / 100
            rows.append(
                dict(
                    objective=objective,
                    seed=options["seed"],
                    metrics=p["metrics"],
                    loss=loss,
                    input_sha256=snap["content_hash"],
                    validation="passed",
                )
            )
    return sum(r["loss"] for r in rows) / len(rows), rows


def publish(expression, directory, policy_id, record, origin):
    directory.mkdir(parents=True, exist_ok=True)
    if (
        not policy_id
        or any(
            c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
            for c in policy_id
        )
        or len(policy_id) > 80
    ):
        raise ValueError("策略ID不合法。")
    target = directory / (policy_id + ".json")
    value = dict(
        format="yuanhang-scalar-v1",
        policy_id=policy_id,
        name="离线启发式评分",
        version="1.0.0",
        origin=origin,
        description="离线生成并由本地基准评估的候选评分。最终效果需同条件比较。",
        expression=expression,
        evolution_record=record,
    )
    # Immutable publish: a version is never silently overwritten.
    with target.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
    with policy_store(directory):
        read_policy(policy_id)
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--describe", action="store_true")
    parser.add_argument(
        "--run",
        action="store_true",
        help="Explicitly call the configured external/local LLM",
    )
    parser.add_argument(
        "--program",
        type=Path,
        help="Deploy one saved EoH priority function after local evaluation",
    )
    parser.add_argument(
        "--record",
        type=Path,
        help="Original evolution record required for imported programs",
    )
    parser.add_argument("--policy-id", default="eoh-offline-v1")
    parser.add_argument("--output", type=Path, default=ROOT / ".local/eoh-evolution")
    parser.add_argument(
        "--deploy",
        type=Path,
        help="Optional runtime/heuristics directory; publishes a new immutable ID",
    )
    parser.add_argument("--population", type=int, default=4)
    parser.add_argument("--generations", type=int, default=3)
    args = parser.parse_args()
    if not args.run and not args.program:
        print(
            json.dumps(
                dict(
                    mode="description_only",
                    network_calls=0,
                    template=TEMPLATE,
                    task=DESCRIPTION,
                    required_env=[
                        "YUANHANG_EOH_ENDPOINT",
                        "YUANHANG_EOH_API_KEY",
                        "YUANHANG_EOH_MODEL",
                    ],
                ),
                ensure_ascii=False,
                indent=2,
            )
        )
        return
    args.output.mkdir(parents=True, exist_ok=True)
    if args.program:
        if not args.record:
            parser.error("--program需要--record原始进化记录；不把初始化规则冒充LLM产物")
        expression = expression_from(args.program.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory(dir=args.output) as scratch:
            fitness, rows = benchmark(expression, Path(scratch))
        if fitness is None:
            raise ValueError("候选未通过本地基准，不能部署。")
        declared = json.loads(args.record.read_text(encoding="utf-8"))
        record = dict(
            source="imported_eoh_record",
            declared=declared,
            local_validation=rows,
            checked_at=datetime.now(timezone.utc).isoformat(),
        )
        print(
            publish(
                expression,
                args.deploy or args.output,
                args.policy_id,
                record,
                "eoh_offline",
            )
        )
        return
    if not 2 <= args.population <= 16 or not 1 <= args.generations <= 30:
        parser.error("population须2–16，generations须1–30")
    required = ["YUANHANG_EOH_ENDPOINT", "YUANHANG_EOH_API_KEY", "YUANHANG_EOH_MODEL"]
    if not all(os.environ.get(k) for k in required):
        parser.error("请先设置离线模型环境变量；默认不会发送任何请求")
    from eoh import EoH, LLMConfig, BaseProblem

    candidates = []

    class RescueRankingProblem(BaseProblem):
        template_program = TEMPLATE
        task_description = DESCRIPTION

        def evaluate_program(self, program_str, callable_func):
            try:
                expression = expression_from(program_str)
                with tempfile.TemporaryDirectory(dir=args.output) as scratch:
                    fitness, rows = benchmark(expression, Path(scratch))
                if fitness is not None:
                    # Runs occur in EoH workers: persist evidence independently of process memory.
                    record = dict(
                        expression=expression,
                        fitness=fitness,
                        cases=rows,
                        source="eoh_offline",
                        model=os.environ["YUANHANG_EOH_MODEL"],
                        checked_at=datetime.now(timezone.utc).isoformat(),
                    )
                    file = args.output / (
                        "candidate-" + content_hash(record)[:20] + ".json"
                    )
                    file.write_text(
                        json.dumps(record, ensure_ascii=False, indent=2),
                        encoding="utf-8",
                    )
                return fitness
            except (ValueError, TypeError, SyntaxError, ArithmeticError):
                return None

    llm = LLMConfig(
        api_endpoint=os.environ[required[0]],
        api_key=os.environ[required[1]],
        model=os.environ[required[2]],
        timeout=150,
    )
    run = EoH(
        llm=llm,
        problem=RescueRankingProblem(timeout=120, n_processes=1),
        pop_size=args.population,
        n_pop=args.generations,
        output_dir=str(args.output / "upstream"),
    )
    run.run()
    for path in args.output.glob("candidate-*.json"):
        candidates.append(json.loads(path.read_text(encoding="utf-8")))
    if not candidates:
        raise ValueError("本轮没有通过本地检查的评分函数。")
    champion = min(candidates, key=lambda c: c["fitness"])
    print(
        publish(
            champion["expression"],
            args.deploy or args.output,
            args.policy_id,
            champion,
            "eoh_offline",
        )
    )


if __name__ == "__main__":
    main()
