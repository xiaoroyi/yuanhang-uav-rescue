"""Read-only, snapshot-bound resource and deadline diagnostics for a real Plan."""

from collections import defaultdict
import math

from solver.metrics import delivery_analysis
from solver.physics import charge_seconds
from solver.bounds import capacity_lower_bound


def interval_peak(intervals):
    events = []
    for start, end in intervals:
        if end > start:
            events.extend([(start, 1), (end, -1)])
    used = peak = 0
    for _, delta in sorted(events):
        used += delta
        peak = max(peak, used)
    return peak


def analyze(snapshot, plan):
    s = snapshot["scenario"]
    drones = {d["drone_id"]: d for d in s["drones"]}
    types = {t["type_id"]: t for t in s["drone_types"]}
    by_battery = defaultdict(list)
    charge_windows = []
    for r in plan["sorties"]:
        by_battery[r["battery_id"]].append(r)
        if r["battery_released_s"] > r["return_s"]:
            charge_windows.append(
                {
                    "battery_id": r["battery_id"],
                    "type_id": drones[r["drone_id"]]["type_id"],
                    "start_s": r.get("charge_start_s", r["return_s"]),
                    "end_s": r["battery_released_s"],
                    "is_initial": False,
                    "sortie_id": r["sortie_id"],
                }
            )
    for row in plan.get("initial_charges", []):
        b = next(b for b in s["batteries"] if b["battery_id"] == row["battery_id"])
        charge_windows.append(
            {
                "battery_id": row["battery_id"],
                "type_id": b["compatible_type_id"],
                "start_s": row["start_s"],
                "end_s": row["end_s"],
                "is_initial": True,
                "sortie_id": None,
            }
        )
    for row in plan.get("relay_sorties", []):
        charge_windows.append(
            {
                "battery_id": row["component_id"],
                "type_id": "R",
                "start_s": row["charge_start_s"],
                "end_s": row["component_released_s"],
                "is_initial": False,
                "sortie_id": row["relay_sortie_id"],
            }
        )
    for b in s["batteries"] if not s.get("resource_limits") else []:
        uses = sorted(by_battery[b["battery_id"]], key=lambda r: r["prepare_start_s"])
        if not uses:
            continue
        first = uses[0]
        capacity = b["capacity_kwh"] * b["soh"]
        departure = first["return_soc"] + first["energy_kwh"] / capacity
        if b["soc"] < 1 - 1e-9 and math.isclose(departure, 1.0, abs_tol=1e-7):
            charge_windows.append(
                {
                    "battery_id": b["battery_id"],
                    "type_id": b["compatible_type_id"],
                    "start_s": b["available_after_s"],
                    "end_s": b["available_after_s"]
                    + charge_seconds(types[b["compatible_type_id"]], b["soc"]),
                    "is_initial": True,
                    "sortie_id": None,
                }
            )
    resources = []
    for kind, records, id_key, type_key, release_key in [
        ("drone", s["drones"], "drone_id", "type_id", "drone_released_s"),
        (
            "battery",
            s["batteries"],
            "battery_id",
            "compatible_type_id",
            "battery_released_s",
        ),
    ]:
        horizon = max(
            [r[release_key] for r in plan["sorties"]]
            + [
                w["end_s"]
                for w in charge_windows
                if kind == "battery" and w["is_initial"]
            ],
            default=0,
        )
        for record in records:
            identity = record[id_key]
            uses = [r for r in plan["sorties"] if r[id_key] == identity]
            initial = sum(
                w["end_s"] - record["available_after_s"]
                for w in charge_windows
                if kind == "battery" and w["battery_id"] == identity and w["is_initial"]
            )
            occupied = (
                sum(r[release_key] - r["prepare_start_s"] for r in uses) + initial
            )
            resources.append(
                {
                    "kind": kind,
                    "resource_id": identity,
                    "type_id": record[type_key],
                    "sortie_count": len(uses),
                    "occupied_s": occupied,
                    "flight_s": sum(r["return_s"] - r["takeoff_s"] for r in uses),
                    "energy_kwh": sum(r["energy_kwh"] for r in uses),
                    "horizon_s": horizon,
                    "utilization": occupied / horizon if horizon else 0,
                }
            )
    by_type = {
        t["type_id"]: interval_peak(
            [
                (w["start_s"], w["end_s"])
                for w in charge_windows
                if w["type_id"] == t["type_id"]
            ]
        )
        for t in s["drone_types"]
    }
    if plan.get("relay_sorties"):
        by_type["R"] = interval_peak(
            [(w["start_s"], w["end_s"]) for w in charge_windows if w["type_id"] == "R"]
        )
        config = s["communication"]
        for kind, records, id_key, release_key in [
            ("relay_drone", config["relay_drones"], "drone_id", "drone_released_s"),
            (
                "relay_energy",
                config["relay_energy"],
                "component_id",
                "component_released_s",
            ),
        ]:
            horizon = max(r[release_key] for r in plan["relay_sorties"])
            for record in records:
                uses = [r for r in plan["relay_sorties"] if r[id_key] == record[id_key]]
                occupied = sum(r[release_key] - r["prepare_start_s"] for r in uses)
                resources.append(
                    {
                        "kind": kind,
                        "resource_id": record[id_key],
                        "type_id": "R",
                        "sortie_count": len(uses),
                        "occupied_s": occupied,
                        "flight_s": sum(
                            r["arrival_s"]
                            - r["takeoff_s"]
                            + r["return_s"]
                            - r["service_end_s"]
                            for r in uses
                        ),
                        "energy_kwh": sum(r["energy_kwh"] for r in uses),
                        "horizon_s": horizon,
                        "utilization": occupied / horizon if horizon else 0,
                    }
                )
    deliveries = delivery_analysis(s, plan)
    slacks = [
        d["hard_deadline_s"] - d["complete_s"]
        for d in deliveries["demands"]
        if d["hard_deadline_s"] is not None and d["complete_s"] is not None
    ]
    return {
        "plan_id": plan["plan_id"],
        "snapshot_id": snapshot["snapshot_id"],
        "scenario_state_version": snapshot["scenario_state_version"],
        "model_scope": plan["model_scope"],
        "capacity_bound": capacity_lower_bound(snapshot),
        "resource_limits": s.get("resource_limits"),
        "prep_peak": interval_peak(
            [
                (r["prepare_start_s"], r["takeoff_s"])
                for r in [*plan["sorties"], *plan.get("relay_sorties", [])]
            ]
        ),
        "charge_wait_s": sum(
            r.get("charge_start_s", r["return_s"]) - r["return_s"]
            for r in [*plan["sorties"], *plan.get("relay_sorties", [])]
        )
        + sum(
            row["start_s"]
            - next(
                b["available_after_s"]
                for b in s["batteries"]
                if b["battery_id"] == row["battery_id"]
            )
            for row in plan.get("initial_charges", [])
        ),
        "delivery": deliveries,
        "resources": resources,
        "charge_windows": sorted(
            charge_windows, key=lambda w: (w["start_s"], w["battery_id"])
        ),
        "charge_peak": interval_peak(
            [(w["start_s"], w["end_s"]) for w in charge_windows]
        ),
        "charge_peak_by_type": by_type,
        "min_hard_slack_s": min(slacks) if slacks else None,
        "notes": [
            "占用率按该类资源从场景零点至最后释放计，属于计划占用，不是设备实测统计。",
            (
                f"有限地面容量：{s['resource_limits']['prep_slots']}个准备工位、{s['resource_limits']['charging_ports']}个充电端口；初始补能和等待单独记录。"
                if s.get("resource_limits")
                else "充电峰值为现有无限端口模型的并发需求，不代表已考虑端口容量。"
            ),
            "期望截止允许延期；硬截止必须通过独立检查。",
            "初始充电仅在本次方案实际先补能时计入。",
        ],
    }
