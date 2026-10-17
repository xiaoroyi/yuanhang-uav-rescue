"""Stateless transport/charging physics adapted from the archived contest model.

Source: references/modeling/submitted-code/问题1/src/flight_physics.py and
问题2/src/routes.py. No legacy imports, output files or environment mutation.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import hashlib
import math
from pathlib import Path

import numpy as np
from pyproj import Geod
from solver.routing import route_path, RoutingUnavailable

ROOT = Path(__file__).resolve().parents[1]
GEOD = Geod(ellps="WGS84")
ENERGY_MODEL = "contest_transport_v1"
CHARGE_MODEL = "contest_two_stage_v1"


class InputNotReady(ValueError):
    pass


@dataclass(frozen=True)
class Leg:
    distance_m: float
    climb_m: float
    descend_m: float
    cruise_m: float
    terrain_checked: bool
    path: tuple


@lru_cache(maxsize=2)
def terrain_data(asset_id: str, expected_hash: str):
    if asset_id != "contest-dem-30m":
        raise InputNotReady("尚未注册该地形资产，请使用已核验的题设DEM或关闭强制地形。")
    from scipy.io import loadmat

    path = next((ROOT / "references/modeling/data/terrain").glob("*DEM.mat"))
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash:
        raise InputNotReady("地形资产内容哈希与快照不一致。")
    values = loadmat(path)
    return (
        values["dem"],
        values["longitude"].ravel(),
        values["latitude"].ravel(),
        float(values["nodata"].item()),
    )


def supercover_cells(x0, y0, x1, y1):
    """All closed raster cells touched by one segment, including corner contacts."""
    cuts = [0.0, 1.0]
    for a, b in [(x0, x1), (y0, y1)]:
        if abs(b - a) > 1e-14:
            cuts.extend(
                (k - a) / (b - a)
                for k in range(math.ceil(min(a, b)), math.floor(max(a, b)) + 1)
                if 0 <= (k - a) / (b - a) <= 1
            )
    cuts = sorted(set(cuts))
    probes = cuts + [(a + b) / 2 for a, b in zip(cuts, cuts[1:])]
    result = set()

    def indices(v):
        nearest = round(v)
        return (nearest - 1, nearest) if abs(v - nearest) <= 1e-9 else (math.floor(v),)

    for t in probes:
        result.update(
            (r, c)
            for c in indices(x0 + t * (x1 - x0))
            for r in indices(y0 + t * (y1 - y0))
        )
    return result


@lru_cache(maxsize=8192)
def terrain_maximum(asset_id, digest, start, finish):
    dem, longitude, latitude, nodata = terrain_data(asset_id, digest)
    # WGS84 geodesic subdivision; closed-cell supercover on each projected raster chord.
    az, _, distance = GEOD.inv(*start, *finish)
    count = max(1, math.ceil(distance / 20))
    pts = (
        [start, *GEOD.npts(*start, *finish, count - 1), finish]
        if count > 1
        else [start, finish]
    )
    dx, dy = float(longitude[1] - longitude[0]), float(latitude[0] - latitude[1])
    pixels = [
        ((p[0] - longitude[0]) / dx + 0.5, (latitude[0] - p[1]) / dy + 0.5) for p in pts
    ]
    cells = set()
    for a, b in zip(pixels, pixels[1:]):
        cells.update(supercover_cells(*a, *b))
    if any(r < 0 or c < 0 or r >= dem.shape[0] or c >= dem.shape[1] for r, c in cells):
        raise InputNotReady("航段超出DEM覆盖范围，无法认证题设净空。")
    values = np.array([dem[r, c] for r, c in cells], dtype=float)
    if not len(values) or not np.all(np.isfinite(values)) or np.any(values == nodata):
        raise InputNotReady("航段接触NoData或无效高程。")
    return float(values.max())


def parameters(drone_type):
    energy = drone_type["energy_model"]
    charge = drone_type["charge_model"]
    if energy["model_id"] != ENERGY_MODEL or charge["model_id"] != CHARGE_MODEL:
        raise InputNotReady("不支持的能耗或充电模型ID。")
    p = energy["parameters"]
    required = [
        "empty_range_m",
        "full_range_m",
        "reference_energy_kwh",
        "climb_efficiency",
        "load_per_box_s",
    ]
    if not all(k in p for k in required):
        raise InputNotReady("能耗模型缺少必要参数。")
    if not (
        p["empty_range_m"] >= p["full_range_m"] > 0
        and p["reference_energy_kwh"] > 0
        and 0 < p["climb_efficiency"] <= 1
        and p["load_per_box_s"] >= 0
    ):
        raise InputNotReady("能耗模型参数范围不合法。")
    if charge["parameters"].get("full_charge_s", 0) <= 0:
        raise InputNotReady("充电模型缺少正的full_charge_s。")
    for key in ["energy_scale", "flight_time_scale"]:
        if p.get(key, 1) <= 0:
            raise InputNotReady("压力倍率必须为正数。")
    return p


def charge_seconds(drone_type, soc):
    full = drone_type["charge_model"]["parameters"]["full_charge_s"]
    s = max(0.0, min(1.0, soc))
    # Contest model: 65% of full duration below 90%, remaining 35% for top-off.
    return (
        full * (0.65 * (0.9 - s) / 0.9 + 0.35)
        if s < 0.9
        else full * 0.35 * (1 - s) / 0.1
    )


def leg(scenario, drone_type, start_id, end_id):
    p = parameters(drone_type)
    nodes = {n["id"]: n for n in [scenario["base"], *scenario["sites"]]}
    start, end = nodes[start_id], nodes[end_id]
    try:
        path = route_path(scenario, start["coordinates"], end["coordinates"])
    except RoutingUnavailable as exc:
        raise InputNotReady(str(exc)) from exc
    distance = sum(abs(GEOD.inv(*a, *b)[2]) for a, b in zip(path, path[1:]))
    base_id = scenario["base"]["id"]
    z0, z1 = start["ground_elevation_m"], end["ground_elevation_m"]
    if z0 is None or z1 is None:
        raise InputNotReady("能耗爬升模型需要基地与需求点的地面高程。")
    service_height = p.get("service_height_m", 30.0)
    work0 = z0 + (0 if start_id == base_id else service_height)
    work1 = z1 + (0 if end_id == base_id else service_height)
    terrain = scenario["terrain"]
    checked = terrain["status"] == "available"
    maximum = (
        max(
            terrain_maximum(
                terrain["asset_id"],
                terrain["sha256"],
                a,
                b,
            )
            for a, b in zip(path, path[1:])
        )
        if checked
        else max(z0, z1)
    )
    cruise = max(maximum + p.get("clearance_m", 50.0), work0, work1)
    return Leg(
        distance,
        max(0.0, cruise - work0),
        max(0.0, cruise - work1),
        cruise,
        checked,
        path,
    )


def leg_values(drone_type, geometry, payload_kg):
    p = parameters(drone_type)
    capacity = drone_type["max_payload_kg"]
    if payload_kg < -1e-8 or payload_kg > capacity + 1e-8:
        raise ValueError("载荷超过机型额定范围。")
    ratio = max(0.0, payload_kg) / capacity
    equivalent_range = (
        p["empty_range_m"] - (p["empty_range_m"] - p["full_range_m"]) * ratio**1.5
    )
    horizontal = p["reference_energy_kwh"] * geometry.distance_m / equivalent_range
    climb = (
        (drone_type["empty_mass_kg"] + payload_kg)
        * 9.81
        * geometry.climb_m
        / (p["climb_efficiency"] * 3600000)
    )
    energy = (horizontal + climb) * p.get("energy_scale", 1.0)
    seconds = (
        geometry.distance_m / drone_type["cruise_speed_mps"]
        + geometry.climb_m / drone_type["climb_speed_mps"]
        + geometry.descend_m / drone_type["descent_speed_mps"]
    ) * p.get("flight_time_scale", 1.0)
    return seconds, energy


def evaluate_route(scenario, drone_type, stops):
    """Compute a candidate using remaining payload on every outward/return leg."""
    cargos = {c["cargo_id"]: c for c in scenario["cargo_items"]}
    cargo_ids = [cid for _, ids in stops for cid in ids]
    if not cargo_ids or len(cargo_ids) != len(set(cargo_ids)):
        return None
    weight = sum(cargos[c]["mass_kg"] for c in cargo_ids)
    volume = sum(cargos[c]["volume_l"] for c in cargo_ids)
    if (
        weight > drone_type["max_payload_kg"] + 1e-9
        or volume > drone_type["max_volume_l"] + 1e-9
    ):
        return None
    p = parameters(drone_type)
    prep = drone_type["prepare_duration_s"] + p["load_per_box_s"] * len(cargo_ids)
    clock, energy, remaining = prep, 0.0, weight
    visits = []
    current = scenario["base"]["id"]
    coords = [scenario["base"]["coordinates"]]
    for dest, ids in [*stops, (scenario["base"]["id"], [])]:
        geom = leg(scenario, drone_type, current, dest)
        coords.extend([list(point) for point in geom.path[1:]])
        duration, use = leg_values(drone_type, geom, remaining)
        clock += duration
        energy += use
        if ids:
            clock += drone_type["handover_fixed_s"] + drone_type[
                "handover_per_box_s"
            ] * len(ids)
            visits.append(
                {"site_id": dest, "cargo_ids": list(ids), "delivery_complete_s": clock}
            )
            remaining -= sum(cargos[c]["mass_kg"] for c in ids)
        current = dest
    return {
        "type_id": drone_type["type_id"],
        "cargo_ids": cargo_ids,
        "stops": [(n, list(bs)) for n, bs in stops],
        "visits": visits,
        "prepare_s": prep,
        "duration_s": clock,
        "energy_kwh": energy,
        "route_geometry": {"type": "LineString", "coordinates": coords},
    }
