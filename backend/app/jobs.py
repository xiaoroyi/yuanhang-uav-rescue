"""Bounded subprocess worker manager with real cancellation and restart recovery."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import threading
import time

from sqlalchemy import select

from backend.app.storage import Database, JobRow, PlanRow
from shared.contracts import validate_outcome

ROOT = Path(__file__).resolve().parents[2]


def now():
    return datetime.now(timezone.utc).isoformat()


class JobManager:
    def __init__(self, database: Database):
        self.db = database
        self.limit = threading.Semaphore(1)
        self.lock = threading.RLock()
        self.processes = {}
        self.threads = []
        self.stopping = False

    def recover(self):
        with self.db.session(immediate=True) as session:
            for row in session.scalars(
                select(JobRow).where(JobRow.state.in_(["queued", "running"]))
            ):
                self._fail(
                    row, "服务上次未正常结束，本任务已标记失败；可基于原快照重新提交。"
                )

    def _fail(self, row, message):
        data = dict(row.content)
        data.update(
            job_state="failed",
            solver_status="ERROR",
            has_validated_plan=False,
            plan_id=None,
            finished_at=now(),
            stop_reason="exception",
            error={
                "code": "INTERNAL_ERROR",
                "message": message,
                "field_path": None,
                "details": {},
                "request_id": row.id,
            },
        )
        row.state = "failed"
        row.content = data

    def _canceled(self, row):
        data = dict(row.content)
        data.update(
            job_state="canceled",
            solver_status=None,
            has_validated_plan=False,
            plan_id=None,
            finished_at=now(),
            stop_reason="canceled",
        )
        row.state = "canceled"
        row.content = data

    @staticmethod
    def _stop(process):
        if process.poll() is not None:
            return
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=3)

    def submit(self, job_id, payload):
        thread = threading.Thread(
            target=self._run,
            args=(job_id, payload),
            daemon=True,
            name="solver-" + job_id,
        )
        self.threads.append(thread)
        thread.start()

    def cancel(self, job_id):
        with self.lock:
            with self.db.session(immediate=True) as session:
                row = session.get(JobRow, job_id)
                if row is None:
                    return None
                if row.state in ("completed", "failed", "canceled"):
                    return row.content
                row.cancel_requested = True
                process = self.processes.get(job_id)
                if process is not None and process.poll() is None:
                    self._stop(process)
                self._canceled(row)
                return row.content

    def _run(self, job_id, payload):
        try:
            self._execute(job_id, payload)
        except Exception as exc:
            with self.lock:
                process = self.processes.pop(job_id, None)
                if process is not None:
                    self._stop(process)
                with self.db.session(immediate=True) as session:
                    row = session.get(JobRow, job_id)
                    if row and row.state in ("queued", "running"):
                        self._fail(row, "求解任务启动或监控失败：" + str(exc)[:300])

    def _execute(self, job_id, payload):
        with self.limit:
            if self.stopping:
                return
            folder = self.db.directory / "jobs" / job_id
            folder.mkdir(parents=True, exist_ok=True)
            source, output, progress = (
                folder / n for n in ("input.json", "outcome.json", "progress.json")
            )
            source.write_text(
                json.dumps(payload, ensure_ascii=False, allow_nan=False),
                encoding="utf-8",
            )
            started = time.perf_counter()
            with self.lock:
                with self.db.session(immediate=True) as session:
                    row = session.get(JobRow, job_id)
                    if row.state == "canceled" or row.cancel_requested:
                        return
                    row.state = "running"
                    row.content = {
                        **row.content,
                        "job_state": "running",
                        "started_at": now(),
                    }
                log = (folder / "worker.log").open("w", encoding="utf-8")
                try:
                    process = subprocess.Popen(
                        [
                            sys.executable,
                            "-m",
                            "backend.app.worker",
                            str(source),
                            str(output),
                            str(progress),
                        ],
                        cwd=ROOT,
                        stdout=log,
                        stderr=subprocess.STDOUT,
                        creationflags=(
                            subprocess.CREATE_NO_WINDOW
                            if sys.platform == "win32"
                            else 0
                        ),
                    )
                except Exception:
                    log.close()
                    raise
                self.processes[job_id] = process
            timed_out = False
            try:
                while process.poll() is None:
                    if (
                        time.perf_counter() - started
                        > payload["options"]["time_limit_s"] + 8
                    ):
                        self._stop(process)
                        timed_out = True
                        break
                    time.sleep(0.05)
            finally:
                log.close()
            with self.lock:
                self.processes.pop(job_id, None)
                with self.db.session(immediate=True) as session:
                    row = session.get(JobRow, job_id)
                    if row.state == "canceled" or row.cancel_requested:
                        return
                    if timed_out or process.returncode != 0 or not output.exists():
                        self._fail(
                            row, "求解进程达到硬超时或异常退出，请查看任务运行日志。"
                        )
                        return
                    try:
                        outcome = json.loads(output.read_text(encoding="utf-8"))
                        validate_outcome(outcome, payload["snapshot"])
                        if outcome["plan"]:
                            plan = outcome["plan"]
                            session.add(
                                PlanRow(
                                    id=plan["plan_id"],
                                    scenario_id=plan["scenario_id"],
                                    snapshot_id=plan["snapshot_id"],
                                    version=plan["scenario_state_version"],
                                    content=plan,
                                    confirmed_at=None,
                                )
                            )
                        row.outcome = outcome
                        if outcome["solver_status"] == "ERROR":
                            self._fail(row, "独立检查未通过，候选已阻止发布。")
                        else:
                            row.state = "completed"
                            row.content = {
                                **row.content,
                                "job_state": "completed",
                                "solver_status": outcome["solver_status"],
                                "plan_id": (
                                    outcome["plan"]["plan_id"]
                                    if outcome["plan"]
                                    else None
                                ),
                                "has_validated_plan": bool(outcome["plan"]),
                                "runtime_s": outcome["runtime_s"],
                                "stop_reason": outcome["stop_reason"],
                                "finished_at": now(),
                                "error": None,
                            }
                    except Exception as exc:
                        self._fail(row, "求解结果未通过公共契约校验：" + str(exc)[:400])

    def progress(self, job_id):
        path = self.db.directory / "jobs" / job_id / "progress.json"
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, ValueError):
            return {"stage": "等待计算资源", "elapsed_s": 0, "candidate_count": 0}

    def close(self):
        self.stopping = True
        with self.lock:
            for job_id in list(self.processes):
                self.cancel(job_id)
        for thread in self.threads:
            thread.join(timeout=5)
