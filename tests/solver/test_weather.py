import copy

import pytest

from shared.contracts import ContractError, content_hash, validate_scenario
from solver.public_api import solve, validate
from solver.weather import type_checks


def manual_weather():
    rule = {
        "type_id": "B",
        "source_ref": "synthetic exercise rule; not a manufacturer limit",
        "max_wind_mps": 10.0,
        "max_gust_mps": None,
        "min_temperature_c": None,
        "max_temperature_c": None,
        "max_precipitation_mm_h": None,
    }
    return {
        "model_id": "manual_operating_window_v1",
        "weather_id": "WX-TEST",
        "source_kind": "manual_scenario",
        "source_ref": "synthetic uniform exercise",
        "issued_at": "2026-10-18T08:00:00+08:00",
        "valid_from_s": 600.0,
        "valid_until_s": 18000.0,
        "height_m": 10.0,
        "height_reference": "AGL",
        "wind_speed_mps": 5.0,
        "gust_mps": None,
        "wind_direction_from_deg": None,
        "temperature_c": None,
        "precipitation_mm_h": None,
        "rules": [rule],
    }


def small_case(case):
    snapshot, options = copy.deepcopy(case)
    s = snapshot["scenario"]
    s["cargo_items"] = s["cargo_items"][:2]
    ids = {c["demand_id"] for c in s["cargo_items"]}
    s["demands"] = [d for d in s["demands"] if d["demand_id"] in ids]
    for d in s["demands"]:
        d.update(
            required_quantity=sum(
                c["demand_id"] == d["demand_id"] for c in s["cargo_items"]
            ),
            hard_deadline_s=None,
            expected_deadline_s=None,
        )
    for c in s["cargo_items"]:
        c.update(mass_kg=1.0, volume_l=1.0)
    s["weather"] = manual_weather()
    snapshot["content_hash"] = content_hash(s)
    options["requested_model_scope"].append("weather_window")
    return snapshot, options


def test_weather_excludes_unqualified_types_and_schedules_inside_window(case):
    snapshot, options = small_case(case)
    before = copy.deepcopy(snapshot)
    checks = type_checks(snapshot["scenario"])
    assert {c["type_id"] for c in checks if c["allowed"]} == {"B"}
    outcome = solve(snapshot, options)
    assert outcome["plan"], outcome
    p = outcome["plan"]
    s = snapshot["scenario"]
    types = {d["drone_id"]: d["type_id"] for d in s["drones"]}
    assert all(
        types[r["drone_id"]] == "B"
        and r["prepare_start_s"] >= 600
        and r["return_s"] <= 18000
        for r in p["sorties"]
    )
    assert (
        "weather_window" in p["model_scope"]
        and validate(snapshot, p)["status"] == "passed"
    )
    assert snapshot == before
    unsafe = copy.deepcopy(snapshot)
    unsafe["scenario"]["weather"]["wind_speed_mps"] = 30
    unsafe["content_hash"] = content_hash(unsafe["scenario"])
    report = validate(unsafe, p)
    assert report["status"] == "failed" and any(
        c["code"] == "weather_window" and c["status"] == "failed"
        for c in report["checks"]
    )


def test_weather_unknown_input_and_too_short_window_do_not_publish_plan(case):
    snap, options = small_case(case)
    snap["scenario"]["weather"]["wind_speed_mps"] = None
    snap["content_hash"] = content_hash(snap["scenario"])
    out = solve(snap, options)
    assert (
        out["plan"] is None
        and out["solver_status"] == "UNKNOWN"
        and out["stop_reason"] == "input_not_ready"
    )
    snap, options = small_case(case)
    snap["scenario"]["weather"]["valid_until_s"] = 601
    snap["content_hash"] = content_hash(snap["scenario"])
    out = solve(snap, {**options, "time_limit_s": 1})
    assert out["plan"] is None and out["solver_status"] == "UNKNOWN"


def test_weather_contract_rejects_duplicate_rules_and_reversed_window(case):
    snap, options = small_case(case)
    weather = snap["scenario"]["weather"]
    weather["rules"].append(copy.deepcopy(weather["rules"][0]))
    with pytest.raises(ContractError):
        validate_scenario(snap["scenario"])
    weather["rules"].pop()
    weather["valid_until_s"] = weather["valid_from_s"]
    with pytest.raises(ContractError):
        validate_scenario(snap["scenario"])


def test_weather_combinations_are_explicitly_unsupported(case):
    snap, options = small_case(case)
    out = solve(snap, {**options, "mode": "improve"})
    assert out["plan"] is None and out["stop_reason"] == "unsupported_scope"
