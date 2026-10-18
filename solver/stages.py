"""Phase projection from the validated contest physics; never changes a Plan."""

from dataclasses import replace
from math import isclose

from solver.physics import GEOD, leg, leg_values, parameters
from solver.errors import InputNotReady


def stage_analysis(snapshot, plan):
    s = snapshot["scenario"]
    types = {t["type_id"]: t for t in s["drone_types"]}
    drones = {d["drone_id"]: d for d in s["drones"]}
    batteries = {b["battery_id"]: b for b in s["batteries"]}
    cargo = {c["cargo_id"]: c for c in s["cargo_items"]}
    nodes = {n["id"]: n for n in [s["base"], *s["sites"]]}
    segments = []
    loads = []
    for r in plan["sorties"]:
        typ = types[drones[r["drone_id"]]["type_id"]]
        p = parameters(typ)
        b = batteries[r["battery_id"]]
        capacity = b["capacity_kwh"] * b["soh"]
        soc = r["return_soc"] + r["energy_kwh"] / capacity
        loaded = list(r["cargo_ids"])
        mass = sum(cargo[c]["mass_kg"] for c in loaded)
        volume = sum(cargo[c]["volume_l"] for c in loaded)
        loads.append(
            {
                "sortie_id": r["sortie_id"],
                "drone_id": r["drone_id"],
                "type_id": typ["type_id"],
                "cargo_count": len(loaded),
                "mass_kg": mass,
                "volume_l": volume,
                "max_payload_kg": typ["max_payload_kg"],
                "max_volume_l": typ["max_volume_l"],
                "mass_utilization": mass / typ["max_payload_kg"],
                "volume_utilization": volume / typ["max_volume_l"],
            }
        )
        current = s["base"]["id"]
        cursor = r["prepare_start_s"]

        def add(kind, end, a, z0, dest=None, z1=None, energy=0):
            nonlocal cursor, soc
            if end <= cursor + 1e-9:
                return
            payload = sum(cargo[c]["mass_kg"] for c in loaded)
            next_soc = soc - energy / capacity
            segments.append(
                {
                    "sortie_id": r["sortie_id"],
                    "drone_id": r["drone_id"],
                    "phase_id": f"{r['sortie_id']}:{len(segments)}",
                    "phase": kind,
                    "start_s": cursor,
                    "end_s": end,
                    "from_coordinates": list(a),
                    "to_coordinates": list(dest if dest is not None else a),
                    "start_elevation_m": z0,
                    "end_elevation_m": z1 if z1 is not None else z0,
                    "vertical_datum": s["terrain"].get("vertical_datum"),
                    "payload_kg": payload,
                    "energy_kwh": energy,
                    "soc_start": soc,
                    "soc_end": next_soc,
                    "cargo_ids": list(loaded),
                }
            )
            cursor, soc = end, next_soc

        add(
            "prepare",
            r["takeoff_s"],
            nodes[current]["coordinates"],
            nodes[current]["ground_elevation_m"],
        )
        for destination, ids, delivery_s in [
            *[
                (v["site_id"], v["cargo_ids"], v["delivery_complete_s"])
                for v in r["visits"]
            ],
            (s["base"]["id"], [], r["return_s"]),
        ]:
            geom = leg(s, typ, current, destination)
            payload = sum(cargo[c]["mass_kg"] for c in loaded)
            seconds, use = leg_values(typ, geom, payload)
            _, horizontal = leg_values(typ, replace(geom, climb_m=0), payload)
            scale = p.get("flight_time_scale", 1.0)
            a, dest = nodes[current], nodes[destination]
            work0 = a["ground_elevation_m"] + (
                0 if current == s["base"]["id"] else p.get("service_height_m", 30)
            )
            work1 = dest["ground_elevation_m"] + (
                0 if destination == s["base"]["id"] else p.get("service_height_m", 30)
            )
            start = cursor
            add(
                "climb",
                cursor + geom.climb_m / typ["climb_speed_mps"] * scale,
                a["coordinates"],
                work0,
                z1=geom.cruise_m,
                energy=use - horizontal,
            )
            for x, y in zip(geom.path, geom.path[1:]):
                distance = abs(GEOD.inv(*x, *y)[2])
                add(
                    "cruise",
                    cursor + distance / typ["cruise_speed_mps"] * scale,
                    x,
                    geom.cruise_m,
                    y,
                    geom.cruise_m,
                    horizontal * distance / geom.distance_m if geom.distance_m else 0,
                )
            add(
                "descent", start + seconds, dest["coordinates"], geom.cruise_m, z1=work1
            )
            if ids:
                handover = typ["handover_fixed_s"] + typ["handover_per_box_s"] * len(
                    ids
                )
                if not isclose(cursor + handover, delivery_s, abs_tol=1e-5):
                    raise InputNotReady("阶段时间与不可变 Plan 交付时刻不一致。")
                add("handover", delivery_s, dest["coordinates"], work1)
                loaded = [c for c in loaded if c not in ids]
            elif not isclose(cursor, r["return_s"], abs_tol=1e-5):
                raise InputNotReady("阶段返航时刻与 Plan 不一致。")
            current = destination
        if not isclose(soc, r["return_soc"], abs_tol=1e-7):
            raise InputNotReady("阶段能源合计与 Plan 不一致。")
        add(
            "turnaround",
            r["drone_released_s"],
            s["base"]["coordinates"],
            s["base"]["ground_elevation_m"],
        )
    return {
        "plan_id": plan["plan_id"],
        "snapshot_id": snapshot["snapshot_id"],
        "analysis_version": "stages-v1",
        "position_semantics": "model_phase_geodesic",
        "soc_semantics": "computed_phase_endpoints_only",
        "trajectory_segments": segments,
        "sortie_loads": loads,
    }


def position(segment, time_s):
    """Geodesic interpolation of position only. SOC is deliberately not interpolated."""
    ratio = min(
        1,
        max(0, (time_s - segment["start_s"]) / (segment["end_s"] - segment["start_s"])),
    )
    a, b = segment["from_coordinates"], segment["to_coordinates"]
    az, _, distance = GEOD.inv(*a, *b)
    lon, lat, _ = GEOD.fwd(*a, az, distance * ratio)
    z0, z1 = segment["start_elevation_m"], segment["end_elevation_m"]
    z = z0 + (z1 - z0) * ratio if z0 is not None and z1 is not None else None
    return [lon, lat], z
