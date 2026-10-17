"""Local-first API: immutable snapshots, bounded real Solver jobs and transactional plans."""

from __future__ import annotations

from contextlib import asynccontextmanager
import copy
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import uuid
from typing import Literal

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import delete, select

from backend.app.generated.domain import (
    Capabilities,
    Event,
    Plan,
    Scenario,
    Snapshot,
    SolveJob,
    Validation,
)
from backend.app.analytics import (
    PlanAnalysis,
    ScenarioOrigin,
    WhatIfReceipt,
    WhatIfRequest,
    WhatIfHistory,
    transform,
)
from backend.app.jobs import JobManager, now
from backend.app.imports import GROUPS, csv_template, excel_template, preview
from backend.app.map_assets import image as terrain_image, metadata as terrain_metadata
from backend.app.reports import build_report
from backend.app.storage import (
    ConfirmationRow,
    Database,
    EventRow,
    JobRow,
    PlanRow,
    ReservationRow,
    ScenarioRow,
    ScenarioForkRow,
    SnapshotRow,
    VersionRow,
)
from shared.contracts import (
    ContractError,
    content_hash,
    validate_event,
    validate_options,
    validate_scenario,
    validate_snapshot,
)
from solver.adapters.contest import compact_scenario, contest_scenario
from solver.physics import InputNotReady, parameters
from solver.public_api import capabilities, validate, playback, analyze

ROOT = Path(__file__).resolve().parents[2]


def new_id(prefix):
    return prefix + "-" + uuid.uuid4().hex[:16].upper()


class AppError(Exception):
    def __init__(self, status, code, message, field_path=None, details=None):
        self.status = status
        self.code = code
        self.message = message
        self.field_path = field_path
        self.details = details or {}


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class VersionRequest(StrictModel):
    expected_state_version: int = Field(ge=1)


class ScenarioUpdate(VersionRequest):
    scenario: Scenario


class ExampleRequest(StrictModel):
    example: Literal["compact", "contest"] = "compact"


class CopyRequest(StrictModel):
    name: str | None = None


class SolveRequest(StrictModel):
    snapshot_id: str
    objective: Literal["time", "energy", "balanced"] = "time"
    mode: Literal["quick", "improve", "replan"] = "quick"
    time_limit_s: float = Field(default=15, gt=0, le=300)
    seed: int = Field(default=42, ge=0)
    parent_plan_id: str | None = None
    event_id: str | None = None
    requested_model_scope: list[str] = Field(
        default_factory=lambda: [
            "cargo_unique",
            "capacity",
            "inventory",
            "aircraft",
            "battery",
            "time_window",
            "energy",
        ]
    )
    allow_partial_service: Literal[False] = False


class ConfirmRequest(VersionRequest):
    idempotency_key: str = Field(min_length=1, max_length=128)


class ScenarioSummary(StrictModel):
    scenario_id: str
    name: str
    state_version: int
    data_origin: str
    site_count: int
    cargo_count: int
    drone_count: int
    battery_count: int
    active_plan_id: str | None
    updated_at: str


class Health(StrictModel):
    service_id: Literal["yuanhang-rescue"] = "yuanhang-rescue"
    workspace_id: str
    status: str
    service_version: str
    solver_ready: bool


class PlanSummary(StrictModel):
    plan_id: str
    snapshot_id: str
    scenario_id: str
    scenario_state_version: int
    objective: str
    generated_at: str
    solver_status: str
    metrics: dict
    confirmed_at: str | None


class Progress(StrictModel):
    stage: str
    elapsed_s: float
    candidate_count: int


class EventReceipt(StrictModel):
    event: Event
    state_version_after: int
    applied: bool


class Confirmation(StrictModel):
    plan_id: str
    scenario_id: str
    state_version: int
    confirmation_state: Literal["confirmed"]
    confirmed_at: str


class Comparison(StrictModel):
    plan_id: str
    other_plan_id: str
    same_snapshot: bool
    comparable: bool
    warnings: list[str]
    differences: dict
    preserved_sortie_ids: list[str]
    removed_sortie_ids: list[str]
    added_sortie_ids: list[str]


class ImportPreview(StrictModel):
    scenario: Scenario
    row_count: int
    issues: list[dict]


