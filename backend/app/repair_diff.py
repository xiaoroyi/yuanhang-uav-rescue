"""Read-only differences against the frozen future, never a mutable current scenario."""

from shared.contracts import content_hash


def reference_sorties(reference):
    import json

    plans = {
        d["document_id"]: json.loads(d["payload_json"])
        for d in reference["documents"]
        if d["kind"] == "plan"
    }
    return [
        (part["plan_id"], route)
        for part in reference["future_parts"]
        for route in plans[part["plan_id"]]["sorties"]
        if route["sortie_id"] in part["sortie_ids"]
    ]


def compare_future(sources, candidate, committed):
    before = {
        cid: (pid, route, visit["delivery_complete_s"])
        for pid, route in sources
        for visit in route["visits"]
        for cid in visit["cargo_ids"]
    }
    rows = []
    for route in candidate["sorties"]:
        for visit in route["visits"]:
            for cid in visit["cargo_ids"]:
                old = before.get(cid)
                pid, previous, delivery = old if old else (None, None, None)
                drone_changed = (
                    previous["drone_id"] != route["drone_id"] if previous else None
                )
                battery_changed = (
                    previous["battery_id"] != route["battery_id"] if previous else None
                )
                takeoff_delta = (
                    route["takeoff_s"] - previous["takeoff_s"] if previous else None
                )
                delivery_delta = (
                    visit["delivery_complete_s"] - delivery if previous else None
                )
                unchanged = (
                    previous
                    and not drone_changed
                    and not battery_changed
                    and abs(takeoff_delta) <= 1e-6
                    and abs(delivery_delta) <= 1e-6
                )
                rows.append(
                    {
                        "cargo_id": cid,
                        "previous_plan_id": pid,
                        "previous_sortie_id": (
                            previous["sortie_id"] if previous else None
                        ),
                        "previous_drone_id": previous["drone_id"] if previous else None,
                        "previous_battery_id": (
                            previous["battery_id"] if previous else None
                        ),
                        "candidate_sortie_id": route["sortie_id"],
                        "candidate_drone_id": route["drone_id"],
                        "candidate_battery_id": route["battery_id"],
                        "change_kind": (
                            "new"
                            if previous is None
                            else "unchanged" if unchanged else "modified"
                        ),
                        "drone_changed": drone_changed,
                        "battery_changed": battery_changed,
                        "takeoff_delta_s": takeoff_delta,
                        "delivery_delta_s": delivery_delta,
                    }
                )
    hashes = {content_hash(route) for route in candidate["sorties"]}
    return {
        "committed_quantity": len(set(committed)),
        "retained_future_sortie_count": sum(
            content_hash(route) in hashes for _, route in sources
        ),
        "drone_reassigned_quantity": sum(r["drone_changed"] is True for r in rows),
        "battery_reassigned_quantity": sum(r["battery_changed"] is True for r in rows),
        "time_shifted_quantity": sum(
            r["takeoff_delta_s"] is not None
            and (abs(r["takeoff_delta_s"]) > 1e-6 or abs(r["delivery_delta_s"]) > 1e-6)
            for r in rows
        ),
        "unchanged_future_quantity": sum(r["change_kind"] == "unchanged" for r in rows),
        "new_quantity": sum(r["change_kind"] == "new" for r in rows),
        "rows": sorted(rows, key=lambda r: r["cargo_id"]),
    }
