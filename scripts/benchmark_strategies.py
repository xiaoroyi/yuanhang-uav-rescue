"""Run the preregistered same-input, same-budget preference/seed matrix."""

from __future__ import annotations

import argparse
import copy
import csv
from datetime import datetime, timezone
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from shared.build_info import verification_fingerprint
from shared.contracts import content_hash, validate_outcome
from solver.adapters.contest import compact_scenario, contest_scenario
from solver.metrics import delivery_analysis
from solver.public_api import solve, validate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", type=float, default=15)
    parser.add_argument("--seeds", default="7,42,2026")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        seeds = [int(v) for v in args.seeds.split(",")]
    except ValueError:
        parser.error("seeds must be comma-separated nonnegative integers")
    if not seeds or len(seeds) > 12 or len(set(seeds)) != len(seeds) or min(seeds) < 0:
        parser.error("use 1–12 distinct nonnegative seeds")
    if not math.isfinite(args.seconds) or not 0 < args.seconds <= 300:
        parser.error("seconds must be finite and in (0,300]")
    output = args.output.resolve()
    csv_path = output.with_suffix(".csv")
    if (
        output.suffix != ".json"
        or not output.is_relative_to(ROOT)
        or output.exists()
        or csv_path.exists()
    ):
        parser.error(
            "choose a new .json output path inside this repository; old evidence is not overwritten"
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    run_id = uuid.uuid4().hex[:12]
    now = lambda: datetime.now(timezone.utc).isoformat()
    git = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    report = dict(
        run_id=run_id,
        created_at_utc=now(),
        complete=False,
        head=git.stdout.strip() if git.returncode == 0 else None,
        source_before_sha256=verification_fingerprint(ROOT),
        environment={
            "python": platform.python_version(),
            "platform": platform.platform(),
            "logical_cpu_count": os.cpu_count(),
            "dependencies": {
                name: importlib.metadata.version(name)
                for name in ["numpy", "ortools", "rasterio"]
            },
        },
        budget_per_run_s=args.seconds,
        seeds=seeds,
        notes=[
            "Preference comparison, not a claim that one algorithm dominates another. Primary objective is weighted per-box expected delay.",
            "Same immutable Snapshot and same budget across strategies; strategy execution order rotates between seeds.",
            "One Python process; terrain caches warm over time. HTTP/worker startup excluded. Other machine load is not controlled; runtime is observational.",
            "All unpublished outcomes are retained, null is not converted to zero; no probability, global-optimality, minimum-fleet or real-flight claim.",
        ],
        snapshots={},
        runs=[],
        summary=[],
    )

    def save():
        output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )

    save()
    scenes = [("compact", compact_scenario()), ("contest", contest_scenario())]
    ground = compact_scenario()
    ground.update(scenario_id="SCN-EXP-GROUND", data_origin="user_input")
    ground["resource_limits"] = {"prep_slots": 1, "charging_ports": 2}
    scenes.append(("compact-ground", ground))
    rows = []
    for case, s in scenes:
        snapshot = dict(
            schema_version=s["schema_version"],
            snapshot_id=f"SNAP-EXP-{run_id}-{case}",
            scenario_id=s["scenario_id"],
            scenario_state_version=s["state_version"],
            content_hash=content_hash(s),
            created_at=now(),
            scenario=s,
        )
        report["snapshots"][case] = copy.deepcopy(snapshot)
        save()
        scope = (
            [
                "cargo_unique",
                "capacity",
                "inventory",
                "aircraft",
                "battery",
                "time_window",
                "energy",
            ]
            + (["terrain"] if s["policy"]["requires_terrain"] else [])
            + (["ground_resource"] if s.get("resource_limits") else [])
        )
        for index, seed in enumerate(seeds):
            strategies = ["time", "energy", "balanced"]
            strategies = strategies[index % 3 :] + strategies[: index % 3]
            for objective in strategies:
                options = dict(
                    schema_version=s["schema_version"],
                    plan_id=f"PLAN-EXP-{run_id}-{case}-{seed}-{objective}",
                    snapshot_id=snapshot["snapshot_id"],
                    objective=objective,
                    mode="quick",
                    time_limit_s=args.seconds,
                    seed=seed,
                    parent_plan_id=None,
                    event_id=None,
                    requested_model_scope=scope,
                    allow_partial_service=False,
                )
                before = copy.deepcopy((snapshot, options))
                started = time.perf_counter()
                outcome = solve(snapshot, options)
                wall = time.perf_counter() - started
                record = dict(
                    case=case,
                    seed=seed,
                    objective=objective,
                    options=before[1],
                    outcome=outcome,
                    independent_recheck=None,
                    audit_error=None,
                )
                report["runs"].append(record)
                try:
                    validate_outcome(outcome, snapshot)
                    if (snapshot, options) != before:
                        raise AssertionError("Solver mutated frozen experiment input")
                    independent = None
                    if outcome["plan"]:
                        independent = validate(snapshot, outcome["plan"])
                        if independent["status"] != "passed":
                            raise AssertionError(
                                "Independent experiment check rejected published plan"
                            )
                except Exception as exc:
                    record["audit_error"] = str(exc)
                    save()
                    raise
                plan = outcome["plan"]
                metrics = plan["metrics"] if plan else {}
                row = dict(
                    case=case,
                    seed=seed,
                    objective=objective,
                    snapshot_content_hash=snapshot["content_hash"],
                    solver_status=outcome["solver_status"],
                    has_validated_plan=bool(plan),
                    runtime_s=outcome["runtime_s"],
                    wall_s=wall,
                    first_feasible_s=outcome["first_feasible_s"],
                    candidate_count=outcome["candidate_count"],
                    weighted_box_delay_s=(
                        delivery_analysis(s, plan)["weighted_box_delay_s"]
                        if plan
                        else None
                    ),
                    **{
                        name: metrics.get(name)
                        for name in [
                            "makespan_s",
                            "last_delivery_s",
                            "energy_kwh",
                            "min_return_soc",
                            "sortie_count",
                        ]
                    },
                )
                rows.append(row)
                record.update(summary=row, independent_recheck=independent)
                save()
                print(
                    case,
                    seed,
                    objective,
                    outcome["solver_status"],
                    round(wall, 3),
                    flush=True,
                )
    fields = [
        "weighted_box_delay_s",
        "makespan_s",
        "last_delivery_s",
        "energy_kwh",
        "min_return_soc",
        "sortie_count",
        "runtime_s",
    ]
    for case, _ in scenes:
        for objective in ["time", "energy", "balanced"]:
            selected = [
                r for r in rows if r["case"] == case and r["objective"] == objective
            ]
            valid = [r for r in selected if r["has_validated_plan"]]
            summary = dict(
                case=case,
                objective=objective,
                runs=len(selected),
                valid_plans=len(valid),
                unpublished=len(selected) - len(valid),
                metrics={},
            )
            for key in fields:
                values = [r[key] for r in valid]
                summary["metrics"][key] = (
                    {
                        "min": min(values),
                        "median": statistics.median(values),
                        "max": max(values),
                    }
                    if values
                    else None
                )
            report["summary"].append(summary)
    report.update(
        complete=True,
        finished_at_utc=now(),
        source_after_sha256=verification_fingerprint(ROOT),
        valid_plan_count=sum(r["has_validated_plan"] for r in rows),
        run_count=len(rows),
    )
    report["source_unchanged"] = (
        report["source_before_sha256"] == report["source_after_sha256"]
    )
    save()
    with csv_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(
        json.dumps(
            {
                "run_count": len(rows),
                "valid_plan_count": report["valid_plan_count"],
                "source_unchanged": report["source_unchanged"],
                "output": str(output.relative_to(ROOT)),
            }
        )
    )
    return (
        0
        if report["source_unchanged"]
        and all(r["solver_status"] != "ERROR" for r in rows)
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
