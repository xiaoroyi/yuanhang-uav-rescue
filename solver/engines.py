"""Offline heuristic provider. No network, imports, I/O during module import or arbitrary exec.

EoH output is reduced to a bounded scalar expression before deployment. The online
solver still owns feasibility, physics, resource assignment and final objectives.
"""

from __future__ import annotations

import ast
from contextlib import contextmanager
from contextvars import ContextVar
import functools
import hashlib
import json
import math
from pathlib import Path
from shared.contracts import unique_pairs, validate_schema

BUILTIN = Path(__file__).parent / "policies"
_store = ContextVar("heuristic_store", default=None)
_current = ContextVar("heuristic_engine", default=None)
FEATURES = {"base_score", "finish_s", "energy_kwh", "cargo_count", "load_ratio"}
FUNCTIONS = {"min": min, "max": max, "abs": abs, "sqrt": math.sqrt, "log1p": math.log1p}


@contextmanager
def policy_store(directory):
    token = _store.set(Path(directory))
    try:
        yield
    finally:
        _store.reset(token)


def checked_expression(expression):
    if not isinstance(expression, str) or len(expression) > 1800:
        raise ValueError("评分表达式须为1800字符以内的文本。")
    tree = ast.parse(expression, mode="eval")
    nodes = list(ast.walk(tree))
    if len(nodes) > 160:
        raise ValueError("评分表达式过于复杂。")
    allowed = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Call,
        ast.Name,
        ast.Load,
        ast.Constant,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.USub,
        ast.UAdd,
    )
    for node in nodes:
        if not isinstance(node, allowed):
            raise ValueError("评分仅允许四则运算与min/max/abs/sqrt/log1p。")
        if isinstance(node, ast.Name) and node.id not in FEATURES | FUNCTIONS.keys():
            raise ValueError("评分引用未知特征。")
        if isinstance(node, ast.Constant) and (
            isinstance(node.value, bool)
            or not isinstance(node.value, (int, float))
            or abs(node.value) > 1e9
            or not math.isfinite(node.value)
        ):
            raise ValueError("评分常数必须为有限数。")
        if isinstance(node, ast.Call) and (
            not isinstance(node.func, ast.Name)
            or node.func.id not in FUNCTIONS
            or node.keywords
            or not 1 <= len(node.args) <= 8
        ):
            raise ValueError("评分函数或参数不合法。")
    return compile(tree, "<offline-heuristic>", "eval")


def _reject_json_constant(value):
    raise ValueError("策略包包含非有限JSON数字。")


def policy_bytes(policy_id="eoh-seed-v1"):
    if (
        not isinstance(policy_id, str)
        or not policy_id
        or len(policy_id) > 80
        or any(
            c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
            for c in policy_id
        )
    ):
        raise ValueError("策略ID不合法。")
    custom = _store.get()
    path = (custom / (policy_id + ".json")) if custom else None
    if not path or not path.is_file():
        path = BUILTIN / (policy_id + ".json")
    if not path.is_file() or path.stat().st_size > 32_768:
        raise ValueError("找不到指定本地策略包。")
    return path.read_bytes()


def read_policy(policy_id="eoh-seed-v1"):
    raw = policy_bytes(policy_id)
    value = json.loads(
        raw, object_pairs_hook=unique_pairs, parse_constant=_reject_json_constant
    )
    validate_schema("heuristic-artifact", value)
    if (
        value.get("policy_id") != policy_id
        or value.get("format") != "yuanhang-scalar-v1"
    ):
        raise ValueError("策略ID或格式与文件不一致。")
    if value.get("origin") not in ("rule_initialization", "eoh_offline"):
        raise ValueError("策略来源不合法。")
    for key, limit in (("name", 120), ("version", 40), ("description", 1200)):
        if not isinstance(value.get(key), str) or not 1 <= len(value[key]) <= limit:
            raise ValueError("策略名称、版本或说明不合法。")
    expression = checked_expression(value["expression"])
    # A quick bounded numerical check is independent of any claimed training record.
    for score in (0.001, 1, 100, 100000):
        for count in (1, 12):
            try:
                evaluate(
                    expression,
                    dict(
                        base_score=score,
                        finish_s=1000,
                        energy_kwh=2,
                        cargo_count=count,
                        load_ratio=0.65,
                    ),
                )
            except (ArithmeticError, TypeError) as exc:
                raise ValueError("策略数值检查失败。") from exc
    return value, hashlib.sha256(raw).hexdigest(), expression


