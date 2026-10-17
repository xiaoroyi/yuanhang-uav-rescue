"""Continuous links in a declared, finite projected DEM model.

Swept-ray clipping adapted from archived 问题3/src/communication.py. No legacy
imports or bootstrap. Terrain is frozen projected closed quadrilaterals; motion
is projected geodesic chords <=250 m. This is not a real radio certificate.
"""

from functools import lru_cache
import math
import time

import numpy as np
from numba import njit
from pyproj import Transformer
from shapely.geometry import MultiPoint, Polygon

from solver.assets import terrain_token, arrays_for_token, validate_reference
from solver.errors import InputNotReady
from solver.physics import GEOD, leg, parameters

RADIO_MODEL = "projected_dem_radio_v1"
PAD_M = 0.002
CHORD_M = 250.0


@njit(cache=True)
def _clip(poly, n, a, b, c):
    out = np.empty((16, 2))
    count = 0
    for i in range(n):
        j = (i + 1) % n
        x, y = poly[i]
        xx, yy = poly[j]
        f, g = a * x + b * y + c, a * xx + b * yy + c
        if f <= 1e-10:
            out[count, 0], out[count, 1] = x, y
            count += 1
        if (f < 0 and g > 0) or (f > 0 and g < 0):
            t = f / (f - g)
            out[count, 0], out[count, 1] = x + t * (xx - x), y + t * (yy - y)
            count += 1
    return out, count


@njit(cache=True)
def swept_blocked(anchor, p0, p1, vertices, heights, pad=PAD_M):
    """Project clipped swept-ray triangle onto u in [0,1], including contacts."""
    result = np.empty((len(heights), 2))
    count = 0
    v0, v1 = p0 - anchor, p1 - anchor
    for k in range(len(heights)):
        if heights[k] + 1e-7 < min(anchor[2], p0[2], p1[2]):
            continue
        poly = np.empty((16, 2))
        poly[0], poly[1], poly[2] = [0.0, 0.0], [1.0, 0.0], [0.0, 1.0]
        n = 3
        for e in range(4):
            x, y = vertices[k, e]
            xx, yy = vertices[k, (e + 1) % 4]
            dx, dy = xx - x, yy - y
            a = dx * v0[1] - dy * v0[0]
            b = dx * v1[1] - dy * v1[0]
            c = dx * (anchor[1] - y) - dy * (anchor[0] - x) - pad * math.hypot(dx, dy)
            poly, n = _clip(poly, n, a, b, c)
            if n == 0:
                break
        if n == 0:
            continue
        poly, n = _clip(poly, n, v0[2], v1[2], anchor[2] - heights[k] - 1e-7)
        low, high, has_zero = 1.0, 0.0, False
        for j in range(n):
            denominator = poly[j, 0] + poly[j, 1]
            if denominator > 1e-12:
                u = poly[j, 1] / denominator
                low, high = min(low, u), max(high, u)
            else:
                has_zero = True
        if has_zero and anchor[2] <= heights[k] + 1e-7:
            low, high = 0.0, 1.0
        if high >= low:
            result[count, 0], result[count, 1] = max(0.0, low), min(1.0, high)
            count += 1
    return result[:count]


def merge(intervals, tolerance=1e-10):
    result = []
    for a, b in sorted(intervals, key=lambda pair: (pair[0], pair[1])):
        if b < a:
            continue
        if result and a <= result[-1][1] + tolerance:
            result[-1][1] = max(result[-1][1], b)
        else:
            result.append([float(a), float(b)])
    return result


