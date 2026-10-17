"""Necessary transport-sortie capacity bound, not a minimum-fleet or feasibility claim."""

from collections import defaultdict
from fractions import Fraction
import math
import sys

from shared.contracts import has_execution_facts, validate_snapshot
from solver.numerics import CAPACITY_TOLERANCE

MODEL = "transport_capacity_relaxation_v1"


def capacity_divisor(rated):
    """Relax the fsum acceptance threshold by four representable values upward."""
    result = float(rated) + CAPACITY_TOLERANCE
    for _ in range(4):
        result = math.nextafter(result, math.inf)
    if not math.isfinite(result) or result <= 0:
        raise ValueError("容量边界不能在当前数值格式中保守表达。")
    return Fraction(result)


def _sum(values):
    # fsum, used by validation, consumes the same binary64 interpretation.
    return sum((Fraction(float(value)) for value in values), Fraction(0))


def capacity_lower_bound(snapshot):
    validate_snapshot(snapshot)
    s = snapshot["scenario"]
    quantity = sum(d["required_quantity"] for d in s["demands"])
    report = dict(
        model_id=MODEL,
        status="limited",
        reason=None,
        snapshot_id=snapshot["snapshot_id"],
        scenario_state_version=snapshot["scenario_state_version"],
        snapshot_content_hash=snapshot["content_hash"],
        required_box_count=quantity,
        eligible_type_ids=[],
        max_payload_kg=None,
        max_volume_l=None,
        mass_min_kg=None,
        volume_min_l=None,
        mass_bound=None,
        volume_bound=None,
        sortie_lower_bound=None,
        exact={},
        witnesses=[],
        numeric_policy="binary64_fsum_capacity_tol_1e-8_plus_4ulp",
        notes=[
            "完整服务运输架次数的质量/体积容量必要下界，不是机体或电池数量下界。",
            "按每项需求分别选最轻和最小体积的可用箱件，两套见证可以不同。",
            "使用可用机体与兼容可补能电池的机型上限；忽略能耗、时限、航路、并发与通信等限制。",
            "达到该下界也不证明完整调度最优或现实可执行，未达到不能单凭差值判断算法损失。",
        ],
    )
    if (
        s["data_origin"] == "mock"
        or has_execution_facts(s)
        or not s["base"]["available"]
    ):
        report["reason"] = "当前下界仅评估非Mock、基地可用且尚未执行的初始输入。"
        return report
    if (
        sys.float_info.radix != 2
        or sys.float_info.mant_dig != 53
        or sys.float_info.rounds != 1
    ):
        report["reason"] = "数值保护需要标准binary64、最近舍入环境。"
        return report
    base = s["base"]["id"]
    battery_types = {
        b["compatible_type_id"]
        for b in s["batteries"]
        if b["status"] in ("available", "charging")
        and b["location_id"] == base
        and b["capacity_kwh"] > 0
        and b["soh"] > 0
    }
    drone_types = {
        d["type_id"]
        for d in s["drones"]
        if d["status"] == "available" and d["location_id"] == base
    }
    eligible = [
        t for t in s["drone_types"] if t["type_id"] in battery_types & drone_types
    ]
    report["eligible_type_ids"] = sorted(t["type_id"] for t in eligible)
    if not eligible:
        report["reason"] = "没有初始可用机体与兼容能源组合，容量下界未评估。"
        return report
    report["max_payload_kg"] = max(t["max_payload_kg"] for t in eligible)
    report["max_volume_l"] = max(t["max_volume_l"] for t in eligible)
    stock = defaultdict(list)
    for box in s["cargo_items"]:
        if box["status"] == "available" and box["location_id"] == base:
            stock[box["demand_id"]].append(box)
    mass = volume = Fraction(0)
    try:
        for demand in s["demands"]:
            amount = demand["required_quantity"]
            if not amount:
                continue
            available = stock[demand["demand_id"]]
            if len(available) < amount:
                report["reason"] = (
                    f"{demand['demand_id']}的基地可用库存少于需求，未发布完整容量下界。"
                )
                return report
            lightest = sorted(
                available, key=lambda b: (float(b["mass_kg"]), b["cargo_id"])
            )[:amount]
            smallest = sorted(
                available, key=lambda b: (float(b["volume_l"]), b["cargo_id"])
            )[:amount]
            local_mass = _sum(b["mass_kg"] for b in lightest)
            local_volume = _sum(b["volume_l"] for b in smallest)
            mass += local_mass
            volume += local_volume
            report["witnesses"].append(
                dict(
                    demand_id=demand["demand_id"],
                    required_quantity=amount,
                    mass_min_kg=float(local_mass),
                    volume_min_l=float(local_volume),
                    mass_cargo_ids=[b["cargo_id"] for b in lightest],
                    volume_cargo_ids=[b["cargo_id"] for b in smallest],
                )
            )
        mass_divisor = max(capacity_divisor(t["max_payload_kg"]) for t in eligible)
        volume_divisor = max(capacity_divisor(t["max_volume_l"]) for t in eligible)
        mass_bound, volume_bound = math.ceil(mass / mass_divisor), math.ceil(
            volume / volume_divisor
        )
        mass_value, volume_value = float(mass), float(volume)
        if not math.isfinite(mass_value) or not math.isfinite(volume_value):
            raise ValueError("汇总规模超出当前有限数值表达。")
    except (ValueError, OverflowError) as exc:
        report["reason"] = str(exc)
        return report
    report.update(
        status="ready",
        mass_min_kg=mass_value,
        volume_min_l=volume_value,
        mass_bound=mass_bound,
        volume_bound=volume_bound,
        sortie_lower_bound=max(mass_bound, volume_bound),
        exact=dict(
            mass_sum=str(mass),
            volume_sum=str(volume),
            mass_divisor=str(mass_divisor),
            volume_divisor=str(volume_divisor),
            mass_ratio=str(mass / mass_divisor),
            volume_ratio=str(volume / volume_divisor),
        ),
    )
    return report


def main():
    import argparse
    from datetime import datetime, timezone
    import json
    from pathlib import Path
    import uuid
    from shared.contracts import content_hash, read_json
    from solver.adapters.contest import compact_scenario, contest_scenario

    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--example", choices=["compact", "contest"])
    source.add_argument("--scenario", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.scenario and args.scenario.resolve() == args.output.resolve():
        parser.error("输出路径不能覆盖输入场景。")
    s = (
        read_json(args.scenario)
        if args.scenario
        else (contest_scenario if args.example == "contest" else compact_scenario)()
    )
    snapshot = dict(
        schema_version=s["schema_version"],
        snapshot_id="SNAP-BOUND-" + uuid.uuid4().hex[:16].upper(),
        scenario_id=s["scenario_id"],
        scenario_state_version=s["state_version"],
        content_hash=content_hash(s),
        created_at=datetime.now(timezone.utc).isoformat(),
        scenario=s,
    )
    report = capacity_lower_bound(snapshot)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(dict(snapshot=snapshot, report=report), ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                key: report[key]
                for key in [
                    "status",
                    "mass_bound",
                    "volume_bound",
                    "sortie_lower_bound",
                ]
            }
        )
    )


if __name__ == "__main__":
    main()
