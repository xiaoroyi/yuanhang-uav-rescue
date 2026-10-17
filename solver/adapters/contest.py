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


def contest_communication(scenario):
    """Opt-in original radio/relay inputs, read from the archived source tables."""
    values = {
        (r[0], r[3]): r[4]
        for r in rows("通信链路参数.xlsx")
        if len(r) > 4 and isinstance(r[4], (int, float))
    }
    relay_rows = rows("中继无人机数据.xlsx")
    r = next(r for r in relay_rows if r[0] == "R" and len(r) > 18 and r[4] == 23.5)
    count, full = next(
        (int(r[1]), float(r[2]))
        for r in relay_rows
        if r[0] == "R" and r[1:3] == [6, 1800]
    )

    def endpoint(name):
        return {
            "tx_power_dbm": float(values[name, "Pt"]),
            "gain_dbi": float(values[name, "G"]),
        }

    base = scenario["base"]
    stations = []
    for site in scenario["sites"]:
        for height in [150, 300]:
            stations.append(
                {
                    "station_id": f"RS-{site['id']}-{height}",
                    "coordinates": list(site["coordinates"]),
                    "agl_m": height,
                }
            )
        a, b = base["coordinates"], site["coordinates"]
        stations.append(
            {
                "station_id": f"RS-MID-{site['id']}",
                "coordinates": [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2],
                "agl_m": 300,
            }
        )
    stations.append(
        {
            "station_id": "RS-BASE-300",
            "coordinates": list(base["coordinates"]),
            "agl_m": 300,
        }
    )
    # Full original case also retains the three historical high-ground candidates.
    # These are coordinates/heights only; all links and flight physics are rebuilt.
    if {n["id"] for n in scenario["sites"]} == {f"S{i:03}" for i in range(1, 16)}:
        from solver.adapters.joint_patterns import archived_stations

        stations = [
            *archived_stations(), stations[-1],
            *[st for st in stations[:-1] if st["agl_m"] == 300],
            *[st for st in stations[:-1] if st["agl_m"] == 150],
        ]
    return {
        "model_id": "projected_dem_radio_v1",
        "frequency_mhz": float(values["传播参数", "f"]),
        "system_loss_db": float(values["传播参数", "Lsys"]),
        "obstruction_loss_db": float(values["传播参数", "Lobs"]),
        "sensitivity_dbm": float(values["接收参数", "Psens"]),
        "fading_margin_db": float(values["接收参数", "M"]),
        "gateway": {
            **endpoint("固定网关 G01"),
            "antenna_height_m": float(values["固定网关 G01", "hG"]),
        },
        "transport": endpoint("运输无人机"),
        "relay_access": endpoint("中继接入端"),
        "relay_backhaul": endpoint("中继回传端"),
        "relay_model": dict(
            zip(["mass_kg", "cruise_speed_mps", "cruise_power_kw"], map(float, r[4:7]))
        )
        | {
            "climb_speed_mps": float(r[12]),
            "descent_speed_mps": float(r[13]),
            "hover_power_kw": float(r[16]),
            "radio_power_kw": float(r[17]),
            "climb_efficiency": float(r[14]),
            "prepare_duration_s": float(r[9]),
            "link_duration_s": float(r[10]),
            "turnaround_duration_s": float(r[11]),
            "full_charge_s": full,
            "max_agl_m": float(r[18]),
            "min_return_soc": float(r[8]) / 100,
        },
        "relay_drones": [
            {
                "drone_id": f"R{i+1:02}",
                "status": "available",
                "location_id": base["id"],
                "available_after_s": 0,
            }
            for i in range(2)
        ],
        "relay_energy": [
            {
                "component_id": f"R-COMP-{i+1:02}",
                "capacity_kwh": float(r[7]),
                "soc": 1,
                "soh": 1,
                "status": "available",
                "location_id": base["id"],
                "available_after_s": 0,
            }
            for i in range(count)
        ],
        "candidate_stations": stations[:48],
    }


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
