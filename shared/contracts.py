"""G0 structural/semantic checks, not an independent physical flight validator."""

from __future__ import annotations

from collections import Counter
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import re
import sys

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from shared.geometry import valid_ring

ROOT = Path(__file__).resolve().parents[1]
FORMAT = FormatChecker()


@FORMAT.checks("date-time")
def aware_datetime(value):
    if not isinstance(value, str):
        return True
    if not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})", value
    ):
        return False
    try:
        return (
            datetime.fromisoformat(value.replace("Z", "+00:00")).utcoffset() is not None
        )
    except ValueError:
        return False


class ContractError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ContractError(message)


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path):
    def reject(value):
        raise ContractError(f"non-finite JSON: {value}")

    return json.loads(
        Path(path).read_text(encoding="utf-8"),
        object_pairs_hook=unique_pairs,
        parse_constant=reject,
    )


def content_hash(scenario):
    payload = json.dumps(
        scenario,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


SCHEMAS = {
    p.name.removesuffix(".schema.json"): read_json(p)
    for p in (ROOT / "contracts").glob("*.schema.json")
}
REGISTRY = Registry().with_resources(
    (s["$id"], Resource.from_contents(s)) for s in SCHEMAS.values()
)


def finite_json(value, path="$"):
    if isinstance(value, float):
        require(math.isfinite(value), f"non-finite JSON number at {path}")
    elif isinstance(value, dict):
        for key, child in value.items():
            finite_json(child, path + "." + str(key))
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            finite_json(child, f"{path}[{index}]")


def validate_schema(name, data):
    finite_json(data)
    errors = sorted(
        Draft202012Validator(
            SCHEMAS[name], registry=REGISTRY, format_checker=FORMAT
        ).iter_errors(data),
        key=lambda e: str(list(e.path)),
    )
    require(
        not errors,
        f"{name}: " + "; ".join(f"{list(e.path)} {e.message}" for e in errors[:4]),
    )


def index(items, key):
    ids = [item[key] for item in items]
    require(len(ids) == len(set(ids)), f"duplicate {key}")
    return dict(zip(ids, items))


def validate_scenario(s):
    validate_schema("scenario", s)
    locations = index([s["base"], *s["sites"]], "id")
    sites = {item["id"] for item in s["sites"]}
    demands = index(s["demands"], "demand_id")
    types = index(s["drone_types"], "type_id")
    index(s["cargo_items"], "cargo_id")
    index(s["drones"], "drone_id")
    index(s["batteries"], "battery_id")
    zones = s.get("restricted_zones", [])
    index(zones, "zone_id")
    require(
        sum(len(z["geometry"]["coordinates"][0]) - 1 for z in zones) <= 160,
        "restricted zone vertex budget exceeded",
    )
    for zone in zones:
        require(
            valid_ring(zone["geometry"]["coordinates"][0]),
            "restricted zone must be a simple closed polygon",
        )
    for d in demands.values():
        require(d["site_id"] in sites, "demand references missing site")
    for c in s["cargo_items"]:
        require(c["demand_id"] in demands, "cargo references missing demand")
        require(
            c["type"] == demands[c["demand_id"]]["cargo_type"],
            "cargo type differs from demand",
        )
        require(c["location_id"] in locations, "cargo references missing location")
    for d in s["drones"]:
        require(d["type_id"] in types, "drone references missing type")
        require(d["location_id"] in locations, "drone references missing location")
    for b in s["batteries"]:
        require(b["compatible_type_id"] in types, "battery references missing type")
        require(b["location_id"] in locations, "battery references missing location")
    terrain = s["terrain"]
    if terrain["status"] == "available":
        require(
            all(
                terrain[k]
                for k in ["asset_id", "sha256", "horizontal_crs", "vertical_datum"]
            ),
            "available terrain missing metadata",
        )


def validate_snapshot(snapshot):
    validate_schema("snapshot", snapshot)
    s = snapshot["scenario"]
    validate_scenario(s)
    require(
        snapshot["scenario_id"] == s["scenario_id"],
        "snapshot scenario identity mismatch",
    )
    require(
        snapshot["scenario_state_version"] == s["state_version"],
        "snapshot version mismatch",
    )
    require(
        snapshot["content_hash"] == content_hash(s), "snapshot content hash mismatch"
    )


def validate_options(options, snapshot):
    validate_schema("solver-options", options)
    require(
        options["snapshot_id"] == snapshot["snapshot_id"], "options snapshot mismatch"
    )
    linked = [options["parent_plan_id"] is not None, options["event_id"] is not None]
    require(
        all(linked) if options["mode"] == "replan" else not any(linked),
        "mode and replan links disagree",
    )
    required = set(
        [
            "cargo_unique",
            "capacity",
            "inventory",
            "aircraft",
            "battery",
            "time_window",
            "energy",
        ]
    )
    for domain in ["terrain", "communication"]:
        if snapshot["scenario"]["policy"]["requires_" + domain]:
            required.add(domain)
    if snapshot["scenario"].get("restricted_zones"):
        required.add("restricted_zone")
    require(
        required <= set(options["requested_model_scope"]),
        "requested scope omits required policy checks",
    )


def close(actual, expected, label):
    require(
        actual is not None
        and math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-6),
        f"{label} aggregation mismatch",
    )


