"""Stable pure-Python planning API. No HTTP, database or UI imports."""

from __future__ import annotations

from collections import Counter, defaultdict
import copy
from datetime import datetime, timezone
import math
import random
import time

from shared.contracts import (
    ContractError,
    validate_options,
    validate_scenario,
    validate_snapshot,
    has_execution_facts,
    require,
    validate_schema,
    validate_applied_event,
)
from solver.physics import (
    CHARGE_MODEL,
    ENERGY_MODEL,
    InputNotReady,
    charge_seconds,
    evaluate_route,
    parameters,
)
from solver.validation import BASE_SCOPE, validate
from solver.presentation import playback
from solver.dependencies import affected_closure
from solver.metrics import objective_score
from solver.analysis import analyze
from solver.ground import earliest_slot, initial_schedule
from solver.identities import sortie_id
from solver.nominal import analyze_single_site


def capabilities():
    return {
        "api_version": "v1",
        "schema_versions": ["0.1.0-draft"],
        "solver_ready": True,
        "supported_objectives": ["time", "energy", "balanced"],
        "supported_events": ["drone.unavailable", "battery.unavailable"],
        "supported_model_scope": BASE_SCOPE
        + ["terrain", "restricted_zone", "ground_resource", "communication"],
        "supported_energy_models": [ENERGY_MODEL],
        "supported_charge_models": [CHARGE_MODEL],
        "features": {
            "partial_service": False,
            "relay_coordination": True,
            "execution_state": False,
            "dem_validation": True,
            "what_if": True,
        },
    }


def _outcome(
    status,
    options,
    started,
    *,
    plan=None,
    reason="finished",
    diagnostics=None,
    first=None,
    count=0,
    validation=None,
    joint_search=None,
):
    return {
        "schema_version": "0.1.0-draft",
        "solver_status": status,
        "plan": plan,
        "model_scope": plan["model_scope"] if plan else [],
        "algorithm_mode": options.get("mode", "quick"),
        "runtime_s": time.perf_counter() - started,
        "first_feasible_s": first,
        "candidate_count": count,
        "seed": options.get("seed", 0),
        "stop_reason": reason,
        "validation": validation or {"status": "not_run", "checks": []},
        "diagnostics": diagnostics or [],
        **({"joint_search": joint_search} if joint_search is not None else {}),
    }


def diagnostic(code, message, object_id=None):
    return {
        "code": code,
        "message": message,
        "field_path": None,
        "object_id": object_id,
    }


def _required_cargos(s, seed=0):
    by_demand = defaultdict(list)
    for box in s["cargo_items"]:
        if box["status"] == "available" and box["location_id"] == s["base"]["id"]:
            by_demand[box["demand_id"]].append(box)
    active = {
        d["type_id"]
        for d in s["drones"]
        if d["status"] == "available" and d["location_id"] == s["base"]["id"]
    }
    equipped = {
        b["compatible_type_id"]
        for b in s["batteries"]
        if b["status"] in ("available", "charging")
        and b["soh"] > 0
        and b["location_id"] == s["base"]["id"]
    }
    types = [t for t in s["drone_types"] if t["type_id"] in active & equipped]

    def rank(box):
        compatible = [
            t
            for t in types
            if box["mass_kg"] <= t["max_payload_kg"]
            and box["volume_l"] <= t["max_volume_l"]
        ]
        # Extra inventory is a choice, not a requirement to load the first ID.
        # Different starts explore the mass/volume trade-off; no infeasibility proof.
        weight = (0.25, 1.0, 4.0)[seed % 3]
        cost = min(
            (
                weight * box["mass_kg"] / t["max_payload_kg"]
                + box["volume_l"] / t["max_volume_l"]
                for t in compatible
            ),
            default=math.inf,
        )
        return not bool(compatible), cost, box["cargo_id"]

    selected = []
    for d in s["demands"]:
        available = sorted(by_demand[d["demand_id"]], key=rank)
        if len(available) < d["required_quantity"]:
            raise InputNotReady(
                f"库存不足：{d['demand_id']}需要{d['required_quantity']}箱，可用{len(available)}箱。"
            )
        selected += [b["cargo_id"] for b in available[: d["required_quantity"]]]
    return selected


