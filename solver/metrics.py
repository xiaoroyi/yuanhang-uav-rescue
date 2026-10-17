"""Consistent objective scoring and read-only delivery analysis."""

import math


def delivery_analysis(scenario, plan):
    cargos = {c["cargo_id"]: c for c in scenario["cargo_items"]}
    deliveries = {
        c: v["delivery_complete_s"]
        for r in plan["sorties"]
        for v in r["visits"]
        for c in v["cargo_ids"]
    }
    demands = []
    for d in scenario["demands"]:
        times = [
            t
            for cid, t in deliveries.items()
            if cargos[cid]["demand_id"] == d["demand_id"]
        ]
        complete = max(times) if len(times) >= d["required_quantity"] else None
        expected = d["expected_deadline_s"]
        hard = d["hard_deadline_s"]
        demands.append(
            {
                "demand_id": d["demand_id"],
                "site_id": d["site_id"],
                "required_quantity": d["required_quantity"],
                "served_quantity": len(times),
                "complete_s": complete,
                "expected_deadline_s": expected,
                "hard_deadline_s": hard,
                "delay_s": (
                    max(0, complete - expected)
                    if complete is not None and expected is not None
                    else None
                ),
                "hard_satisfied": (
                    None
                    if hard is None
                    else complete is not None and complete <= hard + 1e-7
                ),
            }
        )
    by_id = {d["demand_id"]: d for d in scenario["demands"]}
    weighted = sum(
        max(
            0,
            t
            - (
                by_id[cargos[cid]["demand_id"]]["expected_deadline_s"]
                if by_id[cargos[cid]["demand_id"]]["expected_deadline_s"] is not None
                else math.inf
            ),
        )
        * by_id[cargos[cid]["demand_id"]]["priority"]
        for cid, t in deliveries.items()
    )
    return {
        "demands": demands,
        "weighted_box_delay_s": weighted,
        "late_demand_count": sum(
            d["delay_s"] is not None and d["delay_s"] > 1e-7 for d in demands
        ),
        "expected_demand_count": sum(
            d["expected_deadline_s"] is not None for d in demands
        ),
        "hard_violation_count": sum(d["hard_satisfied"] is False for d in demands),
    }


def objective_score(scenario, plan, objective):
    late = delivery_analysis(scenario, plan)["weighted_box_delay_s"]
    m = plan["metrics"]
    if objective == "energy":
        return late, m["energy_kwh"], m["makespan_s"]
    if objective == "balanced":
        return late, m["makespan_s"] + 300 * m["energy_kwh"], m["makespan_s"]
    return late, m["makespan_s"], m["energy_kwh"]
