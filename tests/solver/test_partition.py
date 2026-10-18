import copy
import json
from decimal import Decimal
from pathlib import Path

import pytest

from solver.partition import (
    audit_partition,
    color,
    connected_units,
    partition,
    partitions,
    peak,
    resource_classes,
    frozen_intervals,
)


@pytest.fixture(scope="module")
def frozen():
    root = Path(__file__).resolve().parents[2]
    source = json.loads(
        (root / "evidence/solver/joint-contest-recomputed.json").read_text(
            encoding="utf-8"
        )
    )
    snapshot, plan = source["snapshot"], source["outcome"]["plan"]
    before = copy.deepcopy((snapshot, plan))
    report = partition(snapshot, plan)
    assert report["status"] == "ready", report
    assert (snapshot, plan) == before
    return snapshot, plan, report


def test_original_frozen_joint_partition_preserves_tasks_and_counts(frozen):
    snapshot, plan, report = frozen
    assert len(report["atoms"]) == 3
    assert [(v["group_count"], v["candidate_count"]) for v in report["variants"]] == [
        (2, 3),
        (3, 1),
    ]
    assert report["snapshot_content_hash"] == snapshot["content_hash"]
    for variant in report["variants"]:
        for candidate in [variant["resource_first"], variant["balanced_first"]]:
            audit_partition(snapshot["scenario"], plan, candidate)
            assert sum(g["box_count"] for g in candidate["groups"]) == 80
            assert all(
                r["partition_required"] >= r["pooled_required"]
                for r in candidate["configuration"]
            )
    # Frozen task sharing is lost when groups must own their resources separately.
    two, three = [v["resource_first"] for v in report["variants"]]
    assert sum(r["extra_vs_pool"] for r in three["configuration"]) >= sum(
        r["extra_vs_pool"] for r in two["configuration"]
    )
    assert not two["fits_inventory"] and not three["fits_inventory"]


def test_half_open_decimal_resource_peaks_and_coloring_do_not_round_away_overlap():
    rows = [
        dict(task_id="T1", start=Decimal("0"), end=Decimal("0.1")),
        dict(task_id="T2", start=Decimal("0.1"), end=Decimal("0.2")),
    ]
    assert peak(rows)[0] == 1
    assert len({identity for _, identity in color(rows)}) == 1
    rows[1]["start"] = Decimal("0.0999999999999")
    assert peak(rows)[0] == 2
    assert len({identity for _, identity in color(rows)}) == 2


def test_ground_ports_exclude_waiting_but_energy_remains_occupied(frozen):
    snapshot, plan, _ = frozen
    s = copy.deepcopy(snapshot["scenario"])
    s["resource_limits"] = {"prep_slots": 1, "charging_ports": 1}
    route = copy.deepcopy(plan["sorties"][0])
    route.update(
        prepare_start_s=0,
        takeoff_s=10,
        return_s=100,
        drone_released_s=130,
        charge_start_s=150,
        battery_released_s=200,
    )
    rows = frozen_intervals(s, {"sorties": [route]})
    by_key = {row["resource_key"]: (row["start"], row["end"]) for row in rows}
    tid = next(d["type_id"] for d in s["drones"] if d["drone_id"] == route["drone_id"])
    assert by_key[f"drone:{tid}"] == (0, 130)
    assert by_key[f"battery:{tid}"] == (0, 200)
    assert by_key["prep:ground"] == (0, 10)
    assert by_key["charger:ground"] == (150, 200)


def test_connectivity_keeps_transport_and_shared_relay_clients_together():
    units = connected_units(
        ["S1", "S2", "S3", "S4"],
        [
            dict(site_ids=["S1", "S2"]),
            dict(site_ids=["S2", "S3"]),
        ],
    )
    assert units == [["S1", "S2", "S3"], ["S4"]]
    assert list(partitions(2, 3)) == []
    assert len(list(partitions(4, 2))) == 7
    assert len(list(partitions(4, 3))) == 6


@pytest.mark.parametrize(
    "mutation",
    [
        "missing_class",
        "interval",
        "duplicate_site",
        "allocation",
        "inventory",
        "witness",
        "workload",
    ],
)
def test_frozen_partition_audit_rejects_forged_evidence(frozen, mutation):
    snapshot, plan, report = frozen
    candidate = copy.deepcopy(report["variants"][1]["resource_first"])
    group = candidate["groups"][0]
    resource = next(
        r for g in candidate["groups"] for r in g["resources"] if r["assignments"]
    )
    if mutation == "missing_class":
        group["resources"].pop()
    elif mutation == "interval":
        resource["assignments"][0]["end_s"] += 1
    elif mutation == "duplicate_site":
        candidate["groups"][1]["site_ids"].append(group["site_ids"][0])
    elif mutation == "allocation":
        resource["assignments"][0]["allocated_resource_id"] = "INVENTED-STOCK"
    elif mutation == "inventory":
        candidate["configuration"][0]["inventory"] += 1
    elif mutation == "witness":
        resource["peak_task_ids"] = []
    else:
        group["workload_s"] = 0
    with pytest.raises(ValueError):
        audit_partition(snapshot["scenario"], plan, candidate)


@pytest.mark.parametrize(
    "field,value", [("soh", 0.9), ("soc", 0.8), ("available_after_s", 1)]
)
def test_heterogeneous_initial_energy_cannot_be_treated_as_identical_stock(
    frozen, field, value
):
    snapshot, _, _ = frozen
    s = copy.deepcopy(snapshot["scenario"])
    s["batteries"][0][field] = value
    classes, reason = resource_classes(s)
    assert classes == [] and reason
