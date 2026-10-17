"""Optional finite route-pool optimization; every returned schedule needs independent validation.

Uses OR-Tools optional resource intervals and exact demand coverage. It does not prove
global optimality over all possible routes, and is not used for non-full initial SOC.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import copy
import math
import time

from ortools.sat.python import cp_model

from solver.physics import charge_seconds, evaluate_route
from solver.ground import earliest_slot
from solver.identities import sortie_id

SCALE = (
    100  # Conservative 10 ms scheduling ticks; physical outputs retain full precision.
)
ENERGY_SCALE = 1000


def ticks(value):
    return math.ceil(value * SCALE - 1e-8)


def route_key(type_id, stops):
    return type_id, tuple((site, tuple(sorted(ids))) for site, ids in stops)


def candidate_pool(s, incumbent, deadline):
    drones = {d["drone_id"]: d for d in s["drones"]}
    types = {t["type_id"]: t for t in s["drone_types"]}
    available_types = {
        d["type_id"]
        for d in s["drones"]
        if d["status"] == "available" and d["location_id"] == s["base"]["id"]
    }
    boxes = {
        c["cargo_id"]: c
        for c in s["cargo_items"]
        if c["status"] == "available" and c["location_id"] == s["base"]["id"]
    }
    demands = {d["demand_id"]: d for d in s["demands"]}
    pool = {}
    hints = {}

    def add(type_id, stops):
        key = route_key(type_id, stops)
        if key in pool:
            return
        if len(pool) >= 850 or time.perf_counter() >= deadline:
            return
        route = evaluate_route(s, types[type_id], stops)
        if route is not None:
            pool[key] = route

    # Original route batches provide a feasible seed; also try every compatible aircraft type.
    for r in incumbent["sorties"]:
        stops = [(v["site_id"], v["cargo_ids"]) for v in r["visits"]]
        type_id = drones[r["drone_id"]]["type_id"]
        add(type_id, stops)
        hints[route_key(type_id, stops)] = r
        for t in sorted(available_types):
            add(t, stops)
        for site, ids in stops:
            for t in sorted(available_types):
                add(t, [(site, ids)])
                if len(ids) > 1:
                    middle = (len(ids) + 1) // 2
                    add(t, [(site, ids[:middle])])
                    add(t, [(site, ids[middle:])])
    by_site = defaultdict(list)
    for cid, c in boxes.items():
        by_site[demands[c["demand_id"]]["site_id"]].append(cid)

    def urgency(cid):
        d = demands[boxes[cid]["demand_id"]]
        return (
            d["hard_deadline_s"] if d["hard_deadline_s"] is not None else math.inf,
            -d["priority"],
            cid,
        )

    # Repartition per-site inventory with multiple packing orders, plus singleton fallbacks.
    for site, ids in sorted(by_site.items()):
        for t in sorted(available_types):
            typ = types[t]
            orders = [
                sorted(ids, key=urgency),
                sorted(ids, key=lambda c: (-boxes[c]["mass_kg"], urgency(c))),
                sorted(ids, key=lambda c: (-boxes[c]["volume_l"], urgency(c))),
            ]
            for order in orders:
                left = list(order)
                while left and len(pool) < 850 and time.perf_counter() < deadline:
                    batch = []
                    mass = volume = 0.0
                    for cid in left:
                        c = boxes[cid]
                        if (
                            mass + c["mass_kg"] <= typ["max_payload_kg"] + 1e-8
                            and volume + c["volume_l"] <= typ["max_volume_l"] + 1e-8
                        ):
                            batch.append(cid)
                            mass += c["mass_kg"]
                            volume += c["volume_l"]
                    if not batch:
                        break
                    add(t, [(site, batch)])
                    selected = set(batch)
                    left = [c for c in left if c not in selected]
            for cid in ids:
                add(t, [(site, [cid])])
    return list(pool.items()), hints


def optimize(s, incumbent, objective, seconds, seed, progress=None):
    started = time.perf_counter()
    deadline = started + max(0, seconds)
    stats = {
        "method": "finite_route_pool_cp_sat",
        "status": "NOT_RUN",
        "pool_size": 0,
        "workers": 1,
        "seed": seed,
        "tick_s": 1 / SCALE,
    }
    if seconds < 0.25:
        return None, {**stats, "status": "SKIPPED_BUDGET"}
    if any(
        b["status"] == "charging"
        or (b["status"] == "available" and abs(b["soc"] - 1) > 1e-9)
        for b in s["batteries"]
    ):
        return None, {**stats, "status": "SKIPPED_INITIAL_SOC"}
    limits = s.get("resource_limits")
    if progress:
        progress("构建可替代分批与路线池")
    pool, hints = candidate_pool(s, incumbent, started + min(2.5, seconds * 0.2))
    stats["pool_size"] = len(pool)
    if time.perf_counter() >= deadline - 0.1:
        return None, {**stats, "status": "SKIPPED_BUDGET"}
    drones = {
        d["drone_id"]: d
        for d in s["drones"]
        if d["status"] == "available" and d["location_id"] == s["base"]["id"]
    }
    batteries = {
        b["battery_id"]: b
        for b in s["batteries"]
        if b["status"] == "available"
        and b["location_id"] == s["base"]["id"]
        and b["soh"] > 0
    }
    types = {t["type_id"]: t for t in s["drone_types"]}
    cargos = {c["cargo_id"]: c for c in s["cargo_items"]}
    demands = {d["demand_id"]: d for d in s["demands"]}
    horizon = ticks(
        max(r["battery_released_s"] for r in incumbent["sorties"]) * 1.15 + 60
    )
    total_priority = sum(
        max(0, d["priority"]) * d["required_quantity"] for d in s["demands"]
    )
    energy_bound = sum(
        math.ceil(route["energy_kwh"] * ENERGY_SCALE) for _, route in pool
    )
    goal_bound = (
        horizon
        if objective == "time"
        else (
            energy_bound
            if objective == "energy"
            else horizon + 300 * SCALE // ENERGY_SCALE * energy_bound
        )
    )
    if (
        horizon > 100_000_000
        or horizon * max(1, total_priority) * (goal_bound + 1) > 2**60
    ):
        return None, {**stats, "status": "SKIPPED_INTEGER_RANGE"}
    model = cp_model.CpModel()
    windows = defaultdict(list)
    coverage = defaultdict(list)
    by_demand = defaultdict(list)
    records = []
    late_terms = []
    active_ends = []
    energy_terms = []
    preparation = []
    charging = []
    for index, (key, route) in enumerate(pool):
        typ = types[route["type_id"]]
        choices_d = [
            uid for uid, d in drones.items() if d["type_id"] == route["type_id"]
        ]
        choices_b = [
            bid
            for bid, b in batteries.items()
            if b["compatible_type_id"] == route["type_id"]
            and route["energy_kwh"]
            <= (1 - s["policy"]["min_return_soc"]) * b["capacity_kwh"] * b["soh"] + 1e-8
        ]
        if not choices_d or not choices_b:
            continue
        selected = model.new_bool_var(f"select_{index}")
        start = model.new_int_var(0, horizon, f"start_{index}")
        present_d = {}
        present_b = {}
        charge_starts = {}
        old = hints.get(key)
        model.add_hint(selected, int(old is not None))
        model.add_hint(start, min(horizon, ticks(old["prepare_start_s"])) if old else 0)
        if limits:
            preparation.append(
                model.new_optional_fixed_size_interval_var(
                    start, ticks(route["prepare_s"]), selected, f"prepare_{index}"
                )
            )
        for uid in choices_d:
            presence = model.new_bool_var(f"d_{index}_{uid}")
            present_d[uid] = presence
            windows["drone", uid].append(
                model.new_optional_fixed_size_interval_var(
                    start,
                    ticks(route["duration_s"] + typ["turnaround_duration_s"]),
                    presence,
                    f"drone_{index}_{uid}",
                )
            )
            model.add(start >= ticks(drones[uid]["available_after_s"])).only_enforce_if(
                presence
            )
            model.add_hint(presence, int(old is not None and old["drone_id"] == uid))
        for bid in choices_b:
            presence = model.new_bool_var(f"b_{index}_{bid}")
            present_b[bid] = presence
            b = batteries[bid]
            soc = 1 - route["energy_kwh"] / (b["capacity_kwh"] * b["soh"])
            if limits:
                duration = ticks(charge_seconds(typ, soc))
                charge_begin = model.new_int_var(
                    0, horizon, f"charge_start_{index}_{bid}"
                )
                charge_end = model.new_int_var(
                    0, horizon + duration, f"charge_end_{index}_{bid}"
                )
                occupied = model.new_int_var(
                    0, horizon + duration, f"battery_duration_{index}_{bid}"
                )
                model.add(
                    charge_begin >= start + ticks(route["duration_s"])
                ).only_enforce_if(presence)
                model.add(charge_end == charge_begin + duration).only_enforce_if(
                    presence
                )
                windows["battery", bid].append(
                    model.new_optional_interval_var(
                        start, occupied, charge_end, presence, f"battery_{index}_{bid}"
                    )
                )
                charging.append(
                    model.new_optional_fixed_size_interval_var(
                        charge_begin, duration, presence, f"charging_{index}_{bid}"
                    )
                )
                charge_starts[bid] = charge_begin
                model.add_hint(
                    charge_begin,
                    (
                        min(horizon, ticks(old.get("charge_start_s", old["return_s"])))
                        if old and old["battery_id"] == bid
                        else 0
                    ),
                )
            else:
                windows["battery", bid].append(
                    model.new_optional_fixed_size_interval_var(
                        start,
                        ticks(route["duration_s"] + charge_seconds(typ, soc)),
                        presence,
                        f"battery_{index}_{bid}",
                    )
                )
            model.add(start >= ticks(b["available_after_s"])).only_enforce_if(presence)
            model.add_hint(presence, int(old is not None and old["battery_id"] == bid))
        model.add(sum(present_d.values()) == selected)
        model.add(sum(present_b.values()) == selected)
        end = model.new_int_var(0, horizon, f"end_{index}")
        model.add(end == start + ticks(route["duration_s"])).only_enforce_if(selected)
        model.add(end == 0).only_enforce_if(selected.Not())
        active_ends.append(end)
        for cid in route["cargo_ids"]:
            coverage[cid].append(selected)
        counts = Counter(cargos[cid]["demand_id"] for cid in route["cargo_ids"])
        for did, quantity in counts.items():
            by_demand[did].append(selected * quantity)
        for visit in route["visits"]:
            offset = ticks(visit["delivery_complete_s"])
            groups = Counter(cargos[cid]["demand_id"] for cid in visit["cargo_ids"])
            for did, quantity in groups.items():
                demand = demands[did]
                if demand["hard_deadline_s"] is not None:
                    model.add(
                        start + offset
                        <= math.floor(demand["hard_deadline_s"] * SCALE + 1e-8)
                    ).only_enforce_if(selected)
                if demand["expected_deadline_s"] is not None and demand["priority"]:
                    raw = model.new_int_var(
                        0, horizon + offset, f"late_raw_{index}_{did}"
                    )
                    late = model.new_int_var(0, horizon, f"late_{index}_{did}")
                    model.add_max_equality(
                        raw,
                        [
                            0,
                            start
                            + offset
                            - math.floor(demand["expected_deadline_s"] * SCALE),
                        ],
                    )
                    model.add(late == raw).only_enforce_if(selected)
                    model.add(late == 0).only_enforce_if(selected.Not())
                    late_terms.append(late * demand["priority"] * quantity)
        energy_terms.append(
            selected * math.ceil(route["energy_kwh"] * ENERGY_SCALE - 1e-8)
        )
        records.append((route, selected, start, present_d, present_b, charge_starts))
    for intervals in windows.values():
        model.add_no_overlap(intervals)
    if limits:
        model.add_cumulative(preparation, [1] * len(preparation), limits["prep_slots"])
        model.add_cumulative(charging, [1] * len(charging), limits["charging_ports"])
    for options in coverage.values():
        model.add(sum(options) <= 1)
    for did, demand in demands.items():
        if not by_demand[did]:
            return None, {**stats, "status": "INCOMPLETE_POOL"}
        model.add(sum(by_demand[did]) == demand["required_quantity"])
    makespan = model.new_int_var(0, horizon, "makespan")
    model.add_max_equality(makespan, active_ends)
    energy = sum(energy_terms)
    goal = (
        makespan
        if objective == "time"
        else (
            energy
            if objective == "energy"
            else makespan + (300 * SCALE // ENERGY_SCALE) * energy
        )
    )
    model.minimize(sum(late_terms) * (goal_bound + 1) + goal)
    invalid = model.validate()
    if invalid:
        return None, {**stats, "status": "MODEL_INVALID", "detail": invalid[:400]}
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max(
        0.01, deadline - time.perf_counter() - 0.1
    )
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = int(seed) % 2147483647
    if progress:
        progress(f"深入优化 {len(records)} 条候选路线的机体与电池排程")
    status = solver.solve(model)
    stats.update(
        status=solver.status_name(status),
        runtime_s=time.perf_counter() - started,
        route_count=len(records),
        branches=solver.num_branches,
        best_bound=solver.best_objective_bound,
    )
    if status not in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        return None, stats
    stats["objective_value"] = solver.objective_value
    routes = []
    for route, selected, start, present_d, present_b, charge_starts in records:
        if not solver.boolean_value(selected):
            continue
        uid = next(uid for uid, p in present_d.items() if solver.boolean_value(p))
        bid = next(bid for bid, p in present_b.items() if solver.boolean_value(p))
        typ = types[route["type_id"]]
        b = batteries[bid]
        begin = solver.value(start) / SCALE
        finish = begin + route["duration_s"]
        charge_begin = solver.value(charge_starts[bid]) / SCALE if limits else finish
        soc = 1 - route["energy_kwh"] / (b["capacity_kwh"] * b["soh"])
        visits = [
            {**v, "delivery_complete_s": begin + v["delivery_complete_s"]}
            for v in route["visits"]
        ]
        routes.append(
            {
                "sortie_id": sortie_id(
                    route["cargo_ids"],
                    uid,
                    bid,
                    begin,
                    visits,
                    charge_begin if limits else None,
                ),
                "kind": "transport",
                "drone_id": uid,
                "battery_id": bid,
                "cargo_ids": route["cargo_ids"],
                "visits": visits,
                "route_geometry": copy.deepcopy(route["route_geometry"]),
                "prepare_start_s": begin,
                "takeoff_s": begin + route["prepare_s"],
                "return_s": finish,
                "drone_released_s": finish + typ["turnaround_duration_s"],
                "battery_released_s": charge_begin + charge_seconds(typ, soc),
                "energy_kwh": route["energy_kwh"],
                "return_soc": soc,
                "terrain_status": (
                    "passed"
                    if s["terrain"]["status"] == "available"
                    else "not_evaluated"
                ),
                "communication_status": "not_evaluated",
            }
        )
        if limits:
            routes[-1]["charge_start_s"] = charge_begin
    if limits:
        # In original CP charge-start order, left-shifting cannot extend any release
        # or conflict with a later CP interval; all aircraft starts remain fixed.
        occupied = []
        for route in sorted(
            routes, key=lambda r: (r["charge_start_s"], r["sortie_id"])
        ):
            typ = types[drones[route["drone_id"]]["type_id"]]
            duration = charge_seconds(typ, route["return_soc"])
            begin = earliest_slot(
                route["return_s"], duration, occupied, limits["charging_ports"]
            )
            route.update(charge_start_s=begin, battery_released_s=begin + duration)
            occupied.append((begin, begin + duration))
            route["sortie_id"] = sortie_id(
                route["cargo_ids"],
                route["drone_id"],
                route["battery_id"],
                route["prepare_start_s"],
                route["visits"],
                begin,
            )
    return sorted(routes, key=lambda r: (r["prepare_start_s"], r["drone_id"])), stats
