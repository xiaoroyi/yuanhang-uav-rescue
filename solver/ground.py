"""Finite shared preparation and charging calendars; no database or execution facts."""

import random

from solver.physics import charge_seconds


def earliest_slot(start, duration, windows, capacity):
    if duration <= 0 or capacity is None:
        return start
    candidates = sorted({start, *[end for begin, end in windows if end >= start]})
    for candidate in candidates:
        finish = candidate + duration
        probes = {
            candidate,
            *[
                begin
                for begin, end in windows
                if candidate <= begin < finish and end > candidate
            ],
        }
        if all(
            sum(begin <= t < end for begin, end in windows) < capacity for t in probes
        ):
            return candidate
    raise ValueError("有限日历未找到可用的尾部时隙。")


def initial_schedule(s, seed, windows=(), start_floor=0):
    limits = s.get("resource_limits")
    if not limits:
        return [], {}
    types = {t["type_id"]: t for t in s["drone_types"]}
    active_types = {
        d["type_id"]
        for d in s["drones"]
        if d["status"] == "available" and d["location_id"] == s["base"]["id"]
    }
    batteries = [
        b
        for b in s["batteries"]
        if b["status"] in ["available", "charging"]
        and b["location_id"] == s["base"]["id"]
        and b["soh"] > 0
        and b["soc"] < 1
        and b["compatible_type_id"] in active_types
    ]
    if seed % 3 == 2:
        random.Random(seed).shuffle(batteries)
    batteries.sort(
        key=lambda b: (
            b["available_after_s"],
            (
                charge_seconds(types[b["compatible_type_id"]], b["soc"])
                if seed % 3 == 1
                else 0
            ),
        )
    )
    occupied = list(windows)
    result, ready = [], {}
    for b in batteries:
        duration = charge_seconds(types[b["compatible_type_id"]], b["soc"])
        start = earliest_slot(
            max(start_floor, b["available_after_s"]),
            duration,
            occupied,
            limits["charging_ports"],
        )
        end = start + duration
        result.append(
            {
                "battery_id": b["battery_id"],
                "start_s": start,
                "end_s": end,
                "from_soc": b["soc"],
                "to_soc": 1,
            }
        )
        occupied.append((start, end))
        ready[b["battery_id"]] = end
    return result, ready