@lru_cache(maxsize=2)
def _grid(token, epsg):
    dem, lon, lat, nodata, _ = arrays_for_token(token)
    forward = Transformer.from_crs(4326, epsg, always_xy=True)
    dx, dy = lon[1] - lon[0], lat[0] - lat[1]
    le, la = (
        np.r_[lon - dx / 2, lon[-1] + dx / 2],
        np.r_[lat + dy / 2, lat[-1] - dy / 2],
    )
    lo, lt = np.meshgrid(le, la)
    x, y = forward.transform(lo, lt)
    ex, ey = np.diff(x, axis=1), np.diff(y, axis=1)
    sx, sy = np.diff(x, axis=0), np.diff(y, axis=0)
    horizontal, vertical = np.hypot(ex, ey), np.hypot(sx, sy)
    if not (
        np.all(np.isfinite(horizontal))
        and np.all(np.isfinite(vertical))
        and min(horizontal.min(), vertical.min()) > 0
        and max(horizontal.max(), vertical.max()) <= 1000
    ):
        raise InputNotReady("连续通信需要投影后边长不超过1000m的有效DEM像元。")
    cosine = np.abs(ex[:-1] * sx[:, :-1] + ey[:-1] * sy[:, :-1]) / (
        horizontal[:-1] * vertical[:, :-1]
    )
    if np.any(cosine > 0.2):
        raise InputNotReady("DEM投影像元角度失真超出当前连续通信模型范围。")
    heights = np.where(np.isfinite(dem) & (dem != nodata), dem, 1e9).astype(float)
    tiles = []
    for row in range(0, dem.shape[0], 32):
        for col in range(0, dem.shape[1], 32):
            r1, c1 = min(row + 32, dem.shape[0]), min(col + 32, dem.shape[1])
            xx, yy = x[row : r1 + 1, col : c1 + 1], y[row : r1 + 1, col : c1 + 1]
            tiles.append(
                [
                    row,
                    r1,
                    col,
                    c1,
                    xx.min(),
                    xx.max(),
                    yy.min(),
                    yy.max(),
                    heights[row:r1, col:c1].max(),
                ]
            )
    tiles = np.asarray(tiles)
    for array in [x, y, heights, tiles]:
        array.setflags(write=False)
    return x, y, heights, tiles


