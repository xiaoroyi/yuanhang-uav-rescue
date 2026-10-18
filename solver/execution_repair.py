"""Pure residual planning with lossless references and protected executed cargo."""

from collections import Counter
import hashlib
import json
import time

from shared.contracts import (
    ContractError,
    require,
    validate_options,
    validate_snapshot,
    validate_schema,
)
from shared.operation_contracts import validate_operation
from solver.public_api import _outcome, diagnostic, _try_local_repair, solve
from solver.validation import validate


def repair_remaining(snapshot, reference, options, progress_callback=None):
    started = time.perf_counter()
    stats = {"candidate_count": 0}
    try:
        validate_snapshot(snapshot)
        validate_options(options, snapshot)
        validate_operation("ExecutionRepairReference", reference)
        require(
            reference["input_snapshot_id"] == snapshot["snapshot_id"]
            and options["mode"] == "quick",
            "残余输入快照/求解模式不匹配。",
        )
        docs = {}
        for doc in reference["documents"]:
            require(
                doc["kind"] in ("plan", "snapshot"), "修复引用仅接收原Plan/Snapshot。"
            )
            require(
                hashlib.sha256(doc["payload_json"].encode("utf-8")).hexdigest()
                == doc["sha256"],
                "原文SHA256不匹配。",
            )
            key = (doc["kind"], doc["document_id"])
            require(key not in docs, "修复原文引用重复。")
            docs[key] = json.loads(doc["payload_json"])
        plans = {key[1]: value for key, value in docs.items() if key[0] == "plan"}
        for pid, plan in plans.items():
            validate_schema("plan", plan)
            require(
                plan["plan_id"] == pid
                and plan["data_origin"] == "solver"
                and plan["has_validated_plan"],
                "仅能引用真实Solver原方案。",
            )
            original = docs["snapshot", plan["snapshot_id"]]
            validate_snapshot(original)
            require(
                validate(original, plan)["status"] == "passed",
                "引用原方案未通过当前独立检查。",
            )
        future = []
        keys = set()
        for part in reference["future_parts"]:
            require(
                not part.get("relay_sortie_ids"), "当前残余局部修复不接受中继窗口。"
            )
            plan = plans[part["plan_id"]]
            for sid in part["sortie_ids"]:
                key = (part["plan_id"], sid)
                require(key not in keys, "未来架次来源重复。")
                keys.add(key)
                future.append(next(r for r in plan["sorties"] if r["sortie_id"] == sid))
        locked = set(reference["committed_cargo_ids"])
        source_cargo = {
            cid
            for plan in plans.values()
            for route in plan["sorties"]
            for cid in route["cargo_ids"]
        }
        require(
            len(locked) == len(reference["committed_cargo_ids"])
            and locked.issubset(source_cargo),
            "已承诺箱件不在原方案或存在重复。",
        )
        scene = snapshot["scenario"]
        require(
            not locked.intersection(c["cargo_id"] for c in scene["cargo_items"]),
            "残余输入含已承诺箱件。",
        )
        previous_cargo = [cid for route in future for cid in route["cargo_ids"]]
        require(
            not locked.intersection(previous_cargo)
            and len(set(previous_cargo)) == len(previous_cargo),
            "未来引用重复箱件或覆盖已承诺箱件。",
        )
        identities_unique = len({r["sortie_id"] for r in future}) == len(future)
        known = {c["cargo_id"]: c for c in scene["cargo_items"]}
        coverage = Counter(
            known[cid]["demand_id"] for cid in previous_cargo if cid in known
        )
        exact_coverage = len(previous_cargo) == sum(
            coverage.values()
        ) and coverage == Counter(
            {d["demand_id"]: d["required_quantity"] for d in scene["demands"]}
        )
        local = None
        if (
            reference["repair_policy"] == "dependency"
            and not reference["force_full"]
            and exact_coverage
            and identities_unique
        ):
            local = _try_local_repair(
                snapshot, future, options, started, progress_callback, stats=stats
            )
    except (ContractError, KeyError, TypeError, ValueError, StopIteration) as exc:
        return _outcome(
            "UNKNOWN",
            options,
            started,
            reason="input_not_ready",
            diagnostics=[diagnostic("INPUT_NOT_READY", str(exc))],
        )
    if local is not None:
        result = local
        result["diagnostics"].append(
            diagnostic(
                "REPAIR_LOCAL_APPLIED",
                "保留未受影响的未来任务并修复资源依赖邻域；全部残余任务已独立验证。",
            )
        )
    else:
        spent = time.perf_counter() - started
        remaining = max(0.001, float(options["time_limit_s"]) - spent)

        def progress(value):
            if progress_callback:
                progress_callback(
                    {
                        **value,
                        "stage": "残余全量 · " + value["stage"],
                        "elapsed_s": value["elapsed_s"] + spent,
                        "candidate_count": value["candidate_count"]
                        + stats["candidate_count"],
                    }
                )

        result = solve(snapshot, {**options, "time_limit_s": remaining}, progress)
        result["candidate_count"] += stats["candidate_count"]
        if result["first_feasible_s"] is not None:
            result["first_feasible_s"] += spent
        result["diagnostics"].append(
            diagnostic(
                "REPAIR_FULL_RECOMPUTE",
                "按残余输入全量计算；已开始承诺由执行层独立保留，不重置在飞位置/箱件。",
            )
        )
    result["runtime_s"] = time.perf_counter() - started
    if result["plan"]:
        require(
            not locked.intersection(
                cid for r in result["plan"]["sorties"] for cid in r["cargo_ids"]
            ),
            "结果覆盖已承诺箱件。",
        )
    return result
