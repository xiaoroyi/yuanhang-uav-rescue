import copy
from decimal import Decimal
import functools
import math

import pytest

from shared.contracts import content_hash
from solver.adapters.contest import contest_scenario
from solver.nominal import analyze_single_site, safe_capacity, validate_batches
from solver.physics import evaluate_route, parameters


def snapshot(s):
    return dict(
        schema_version=s["schema_version"],
        snapshot_id="SNAP-NOMINAL-TEST",
        scenario_id=s["scenario_id"],
        scenario_state_version=s["state_version"],
        content_hash=content_hash(s),
        created_at=s["start_time"],
        scenario=s,
    )


def tiny(case):
    s = copy.deepcopy(case[0]["scenario"])
    s["data_origin"] = "user_input"
    s["sites"] = [next(a for a in s["sites"] if a["id"] == "S001")]
    demand = copy.deepcopy(s["demands"][0])
    demand.update(
        demand_id="D-NOMINAL", site_id="S001", cargo_type="MED", required_quantity=4
    )
    box = s["cargo_items"][0]
    s["demands"] = [demand]
    s["cargo_items"] = [
        dict(
            box,
            cargo_id=f"C-{i}",
            demand_id="D-NOMINAL",
            type="MED",
            mass_kg=10.0,
            volume_l=1.0,
        )
        for i in range(4)
    ]
    for typ in s["drone_types"]:
        typ.update(max_payload_kg=25.0, max_volume_l=100.0)
        typ["energy_model"]["parameters"].update(empty_range_m=1e9, full_range_m=1e9)
    return s


def test_original_80_box_count_dp_and_all_baselines_are_recomputed():
    snap = snapshot(contest_scenario())
    original = copy.deepcopy(snap)
    report = analyze_single_site(snap)
    assert snap == original
    assert report["status"] == "complete"
    assert report["metrics"]["sortie_count"] == 18
    assert report["metrics"]["energy_kwh"] == pytest.approx(59.13129602205529)
    assert len(report["capacities"]) == 45
    assert report["required_box_count"] == report["available_box_count"] == 80
    ids = [c for row in report["batches"] for c in row["cargo_ids"]]
    assert len(ids) == len(set(ids)) == 80
    assert len(report["audit_checks"]) == 6
    assert report["single_box_baseline"]["sortie_count"] == 80
    assert report["greedy_baseline"]["sortie_count"] >= 18
    assert [
        (row["min_return_soc"], row["metrics"]["sortie_count"])
        for row in report["sensitivity"]
    ] == [(0.1, 18), (0.2, 18), (0.3, 20)]
    assert min(row["return_soc"] for row in report["batches"]) >= 0.2
    assert all(
        not ({"drone_id", "battery_id", "start_s"} & row.keys())
        for row in report["batches"]
    )


def test_changed_mass_changes_real_answer_and_distinct_subset_oracle_agrees(case):
    s = tiny(case)
    first = analyze_single_site(snapshot(s))
    assert first["metrics"]["sortie_count"] == 2
    s["cargo_items"][0]["mass_kg"] = 20.0
    second = analyze_single_site(snapshot(s))
    assert second["metrics"]["sortie_count"] == 3
    assert second["analysis_input_hash"] != first["analysis_input_hash"]
    boxes = s["cargo_items"]
    choices = {}
    for mask in range(1, 1 << len(boxes)):
        ids = [box["cargo_id"] for i, box in enumerate(boxes) if mask & (1 << i)]
        costs = []
        for typ in s["drone_types"]:
            route = evaluate_route(s, typ, [("S001", ids)])
            if (
                route
                and 1 - route["energy_kwh"] / parameters(typ)["reference_energy_kwh"]
                >= 0.2
            ):
                costs.append(
                    (
                        1,
                        Decimal(str(route["energy_kwh"])),
                        Decimal(str(route["duration_s"])),
                    )
                )
        if costs:
            choices[mask] = min(costs)

    @functools.lru_cache(None)
    def oracle(mask):
        if not mask:
            return 0, Decimal(0), Decimal(0)
        values = []
        for subset, cost in choices.items():
            if subset & mask == subset:
                rest = oracle(mask ^ subset)
                if rest is not None:
                    values.append(tuple(a + b for a, b in zip(cost, rest)))
        return min(values) if values else None

    expected = oracle((1 << len(boxes)) - 1)
    assert second["metrics"]["sortie_count"] == expected[0]
    assert second["metrics"]["energy_kwh"] == pytest.approx(float(expected[1]))
    assert second["metrics"]["operation_s"] == pytest.approx(float(expected[2]))


