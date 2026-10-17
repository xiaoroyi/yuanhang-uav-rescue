"""Read original contest Excel inputs and produce the common Scenario contract."""

from collections import Counter
from functools import lru_cache
import copy
import hashlib
from pathlib import Path

from openpyxl import load_workbook

from shared.contracts import validate_scenario

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "references/modeling/data"


def rows(filename, sheet="数据"):
    wb = load_workbook(DATA / "tables" / filename, read_only=True, data_only=True)
    try:
        return [list(r) for r in wb[sheet].values if any(x is not None for x in r)]
    finally:
        wb.close()


@lru_cache(maxsize=1)
def _source():
    locations = []
    for r in rows("调度中心与服务区.xlsx"):
        if r[0] == "O01" or (
            isinstance(r[0], str) and r[0].startswith("S") and r[0][1:].isdigit()
        ):
            locations.append(
                {
                    "id": r[0],
                    "name": r[1],
                    "coordinates": [float(r[2]), float(r[3])],
                    "ground_elevation_m": float(r[4]),
                    "available": True,
                }
            )
    raw_types = {}
    vehicle_rows = rows("运输无人机数据.xlsx")
    keys = [
        "m0",
        "Q",
        "V",
        "speed",
        "L0",
        "LF",
        "Euse",
        "rho_percent",
        "prep",
        "load",
        "handover",
        "handover_box",
        "up",
        "down",
        "eta",
        "down_eff",
    ]
    for r in vehicle_rows:
        if (
            r[0] in ("A", "B", "C")
            and r[0] not in raw_types
            and len(r) >= 18
            and isinstance(r[2], (int, float))
        ):
            raw_types[r[0]] = dict(zip(keys, r[2:18]))
    boxes = []
    demands = []
    for r in rows("物资需求与配送时限.xlsx", "逐箱货箱清单")[1:]:
        category = r[0].split("-")[1]
        # Per-box demand preserves original first-box/medical deadlines without losing quantities.
        did = "D-" + r[0]
        hard = r[6] if r[5] == "是" else None
        if category == "MED":
            hard = min(x for x in [hard, r[7]] if x is not None)
        demands.append(
            {
                "demand_id": did,
                "site_id": r[1],
                "cargo_type": category,
                "required_quantity": 1,
                "priority": int(r[8]),
                "expected_deadline_s": float(r[7]) if r[7] is not None else None,
                "hard_deadline_s": float(hard) if hard is not None else None,
                "mandatory": True,
            }
        )
        boxes.append(
            {
                "cargo_id": r[0],
                "demand_id": did,
                "type": category,
                "mass_kg": float(r[3]),
                "volume_l": float(r[4]) * 1000,
                "status": "available",
                "location_id": "O01",
            }
        )
    types = []
    # Original entity counts are explicit contest resources; fleet is editable after import.
    fleet_rows = [
        r
        for r in vehicle_rows
        if isinstance(r[0], str)
        and r[0].startswith("U")
        and r[0][1:].isdigit()
        and r[1] in raw_types
    ]
    battery_counts = {}
    charge_times = {}
    for r in vehicle_rows:
        if (
            r[0] in raw_types
            and len(r) > 2
            and isinstance(r[1], (int, float))
            and isinstance(r[2], (int, float))
        ):
            # Battery table rows use (type, count, full charge duration).
            if r[1] in (4, 5, 6) and r[2] > 100:
                charge_times[r[0]] = float(r[2])
                battery_counts[r[0]] = int(r[1])
    for name, m in raw_types.items():
        types.append(
            {
                "type_id": name,
                "max_payload_kg": float(m["Q"]),
                "max_volume_l": float(m["V"]) * 1000,
                "cruise_speed_mps": float(m["speed"]),
                "climb_speed_mps": float(m["up"]),
                "descent_speed_mps": float(m["down"]),
                "prepare_duration_s": float(m["prep"]),
                "turnaround_duration_s": 0.0,
                "handover_fixed_s": float(m["handover"]),
                "handover_per_box_s": float(m["handover_box"]),
                "empty_mass_kg": float(m["m0"]),
                "energy_model": {
                    "model_id": "contest_transport_v1",
                    "parameters": {
                        "empty_range_m": float(m["L0"]),
                        "full_range_m": float(m["LF"]),
                        "reference_energy_kwh": float(m["Euse"]),
                        "climb_efficiency": float(m["eta"]),
                        "load_per_box_s": float(m["load"]),
                        "service_height_m": 30,
                        "clearance_m": 50,
                        "energy_scale": 1,
                        "flight_time_scale": 1,
                    },
                },
                "charge_model": {
                    "model_id": "contest_two_stage_v1",
                    "parameters": {"full_charge_s": charge_times.get(name, 1800.0)},
                },
            }
        )
    drones = []
    batteries = []
    for r in fleet_rows:
        drones.append(
            {
                "drone_id": r[0],
                "type_id": r[1],
                "status": "available",
                "location_id": r[2],
                "available_after_s": 0,
            }
        )
    for name, count in battery_counts.items():
        capacity = raw_types[name]["Euse"]
        for j in range(count):
            batteries.append(
                {
                    "battery_id": f"BAT-{name}-{j+1:02}",
                    "compatible_type_id": name,
                    "capacity_kwh": float(capacity),
                    "soc": 1.0,
                    "soh": 1.0,
                    "status": "available",
                    "location_id": "O01",
                    "available_after_s": 0,
                }
            )
    dem = next((DATA / "terrain").glob("*DEM.mat"))
    scenario = {
        "schema_version": "0.1.0-draft",
        "scenario_id": "SCN-CONTEST-001",
        "name": "镇龙乡 · 原题运输基准",
        "state_version": 1,
        "mode": "simulation",
        "data_origin": "verified_dataset",
        "start_time": "2026-10-17T08:00:00+08:00",
        "timezone": "Asia/Shanghai",
        "coordinate_system": "EPSG:4326",
        "terrain": {
            "status": "available",
            "asset_id": "contest-dem-30m",
            "sha256": hashlib.sha256(dem.read_bytes()).hexdigest(),
            "horizontal_crs": "EPSG:4326",
            "vertical_datum": "contest_provided_elevation_reference",
        },
        "base": next(n for n in locations if n["id"] == "O01"),
        "sites": [n for n in locations if n["id"] != "O01"],
        "demands": demands,
        "cargo_items": boxes,
        "drone_types": types,
        "drones": drones,
        "batteries": batteries,
        "policy": {
            "min_return_soc": 0.2,
            "requires_terrain": True,
            "requires_communication": False,
            "delivery_time_policy": "station_end",
            "cost_model_available": False,
        },
    }
    validate_scenario(scenario)
    return scenario


def contest_scenario():
    return copy.deepcopy(_source())


def compact_scenario():
    """A declared subset of real contest inputs, not an invented success plan."""
    s = contest_scenario()
    s.update(scenario_id="SCN-EXERCISE-001", name="镇龙乡 · 应急运输演练")
    from pyproj import Geod

    geod = Geod(ellps="WGS84")
    sites = sorted(
        s["sites"],
        key=lambda n: geod.inv(*s["base"]["coordinates"], *n["coordinates"])[2],
    )[:5]
    allowed = {n["id"] for n in sites}
    s["sites"] = sites
    demands = [d for d in s["demands"] if d["site_id"] in allowed]
    # Keep all actual boxes at the five nearest sites and retain their original deadlines.
    s["demands"] = demands
    ids = {d["demand_id"] for d in demands}
    s["cargo_items"] = [c for c in s["cargo_items"] if c["demand_id"] in ids]
    s["drones"] = [d for d in s["drones"] if d["drone_id"] in ("U01", "U05", "U07")]
    s["batteries"] = [
        b for b in s["batteries"] if b["battery_id"].endswith(("01", "02"))
    ]
    validate_scenario(s)
    return s
