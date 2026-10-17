"""Q1 nominal single-site capability and exact bounded count-pattern packing.

No physical entities, charging schedule, deadlines or radio claims are produced.
The archived Q1 method is adapted to current contracts without importing legacy
bootstrap/env. All costs and box identities are recomputed from the Snapshot.
"""

from collections import defaultdict
from decimal import Decimal, localcontext
import itertools
import hashlib
import math
import time

from shared.contracts import content_hash, has_execution_facts, validate_snapshot
from solver.errors import InputNotReady
from solver.physics import evaluate_route, leg, leg_values, parameters

MODEL = "single_site_nominal_transport_v1"
MAX_STATES = 512


def safe_capacity(s, typ, site, reserve):
    p = parameters(typ)
    outward = leg(s, typ, s["base"]["id"], site)
    backward = leg(s, typ, site, s["base"]["id"])
    reference = p["reference_energy_kwh"]
    limit = (1 - reserve) * reference

    def energy(payload):
        return leg_values(typ, outward, payload)[1] + leg_values(typ, backward, 0)[1]

    empty, full = energy(0), energy(typ["max_payload_kg"])
    row = dict(
        site_id=site,
        type_id=typ["type_id"],
        capacity_kg=None,
        max_volume_l=typ["max_volume_l"],
        nominal_energy_kwh=reference,
        allowed_energy_kwh=limit,
        empty_energy_kwh=empty,
        full_energy_kwh=full,
        roundtrip_distance_m=outward.distance_m + backward.distance_m,
        terrain_evaluated=outward.terrain_checked and backward.terrain_checked,
        limit="empty_infeasible",
        root_width_kg=None,
        residual_kwh=None,
        reason=None,
    )
    if empty > limit:
        return row
    lo, hi = 0.0, typ["max_payload_kg"]
    if full <= limit:
        lo, status = hi, "rated_payload"
    else:
        status = "energy"
        for _ in range(60):
            middle = (lo + hi) / 2
            if energy(middle) <= limit:
                lo = middle
            else:
                hi = middle
            if hi - lo <= 1e-7:
                break
    row.update(
        capacity_kg=lo,
        limit=status,
        root_width_kg=hi - lo,
        residual_kwh=limit - energy(lo),
    )
    return row


def _cost(pattern):
    return 1, Decimal(str(pattern["energy_kwh"])), Decimal(str(pattern["duration_s"]))


def count_dp(counts, patterns, reserve, deadline):
    """All count states, exact integer primary objective and decimal tie costs."""
    best_by_counts = {}
    for pattern in patterns:
        if pattern["return_soc"] < reserve - 1e-9:
            continue
        key = pattern["counts"]
        if key not in best_by_counts or _cost(pattern) < _cost(best_by_counts[key]):
            best_by_counts[key] = pattern
    library = sorted(
        best_by_counts.values(),
        key=lambda p: (-sum(p["counts"]), _cost(p), p["type_id"]),
    )
    zero = (0,) * len(counts)
    values, choices = {zero: (0, Decimal(0), Decimal(0))}, {}
    states = sorted(
        itertools.product(*(range(n + 1) for n in counts)), key=lambda a: (sum(a), a)
    )
    for remaining in states[1:]:
        if time.perf_counter() > deadline:
            raise TimeoutError("额定组批诊断达到有限计算预算。")
        focus = next(i for i, n in enumerate(remaining) if n)
        for pattern in library:
            vector = pattern["counts"]
            if not vector[focus] or any(a > b for a, b in zip(vector, remaining)):
                continue
            previous = tuple(b - a for a, b in zip(vector, remaining))
            if previous not in values:
                continue
            candidate = tuple(a + b for a, b in zip(values[previous], _cost(pattern)))
            if remaining not in values or candidate < values[remaining]:
                values[remaining], choices[remaining] = candidate, pattern
    state, selected = tuple(counts), []
    if state not in values:
        return None
    while any(state):
        pattern = choices[state]
        selected.append(pattern)
        state = tuple(a - b for a, b in zip(state, pattern["counts"]))
    return selected