def validate_plan(plan, snapshot):
    validate_schema("plan", plan)
    validate_snapshot(snapshot)
    s = snapshot["scenario"]
    for key, value in [
        ("scenario_id", s["scenario_id"]),
        ("snapshot_id", snapshot["snapshot_id"]),
        ("scenario_state_version", s["state_version"]),
    ]:
        require(plan[key] == value, f"plan {key} mismatch")
    require(
        (plan["parent_plan_id"] is None) == (plan["event_id"] is None),
        "plan replan links must be paired",
    )
    require(
        (plan["parent_plan_id"] is None) == (plan["change_summary"] is None),
        "change summary must match replan links",
    )
    drones = index(s["drones"], "drone_id")
    batteries = index(s["batteries"], "battery_id")
    cargos = index(s["cargo_items"], "cargo_id")
    demands = index(s["demands"], "demand_id")
    sites = index(s["sites"], "id")
    index(plan["sorties"], "sortie_id")
    assigned = []
    quantities = Counter()
    windows = {}
    deliveries = []
    for sortie in plan["sorties"]:
        require(
            sortie["drone_id"] in drones and sortie["battery_id"] in batteries,
            "sortie missing resource reference",
        )
        drone, battery = drones[sortie["drone_id"]], batteries[sortie["battery_id"]]
        require(
            drone["type_id"] == battery["compatible_type_id"], "incompatible battery"
        )
        require(
            drone["status"] in ("available", "reserved")
            and battery["status"] in ("available", "reserved", "charging"),
            "unavailable resource assigned",
        )
        start, takeoff, end = (
            sortie["prepare_start_s"],
            sortie["takeoff_s"],
            sortie["return_s"],
        )
        require(
            start <= takeoff < end <= sortie["drone_released_s"],
            "invalid sortie time ordering",
        )
        require(end <= sortie["battery_released_s"], "battery released before return")
        require(
            start >= max(drone["available_after_s"], battery["available_after_s"]),
            "resource used before available",
        )
        for kind, resource, release in [
            ("drone", sortie["drone_id"], sortie["drone_released_s"]),
            ("battery", sortie["battery_id"], sortie["battery_released_s"]),
        ]:
            windows.setdefault((kind, resource), []).append(
                (start, release, sortie["sortie_id"])
            )
        require(
            sortie["route_geometry"]["coordinates"][0] == s["base"]["coordinates"]
            and sortie["route_geometry"]["coordinates"][-1] == s["base"]["coordinates"],
            "P0 route must return to base",
        )
        assigned.extend(sortie["cargo_ids"])
        visited = []
        previous = takeoff
        for visit in sortie["visits"]:
            require(visit["site_id"] in sites, "missing visit site")
            require(
                previous <= visit["delivery_complete_s"] <= end,
                "invalid visit time ordering",
            )
            previous = visit["delivery_complete_s"]
            deliveries.append(previous)
            for cid in visit["cargo_ids"]:
                require(cid in cargos, "missing cargo reference")
                cargo = cargos[cid]
                require(
                    demands[cargo["demand_id"]]["site_id"] == visit["site_id"],
                    "wrong delivery destination",
                )
                require(
                    cargo["status"] in ("available", "reserved")
                    and cargo["location_id"] == s["base"]["id"],
                    "cargo not available at base",
                )
                quantities[cargo["demand_id"]] += 1
            visited.extend(visit["cargo_ids"])
        require(
            Counter(visited) == Counter(sortie["cargo_ids"]),
            "visit cargo differs from manifest",
        )
    require(len(assigned) == len(set(assigned)), "cargo assigned more than once")
    for resource, intervals in windows.items():
        ordered = sorted(intervals)
        for earlier, later in zip(ordered, ordered[1:]):
            require(
                earlier[1] <= later[0],
                f"overlapping {resource}: {earlier[2]} and {later[2]}",
            )
    unserved = []
    for did, d in demands.items():
        require(
            quantities[did] in (0, d["required_quantity"]),
            "P0 cannot represent partial service or overdelivery",
        )
        if quantities[did] < d["required_quantity"]:
            unserved.append(did)
    require(
        len(plan["unserved_demand_ids"]) == len(set(plan["unserved_demand_ids"])),
        "duplicate unserved demand",
    )
    require(
        set(plan["unserved_demand_ids"]) == set(unserved), "unserved demand mismatch"
    )
    m = plan["metrics"]
    require(
        m["sortie_count"] == len(plan["sorties"])
        and m["unserved_demand_count"] == len(unserved),
        "metric count mismatch",
    )
    total = sum(d["mandatory"] for d in demands.values())
    require(m["mandatory_total_count"] == total, "mandatory total mismatch")
    require(
        m["mandatory_served_count"]
        == sum(d["mandatory"] and did not in unserved for did, d in demands.items()),
        "mandatory service mismatch",
    )
    if plan["sorties"]:
        close(m["makespan_s"], max(x["return_s"] for x in plan["sorties"]), "makespan")
        close(m["last_delivery_s"], max(deliveries), "last delivery")
        energies = [x["energy_kwh"] for x in plan["sorties"]]
        socs = [x["return_soc"] for x in plan["sorties"]]
        require(
            (
                m["energy_kwh"] is None
                if any(e is None for e in energies)
                else m["energy_kwh"] is not None
            ),
            "unknown energy must remain null",
        )
        if all(e is not None for e in energies):
            close(m["energy_kwh"], sum(energies), "energy")
        require(
            (
                m["min_return_soc"] is None
                if any(e is None for e in socs)
                else m["min_return_soc"] is not None
            ),
            "unknown SOC must remain null",
        )
        if all(e is not None for e in socs):
            close(m["min_return_soc"], min(socs), "SOC")
    if plan["has_validated_plan"]:
        require(
            s["data_origin"] != "mock",
            "mock input cannot produce publishable validated plan",
        )
        required = set(
            [
                "cargo_unique",
                "capacity",
                "inventory",
                "aircraft",
                "battery",
                "time_window",
                "energy",
            ]
        )
        for domain in ["terrain", "communication"]:
            if s["policy"]["requires_" + domain]:
                required.add(domain)
                require(
                    all(x[domain + "_status"] == "passed" for x in plan["sorties"]),
                    f"{domain} not validated",
                )
        checks = plan["validation"]["checks"]
        if s.get("restricted_zones"):
            required.add("restricted_zone")
        require(
            required <= set(plan["model_scope"]),
            "validated plan scope missing required check",
        )
        require(
            required <= {c["code"] for c in checks if c["status"] == "passed"},
            "validated plan lacks passed check evidence",
        )
        require(
            not any(c["status"] == "failed" for c in checks),
            "failed validation check in published plan",
        )
        require(
            not unserved, "P0 validated full-service plan cannot leave unserved demand"
        )