def _construct(
    s,
    objective,
    seed,
    deadline,
    cache,
    start_floor=0.0,
    target_cargos=None,
    fixed_routes=(),
):
    rng = random.Random(seed)
    cargos = {c["cargo_id"]: c for c in s["cargo_items"]}
    demands = {d["demand_id"]: d for d in s["demands"]}
    types = {t["type_id"]: t for t in s["drone_types"]}
    sites = {n["id"]: n for n in s["sites"]}
    remaining = set(
        _required_cargos(s, seed) if target_cargos is None else target_cargos
    )
    reserved = defaultdict(list)
    for fixed in fixed_routes:
        for kind, identity, end in [
            ("drone", fixed["drone_id"], fixed["drone_released_s"]),
            ("battery", fixed["battery_id"], fixed["battery_released_s"]),
        ]:
            reserved[kind, identity].append((fixed["prepare_start_s"], end))
    limits = s.get("resource_limits")
    prep_windows = [(r["prepare_start_s"], r["takeoff_s"]) for r in fixed_routes]
    charge_windows = [
        (r.get("charge_start_s", r["return_s"]), r["battery_released_s"])
        for r in fixed_routes
    ]
    initial_charges, initial_ready = initial_schedule(
        s, seed, charge_windows, start_floor
    )
    charge_windows.extend((w["start_s"], w["end_s"]) for w in initial_charges)
    drones = {
        d["drone_id"]: {**d, "ready": max(start_floor, d["available_after_s"])}
        for d in s["drones"]
        if d["status"] == "available" and d["location_id"] == s["base"]["id"]
    }
    batteries = {
        b["battery_id"]: {**b, "ready": max(start_floor, b["available_after_s"])}
        for b in s["batteries"]
        if b["status"] in ("available", "charging")
        and b["location_id"] == s["base"]["id"]
        and b["soh"] > 0
    }
    for bid, ready in initial_ready.items():
        batteries[bid].update(ready=ready, soc=1.0, status="available")
    result = []

    def due(cid):
        d = demands[cargos[cid]["demand_id"]]
        return (
            (
                d["hard_deadline_s"]
                if d["hard_deadline_s"] is not None
                else (
                    d["expected_deadline_s"]
                    if d["expected_deadline_s"] is not None
                    else 1e12
                )
                + 20000
            ),
            -d["priority"],
            cid,
        )

    def evaluate(typ, stops):
        key = (typ, tuple((n, tuple(sorted(cs))) for n, cs in stops))
        if key not in cache:
            cache[key] = evaluate_route(s, types[typ], stops)
        return cache[key]

    def assignment(route):
        typ = types[route["type_id"]]
        choices = []
        for uid, u in drones.items():
            if u["type_id"] != route["type_id"]:
                continue
            for bid, b in batteries.items():
                if b["compatible_type_id"] != u["type_id"]:
                    continue
                usable = b["capacity_kwh"] * b["soh"]
                soc = b["soc"]
                ready = b["ready"]
                if (
                    route["energy_kwh"]
                    > (1 - s["policy"]["min_return_soc"]) * usable + 1e-9
                ):
                    continue
                if (
                    b["status"] == "charging"
                    or route["energy_kwh"]
                    > (soc - s["policy"]["min_return_soc"]) * usable + 1e-9
                ):
                    ready += charge_seconds(typ, soc)
                    soc = 1.0
                start = max(u["ready"], ready)
                return_soc = soc - route["energy_kwh"] / usable
                for _ in range(
                    len(fixed_routes) * 2 + len(prep_windows) + len(charge_windows) + 2
                ):
                    start = earliest_slot(
                        start,
                        route["prepare_s"],
                        prep_windows,
                        limits["prep_slots"] if limits else None,
                    )
                    charge_start = earliest_slot(
                        start + route["duration_s"],
                        charge_seconds(typ, return_soc),
                        charge_windows,
                        limits["charging_ports"] if limits else None,
                    )
                    occupied = []
                    for kind, identity, release in [
                        (
                            "drone",
                            uid,
                            start + route["duration_s"] + typ["turnaround_duration_s"],
                        ),
                        (
                            "battery",
                            bid,
                            charge_start + charge_seconds(typ, return_soc),
                        ),
                    ]:
                        occupied.extend(
                            end
                            for begin, end in reserved[kind, identity]
                            if start < end - 1e-8 and begin < release - 1e-8
                        )
                    if not occupied:
                        break
                    start = max(occupied)
                if any(
                    demands[cargos[c]["demand_id"]]["hard_deadline_s"] is not None
                    and start + v["delivery_complete_s"]
                    > demands[cargos[c]["demand_id"]]["hard_deadline_s"] + 1e-7
                    for v in route["visits"]
                    for c in v["cargo_ids"]
                ):
                    continue
                choices.append(
                    (start + route["duration_s"], start, uid, bid, soc, charge_start)
                )
        return min(choices) if choices else None

    while remaining:
        if time.perf_counter() > deadline:
            return None
        focus = min(remaining, key=due)
        destination = demands[cargos[focus]["demand_id"]]["site_id"]
        if not sites[destination]["available"]:
            return None
        alternatives = []
        for type_id in sorted(types):
            if not any(d["type_id"] == type_id for d in drones.values()):
                continue
            route = evaluate(type_id, [(destination, [focus])])
            if route is None or assignment(route) is None:
                continue
            others = sorted(
                remaining - {focus},
                key=lambda cid: (
                    demands[cargos[cid]["demand_id"]]["site_id"] != destination,
                    due(cid),
                ),
            )
            if seed % 3 == 2:
                first = [
                    cid
                    for cid in others
                    if demands[cargos[cid]["demand_id"]]["hard_deadline_s"] is not None
                ]
                rest = [cid for cid in others if cid not in first]
                rng.shuffle(rest)
                others = first + rest
            # Candidate insertion supports up to three distinct delivery points per sortie.
            for cid in others[:80]:
                dest = demands[cargos[cid]["demand_id"]]["site_id"]
                if not sites[dest]["available"]:
                    continue
                trials = []
                if dest in [n for n, _ in route["stops"]]:
                    stops = copy.deepcopy(route["stops"])
                    next(cs for n, cs in stops if n == dest).append(cid)
                    trials.append(stops)
                elif len(route["stops"]) < 3:
                    for i in range(len(route["stops"]) + 1):
                        trial = copy.deepcopy(route["stops"])
                        trial.insert(i, (dest, [cid]))
                        trials.append(trial)
                candidates = []
                for stops in trials:
                    candidate = evaluate(type_id, stops)
                    if candidate is not None:
                        assigned = assignment(candidate)
                        if assigned:
                            candidates.append((candidate, assigned))
                if candidates:
                    route, _ = min(
                        candidates,
                        key=lambda x: (
                            x[0]["energy_kwh"] if objective == "energy" else x[1][0]
                        ),
                    )
            assigned = assignment(route)
            if not assigned:
                continue
            finish, start, uid, bid, soc, charge_start = assigned
            throughput = len(route["cargo_ids"]) ** 0.72
            score = (
                route["energy_kwh"] / throughput
                if objective == "energy"
                else finish / throughput
            )
            if objective == "balanced":
                score = finish / throughput + 300 * route["energy_kwh"] / throughput
            score *= 1.0 if seed == 0 else rng.uniform(0.94, 1.06)
            alternatives.append((score, route, assigned))
        if not alternatives:
            return None
        _, route, (finish, start, uid, bid, soc, charge_start) = min(
            alternatives, key=lambda x: x[0]
        )
        b = batteries[bid]
        typ = types[route["type_id"]]
        return_soc = soc - route["energy_kwh"] / (b["capacity_kwh"] * b["soh"])
        visits = [
            {**v, "delivery_complete_s": start + v["delivery_complete_s"]}
            for v in route["visits"]
        ]
        sortie = {
            "sortie_id": sortie_id(
                route["cargo_ids"],
                uid,
                bid,
                start,
                visits,
                charge_start if limits else None,
            ),
            "kind": "transport",
            "drone_id": uid,
            "battery_id": bid,
            "cargo_ids": route["cargo_ids"],
            "visits": visits,
            "route_geometry": route["route_geometry"],
            "prepare_start_s": start,
            "takeoff_s": start + route["prepare_s"],
            "return_s": finish,
            "drone_released_s": finish + typ["turnaround_duration_s"],
            "battery_released_s": charge_start + charge_seconds(typ, return_soc),
            "energy_kwh": route["energy_kwh"],
            "return_soc": return_soc,
            "terrain_status": (
                "passed" if s["terrain"]["status"] == "available" else "not_evaluated"
            ),
            "communication_status": "not_evaluated",
        }
        if limits:
            sortie["charge_start_s"] = charge_start
        result.append(sortie)
        prep_windows.append((sortie["prepare_start_s"], sortie["takeoff_s"]))
        charge_windows.append((charge_start, sortie["battery_released_s"]))
        drones[uid]["ready"] = sortie["drone_released_s"]
        batteries[bid].update(ready=sortie["battery_released_s"], soc=1.0)
        remaining.difference_update(route["cargo_ids"])
    return {"sorties": result, "initial_charges": initial_charges}


