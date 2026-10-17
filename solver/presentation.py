"""Read-only views of an already validated plan, with no execution side effects."""

from __future__ import annotations


def playback(plan, snapshot):
    """Expose planned phases. Coordinates between endpoints are schematic, not telemetry."""
    scenario = snapshot["scenario"]
    drones = {d["drone_id"]: d for d in scenario["drones"]}
    types = {t["type_id"]: t for t in scenario["drone_types"]}
    nodes = {n["id"]: n for n in [scenario["base"], *scenario["sites"]]}
    phases = []
    for sortie in plan["sorties"]:
        model = types[drones[sortie["drone_id"]]["type_id"]]
        current = scenario["base"]["coordinates"]
        cursor = sortie["takeoff_s"]

        def phase(kind, start, end, origin, destination):
            if end > start:
                phases.append(
                    {
                        "sortie_id": sortie["sortie_id"],
                        "drone_id": sortie["drone_id"],
                        "phase": kind,
                        "start_s": start,
                        "end_s": end,
                        "from_coordinates": origin,
                        "to_coordinates": destination,
                    }
                )

        phase("prepare", sortie["prepare_start_s"], cursor, current, current)
        for visit in sortie["visits"]:
            destination = nodes[visit["site_id"]]["coordinates"]
            handover = model["handover_fixed_s"] + model["handover_per_box_s"] * len(
                visit["cargo_ids"]
            )
            arrival = visit["delivery_complete_s"] - handover
            phase("flight", cursor, arrival, current, destination)
            phase(
                "handover",
                arrival,
                visit["delivery_complete_s"],
                destination,
                destination,
            )
            cursor, current = visit["delivery_complete_s"], destination
        phase(
            "return",
            cursor,
            sortie["return_s"],
            current,
            scenario["base"]["coordinates"],
        )
    return {
        "plan_id": plan["plan_id"],
        "snapshot_id": plan["snapshot_id"],
        "position_semantics": "schematic_linear_interpolation",
        "is_execution_fact": False,
        "phases": sorted(phases, key=lambda p: (p["start_s"], p["drone_id"])),
    }