def _summary(rows):
    return dict(
        sortie_count=len(rows),
        energy_kwh=math.fsum(row["energy_kwh"] for row in rows),
        operation_s=math.fsum(row["duration_s"] for row in rows),
        min_return_soc=min((row["return_soc"] for row in rows), default=None),
    )


def _assign(site, classes, selected):
    queues = [list(group) for group in classes]
    rows = []
    for pattern in selected:
        ids = []
        for i, amount in enumerate(pattern["counts"]):
            ids.extend(box["cargo_id"] for box in queues[i][:amount])
            queues[i] = queues[i][amount:]
        rows.append(
            dict(
                batch_id="NOM-"
                + hashlib.sha256(
                    f"{site}|{pattern['type_id']}|{'|'.join(sorted(ids))}".encode()
                ).hexdigest()[:12],
                site_id=site,
                type_id=pattern["type_id"],
                cargo_ids=ids,
                mass_kg=pattern["mass_kg"],
                volume_l=pattern["volume_l"],
                duration_s=pattern["duration_s"],
                energy_kwh=pattern["energy_kwh"],
                return_soc=pattern["return_soc"],
            )
        )
    if any(queues):
        raise ValueError("Nominal packing lost box identities.")
    return rows


def _baselines(counts, patterns, reserve):
    best = {}
    for pattern in patterns:
        if pattern["return_soc"] >= reserve - 1e-9:
            key = pattern["counts"]
            if key not in best or _cost(pattern) < _cost(best[key]):
                best[key] = pattern
    singles, bins = [], []
    for i, size in enumerate(counts):
        one = tuple(int(j == i) for j in range(len(counts)))
        if size and one not in best:
            return None, None
        for _ in range(size):
            singles.append(best[one])
            options = []
            for j, old in enumerate(bins):
                key = tuple(a + b for a, b in zip(old["counts"], one))
                if key in best:
                    new = best[key]
                    options.append((new["energy_kwh"] - old["energy_kwh"], j, new))
            if options:
                _, j, replacement = min(options, key=lambda r: (r[0], r[1]))
                bins[j] = replacement
            else:
                bins.append(best[one])
    while True:
        merges = []
        for i, j in itertools.combinations(range(len(bins)), 2):
            key = tuple(a + b for a, b in zip(bins[i]["counts"], bins[j]["counts"]))
            if key in best:
                replacement = best[key]
                merges.append(
                    (
                        replacement["energy_kwh"]
                        - bins[i]["energy_kwh"]
                        - bins[j]["energy_kwh"],
                        i,
                        j,
                        replacement,
                    )
                )
        if not merges:
            break
        _, i, j, replacement = min(merges, key=lambda r: r[:3])
        bins[i] = replacement
        bins.pop(j)
    return singles, bins