def _make_plan(snapshot, options, routes, initial_charges=None):
    s = snapshot["scenario"]
    return {
        "schema_version": "0.1.0-draft",
        "plan_id": options["plan_id"],
        "scenario_id": s["scenario_id"],
        "snapshot_id": snapshot["snapshot_id"],
        "scenario_state_version": s["state_version"],
        "data_origin": "solver",
        "objective": options["objective"],
        "solver_status": "FEASIBLE",
        "has_validated_plan": True,
        "model_scope": BASE_SCOPE
        + (["terrain"] if s["terrain"]["status"] == "available" else [])
        + (["restricted_zone"] if s.get("restricted_zones") else [])
        + (["ground_resource"] if s.get("resource_limits") else []),
        **(
            {"initial_charges": copy.deepcopy(initial_charges or [])}
            if s.get("resource_limits")
            else {}
        ),
        "metrics": {
            "last_delivery_s": max(
                v["delivery_complete_s"] for r in routes for v in r["visits"]
            ),
            "makespan_s": max(r["return_s"] for r in routes),
            "energy_kwh": sum(r["energy_kwh"] for r in routes),
            "cost_cny": None,
            "sortie_count": len(routes),
            "unserved_demand_count": 0,
            "mandatory_served_count": sum(d["mandatory"] for d in s["demands"]),
            "mandatory_total_count": sum(d["mandatory"] for d in s["demands"]),
            "min_return_soc": min(r["return_soc"] for r in routes),
        },
        "sorties": routes,
        "unserved_demand_ids": [],
        "validation": {"status": "not_run", "checks": []},
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "solver_notes": [
            "真实限时多起点插入启发式；未证明全局最优。",
            "共同排序先减少优先级加权逐箱期望延期，再比较所选时间/能耗/均衡目标；更优方案可能增加另一指标。",
            (
                f"有限保障：准备工位{s['resource_limits']['prep_slots']}、充电端口{s['resource_limits']['charging_ports']}，初始低SOC先补满并记录等待。"
                if s.get("resource_limits")
                else "题设载荷能耗、两段充电；充电端口无限。"
            ),
            "航段为WGS84测地线近似；不包含风雨、实时障碍与全航程多机避碰。",
            *(
                [
                    "local_polygon_v1：基地100km范围静态禁入区与米制缓冲，绕行另加10m数值余量；测地段20m弦检查。"
                ]
                if s.get("restricted_zones")
                else []
            ),
            "通信未评估；输出为仿真/规划建议，不是实飞许可。",
        ],
        "parent_plan_id": options["parent_plan_id"],
        "event_id": options["event_id"],
        "change_summary": (
            {
                "preserved_sortie_ids": [],
                "removed_sortie_ids": [],
                "added_sortie_ids": [r["sortie_id"] for r in routes],
            }
            if options["parent_plan_id"]
            else None
        ),
    }


