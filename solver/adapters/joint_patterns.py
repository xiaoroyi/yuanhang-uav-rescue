"""Archived grouping candidates, always evaluated against the current Scenario.

The asset contains box grouping, visit order and candidate coordinates only.
It contains no historical schedules, energy, SOC or validation flags. These
private patterns are never a publishable Plan until joint CP and validation.
"""

import copy
import json
from functools import lru_cache
from pathlib import Path

from solver.errors import InputNotReady
from solver.physics import charge_seconds, evaluate_route


@lru_cache(maxsize=1)
def _data():
    return json.loads(
        (
            Path(__file__).resolve().parents[1] / "data/contest_joint_patterns.json"
        ).read_text(encoding="utf-8")
    )


def archived_stations():
    return copy.deepcopy(_data()["stations"])


def transport_pattern(s, required_cargo_ids):
    """Return a private fixed grouping only when it matches current whole boxes."""
    data = _data()
    expected = [
        cid for p in data["patterns"] for v in p["stops"] for cid in v["cargo_ids"]
    ]
    if len(expected) != len(set(expected)) or set(expected) != set(required_cargo_ids):
        return None
    stations = {p["station_id"] for p in data["stations"]}
    if not stations <= {
        p["station_id"] for p in s["communication"]["candidate_stations"]
    }:
        return None
    types = {t["type_id"]: t for t in s["drone_types"]}
    demands = {d["demand_id"]: d for d in s["demands"]}
    cargos = {b["cargo_id"]: b for b in s["cargo_items"]}
    available_sites = {n["id"] for n in s["sites"] if n["available"]}
    routes = []
    for pattern in data["patterns"]:
        tid = pattern["type_id"]
        vehicles = [
            d
            for d in s["drones"]
            if d["type_id"] == tid
            and d["status"] == "available"
            and d["location_id"] == s["base"]["id"]
        ]
        batteries = [
            b
            for b in s["batteries"]
            if b["compatible_type_id"] == tid
            and b["status"] == "available"
            and b["location_id"] == s["base"]["id"]
            and b["soc"] >= 1 - 1e-9
            and b["soh"] > 0
        ]
        if tid not in types or not vehicles or not batteries:
            return None
        stops = [(v["site_id"], v["cargo_ids"]) for v in pattern["stops"]]
        if any(
            site not in available_sites
            or any(
                cargos[cid]["status"] != "available"
                or cargos[cid]["location_id"] != s["base"]["id"]
                or demands[cargos[cid]["demand_id"]]["site_id"] != site
                for cid in ids
            )
            for site, ids in stops
        ):
            return None
        try:
            route = evaluate_route(s, types[tid], stops)
        except InputNotReady:
            return None
        if route is None:
            return None
        battery = max(batteries, key=lambda b: b["capacity_kwh"] * b["soh"])
        soc = 1 - route["energy_kwh"] / (battery["capacity_kwh"] * battery["soh"])
        if soc < s["policy"]["min_return_soc"] - 1e-9:
            return None
        routes.append(
            {
                "sortie_id": pattern["pattern_id"],
                "kind": "transport",
                "drone_id": vehicles[0]["drone_id"],
                "battery_id": battery["battery_id"],
                "cargo_ids": route["cargo_ids"],
                "visits": route["visits"],
                "route_geometry": route["route_geometry"],
                "prepare_start_s": 0,
                "takeoff_s": route["prepare_s"],
                "return_s": route["duration_s"],
                "drone_released_s": route["duration_s"]
                + types[tid]["turnaround_duration_s"],
                "battery_released_s": route["duration_s"]
                + charge_seconds(types[tid], soc),
                "energy_kwh": route["energy_kwh"],
                "return_soc": soc,
                "terrain_status": (
                    "passed"
                    if s["terrain"]["status"] == "available"
                    else "not_evaluated"
                ),
                "communication_status": "not_evaluated",
            }
        )
    return {
        "sorties": routes,
        "pattern_only": True,
        "source": "archived_grouping_recomputed",
    }, stations