def validate_outcome(outcome, snapshot):
    validate_schema("solver-outcome", outcome)
    first = outcome["first_feasible_s"]
    require(
        first is None or first <= outcome["runtime_s"], "first feasible exceeds runtime"
    )
    success = outcome["solver_status"] in ("FEASIBLE", "OPTIMAL")
    if success:
        require(
            outcome["stop_reason"] in ("finished", "time_limit"),
            "success has incompatible stop reason",
        )
        require(
            outcome["candidate_count"] > 0 and first is not None,
            "success lacks candidate timing",
        )
        plan = outcome["plan"]
        validate_plan(plan, snapshot)
        require(plan["has_validated_plan"], "success plan not independently validated")
        require(
            plan["solver_status"] == outcome["solver_status"],
            "outcome/plan solver status mismatch",
        )
        require(
            plan["validation"] == outcome["validation"],
            "outcome/plan validation differs",
        )
        require(
            plan["model_scope"] == outcome["model_scope"], "outcome/plan scope differs"
        )
    if outcome["solver_status"] == "ERROR":
        require(
            outcome["stop_reason"] in ("validation_failed", "exception"),
            "ERROR needs validation failure or exception",
        )


def validate_job(job, plan=None):
    validate_schema("solve-job", job)
    if job["job_state"] == "completed":
        success = job["solver_status"] in ("FEASIBLE", "OPTIMAL")
        require(
            success == job["has_validated_plan"],
            "completed job success/validated disagreement",
        )
        require((job["plan_id"] is not None) == success, "job plan/status disagreement")
    if job["has_validated_plan"]:
        require(plan is not None, "validated job must resolve a stored Plan")
        require(
            job["plan_id"] == job["reserved_plan_id"] == plan["plan_id"],
            "job plan identity mismatch",
        )
        require(
            plan["data_origin"] == "solver"
            and plan["has_validated_plan"]
            and plan["validation"]["status"] == "passed",
            "job must reference validated solver plan",
        )
        require(
            job["snapshot_id"] == plan["snapshot_id"]
            and job["scenario_id"] == plan["scenario_id"],
            "job snapshot/scenario mismatch",
        )