def solve(snapshot, options, progress_callback=None, *, initial_plan=None):
    started = time.perf_counter()
    best = None
    first = None
    count = 0
    cache = {}

    def progress(stage):
        if progress_callback:
            progress_callback(
                {
                    "stage": stage,
                    "elapsed_s": time.perf_counter() - started,
                    "candidate_count": count,
                }
            )

    try:
        validate_snapshot(snapshot)
        validate_options(options, snapshot)
        s = snapshot["scenario"]
        if has_execution_facts(s):
            return _outcome(
                "UNKNOWN",
                options,
                started,
                reason="unsupported_scope",
                diagnostics=[
                    diagnostic(
                        "UNSUPPORTED_EXECUTION_STATE",
                        "当前只支持尚未执行的规划场景；存在装载、在途、已交付或已占用事实，不能通过全量求解覆盖。",
                    )
                ],
            )
        if set(options["requested_model_scope"]) - set(
            capabilities()["supported_model_scope"]
        ):
            return _outcome(
                "UNKNOWN",
                options,
                started,
                reason="unsupported_scope",
                diagnostics=[
                    diagnostic(
                        "UNSUPPORTED_SCOPE", "请求包含当前引擎尚未支持的模型范围。"
                    )
                ],
            )
        if (
            "terrain" in options["requested_model_scope"]
            and s["terrain"]["status"] != "available"
        ):
            return _outcome(
                "UNKNOWN",
                options,
                started,
                reason="input_not_ready",
                diagnostics=[
                    diagnostic("INPUT_NOT_READY", "强制地形检查但没有可用DEM。")
                ],
            )
        if s["data_origin"] == "mock":
            raise InputNotReady("Mock只能用于界面开发，不能作为本次真实求解输入。")
        for t in s["drone_types"]:
            parameters(t)
        cargo_ids = _required_cargos(s)
        if not cargo_ids:
            raise InputNotReady("没有可调度的需求箱件。")
        if not s["base"]["available"]:
            return _outcome(
                "INFEASIBLE",
                options,
                started,
                diagnostics=[
                    diagnostic(
                        "BASE_UNAVAILABLE",
                        "当前单基地模型的调度基地不可用，无法执行运输。",
                    )
                ],
            )
        available = [
            d
            for d in s["drones"]
            if d["status"] == "available" and d["location_id"] == s["base"]["id"]
        ]
        if not available:
            return _outcome(
                "INFEASIBLE",
                options,
                started,
                diagnostics=[
                    diagnostic("NO_AVAILABLE_DRONE", "当前单基地模型无任何可用运输机。")
                ],
            )
        if not any(
            b["status"] in ("available", "charging")
            and b["soh"] > 0
            and b["location_id"] == s["base"]["id"]
            and b["compatible_type_id"] in {d["type_id"] for d in available}
            for b in s["batteries"]
        ):
            return _outcome(
                "INFEASIBLE",
                options,
                started,
                diagnostics=[
                    diagnostic("NO_COMPATIBLE_BATTERY", "当前模型没有可用的兼容电池。")
                ],
            )
        budget = max(0.01, min(float(options["time_limit_s"]), 3600.0))
        if "ground_resource" in options["requested_model_scope"] and not s.get(
            "resource_limits"
        ):
            raise InputNotReady("请求地面容量检查，但场景尚未设置准备工位与充电端口。")
        if "communication" in options["requested_model_scope"]:
            if not s.get("communication"):
                return _outcome(
                    "UNKNOWN",
                    options,
                    started,
                    reason="unsupported_scope",
                    diagnostics=[
                        diagnostic(
                            "INPUT_NOT_READY", "连续通信尚未配置链路参数和中继资源。"
                        )
                    ],
                )
            if not s["policy"]["requires_communication"]:
                raise InputNotReady(
                    "请求通信求解前，请先开启场景的连续通信策略并保存新版本。"
                )
            return _solve_joint(
                snapshot, options, started, progress_callback, initial_plan
            )
        deadline = started + (
            min(5.0, budget * 0.3) if options["mode"] == "improve" else budget * 0.9
        )
        if initial_plan is not None:
            if (
                initial_plan["data_origin"] != "solver"
                or not initial_plan["has_validated_plan"]
            ):
                raise InputNotReady("深入优化只能继承已发布的真实Solver方案。")
            if (
                options["mode"] != "improve"
                or initial_plan["snapshot_id"] != snapshot["snapshot_id"]
                or initial_plan["objective"] != options["objective"]
            ):
                raise InputNotReady("深入优化基线必须来自同一快照，且mode=improve。")
            if validate(snapshot, initial_plan)["status"] != "passed":
                raise InputNotReady("深入优化基线未通过当前快照的独立检查。")
            base = _make_plan(
                snapshot,
                options,
                copy.deepcopy(initial_plan["sorties"]),
                initial_plan.get("initial_charges", []),
            )
            base["validation"] = validate(snapshot, base)
            base["solver_notes"].append(
                "深入优化继承已验算基线 "
                + initial_plan["plan_id"]
                + "；只有严格改善共同目标的候选才替换基线。"
            )
            best = (objective_score(s, base, options["objective"]), base)
            first = time.perf_counter() - started
            count = 1
        progress("计算航段与箱件插入")
        non_improving = 0
        primary_best = best[0][0] if best else math.inf
        for iteration in range(48):
            if time.perf_counter() >= deadline:
                break
            schedule = _construct(
                s,
                ("time", "energy", "balanced")[iteration % 3],
                options["seed"] + iteration,
                deadline,
                cache,
            )
            if schedule is None:
                non_improving += 1
                continue
            candidate = _make_plan(
                snapshot, options, schedule["sorties"], schedule["initial_charges"]
            )
            progress("独立重算约束")
            report = validate(snapshot, candidate)
            count += 1
            if report["status"] != "passed":
                return _outcome(
                    "ERROR",
                    options,
                    started,
                    reason="validation_failed",
                    validation=report,
                    diagnostics=[
                        diagnostic(
                            "VALIDATION_FAILED", "候选未通过独立检查，已阻止发布。"
                        )
                    ],
                    count=count,
                )
            candidate["validation"] = report
            if first is None:
                first = time.perf_counter() - started
            score = objective_score(s, candidate, options["objective"])
            if best is None or score < best[0]:
                best = (score, candidate)
            # The construction portfolio and its early stop use the common
            # primary goal, so strategy comparisons explore the same sequence.
            if score[0] < primary_best - 1e-7:
                primary_best = score[0]
                non_improving = 0
            else:
                non_improving += 1
            progress("改进已验证方案")
            if non_improving >= 12:
                break
        deep_limited = False
        if best and options["mode"] == "improve":
            remaining = started + budget * 0.96 - time.perf_counter()
            if remaining > 0.25:
                try:
                    from solver.cp_pool import optimize

                    routes, details = optimize(
                        s,
                        best[1],
                        options["objective"],
                        remaining,
                        options["seed"],
                        progress,
                    )
                except (ImportError, ValueError, OverflowError, RuntimeError) as exc:
                    routes = None
                    details = {
                        "status": "ERROR_KEEP_INCUMBENT",
                        "pool_size": 0,
                        "error_type": type(exc).__name__,
                    }
                deep_limited = details["status"] in ("FEASIBLE", "UNKNOWN")
                summary = f"有限路线池深入优化：{details['pool_size']}条候选，CP-SAT状态{details['status']}，10毫秒保守时间网格、单线程；未证明所有路线空间的全局最优。"
                if routes:
                    candidate = _make_plan(
                        snapshot, options, routes, best[1].get("initial_charges", [])
                    )
                    report = validate(snapshot, candidate)
                    count += 1
                    if report["status"] == "passed":
                        candidate["validation"] = report
                        score = objective_score(s, candidate, options["objective"])
                        if score < best[0]:
                            best = (score, candidate)
                    else:
                        summary += "深入候选未通过独立检查，已保留原可行方案。"
                best[1]["solver_notes"].append(summary)
        if best:
            return _outcome(
                "FEASIBLE",
                options,
                started,
                plan=best[1],
                first=first,
                count=count,
                validation=best[1]["validation"],
                reason=(
                    "time_limit"
                    if deep_limited
                    or time.perf_counter()
                    >= (
                        started + budget * 0.96
                        if options["mode"] == "improve"
                        else deadline
                    )
                    else "finished"
                ),
            )
        return _outcome(
            "UNKNOWN",
            options,
            started,
            reason="time_limit" if time.perf_counter() >= deadline else "finished",
            count=count,
            diagnostics=[
                diagnostic(
                    "NO_VALIDATED_CANDIDATE",
                    "当前预算和候选范围内未找到完整可行方案，可增加预算、设备或调整非关键时限。",
                )
            ],
        )
    except (ContractError, InputNotReady, KeyError, ValueError) as exc:
        return _outcome(
            "UNKNOWN",
            options,
            started,
            reason="input_not_ready",
            diagnostics=[diagnostic("INPUT_NOT_READY", str(exc))],
        )


