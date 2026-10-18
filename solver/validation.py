"""Rebuild a candidate's physics and resources from the snapshot, ignoring self-reported checks."""

from __future__ import annotations

import copy
import math

from shared.contracts import (
    ContractError,
    validate_plan,
    validate_snapshot,
    has_execution_facts,
)
from solver.physics import InputNotReady, charge_seconds, leg, parameters
from solver.routing import path_is_clear
from solver.numerics import CAPACITY_TOLERANCE
from solver.weather import check_plan as check_weather_plan

BASE_SCOPE = [
    "cargo_unique",
    "capacity",
    "inventory",
    "aircraft",
    "battery",
    "time_window",
    "energy",
]


def validate(snapshot, plan):
    checks = []

    def add(code, status, message, object_id=None):
        checks.append(
            {"code": code, "status": status, "object_id": object_id, "message": message}
        )

    try:
        validate_snapshot(snapshot)
        # Shape/resource checks must not trust or require the optimizer's publication flag.
        candidate = copy.deepcopy(plan)
        candidate.update(
            data_origin="imported_historical",
            has_validated_plan=False,
            validation={"status": "not_run", "checks": []},
        )
        validate_plan(candidate, snapshot)
    except (ContractError, KeyError, TypeError, ValueError) as exc:
        add("cargo_unique", "failed", str(exc))
        return {"status": "failed", "checks": checks}
    s = snapshot["scenario"]
    if s["data_origin"] == "mock" or has_execution_facts(s):
        add("inventory", "failed", "当前真实规划模型不能认证Mock输入或覆盖已有执行事实")
    if not s["base"]["available"]:
        add("inventory", "failed", "调度基地不可用，不能发布运输方案")
    types = {t["type_id"]: t for t in s["drone_types"]}
    drones = {d["drone_id"]: d for d in s["drones"]}
    batteries = {b["battery_id"]: b for b in s["batteries"]}
    cargos = {c["cargo_id"]: c for c in s["cargo_items"]}
    demands = {d["demand_id"]: d for d in s["demands"]}
    battery_uses = {}
    energy_total = 0.0
    terrain_ok = True
    zone_checked = 0
    limits = s.get("resource_limits")
    initial_charges_by_battery = {}
    charge_windows = []

    def equal(actual, expected, code, label, object_id):
        if actual is None or not math.isclose(
            actual, expected, rel_tol=1e-8, abs_tol=1e-5
        ):
            add(
                code,
                "failed",
                f"{label}不一致：给定{actual}，独立重算{expected:.6f}",
                object_id,
            )

    if plan.get("initial_charges") and not limits:
        add("ground_resource", "failed", "未声明有限地面模型，不能增加初始补能任务")
    for row in plan.get("initial_charges", []):
        bid = row["battery_id"]
        if bid not in batteries or bid in initial_charges_by_battery:
            add("battery", "failed", "初始补能引用不存在或重复的电池", bid)
            continue
        b = batteries[bid]
        typ = types[b["compatible_type_id"]]
        try:
            parameters(typ)
        except (InputNotReady, KeyError) as exc:
            add("battery", "failed", str(exc), bid)
            continue
        if (
            b["status"] not in ["available", "charging"]
            or b["location_id"] != s["base"]["id"]
            or b["soh"] <= 0
        ):
            add("inventory", "failed", "初始补能电池状态或位置不允许", bid)
        if row["start_s"] < b["available_after_s"] or row["end_s"] < row["start_s"]:
            add("time_window", "failed", "初始补能发生在可用时间前或时间倒序", bid)
        equal(row["from_soc"], b["soc"], "battery", "初始补能SOC", bid)
        equal(
            row["end_s"] - row["start_s"],
            charge_seconds(typ, b["soc"]),
            "battery",
            "初始补能时长",
            bid,
        )
        initial_charges_by_battery[bid] = row
        charge_windows.append((row["start_s"], row["end_s"]))

    for route in plan["sorties"]:
        rid = route["sortie_id"]
        typ = types[drones[route["drone_id"]]["type_id"]]
        try:
            p = parameters(typ)
            mass = math.fsum(cargos[c]["mass_kg"] for c in route["cargo_ids"])
            volume = math.fsum(cargos[c]["volume_l"] for c in route["cargo_ids"])
            if (
                mass > typ["max_payload_kg"] + CAPACITY_TOLERANCE
                or volume > typ["max_volume_l"] + CAPACITY_TOLERANCE
            ):
                add("capacity", "failed", "质量或容积超过机型上限", rid)
            prep = typ["prepare_duration_s"] + p["load_per_box_s"] * len(
                route["cargo_ids"]
            )
            equal(
                route["takeoff_s"] - route["prepare_start_s"],
                prep,
                "time_window",
                "准备时长",
                rid,
            )
            clock = route["prepare_start_s"] + prep
            energy = 0.0
            current = s["base"]["id"]
            expected_coords = [s["base"]["coordinates"]]
            nodes = {n["id"]: n for n in s["sites"]}
            for visit in [
                *route["visits"],
                {"site_id": s["base"]["id"], "cargo_ids": []},
            ]:
                geometry = leg(s, typ, current, visit["site_id"])
                expected_coords.extend([list(p) for p in geometry.path[1:]])
                terrain_ok = terrain_ok and geometry.terrain_checked
                # Recompute from raw mass and model parameters; never read optimizer energy contributions.
                ratio = max(0.0, mass) / typ["max_payload_kg"]
                span = (
                    p["empty_range_m"]
                    - (p["empty_range_m"] - p["full_range_m"]) * ratio**1.5
                )
                energy += (
                    p["reference_energy_kwh"] * geometry.distance_m / span
                    + (typ["empty_mass_kg"] + mass)
                    * 9.81
                    * geometry.climb_m
                    / (p["climb_efficiency"] * 3600000)
                ) * p.get("energy_scale", 1.0)
                clock += (
                    geometry.distance_m / typ["cruise_speed_mps"]
                    + geometry.climb_m / typ["climb_speed_mps"]
                    + geometry.descend_m / typ["descent_speed_mps"]
                ) * p.get("flight_time_scale", 1.0)
                if visit["cargo_ids"]:
                    clock += typ["handover_fixed_s"] + typ["handover_per_box_s"] * len(
                        visit["cargo_ids"]
                    )
                    equal(
                        visit["delivery_complete_s"],
                        clock,
                        "time_window",
                        "交接完成时间",
                        rid,
                    )
                    for cid in visit["cargo_ids"]:
                        due = demands[cargos[cid]["demand_id"]]["hard_deadline_s"]
                        if due is not None and clock > due + 1e-6:
                            add(
                                "time_window",
                                "failed",
                                f"{cid}超过硬截止{due:.3f}s",
                                rid,
                            )
                        if not nodes[visit["site_id"]]["available"]:
                            add("inventory", "failed", "投送点不可用", visit["site_id"])
                    mass -= sum(cargos[c]["mass_kg"] for c in visit["cargo_ids"])
                current = visit["site_id"]
            if route["route_geometry"]["coordinates"] != expected_coords:
                add("time_window", "failed", "路线几何与实际访问次序不一致", rid)
            if s.get("restricted_zones") and not path_is_clear(
                s, route["route_geometry"]["coordinates"]
            ):
                add("restricted_zone", "failed", "提交航线接触限制区或其安全缓冲", rid)
            zone_checked += 1
            equal(route["return_s"], clock, "time_window", "返航时刻", rid)
            equal(
                route["drone_released_s"],
                clock + typ["turnaround_duration_s"],
                "aircraft",
                "机体释放",
                rid,
            )
            equal(route["energy_kwh"], energy, "energy", "架次能耗", rid)
            energy_total += energy
            battery = batteries[route["battery_id"]]
            usable = battery["capacity_kwh"] * battery["soh"]
            if usable <= 0 or route["return_soc"] is None:
                add("energy", "failed", "电池可用容量或返航SOC无效", rid)
                continue
            if route["return_soc"] < s["policy"]["min_return_soc"] - 1e-8:
                add("energy", "failed", "返航电量低于策略储备", rid)
            departure = route["return_soc"] + energy / usable
            if departure > 1 + 1e-8:
                add("energy", "failed", "出发可用电量不足以完成该架次", rid)
            charge_start = route.get("charge_start_s", clock)
            if limits and "charge_start_s" not in route:
                add("ground_resource", "failed", "有限端口模型缺少充电开始时刻", rid)
            if not limits and not math.isclose(charge_start, clock, abs_tol=1e-7):
                add("ground_resource", "failed", "无限端口模型不能隐含充电排队", rid)
            if charge_start < clock - 1e-7:
                add("battery", "failed", "尚未返航即开始充电", rid)
            equal(
                route["battery_released_s"],
                charge_start + charge_seconds(typ, route["return_soc"]),
                "battery",
                "补能完成时刻",
                rid,
            )
            charge_windows.append((charge_start, route["battery_released_s"]))
            battery_uses.setdefault(route["battery_id"], []).append(
                (
                    route["prepare_start_s"],
                    route["battery_released_s"],
                    departure,
                    typ,
                    rid,
                )
            )
        except (InputNotReady, KeyError, ValueError, ZeroDivisionError) as exc:
            add("energy", "failed", str(exc), rid)
            terrain_ok = False
    for bid, uses in battery_uses.items():
        b = batteries[bid]
        uses.sort()
        for i, (start, release, departure, typ, rid) in enumerate(uses):
            if i == 0:
                initial = b["soc"]
                fully_ready = b["available_after_s"] + charge_seconds(typ, initial)
                allowed = ([initial] if b["status"] != "charging" else []) + (
                    [1.0] if start + 1e-8 >= fully_ready else []
                )
                if limits:
                    # Explicit ground model cannot infer an unrecorded free charger.
                    initial_row = initial_charges_by_battery.get(bid)
                    allowed = (
                        [1.0]
                        if initial_row and start + 1e-8 >= initial_row["end_s"]
                        else (
                            [b["soc"]]
                            if not initial_row and abs(b["soc"] - 1) < 1e-9
                            else []
                        )
                    )
                if not any(math.isclose(departure, v, abs_tol=1e-7) for v in allowed):
                    add(
                        "battery",
                        "failed",
                        "首次出发SOC与输入状态/初始补能时间不一致",
                        rid,
                    )
            elif not math.isclose(departure, 1.0, abs_tol=1e-7):
                add("battery", "failed", "复用电池必须在本模型完成补能", rid)
    if plan["unserved_demand_ids"]:
        add("inventory", "failed", "当前完整服务模式仍存在未保障需求")
    if s["data_origin"] == "mock":
        add("inventory", "failed", "Mock数据不能发布已验证方案")
    equal(
        plan["metrics"]["energy_kwh"], energy_total, "energy", "总能耗", plan["plan_id"]
    )
    for code in BASE_SCOPE:
        if not any(c["code"] == code and c["status"] == "failed" for c in checks):
            add(code, "passed", "已根据输入、架次与资源实体独立复算")
    add(
        "terrain",
        "passed" if terrain_ok and bool(plan["sorties"]) else "not_evaluated",
        (
            "绑定DEM闭像元航段净空已检查；非现实障碍/适航认证"
            if terrain_ok
            else "缺少可认证DEM，地形未评估"
        ),
    )
    if s["policy"]["requires_communication"] or "communication" in plan["model_scope"]:
        try:
            from solver.relay import validate_joint

            issues, report = validate_joint(s, plan)
            for code, message, identity in issues:
                add(code, "failed", message, identity)
            if not issues:
                add(
                    "communication",
                    "passed",
                    f"投影DEM连续区间模型：直连{report['direct_s']:.2f}秒、中继{report['relay_s']:.2f}秒、缺口0；非现实链路认证",
                )
        except (InputNotReady, KeyError, TypeError, ValueError) as exc:
            add("communication", "failed", str(exc))
    else:
        add("communication", "not_evaluated", "当前方案未要求连续无线链路检查")
        if plan.get("relay_sorties") or plan.get("communication_report"):
            add("communication", "failed", "未启用通信模型却包含中继或覆盖报告")
    charge_windows.extend(
        (r["charge_start_s"], r["component_released_s"])
        for r in plan.get("relay_sorties", [])
    )
    if limits:

        def peak(windows):
            events = sorted(
                [
                    (time, change)
                    for start, end in windows
                    if end > start
                    for time, change in [(start, 1), (end, -1)]
                ]
            )
            active = maximum = 0
            for _, change in events:
                active += change
                maximum = max(maximum, active)
            return maximum

        prep_peak = peak(
            [
                (r["prepare_start_s"], r["takeoff_s"])
                for r in [*plan["sorties"], *plan.get("relay_sorties", [])]
            ]
        )
        charge_peak = peak(charge_windows)
        if prep_peak > limits["prep_slots"]:
            add(
                "ground_resource",
                "failed",
                f"准备并发{prep_peak}超过工位{limits['prep_slots']}",
            )
        if charge_peak > limits["charging_ports"]:
            add(
                "ground_resource",
                "failed",
                f"充电并发{charge_peak}超过端口{limits['charging_ports']}",
            )
        if not any(
            c["code"] == "ground_resource" and c["status"] == "failed" for c in checks
        ):
            add(
                "ground_resource",
                "passed",
                f"准备峰值{prep_peak}/{limits['prep_slots']}，含初始补能的充电峰值{charge_peak}/{limits['charging_ports']}；等待占用电池",
            )
    if s.get("restricted_zones") and not any(
        c["code"] == "restricted_zone" and c["status"] == "failed" for c in checks
    ):
        add(
            "restricted_zone",
            (
                "passed"
                if zone_checked == len(plan["sorties"]) and zone_checked
                else "not_evaluated"
            ),
            "静态限制区及缓冲按测地航段20m弦检查；若航段输入无效则未完成，不含空域许可",
        )
    if s.get("weather") or "weather_window" in plan["model_scope"]:
        problems = check_weather_plan(s, plan)
        for message in problems:
            add("weather_window", "failed", message)
        if not problems:
            add(
                "weather_window",
                "passed",
                "逐架次机型限值与人工气象有效窗口独立复核；未评估风致能耗/时长。",
            )
    required = sorted(
        set(
            BASE_SCOPE
            + plan["model_scope"]
            + (["ground_resource"] if limits else [])
            + (["restricted_zone"] if s.get("restricted_zones") else [])
            + (["weather_window"] if s.get("weather") else [])
            + [d for d in ["terrain", "communication"] if s["policy"]["requires_" + d]]
        )
    )
    for code in set(required) - set(plan["model_scope"]):
        add(code, "failed", "Plan未声明场景要求的必检模型范围")
    failed = any(c["status"] == "failed" for c in checks)
    complete = all(
        any(c["code"] == code and c["status"] == "passed" for c in checks)
        for code in required
    )
    return {
        "status": "failed" if failed else ("passed" if complete else "partial"),
        "checks": checks,
    }
