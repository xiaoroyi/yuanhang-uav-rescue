"""Bounded local static polygon routing, separate from scheduling and resource search.

Polygons/buffers are interpreted in a base-centred WGS84 azimuthal equidistant
projection. Final geodesic segments are checked as 20 m chords against the
closed forbidden areas. This is a planning model, never an airspace permit.
"""

from functools import lru_cache
import heapq
import json
import math

from pyproj import CRS, Geod, Transformer
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

GEOD = Geod(ellps="WGS84")


class RoutingUnavailable(ValueError):
    pass


@lru_cache(maxsize=64)
def context(base, encoded_zones):
    crs = CRS.from_proj4(
        f"+proj=aeqd +lat_0={base[1]} +lon_0={base[0]} +datum=WGS84 +units=m"
    )
    forward = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
    backward = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
    forbidden, guards = [], []
    for zone in json.loads(encoded_zones):
        ring = zone["geometry"]["coordinates"][0]
        for point in ring:
            within_domain(base, point)
        polygon = Polygon([forward.transform(*p) for p in ring])
        if not polygon.is_valid or polygon.area < 0.001:
            raise RoutingUnavailable("限制区多边形无效或面积过小。")
        forbidden.append(polygon.buffer(zone["buffer_m"], join_style="mitre"))
        guards.append(polygon.buffer(zone["buffer_m"] + 10, join_style="mitre"))
    blocked = unary_union(forbidden)
    guard = unary_union(guards)
    polygons = [guard] if guard.geom_type == "Polygon" else list(guard.geoms)
    vertices = []
    for p in polygons:
        vertices.extend(p.exterior.coords[:-1])
        for hole in p.interiors:
            vertices.extend(hole.coords[:-1])
    vertices = sorted(
        set(tuple(p) for p in vertices if not blocked.intersects(Point(p)))
    )
    if len(vertices) > 240:
        raise RoutingUnavailable("限制区合并后的可见图过大，请简化边界。")
    return forward, backward, blocked, vertices


def within_domain(base, point):
    if abs(GEOD.inv(*base, *point)[2]) > 100_000:
        raise RoutingUnavailable("限制区模型只支持基地100km范围，请拆分场景。")


def geodesic_clear(path, forward, blocked):
    for start, end in zip(path, path[1:]):
        distance = abs(GEOD.inv(*start, *end)[2])
        count = max(1, math.ceil(distance / 20))
        points = (
            [start, *GEOD.npts(*start, *end, count - 1), end]
            if count > 1
            else [start, end]
        )
        if blocked.intersects(LineString([forward.transform(*p) for p in points])):
            return False
    return True


def signature(scenario):
    return tuple(scenario["base"]["coordinates"]), json.dumps(
        scenario.get("restricted_zones", []), sort_keys=True, separators=(",", ":")
    )


@lru_cache(maxsize=2048)
def _path(base, encoded_zones, start, end):
    within_domain(base, start)
    within_domain(base, end)
    forward, backward, blocked, vertices = context(base, encoded_zones)
    a, b = forward.transform(*start), forward.transform(*end)
    if blocked.intersects(Point(a)) or blocked.intersects(Point(b)):
        raise RoutingUnavailable("基地或服务点位于限制区及安全缓冲内，不能生成此航段。")
    if geodesic_clear([start, end], forward, blocked):
        return (start, end)
    points = [a, b, *vertices]
    neighbours = [[] for _ in points]
    for i, p in enumerate(points):
        for j in range(i):
            q = points[j]
            if not blocked.intersects(LineString([p, q])):
                distance = math.dist(p, q)
                neighbours[i].append((j, distance))
                neighbours[j].append((i, distance))
    distance = {0: 0.0}
    previous = {}
    queue = [(0.0, 0)]
    while queue:
        cost, node = heapq.heappop(queue)
        if cost > distance[node]:
            continue
        if node == 1:
            break
        for dest, weight in neighbours[node]:
            new = cost + weight
            if new < distance.get(dest, math.inf):
                distance[dest] = new
                previous[dest] = node
                heapq.heappush(queue, (new, dest))
    if 1 not in distance:
        raise RoutingUnavailable("有限可见图内未找到可认证绕行路径。")
    order, cursor = [1], 1
    while cursor != 0:
        cursor = previous[cursor]
        order.append(cursor)
    order.reverse()
    path = tuple(
        (
            start
            if i == 0
            else (
                end
                if i == 1
                else tuple(round(v, 12) for v in backward.transform(*points[i]))
            )
        )
        for i in order
    )
    if not geodesic_clear(path, forward, blocked):
        raise RoutingUnavailable("绕行测地航段仍接触限制区，已阻止发布。")
    return path


def route_path(scenario, start, end):
    if not scenario.get("restricted_zones"):
        return (tuple(start), tuple(end))
    return _path(*signature(scenario), tuple(start), tuple(end))


def path_is_clear(scenario, path):
    if not scenario.get("restricted_zones"):
        return True
    forward, _, blocked, _ = context(*signature(scenario))
    for p in path:
        within_domain(scenario["base"]["coordinates"], p)
    return geodesic_clear(path, forward, blocked)