def _joint_search_evidence(details):
    return {
        "method": "fixed_grouping_joint_cp_v1",
        "status": details["status"],
        "station_count": details.get("stations", 0),
        "coverage_atom_count": details.get("atoms", 0),
        "relay_slot_limit": details.get("relay_slots", 0),
        "stages": details.get("stages", []),
    }


def _solve_joint(snapshot, options, started, progress_callback, initial_plan):
    """Build a private transport relaxation, then independently check the joint plan."""
    import hashlib
    from shared.contracts import content_hash
    from solver.joint import schedule

    s = snapshot["scenario"]
    budget = max(0.01, min(float(options["time_limit_s"]), 3600))
    deadline = started + budget * 0.90
    incumbent = None
    first_verified = None
    if initial_plan is not None:
        fresh_validation = validate(snapshot, initial_plan)
        if (
            options["mode"] != "improve"
            or initial_plan["data_origin"] != "solver"
            or not initial_plan["has_validated_plan"]
            or initial_plan["snapshot_id"] != snapshot["snapshot_id"]
            or initial_plan["objective"] != options["objective"]
            or fresh_validation["status"] != "passed"
        ):
            raise InputNotReady("联合深入优化基线必须是同一快照/策略的已验证方案。")
        incumbent = copy.deepcopy(initial_plan)
        incumbent["validation"] = fresh_validation
        incumbent["solver_status"] = "FEASIBLE"
        first_verified = time.perf_counter() - started

    def progress(message):
        if progress_callback:
            progress_callback(
                {
                    "stage": message,
                    "elapsed_s": time.perf_counter() - started,
                    "candidate_count": int(incumbent is not None),
                }
            )

    progress("生成私有运输松弛候选，尚不是联合可行方案")
    relaxed = copy.deepcopy(snapshot)
    relaxed["scenario"]["policy"]["requires_communication"] = False
    relaxed["scenario"].pop("communication", None)
    relaxed["content_hash"] = content_hash(relaxed["scenario"])
    relaxed["snapshot_id"] = (
        "SNAP-RELAXED-"
        + hashlib.sha256(snapshot["snapshot_id"].encode()).hexdigest()[:16]
    )
    seed_options = {
        **options,
        "snapshot_id": relaxed["snapshot_id"],
        "plan_id": "PLAN-PRIVATE-RELAXED",
        "mode": "quick",
        "time_limit_s": min(5, budget * 0.18),
        "parent_plan_id": None,
        "event_id": None,
        "requested_model_scope": [
            code for code in options["requested_model_scope"] if code != "communication"
        ],
    }
    from solver.adapters.joint_patterns import transport_pattern

    candidate = None
    seed = {"plan": None, "candidate_count": 0, "diagnostics": []}
    details = {"status": "NO_TRANSPORT_SEED"}
    for family in ["archive", "heuristic"]:
        if candidate is not None or time.perf_counter() >= deadline - 0.2:
            break
        schedule_options = {}
        attempt_deadline = deadline
        if family == "archive":
            if budget < 20:
                continue
            pattern = transport_pattern(s, _required_cargos(s, options["seed"]))
            if pattern is None:
                continue
            seed = {"plan": pattern[0], "candidate_count": 0, "diagnostics": []}
            schedule_options = {
                "station_ids": pattern[1],
                "max_relay_sorties": 3,
                "coverage_block_s": 600,
            }
            attempt_deadline = min(
                deadline, time.perf_counter() + min(40, budget * 0.6)
            )
            progress("重算历史分组候选的全部物理，搜索新的联合排程")
        else:
            remaining = deadline - time.perf_counter()
            if remaining <= 0.2:
                break
            seed_options["time_limit_s"] = min(
                seed_options["time_limit_s"], remaining * 0.2
            )
            seed = solve(relaxed, seed_options)
        if seed["plan"]:
            try:
                routes, relays, communication, details = schedule(
                    s,
                    seed["plan"],
                    options,
                    attempt_deadline,
                    progress,
                    **schedule_options,
                )
                if routes:
                    candidate = _make_plan(snapshot, options, routes)
                    candidate["model_scope"].append("communication")
                    candidate["relay_sorties"] = relays
                    relay_energy = sum(r["energy_kwh"] for r in relays)
                    candidate["joint_metrics"] = {
                        "relay_energy_kwh": relay_energy,
                        "joint_energy_kwh": candidate["metrics"]["energy_kwh"]
                        + relay_energy,
                        "joint_makespan_s": max(
                            [
                                candidate["metrics"]["makespan_s"],
                                *[r["return_s"] for r in relays],
                            ]
                        ),
                        "relay_sortie_count": len(relays),
                    }
                    candidate["communication_report"] = communication
                    candidate["joint_search"] = _joint_search_evidence(details)
                    candidate["solver_notes"] = [
                        note
                        for note in candidate["solver_notes"]
                        if not note.startswith("通信未评估")
                    ]
                    candidate["solver_notes"].extend(
                        [
                            "有限运输组批/访问顺序与悬停候选上的联合排程；解析连续覆盖，未证明原问题全局最优。",
                            "projected_dem_radio_v1：UTM闭四边形DEM、最多250m运动弦、2mm像元数值外扩；不是实际无线电覆盖认证。",
                            "既有metrics仅统计运输，joint_metrics统计运输与中继；中继CP采用全充电时长上界，输出与独立检查使用实际两阶段补能。",
                            f"有限联合候选：{details.get('stations', 0)}个悬停位置、{details.get('atoms', 0)}段覆盖需求；详细搜索状态见计划JSON，不代表原问题全局最优。",
                        ]
                    )
                    progress("独立复算中继物理、实体占用和全阶段通信")
                    candidate["validation"] = validate(snapshot, candidate)
                    if candidate["validation"]["status"] != "passed":
                        details = {
                            "status": "VALIDATION_FAILED",
                            "checks": candidate["validation"]["checks"],
                        }
                        candidate = None
                    else:
                        if first_verified is None:
                            first_verified = time.perf_counter() - started
                        if family == "archive":
                            candidate["solver_notes"].append(
                                "历史分组仅作候选；箱件、飞行物理、排程、实体和连续通信均按当前快照重新计算，未复用历史时刻或能耗。"
                            )
            except (InputNotReady, TimeoutError) as exc:
                details = {
                    "status": "LIMITED_CANDIDATES_OR_BUDGET",
                    "message": str(exc),
                }
    if incumbent is not None and (
        candidate is None
        or objective_score(s, incumbent, options["objective"])
        <= objective_score(s, candidate, options["objective"])
    ):
        candidate = incumbent
        candidate.update(
            plan_id=options["plan_id"],
            generated_at=datetime.now(timezone.utc).isoformat(),
        )
        candidate["solver_notes"].append(
            "联合深入优化保留已验算基线；有限分解内未找到严格改善。"
        )
    if candidate is None:
        if details["status"] == "VALIDATION_FAILED":
            return _outcome(
                "ERROR",
                options,
                started,
                reason="validation_failed",
                count=seed["candidate_count"],
                validation={"status": "failed", "checks": details["checks"]},
                diagnostics=[
                    diagnostic(
                        "VALIDATION_FAILED", "联合候选未通过独立重算，已阻止发布。"
                    )
                ],
                joint_search=_joint_search_evidence(details),
            )
        message = details.get("message") or (
            seed["diagnostics"][0]["message"]
            if seed["diagnostics"]
            else f"有限模型状态{details['status']}，检查了{details.get('stations', 0)}个悬停位置。"
        )
        return _outcome(
            "UNKNOWN",
            options,
            started,
            reason=(
                "time_limit"
                if time.perf_counter() >= deadline
                or details["status"] in ("UNKNOWN", "BUDGET")
                else "finished"
            ),
            count=seed["candidate_count"],
            diagnostics=[
                diagnostic(
                    "JOINT_CANDIDATE_NOT_FOUND",
                    "当前候选与预算内未得到可验证的联合方案。"
                    + message
                    + "这不证明原问题不可行。",
                )
            ],
            joint_search=_joint_search_evidence(details),
        )
    return _outcome(
        "FEASIBLE",
        options,
        started,
        plan=candidate,
        first=first_verified,
        count=seed["candidate_count"] + 1,
        validation=candidate["validation"],
        reason="time_limit" if time.perf_counter() >= deadline else "finished",
    )