def evaluate(expression, features):
    value = eval(expression, {"__builtins__": {}}, {**FUNCTIONS, **features})
    if (
        isinstance(value, bool)
        or not isinstance(value, (float, int))
        or not math.isfinite(value)
        or abs(value) > 1e15
    ):
        raise ValueError("本地策略评分不是合法有限数。")
    return float(value)


def catalog():
    ids = {p.stem for p in BUILTIN.glob("*.json")}
    custom = _store.get()
    if custom and custom.is_dir():
        ids.update(p.stem for p in custom.glob("*.json"))
    rows = []
    for policy_id in sorted(ids):
        try:
            value, digest, _ = read_policy(policy_id)
            rows.append(
                {
                    k: value[k]
                    for k in ("policy_id", "name", "version", "origin", "description")
                }
                | {
                    "sha256": digest,
                    "online_network_required": False,
                    "evolution_record": value.get("evolution_record"),
                }
            )
        except (ValueError, KeyError, OSError, SyntaxError):
            continue
    return rows


def ranking_score(base_score, *, finish_s, energy_kwh, cargo_count, load_ratio):
    state = _current.get()
    if state is None or state["engine_type"] == "standard":
        return base_score
    try:
        result = evaluate(
            state["expression"],
            dict(
                base_score=base_score,
                finish_s=finish_s,
                energy_kwh=energy_kwh,
                cargo_count=cargo_count,
                load_ratio=load_ratio,
            ),
        )
        state["ranking_evaluations"] += 1
        return result
    except (ArithmeticError, ValueError, TypeError, OverflowError):
        state["fallback_evaluations"] += 1
        return base_score


def engine_trace():
    state = _current.get()
    if state is None:
        return None
    return {k: v for k, v in state.items() if k != "expression"}


def engine_run(func):
    """Scope one solver invocation; nested joint/repair calls share the same trace."""

    @functools.wraps(func)
    def run(*args, **kwargs):
        # Stable entry points have options at the penultimate positional slot.
        options = kwargs.get("options")
        if options is None:
            index = (
                1 if func.__name__ == "solve" else 3 if func.__name__ == "replan" else 2
            )
            options = args[index]
        requested = options.get("engine_type", "standard")
        policy_id = options.get("heuristic_policy_id") or "eoh-seed-v1"
        previous = _current.get()
        if previous is not None:
            return func(*args, **kwargs)
        state = dict(
            engine_type=requested,
            policy_id=None,
            version=None,
            origin="standard",
            sha256=None,
            ranking_evaluations=0,
            fallback_evaluations=0,
        )
        if requested == "eoh":
            value, digest, expression = read_policy(policy_id)
            if (
                options.get("heuristic_policy_sha256")
                and options["heuristic_policy_sha256"] != digest
            ):
                raise ValueError("本地策略指纹与已提交任务不同，已阻止评分。")
            state.update(
                policy_id=policy_id,
                version=value["version"],
                origin=value["origin"],
                sha256=digest,
                expression=expression,
            )
        elif requested != "standard":
            raise ValueError("不支持的调度引擎。")
        token = _current.set(state)
        try:
            result = func(*args, **kwargs)
            # Old requests keep their byte-level field shape; no history is rewritten.
            if result.get("plan") is not None and "engine_type" in options:
                result["plan"]["engine"] = engine_trace()
            return result
        finally:
            _current.reset(token)

    return run
