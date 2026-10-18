import copy
from fractions import Fraction
from functools import lru_cache
import math
import sys

import pytest

from shared.contracts import ContractError, content_hash, validate_outcome
from solver.bounds import capacity_divisor, capacity_lower_bound
from solver.numerics import CAPACITY_TOLERANCE
from solver.public_api import analyze, solve


def bind(s):
    return dict(
        schema_version=s["schema_version"],
        snapshot_id="SNAP-CAP-TEST",
        scenario_id=s["scenario_id"],
        scenario_state_version=s["state_version"],
        content_hash=content_hash(s),
        created_at=s["start_time"],
        scenario=s,
    )


def inventory(case, masses, volumes, capacity=10):
    s = copy.deepcopy(case[0]["scenario"])
    s["data_origin"] = "user_input"
    site = s["sites"][0]
    s["sites"] = [site]
    demand = copy.deepcopy(s["demands"][0])
    demand.update(
        demand_id="D-CAP",
        site_id=site["id"],
        cargo_type="MED",
        required_quantity=len(masses),
    )
    s["demands"] = [demand]
    sample = s["cargo_items"][0]
    s["cargo_items"] = [
        dict(
            sample,
            cargo_id=f"CAP-{i}",
            demand_id="D-CAP",
            type="MED",
            mass_kg=mass,
            volume_l=volume,
        )
        for i, (mass, volume) in enumerate(zip(masses, volumes))
    ]
    for typ in s["drone_types"]:
        typ.update(max_payload_kg=capacity, max_volume_l=capacity)
    return s


def packing_oracle(masses, volumes, capacity):
    masks = []
    for mask in range(1, 1 << len(masses)):
        if (
            math.fsum(value for i, value in enumerate(masses) if mask & (1 << i))
            <= capacity + CAPACITY_TOLERANCE
            and math.fsum(value for i, value in enumerate(volumes) if mask & (1 << i))
            <= capacity + CAPACITY_TOLERANCE
        ):
            masks.append(mask)

    @lru_cache(None)
    def dp(state):
        if not state:
            return 0
        results = [
            1 + dp(state ^ mask)
            for mask in masks
            if mask & state == mask and dp(state ^ mask) is not None
        ]
        return min(results) if results else None

    return dp((1 << len(masses)) - 1)


@pytest.mark.parametrize(
    "masses,volumes",
    [([6, 6, 4, 4], [4, 4, 6, 6]), ([6, 6, 6], [1, 1, 1]), ([3, 3, 3], [3, 3, 3])],
)
def test_bound_does_not_exceed_independent_exact_packing_oracle(case, masses, volumes):
    s = inventory(case, masses, volumes)
    report = capacity_lower_bound(bind(s))
    optimum = packing_oracle(masses, volumes, 10)
    assert report["status"] == "ready"
    assert report["sortie_lower_bound"] <= optimum
    if masses == [6, 6, 6]:
        assert report["sortie_lower_bound"] == 2 and optimum == 3
    ratio = Fraction(report["exact"]["mass_ratio"])
    assert report["mass_bound"] == math.ceil(ratio)


def test_surplus_inventory_uses_independent_lightest_and_smallest_witnesses(case):
    s = inventory(case, [1, 100, 50], [100, 1, 50], capacity=80)
    s["demands"][0]["required_quantity"] = 1
    before = copy.deepcopy(s)
    report = capacity_lower_bound(bind(s))
    witness = report["witnesses"][0]
    assert report["status"] == "ready" and report["sortie_lower_bound"] == 1
    assert witness["mass_cargo_ids"] == ["CAP-0"]
    assert witness["volume_cargo_ids"] == ["CAP-1"]
    assert report["mass_min_kg"] == report["volume_min_l"] == 1
    assert s == before


def test_resource_intersection_changes_bound_without_using_unavailable_large_type(case):
    s = copy.deepcopy(case[0]["scenario"])
    first = capacity_lower_bound(bind(s))
    assert first["sortie_lower_bound"] == 4 and "C" in first["eligible_type_ids"]
    for battery in s["batteries"]:
        if battery["compatible_type_id"] == "C":
            battery["status"] = "unavailable"
    second = capacity_lower_bound(bind(s))
    assert "C" not in second["eligible_type_ids"]
    assert second["sortie_lower_bound"] > first["sortie_lower_bound"]
    for battery in s["batteries"]:
        if battery["compatible_type_id"] == "C":
            battery.update(status="charging", soc=0.4)
    assert capacity_lower_bound(bind(s))["sortie_lower_bound"] == 4
    for drone in s["drones"]:
        if drone["type_id"] == "C":
            drone["status"] = "unavailable"
    assert "C" not in capacity_lower_bound(bind(s))["eligible_type_ids"]


@pytest.mark.parametrize(
    "fault", ["mock", "facts", "short_stock", "no_fleet", "closed_base"]
)
def test_unsupported_or_incomplete_input_withholds_numeric_bound(case, fault):
    s = copy.deepcopy(case[0]["scenario"])
    if fault == "mock":
        s["data_origin"] = "mock"
    elif fault == "facts":
        s["cargo_items"][0]["status"] = "loaded"
    elif fault == "short_stock":
        s["cargo_items"].pop()
    elif fault == "no_fleet":
        for drone in s["drones"]:
            drone["status"] = "unavailable"
    else:
        s["base"]["available"] = False
    report = capacity_lower_bound(bind(s))
    assert report["status"] == "limited" and report["sortie_lower_bound"] is None
    assert report["reason"]


def test_invalid_zero_demand_is_rejected_by_existing_contract(case):
    s = copy.deepcopy(case[0]["scenario"])
    for demand in s["demands"]:
        demand["required_quantity"] = 0
    for drone in s["drones"]:
        drone["status"] = "unavailable"
    with pytest.raises(ContractError):
        capacity_lower_bound(bind(s))


def test_integer_boundary_respects_validator_tolerance_and_binary64_summation(case):
    for masses, capacity in [
        ([0.1] * 10, 1),
        ([10 + CAPACITY_TOLERANCE / 2], 10),
        ([1e16] + [0.1] * 100, 1e16 + 10),
    ]:
        assert math.fsum(masses) <= capacity + CAPACITY_TOLERANCE
        exact = sum((Fraction(float(value)) for value in masses), Fraction(0))
        assert math.ceil(exact / capacity_divisor(capacity)) <= 1
    s = inventory(case, [0.1] * 10, [0.1] * 10, capacity=1)
    assert capacity_lower_bound(bind(s))["sortie_lower_bound"] == 1
    with pytest.raises(ValueError):
        capacity_divisor(sys.float_info.max)


def test_published_real_plan_and_analysis_respect_bound_and_preserve_snapshot(case):
    snapshot, options = case
    before = copy.deepcopy(snapshot)
    outcome = solve(snapshot, options)
    assert outcome["plan"]
    validate_outcome(outcome, snapshot)
    report = analyze(snapshot, outcome["plan"])["capacity_bound"]
    assert report["status"] == "ready"
    assert report["sortie_lower_bound"] <= len(outcome["plan"]["sorties"])
    assert report["snapshot_content_hash"] == snapshot["content_hash"]
    assert snapshot == before