class Radio:
    def __init__(self, scenario, deadline=math.inf):
        self.s = scenario
        self.config = scenario.get("communication")
        if not self.config or self.config["model_id"] != RADIO_MODEL:
            raise InputNotReady("连续通信需要已配置的投影DEM链路模型。")
        terrain = scenario["terrain"]
        if terrain["status"] != "available":
            raise InputNotReady("连续通信需要绑定有效DEM。")
        validate_reference(terrain)
        self.token = terrain_token(terrain["asset_id"], terrain["sha256"])
        self.dem, self.lon, self.lat, self.nodata, _ = arrays_for_token(self.token)
        longitude, latitude = scenario["base"]["coordinates"]
        if not -80 <= latitude <= 84:
            raise InputNotReady("当前通信投影模型仅支持UTM纬度范围。")
        zone = min(60, max(1, math.floor((longitude + 180) / 6) + 1))
        self.epsg = (32600 if latitude >= 0 else 32700) + zone
        self.forward = Transformer.from_crs(4326, self.epsg, always_xy=True)
        self.inverse = Transformer.from_crs(self.epsg, 4326, always_xy=True)
        self.x, self.y, self.heights, self.tiles = _grid(self.token, self.epsg)
        xx, yy = self.x, self.y
        boundary = [
            *zip(xx[0], yy[0]),
            *zip(xx[1:, -1], yy[1:, -1]),
            *zip(xx[-1, -2::-1], yy[-1, -2::-1]),
            *zip(xx[-2:0:-1, 0], yy[-2:0:-1, 0]),
        ]
        self.domain = Polygon(boundary)
        if not self.domain.is_valid:
            raise InputNotReady("DEM投影外边界无效，无法检查连续通信。")
        self.deadline = deadline
        self.cache = {}
        self.dx, self.dy = self.lon[1] - self.lon[0], self.lat[0] - self.lat[1]
        base = scenario["base"]
        self.gateway = self.xyz(
            base["coordinates"],
            base["ground_elevation_m"] + self.config["gateway"]["antenna_height_m"],
        )
        self.base_loss = 32.45 + 20 * math.log10(self.config["frequency_mhz"]) - 60
        self.radii = {}
        self.limits = {}
        for kind, names in {
            "direct": ("gateway", "transport"),
            "access": ("relay_access", "transport"),
            "backhaul": ("gateway", "relay_backhaul"),
        }.items():
            a, b = [self.config[name] for name in names]
            threshold = self.config["sensitivity_dbm"] + self.config["fading_margin_db"]
            limit = (
                min(a["tx_power_dbm"], b["tx_power_dbm"])
                + a["gain_dbi"]
                + b["gain_dbi"]
                - self.config["system_loss_db"]
                - threshold
            )
            self.limits[kind] = limit
            self.radii[kind] = (
                10
                ** ((limit - self.base_loss - self.config["obstruction_loss_db"]) / 20),
                10 ** ((limit - self.base_loss) / 20),
            )

    def check_time(self):
        if time.perf_counter() > self.deadline:
            raise TimeoutError("连续通信几何计算达到预算。")

    def xyz(self, coordinate, altitude):
        if abs(GEOD.inv(*self.s["base"]["coordinates"], *coordinate)[2]) > 100000:
            raise InputNotReady("当前通信模型限制在基地100km范围内。")
        c, r = (coordinate[0] - self.lon[0]) / self.dx + 0.5, (
            self.lat[0] - coordinate[1]
        ) / self.dy + 0.5
        if not (0 < c < self.dem.shape[1] and 0 < r < self.dem.shape[0]):
            raise InputNotReady("通信端点超出DEM内部覆盖范围。")
        return np.array([*self.forward.transform(*coordinate), altitude], dtype=float)

    def cells(self, a, p0, p1):
        points = np.array([a, p0, p1])
        xmin, ymin = points[:, :2].min(axis=0)
        xmax, ymax = points[:, :2].max(axis=0)
        # Exact bbox hierarchy of the frozen quadrilaterals: no inverse-projection
        # sampling heuristic may discard a cell that touches the swept triangle.
        tiles = self.tiles
        guard = PAD_M * 4
        selected = tiles[
            (tiles[:, 4] <= xmax + guard)
            & (tiles[:, 5] >= xmin - guard)
            & (tiles[:, 6] <= ymax + guard)
            & (tiles[:, 7] >= ymin - guard)
            & (tiles[:, 8] >= points[:, 2].min() - 1e-7)
        ]
        rows, cols = [], []
        for tile in selected:
            r0, r1, c0, c1 = tile[:4].astype(int)
            rr, cc = np.where(self.heights[r0:r1, c0:c1] >= points[:, 2].min() - 1e-7)
            rr, cc = rr + r0, cc + c0
            xs = np.stack(
                [
                    self.x[rr, cc],
                    self.x[rr, cc + 1],
                    self.x[rr + 1, cc + 1],
                    self.x[rr + 1, cc],
                ],
                axis=1,
            )
            ys = np.stack(
                [
                    self.y[rr, cc],
                    self.y[rr, cc + 1],
                    self.y[rr + 1, cc + 1],
                    self.y[rr + 1, cc],
                ],
                axis=1,
            )
            keep = (
                (xs.min(axis=1) <= xmax + guard)
                & (xs.max(axis=1) >= xmin - guard)
                & (ys.min(axis=1) <= ymax + guard)
                & (ys.max(axis=1) >= ymin - guard)
            )
            rows.append(rr[keep])
            cols.append(cc[keep])
        rs = np.concatenate(rows) if rows else np.array([], dtype=int)
        cs = np.concatenate(cols) if cols else np.array([], dtype=int)
        vertices = np.stack(
            [
                np.stack([self.x[rs, cs], self.y[rs, cs]], axis=1),
                np.stack([self.x[rs, cs + 1], self.y[rs, cs + 1]], axis=1),
                np.stack([self.x[rs + 1, cs + 1], self.y[rs + 1, cs + 1]], axis=1),
                np.stack([self.x[rs + 1, cs], self.y[rs + 1, cs]], axis=1),
            ],
            axis=1,
        )
        return vertices, self.heights[rs, cs]

    def profile(self, anchor, p0, p1, kind):
        self.check_time()
        a, p0, p1 = [np.asarray(v, dtype=float) for v in [anchor, p0, p1]]
        key = (*a, *p0, *p1, kind)
        if key in self.cache:
            return self.cache[key]
        if not self.domain.covers(MultiPoint([a[:2], p0[:2], p1[:2]]).convex_hull):
            raise InputNotReady(
                "通信视线扫掠范围超出投影DEM，不能用范围外未知高程认证。"
            )
        rb, rc = self.radii[kind]
        v, w = p1 - p0, p0 - a
        aa, bb, cc = np.dot(v, v), 2 * np.dot(w, v), np.dot(w, w)
        if max(np.linalg.norm(w), np.linalg.norm(p1 - a)) <= rb:
            return {"pieces": [[0.0, 1.0, True]], "events": []}
        u = np.clip(-bb / (2 * aa), 0, 1) if aa > 1e-18 else 0
        if np.linalg.norm(w + u * v) > rc:
            return {"pieces": [[0.0, 1.0, False]], "events": [0.0, 1.0]}
        vertices, heights = self.cells(a, p0, p1)
        blocked = merge(swept_blocked(a, p0, p1, vertices, heights))
        cuts = [0.0, 1.0, *[u for pair in blocked for u in pair]]
        for radius in [rb, rc]:
            if aa > 1e-18:
                discriminant = bb * bb - 4 * aa * (cc - radius * radius)
                if discriminant >= 0:
                    cuts.extend(
                        u
                        for u in [
                            (-bb - math.sqrt(discriminant)) / (2 * aa),
                            (-bb + math.sqrt(discriminant)) / (2 * aa),
                        ]
                        if 0 < u < 1
                    )
        cuts = sorted(set(cuts))

        def valid(u):
            distance = np.linalg.norm(w + u * v)
            obstacle = any(lo - 1e-11 <= u <= hi + 1e-11 for lo, hi in blocked)
            return bool(
                distance <= rb + 1e-8 or (not obstacle and distance <= rc + 1e-8)
            )

        result = {
            "pieces": [
                [lo, hi, valid((lo + hi) / 2)]
                for lo, hi in zip(cuts, cuts[1:])
                if hi > lo
            ],
            "events": [u for u in cuts if not valid(u)],
        }
        self.cache[key] = result
        return result


