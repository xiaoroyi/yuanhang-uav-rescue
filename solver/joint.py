"""Finite fixed-grouping transport/relay joint scheduling, with explicit resources.

Geometry atoms are continuous in the declared model. CP uses conservative 10ms
envelopes and full-charge upper bounds for relay components. Every result must
pass the independent physics and coverage reconstruction before publication.
"""

import copy
import hashlib
import math
import time
from collections import defaultdict

from ortools.sat.python import cp_model as cp

from solver.errors import InputNotReady
from solver.identities import sortie_id
from solver.physics import charge_seconds
from solver.radio import Radio
from solver.relay import build_atoms, coverage_report, relay_sortie, station_physics

SCALE = 100


def ceil_tick(value):
    return math.ceil(value * SCALE - 1e-8)


def floor_tick(value):
    return math.floor(value * SCALE + 1e-8)


def schedule(s, transport, options, deadline, progress=None):
    def report(message):
        if progress:
            progress(message)

    config = s["communication"]
    rm = config["relay_model"]
    if any(
        b["status"] == "charging"
        or (b["status"] == "available" and b["soc"] < 1 - 1e-9)
        for b in s["batteries"]
    ):
        raise InputNotReady(
            "当前联合调度只支持初始满SOC运输电池；低SOC运输能力仍可在关闭通信时单独求解。"
        )
    radio = Radio(s, deadline)
    report("检查中继候选飞行净空与双向回传")
    stations = []
    for candidate in config["candidate_stations"]:
        radio.check_time()
        try:
            station = station_physics(s, candidate, radio)
        except (InputNotReady, ValueError):
            continue
        if station:
            stations.append(station)
    report("构造连续直连缺口与中继覆盖区间")
    atoms = build_atoms(s, transport["sorties"], stations, radio)
    if not any(atoms):
        routes = copy.deepcopy(transport["sorties"])
        for route in routes:
            route["communication_status"] = "passed"
        return (
            routes,
            [],
            coverage_report(s, {"sorties": routes, "relay_sorties": []}, radio),
            {"status": "DIRECT_ONLY", "stations": len(stations), "atoms": 0},
        )
    relay_drones = [
        d
        for d in config["relay_drones"]
        if d["status"] == "available" and d["location_id"] == s["base"]["id"]
    ]
    components = [
        b
        for b in config["relay_energy"]
        if b["status"] == "available"
        and b["location_id"] == s["base"]["id"]
        and b["soh"] > 0
        and b["soc"] >= 1 - 1e-9
    ]
    if not relay_drones or not components:
        raise InputNotReady("存在运输直连缺口，但没有可用的满SOC中继实体与能源组件。")
    if time.perf_counter() >= deadline - 0.2:
        raise TimeoutError("连续覆盖候选计算用完预算。")
    model = cp.CpModel()
    horizon = ceil_tick(
        max(36000, max(r["battery_released_s"] for r in transport["sorties"]) * 2)
    )
    drones = {
        d["drone_id"]: d
        for d in s["drones"]
        if d["status"] == "available" and d["location_id"] == s["base"]["id"]
    }
    batteries = {
        b["battery_id"]: b
        for b in s["batteries"]
        if b["status"] == "available"
        and b["soh"] > 0
        and b["location_id"] == s["base"]["id"]
        and b["soc"] >= 1 - 1e-9
    }
    types = {t["type_id"]: t for t in s["drone_types"]}
    cargos = {b["cargo_id"]: b for b in s["cargo_items"]}
    demands = {d["demand_id"]: d for d in s["demands"]}
    u_windows, b_windows = defaultdict(list), defaultdict(list)
    prep_windows, charge_windows = [], []
    starts, finishes, assignments, lateness = [], [], [], []
    for i, route in enumerate(transport["sorties"]):
        typ = types[
            next(
                d["type_id"] for d in s["drones"] if d["drone_id"] == route["drone_id"]
            )
        ]
        start = model.new_int_var(0, horizon, f"ts{i}")
        duration = route["return_s"] - route["prepare_start_s"]
        end = model.new_int_var(0, horizon, f"te{i}")
        model.add(end == start + ceil_tick(duration))
        prep_duration = ceil_tick(route["takeoff_s"] - route["prepare_start_s"])
        prep_windows.append(
            model.new_fixed_size_interval_var(start, prep_duration, f"tp{i}")
        )
        us, bs = [], []
        for uid, u in drones.items():
            if u["type_id"] != typ["type_id"]:
                continue
            chosen = model.new_bool_var(f"tu{i}_{uid}")
            model.add(start >= ceil_tick(u["available_after_s"])).only_enforce_if(
                chosen
            )
            u_windows[uid].append(
                model.new_optional_fixed_size_interval_var(
                    start,
                    ceil_tick(duration + typ["turnaround_duration_s"]),
                    chosen,
                    f"tui{i}_{uid}",
                )
            )
            us.append((uid, chosen))
        for bid, b in batteries.items():
            usable = b["capacity_kwh"] * b["soh"]
            if (
                b["compatible_type_id"] != typ["type_id"]
                or route["energy_kwh"]
                > (1 - s["policy"]["min_return_soc"]) * usable + 1e-9
            ):
                continue
            chosen = model.new_bool_var(f"tb{i}_{bid}")
            charging = model.new_int_var(0, horizon, f"tbc{i}_{bid}")
            release = model.new_int_var(0, horizon, f"tbr{i}_{bid}")
            charge_duration = ceil_tick(
                charge_seconds(typ, 1 - route["energy_kwh"] / usable)
            )
            model.add(charging >= end).only_enforce_if(chosen)
            model.add(release == charging + charge_duration).only_enforce_if(chosen)
            model.add(start >= ceil_tick(b["available_after_s"])).only_enforce_if(
                chosen
            )
            size = model.new_int_var(0, horizon, f"tbz{i}_{bid}")
            model.add(size == release - start).only_enforce_if(chosen)
            b_windows[bid].append(
                model.new_optional_interval_var(
                    start, size, release, chosen, f"tbi{i}_{bid}"
                )
            )
            charge_windows.append(
                model.new_optional_fixed_size_interval_var(
                    charging, charge_duration, chosen, f"tci{i}_{bid}"
                )
            )
            bs.append((bid, chosen, charging))
        if not us or not bs:
            raise InputNotReady(
                "当前联合分解中的运输组批没有可用实体；需改变组批或补充资源。"
            )
        model.add_exactly_one([v for _, v in us])
        model.add_exactly_one([v for _, v, _ in bs])
        for visit in route["visits"]:
            delivery = start + ceil_tick(
                visit["delivery_complete_s"] - route["prepare_start_s"]
            )
            for cid in visit["cargo_ids"]:
                demand = demands[cargos[cid]["demand_id"]]
                if demand["hard_deadline_s"] is not None:
                    model.add(delivery <= floor_tick(demand["hard_deadline_s"]))
                if demand["expected_deadline_s"] is not None:
                    late = model.new_int_var(0, horizon, f"late{i}_{cid}")
                    model.add_max_equality(
                        late, [0, delivery - floor_tick(demand["expected_deadline_s"])]
                    )
                    lateness.append(demand["priority"] * late)
        starts.append(start)
        finishes.append(end)
        assignments.append((us, bs))
        model.add_hint(start, ceil_tick(route["prepare_start_s"]))
    for intervals in [*u_windows.values(), *b_windows.values()]:
        model.add_no_overlap(intervals)
    slots = min(12, max(4, len(transport["sorties"])))
    relay_vars, relay_u, relay_b = [], defaultdict(list), defaultdict(list)
    ready_offsets = [0, *[ceil_tick(st["ready_offset_s"]) for st in stations]]
    arrival_offsets = [0, *[floor_tick(st["arrival_offset_s"]) for st in stations]]
    backs = [0, *[ceil_tick(st["back_s"]) for st in stations]]
    fly_energy = [0, *[math.ceil(st["fly_energy_kwh"] * 1e9) for st in stations]]
    hover_coefficient = math.ceil(
        (rm["hover_power_kw"] + rm["radio_power_kw"]) * 1e9 / (3600 * SCALE)
    )
    relay_energy_units = []
    for j in range(slots):
        used = model.new_bool_var(f"ry{j}")
        loc = model.new_int_var(0, len(stations), f"rl{j}")
        begin = model.new_int_var(0, horizon, f"rs{j}")
        ready = model.new_int_var(0, horizon, f"rb{j}")
        finish = model.new_int_var(0, horizon, f"rf{j}")
        returned = model.new_int_var(0, horizon, f"rr{j}")
        charging = model.new_int_var(0, horizon, f"rc{j}")
        component_end = model.new_int_var(0, horizon, f"rce{j}")
        model.add(loc >= 1).only_enforce_if(used)
        model.add(loc == 0).only_enforce_if(used.Not())
        for value in [begin, ready, finish, returned, charging, component_end]:
            model.add(value == 0).only_enforce_if(used.Not())
        off_ready = model.new_int_var(0, max(ready_offsets), f"rd{j}")
        off_arrival = model.new_int_var(0, max(arrival_offsets), f"ra{j}")
        off_back = model.new_int_var(0, max(backs), f"rk{j}")
        off_fly = model.new_int_var(0, max(fly_energy), f"re{j}")
        for table, variable in [
            (ready_offsets, off_ready),
            (arrival_offsets, off_arrival),
            (backs, off_back),
            (fly_energy, off_fly),
        ]:
            model.add_element(loc, table, variable)
        model.add(ready == begin + off_ready)
        model.add(finish >= ready)
        model.add(returned == finish + off_back)
        model.add(charging >= returned)
        model.add(component_end == charging + ceil_tick(rm["full_charge_s"]) * used)
        nano = model.new_int_var(
            0,
            math.floor(max(b["capacity_kwh"] * b["soh"] for b in components) * 1e9),
            f"ren{j}",
        )
        model.add(nano == off_fly + hover_coefficient * (finish - begin - off_arrival))
        energy_unit = model.new_int_var(0, 10000000, f"rem{j}")
        model.add_division_equality(energy_unit, nano + 999999, 1000000)
        relay_energy_units.append(energy_unit)
        us, bs = [], []
        for u in relay_drones:
            chosen = model.new_bool_var(f"ru{j}_{u['drone_id']}")
            model.add(begin >= ceil_tick(u["available_after_s"])).only_enforce_if(
                chosen
            )
            end_u = model.new_int_var(0, horizon, f"rue{j}_{u['drone_id']}")
            size = model.new_int_var(0, horizon, f"ruz{j}_{u['drone_id']}")
            model.add(
                end_u == returned + ceil_tick(rm["turnaround_duration_s"])
            ).only_enforce_if(chosen)
            model.add(size == end_u - begin).only_enforce_if(chosen)
            relay_u[u["drone_id"]].append(
                model.new_optional_interval_var(
                    begin, size, end_u, chosen, f"rui{j}_{u['drone_id']}"
                )
            )
            us.append((u["drone_id"], chosen))
        for b in components:
            chosen = model.new_bool_var(f"rk{j}_{b['component_id']}")
            model.add(begin >= ceil_tick(b["available_after_s"])).only_enforce_if(
                chosen
            )
            model.add(
                nano
                <= math.floor(
                    (1 - rm["min_return_soc"]) * b["capacity_kwh"] * b["soh"] * 1e9
                )
            ).only_enforce_if(chosen)
            size = model.new_int_var(0, horizon, f"rkz{j}_{b['component_id']}")
            model.add(size == component_end - begin).only_enforce_if(chosen)
            relay_b[b["component_id"]].append(
                model.new_optional_interval_var(
                    begin, size, component_end, chosen, f"rki{j}_{b['component_id']}"
                )
            )
            bs.append((b, chosen))
        model.add(sum(v for _, v in us) == used)
        model.add(sum(v for _, v in bs) == used)
        prep_windows.append(
            model.new_optional_fixed_size_interval_var(
                begin, ceil_tick(rm["prepare_duration_s"]), used, f"rp{j}"
            )
        )
        charge_windows.append(
            model.new_optional_fixed_size_interval_var(
                charging, ceil_tick(rm["full_charge_s"]), used, f"rch{j}"
            )
        )
        if j:
            model.add(used <= relay_vars[-1]["used"])
            model.add(begin >= relay_vars[-1]["begin"]).only_enforce_if(used)
        relay_vars.append(
            {
                "used": used,
                "loc": loc,
                "begin": begin,
                "ready": ready,
                "finish": finish,
                "returned": returned,
                "charging": charging,
                "us": us,
                "bs": bs,
            }
        )
    for intervals in [*relay_u.values(), *relay_b.values()]:
        model.add_no_overlap(intervals)
    used_by_slot = [[] for _ in relay_vars]
    for i, route_atoms in enumerate(atoms):
        for k, atom in enumerate(route_atoms):
            selections = []
            for j, relay in enumerate(relay_vars):
                chosen = model.new_bool_var(f"cover{i}_{k}_{j}")
                model.add(chosen <= relay["used"])
                model.add_allowed_assignments(
                    [relay["loc"]], [[index + 1] for index in atom["stations"]]
                ).only_enforce_if(chosen)
                model.add(
                    relay["ready"] <= starts[i] + floor_tick(atom["start_s"])
                ).only_enforce_if(chosen)
                model.add(
                    relay["finish"] >= starts[i] + ceil_tick(atom["end_s"])
                ).only_enforce_if(chosen)
                selections.append(chosen)
                used_by_slot[j].append(chosen)
            model.add_exactly_one(selections)
    for j, relay in enumerate(relay_vars):
        model.add(sum(used_by_slot[j]) >= relay["used"])
    limits = s.get("resource_limits")
    if limits:
        model.add_cumulative(
            prep_windows, [1] * len(prep_windows), limits["prep_slots"]
        )
        model.add_cumulative(
            charge_windows, [1] * len(charge_windows), limits["charging_ports"]
        )
    joint_end = model.new_int_var(0, horizon, "joint_end")
    model.add_max_equality(joint_end, [*finishes, *[v["returned"] for v in relay_vars]])
    primary = sum(lateness)
    energy = sum(relay_energy_units)
    goal = (
        energy
        if options["objective"] == "energy"
        else (
            joint_end + 30 * energy if options["objective"] == "balanced" else joint_end
        )
    )
    error = model.validate()
    if error:
        raise ValueError(error)
    evidence = []
    chosen_solver = None
    for stage, expression in [("priority_delay", primary), ("joint_objective", goal)]:
        remaining = deadline - time.perf_counter()
        if remaining <= 0.1:
            break
        report(
            "联合排程：优先级延期"
            if stage == "priority_delay"
            else "联合排程：运输与中继总目标"
        )
        model.minimize(expression)
        solver = cp.CpSolver()
        solver.parameters.max_time_in_seconds = (
            remaining * 0.52 if stage == "priority_delay" else remaining * 0.95
        )
        solver.parameters.num_search_workers = 1
        solver.parameters.random_seed = options["seed"]

        class StopAtZero(cp.CpSolverSolutionCallback):
            def on_solution_callback(self):
                if stage == "priority_delay" and self.objective_value == 0:
                    self.stop_search()

        status = solver.solve(model, StopAtZero())
        evidence.append(
            {
                "stage": stage,
                "status": solver.status_name(status),
                "seconds": solver.wall_time,
                "objective": (
                    solver.objective_value
                    if status in (cp.FEASIBLE, cp.OPTIMAL)
                    else None
                ),
            }
        )
        if status not in (cp.FEASIBLE, cp.OPTIMAL):
            if (
                status == cp.UNKNOWN
                and chosen_solver is None
                and deadline - time.perf_counter() > 0.2
            ):
                report("联合排程：在剩余预算中搜索可行方案")
                model.clear_objective()
                recovery = cp.CpSolver()
                recovery.parameters.max_time_in_seconds = (
                    deadline - time.perf_counter()
                ) * 0.95
                recovery.parameters.num_search_workers = 1
                recovery.parameters.random_seed = options["seed"] + 101
                recovery.parameters.stop_after_first_solution = True
                recovered = recovery.solve(model)
                evidence.append(
                    {
                        "stage": "feasibility_recovery",
                        "status": recovery.status_name(recovered),
                        "seconds": recovery.wall_time,
                        "objective": None,
                    }
                )
                if recovered in (cp.FEASIBLE, cp.OPTIMAL):
                    chosen_solver = recovery
            break
        chosen_solver = solver
        model.add(expression <= solver.value(expression))
        model.clear_hints()
        for index in range(len(model.proto.variables)):
            variable = model.get_int_var_from_proto_index(index)
            model.add_hint(variable, solver.value(variable))
    if chosen_solver is None:
        return (
            None,
            None,
            None,
            {
                "status": evidence[-1]["status"] if evidence else "BUDGET",
                "stations": len(stations),
                "atoms": sum(map(len, atoms)),
                "relay_slots": slots,
                "stages": evidence,
            },
        )
    solved = chosen_solver
    routes = []
    for i, original in enumerate(transport["sorties"]):
        route = copy.deepcopy(original)
        start = solved.value(starts[i]) / SCALE
        shift = start - original["prepare_start_s"]
        for key in ["prepare_start_s", "takeoff_s", "return_s", "drone_released_s"]:
            route[key] += shift
        for visit in route["visits"]:
            visit["delivery_complete_s"] += shift
        us, bs = assignments[i]
        route["drone_id"] = next(uid for uid, chosen in us if solved.value(chosen))
        bid, _, charge = next(row for row in bs if solved.value(row[1]))
        route["battery_id"] = bid
        b = batteries[bid]
        typ = types[drones[route["drone_id"]]["type_id"]]
        route["return_soc"] = 1 - route["energy_kwh"] / (b["capacity_kwh"] * b["soh"])
        charge_start = solved.value(charge) / SCALE if limits else route["return_s"]
        route["battery_released_s"] = charge_start + charge_seconds(
            typ, route["return_soc"]
        )
        if limits or charge_start > route["return_s"] + 1e-7:
            route["charge_start_s"] = charge_start
        route["communication_status"] = "passed"
        route["sortie_id"] = sortie_id(
            route["cargo_ids"],
            route["drone_id"],
            bid,
            start,
            route["visits"],
            charge_start if limits else None,
        )
        routes.append(route)
    relays = []
    for index, v in enumerate(relay_vars):
        if not solved.value(v["used"]):
            continue
        station = stations[solved.value(v["loc"]) - 1]
        uid = next(uid for uid, chosen in v["us"] if solved.value(chosen))
        component = next(b for b, chosen in v["bs"] if solved.value(chosen))
        start, finish, charge_start = [
            solved.value(v[key]) / SCALE for key in ["begin", "finish", "charging"]
        ]
        identity = (
            "RLY-"
            + hashlib.sha256(
                f"{uid}|{component['component_id']}|{station['station_id']}|{start:.6f}|{finish:.6f}".encode()
            ).hexdigest()[:12]
        )
        if not limits:
            charge_start = finish + station["back_s"]
        relays.append(
            relay_sortie(
                s, station, uid, component, start, finish, charge_start, identity
            )
        )
    # Independent validation below gets a fresh geometry engine; this preliminary
    # reconstruction only provides a candidate report, never a publication flag.
    radio.deadline = math.inf
    report("重建联合方案的完整连续覆盖")
    communication = coverage_report(
        s, {"sorties": routes, "relay_sorties": relays}, radio
    )
    return (
        routes,
        relays,
        communication,
        {
            "status": "FEASIBLE",
            "stations": len(stations),
            "atoms": sum(map(len, atoms)),
            "relay_slots": slots,
            "stages": evidence,
        },
    )
