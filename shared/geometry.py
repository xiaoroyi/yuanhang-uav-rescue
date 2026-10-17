"""Dependency-free structural checks for simple closed WGS84 polygon rings."""


def valid_ring(ring):
    if (
        len(ring) < 4
        or ring[0] != ring[-1]
        or len(set(map(tuple, ring[:-1]))) != len(ring) - 1
    ):
        return False

    def cross(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    def on(a, b, c):
        return abs(cross(a, b, c)) <= 1e-15 and all(
            min(a[k], b[k]) - 1e-12 <= c[k] <= max(a[k], b[k]) + 1e-12 for k in [0, 1]
        )

    def touches(a, b, c, d):
        ab1, ab2, cd1, cd2 = (
            cross(a, b, c),
            cross(a, b, d),
            cross(c, d, a),
            cross(c, d, b),
        )
        return (
            ab1 * ab2 < 0
            and cd1 * cd2 < 0
            or on(a, b, c)
            or on(a, b, d)
            or on(c, d, a)
            or on(c, d, b)
        )

    edges = list(zip(ring, ring[1:]))
    for i, b in enumerate(ring[:-1]):
        a, c = ring[i - 1] if i else ring[-2], ring[i + 1]
        if (
            abs(cross(a, b, c)) <= 1e-15
            and sum((a[k] - b[k]) * (c[k] - b[k]) for k in [0, 1]) > 0
        ):
            return False
    for i, (a, b) in enumerate(edges):
        for j, (c, d) in enumerate(edges[i + 1 :], i + 1):
            if j == i + 1 or (i == 0 and j == len(edges) - 1):
                continue
            if touches(a, b, c, d):
                return False
    # Translate before shoelace to avoid cancellation at large geographic coordinates.
    x, y = ring[0]
    area = sum((a[0] - x) * (b[1] - y) - (b[0] - x) * (a[1] - y) for a, b in edges)
    return abs(area) > 1e-14