def bad_intervals(profile, start, end, padding=1e-5):
    intervals = [
        [
            max(start, start + lo * (end - start) - padding),
            min(end, start + hi * (end - start) + padding),
        ]
        for lo, hi, ok in profile["pieces"]
        if not ok
    ]
    intervals += [
        [
            max(start, start + u * (end - start) - padding),
            min(end, start + u * (end - start) + padding),
        ]
        for u in profile["events"]
    ]
    return merge(intervals)


def all_pass(profile, lo, hi):
    return not any(
        not ok and b > lo + 1e-12 and a < hi - 1e-12 for a, b, ok in profile["pieces"]
    ) and not any(lo - 1e-12 <= event <= hi + 1e-12 for event in profile["events"])


def transport_phases(s, sortie, radio):
    drones = {d["drone_id"]: d for d in s["drones"]}
    typ = next(
        t
        for t in s["drone_types"]
        if t["type_id"] == drones[sortie["drone_id"]]["type_id"]
    )
    params = parameters(typ)
    nodes = {n["id"]: n for n in [s["base"], *s["sites"]]}
    current, tick, result = s["base"]["id"], sortie["takeoff_s"], []

    def append(kind, a, b, duration):
        nonlocal tick
        if duration > 1e-10:
            result.append(
                {
                    "phase": kind,
                    "start_s": tick,
                    "end_s": tick + duration,
                    "p0": a,
                    "p1": b,
                }
            )
        tick += duration

    for visit in [*sortie["visits"], {"site_id": s["base"]["id"], "cargo_ids": []}]:
        dest = visit["site_id"]
        geometry = leg(s, typ, current, dest)
        scale = params.get("flight_time_scale", 1)
        z0 = nodes[current]["ground_elevation_m"] + (
            0 if current == s["base"]["id"] else params.get("service_height_m", 30)
        )
        z1 = nodes[dest]["ground_elevation_m"] + (
            0 if dest == s["base"]["id"] else params.get("service_height_m", 30)
        )
        coordinate = nodes[current]["coordinates"]
        append(
            "climb",
            radio.xyz(coordinate, z0),
            radio.xyz(coordinate, geometry.cruise_m),
            geometry.climb_m / typ["climb_speed_mps"] * scale,
        )
        for a, b in zip(geometry.path, geometry.path[1:]):
            distance = abs(GEOD.inv(*a, *b)[2])
            count = max(1, math.ceil(distance / CHORD_M))
            points = [a, *GEOD.npts(*a, *b, count - 1), b] if count > 1 else [a, b]
            for aa, bb in zip(points, points[1:]):
                duration = abs(GEOD.inv(*aa, *bb)[2]) / typ["cruise_speed_mps"] * scale
                append(
                    "cruise",
                    radio.xyz(aa, geometry.cruise_m),
                    radio.xyz(bb, geometry.cruise_m),
                    duration,
                )
        coordinate = nodes[dest]["coordinates"]
        append(
            "descent",
            radio.xyz(coordinate, geometry.cruise_m),
            radio.xyz(coordinate, z1),
            geometry.descend_m / typ["descent_speed_mps"] * scale,
        )
        if visit["cargo_ids"]:
            append(
                "handover",
                radio.xyz(coordinate, z1),
                radio.xyz(coordinate, z1),
                typ["handover_fixed_s"]
                + typ["handover_per_box_s"] * len(visit["cargo_ids"]),
            )
        current = dest
    if abs(tick - sortie["return_s"]) > 1e-5:
        raise InputNotReady("通信阶段与运输返航时间不一致。")
    return result
