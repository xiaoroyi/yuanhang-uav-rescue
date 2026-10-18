"""Relay flight physics, continuous coverage atoms and independent reconstruction."""

import copy
import math

from solver.errors import InputNotReady
from solver.physics import GEOD, charge_seconds, terrain_maximum
from solver.radio import (
    Radio,
    RADIO_MODEL,
    all_pass,
    bad_intervals,
    merge,
    transport_phases,
)
from solver.routing import route_path


def relay_charge(model, soc):
    return charge_seconds(
        {"charge_model": {"parameters": {"full_charge_s": model["full_charge_s"]}}}, soc
    )


def station_physics(s, station, radio):
    model = s["communication"]["relay_model"]
    if not (0 < station["agl_m"] <= model["max_agl_m"]):
        raise InputNotReady("中继悬停离地高度超过模型上限。")
    terrain = s["terrain"]
    point = tuple(station["coordinates"])
    ground = terrain_maximum(terrain["asset_id"], terrain["sha256"], point, point)
    altitude = ground + station["agl_m"]
    xyz = radio.xyz(point, altitude)
    if bad_intervals(radio.profile(radio.gateway, xyz, xyz, "backhaul"), 0, 1):
        return None
    base = s["base"]
    path = route_path(s, base["coordinates"], station["coordinates"])
    maximum = max(
        terrain_maximum(terrain["asset_id"], terrain["sha256"], a, b)
        for a, b in zip(path, path[1:])
    )
    cruise = max(maximum + 50, base["ground_elevation_m"], altitude)
    distance = sum(abs(GEOD.inv(*a, *b)[2]) for a, b in zip(path, path[1:]))
    out_up, out_down = cruise - base["ground_elevation_m"], cruise - altitude
    outbound = (
        out_up / model["climb_speed_mps"]
        + distance / model["cruise_speed_mps"]
        + out_down / model["descent_speed_mps"]
    )
    inbound = (
        out_down / model["climb_speed_mps"]
        + distance / model["cruise_speed_mps"]
        + out_up / model["descent_speed_mps"]
    )
    energy = model["cruise_power_kw"] * 2 * distance / model[
        "cruise_speed_mps"
    ] / 3600 + model["mass_kg"] * 9.81 * (out_up + out_down) / (
        model["climb_efficiency"] * 3600000
    )
    return {
        **station,
        "xyz": xyz,
        "ground_m": ground,
        "altitude_m": altitude,
        "out_s": outbound,
        "back_s": inbound,
        "fly_energy_kwh": energy,
        "prepare_s": model["prepare_duration_s"],
        "ready_offset_s": model["prepare_duration_s"]
        + outbound
        + model["link_duration_s"],
        "arrival_offset_s": model["prepare_duration_s"] + outbound,
        "route_geometry": {
            "type": "LineString",
            "coordinates": [list(p) for p in [*path, *list(reversed(path))[1:]]],
        },
    }