def _try_local_repair(snapshot, previous_plan, options, started, progress_callback):
    """Keep complete validated reservations, expanding through resource successors if needed."""
    try:
        validate_snapshot(snapshot)
        validate_options(options, snapshot)
        s = snapshot["scenario"]
        if s["policy"]["requires_communication"]:
            return None
        if s["data_origin"] == "mock" or not s["base"]["available"]:
            return None
        if set(options["requested_model_scope"]) - set(
            capabilities()["supported_model_scope"]
        ):
            return None
        if (
            "terrain" in options["requested_model_scope"]
            and s["terrain"]["status"] != "available"
        ):
            return None
        # Retaining old battery return SOC is exact only for these initial full-charge states.
        # Other initial SOC/charging states use the independently verified full solver.
        if any(
            abs(b["soc"] - 1) > 1e-9 or b["status"] == "charging"
            for b in s["batteries"]
        ):
            return None
        available = {d["drone_id"] for d in s["drones"] if d["status"] == "available"}
        available_batteries = {
            b["battery_id"] for b in s["batteries"] if b["status"] == "available"
        }
        direct = {
            r["sortie_id"]
            for r in previous_plan["sorties"]
            if r["drone_id"] not in available
            or r["battery_id"] not in available_batteries
        }
        expanded, edges = affected_closure(previous_plan["sorties"], direct)
        neighborhoods = [direct] + ([expanded] if expanded != direct else [])
        budget = min(6.0, float(options["time_limit_s"]) * 0.45)
        cache = {}
        count = 0
        first = None
        for stage, removed in enumerate(neighborhoods):
            deadline = started + budget * (stage + 1) / len(neighborhoods)
            fixed = [
                copy.deepcopy(r)
                for r in previous_plan["sorties"]
                if r["sortie_id"] not in removed
            ]
            targets = [
                cid
                for r in previous_plan["sorties"]
                if r["sortie_id"] in removed
                for cid in r["cargo_ids"]
            ]
            best = None
            for seed in range(5):
                if time.perf_counter() >= deadline:
                    break
                if progress_callback:
                    progress_callback(
                        {
                            "stage": (
                                "保留任务并局部修复"
                                if stage == 0
                                else "沿资源依赖扩大修复"
                            ),
                            "elapsed_s": time.perf_counter() - started,
                            "candidate_count": count,
                        }
                    )
                changed = _construct(
                    s,
                    options["objective"],
                    options["seed"] + seed,
                    deadline,
                    cache,
                    target_cargos=targets,
                    fixed_routes=fixed,
                )
                if changed is None:
                    continue
                routes = sorted(
                    [*fixed, *changed["sorties"]],
                    key=lambda r: (r["prepare_start_s"], r["sortie_id"]),
                )
                candidate = _make_plan(
                    snapshot, options, routes, changed["initial_charges"]
                )
                report = validate(snapshot, candidate)
                count += 1
                if report["status"] != "passed":
                    continue
                candidate["validation"] = report
                if first is None:
                    first = time.perf_counter() - started
                score = objective_score(s, candidate, options["objective"])
                if best is None or score < best[0]:
                    best = score, candidate
            if best:
                best[1]["solver_notes"].append(
                    f"依赖图局部修复：{len(edges)}条机体/电池前序边，直接影响{len(direct)}架次，传播范围{len(expanded)}架次，本轮保留{len(fixed)}个原架次及原时间。启发式未证明最小改动。"
                )
                return _outcome(
                    "FEASIBLE",
                    options,
                    started,
                    plan=best[1],
                    validation=best[1]["validation"],
                    first=first,
                    count=count,
                )
    except (ContractError, InputNotReady, KeyError, ValueError):
        return None
    return None


