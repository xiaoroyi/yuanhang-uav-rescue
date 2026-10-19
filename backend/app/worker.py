"""One-job subprocess. The API owns process cancellation and the SQLite transaction."""

import json
import os
from pathlib import Path
import sys
import traceback
import time

from solver.public_api import replan, solve, repair_remaining
from solver.assets import terrain_store
from solver.engines import policy_store


def atomic_json(path: Path, value):
    temp = path.with_suffix(".tmp")
    temp.write_text(
        json.dumps(value, ensure_ascii=False, allow_nan=False), encoding="utf-8"
    )
    # Windows may reject replacement while a reader/virus scanner briefly holds the destination.
    # Keep the previous complete JSON visible, then retry instead of publishing a partial file.
    for attempt in range(20):
        try:
            os.replace(temp, path)
            return
        except PermissionError:
            if attempt == 19:
                raise
            time.sleep(0.01)


def main():
    source, output, progress = map(Path, sys.argv[1:4])
    data = json.loads(source.read_text(encoding="utf-8"))
    # input.json lives in runtime/jobs/JOB-id; no user path enters core SolverOptions.
    with terrain_store(source.parents[2] / "assets"), policy_store(
        source.parents[2] / "heuristics"
    ):
        return run_job(data, output, progress)


def run_job(data, output, progress):

    def callback(value):
        try:
            atomic_json(progress, value)
        except PermissionError:
            # Progress is advisory. A transient reporting failure must not abort a valid solve.
            pass

    try:
        if "repair_reference" in data:
            result = repair_remaining(
                data["snapshot"], data["repair_reference"], data["options"], callback
            )
        elif data["options"]["mode"] == "replan":
            result = replan(
                data["snapshot"],
                data["previous_plan"],
                data["event"],
                data["options"],
                callback,
            )
        else:
            result = solve(
                data["snapshot"],
                data["options"],
                callback,
                initial_plan=data.get("initial_plan"),
            )
        atomic_json(output, result)
    except Exception:
        traceback.print_exc()
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
