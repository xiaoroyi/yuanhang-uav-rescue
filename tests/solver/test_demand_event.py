import copy

import pytest

from shared.contracts import (
    ContractError,
    apply_event_to_scenario,
    content_hash,
    validate_event,
    validate_outcome,
)
from solver.public_api import replan, solve


def event_for(s, quantity=2):
    demand = dict(
        s["demands"][0],
        demand_id="URG-TEST",
        required_quantity=quantity,
        priority=7,
        mandatory=True,
        expected_deadline_s=5400,
        hard_deadline_s=18000,
    )
    return dict(
        schema_version=s["schema_version"],
        event_id="EVT-DEMAND-TEST",
        scenario_id=s["scenario_id"],
        expected_state_version=s["state_version"],
        event_type="demand.added",
        occurred_at=s["start_time"],
        received_at=s["start_time"],
        effective_time_s=0,
        actor="simulation",
        reason="New urgent stock at existing site",
        payload=dict(
            demand=demand,
            cargo_items=[
                dict(
                    s["cargo_items"][0],
                    cargo_id=f"URG-BOX-{i}",
                    demand_id=demand["demand_id"],
                    type=demand["cargo_type"],
                    mass_kg=3,
                    volume_l=12,
                    status="available",
                    location_id=s["base"]["id"],
                )
                for i in range(quantity)
            ],
        ),
    )


def prepared(case):
    snapshot, options = copy.deepcopy(case)
    old = solve(snapshot, options)["plan"]
    assert old
    event = event_for(snapshot["scenario"])
    s = apply_event_to_scenario(event, snapshot["scenario"])
    new = dict(
        snapshot,
        snapshot_id="SNAP-URG-2",
        scenario_state_version=2,
        content_hash=content_hash(s),
        scenario=s,
    )
    opts = dict(
        options,
        plan_id="PLAN-URG-2",
        snapshot_id=new["snapshot_id"],
        mode="replan",
        parent_plan_id=old["plan_id"],
        event_id=event["event_id"],
        time_limit_s=10,
    )
    return snapshot, old, event, new, opts


def test_urgent_event_preserves_original_records_and_full_replan_serves_new_inventory(
    case, monkeypatch
):
    original, old, event, snapshot, options = prepared(case)
    before = copy.deepcopy((original, old, event, snapshot, options))

    def no_local(*args, **kwargs):
        raise AssertionError("Added demand must not enter old-task-only local repair")

    monkeypatch.setattr("solver.public_api._try_local_repair", no_local)
    outcome = replan(snapshot, old, event, options)
    assert outcome["plan"], outcome
    validate_outcome(outcome, snapshot)
    plan = outcome["plan"]
    expected = {c["cargo_id"] for c in snapshot["scenario"]["cargo_items"]}
    assert {c for r in plan["sorties"] for c in r["cargo_ids"]} == expected
    assert (
        len(expected) == 34
        and plan["metrics"]["mandatory_total_count"]
        == old["metrics"]["mandatory_total_count"] + 1
    )
    assert (
        plan["parent_plan_id"] == old["plan_id"]
        and plan["event_id"] == event["event_id"]
    )
    expected_scene = copy.deepcopy(original["scenario"])
    expected_scene.update(state_version=2, data_origin="user_input")
    expected_scene["demands"].append(event["payload"]["demand"])
    expected_scene["cargo_items"].extend(event["payload"]["cargo_items"])
    assert snapshot["scenario"] == expected_scene
    assert (original, old, event, snapshot, options) == before


@pytest.mark.parametrize(
    "fault",
    [
        "demand_collision",
        "box_collision",
        "duplicate_box",
        "quantity",
        "type",
        "demand_ref",
        "site",
        "location",
        "box_status",
        "mandatory",
        "new_type",
        "deadlines",
        "too_many",
        "nonzero",
        "execution",
        "clock",
    ],
)
def test_invalid_insertions_are_rejected_without_mutating_scene_or_event(case, fault):
    s = copy.deepcopy(case[0]["scenario"])
    e = event_for(s)
    p = e["payload"]
    d = p["demand"]
    b = p["cargo_items"][0]
    if fault == "demand_collision":
        d["demand_id"] = s["demands"][0]["demand_id"]
    elif fault == "box_collision":
        b["cargo_id"] = s["cargo_items"][0]["cargo_id"]
    elif fault == "duplicate_box":
        p["cargo_items"][1]["cargo_id"] = b["cargo_id"]
    elif fault == "quantity":
        d["required_quantity"] = 1
    elif fault == "type":
        b["type"] = "MISMATCH"
    elif fault == "demand_ref":
        b["demand_id"] = s["demands"][0]["demand_id"]
    elif fault == "site":
        d["site_id"] = "MISSING"
    elif fault == "location":
        b["location_id"] = s["sites"][0]["id"]
    elif fault == "box_status":
        b["status"] = "loaded"
    elif fault == "mandatory":
        d["mandatory"] = False
    elif fault == "new_type":
        d["cargo_type"] = "UNREGISTERED"
        for box in p["cargo_items"]:
            box["type"] = "UNREGISTERED"
    elif fault == "deadlines":
        d.update(expected_deadline_s=20, hard_deadline_s=10)
    elif fault == "too_many":
        p["cargo_items"] = [dict(b, cargo_id=f"TOO-{i}") for i in range(33)]
        d["required_quantity"] = 33
    elif fault == "nonzero":
        e["effective_time_s"] = 1
    elif fault == "execution":
        s["batteries"][0]["status"] = "in_use"
    else:
        e["received_at"] = "2000-01-01T00:00:00Z"
    before = copy.deepcopy((s, e))
    with pytest.raises(ContractError):
        apply_event_to_scenario(e, s)
    assert (s, e) == before


@pytest.mark.parametrize(
    "fault", ["missing_box", "modified_box", "modified_demand", "event_payload"]
)
def test_applied_payload_corruption_is_rejected_before_any_solve(
    case, monkeypatch, fault
):
    _, old, event, snap, opts = prepared(case)
    if fault == "missing_box":
        snap["scenario"]["cargo_items"].pop()
    elif fault == "modified_box":
        snap["scenario"]["cargo_items"][-1]["mass_kg"] += 1
    elif fault == "modified_demand":
        snap["scenario"]["demands"][-1]["priority"] += 1
    else:
        event["payload"]["cargo_items"][0]["mass_kg"] += 1
    snap["content_hash"] = content_hash(snap["scenario"])

    def forbidden(*args, **kwargs):
        raise AssertionError("Malformed identity must not start computation")

    monkeypatch.setattr("solver.public_api.solve", forbidden)
    monkeypatch.setattr("solver.public_api._try_local_repair", forbidden)
    result = replan(snap, old, event, opts)
    assert result["plan"] is None and result["stop_reason"] == "input_not_ready"


def test_impossible_new_hard_deadline_does_not_republish_old_plan(case):
    _, old, event, snapshot, options = prepared(case)
    event["payload"]["demand"].update(expected_deadline_s=0, hard_deadline_s=0)
    snapshot["scenario"]["demands"][-1].update(expected_deadline_s=0, hard_deadline_s=0)
    snapshot["content_hash"] = content_hash(snapshot["scenario"])
    options["time_limit_s"] = 2
    before = copy.deepcopy(old)
    result = replan(snapshot, old, event, options)
    assert result["plan"] is None and result["solver_status"] == "UNKNOWN"
    assert old == before
