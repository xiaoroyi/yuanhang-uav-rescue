"""Exact, bounded partitioning of a frozen joint Plan; never reschedules tasks.

Decimal event times and Fraction ranking preserve the serialized input order.
The interval-graph resource theorem is used only for homogeneous full-SOC,
initially available resource classes. Every chosen partition is audited again.
"""

from collections import defaultdict
from decimal import Decimal
from fractions import Fraction
import heapq
import math

from shared.contracts import content_hash, has_execution_facts
from solver.validation import validate

MAX_ATOMS = 10


def dec(value):
    return Decimal(str(value))


def connected_units(site_ids, edges):
    """Union-find with a separate bipartite flood-fill agreement check."""
    parent = {site: site for site in site_ids}

    def root(site):
        while parent[site] != site:
            parent[site] = parent[parent[site]]
            site = parent[site]
        return site

    graph = defaultdict(set)
    for i, edge in enumerate(edges):
        members = edge["site_ids"]
        for site in members:
            parent[root(site)] = root(members[0])
            graph["site", site].add(("edge", i))
            graph["edge", i].add(("site", site))
    groups = defaultdict(list)
    for site in site_ids:
        groups[root(site)].append(site)
    groups = sorted(sorted(group) for group in groups.values())
    remaining, rebuilt = {("site", site) for site in site_ids}, []
    while remaining:
        reached, todo = set(), [min(remaining)]
        while todo:
            node = todo.pop()
            if node not in reached:
                reached.add(node)
                todo.extend(graph[node] - reached)
        sites = sorted(node[1] for node in reached if node[0] == "site")
        remaining -= reached
        rebuilt.append(sites)
    if sorted(rebuilt) != groups:
        raise ValueError("Frozen partition connectivity audit failed.")
    return groups


def peak(rows):
    events = []
    for row in rows:
        if row["end"] > row["start"]:
            events.extend(
                [(row["start"], 1, row["task_id"]), (row["end"], -1, row["task_id"])]
            )
    active, witness, at = set(), set(), None
    for instant, delta, identity in sorted(events):
        if delta < 0:
            active.remove(identity)
        else:
            active.add(identity)
        if len(active) > len(witness):
            witness, at = active.copy(), instant
    return len(witness), at, sorted(witness)


def color(rows):
    """Greedy interval coloring; equality releases before reallocation."""
    heap, count, result = [], 0, []
    for row in sorted(rows, key=lambda r: (r["start"], r["end"], r["task_id"])):
        if row["end"] <= row["start"]:
            continue
        if heap and heap[0][0] <= row["start"]:
            _, identity = heapq.heappop(heap)
        else:
            count += 1
            identity = count
        heapq.heappush(heap, (row["end"], identity))
        result.append((row, identity))
    if count != peak(rows)[0]:
        raise ValueError("Interval coloring disagrees with resource peak.")
    return result


def partitions(n, k):
    """Restricted-growth sequences enumerate each nonempty unlabeled partition."""
    if n < k:
        return

    def visit(sequence):
        if len(sequence) == n:
            if max(sequence) + 1 == k:
                yield [
                    sum(1 << i for i, group in enumerate(sequence) if group == g)
                    for g in range(k)
                ]
            return
        for group in range(min(k - 1, max(sequence) + 1) + 1):
            yield from visit([*sequence, group])

    yield from visit([0])