def build_atoms(s, routes, stations, radio):
    """Finite continuous closed coverage atoms, relative to each route preparation."""
    by_route = []
    for route in routes:
        relative = copy.deepcopy(route)
        shift = route["prepare_start_s"]
        for key in [
            "prepare_start_s",
            "takeoff_s",
            "return_s",
            "drone_released_s",
            "battery_released_s",
            "charge_start_s",
        ]:
            if key in relative:
                relative[key] -= shift
        for visit in relative["visits"]:
            visit["delivery_complete_s"] -= shift
        atoms = []
        for phase in transport_phases(s, relative, radio):
            radio.check_time()
            direct = radio.profile(radio.gateway, phase["p0"], phase["p1"], "direct")
            gaps = bad_intervals(direct, 0, 1, padding=1e-7)
            if not gaps:
                continue
            access = [
                radio.profile(station["xyz"], phase["p0"], phase["p1"], "access")
                for station in stations
            ]
            for lo, hi in gaps:
                cuts = {lo, hi}
                for profile in access:
                    cuts.update(
                        value
                        for a, b, _ in profile["pieces"]
                        for value in [a, b]
                        if lo < value < hi
                    )
                    cuts.update(value for value in profile["events"] if lo < value < hi)
                cuts = sorted(cuts)
                for a, b in zip(cuts, cuts[1:]):
                    allowed = [
                        i for i, profile in enumerate(access) if all_pass(profile, a, b)
                    ]
                    begin = phase["start_s"] + a * (phase["end_s"] - phase["start_s"])
                    end = phase["start_s"] + b * (phase["end_s"] - phase["start_s"])
                    if not allowed:
                        raise InputNotReady(
                            "有限悬停候选无法覆盖一段运输断链区间；需增补悬停点或改变运输路线。"
                        )
                    # Split long continuous windows so successive relays can hand over.
                    count = max(1, math.ceil((end - begin) / 60))
                    for j in range(count):
                        atoms.append(
                            {
                                "start_s": begin + (end - begin) * j / count,
                                "end_s": begin + (end - begin) * (j + 1) / count,
                                "stations": allowed,
                            }
                        )
        compact = []
        for atom in atoms:
            if (
                compact
                and compact[-1]["stations"] == atom["stations"]
                and abs(compact[-1]["end_s"] - atom["start_s"]) <= 1e-8
                and atom["end_s"] - compact[-1]["start_s"] <= 60
            ):
                compact[-1]["end_s"] = atom["end_s"]
            else:
                compact.append(atom)
        by_route.append(compact)
    return by_route


def relay_sortie(
    s, station, drone_id, component, start, service_end, charge_start, identity
):
    model = s["communication"]["relay_model"]
    arrival = start + station["arrival_offset_s"]
    energy = (
        station["fly_energy_kwh"]
        + (model["hover_power_kw"] + model["radio_power_kw"])
        * (service_end - arrival)
        / 3600
    )
    soc = 1 - energy / (component["capacity_kwh"] * component["soh"])
    returned = service_end + station["back_s"]
    return {
        "relay_sortie_id": identity,
        "drone_id": drone_id,
        "component_id": component["component_id"],
        "station_id": station["station_id"],
        "station_coordinates": list(station["coordinates"]),
        "station_agl_m": station["agl_m"],
        "station_elevation_m": station["altitude_m"],
        "prepare_start_s": start,
        "takeoff_s": start + model["prepare_duration_s"],
        "arrival_s": arrival,
        "service_start_s": start + station["ready_offset_s"],
        "service_end_s": service_end,
        "return_s": returned,
        "drone_released_s": returned + model["turnaround_duration_s"],
        "charge_start_s": charge_start,
        "component_released_s": charge_start + relay_charge(model, soc),
        "energy_kwh": energy,
        "return_soc": soc,
        "route_geometry": station["route_geometry"],
    }