def validate_batches(s, batches, expected_ids, reserve):
    """Independent reconstruction, not evaluate_route or optimizer flags."""
    types = {t["type_id"]: t for t in s["drone_types"]}
    boxes = {b["cargo_id"]: b for b in s["cargo_items"]}
    demands = {d["demand_id"]: d for d in s["demands"]}
    ids = [cid for row in batches for cid in row["cargo_ids"]]
    if len(ids) != len(set(ids)) or set(ids) != set(expected_ids):
        raise ValueError("额定组批箱件重复、遗漏或新增。")
    for row in batches:
        typ = types[row["type_id"]]
        p = parameters(typ)
        items = [boxes[cid] for cid in row["cargo_ids"]]
        if any(
            c["status"] != "available" or c["location_id"] != s["base"]["id"]
            for c in items
        ):
            raise ValueError("额定组批不能重置实际箱件状态或位置。")
        mass, volume = math.fsum(c["mass_kg"] for c in items), math.fsum(
            c["volume_l"] for c in items
        )
        if mass > typ["max_payload_kg"] + 1e-8 or volume > typ["max_volume_l"] + 1e-8:
            raise ValueError("额定组批超过质量或体积限制。")
        if any(demands[c["demand_id"]]["site_id"] != row["site_id"] for c in items):
            raise ValueError("额定组批跨越多个站点。")
        outward = leg(s, typ, s["base"]["id"], row["site_id"])
        backward = leg(s, typ, row["site_id"], s["base"]["id"])
        out_time, out_energy = leg_values(typ, outward, mass)
        back_time, back_energy = leg_values(typ, backward, 0)
        energy = out_energy + back_energy
        soc = 1 - energy / p["reference_energy_kwh"]
        duration = (
            out_time
            + back_time
            + typ["prepare_duration_s"]
            + p["load_per_box_s"] * len(items)
            + typ["handover_fixed_s"]
            + typ["handover_per_box_s"] * len(items)
        )
        for key, value in [
            ("mass_kg", mass),
            ("volume_l", volume),
            ("energy_kwh", energy),
            ("duration_s", duration),
            ("return_soc", soc),
        ]:
            if not math.isclose(row[key], value, rel_tol=1e-9, abs_tol=1e-7):
                raise ValueError(f"额定组批{key}与独立重算不一致。")
        if soc < reserve - 1e-8:
            raise ValueError("额定组批不满足返航余量。")
    return [
        "箱件唯一与完整覆盖",
        "单站点归属",
        "质量与体积",
        "航段能耗与额定SOC",
        "累计作业时长",
        "当前地形与静态路径模型",
    ]


