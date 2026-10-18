import copy

import pytest

from shared.contracts import content_hash, validate_event, validate_outcome
from solver.public_api import replan, solve, validate


def battery_event(scenario, battery_id, expected_version=1):
    return dict(
        schema_version=scenario["schema_version"],
        event_id="EVT-BATTERY-TEST",
        scenario_id=scenario["scenario_id"],
        expected_state_version=expected_version,
        event_type="battery.unavailable",
        occurred_at=scenario["start_time"],
        received_at=scenario["start_time"],
        effective_time_s=0,
        actor="simulation",
        reason="Transport battery withdrawal",
        payload={"battery_id": battery_id},
    )


def prepare(case):
    snap, options = copy.deepcopy(case)
    for demand in snap["scenario"]["demands"]:
        demand.update(expected_deadline_s=None, hard_deadline_s=None)
    snap["content_hash"] = content_hash(snap["scenario"])
    old = solve(snap, options)["plan"]
    assert old
    failed = old["sorties"][0]["battery_id"]
    event = battery_event(snap["scenario"], failed)
    validate_event(event, snap["scenario"])
    next(b for b in snap["scenario"]["batteries"] if b["battery_id"] == failed)[
        "status"
    ] = "unavailable"
    snap["scenario"]["state_version"] = 2
    snap.update(
        snapshot_id="SNAP-BATTERY-2",
        scenario_state_version=2,
        content_hash=content_hash(snap["scenario"]),
    )
    options.update(
        mode="replan",
        plan_id="PLAN-BATTERY-2",
        snapshot_id=snap["snapshot_id"],
        parent_plan_id=old["plan_id"],
        event_id=event["event_id"],
        time_limit_s=10,
    )
    return snap, old, event, options, failed


def test_battery_withdrawal_recomputes_and_preserves_valid_unaffected_reservations(
    case,
):
    snap, old, event, options, failed = prepare(case)
    before = copy.deepcopy((snap, old, event, options))
    outcome = replan(snap, old, event, options)
    assert outcome["plan"], outcome
    validate_outcome(outcome, snap)
    plan = outcome["plan"]
    assert all(r["battery_id"] != failed for r in plan["sorties"])
    assert {c for r in plan["sorties"] for c in r["cargo_ids"]} == {
        c for r in old["sorties"] for c in r["cargo_ids"]
    }
    assert set(plan["change_summary"]["preserved_sortie_ids"])
    assert any("依赖图局部修复" in note for note in plan["solver_notes"])
    assert (snap, old, event, options) == before
    corrupted = copy.deepcopy(plan)
    replacement = next(
        r
        for r in corrupted["sorties"]
        if r["drone_id"] == old["sorties"][0]["drone_id"]
    )
    replacement["battery_id"] = failed
    assert validate(snap, corrupted)["status"] == "failed"


def test_malformed_applied_event_chain_is_rejected_before_any_repair_or_solve(
    case, monkeypatch
):
    snap, old, event, options, failed = prepare(case)
    variants = []
    variants.append((dict(event, scenario_id="SCN-OTHER"), snap, old, options))
    variants.append((dict(event, expected_state_version=2), snap, old, options))
    variants.append((dict(event, effective_time_s=1), snap, old, options))
    variants.append(
        (
            dict(event, payload={"drone_id": old["sorties"][0]["drone_id"]}),
            snap,
            old,
            options,
        )
    )
    variants.append(
        (dict(event, received_at="2000-01-01T00:00:00Z"), snap, old, options)
    )
    other = next(
        b["battery_id"]
        for b in snap["scenario"]["batteries"]
        if b["battery_id"] != failed
    )
    variants.append((dict(event, payload={"battery_id": other}), snap, old, options))
    variants.append((event, snap, dict(old, data_origin="mock"), options))
    variants.append((event, snap, old, dict(options, parent_plan_id="PLAN-WRONG")))
    variants.append((event, dict(snap, content_hash="0" * 64), old, options))
    with_facts = copy.deepcopy(snap)
    next(b for b in with_facts["scenario"]["batteries"] if b["battery_id"] != failed)[
        "status"
    ] = "in_use"
    with_facts["content_hash"] = content_hash(with_facts["scenario"])
    variants.append((event, with_facts, old, options))

    def forbidden(*args, **kwargs):
        pytest.fail("An invalid event reached computation.")

    monkeypatch.setattr("solver.public_api._try_local_repair", forbidden)
    monkeypatch.setattr("solver.public_api.solve", forbidden)
    for bad_event, bad_snap, bad_old, bad_options in variants:
        outcome = replan(bad_snap, bad_old, bad_event, bad_options)
        assert outcome["plan"] is None and outcome["solver_status"] == "UNKNOWN"
        assert outcome["stop_reason"] == "input_not_ready"