def test_capacity_bisection_is_safe_and_unreachable_is_null(case):
    s = case[0]["scenario"]
    typ = s["drone_types"][0]
    capacities = [safe_capacity(s, typ, "S001", rho) for rho in [0.1, 0.2, 0.5]]
    assert all(
        row["residual_kwh"] >= -1e-10
        for row in capacities
        if row["capacity_kg"] is not None
    )
    values = [row["capacity_kg"] or 0 for row in capacities]
    assert values == sorted(values, reverse=True)
    for row in capacities:
        if row["limit"] == "energy":
            assert 0 <= row["root_width_kg"] <= 1e-7
    empty = safe_capacity(s, typ, "S001", 1.0)
    assert empty["capacity_kg"] is None and empty["limit"] == "empty_infeasible"
    assert empty["empty_energy_kwh"] > 0


@pytest.mark.parametrize(
    "fault",
    [
        "duplicate",
        "missing",
        "energy",
        "soc",
        "duration",
        "volume",
        "type",
        "site",
        "empty_batch",
        "batch_id",
    ],
)
def test_independent_auditor_rejects_corrupted_batches(case, fault):
    s = tiny(case)
    rows = analyze_single_site(snapshot(s))["batches"]
    if fault == "duplicate":
        rows[0]["cargo_ids"].append(rows[0]["cargo_ids"][0])
    elif fault == "missing":
        rows.pop()
    elif fault == "empty_batch":
        rows.append(dict(rows[0], batch_id="EMPTY", cargo_ids=[]))
    elif fault == "batch_id":
        rows[1]["batch_id"] = rows[0]["batch_id"]
    elif fault == "type":
        rows[0]["type_id"] = "DOES-NOT-EXIST"
    elif fault == "site":
        rows[0]["site_id"] = s["base"]["id"]
    else:
        key = {
            "energy": "energy_kwh",
            "soc": "return_soc",
            "duration": "duration_s",
            "volume": "volume_l",
        }[fault]
        rows[0][key] += 1.0
    with pytest.raises((ValueError, KeyError)):
        validate_batches(s, rows, [b["cargo_id"] for b in s["cargo_items"]], 0.2)


def test_surplus_and_excessive_states_withhold_complete_optimality(case):
    s = tiny(case)
    s["cargo_items"].append(dict(s["cargo_items"][0], cargo_id="SURPLUS"))
    report = analyze_single_site(snapshot(s))
    assert report["status"] == "partial" and report["metrics"] is None
    assert "库存" in report["sites"][0]["reason"]
    s = tiny(case)
    s["demands"][0]["required_quantity"] = 10
    s["cargo_items"] = [
        dict(s["cargo_items"][0], cargo_id=f"VAR-{i}", mass_kg=1.0 + i / 100)
        for i in range(10)
    ]
    report = analyze_single_site(snapshot(s))
    assert report["status"] == "partial" and report["metrics"] is None
    assert report["sites"][0]["status"] == "limited"
    assert report["sites"][0]["count_states"] == 1024


def test_timeout_is_limited_and_finite_complete_no_packing_is_infeasible(
    case, monkeypatch
):
    s = tiny(case)

    def exhausted(*args):
        raise TimeoutError("test budget")

    monkeypatch.setattr("solver.nominal.count_dp", exhausted)
    limited = analyze_single_site(snapshot(s))
    assert limited["status"] == "partial"
    assert limited["sites"][0]["status"] == "limited"
    monkeypatch.undo()
    infeasible = analyze_single_site(snapshot(s), 1.0)
    assert infeasible["status"] == "partial"
    assert infeasible["sites"][0]["status"] == "infeasible"


def test_nominal_ignores_stock_counts_but_does_not_reset_execution_facts(case):
    s = tiny(case)
    for drone in s["drones"]:
        drone["status"] = "unavailable"
    for battery in s["batteries"]:
        battery.update(status="unavailable", soh=0.5, soc=0.2)
    assert analyze_single_site(snapshot(s))["metrics"]["sortie_count"] == 2
    s["cargo_items"][0]["status"] = "loaded"
    result = analyze_single_site(snapshot(s))
    assert result["status"] == "limited" and result["metrics"] is None
    assert result["runtime_s"] > 0


@pytest.mark.parametrize("reserve", [math.nan, math.inf, -0.1, 1.1])
def test_invalid_diagnostic_reserve_is_rejected(case, reserve):
    with pytest.raises(ValueError, match="SOC"):
        analyze_single_site(case[0], reserve)
