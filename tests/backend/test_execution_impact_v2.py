"""Cross-plan IDs must never collapse dependency or commitment identity."""

import copy
import pytest
from backend.app.execution_impact import build_impact, validate_frozen_impact
from backend.app.operation_models import ExecutionImpact


def route(pid, sid, drone, battery, t):
    return {
        "_plan_id": pid,
        "sortie_id": sid,
        "drone_id": drone,
        "battery_id": battery,
        "cargo_ids": [pid + sid],
        "prepare_start_s": t,
        "takeoff_s": t + 10,
        "return_s": t + 20,
        "drone_released_s": t + 30,
        "battery_released_s": t + 40,
    }


def test_duplicate_sortie_ids_in_distinct_plans_keep_independent_closures_and_facts():
    sorties = [
        route("P1", "SAME", "D1", "B1", 0),
        route("P2", "SAME", "D2", "B2", 0),
        route("P1", "NEXT", "D1", "B3", 50),
        route("P2", "NEXT", "D2", "B4", 50),
    ]
    impact = build_impact(
        sorties, {("P1", "SAME")}, {("P2", "SAME")}, 2, 1, "unlimited"
    )
    ExecutionImpact.model_validate(impact)
    assert {
        (n["plan_id"], n["sortie_id"]) for n in impact["nodes"] if n["affected"]
    } == {("P1", "SAME"), ("P1", "NEXT")}
    assert {
        (n["plan_id"], n["sortie_id"]) for n in impact["nodes"] if n["committed"]
    } == {("P2", "SAME")}
    plans = {
        pid: {"sorties": [r for r in sorties if r["_plan_id"] == pid]}
        for pid in ("P1", "P2")
    }
    facts = [{"kind": "loaded", "plan_id": "P2", "sortie_id": "SAME", "cursor": 1}]
    event = {
        "time_s": 2,
        "facts_cursor": 1,
        "event_type": "battery.unavailable",
        "object_id": "B1",
    }
    validate_frozen_impact(impact, event, plans, facts)
    for mutation in ("identity", "propagation", "edge", "commitment", "route"):
        bad = copy.deepcopy(impact)
        if mutation == "identity":
            bad["nodes"][0]["node_id"] = "SAME"
        if mutation == "propagation":
            bad["nodes"][-1]["affected"] = True
        if mutation == "edge":
            bad["edges"] = []
        if mutation == "commitment":
            bad["nodes"][0]["committed"] = True
        if mutation == "route":
            bad["nodes"][0]["battery_id"] = "FORGED"
        with pytest.raises(ValueError):
            validate_frozen_impact(bad, event, plans, facts)


def test_shared_battery_propagates_between_drones_without_changing_direct_hits():
    sorties = [
        route("P1", "A", "D1", "B1", 0),
        route("P2", "B", "D2", "B1", 50),
        route("P2", "C", "D2", "B2", 100),
    ]
    impact = build_impact(
        sorties, {("P1", "A")}, set(), 0, 0, "conservative_common_release"
    )
    assert len([n for n in impact["nodes"] if n["affected"]]) == 3
    assert len([n for n in impact["nodes"] if n["direct"]]) == 1
    assert {e["resource_kind"] for e in impact["edges"]} == {"drone", "battery"}
    assert impact["ground_model"] == "conservative_common_release"
