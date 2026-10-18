"""Frozen event-time transport graph. Plan/sortie tuples never share a raw ID key."""

from collections import defaultdict, deque
import json

ROUTE_FIELDS = (
    "drone_id",
    "battery_id",
    "cargo_ids",
    "prepare_start_s",
    "takeoff_s",
    "return_s",
    "drone_released_s",
    "battery_released_s",
)


def node_id(plan_id, sortie_id):
    return json.dumps([plan_id, sortie_id], ensure_ascii=False, separators=(",", ":"))


def build_impact(sorties, direct_keys, started, tick, cursor, ground_model):
    """No time advancement or writes; direct_keys/started contain (plan, sortie)."""
    nodes = []
    groups = defaultdict(list)
    for r in sorted(
        sorties, key=lambda r: (r["prepare_start_s"], r["_plan_id"], r["sortie_id"])
    ):
        key = (r["_plan_id"], r["sortie_id"])
        n = {
            "node_id": node_id(*key),
            "plan_id": key[0],
            "sortie_id": key[1],
            **{k: r[k] for k in ROUTE_FIELDS},
            "direct": key in direct_keys,
            "affected": key in direct_keys,
            "committed": key in started,
        }
        nodes.append(n)
        for kind in ("drone", "battery"):
            groups[kind, r[kind + "_id"]].append(n)
    if len({n["node_id"] for n in nodes}) != len(nodes):
        raise ValueError("Duplicate plan/sortie in execution schedule")
    edges = []
    successors = defaultdict(set)
    for (kind, resource), rows in sorted(groups.items()):
        for a, b in zip(rows, rows[1:]):
            successors[a["node_id"]].add(b["node_id"])
            edges.append(
                {
                    "from_node_id": a["node_id"],
                    "to_node_id": b["node_id"],
                    "resource_kind": kind,
                    "resource_id": resource,
                }
            )
    affected = {n["node_id"] for n in nodes if n["direct"]}
    queue = deque(sorted(affected))
    while queue:
        for child in sorted(successors[queue.popleft()]):
            if child not in affected:
                affected.add(child)
                queue.append(child)
    for n in nodes:
        n["affected"] = n["node_id"] in affected
    return {
        "scope": "frozen_transport_resource_precedence",
        "time_s": tick,
        "facts_cursor": cursor,
        "ground_model": ground_model,
        "nodes": nodes,
        "edges": edges,
    }


def validate_frozen_impact(impact, event, plans, facts):
    """Rebuild edge/closure/commitment from original routes; no physics certification."""
    if (
        impact["time_s"] != event["time_s"]
        or impact["facts_cursor"] != event["facts_cursor"]
    ):
        raise ValueError("影响图时刻/事实游标与事件不符。")
    sorties = []
    direct = set()
    for n in impact["nodes"]:
        p = plans.get(n["plan_id"])
        r = (
            next((r for r in p["sorties"] if r["sortie_id"] == n["sortie_id"]), None)
            if p
            else None
        )
        if not r or any(n[k] != r[k] for k in ROUTE_FIELDS):
            raise ValueError("影响图节点与原始方案不符。")
        sorties.append({**r, "_plan_id": n["plan_id"]})
        if n["direct"]:
            direct.add((n["plan_id"], n["sortie_id"]))
    started = {
        (f["plan_id"], f["sortie_id"])
        for f in facts
        if f["kind"] == "loaded" and f["cursor"] <= event["facts_cursor"]
    }
    expected_direct = set()
    for r in sorties:
        kind = event["event_type"]
        hit = False
        if kind in ("drone.unavailable", "battery.unavailable"):
            hit = (
                r[kind.split(".")[0] + "_id"] == event["object_id"]
                and r["drone_released_s"] > event["time_s"]
            )
        elif kind == "site.unavailable":
            hit = (
                any(v["site_id"] == event["object_id"] for v in r["visits"])
                and r["drone_released_s"] > event["time_s"]
            )
        elif kind == "weather.changed":
            hit = (
                r["return_s"] > event["time_s"]
                and r["return_s"] > event["weather"]["valid_from_s"]
            )
        if hit:
            expected_direct.add((r["_plan_id"], r["sortie_id"]))
    if direct != expected_direct:
        raise ValueError("影响图直接命中与事件目标/时间不符。")
    rebuilt = build_impact(
        sorties,
        direct,
        started,
        event["time_s"],
        event["facts_cursor"],
        impact["ground_model"],
    )
    if rebuilt != impact:
        raise ValueError("影响图身份、资源后继、传播或承诺与冻结来源不符。")