def resource_classes(s):
    classes = []
    for kind, records, identity_key, type_key, label in [
        ("drone", s["drones"], "drone_id", "type_id", "运输机"),
        ("battery", s["batteries"], "battery_id", "compatible_type_id", "运输电池"),
        ("relay_drone", s["communication"]["relay_drones"], "drone_id", None, "中继机"),
        (
            "relay_energy",
            s["communication"]["relay_energy"],
            "component_id",
            None,
            "中继能源",
        ),
    ]:
        tids = sorted({r[type_key] for r in records}) if type_key else ["R"]
        for tid in tids:
            available = [
                r
                for r in records
                if r["status"] == "available"
                and r["location_id"] == s["base"]["id"]
                and (type_key is None or r[type_key] == tid)
            ]
            if any(r["available_after_s"] != 0 for r in available):
                return (
                    [],
                    "资源存在非零初始可用时刻，当前分区峰值模型不能将其当成零时刻库存。",
                )
            if kind in ("battery", "relay_energy") and available:
                usable = available[0]["capacity_kwh"] * available[0]["soh"]
                if any(
                    r["soc"] < 1 - 1e-9
                    or r["soh"] <= 0
                    or not math.isclose(
                        r["capacity_kwh"] * r["soh"], usable, rel_tol=1e-9, abs_tol=1e-9
                    )
                    for r in available
                ):
                    return (
                        [],
                        "当前分区计数要求同类能源具有相同可用容量和初始满SOC，不能忽略异质健康度或初始补能。",
                    )
            classes.append(
                dict(
                    key=f"{kind}:{tid}",
                    kind=kind,
                    type_id=tid,
                    label=f"{tid}型{label}" if type_key else label,
                    inventory=len(available),
                    resource_ids=sorted(r[identity_key] for r in available),
                )
            )
    if s.get("resource_limits"):
        for kind, field, label in [
            ("prep", "prep_slots", "准备工位"),
            ("charger", "charging_ports", "充电端口"),
        ]:
            size = s["resource_limits"][field]
            classes.append(
                dict(
                    key=f"{kind}:ground",
                    kind=kind,
                    type_id="ground",
                    label=label,
                    inventory=size,
                    resource_ids=[f"{kind.upper()}-{i+1:02}" for i in range(size)],
                )
            )
    return classes, None


def frozen_intervals(s, plan):
    types = {d["drone_id"]: d["type_id"] for d in s["drones"]}
    rows = []

    def add(task, key, start, end, original):
        if dec(end) > dec(start):
            rows.append(
                dict(
                    task_id=task,
                    resource_key=key,
                    start=dec(start),
                    end=dec(end),
                    original_resource_id=original,
                )
            )

    for route in [*plan["sorties"], *plan.get("relay_sorties", [])]:
        relay = "relay_sortie_id" in route
        task = route["relay_sortie_id"] if relay else route["sortie_id"]
        tid = "R" if relay else types[route["drone_id"]]
        for key, end, identity in [
            (
                f"relay_drone:{tid}" if relay else f"drone:{tid}",
                "drone_released_s",
                "drone_id",
            ),
            (
                f"relay_energy:{tid}" if relay else f"battery:{tid}",
                "component_released_s" if relay else "battery_released_s",
                "component_id" if relay else "battery_id",
            ),
        ]:
            add(task, key, route["prepare_start_s"], route[end], route[identity])
        if s.get("resource_limits"):
            add(task, "prep:ground", route["prepare_start_s"], route["takeoff_s"], "")
            add(
                task,
                "charger:ground",
                route.get("charge_start_s", route["return_s"]),
                route["component_released_s" if relay else "battery_released_s"],
                "",
            )
    return rows