def replan(snapshot, previous_plan, event, options, progress_callback=None):
    started = time.perf_counter()
    if event.get("event_type") not in capabilities()["supported_events"]:
        return _outcome(
            "UNKNOWN",
            options,
            started,
            reason="unsupported_scope",
            diagnostics=[
                diagnostic("UNSUPPORTED_SCOPE", "当前只支持零时刻机体或运输电池退出。")
            ],
        )
    try:
        validate_snapshot(snapshot)
        validate_options(options, snapshot)
        validate_schema("plan", previous_plan)
        validate_applied_event(event, snapshot["scenario"])
        require(
            options["mode"] == "replan"
            and options["parent_plan_id"] == previous_plan["plan_id"]
            and options["event_id"] == event["event_id"]
            and previous_plan["scenario_id"] == snapshot["scenario_id"]
            and previous_plan["scenario_state_version"]
            <= event["expected_state_version"]
            and previous_plan["data_origin"] == "solver"
            and previous_plan["has_validated_plan"]
            and previous_plan["validation"]["status"] == "passed",
            "重规划身份链或原方案来源不完整。",
        )
    except (ValueError, KeyError, TypeError) as exc:
        return _outcome(
            "UNKNOWN",
            options,
            started,
            reason="input_not_ready",
            diagnostics=[diagnostic("INPUT_NOT_READY", str(exc))],
        )
    result = _try_local_repair(
        snapshot, previous_plan, options, started, progress_callback
    )
    if result is None:
        spent = time.perf_counter() - started
        remaining = max(0.001, float(options["time_limit_s"]) - spent)

        def report_full(value):
            if progress_callback:
                progress_callback(
                    {
                        **value,
                        "stage": "全量回退 · " + value["stage"],
                        "elapsed_s": value["elapsed_s"] + spent,
                    }
                )

        result = solve(snapshot, {**options, "time_limit_s": remaining}, report_full)
        result["runtime_s"] = time.perf_counter() - started
        if result["first_feasible_s"] is not None:
            result["first_feasible_s"] += spent
        if result["plan"]:
            result["plan"]["solver_notes"].append(
                "局部修复不适用或未找到可行候选，已在剩余预算内全量回退。"
            )
    if result["plan"]:
        old = {r["sortie_id"] for r in previous_plan["sorties"]}
        new = {r["sortie_id"] for r in result["plan"]["sorties"]}
        result["plan"]["change_summary"] = {
            "preserved_sortie_ids": sorted(old & new),
            "removed_sortie_ids": sorted(old - new),
            "added_sortie_ids": sorted(new - old),
        }
    return result