class PlaybackPhase(StrictModel):
    sortie_id: str
    drone_id: str
    phase: Literal["prepare", "flight", "handover", "return"]
    start_s: float
    end_s: float
    from_coordinates: tuple[float, float]
    to_coordinates: tuple[float, float]


class Playback(StrictModel):
    plan_id: str
    snapshot_id: str
    position_semantics: Literal["schematic_linear_interpolation"]
    is_execution_fact: Literal[False]
    phases: list[PlaybackPhase]


def create_app(runtime_dir: Path | None = None):
    directory = runtime_dir or Path(
        os.environ.get("YUANHANG_RUNTIME", str(ROOT / "runtime"))
    )
    database = Database(directory)

    @asynccontextmanager
    async def lifespan(app):
        database.initialize()
        manager = JobManager(database)
        manager.recover()
        app.state.jobs = manager
        yield
        manager.close()
        database.engine.dispose()

    app = FastAPI(title="援航 · 应急调度API", version="0.1.0", lifespan=lifespan)
    app.state.database = database
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT"],
        allow_headers=["Content-Type", "X-Request-ID"],
    )

    @app.middleware("http")
    async def request_id(request, call_next):
        request.state.request_id = new_id("REQ")
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response

    @app.exception_handler(AppError)
    async def domain_error(request, exc):
        return JSONResponse(
            status_code=exc.status,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "field_path": exc.field_path,
                    "details": exc.details,
                    "request_id": request.state.request_id,
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def invalid_request(request, exc):
        errors = [
            {"field_path": ".".join(str(v) for v in e["loc"]), "message": e["msg"]}
            for e in exc.errors()
        ]
        return await domain_error(
            request,
            AppError(
                422,
                "SCHEMA_INVALID",
                "输入字段或格式不符合契约。",
                details={"errors": errors},
            ),
        )

    def checked_scenario(s):
        try:
            validate_scenario(s)
        except ContractError as exc:
            raise AppError(422, "REFERENCE_INVALID", str(exc)) from exc
        return s

    def require_row(session, model, identity):
        row = session.get(model, identity)
        if row is None:
            raise AppError(
                404, "REFERENCE_INVALID", "未找到指定的场景、快照、任务或方案。"
            )
        return row

    def require_version(row, expected):
        if row.version != expected:
            raise AppError(
                409,
                "STATE_VERSION_CONFLICT",
                "场景已有新版本，请刷新后重试。",
                "expected_state_version",
                {"expected": expected, "actual": row.version},
            )

    def save_new(s, origin=None):
        s = copy.deepcopy(s)
        s.update(scenario_id=new_id("SCN"), state_version=1)
        # Persist exactly the typed representation emitted over HTTP before computing hashes.
        s = Scenario.model_validate(s).model_dump(mode="json")
        checked_scenario(s)
        with database.session(immediate=True) as session:
            session.add(
                ScenarioRow(
                    id=s["scenario_id"],
                    name=s["name"],
                    version=1,
                    content=s,
                    active_plan_id=None,
                    updated_at=now(),
                )
            )
            session.add(
                VersionRow(
                    scenario_id=s["scenario_id"],
                    version=1,
                    content=s,
                    content_hash=content_hash(s),
                )
            )
            if origin is not None:
                session.add(
                    ScenarioForkRow(scenario_id=s["scenario_id"], origin=origin)
                )
        return s

    def snapshot_for(session, row):
        s = copy.deepcopy(row.content)
        snap = {
            "schema_version": s["schema_version"],
            "snapshot_id": new_id("SNAP"),
            "scenario_id": row.id,
            "scenario_state_version": row.version,
            "content_hash": content_hash(s),
            "created_at": now(),
            "scenario": s,
        }
        session.add(
            SnapshotRow(
                id=snap["snapshot_id"],
                scenario_id=row.id,
                version=row.version,
                content=snap,
            )
        )
        return snap

    @app.get("/api/v1/health", response_model=Health)
    def health():
        return {
            "service_id": "yuanhang-rescue",
            "workspace_id": hashlib.sha256(str(ROOT).casefold().encode()).hexdigest()[
                :12
            ],
            "status": "ok",
            "service_version": "0.1.0",
            "solver_ready": True,
        }

    @app.get("/api/v1/meta/capabilities", response_model=Capabilities)
    def meta():
        return capabilities()

    @app.get("/api/v1/map/terrain")
    def map_terrain():
        return terrain_metadata()

    @app.get("/api/v1/map/terrain.png")
    def map_terrain_image():
        return FileResponse(
            terrain_image(directory),
            media_type="image/png",
            headers={"Cache-Control": "public, max-age=86400"},
        )

    @app.get("/api/v1/scenarios", response_model=list[ScenarioSummary])
    def list_scenarios():
        with database.session() as session:
            return [
                {
                    "scenario_id": r.id,
                    "name": r.name,
                    "state_version": r.version,
                    "data_origin": r.content["data_origin"],
                    "site_count": len(r.content["sites"]),
                    "cargo_count": len(r.content["cargo_items"]),
                    "drone_count": sum(
                        d["status"] == "available" for d in r.content["drones"]
                    ),
                    "battery_count": sum(
                        b["status"] == "available" for b in r.content["batteries"]
                    ),
                    "active_plan_id": r.active_plan_id,
                    "updated_at": r.updated_at,
                }
                for r in session.scalars(
                    select(ScenarioRow).order_by(ScenarioRow.updated_at.desc())
                )
            ]

    @app.post("/api/v1/scenarios/examples", response_model=Scenario, status_code=201)
    def load_example(body: ExampleRequest):
        return save_new(
            compact_scenario() if body.example == "compact" else contest_scenario()
        )

    @app.post("/api/v1/scenarios/import", response_model=Scenario, status_code=201)
    def import_scenario(body: Scenario):
        data = body.model_dump(mode="json")
        if data["data_origin"] != "mock":
            data["data_origin"] = "user_input"
        return save_new(data)

    @app.get("/api/v1/plans/{plan_id}/playback", response_model=Playback)
    def plan_playback(plan_id: str):
        with database.session() as session:
            plan = require_row(session, PlanRow, plan_id).content
            snap = require_row(session, SnapshotRow, plan["snapshot_id"]).content
            return playback(plan, snap)

    @app.get("/api/v1/plans/{plan_id}/analysis", response_model=PlanAnalysis)
    def plan_analysis(plan_id: str):
        with database.session() as session:
            plan = require_row(session, PlanRow, plan_id).content
            snap = require_row(session, SnapshotRow, plan["snapshot_id"]).content
            return analyze(snap, plan)

    @app.get("/api/v1/plans/{plan_id}/report", response_class=HTMLResponse)
    def plan_report(plan_id: str):
        with database.session() as session:
            plan = require_row(session, PlanRow, plan_id).content
            snap = require_row(session, SnapshotRow, plan["snapshot_id"]).content
        return HTMLResponse(
            build_report(snap, plan, analyze(snap, plan)),
            headers={
                "Content-Disposition": f'inline; filename="{plan["plan_id"]}-report.html"'
            },
        )

    @app.post(
        "/api/v1/scenarios/{scenario_id}/what-if",
        response_model=WhatIfReceipt,
        status_code=201,
    )
    def what_if(scenario_id: str, body: WhatIfRequest):
        with database.session() as session:
            row = require_row(session, ScenarioRow, scenario_id)
            require_version(row, body.expected_state_version)
            source = copy.deepcopy(row.content)
            if source["data_origin"] == "mock":
                raise AppError(
                    422, "NO_VALIDATED_PLAN", "Mock场景不能作为真实试算基线。"
                )
            if body.source_plan_id:
                plan = require_row(session, PlanRow, body.source_plan_id)
                if plan.scenario_id != scenario_id or plan.version != row.version:
                    raise AppError(
                        409, "SNAPSHOT_STALE", "基线计划与当前场景版本不一致。"
                    )
        try:
            derived, changes = transform(source, body)
        except ValueError as exc:
            raise AppError(422, "SCHEMA_INVALID", str(exc)) from exc
        origin = ScenarioOrigin(
            source_scenario_id=scenario_id,
            source_state_version=source["state_version"],
            source_content_hash=content_hash(source),
            source_plan_id=body.source_plan_id,
            parameters=body,
            changes=changes,
        ).model_dump(mode="json")
        return {"scenario": save_new(derived, origin), "origin": origin}

    @app.get(
        "/api/v1/scenarios/{scenario_id}/origin", response_model=ScenarioOrigin | None
    )
    def scenario_origin(scenario_id: str):
        with database.session() as session:
            require_row(session, ScenarioRow, scenario_id)
            row = session.get(ScenarioForkRow, scenario_id)
            return row.origin if row else None

    @app.get(
        "/api/v1/scenarios/{scenario_id}/what-if", response_model=list[WhatIfHistory]
    )
    def what_if_history(scenario_id: str):
        with database.session() as session:
            require_row(session, ScenarioRow, scenario_id)
            forks = list(
                session.scalars(
                    select(ScenarioForkRow).where(
                        ScenarioForkRow.origin["source_scenario_id"].as_string()
                        == scenario_id
                    )
                )
            )
            result = []
            for fork in forks:
                scene = require_row(session, ScenarioRow, fork.scenario_id)
                jobs = list(
                    session.scalars(
                        select(JobRow).where(JobRow.scenario_id == fork.scenario_id)
                    )
                )
                jobs = [
                    job
                    for job in jobs
                    if require_row(
                        session, SnapshotRow, job.content["snapshot_id"]
                    ).version
                    == 1
                ]
                job = max(jobs, key=lambda j: j.content["created_at"], default=None)
                plans = list(
                    session.scalars(
                        select(PlanRow).where(
                            PlanRow.scenario_id == fork.scenario_id,
                            PlanRow.version == 1,
                        )
                    )
                )
                plan = max(plans, key=lambda p: p.content["generated_at"], default=None)
                result.append(
                    {
                        "scenario_id": scene.id,
                        "name": scene.name,
                        "scenario_state_version": scene.version,
                        "origin": fork.origin,
                        "job": job.content if job else None,
                        "plan": plan.content if plan else None,
                    }
                )
            return list(reversed(result))

    @app.post("/api/v1/scenarios/import-file", response_model=ImportPreview)
    async def import_file(
        file: UploadFile = File(...),
        scenario_id: str | None = None,
        entity: str | None = None,
    ):
        data = await file.read(12 * 1024 * 1024 + 1)
        if len(data) > 12 * 1024 * 1024:
            raise AppError(422, "SCHEMA_INVALID", "文件超出12MiB导入限制。")
        current = None
        if scenario_id:
            with database.session() as session:
                current = require_row(session, ScenarioRow, scenario_id).content
        try:
            return preview(file.filename or "", data, current, entity)
        except Exception as exc:
            raise AppError(
                422,
                "SCHEMA_INVALID",
                "文件预览校验失败：" + str(exc)[:1200],
                details={"filename": file.filename},
            ) from exc

    @app.get("/api/v1/scenarios/{scenario_id}/template")
    def template(
        scenario_id: str,
        format: Literal["csv", "xlsx"] = "xlsx",
        entity: str = "cargo_items",
    ):
        with database.session() as session:
            s = require_row(session, ScenarioRow, scenario_id).content
        if format == "csv":
            if entity not in GROUPS:
                raise AppError(422, "SCHEMA_INVALID", "请选择合法实体表。")
            return Response(
                csv_template(s, entity),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f'attachment; filename="yuanhang-{entity}.csv"'
                },
            )
        return Response(
            excel_template(s),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": 'attachment; filename="yuanhang-scenario.xlsx"'
            },
        )

    @app.get("/api/v1/scenarios/{scenario_id}", response_model=Scenario)
    def get_scenario(scenario_id: str):
        with database.session() as session:
            return require_row(session, ScenarioRow, scenario_id).content

    @app.put("/api/v1/scenarios/{scenario_id}", response_model=Scenario)
    def update_scenario(scenario_id: str, body: ScenarioUpdate):
        s = body.scenario.model_dump(mode="json")
        if s["scenario_id"] != scenario_id:
            raise AppError(422, "REFERENCE_INVALID", "路径和正文场景ID不一致。")
        with database.session(immediate=True) as session:
            row = require_row(session, ScenarioRow, scenario_id)
            require_version(row, body.expected_state_version)
            s["state_version"] = row.version + 1
            # Editing is user input, never an upgrade to a verified dataset.
            if s["data_origin"] != "mock":
                s["data_origin"] = "user_input"
            checked_scenario(s)
            row.version = s["state_version"]
            row.name = s["name"]
            row.content = s
            row.updated_at = now()
            session.add(
                VersionRow(
                    scenario_id=row.id,
                    version=row.version,
                    content=s,
                    content_hash=content_hash(s),
                )
            )
            return s

    @app.post(
        "/api/v1/scenarios/{scenario_id}/copy", response_model=Scenario, status_code=201
    )
    def copy_scenario(scenario_id: str, body: CopyRequest):
        with database.session() as session:
            s = copy.deepcopy(require_row(session, ScenarioRow, scenario_id).content)
        s["name"] = body.name or s["name"] + " · 副本"
        return save_new(s)

    @app.post("/api/v1/scenarios/{scenario_id}/validate", response_model=Validation)
    def validate_input(scenario_id: str, body: VersionRequest):
        with database.session() as session:
            row = require_row(session, ScenarioRow, scenario_id)
            require_version(row, body.expected_state_version)
            s = row.content
        checked_scenario(s)
        checks = []
        for code in [
            "cargo_unique",
            "capacity",
            "inventory",
            "aircraft",
            "battery",
            "time_window",
            "energy",
        ]:
            checks.append(
                {
                    "code": code,
                    "status": "not_evaluated",
                    "object_id": None,
                    "message": "结构和引用可读取；物理与排程资格将在真实求解独立重算。",
                }
            )
        try:
            for t in s["drone_types"]:
                parameters(t)
        except InputNotReady as exc:
            checks.append(
                {
                    "code": "energy",
                    "status": "failed",
                    "object_id": None,
                    "message": str(exc),
                }
            )
        return {
            "status": (
                "failed" if any(c["status"] == "failed" for c in checks) else "partial"
            ),
            "checks": checks,
        }

    @app.post(
        "/api/v1/scenarios/{scenario_id}/snapshots",
        response_model=Snapshot,
        status_code=201,
    )
    def make_snapshot(scenario_id: str, body: VersionRequest):
        with database.session(immediate=True) as session:
            row = require_row(session, ScenarioRow, scenario_id)
            require_version(row, body.expected_state_version)
            return snapshot_for(session, row)

    @app.get("/api/v1/snapshots/{snapshot_id}", response_model=Snapshot)
    def get_snapshot(snapshot_id: str):
        with database.session() as session:
            return require_row(session, SnapshotRow, snapshot_id).content

    @app.post("/api/v1/solve-jobs", response_model=SolveJob, status_code=202)
    def create_job(body: SolveRequest):
        with database.session(immediate=True) as session:
            snap = require_row(session, SnapshotRow, body.snapshot_id).content
            queued = len(
                list(
                    session.scalars(
                        select(JobRow).where(JobRow.state.in_(["queued", "running"]))
                    )
                )
            )
            if queued >= 4:
                raise AppError(
                    503, "SOLVER_BUSY", "当前已有4个计算任务，请稍候或取消。"
                )
            job_id, plan_id = new_id("JOB"), new_id("PLAN")
            options = {
                "schema_version": snap["schema_version"],
                "plan_id": plan_id,
                **body.model_dump(),
            }
            if (
                snap["scenario"]["policy"]["requires_terrain"]
                and "terrain" not in options["requested_model_scope"]
            ):
                options["requested_model_scope"].append("terrain")
            try:
                validate_options(options, snap)
            except ContractError as exc:
                raise AppError(422, "SCHEMA_INVALID", str(exc)) from exc
            payload = {"snapshot": snap, "options": options}
            if body.mode == "replan":
                old = require_row(session, PlanRow, body.parent_plan_id).content
                event = require_row(
                    session, EventRow, (snap["scenario_id"], body.event_id)
                )
                if (
                    old["scenario_id"] != snap["scenario_id"]
                    or event.version_after != snap["scenario_state_version"]
                    or old["scenario_state_version"] >= snap["scenario_state_version"]
                ):
                    raise AppError(
                        422,
                        "REFERENCE_INVALID",
                        "事件、旧计划与事件后快照的版本链不一致。",
                    )
                payload.update(previous_plan=old, event=event.content)
            job = {
                "schema_version": snap["schema_version"],
                "job_id": job_id,
                "scenario_id": snap["scenario_id"],
                "snapshot_id": body.snapshot_id,
                "reserved_plan_id": plan_id,
                "job_state": "queued",
                "solver_status": None,
                "plan_id": None,
                "has_validated_plan": False,
                "runtime_s": None,
                "stop_reason": None,
                "created_at": now(),
                "started_at": None,
                "finished_at": None,
                "error": None,
            }
            session.add(
                JobRow(
                    id=job_id,
                    scenario_id=snap["scenario_id"],
                    state="queued",
                    content=job,
                    options=options,
                    outcome=None,
                    progress={},
                    cancel_requested=False,
                )
            )
        app.state.jobs.submit(job_id, payload)
        return job

    @app.get("/api/v1/solve-jobs/{job_id}", response_model=SolveJob)
    def get_job(job_id: str):
        with database.session() as session:
            return require_row(session, JobRow, job_id).content

    @app.get(
        "/api/v1/scenarios/{scenario_id}/solve-jobs", response_model=list[SolveJob]
    )
    def scenario_jobs(scenario_id: str):
        with database.session() as session:
            require_row(session, ScenarioRow, scenario_id)
            rows = list(
                session.scalars(select(JobRow).where(JobRow.scenario_id == scenario_id))
            )
            return [
                r.content
                for r in sorted(
                    rows, key=lambda r: r.content["created_at"], reverse=True
                )
            ]

    @app.get("/api/v1/solve-jobs/{job_id}/progress", response_model=Progress)
    def get_progress(job_id: str):
        with database.session() as session:
            require_row(session, JobRow, job_id)
        return app.state.jobs.progress(job_id)

    @app.get("/api/v1/solve-jobs/{job_id}/diagnostics")
    def get_job_diagnostics(job_id: str):
        with database.session() as session:
            row = require_row(session, JobRow, job_id)
            return {
                "diagnostics": row.outcome["diagnostics"] if row.outcome else [],
                "validation": row.outcome["validation"] if row.outcome else None,
            }

    @app.post(
        "/api/v1/solve-jobs/{job_id}/cancel", response_model=SolveJob, status_code=202
    )
    def cancel_job(job_id: str):
        result = app.state.jobs.cancel(job_id)
        if result is None:
            raise AppError(404, "REFERENCE_INVALID", "计算任务不存在。")
        return result

    @app.get("/api/v1/scenarios/{scenario_id}/plans", response_model=list[PlanSummary])
    def list_plans(scenario_id: str):
        with database.session() as session:
            require_row(session, ScenarioRow, scenario_id)
            rows = list(
                session.scalars(
                    select(PlanRow).where(PlanRow.scenario_id == scenario_id)
                )
            )
            rows.sort(key=lambda r: r.content["generated_at"], reverse=True)
            return [
                {
                    k: r.content[k]
                    for k in [
                        "plan_id",
                        "snapshot_id",
                        "scenario_id",
                        "scenario_state_version",
                        "objective",
                        "generated_at",
                        "solver_status",
                        "metrics",
                    ]
                }
                | {"confirmed_at": r.confirmed_at}
                for r in rows
            ]

    @app.get("/api/v1/plans/{plan_id}", response_model=Plan)
    def get_plan(plan_id: str):
        with database.session() as session:
            return require_row(session, PlanRow, plan_id).content

    @app.get("/api/v1/plans/{plan_id}/comparison", response_model=Comparison)
    def compare(plan_id: str, other_plan_id: str):
        with database.session() as session:
            a = require_row(session, PlanRow, plan_id).content
            b = require_row(session, PlanRow, other_plan_id).content
        same = a["snapshot_id"] == b["snapshot_id"]
        warnings = []
        if a["scenario_id"] != b["scenario_id"]:
            warnings.append("来自不同场景，只能查看差异。")
        if not same:
            warnings.append("不同快照：这是状态变化前后对比，不是同条件策略优势。")
        if a["model_scope"] != b["model_scope"]:
            warnings.append("验证范围不同。")
        differences = {
            k: (
                (b["metrics"][k] - a["metrics"][k])
                if a["metrics"][k] is not None and b["metrics"][k] is not None
                else None
            )
            for k in a["metrics"]
        }
        old = {r["sortie_id"] for r in a["sorties"]}
        new = {r["sortie_id"] for r in b["sorties"]}
        return {
            "plan_id": plan_id,
            "other_plan_id": other_plan_id,
            "same_snapshot": same,
            "comparable": same and not warnings,
            "warnings": warnings,
            "differences": differences,
            "preserved_sortie_ids": sorted(old & new),
            "removed_sortie_ids": sorted(old - new),
            "added_sortie_ids": sorted(new - old),
        }

    @app.post("/api/v1/plans/{plan_id}/confirm", response_model=Confirmation)
    def confirm(plan_id: str, body: ConfirmRequest):
        digest = hashlib.sha256(
            json.dumps(
                {"plan_id": plan_id, **body.model_dump()}, sort_keys=True
            ).encode()
        ).hexdigest()
        with database.session(immediate=True) as session:
            existing = session.get(ConfirmationRow, body.idempotency_key)
            if existing:
                if existing.request_hash != digest:
                    raise AppError(
                        409, "RESOURCE_CONFLICT", "相同幂等键已用于不同确认请求。"
                    )
                return existing.response
            row = require_row(session, PlanRow, plan_id)
            plan = row.content
            scenario = require_row(session, ScenarioRow, row.scenario_id)
            require_version(scenario, body.expected_state_version)
            if row.version != scenario.version:
                raise AppError(
                    409, "SNAPSHOT_STALE", "方案来自旧快照，不能直接确认为当前计划。"
                )
            snap = require_row(session, SnapshotRow, row.snapshot_id).content
            if content_hash(scenario.content) != snap["content_hash"]:
                raise AppError(409, "SNAPSHOT_STALE", "当前输入与方案快照不同。")
            if (
                plan["data_origin"] != "solver"
                or not plan["has_validated_plan"]
                or validate(snap, plan)["status"] != "passed"
            ):
                raise AppError(
                    422, "NO_VALIDATED_PLAN", "方案未通过本次模型范围的独立检查。"
                )
            # P0 has no actual execution facts; switch reservations atomically in this scenario only.
            session.execute(
                delete(ReservationRow).where(ReservationRow.scenario_id == scenario.id)
            )
            for r in plan["sorties"]:
                for kind, rid, end in [
                    ("drone", r["drone_id"], r["drone_released_s"]),
                    ("battery", r["battery_id"], r["battery_released_s"]),
                ]:
                    session.add(
                        ReservationRow(
                            scenario_id=scenario.id,
                            plan_id=plan_id,
                            kind=kind,
                            resource_id=rid,
                            start_s=r["prepare_start_s"],
                            end_s=end,
                        )
                    )
                for cid in r["cargo_ids"]:
                    session.add(
                        ReservationRow(
                            scenario_id=scenario.id,
                            plan_id=plan_id,
                            kind="cargo",
                            resource_id=cid,
                            start_s=0,
                            end_s=r["return_s"],
                        )
                    )
            when = now()
            scenario.active_plan_id = plan_id
            row.confirmed_at = when
            response = {
                "plan_id": plan_id,
                "scenario_id": scenario.id,
                "state_version": scenario.version,
                "confirmation_state": "confirmed",
                "confirmed_at": when,
            }
            session.add(
                ConfirmationRow(
                    key=body.idempotency_key, request_hash=digest, response=response
                )
            )
            return response

    @app.post("/api/v1/events", response_model=EventReceipt)
    def apply_event(body: Event):
        value = body.model_dump(mode="json")
        request_body = {k: v for k, v in value.items() if k != "received_at"}
        digest = content_hash(request_body)
        with database.session(immediate=True) as session:
            existing = session.get(EventRow, (value["scenario_id"], value["event_id"]))
            if existing:
                if existing.request_hash != digest:
                    raise AppError(
                        409,
                        "RESOURCE_CONFLICT",
                        "相同事件ID的内容不同，不能覆盖既有事件。",
                    )
                return {
                    "event": existing.content,
                    "state_version_after": existing.version_after,
                    "applied": False,
                }
            row = require_row(session, ScenarioRow, value["scenario_id"])
            require_version(row, value["expected_state_version"])
            try:
                validate_event(value, row.content)
            except ContractError as exc:
                raise AppError(422, "UNSUPPORTED_EVENT_STATE", str(exc)) from exc
            s = copy.deepcopy(row.content)
            next(
                d for d in s["drones"] if d["drone_id"] == value["payload"]["drone_id"]
            )["status"] = "unavailable"
            s["state_version"] = row.version + 1
            value["received_at"] = now()
            row.version = s["state_version"]
            row.content = s
            row.updated_at = now()
            row.active_plan_id = None
            session.add(
                VersionRow(
                    scenario_id=row.id,
                    version=row.version,
                    content=s,
                    content_hash=content_hash(s),
                )
            )
            session.add(
                EventRow(
                    scenario_id=row.id,
                    id=value["event_id"],
                    request_hash=digest,
                    content=value,
                    version_after=row.version,
                )
            )
            session.execute(
                delete(ReservationRow).where(ReservationRow.scenario_id == row.id)
            )
            return {"event": value, "state_version_after": row.version, "applied": True}

    @app.get("/api/v1/scenarios/{scenario_id}/events", response_model=list[Event])
    def list_events(scenario_id: str):
        with database.session() as session:
            require_row(session, ScenarioRow, scenario_id)
            return [
                r.content
                for r in session.scalars(
                    select(EventRow)
                    .where(EventRow.scenario_id == scenario_id)
                    .order_by(EventRow.version_after)
                )
            ]

    @app.get("/api/v1/plans/{plan_id}/export")
    def export_plan(plan_id: str, format: Literal["json", "csv", "geojson"] = "json"):
        with database.session() as session:
            plan = copy.deepcopy(require_row(session, PlanRow, plan_id).content)
        headers = {"Content-Disposition": f'attachment; filename="{plan_id}.{format}"'}
        if format == "json":
            return JSONResponse(content=plan, headers=headers)
        if format == "geojson":
            features = [
                {
                    "type": "Feature",
                    "properties": {
                        "plan_id": plan_id,
                        "snapshot_id": plan["snapshot_id"],
                        "data_origin": plan["data_origin"],
                        **{
                            k: r[k]
                            for k in [
                                "sortie_id",
                                "drone_id",
                                "battery_id",
                                "takeoff_s",
                                "return_s",
                                "energy_kwh",
                            ]
                        },
                    },
                    "geometry": r["route_geometry"],
                }
                for r in plan["sorties"]
            ]
            return Response(
                json.dumps(
                    {"type": "FeatureCollection", "features": features},
                    ensure_ascii=False,
                ),
                media_type="application/geo+json",
                headers=headers,
            )
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(
            [
                "plan_id",
                "snapshot_id",
                "data_origin",
                "sortie_id",
                "drone_id",
                "battery_id",
                "cargo_id",
                "site_id",
                "prepare_start_s",
                "takeoff_s",
                "delivery_complete_s",
                "return_s",
                "energy_kwh",
                "return_soc",
            ]
        )
        for r in plan["sorties"]:
            for v in r["visits"]:
                for cid in v["cargo_ids"]:
                    writer.writerow(
                        [
                            plan_id,
                            plan["snapshot_id"],
                            plan["data_origin"],
                            r["sortie_id"],
                            r["drone_id"],
                            r["battery_id"],
                            cid,
                            v["site_id"],
                            r["prepare_start_s"],
                            r["takeoff_s"],
                            v["delivery_complete_s"],
                            r["return_s"],
                            r["energy_kwh"],
                            r["return_soc"],
                        ]
                    )
        return Response(
            "\ufeff" + buffer.getvalue(),
            media_type="text/csv; charset=utf-8",
            headers=headers,
        )

    @app.get("/api/v1/scenarios/{scenario_id}/export", response_model=Scenario)
    def export_scenario(scenario_id: str):
        return get_scenario(scenario_id)

    @app.get("/api/v1/scenarios/{scenario_id}/bundle")
    def export_bundle(scenario_id: str):
        with database.session() as session:
            row = require_row(session, ScenarioRow, scenario_id)
            return {
                "bundle_version": "0.1.0",
                "scenario": row.content,
                "snapshots": [
                    r.content
                    for r in session.scalars(
                        select(SnapshotRow).where(
                            SnapshotRow.scenario_id == scenario_id
                        )
                    )
                ],
                "plans": [
                    r.content
                    for r in session.scalars(
                        select(PlanRow).where(PlanRow.scenario_id == scenario_id)
                    )
                ],
                "events": [
                    r.content
                    for r in session.scalars(
                        select(EventRow).where(EventRow.scenario_id == scenario_id)
                    )
                ],
            }

    frontend = ROOT / "frontend/dist"
    if frontend.is_dir():
        assets = frontend / "assets"
        if assets.is_dir():
            app.mount("/assets", StaticFiles(directory=assets), name="ui-assets")

        @app.get("/{path:path}", include_in_schema=False)
        def frontend_index(path: str):
            if path.startswith(("api/", "openapi")):
                raise AppError(404, "REFERENCE_INVALID", "接口不存在。")
            return FileResponse(frontend / "index.html")

    return app


app = create_app()
