"""Read-only spatial samples using the same saved DEM/radio model as the solver."""

from __future__ import annotations
import math
import time
from functools import lru_cache
import json
import copy
from typing import Literal

import numpy as np
from pydantic import BaseModel, ConfigDict
from solver.radio import Radio, all_pass
from solver.errors import InputNotReady
from solver.assets import validate_reference
from backend.app.flight_profiles import ground_sample


class CoveragePoint(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    coordinates: tuple[float, float]
    elevation_m: float | None
    source: Literal["gateway", "relay", "uncovered", "unknown"]


class RadioCoverage(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    plan_id: str
    snapshot_id: str
    terrain_sha256: str
    vertical_datum: str | None
    relay_sortie_id: str | None
    relay_service_start_s: float | None
    relay_service_end_s: float | None
    relay_backhaul_available: bool | None
    altitude_agl_m: float
    bounds: tuple[float, float, float, float]
    grid_size: int
    points: list[CoveragePoint]
    complete: bool
    notice: str


def radio_coverage(snapshot, plan, altitude_agl_m, relay_sortie_id=None, grid_size=21):
    # Cache immutable source JSON only, including the exact terrain digest.
    validate_reference(snapshot["scenario"]["terrain"])
    result = _coverage(
        json.dumps(snapshot, sort_keys=True),
        json.dumps(plan, sort_keys=True),
        altitude_agl_m,
        relay_sortie_id,
        grid_size,
    )
    if not result["complete"]:
        _coverage.cache_clear()  # A retry can finish after a cold JIT startup.
    return copy.deepcopy(result)


@lru_cache(maxsize=24)
def _coverage(snapshot_json, plan_json, agl, relay_id, grid_size):
    snapshot, plan = json.loads(snapshot_json), json.loads(plan_json)
    s = snapshot["scenario"]
    if not s.get("communication"):
        raise InputNotReady("本方案快照未配置通信模型。")
    relay = next(
        (r for r in plan.get("relay_sorties", []) if r["relay_sortie_id"] == relay_id),
        None,
    )
    if relay_id and relay is None:
        raise KeyError(relay_id)
    radio = Radio(s, deadline=time.perf_counter() + 12)
    dem = (radio.dem, radio.lon, radio.lat, radio.nodata)
    coords = [s["base"]["coordinates"], *[p["coordinates"] for p in s["sites"]]]
    if relay:
        coords.append(relay["station_coordinates"])
    xs, ys = zip(*coords)
    xspan = max(max(xs) - min(xs), 0.01)
    yspan = max(max(ys) - min(ys), 0.01)
    # Interior only; never infer terrain outside the native DEM.
    west = max(float(min(radio.lon) + abs(radio.dx)), min(xs) - xspan * 0.15)
    east = min(float(max(radio.lon) - abs(radio.dx)), max(xs) + xspan * 0.15)
    south = max(float(min(radio.lat) + abs(radio.dy)), min(ys) - yspan * 0.15)
    north = min(float(max(radio.lat) - abs(radio.dy)), max(ys) + yspan * 0.15)
    if west >= east or south >= north:
        raise InputNotReady("任务范围与有效DEM内部没有足够重叠。")
    station = (
        radio.xyz(relay["station_coordinates"], relay["station_elevation_m"])
        if relay
        else None
    )
    backhaul = (
        all_pass(radio.profile(radio.gateway, station, station, "backhaul"), 0, 1)
        if relay
        else None
    )
    points = []
    complete = True
    for lat in np.linspace(south, north, grid_size):
        for lon in np.linspace(west, east, grid_size):
            coordinate = (float(lon), float(lat))
            ground = ground_sample(dem, coordinate)
            source = "unknown"
            height = None
            if ground is not None and math.isfinite(ground):
                height = ground + agl
                try:
                    p = radio.xyz(coordinate, height)
                    direct = all_pass(
                        radio.profile(radio.gateway, p, p, "direct"), 0, 1
                    )
                    if direct:
                        source = "gateway"
                    elif backhaul and all_pass(
                        radio.profile(station, p, p, "access"), 0, 1
                    ):
                        source = "relay"
                    else:
                        source = "uncovered"
                except TimeoutError:
                    complete = False
                except InputNotReady:
                    pass
            points.append(
                {"coordinates": coordinate, "elevation_m": height, "source": source}
            )
    return {
        "plan_id": plan["plan_id"],
        "snapshot_id": snapshot["snapshot_id"],
        "terrain_sha256": s["terrain"]["sha256"],
        "vertical_datum": s["terrain"].get("vertical_datum"),
        "relay_sortie_id": relay_id,
        "relay_service_start_s": relay["service_start_s"] if relay else None,
        "relay_service_end_s": relay["service_end_s"] if relay else None,
        "relay_backhaul_available": backhaul,
        "altitude_agl_m": agl,
        "bounds": [west, south, east, north],
        "grid_size": grid_size,
        "points": points,
        "complete": complete,
        "notice": "指定离地高度的离散空间采样；采用保存快照的双向预算与原始DEM遮挡模型。中继采样仅解释该站位在其服务期内的空间连接能力，不表示采样点之间连续覆盖，不替代实际航迹的连续时间验证，也不是真实射频认证。未知点保持未知。",
    }