def coverage_report(s, plan, radio=None):
    """Recompute every phase; schedule windows/flags in plan are never trusted."""
    radio = radio or Radio(s)
    relays = []
    for sortie in plan.get("relay_sorties", []):
        station = radio.xyz(
            sortie["station_coordinates"], sortie["station_elevation_m"]
        )
        if bad_intervals(
            radio.profile(radio.gateway, station, station, "backhaul"), 0, 1
        ):
            raise InputNotReady("中继服务的固定网关回传不可用。")
        relays.append((sortie, station))
    windows = []
    active = direct_seconds = relay_seconds = gap_seconds = 0.0
    for route in plan["sorties"]:
        for phase in transport_phases(s, route, radio):
            start, end = phase["start_s"], phase["end_s"]
            active += end - start
            direct = radio.profile(radio.gateway, phase["p0"], phase["p1"], "direct")
            direct_bad = bad_intervals(direct, start, end)
            access_bad = [
                (
                    sortie,
                    bad_intervals(
                        radio.profile(station, phase["p0"], phase["p1"], "access"),
                        start,
                        end,
                    ),
                )
                for sortie, station in relays
                if sortie["service_start_s"] <= end and sortie["service_end_s"] >= start
            ]
            cuts = {start, end, *[value for pair in direct_bad for value in pair]}
            for sortie, bad in access_bad:
                cuts.update(value for pair in bad for value in pair)
                cuts.update(
                    value
                    for value in [sortie["service_start_s"], sortie["service_end_s"]]
                    if start < value < end
                )
            cuts = sorted(cuts)
            for lo, hi in zip(cuts, cuts[1:]):
                if hi <= lo:
                    continue
                mid = (lo + hi) / 2
                source, identity = None, None
                if not any(a <= mid <= b for a, b in direct_bad):
                    source = "gateway"
                    direct_seconds += hi - lo
                else:
                    for sortie, bad in access_bad:
                        if (
                            sortie["service_start_s"] <= lo
                            and sortie["service_end_s"] >= hi
                            and not any(a <= mid <= b for a, b in bad)
                        ):
                            source, identity = "relay", sortie["relay_sortie_id"]
                            relay_seconds += hi - lo
                            break
                if source is None:
                    gap_seconds += hi - lo
                    continue
                row = {
                    "sortie_id": route["sortie_id"],
                    "start_s": lo,
                    "end_s": hi,
                    "source": source,
                    "relay_sortie_id": identity,
                }
                if (
                    windows
                    and all(
                        windows[-1][key] == row[key]
                        for key in ["sortie_id", "source", "relay_sortie_id"]
                    )
                    and abs(windows[-1]["end_s"] - lo) <= 1e-8
                ):
                    windows[-1]["end_s"] = hi
                else:
                    windows.append(row)
    return {
        "model_id": RADIO_MODEL,
        "transport_active_s": active,
        "direct_s": direct_seconds,
        "relay_s": relay_seconds,
        "coverage_gap_s": gap_seconds,
        "windows": windows,
    }


