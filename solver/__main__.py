import argparse
import json
from pathlib import Path

from shared.contracts import content_hash
from solver.adapters.contest import compact_scenario, contest_scenario
from solver.public_api import solve


def main():
    parser = argparse.ArgumentParser(description="援航真实运输求解CLI")
    parser.add_argument("--scenario", type=Path)
    parser.add_argument("--example", choices=["compact", "contest"], default="compact")
    parser.add_argument(
        "--objective", choices=["time", "energy", "balanced"], default="time"
    )
    parser.add_argument("--seconds", type=float, default=15)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    s = (
        json.loads(args.scenario.read_text(encoding="utf-8"))
        if args.scenario
        else (compact_scenario() if args.example == "compact" else contest_scenario())
    )
    snapshot = {
        "schema_version": s["schema_version"],
        "snapshot_id": "SNAP-CLI-001",
        "scenario_id": s["scenario_id"],
        "scenario_state_version": s["state_version"],
        "content_hash": content_hash(s),
        "created_at": "2026-10-17T08:00:00+08:00",
        "scenario": s,
    }
    scope = [
        "cargo_unique",
        "capacity",
        "inventory",
        "aircraft",
        "battery",
        "time_window",
        "energy",
    ] + (["terrain"] if s["policy"]["requires_terrain"] else [])
    options = {
        "schema_version": s["schema_version"],
        "plan_id": "PLAN-CLI-001",
        "snapshot_id": snapshot["snapshot_id"],
        "objective": args.objective,
        "mode": "quick",
        "time_limit_s": args.seconds,
        "seed": args.seed,
        "parent_plan_id": None,
        "event_id": None,
        "requested_model_scope": scope,
        "allow_partial_service": False,
    }
    result = solve(snapshot, options)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(
            {"snapshot": snapshot, "options": options, "outcome": result},
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": result["solver_status"],
                "runtime_s": result["runtime_s"],
                "first_feasible_s": result["first_feasible_s"],
                "metrics": result["plan"]["metrics"] if result["plan"] else None,
                "diagnostics": result["diagnostics"],
            },
            ensure_ascii=False,
        )
    )
    return 0 if result["plan"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
