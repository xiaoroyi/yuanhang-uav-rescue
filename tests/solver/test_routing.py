import copy

import pytest

from shared.contracts import (
    ContractError,
    content_hash,
    validate_outcome,
    validate_scenario,
)
from solver.physics import leg
from solver.public_api import solve, validate, playback
from solver.routing import route_path, path_is_clear, RoutingUnavailable


@pytest.fixture
def spatial_case(case):
    snap, opts = copy.deepcopy(case)
    s = snap["scenario"]
    s["base"].update(coordinates=[108.0, 23.0], ground_elevation_m=100.0)
    s["sites"] = [
        {**s["sites"][0], "coordinates": [108.02, 23.0], "ground_elevation_m": 100.0}
    ]
    s["demands"] = [
        {
            **s["demands"][0],
            "site_id": s["sites"][0]["id"],
            "required_quantity": 1,
            "hard_deadline_s": None,
            "expected_deadline_s": None,
        }
    ]
    s["cargo_items"] = [
        {
            **s["cargo_items"][0],
            "demand_id": s["demands"][0]["demand_id"],
            "mass_kg": 1.0,
            "volume_l": 1.0,
        }
    ]
    s["terrain"].update(
        status="not_evaluated",
        asset_id=None,
        sha256=None,
        horizontal_crs=None,
        vertical_datum=None,
    )
    s["policy"]["requires_terrain"] = False
    s["data_origin"] = "user_input"
    s["restricted_zones"] = [
        {
            "zone_id": "ZONE-001",
            "name": "Test no-fly area",
            "buffer_m": 30.0,
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [108.009, 22.998],
                        [108.011, 22.998],
                        [108.011, 23.002],
                        [108.009, 23.002],
                        [108.009, 22.998],
                    ]
                ],
            },
        }
    ]
    snap["content_hash"] = content_hash(s)
    opts["requested_model_scope"] = [
        c for c in opts["requested_model_scope"] if c != "terrain"
    ] + ["restricted_zone"]
    return snap, opts


def test_detour_changes_true_physics_and_passes_independent_checks(spatial_case):
    snap, opts = spatial_case
    s = snap["scenario"]
    typ = s["drone_types"][0]
    a, b = s["base"]["coordinates"], s["sites"][0]["coordinates"]
    path = route_path(s, a, b)
    assert len(path) > 2 and path_is_clear(s, path)
    assert not path_is_clear(s, [a, b])
    moved = copy.deepcopy(s)
    ring = moved["restricted_zones"][0]["geometry"]["coordinates"][0]
    for point in ring:
        point[1] += 0.02
    assert route_path(moved, a, b) == (tuple(a), tuple(b))
    assert route_path(s, a, b) == path
    baseline = copy.deepcopy(s)
    baseline.pop("restricted_zones")
    assert (
        leg(s, typ, s["base"]["id"], s["sites"][0]["id"]).distance_m
        > leg(baseline, typ, s["base"]["id"], s["sites"][0]["id"]).distance_m
    )
    result = solve(snap, opts)
    assert result["plan"], result
    validate_outcome(result, snap)
    plan = result["plan"]
    assert "restricted_zone" in plan["model_scope"]
    assert any(
        c["code"] == "restricted_zone" and c["status"] == "passed"
        for c in plan["validation"]["checks"]
    )
    assert len(plan["sorties"][0]["route_geometry"]["coordinates"]) > 3
    replay = playback(plan, snap)
    assert len([p for p in replay["phases"] if p["phase"] == "flight"]) > 1
    for phase in replay["phases"]:
        assert path_is_clear(s, [phase["from_coordinates"], phase["to_coordinates"]])
    forged = copy.deepcopy(plan)
    forged["sorties"][0]["route_geometry"]["coordinates"] = [a, b, a]
    report = validate(snap, forged)
    assert report["status"] == "failed"
    assert any(
        c["code"] == "restricted_zone" and c["status"] == "failed"
        for c in report["checks"]
    )


@pytest.mark.parametrize("bad", ["open", "bowtie", "duplicate", "degenerate"])
def test_malformed_polygons_rejected_before_solve(spatial_case, bad):
    snap, _ = spatial_case
    s = snap["scenario"]
    ring = s["restricted_zones"][0]["geometry"]["coordinates"][0]
    if bad == "open":
        ring[-1] = [108.0, 23.0]
    elif bad == "bowtie":
        ring[1], ring[2] = ring[2], ring[1]
    elif bad == "duplicate":
        ring[1] = ring[0]
    else:
        ring[:] = [[108.0, 23.0], [108.001, 23.0], [108.002, 23.0], [108.0, 23.0]]
    with pytest.raises(ContractError):
        validate_scenario(s)


def test_buffer_boundary_endpoint_and_domain_are_not_silently_ignored(spatial_case):
    snap, opts = spatial_case
    s = snap["scenario"]
    with pytest.raises(RoutingUnavailable):
        route_path(s, [108.01, 23.0], s["base"]["coordinates"])
    with pytest.raises(RoutingUnavailable):
        route_path(s, [108.009, 22.998], s["base"]["coordinates"])
    with pytest.raises(RoutingUnavailable):
        route_path(s, [108.0089, 23.0], s["base"]["coordinates"])
    with pytest.raises(RoutingUnavailable):
        route_path(s, [110.0, 23.0], s["base"]["coordinates"])
    s["sites"][0]["coordinates"] = [108.01, 23.0]
    snap["content_hash"] = content_hash(s)
    result = solve(snap, opts)
    assert result["plan"] is None and result["solver_status"] == "UNKNOWN"