def validate_event(event, scenario):
    validate_schema("event", event)
    require(event["scenario_id"] == scenario["scenario_id"], "event scenario mismatch")
    require(
        event["expected_state_version"] == scenario["state_version"],
        "event expected version mismatch",
    )
    drones = index(scenario["drones"], "drone_id")
    require(event["payload"]["drone_id"] in drones, "event missing drone")
    require(
        all(d["status"] in ("available", "unavailable") for d in scenario["drones"]),
        "P0 event unsupported execution state",
    )
    require(
        all(
            c["status"] in ("available", "unavailable") for c in scenario["cargo_items"]
        ),
        "P0 event cannot reset execution facts",
    )
    occurred, received = (
        datetime.fromisoformat(event[k].replace("Z", "+00:00"))
        for k in ("occurred_at", "received_at")
    )
    require(received >= occurred, "event receive time precedes occurrence")


def check_http_draft():
    spec = read_json(ROOT / "contracts/http/openapi.draft.json")
    operations = []

    def walk(value):
        if isinstance(value, dict):
            if "$ref" in value:
                target = value["$ref"]
                if target.startswith("#/"):
                    cursor = spec
                    for key in target[2:].split("/"):
                        require(key in cursor, f"unresolved OpenAPI ref {target}")
                        cursor = cursor[key]
                else:
                    require(
                        target.split("#")[0] in {s["$id"] for s in SCHEMAS.values()},
                        f"unknown external OpenAPI ref {target}",
                    )
            for x in value.values():
                walk(x)
        elif isinstance(value, list):
            for x in value:
                walk(x)

    walk(spec)
    for path, methods in spec["paths"].items():
        for method, item in methods.items():
            require(
                method in ("get", "post", "put", "delete", "patch"),
                "unexpected HTTP verb",
            )
            operations.append(item["operationId"])
            names = {
                p["name"]
                for p in item.get("parameters", [])
                if p["in"] == "path" and p["required"]
            }
            require(
                names == set(re.findall(r"\{([^}]+)\}", path)),
                f"path params mismatch: {path}",
            )
    require(len(operations) == len(set(operations)), "duplicate operationId")
    return len(operations)


def main():
    manifest = read_json(ROOT / "contracts/manifest.json")
    require(
        set(manifest["schemas"]) == {k + ".schema.json" for k in SCHEMAS},
        "schema manifest mismatch",
    )
    for s in SCHEMAS.values():
        Draft202012Validator.check_schema(s)
    entries = read_json(ROOT / "fixtures/index.json")["fixtures"]
    data = {e["path"]: read_json(ROOT / e["path"]) for e in entries}
    for e in entries:
        validate_schema(e["schema"], data[e["path"]])
    snap = data["fixtures/mock/snapshot.json"]
    validate_snapshot(snap)
    require(
        data["fixtures/mock/scenario.json"] == snap["scenario"],
        "fixture scenario/snapshot drift",
    )
    validate_plan(data["fixtures/mock/plan.json"], snap)
    validate_options(data["fixtures/mock/solver-options.json"], snap)
    validate_outcome(data["fixtures/mock/solver-outcome.json"], snap)
    validate_event(data["fixtures/mock/event.json"], snap["scenario"])
    for e in entries:
        if e["schema"] == "solve-job":
            validate_job(data[e["path"]])
    require(
        not data["fixtures/mock/capabilities.json"]["solver_ready"],
        "G0 fixture cannot claim solver ready",
    )
    print(
        f"PASS: {len(SCHEMAS)} schemas, {len(entries)} mock fixtures, {check_http_draft()} draft HTTP operations; references/hash/state smoke checks."
    )
    print(
        "Scope: no solver execution, physical feasibility validation, running API, or UI build."
    )


if __name__ == "__main__":
    try:
        main()
    except (ContractError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
