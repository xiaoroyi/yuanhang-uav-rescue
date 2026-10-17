"""Save actual commands, exits, timings and code identity for a reviewable checkpoint."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from shared.build_info import verification_fingerprint


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser", action="store_true")
    args = parser.parse_args()
    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    py = sys.executable
    commands = [
        [py, "-m", "pytest", "tests", "-q"],
        [py, "scripts/check_contracts.py"],
        [py, "scripts/check_governance.py"],
        [npm, "--prefix", "frontend", "run", "lint"],
        [npm, "--prefix", "frontend", "run", "test:unit"],
        [npm, "--prefix", "frontend", "run", "build"],
    ]
    if args.browser:
        commands.append([npm, "--prefix", "frontend", "run", "test:e2e"])
    out = ROOT / "evidence/verification"
    out.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    records = []
    source_before = verification_fingerprint(ROOT)
    for i, command in enumerate(commands):
        start = time.perf_counter()
        run = subprocess.run(
            command,
            cwd=ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding="utf-8",
            errors="replace",
        )
        path = out / f"check-{i+1:02}.txt"
        path.write_text(run.stdout.rstrip() + "\n", encoding="utf-8", newline="\n")
        record = {
            "command": subprocess.list2cmdline(command),
            "exit_code": run.returncode,
            "elapsed_s": round(time.perf_counter() - start, 3),
            "output": str(path.relative_to(ROOT)).replace("\\", "/"),
        }
        records.append(record)
        print(
            f'{i+1}/{len(commands)} exit={run.returncode}: {record["command"]}',
            flush=True,
        )
    tracked = subprocess.check_output(["git", "diff", "--binary", "HEAD"], cwd=ROOT)
    source_after = verification_fingerprint(ROOT)
    report = {
        "at_utc": datetime.now(timezone.utc).isoformat(),
        "head": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "branch": subprocess.check_output(
            ["git", "branch", "--show-current"], cwd=ROOT, text=True
        ).strip(),
        "working_tree_diff_sha256": hashlib.sha256(tracked).hexdigest(),
        "note": "This report may precede the checkpoint commit; untracked files are listed separately.",
        "status": subprocess.check_output(
            ["git", "status", "--short"], cwd=ROOT, text=True, encoding="utf-8"
        ),
        "checks": records,
        "verification_source_before_sha256": source_before,
        "verification_source_after_sha256": source_after,
        "source_unchanged": source_before == source_after,
        "passed": all(r["exit_code"] == 0 for r in records)
        and source_before == source_after,
    }
    (out / "latest.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
