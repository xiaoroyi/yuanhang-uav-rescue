"""Bounded real-worker comparisons, isolated from mission inputs and confirmations."""

from __future__ import annotations

import base64
import copy
import hashlib
from importlib.metadata import version
import os
from pathlib import Path
import platform
import statistics
import subprocess
import threading

from sqlalchemy import select

from backend.app.execution_archive import document
from backend.app.jobs import now
from backend.app.missions import identity, require
from backend.app.operation_models import (
    ExperimentRequest,
    ExperimentView,
    ExperimentBundle,
)
from backend.app.storage import (
    OperationRecordRow,
    SnapshotRow,
    PlanRow,
    ScenarioRow,
    VersionRow,
    JobRow,
)
from shared.build_info import service_fingerprint
from shared.contracts import content_hash, validate_scenario
from solver.metrics import delivery_analysis

ROOT = Path(__file__).resolve().parents[2]
TERMINAL = {"completed", "failed", "canceled"}


def environment():
    def git(*args):
        try:
            result = subprocess.run(
                ["git", *args],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=3,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except (OSError, subprocess.TimeoutExpired):
            return None

    return {
        "service_source_sha256": service_fingerprint(ROOT),
        "git_commit": git("rev-parse", "HEAD"),
        "git_worktree_dirty": bool(
            git("status", "--porcelain", "--untracked-files=no")
        ),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "processor": platform.processor() or None,
        "logical_cpu_count": os.cpu_count(),
        "ortools_version": version("ortools"),
        "numpy_version": version("numpy"),
        "worker_serial_limit": 1,
        "cp_sat_threads": 1,
        "cache_policy": "每例独立Worker进程；OS文件缓存不重置。runtime_s为Solver报告时间，非端到端/设备响应。",
    }


def case_projection(session, case):
    value = copy.deepcopy(case)
    job = session.get(JobRow, case["job"]["job_id"]) if case["job"] else None
    if job:
        value["job"] = copy.deepcopy(job.content)
        value["status"] = job.state if job.state in TERMINAL else "running"
        outcome = job.outcome
        value["runtime_s"] = (outcome or {}).get(
            "runtime_s", job.content.get("runtime_s")
        )
        if outcome:
            value.update(
                first_feasible_s=outcome["first_feasible_s"],
                candidate_count=outcome["candidate_count"],
                diagnostics=outcome["diagnostics"],
                model_scope=outcome["model_scope"],
                validation_status=outcome["validation"]["status"],
            )
            plan = outcome.get("plan")
            if plan:
                m = plan["metrics"]
                joint = plan.get("joint_metrics") or {}
                scene = session.get(SnapshotRow, plan["snapshot_id"]).content[
                    "scenario"
                ]
                value.update(
                    energy_kwh=joint.get("joint_energy_kwh", m["energy_kwh"]),
                    makespan_s=joint.get("joint_makespan_s", m["makespan_s"]),
                    last_delivery_s=m["last_delivery_s"],
                    min_return_soc=m["min_return_soc"],
                    weighted_tardiness_s=delivery_analysis(scene, plan)[
                        "weighted_box_delay_s"
                    ],
                    allocated_quantity=len(
                        {c for r in plan["sorties"] for c in r["cargo_ids"]}
                    ),
                )
        if job.content.get("error"):
            value["message"] = job.content["error"]["message"]
        elif value["status"] == "completed" and not job.content["has_validated_plan"]:
            value["message"] = (
                "当前声明模型中不可行，具体原因见诊断。"
                if job.content["solver_status"] == "INFEASIBLE"
                else "当前预算/方法未得到可验证方案；不等于已证明无解。"
            )
    return value


def grouped(cases):
    rows = []
    for method, objective in sorted({(c["method"], c["objective"]) for c in cases}):
        selected = [
            c for c in cases if (c["method"], c["objective"]) == (method, objective)
        ]
        finished = [c for c in selected if c["status"] in TERMINAL]
        feasible = [c for c in finished if c["job"] and c["job"]["has_validated_plan"]]
        runtimes = sorted(
            c["runtime_s"] for c in finished if c["runtime_s"] is not None
        )

        # Linear interpolation is defined for a single observation, but is not a statistical guarantee.
        def quantile(fraction):
            if not runtimes:
                return None
            pos = (len(runtimes) - 1) * fraction
            i = int(pos)
            return runtimes[i] + (
                runtimes[min(i + 1, len(runtimes) - 1)] - runtimes[i]
            ) * (pos - i)

        rows.append(
            {
                "method": method,
                "objective": objective,
                "total": len(selected),
                "finished": len(finished),
                "feasible": len(feasible),
                "failed_or_unvalidated": sum(
                    c["status"] != "canceled"
                    and not (c["job"] and c["job"]["has_validated_plan"])
                    for c in finished
                ),
                "canceled": sum(c["status"] == "canceled" for c in finished),
                "runtime_sample_count": len(runtimes),
                "runtime_p50_s": quantile(0.5),
                "runtime_p95_s": quantile(0.95),
                "feasible_energy_median_kwh": (
                    statistics.median(c["energy_kwh"] for c in feasible)
                    if feasible
                    else None
                ),
                "feasible_makespan_median_s": (
                    statistics.median(c["makespan_s"] for c in feasible)
                    if feasible
                    else None
                ),
            }
        )
    return rows


def view(session, row):
    value = copy.deepcopy(row.content)
    value["cases"] = [case_projection(session, c) for c in value["cases"]]
    value["groups"] = grouped(value["cases"])
    return value


class ExperimentCoordinator:
    def __init__(self, database, create_job, solve_request, jobs):
        self.db, self.create_job, self.solve_request, self.jobs = (
            database,
            create_job,
            solve_request,
            jobs,
        )
        self.lock = threading.RLock()
        self.stop = threading.Event()
        self.environment = environment()
        with self.db.session(immediate=True) as session:
            for row in session.scalars(
                select(OperationRecordRow).where(
                    OperationRecordRow.namespace == "experiment.run"
                )
            ):
                value = copy.deepcopy(row.content)
                for case in value["cases"]:
                    if case["status"] == "dispatching" and case["job"] is None:
                        case.update(
                            status="failed",
                            message="服务在派发和绑定之间退出，结果未确定；本例不自动重发。",
                        )
                row.content = value
        self.thread = threading.Thread(
            target=self.run, name="experiment-coordinator", daemon=True
        )
        self.thread.start()

    def close(self):
        self.stop.set()
        self.thread.join(timeout=5)

    def run(self):
        while not self.stop.wait(0.35):
            try:
                with self.lock:
                    with self.db.session() as session:
                        ids = [
                            r.id
                            for r in session.scalars(
                                select(OperationRecordRow).where(
                                    OperationRecordRow.namespace == "experiment.run"
                                )
                            )
                            if r.content["status"] in ("queued", "running")
                        ]
                    for eid in ids:
                        self.tick(eid)
            except Exception:
                import logging

                logging.getLogger(__name__).exception(
                    "Experiment coordinator tick failed"
                )

    def tick(self, eid):
        with self.db.session(immediate=True) as session:
            row = session.get(OperationRecordRow, ("experiment.run", eid))
            value = view(session, row)
            if value["cancel_requested"]:
                for c in value["cases"]:
                    if c["job"] is None and c["status"] not in TERMINAL:
                        c.update(status="canceled", message="尚未启动，已取消。")
            active = next(
                (
                    c
                    for c in value["cases"]
                    if c["status"] in ("running", "dispatching")
                ),
                None,
            )
            if active or all(c["status"] in TERMINAL for c in value["cases"]):
                if not active:
                    value.update(
                        status="canceled" if value["cancel_requested"] else "completed",
                        finished_at=now(),
                    )
                row.content = value
                return
            case = next(c for c in value["cases"] if c["status"] == "queued")
            case["status"] = "dispatching"
            value["status"] = "running"
            row.content = value
            options = {
                "snapshot_id": value["snapshot_id"],
                "objective": case["objective"],
                "objective_policy": value["objective_policy"],
                "mode": case["method"],
                "seed": case["seed"],
                "time_limit_s": case["time_limit_s"],
            }
        job = None
        failure = None
        try:
            job = self.create_job(self.solve_request.model_validate(options))
        except Exception as exc:
            failure = exc
        with self.db.session(immediate=True) as session:
            row = session.get(OperationRecordRow, ("experiment.run", eid))
            value = copy.deepcopy(row.content)
            target = next(c for c in value["cases"] if c["case_id"] == case["case_id"])
            if job:
                target.update(status="running", job=job, message=None)
            elif getattr(failure, "status", None) == 503:
                target.update(
                    status="queued", message="求解队列繁忙，等待空位；未计入失败。"
                )
            else:
                target.update(
                    status="failed",
                    message=(getattr(failure, "message", None) or str(failure))[:1000],
                )
            row.content = value

    def cancel(self, eid, error):
        with self.lock:
            with self.db.session(immediate=True) as session:
                row = require(
                    session, OperationRecordRow, ("experiment.run", eid), error
                )
                value = view(session, row)
                if value["status"] in ("completed", "canceled"):
                    return value
                value["cancel_requested"] = True
                row.content = value
                active = [
                    c["job"]["job_id"]
                    for c in value["cases"]
                    if c["job"] and c["status"] not in TERMINAL
                ]
            for job in active:
                self.jobs.cancel(job)
            self.tick(eid)
            with self.db.session() as session:
                return view(
                    session,
                    require(
                        session, OperationRecordRow, ("experiment.run", eid), error
                    ),
                )


def register_experiments(app, database, error, create_job, solve_request, snapshot_for):
    @app.post("/api/v1/experiments", response_model=ExperimentView, status_code=202)
    def create_experiment(body: ExperimentRequest):
        with app.state.experiments.lock:
            with database.session(immediate=True) as session:
                digest = content_hash(body.model_dump(mode="json"))
                old = session.get(
                    OperationRecordRow, ("experiment.create", body.idempotency_key)
                )
                if old:
                    if old.request_hash != digest:
                        raise error(
                            409, "IDEMPOTENCY_CONFLICT", "评测幂等键对应不同输入。"
                        )
                    return view(
                        session,
                        require(
                            session,
                            OperationRecordRow,
                            ("experiment.run", old.owner_id),
                            error,
                        ),
                    )
                ongoing = [
                    r
                    for r in session.scalars(
                        select(OperationRecordRow).where(
                            OperationRecordRow.namespace == "experiment.run"
                        )
                    )
                    if r.content["status"] in ("queued", "running")
                ]
                if len(ongoing) >= 2:
                    raise error(
                        503, "SOLVER_BUSY", "最多同时保留2组活动评测，请等待或取消。"
                    )
                source = require(
                    session, SnapshotRow, body.source_snapshot_id, error
                ).content
                s = copy.deepcopy(source["scenario"])
                eid = identity("EXP")
                s.update(
                    scenario_id=identity("SCN"),
                    state_version=1,
                    name=body.name + " · 隔离评测",
                    mode="simulation",
                )
                validate_scenario(s)
                scenario = ScenarioRow(
                    id=s["scenario_id"],
                    name=s["name"],
                    version=1,
                    content=s,
                    active_plan_id=None,
                    updated_at=now(),
                )
                session.add(scenario)
                session.add(
                    VersionRow(
                        scenario_id=scenario.id,
                        version=1,
                        content=s,
                        content_hash=content_hash(s),
                    )
                )
                snapshot = snapshot_for(session, scenario)
                specs = (
                    [("quick", o) for o in ("time", "energy", "balanced")]
                    if body.suite == "strategy"
                    else [(m, body.objective) for m in ("quick", "improve")]
                )
                cases = [
                    {
                        "case_id": identity("CASE"),
                        "method": method,
                        "objective": objective,
                        "seed": seed,
                        "time_limit_s": body.time_limit_s,
                        "status": "queued",
                        "job": None,
                        "first_feasible_s": None,
                        "candidate_count": None,
                        "runtime_s": None,
                        "energy_kwh": None,
                        "makespan_s": None,
                        "last_delivery_s": None,
                        "weighted_tardiness_s": None,
                        "min_return_soc": None,
                        "allocated_quantity": None,
                        "model_scope": [],
                        "validation_status": None,
                        "diagnostics": [],
                        "message": None,
                    }
                    for seed in body.seeds
                    for method, objective in specs
                ]
                value = {
                    "experiment_id": eid,
                    "name": body.name,
                    "source_snapshot_id": body.source_snapshot_id,
                    "source_content_hash": source["content_hash"],
                    "snapshot_id": snapshot["snapshot_id"],
                    "snapshot_content_hash": snapshot["content_hash"],
                    "data_origin": s["data_origin"],
                    "suite": body.suite,
                    "objective_policy": body.objective_policy,
                    "status": "queued",
                    "cancel_requested": False,
                    "created_at": now(),
                    "finished_at": None,
                    "environment": app.state.experiments.environment,
                    "cases": cases,
                    "groups": grouped(cases),
                    "message": "独立分析输入，固定约束与预算上限；偏好对照不等同算法贡献，失败样本完整保留。",
                }
                ExperimentView.model_validate(value)
                session.add(
                    OperationRecordRow(
                        namespace="experiment.run",
                        id=eid,
                        owner_id=eid,
                        request_hash=digest,
                        content=value,
                    )
                )
                session.add(
                    OperationRecordRow(
                        namespace="experiment.create",
                        id=body.idempotency_key,
                        owner_id=eid,
                        request_hash=digest,
                        content={"experiment_id": eid},
                    )
                )
                return value

    @app.get("/api/v1/experiments", response_model=list[ExperimentView])
    def list_experiments():
        with database.session() as session:
            return [
                view(session, r)
                for r in sorted(
                    session.scalars(
                        select(OperationRecordRow).where(
                            OperationRecordRow.namespace == "experiment.run"
                        )
                    ),
                    key=lambda r: r.content["created_at"],
                    reverse=True,
                )
            ]

    @app.get("/api/v1/experiments/{experiment_id}", response_model=ExperimentView)
    def get_experiment(experiment_id: str):
        with database.session() as session:
            return view(
                session,
                require(
                    session,
                    OperationRecordRow,
                    ("experiment.run", experiment_id),
                    error,
                ),
            )

    @app.post(
        "/api/v1/experiments/{experiment_id}/cancel",
        response_model=ExperimentView,
        status_code=202,
    )
    def cancel_experiment(experiment_id: str):
        return app.state.experiments.cancel(experiment_id, error)

    @app.get(
        "/api/v1/experiments/{experiment_id}/export", response_model=ExperimentBundle
    )
    def export_experiment(experiment_id: str):
        with database.session() as session:
            run = view(
                session,
                require(
                    session,
                    OperationRecordRow,
                    ("experiment.run", experiment_id),
                    error,
                ),
            )
            docs = [
                document(
                    "snapshot", sid, require(session, SnapshotRow, sid, error).content
                )
                for sid in {run["source_snapshot_id"], run["snapshot_id"]}
            ]
            for case in run["cases"]:
                if case["job"] and case["job"]["plan_id"]:
                    pid = case["job"]["plan_id"]
                    docs.append(
                        document(
                            "plan", pid, require(session, PlanRow, pid, error).content
                        )
                    )
        artifacts, missing = [], []
        for case in run["cases"]:
            for name in ("input.json", "outcome.json", "progress.json", "worker.log"):
                directory = (
                    database.directory / "jobs" / case["job"]["job_id"]
                    if case["job"]
                    else None
                )
                path = directory / name if directory else None
                try:
                    if path is None:
                        raise FileNotFoundError()
                    with path.open("rb") as stream:
                        raw = stream.read(4 * 1024 * 1024 + 1)
                    if len(raw) > 4 * 1024 * 1024:
                        raise ValueError("Artifact over 4 MiB")
                    artifacts.append(
                        {
                            "case_id": case["case_id"],
                            "name": name,
                            "byte_count": len(raw),
                            "content_sha256": hashlib.sha256(raw).hexdigest(),
                            "content_base64": base64.b64encode(raw).decode("ascii"),
                        }
                    )
                except (OSError, ValueError):
                    missing.append(case["case_id"] + ":" + name)
        value = {
            "bundle_version": "experiment-v1",
            "captured_at": now(),
            "run": run,
            "documents": docs,
            "artifacts": artifacts,
            "missing_artifacts": missing,
        }
        normalized = ExperimentBundle.model_validate(
            {**value, "content_sha256": "0" * 64}
        ).model_dump(mode="json", exclude_unset=True)
        normalized["content_sha256"] = content_hash(
            {k: v for k, v in normalized.items() if k != "content_sha256"}
        )
        return normalized

    app.state.create_experiment_job = create_job
    app.state.experiment_solve_request = solve_request
