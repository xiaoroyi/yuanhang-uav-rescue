"""Read-only model altitude and energy diagnostics, bound to a saved Snapshot."""

from dataclasses import replace
import math

import numpy as np
from pydantic import BaseModel, ConfigDict, Field

from shared.contracts import content_hash
from solver.assets import terrain_data
from solver.errors import InputNotReady
from solver.physics import GEOD, leg, leg_values, parameters, terrain_maximum


class View(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class FlightProfileSample(View):
    distance_m: float
    longitude: float
    latitude: float
    ground_elevation_m: float | None
    cruise_elevation_m: float


class FlightProfileLeg(View):
    leg_index: int
    from_id: str
    to_id: str
    distance_m: float
    start_distance_m: float
    end_distance_m: float
    start_work_elevation_m: float
    end_work_elevation_m: float
    cruise_elevation_m: float
    climb_m: float
    descent_m: float
    clearance_required_m: float
    payload_kg: float
    flight_time_s: float
    energy_kwh: float
    horizontal_energy_kwh: float
    climb_energy_kwh: float
    terrain_checked: bool
    terrain_maximum_m: float | None
    cruise_clearance_margin_m: float | None
    samples: list[FlightProfileSample] = Field(min_length=2, max_length=240)


class FlightProfile(View):
    plan_id: str
    snapshot_id: str
    scenario_state_version: int
    sortie_id: str
    drone_id: str
    drone_type_id: str
    terrain_asset_id: str | None
    terrain_sha256: str | None
    vertical_datum: str | None
    total_distance_m: float
    total_climb_m: float
    total_descent_m: float
    flight_time_s: float
    modeled_energy_kwh: float
    horizontal_energy_kwh: float
    climb_energy_kwh: float
    plan_sortie_energy_kwh: float | None
    legs: list[FlightProfileLeg] = Field(min_length=1, max_length=120)
    notice: str


def ground_sample(terrain, coordinates):
    if terrain is None:
        return None
    z, lon, lat, nodata = terrain
    dx, dy = float(lon[1] - lon[0]), float(lat[0] - lat[1])
    c = math.floor((coordinates[0] - float(lon[0])) / dx + 0.5)
    r = math.floor((float(lat[0]) - coordinates[1]) / dy + 0.5)
    if r < 0 or c < 0 or r >= z.shape[0] or c >= z.shape[1]:
        return None
    value = float(z[r, c])
    return value if math.isfinite(value) and value != nodata else None


def path_samples(geometry, count, offset, terrain):
    path = geometry.path
    segments = []
    total = 0.0
    for a, b in zip(path, path[1:]):
        azimuth, _, length = GEOD.inv(*a, *b)
        segments.append((total, total + abs(length), a, b, azimuth))
        total += abs(length)
    result = []
    index = 0
    for distance in np.linspace(0.0, total, count):
        while index < len(segments) - 1 and distance > segments[index][1]:
            index += 1
        start, end, a, b, azimuth = segments[index]
        if distance >= total:
            coordinates = b
        elif end <= start:
            coordinates = a
        else:
            x, y, _ = GEOD.fwd(*a, azimuth, float(distance) - start)
            coordinates = (x, y)
        result.append(
            {
                "distance_m": offset + float(distance),
                "longitude": float(coordinates[0]),
                "latitude": float(coordinates[1]),
                "ground_elevation_m": ground_sample(terrain, coordinates),
                "cruise_elevation_m": geometry.cruise_m,
            }
        )
    return result


def flight_profile(snapshot, plan, sortie_id):
    scenario = snapshot["scenario"]
    if (
        plan["snapshot_id"] != snapshot["snapshot_id"]
        or plan["scenario_id"] != snapshot["scenario_id"]
        or plan["scenario_state_version"] != snapshot["scenario_state_version"]
        or content_hash(scenario) != snapshot["content_hash"]
    ):
        raise InputNotReady("方案与不可变输入快照不匹配。")
    sortie = next((s for s in plan["sorties"] if s["sortie_id"] == sortie_id), None)
    if sortie is None:
        raise KeyError(sortie_id)
    drones = {d["drone_id"]: d for d in scenario["drones"]}
    drone_type_id = drones[sortie["drone_id"]]["type_id"]
    typ = next(t for t in scenario["drone_types"] if t["type_id"] == drone_type_id)
    p = parameters(typ)
    nodes = {n["id"]: n for n in [scenario["base"], *scenario["sites"]]}
    cargos = {c["cargo_id"]: c for c in scenario["cargo_items"]}
    base_id = scenario["base"]["id"]
    stops = [(v["site_id"], v["cargo_ids"]) for v in sortie["visits"]] + [(base_id, [])]
    if len(stops) > 120:
        raise InputNotReady("高度剖面最多显示120个航段。")
    ref = scenario["terrain"]
    terrain = (
        terrain_data(ref["asset_id"], ref["sha256"])
        if ref["status"] == "available"
        else None
    )
    count = max(2, 240 // len(stops))
    remaining = sum(cargos[cid]["mass_kg"] for cid in sortie["cargo_ids"])
    current, offset = base_id, 0.0
    result, route = [], [scenario["base"]["coordinates"]]
    for index, (destination, delivered) in enumerate(stops):
        geometry = leg(scenario, typ, current, destination)
        seconds, energy = leg_values(typ, geometry, remaining)
        _, horizontal = leg_values(typ, replace(geometry, climb_m=0.0), remaining)
        maximum = (
            max(
                terrain_maximum(ref["asset_id"], ref["sha256"], a, b)
                for a, b in zip(geometry.path, geometry.path[1:])
            )
            if geometry.terrain_checked
            else None
        )

        def work(node_id):
            return nodes[node_id]["ground_elevation_m"] + (
                0.0 if node_id == base_id else p.get("service_height_m", 30.0)
            )

        clearance = p.get("clearance_m", 50.0)
        result.append(
            {
                "leg_index": index,
                "from_id": current,
                "to_id": destination,
                "distance_m": geometry.distance_m,
                "start_distance_m": offset,
                "end_distance_m": offset + geometry.distance_m,
                "start_work_elevation_m": work(current),
                "end_work_elevation_m": work(destination),
                "cruise_elevation_m": geometry.cruise_m,
                "climb_m": geometry.climb_m,
                "descent_m": geometry.descend_m,
                "clearance_required_m": clearance,
                "payload_kg": remaining,
                "flight_time_s": seconds,
                "energy_kwh": energy,
                "horizontal_energy_kwh": horizontal,
                "climb_energy_kwh": energy - horizontal,
                "terrain_checked": geometry.terrain_checked,
                "terrain_maximum_m": maximum,
                "cruise_clearance_margin_m": (
                    geometry.cruise_m - maximum - clearance
                    if maximum is not None
                    else None
                ),
                "samples": path_samples(geometry, count, offset, terrain),
            }
        )
        route.extend([list(point) for point in geometry.path[1:]])
        remaining -= sum(cargos[cid]["mass_kg"] for cid in delivered)
        current, offset = destination, offset + geometry.distance_m
    stored = sortie["route_geometry"]["coordinates"]
    if len(route) != len(stored) or any(
        abs(float(x) - float(y)) > 1e-8
        for a, b in zip(route, stored)
        for x, y in zip(a, b)
    ):
        raise InputNotReady(
            "当前物理模型重建路线与历史方案不一致，不能替历史路线生成高度图。"
        )
    return {
        "plan_id": plan["plan_id"],
        "snapshot_id": snapshot["snapshot_id"],
        "scenario_state_version": snapshot["scenario_state_version"],
        "sortie_id": sortie_id,
        "drone_id": sortie["drone_id"],
        "drone_type_id": drone_type_id,
        "terrain_asset_id": ref.get("asset_id") if terrain is not None else None,
        "terrain_sha256": ref.get("sha256") if terrain is not None else None,
        "vertical_datum": ref.get("vertical_datum") if terrain is not None else None,
        "total_distance_m": offset,
        "total_climb_m": sum(row["climb_m"] for row in result),
        "total_descent_m": sum(row["descent_m"] for row in result),
        "flight_time_s": sum(row["flight_time_s"] for row in result),
        "modeled_energy_kwh": sum(row["energy_kwh"] for row in result),
        "horizontal_energy_kwh": sum(row["horizontal_energy_kwh"] for row in result),
        "climb_energy_kwh": sum(row["climb_energy_kwh"] for row in result),
        "plan_sortie_energy_kwh": sortie["energy_kwh"],
        "legs": result,
        "notice": "按原Snapshot和现有leg/leg_values物理模型重建；高程按资产声明的垂直基准。巡航高程是模型水平航段高度，起终作业点另列；不是遥测或可执行飞控轨迹。沿线最多240个DEM显示采样保留未知，不能代替逐像元净空检查。净空余量只指水平巡航包络，不认证起降走廊；下降不计能量回收，飞行时间不含准备与交接。",
    }