def partition(snapshot, plan):
    s = snapshot["scenario"]
    report = dict(
        model_id="frozen_joint_homogeneous_v1",
        status="limited",
        reason=None,
        plan_id=plan["plan_id"],
        snapshot_id=snapshot["snapshot_id"],
        scenario_state_version=snapshot["scenario_state_version"],
        snapshot_content_hash=snapshot["content_hash"],
        source_plan_hash=content_hash(plan),
        max_atoms=MAX_ATOMS,
        atoms=[],
        edges=[],
        resource_classes=[],
        pooled_requirements=[],
        variants=[],
        audit_checks=[],
        notes=[
            "固定任务、时刻、驻点和通信实际来源；只允许同质资源重新编号，各组不得共享实体。",
            "峰值与配置最优只针对冻结任务及有限分区，不是重新调度时最少资源。",
            "工作量为运输与中继从准备到返航的累计秒数，不包含充电和机体周转。",
        ],
    )

    def limited(reason):
        report["reason"] = reason
        return report

    if not s.get("communication") or "communication" not in plan["model_scope"]:
        return limited("需要先生成并验证包含连续通信范围的联合方案。")
    if has_execution_facts(s) or plan.get("initial_charges"):
        return limited("当前分区只支持未执行、无初始补能的同质资源场景。")
    if validate(snapshot, plan)["status"] != "passed":
        return limited("绑定快照上的联合方案未通过独立重算，已阻止分区。")
    classes, error = resource_classes(s)
    if error:
        return limited(error)
    report["resource_classes"] = [
        {key: value for key, value in row.items() if key != "resource_ids"}
        for row in classes
    ]
    routes = {r["sortie_id"]: r for r in plan["sorties"]}
    relays = {r["relay_sortie_id"]: r for r in plan.get("relay_sorties", [])}
    sites = {
        identity: sorted({v["site_id"] for v in row["visits"]})
        for identity, row in routes.items()
    }
    edges = [
        dict(kind="transport", task_id=identity, site_ids=members)
        for identity, members in sites.items()
    ]
    for identity in relays:
        clients = {
            w["sortie_id"]
            for w in plan["communication_report"]["windows"]
            if w["source"] == "relay" and w["relay_sortie_id"] == identity
        }
        if not clients:
            return limited(
                "存在没有实际保障对象的中继任务；其分组归属需要先明确，不能静默丢弃。"
            )
        members = sorted({site for task in clients for site in sites[task]})
        edges.append(dict(kind="relay", task_id=identity, site_ids=members))
    units = connected_units([n["id"] for n in s["sites"]], edges)
    report["edges"] = edges
    task_atom, atoms = {}, []
    for index, members in enumerate(units):
        tasks = {
            edge["task_id"] for edge in edges if set(edge["site_ids"]) <= set(members)
        }
        task_atom.update({task: index for task in tasks})
        atoms.append(
            dict(
                atom_id=f"C{index+1:02}",
                site_ids=members,
                transport_sortie_ids=sorted(tasks & routes.keys()),
                relay_sortie_ids=sorted(tasks & relays.keys()),
            )
        )
    report["atoms"] = atoms
    if len(atoms) > MAX_ATOMS:
        return limited(
            f"共有{len(atoms)}个不可拆分单元，超过当前完整枚举上限{MAX_ATOMS}；不代表不存在合法划分。"
        )
    intervals = frozen_intervals(s, plan)
    task_work = {
        identity: dec(row["return_s"]) - dec(row["prepare_start_s"])
        for identity, row in {**routes, **relays}.items()
    }
    subsets = {}
    for mask in range(1, 1 << len(atoms)):
        tasks = {task for task, index in task_atom.items() if mask & (1 << index)}
        by_resource = {
            c["key"]: [
                r
                for r in intervals
                if r["task_id"] in tasks and r["resource_key"] == c["key"]
            ]
            for c in classes
        }
        subsets[mask] = dict(
            tasks=tasks,
            rows=by_resource,
            counts=[peak(by_resource[c["key"]])[0] for c in classes],
            work=sum((task_work[t] for t in tasks), Decimal(0)),
        )
    all_mask = (1 << len(atoms)) - 1
    pooled = subsets[all_mask]["counts"]
    report["pooled_requirements"] = [
        dict(resource_key=c["key"], required_count=n) for c, n in zip(classes, pooled)
    ]
    stock = [c["inventory"] for c in classes]

    def objective(masks):
        total = [
            sum(subsets[mask]["counts"][i] for mask in masks)
            for i in range(len(classes))
        ]
        deficit = sum(
            (Fraction(max(0, n - size), max(1, size)) for n, size in zip(total, stock)),
            Fraction(),
        )
        scale = sum(
            (Fraction(n, max(1, size)) for n, size in zip(total, stock)), Fraction()
        )
        work = [Fraction(subsets[mask]["work"]) for mask in masks]
        cv2 = (
            len(masks) * sum(w * w for w in work) / sum(work) ** 2 - 1
            if sum(work)
            else Fraction()
        )
        return deficit, scale, cv2, tuple(masks)

    def materialize(masks):
        obj = objective(masks)
        groups, offsets = [], [0] * len(classes)
        for number, mask in enumerate(masks, 1):
            subset = subsets[mask]
            group = dict(
                group_id=f"K{len(masks)}-G{number}",
                atom_ids=[a["atom_id"] for i, a in enumerate(atoms) if mask & (1 << i)],
                site_ids=sorted(
                    site
                    for i, a in enumerate(atoms)
                    if mask & (1 << i)
                    for site in a["site_ids"]
                ),
                transport_sortie_ids=sorted(subset["tasks"] & routes.keys()),
                relay_sortie_ids=sorted(subset["tasks"] & relays.keys()),
                box_count=sum(
                    len(routes[t]["cargo_ids"]) for t in subset["tasks"] & routes.keys()
                ),
                workload_s=float(subset["work"]),
                resources=[],
            )
            for i, cls in enumerate(classes):
                rows = subset["rows"][cls["key"]]
                count, instant, witness = peak(rows)
                assigned = []
                for row, index in color(rows):
                    ordinal = offsets[i] + index
                    identity = (
                        cls["resource_ids"][ordinal - 1]
                        if ordinal <= cls["inventory"]
                        else f"ADD-{cls['key']}-{ordinal - cls['inventory']:02}"
                    )
                    assigned.append(
                        dict(
                            task_id=row["task_id"],
                            start_s=float(row["start"]),
                            end_s=float(row["end"]),
                            original_resource_id=row["original_resource_id"],
                            allocated_resource_id=identity,
                            needs_addition=ordinal > cls["inventory"],
                        )
                    )
                offsets[i] += count
                group["resources"].append(
                    dict(
                        resource_key=cls["key"],
                        required_count=count,
                        peak_at_s=float(instant) if instant is not None else None,
                        peak_task_ids=witness,
                        assignments=assigned,
                    )
                )
            groups.append(group)
        configuration = [
            dict(
                resource_key=c["key"],
                inventory=c["inventory"],
                pooled_required=pooled[i],
                partition_required=offsets[i],
                extra_vs_pool=offsets[i] - pooled[i],
                shortfall=max(0, offsets[i] - c["inventory"]),
                unallocated_stock=max(0, c["inventory"] - offsets[i]),
            )
            for i, c in enumerate(classes)
        ]
        result = dict(
            groups=groups,
            configuration=configuration,
            normalized_deficit=float(obj[0]),
            normalized_size=float(obj[1]),
            workload_cv2=float(obj[2]),
            objective_exact=dict(
                deficit=str(obj[0]), size=str(obj[1]), cv2=str(obj[2])
            ),
            fits_inventory=all(row["shortfall"] == 0 for row in configuration),
        )
        audit_partition(s, plan, result)
        return result

    for k in [2, 3]:
        count, resource_choice, balanced_choice = 0, None, None
        for masks in partitions(len(atoms), k):
            count += 1
            key = objective(masks)
            if resource_choice is None or key < resource_choice[0]:
                resource_choice = key, masks
            balance_key = key[2], key[0], key[1], key[3]
            if balanced_choice is None or balance_key < balanced_choice[0]:
                balanced_choice = balance_key, masks
        report["variants"].append(
            dict(
                group_count=k,
                candidate_count=count,
                status="available" if count else "not_possible",
                reason=(
                    None
                    if count
                    else "不可拆分单元少于要求组数，保持当前任务及通信关系时不能合法拆分。"
                ),
                resource_first=(
                    materialize(resource_choice[1]) if resource_choice else None
                ),
                balanced_first=(
                    materialize(balanced_choice[1]) if balanced_choice else None
                ),
            )
        )
    report.update(
        status="ready",
        audit_checks=[
            "联合方案独立重算",
            "并查集与二分图连通性一致",
            "站点和任务唯一归属",
            "通信实际来源不跨组",
            "冻结区间与峰值见证一致",
            "同质资源区间着色不重叠",
            "专用实体不跨组",
            "完整枚举与有理数字典序排序",
        ],
    )
    return report