def validate_joint(s, plan):
    """Rebuild relay physical/resource constraints and the continuous link report."""
    issues = []
    config = s.get("communication")
    if not config:
        return [("communication", "缺少连续通信模型与资源配置", None)], None
    radio = Radio(s)
    model = config["relay_model"]
    stations = {row["station_id"]: row for row in config["candidate_stations"]}
    drones = {row["drone_id"]: row for row in config["relay_drones"]}
    components = {row["component_id"]: row for row in config["relay_energy"]}
    occupied = {}

    def fail(message, identity=None):
        issues.append(("communication", message, identity))

    def equal(actual, expected, label, identity):
        if not math.isclose(actual, expected, rel_tol=1e-8, abs_tol=1e-5):
            fail(f"中继{label}与独立物理重算不一致", identity)

    for row in plan.get("relay_sorties", []):
        identity = row["relay_sortie_id"]
        u, b, candidate = (
            drones.get(row["drone_id"]),
            components.get(row["component_id"]),
            stations.get(row["station_id"]),
        )
        if u is None or b is None or candidate is None:
            fail("中继架次引用不存在的机体、能源组件或候选位置", identity)
            continue
        if (
            row["station_coordinates"] != candidate["coordinates"]
            or row["station_agl_m"] != candidate["agl_m"]
        ):
            fail("中继架次修改了快照中的悬停候选", identity)
            continue
        if (
            u["status"] != "available"
            or b["status"] != "available"
            or b["soc"] < 1 - 1e-9
            or b["soh"] <= 0
            or u["location_id"] != s["base"]["id"]
            or b["location_id"] != s["base"]["id"]
        ):
            fail("当前联合模型要求基地可用机体及满SOC能源组件", identity)
        if b["soh"] <= 0:
            continue
        station = station_physics(s, candidate, radio)
        if station is None:
            fail("中继悬停点固定网关回传不可用", identity)
            continue
        start = row["prepare_start_s"]
        if start < max(u["available_after_s"], b["available_after_s"]):
            fail("中继资源在可用时间之前占用", identity)
        equal(row["station_elevation_m"], station["altitude_m"], "悬停海拔", identity)
        equal(
            row["takeoff_s"], start + model["prepare_duration_s"], "起飞时刻", identity
        )
        equal(
            row["arrival_s"], start + station["arrival_offset_s"], "到达时刻", identity
        )
        equal(
            row["service_start_s"],
            row["arrival_s"] + model["link_duration_s"],
            "建链时刻",
            identity,
        )
        if row["service_end_s"] < row["service_start_s"]:
            fail("中继服务在完成建链之前结束", identity)
        returned = row["service_end_s"] + station["back_s"]
        equal(row["return_s"], returned, "返航时刻", identity)
        equal(
            row["drone_released_s"],
            returned + model["turnaround_duration_s"],
            "机体释放",
            identity,
        )
        energy = (
            station["fly_energy_kwh"]
            + (model["hover_power_kw"] + model["radio_power_kw"])
            * (row["service_end_s"] - row["arrival_s"])
            / 3600
        )
        soc = 1 - energy / (b["capacity_kwh"] * b["soh"])
        equal(row["energy_kwh"], energy, "能耗", identity)
        equal(row["return_soc"], soc, "返航SOC", identity)
        if energy < 0 or soc < model["min_return_soc"] - 1e-8:
            fail("中继能源不足以满足返航安全余量", identity)
        if row["charge_start_s"] < returned - 1e-7:
            fail("中继能源组件在返航之前开始充电", identity)
        if not s.get("resource_limits") and not math.isclose(
            row["charge_start_s"], returned, abs_tol=1e-7
        ):
            fail("无限容量模型不应安排中继充电排队", identity)
        equal(
            row["component_released_s"],
            row["charge_start_s"] + relay_charge(model, soc),
            "能源组件充电释放",
            identity,
        )
        if row["route_geometry"] != station["route_geometry"]:
            fail("中继路线与地形/限制区路径不一致", identity)
        for kind, key, end in [
            ("relay_drone", u["drone_id"], row["drone_released_s"]),
            ("relay_energy", b["component_id"], row["component_released_s"]),
        ]:
            occupied.setdefault((kind, key), []).append((start, end))
    for resource, intervals in occupied.items():
        ordered = sorted(intervals)
        if any(a[1] > b[0] + 1e-7 for a, b in zip(ordered, ordered[1:])):
            fail("中继机体或能源组件发生占用重叠", resource[1])
    if not all(
        key in plan
        for key in ["relay_sorties", "joint_metrics", "communication_report"]
    ):
        fail("联合方案缺少中继任务、联合指标或连续覆盖报告")
    if issues:
        return issues, None
    report = coverage_report(s, plan, radio)
    if report["coverage_gap_s"] > 1e-7:
        fail(f"连续通信仍存在{report['coverage_gap_s']:.8f}秒缺口")
    provided = plan["communication_report"]
    for key in ["transport_active_s", "direct_s", "relay_s", "coverage_gap_s"]:
        equal(provided[key], report[key], "通信统计" + key, plan["plan_id"])
    if len(provided["windows"]) != len(report["windows"]):
        fail("通信窗口数量与独立重算不一致")
    else:
        for actual, expected in zip(provided["windows"], report["windows"]):
            for key in ["sortie_id", "source", "relay_sortie_id"]:
                if actual[key] != expected[key]:
                    fail("通信窗口归属与独立重算不一致", actual["sortie_id"])
                    break
            equal(
                actual["start_s"],
                expected["start_s"],
                "通信窗口开始",
                actual["sortie_id"],
            )
            equal(
                actual["end_s"], expected["end_s"], "通信窗口结束", actual["sortie_id"]
            )
    return issues, report