def analyze_single_site(snapshot, min_return_soc=None, time_limit_s=15):
    started = time.perf_counter()
    validate_snapshot(snapshot)
    s = snapshot["scenario"]
    reserve = (
        s["policy"]["min_return_soc"]
        if min_return_soc is None
        else float(min_return_soc)
    )
    if not math.isfinite(reserve) or not 0 <= reserve <= 1:
        raise ValueError("诊断返航SOC下限必须在0到1之间。")
    parameters_record = dict(
        min_return_soc=reserve,
        nominal_soc=1.0,
        nominal_soh=1.0,
        max_count_states_per_site=MAX_STATES,
        priority=["sortie_count", "energy_kwh", "operation_s"],
    )
    report = dict(
        model_id=MODEL,
        status="limited",
        reason=None,
        snapshot_id=snapshot["snapshot_id"],
        scenario_id=s["scenario_id"],
        scenario_state_version=s["state_version"],
        snapshot_content_hash=snapshot["content_hash"],
        required_box_count=sum(d["required_quantity"] for d in s["demands"]),
        available_box_count=sum(
            b["status"] == "available" and b["location_id"] == s["base"]["id"]
            for b in s["cargo_items"]
        ),
        parameters=parameters_record,
        analysis_input_hash=content_hash(
            dict(
                snapshot_content_hash=snapshot["content_hash"],
                model_id=MODEL,
                parameters=parameters_record,
            )
        ),
        capacities=[],
        sites=[],
        batches=[],
        metrics=None,
        single_box_baseline=None,
        greedy_baseline=None,
        sensitivity=[],
        audit_checks=[],
        runtime_s=0.0,
        notes=[
            "额定满电、SOH=100%的单点运输物理诊断，不是实际实体调度Plan。",
            "不考虑机体/电池数量、充电、并发、物资时限与通信；确认方案仍须正式求解。",
            "每批只服务一个站点；目标依次为最少架次、最小能耗、最小累计作业时长。",
            "体积约束单独参与整箱组批，不用未知密度换算最大安全质量。",
            "切换诊断余量不会修改场景策略；有限模型最少架次不代表多站调度全局最优。",
        ],
    )
    if (
        s["data_origin"] == "mock"
        or has_execution_facts(s)
        or not s["base"]["available"]
    ):
        report["reason"] = "当前额定诊断需要非Mock、尚未执行且基地可用的输入。"
        report["runtime_s"] = time.perf_counter() - started
        return report
    if s["policy"]["requires_terrain"] and s["terrain"]["status"] != "available":
        report["reason"] = "场景要求地形检查，但没有绑定可用DEM。"
        report["runtime_s"] = time.perf_counter() - started
        return report
    deadline = started + min(30, max(0.1, time_limit_s))
    by_demand = defaultdict(list)
    for box in s["cargo_items"]:
        if box["status"] == "available" and box["location_id"] == s["base"]["id"]:
            by_demand[box["demand_id"]].append(box)
    site_boxes, site_reasons = defaultdict(list), {}
    for demand in s["demands"]:
        if not demand["required_quantity"]:
            continue
        boxes = by_demand[demand["demand_id"]]
        if len(boxes) != demand["required_quantity"]:
            site_reasons[demand["site_id"]] = (
                "可用逐箱库存与需求数量不一致；当前精确组批不包含库存选择。"
            )
        site_boxes[demand["site_id"]].extend(boxes)
    prepared = []
    for site in s["sites"]:
        sid = site["id"]
        for typ in s["drone_types"]:
            try:
                if time.perf_counter() > deadline:
                    raise InputNotReady("额定诊断达到有限计算预算，本站能力尚未评估。")
                report["capacities"].append(safe_capacity(s, typ, sid, reserve))
            except InputNotReady as exc:
                report["capacities"].append(
                    dict(
                        site_id=sid,
                        type_id=typ["type_id"],
                        capacity_kg=None,
                        max_volume_l=typ["max_volume_l"],
                        nominal_energy_kwh=None,
                        allowed_energy_kwh=None,
                        empty_energy_kwh=None,
                        full_energy_kwh=None,
                        roundtrip_distance_m=None,
                        terrain_evaluated=False,
                        limit="unavailable",
                        root_width_kg=None,
                        residual_kwh=None,
                        reason=str(exc),
                    )
                )
        grouped = defaultdict(list)
        for box in site_boxes[sid]:
            grouped[box["type"], box["mass_kg"], box["volume_l"]].append(box)
        classes = [
            sorted(items, key=lambda b: b["cargo_id"])
            for _, items in sorted(grouped.items())
        ]
        counts = tuple(map(len, classes))
        states = math.prod(n + 1 for n in counts)
        reason = site_reasons.get(sid)
        if not site["available"]:
            reason = "站点当前不可用。"
        if states > MAX_STATES:
            reason = f"本站有{states}个计数状态，超过完整枚举上限{MAX_STATES}。"
        patterns = []
        if reason is None:
            try:
                for vector in itertools.product(*(range(n + 1) for n in counts)):
                    if not any(vector):
                        continue
                    if time.perf_counter() > deadline:
                        raise TimeoutError("额定组批诊断达到有限计算预算。")
                    ids = [
                        b["cargo_id"]
                        for group, amount in zip(classes, vector)
                        for b in group[:amount]
                    ]
                    for typ in s["drone_types"]:
                        route = evaluate_route(s, typ, [(sid, ids)])
                        if route is not None:
                            p = parameters(typ)
                            patterns.append(
                                dict(
                                    counts=vector,
                                    type_id=typ["type_id"],
                                    mass_kg=math.fsum(
                                        b["mass_kg"]
                                        for group, amount in zip(classes, vector)
                                        for b in group[:amount]
                                    ),
                                    volume_l=math.fsum(
                                        b["volume_l"]
                                        for group, amount in zip(classes, vector)
                                        for b in group[:amount]
                                    ),
                                    energy_kwh=route["energy_kwh"],
                                    duration_s=route["duration_s"],
                                    return_soc=1
                                    - route["energy_kwh"] / p["reference_energy_kwh"],
                                )
                            )
            except (InputNotReady, TimeoutError) as exc:
                reason = str(exc)
        prepared.append((sid, classes, counts, patterns, states, reason))

    def run_case(rho, include_rows=False):
        all_rows, all_single, all_greedy, site_rows = [], [], [], []
        complete = True
        for sid, classes, counts, patterns, states, reason in prepared:
            chosen, error = None, reason
            limited = reason is not None
            if error is None:
                try:
                    chosen = count_dp(counts, patterns, rho, deadline)
                    if chosen is None:
                        error = "完整有限单点模式中没有满足容量与额定余量的整箱组合。"
                except TimeoutError as exc:
                    error = str(exc)
                    limited = True
            if error:
                complete = False
                site_rows.append(
                    dict(
                        site_id=sid,
                        status="limited" if limited else "infeasible",
                        reason=error,
                        count_states=states,
                        box_count=sum(counts),
                        metrics=None,
                    )
                )
                continue
            rows = _assign(sid, classes, chosen)
            expected = [box["cargo_id"] for group in classes for box in group]
            validate_batches(s, rows, expected, rho)
            all_rows.extend(rows)
            single, greedy = _baselines(counts, patterns, rho)
            if single is None or greedy is None:
                raise ValueError("完整单点组批缺少可行的单箱基线，拒绝发布诊断。")
            validate_batches(s, _assign(sid, classes, single), expected, rho)
            validate_batches(s, _assign(sid, classes, greedy), expected, rho)
            all_single.extend(single)
            all_greedy.extend(greedy)
            site_rows.append(
                dict(
                    site_id=sid,
                    status="complete",
                    reason=None,
                    count_states=states,
                    box_count=sum(counts),
                    metrics=_summary(rows),
                )
            )
        result = dict(
            min_return_soc=rho,
            status="complete" if complete else "partial",
            metrics=_summary(all_rows) if complete else None,
        )
        if include_rows:
            result.update(
                batches=all_rows,
                sites=site_rows,
                single_box_baseline=_summary(all_single) if complete else None,
                greedy_baseline=_summary(all_greedy) if complete else None,
            )
        return result

    with localcontext() as context:
        context.prec = 50
        main = run_case(reserve, True)
        report.update(
            {
                k: main[k]
                for k in [
                    "status",
                    "metrics",
                    "batches",
                    "sites",
                    "single_box_baseline",
                    "greedy_baseline",
                ]
            }
        )
        for rho in sorted(
            {round(max(0, reserve - 0.1), 8), reserve, round(min(1, reserve + 0.1), 8)}
        ):
            report["sensitivity"].append(
                {k: main[k] for k in ("min_return_soc", "status", "metrics")}
                if rho == reserve
                else run_case(rho)
            )
    if report["status"] == "complete":
        expected = [b["cargo_id"] for items in site_boxes.values() for b in items]
        report["audit_checks"] = validate_batches(
            s, report["batches"], expected, reserve
        )
    else:
        report["reason"] = (
            "部分站点不满足当前有限组批模型条件，未发布完整场景最优性结论。"
        )
    report["runtime_s"] = time.perf_counter() - started
    return report


def main():
    """Reproducible offline diagnostic; importing this module has no side effects."""
    import argparse
    from datetime import datetime, timezone
    import json
    from pathlib import Path
    import uuid

    from solver.adapters.contest import compact_scenario, contest_scenario

    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--example", choices=["compact", "contest"])
    source.add_argument("--scenario", type=Path)
    parser.add_argument("--min-return-soc", type=float)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.scenario and args.scenario.resolve() == args.output.resolve():
        parser.error("输出路径不能覆盖输入场景。")
    s = (
        json.loads(args.scenario.read_text(encoding="utf-8"))
        if args.scenario
        else (contest_scenario if args.example == "contest" else compact_scenario)()
    )
    snapshot = dict(
        schema_version=s["schema_version"],
        snapshot_id="SNAP-NOM-" + uuid.uuid4().hex[:16].upper(),
        scenario_id=s["scenario_id"],
        scenario_state_version=s["state_version"],
        content_hash=content_hash(s),
        created_at=datetime.now(timezone.utc).isoformat(),
        scenario=s,
    )
    report = analyze_single_site(snapshot, args.min_return_soc)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(dict(snapshot=snapshot, report=report), ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": report["status"], "metrics": report["metrics"]}))


if __name__ == "__main__":
    main()