def audit_partition(s, plan, result):
    """Check the emitted ownership and allocations independently of enumeration."""
    site_owner, task_owner = {}, {}
    expected_sites = {n["id"] for n in s["sites"]}
    tasks = {r["sortie_id"]: r for r in plan["sorties"]}
    relays = {r["relay_sortie_id"]: r for r in plan.get("relay_sorties", [])}
    intervals = frozen_intervals(s, plan)
    classes, error = resource_classes(s)
    if error:
        raise ValueError(error)
    class_by_key = {row["key"]: row for row in classes}
    owners, totals, audited_work = {}, defaultdict(int), []
    for group in result["groups"]:
        gid = group["group_id"]
        if not group["site_ids"]:
            raise ValueError("Partition group cannot be empty.")
        if (
            not set(group["transport_sortie_ids"]) <= tasks.keys()
            or not set(group["relay_sortie_ids"]) <= relays.keys()
            or len(group["resources"]) != len(classes)
            or {r["resource_key"] for r in group["resources"]} != class_by_key.keys()
        ):
            raise ValueError("Partition resource classes or task kinds changed.")
        for site in group["site_ids"]:
            if site in site_owner:
                raise ValueError("Partition repeats a site.")
            site_owner[site] = gid
        group_tasks = [*group["transport_sortie_ids"], *group["relay_sortie_ids"]]
        for task in group_tasks:
            if task in task_owner:
                raise ValueError("Partition repeats a task.")
            task_owner[task] = gid
        records = {**tasks, **relays}
        workload = sum(
            (
                dec(records[t]["return_s"]) - dec(records[t]["prepare_start_s"])
                for t in group_tasks
            ),
            Decimal(0),
        )
        audited_work.append(Fraction(workload))
        if group["workload_s"] != float(workload) or group["box_count"] != sum(
            len(tasks[t]["cargo_ids"]) for t in group["transport_sortie_ids"]
        ):
            raise ValueError("Partition workload or cargo count changed.")
        for resource in group["resources"]:
            key = resource["resource_key"]
            expected = [
                row
                for row in intervals
                if row["task_id"] in group_tasks and row["resource_key"] == key
            ]
            assignment = resource["assignments"]
            if sorted(
                (r["task_id"], r["start"], r["end"], r["original_resource_id"])
                for r in expected
            ) != sorted(
                (
                    r["task_id"],
                    dec(r["start_s"]),
                    dec(r["end_s"]),
                    r["original_resource_id"],
                )
                for r in assignment
            ):
                raise ValueError("Partition changed a frozen resource interval.")
            by_entity = defaultdict(list)
            for row in assignment:
                identity = key, row["allocated_resource_id"]
                from_stock = (
                    row["allocated_resource_id"] in class_by_key[key]["resource_ids"]
                )
                if row["needs_addition"] == from_stock or (
                    not from_stock
                    and not row["allocated_resource_id"].startswith(f"ADD-{key}-")
                ):
                    raise ValueError("Partition invents existing resource inventory.")
                if identity in owners and owners[identity] != gid:
                    raise ValueError("Dedicated resource crosses partition groups.")
                owners[identity] = gid
                by_entity[identity].append((dec(row["start_s"]), dec(row["end_s"])))
            for series in by_entity.values():
                series.sort()
                if any(a[1] > b[0] for a, b in zip(series, series[1:])):
                    raise ValueError("Partition allocation overlaps.")
            count, instant, witness = peak(expected)
            if count != len(by_entity) or count != resource["required_count"]:
                raise ValueError("Partition resource count is not the frozen peak.")
            if resource["peak_task_ids"] != witness or resource["peak_at_s"] != (
                float(instant) if instant is not None else None
            ):
                raise ValueError("Partition peak witness changed.")
            totals[key] += count
    if set(site_owner) != expected_sites or set(task_owner) != set(tasks) | set(relays):
        raise ValueError("Partition lost or invented sites/tasks.")
    for identity, row in tasks.items():
        if any(site_owner[v["site_id"]] != task_owner[identity] for v in row["visits"]):
            raise ValueError("Transport visit order crosses partition groups.")
    for window in plan["communication_report"]["windows"]:
        if (
            window["source"] == "relay"
            and task_owner[window["sortie_id"]] != task_owner[window["relay_sortie_id"]]
        ):
            raise ValueError("Frozen communication source crosses partition groups.")
    if (
        len(result["configuration"]) != len(classes)
        or {row["resource_key"] for row in result["configuration"]}
        != class_by_key.keys()
    ):
        raise ValueError("Partition configuration lost a resource class.")
    for row in result["configuration"]:
        key = row["resource_key"]
        inventory = class_by_key[key]["inventory"]
        pooled = peak([r for r in intervals if r["resource_key"] == key])[0]
        additions = len(
            {
                entity
                for (resource, entity) in owners
                if resource == key and entity not in class_by_key[key]["resource_ids"]
            }
        )
        if (
            row["partition_required"] != totals[key]
            or row["inventory"] != inventory
            or row["pooled_required"] != pooled
            or row["extra_vs_pool"] != totals[key] - pooled
            or row["extra_vs_pool"] < 0
            or row["shortfall"] != max(0, totals[key] - inventory)
            or row["unallocated_stock"] != max(0, inventory - totals[key])
            or additions != row["shortfall"]
        ):
            raise ValueError("Partition configuration total is inconsistent.")
    deficit = sum(
        (
            Fraction(max(0, totals[c["key"]] - c["inventory"]), max(1, c["inventory"]))
            for c in classes
        ),
        Fraction(),
    )
    size = sum(
        (Fraction(totals[c["key"]], max(1, c["inventory"])) for c in classes),
        Fraction(),
    )
    cv2 = (
        len(audited_work) * sum(w * w for w in audited_work) / sum(audited_work) ** 2
        - 1
        if sum(audited_work)
        else Fraction()
    )
    if (
        result["objective_exact"]
        != dict(deficit=str(deficit), size=str(size), cv2=str(cv2))
        or result["normalized_deficit"] != float(deficit)
        or result["normalized_size"] != float(size)
        or result["workload_cv2"] != float(cv2)
        or result["fits_inventory"] != (deficit == 0)
    ):
        raise ValueError("Partition objective or inventory verdict is inconsistent.")


def main():
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(description="冻结联合Plan的分区与资源配置")
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="含snapshot与outcome.plan的真实CLI结果JSON",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve():
        parser.error("输出不能覆盖原始联合方案输入。")
    source = json.loads(args.input.read_text(encoding="utf-8"))
    plan = source.get("outcome", {}).get("plan") or source.get("plan")
    if not plan or "snapshot" not in source:
        parser.error("输入没有绑定Snapshot与Plan，不能进行冻结分区。")
    result = partition(source["snapshot"], plan)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            dict(
                status=result["status"],
                reason=result["reason"],
                atoms=len(result["atoms"]),
                candidates={
                    v["group_count"]: v["candidate_count"] for v in result["variants"]
                },
            ),
            ensure_ascii=False,
        )
    )
    return 0 if result["status"] == "ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())
