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

from fastapi import (
    FastAPI,
    File,
    Form,
    Query,
    Request,
    UploadFile,
    Path as PathParameter,
)
from starlette.concurrency import run_in_threadpool
from rasterio.errors import RasterioError
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.routing import APIRoute
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
    Communication,
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
from backend.app.map_assets import (
    image as terrain_image,
    metadata as terrain_metadata,
    surface as terrain_surface,
)
from backend.app.map_models import TerrainSurface
from backend.app.flight_profiles import FlightProfile, flight_profile
from backend.app.version_views import ScenarioVersionSummary
from backend.app.reports import build_report
from backend.app.partition_views import PartitionReport
from backend.app.nominal_views import NominalReport
from backend.app.terrain_assets import (
    TerrainAsset,
    catalog as terrain_catalog,
    register as register_terrain,
    describe as describe_terrain,
)
from solver.assets import terrain_store, terrain_info
from backend.app.terrain_packages import (
    export_package as export_terrain_package,
    import_package as import_terrain_package,
)
from backend.app.storage import (
    ConfirmationRow,
    Database,
    EventRow,
    JobRow,
    PlanRow,
    PlanRefinementRow,
    ReservationRow,
    ScenarioRow,
    ScenarioForkRow,
    SnapshotRow,
    VersionRow,
)
from shared.contracts import (
    ContractError,
    content_hash,
    validate_options,
    validate_scenario,
    validate_snapshot,
    apply_event_to_scenario,
)
from shared.build_info import service_fingerprint
from solver.adapters.contest import (
    compact_scenario,
    contest_scenario,
    contest_communication,
)
from solver.physics import InputNotReady, parameters, terrain_maximum
from solver.public_api import (
    capabilities,
    validate,
    playback,
    analyze,
    analyze_single_site,
)
from solver.partition import partition

ROOT = Path(__file__).resolve().parents[2]
STARTUP_SOURCE_SHA256 = service_fingerprint(ROOT)


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


class PreserveMissingFieldsRoute(APIRoute):
    """Omitted optional extensions must not change old Snapshot wire hashes."""

    def __init__(self, *args, **kwargs):
        kwargs["response_model_exclude_unset"] = True
        super().__init__(*args, **kwargs)


class VersionRequest(StrictModel):
    expected_state_version: int = Field(ge=1)


class ScenarioUpdate(VersionRequest):
    scenario: Scenario


class TerrainAssignment(VersionRequest):
    asset_id: str
    sha256: str = Field(pattern="^[a-f0-9]{64}$")
    update_dem_elevations: bool = True


class TerrainMap(StrictModel):
    asset_id: str
    name: str
    sha256: str
    bounds: tuple[float, float, float, float]
    coordinates: tuple[
        tuple[float, float],
        tuple[float, float],
        tuple[float, float],
        tuple[float, float],
    ]
    crs: str
    source: str
    notice: str
    image_url: str


class ExampleRequest(StrictModel):
    example: Literal["compact", "contest"] = "compact"


class CopyRequest(StrictModel):
    name: str | None = None


class SolveRequest(StrictModel):
    snapshot_id: str
    objective: Literal["time", "energy", "balanced"] = "time"
    objective_policy: Literal["deadline_first_v1", "tradeoff_v2"] = "deadline_first_v1"
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
    initial_plan_id: str | None = None


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
    service_source_sha256: str
    runtime_id: str


class PlanSummary(StrictModel):
    plan_id: str
    snapshot_id: str
    scenario_id: str
    scenario_state_version: int
    objective: str
    objective_policy: Literal["deadline_first_v1", "tradeoff_v2"] = "deadline_first_v1"
    generated_at: str
    solver_status: str
    metrics: dict
    confirmed_at: str | None
    algorithm_mode: Literal["quick", "improve", "replan"] = "quick"
    source_plan_id: str | None = None


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
        from backend.app.simulation import SimulationEngine

        app.state.simulation = SimulationEngine(
            database, AppError, command_tick=app.state.simulation_commands_tick
        )
        yield
        app.state.simulation.close()
        manager.close()
        database.engine.dispose()

    app = FastAPI(title="援航 · 应急调度API", version="0.1.0", lifespan=lifespan)
    app.router.route_class = PreserveMissingFieldsRoute
    app.state.database = database
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH"],
        allow_headers=["Content-Type", "X-Request-ID"],
    )

    @app.middleware("http")
    async def request_id(request, call_next):
        request.state.request_id = new_id("REQ")
        with terrain_store(directory / "assets"):
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
        s = Scenario.model_validate(s).model_dump(mode="json", exclude_unset=True)
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
            "service_source_sha256": STARTUP_SOURCE_SHA256,
            "runtime_id": hashlib.sha256(
                str(directory.resolve()).casefold().encode()
            ).hexdigest()[:12],
        }

    @app.get("/api/v1/meta/capabilities", response_model=Capabilities)
    def meta():
        return capabilities()

    @app.get("/api/v1/map/terrain", response_model=TerrainMap)
    def map_terrain(asset_id: str | None = None, sha256: str | None = None):
        try:
            return terrain_metadata(asset_id, sha256)
        except InputNotReady as exc:
            raise AppError(422, "SCHEMA_INVALID", str(exc), "terrain") from exc

    @app.get("/api/v1/map/terrain/{asset_id}/{sha256}.png")
    def bound_terrain_image(asset_id: str, sha256: str):
        try:
            return FileResponse(
                terrain_image(directory, asset_id, sha256),
                media_type="image/png",
                headers={"Cache-Control": "public, max-age=31536000, immutable"},
            )
        except InputNotReady as exc:
            raise AppError(422, "SCHEMA_INVALID", str(exc), "terrain") from exc

    @app.get("/api/v1/map/surface", response_model=TerrainSurface)
    def map_surface(
        asset_id: str = Query(
            pattern="^(contest-dem-30m|DEM-[a-f0-9]{20})$", max_length=32
        ),
        sha256: str = Query(pattern="^[a-f0-9]{64}$", max_length=64),
    ):
        try:
            return terrain_surface(asset_id, sha256)
        except InputNotReady as exc:
            raise AppError(422, "SCHEMA_INVALID", str(exc), "terrain") from exc

    @app.get("/api/v1/map/terrain.png")
    def map_terrain_image():
        return FileResponse(
            terrain_image(directory),
            media_type="image/png",
            headers={"Cache-Control": "public, max-age=86400"},
        )

    @app.get(
        "/api/v1/scenarios/{scenario_id}/versions",
        response_model=list[ScenarioVersionSummary],
    )
    def scenario_versions(scenario_id: str):
        with database.session() as session:
            require_row(session, ScenarioRow, scenario_id)
            rows = session.scalars(
                select(VersionRow)
                .where(VersionRow.scenario_id == scenario_id)
                .order_by(VersionRow.version.desc())
            ).all()
            return [
                {
                    "scenario_id": row.scenario_id,
                    "state_version": row.version,
                    "name": row.content["name"],
                    "content_hash": row.content_hash,
                    # VersionRow never stored a timestamp. Current updated_at is not its date.
                    "created_at": None,
                    "data_origin": row.content["data_origin"],
                    "site_count": len(row.content["sites"]),
                    "cargo_count": len(row.content["cargo_items"]),
                    "drone_count": len(row.content["drones"]),
                    "battery_count": len(row.content["batteries"]),
                }
                for row in rows
            ]

    @app.get(
        "/api/v1/scenarios/{scenario_id}/versions/{version}", response_model=Scenario
    )
    def scenario_version(scenario_id: str, version: int = PathParameter(ge=1)):
        with database.session() as session:
            require_row(session, ScenarioRow, scenario_id)
            return require_row(session, VersionRow, (scenario_id, version)).content

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

    @app.get("/api/v1/terrain-assets", response_model=list[TerrainAsset])
    def list_terrain_assets():
        return terrain_catalog(directory / "assets")

    @app.post("/api/v1/terrain-assets", response_model=TerrainAsset, status_code=201)
    async def upload_terrain(
        file: UploadFile = File(...), vertical_datum: str = Form(...)
    ):
        data = await file.read(16 * 1024 * 1024 + 1)
        try:
            return await run_in_threadpool(
                register_terrain,
                directory / "assets",
                data,
                file.filename or "local-dem.tif",
                vertical_datum,
            )
        except (ValueError, RasterioError, OSError) as exc:
            raise AppError(422, "SCHEMA_INVALID", str(exc), "terrain") from exc

    @app.get("/api/v1/terrain-assets/{asset_id}/source")
    def download_terrain(asset_id: str, sha256: str):
        try:
            info = terrain_info(asset_id, sha256)
            digest = info.get("source_sha256")
            if digest is None:
                path = next(
                    (ROOT / "references/modeling/data/terrain").glob("*DEM.mat")
                )
                return FileResponse(path, filename="contest-dem.mat")
            if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
                raise InputNotReady("来源hash无效。")
            root = (directory / "assets/sources").resolve()
            path = (root / (digest + ".tif")).resolve()
            if path.parent != root or not path.is_file():
                raise InputNotReady("DEM原始文件缺失。")
            if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                raise InputNotReady("DEM原始文件内容hash不一致。")
            return FileResponse(path, filename=info["name"])
        except InputNotReady as exc:
            raise AppError(422, "SCHEMA_INVALID", str(exc), "terrain") from exc

    @app.get("/api/v1/terrain-assets/{asset_id}/package")
    def download_terrain_package(asset_id: str, sha256: str):
        try:
            data = export_terrain_package(directory / "assets", asset_id, sha256)
            return Response(
                data,
                media_type="application/zip",
                headers={
                    "Content-Disposition": f'attachment; filename="{asset_id}.yuanhang-dem.zip"'
                },
            )
        except (ValueError, OSError) as exc:
            raise AppError(422, "SCHEMA_INVALID", str(exc), "terrain") from exc

    @app.post(
        "/api/v1/terrain-assets/import-package",
        response_model=TerrainAsset,
        status_code=201,
    )
    async def upload_terrain_package(file: UploadFile = File(...)):
        data = await file.read(40 * 1024 * 1024 + 1)
        try:
            return await run_in_threadpool(
                import_terrain_package, directory / "assets", data
            )
        except (ValueError, RasterioError, OSError) as exc:
            raise AppError(422, "SCHEMA_INVALID", str(exc), "terrain") from exc

    @app.post("/api/v1/scenarios/{scenario_id}/terrain", response_model=Scenario)
    def assign_terrain(scenario_id: str, body: TerrainAssignment):
        with database.session() as session:
            row = require_row(session, ScenarioRow, scenario_id)
            require_version(row, body.expected_state_version)
            s = copy.deepcopy(row.content)
        try:
            asset = describe_terrain(body.asset_id, body.sha256)
            for node in [s["base"], *s["sites"]]:
                coordinates = tuple(node["coordinates"])
                elevation = terrain_maximum(
                    body.asset_id, body.sha256, coordinates, coordinates
                )
                if body.update_dem_elevations:
                    node["ground_elevation_m"] = elevation
            s["terrain"] = asset["terrain"]
            s["policy"]["requires_terrain"] = True
        except InputNotReady as exc:
            raise AppError(422, "SCHEMA_INVALID", str(exc), "terrain") from exc
        return update_scenario(
            scenario_id,
            ScenarioUpdate(
                expected_state_version=body.expected_state_version, scenario=s
            ),
        )

    @app.post("/api/v1/scenarios/examples", response_model=Scenario, status_code=201)
    def load_example(body: ExampleRequest):
        return save_new(
            compact_scenario() if body.example == "compact" else contest_scenario()
        )

    @app.post("/api/v1/scenarios/import", response_model=Scenario, status_code=201)
    def import_scenario(body: Scenario):
        data = body.model_dump(mode="json", exclude_unset=True)
        if data["data_origin"] != "mock":
            data["data_origin"] = "user_input"
        return save_new(data)

    @app.get(
        "/api/v1/scenarios/{scenario_id}/communication-template",
        response_model=Communication,
    )
    def communication_template(scenario_id: str):
        with database.session() as session:
            scenario = require_row(session, ScenarioRow, scenario_id).content
            # Read-only suggestion. Applying it uses normal versioned Scenario PUT.
            return contest_communication(scenario)

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

    @app.get("/api/v1/plans/{plan_id}/flight-profile", response_model=FlightProfile)
    def plan_flight_profile(
        plan_id: str,
        sortie_id: str = Query(
            min_length=1, max_length=128, pattern="^[A-Za-z0-9][A-Za-z0-9_.:-]*$"
        ),
    ):
        with database.session() as session:
            plan = require_row(session, PlanRow, plan_id).content
            snap = require_row(session, SnapshotRow, plan["snapshot_id"]).content
        try:
            return flight_profile(snap, plan, sortie_id)
        except KeyError as exc:
            raise AppError(
                404, "REFERENCE_INVALID", "此方案不包含指定运输架次。", "sortie_id"
            ) from exc
        except InputNotReady as exc:
            raise AppError(422, "SCHEMA_INVALID", str(exc), "terrain") from exc

    @app.get("/api/v1/plans/{plan_id}/partition", response_model=PartitionReport)
    def plan_partition(plan_id: str):
        with database.session() as session:
            # Hash the same JSON representation emitted by GET /plans/{id}.
            # Pydantic normalizes UTC datetime strings (+00:00 -> Z).
            plan = Plan.model_validate(
                require_row(session, PlanRow, plan_id).content
            ).model_dump(mode="json", exclude_unset=True)
            snap = require_row(session, SnapshotRow, plan["snapshot_id"]).content
        return partition(snap, plan)

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
            transformation_version=(
                "what_if_v2_ground_capacity"
                if body.ground_addition is not None
                else "what_if_v1"
            ),
            parameters=body,
            changes=changes,
        ).model_dump(mode="json")
        if body.ground_addition is None:
            # Preserve the existing v1 wire shape for omitted/null extensions.
            origin["parameters"].pop("ground_addition", None)
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
        s = body.scenario.model_dump(mode="json", exclude_unset=True)
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

    @app.get(
        "/api/v1/snapshots/{snapshot_id}/single-site-analysis",
        response_model=NominalReport,
    )
    def single_site_analysis(
        snapshot_id: str, min_return_soc: float | None = Query(None, ge=0, le=1)
    ):
        with database.session() as session:
            snap = require_row(session, SnapshotRow, snapshot_id).content
        return analyze_single_site(snap, min_return_soc)

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
                **body.model_dump(exclude={"initial_plan_id"}),
            }
            if (
                snap["scenario"].get("resource_limits")
                and "ground_resource" not in options["requested_model_scope"]
            ):
                options["requested_model_scope"].append("ground_resource")
            if (
                snap["scenario"].get("restricted_zones")
                and "restricted_zone" not in options["requested_model_scope"]
            ):
                options["requested_model_scope"].append("restricted_zone")
            if (
                snap["scenario"]["policy"]["requires_terrain"]
                and "terrain" not in options["requested_model_scope"]
            ):
                options["requested_model_scope"].append("terrain")
            if (
                snap["scenario"]["policy"]["requires_communication"]
                and "communication" not in options["requested_model_scope"]
            ):
                options["requested_model_scope"].append("communication")
            if (
                snap["scenario"].get("weather")
                and "weather_window" not in options["requested_model_scope"]
            ):
                options["requested_model_scope"].append("weather_window")
            try:
                validate_options(options, snap)
            except ContractError as exc:
                raise AppError(422, "SCHEMA_INVALID", str(exc)) from exc
            payload = {"snapshot": snap, "options": options}
            if body.initial_plan_id:
                if body.mode != "improve":
                    raise AppError(
                        422, "SCHEMA_INVALID", "initial_plan_id仅用于深入优化。"
                    )
                base = require_row(session, PlanRow, body.initial_plan_id)
                if (
                    base.snapshot_id != body.snapshot_id
                    or base.content["objective"] != body.objective
                    or base.content.get("objective_policy", "deadline_first_v1")
                    != body.objective_policy
                ):
                    raise AppError(
                        409,
                        "SNAPSHOT_STALE",
                        "深入优化基线必须来自同一快照、相同目标和目标规则版本。",
                    )
                payload["initial_plan"] = base.content
                session.add(PlanRefinementRow(plan_id=plan_id, source_plan_id=base.id))
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
            modes = {
                j.content["reserved_plan_id"]: j.options["mode"]
                for j in session.scalars(
                    select(JobRow).where(JobRow.scenario_id == scenario_id)
                )
            }
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
                | {
                    "objective_policy": r.content.get(
                        "objective_policy", "deadline_first_v1"
                    ),
                    "confirmed_at": r.confirmed_at,
                    "algorithm_mode": modes.get(r.id, "quick"),
                    "source_plan_id": (
                        refinement.source_plan_id
                        if (refinement := session.get(PlanRefinementRow, r.id))
                        else None
                    ),
                }
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
        if a.get("objective_policy", "deadline_first_v1") != b.get(
            "objective_policy", "deadline_first_v1"
        ):
            warnings.append(
                "目标规则版本不同：旧版先最小化期望延期，新版直接比较时间/能耗。请按同一规则重新计算。"
            )
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
            for initial in plan.get("initial_charges", []):
                battery = next(
                    b
                    for b in snap["scenario"]["batteries"]
                    if b["battery_id"] == initial["battery_id"]
                )
                session.add(
                    ReservationRow(
                        scenario_id=scenario.id,
                        plan_id=plan_id,
                        kind="battery",
                        resource_id=initial["battery_id"],
                        start_s=battery["available_after_s"],
                        end_s=initial["end_s"],
                    )
                )
            for r in plan.get("relay_sorties", []):
                for kind, identity, end in [
                    ("relay_drone", r["drone_id"], r["drone_released_s"]),
                    ("relay_energy", r["component_id"], r["component_released_s"]),
                ]:
                    session.add(
                        ReservationRow(
                            scenario_id=scenario.id,
                            plan_id=plan_id,
                            kind=kind,
                            resource_id=identity,
                            start_s=r["prepare_start_s"],
                            end_s=end,
                        )
                    )
            limits = snap["scenario"].get("resource_limits")
            if limits:
                charge_windows = analyze(snap, plan)["charge_windows"]
                for kind, capacity, windows in [
                    (
                        "prep_slot",
                        limits["prep_slots"],
                        [
                            (r["prepare_start_s"], r["takeoff_s"])
                            for r in [*plan["sorties"], *plan.get("relay_sorties", [])]
                        ],
                    ),
                    (
                        "charging_port",
                        limits["charging_ports"],
                        [(w["start_s"], w["end_s"]) for w in charge_windows],
                    ),
                ]:
                    available = [0.0] * capacity
                    for begin, end in sorted(windows):
                        if end <= begin:
                            continue
                        candidates = [i for i, t in enumerate(available) if t <= begin]
                        if not candidates:
                            raise AppError(
                                409,
                                "RESOURCE_CONFLICT",
                                "地面资源窗口分配不一致，确认已回滚。",
                            )
                        slot = candidates[0]
                        available[slot] = end
                        session.add(
                            ReservationRow(
                                scenario_id=scenario.id,
                                plan_id=plan_id,
                                kind=kind,
                                resource_id=f"{snap['scenario']['base']['id']}:{kind}:{slot+1}",
                                start_s=begin,
                                end_s=end,
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
            value["received_at"] = now()
            try:
                s = apply_event_to_scenario(value, row.content)
            except ContractError as exc:
                raise AppError(422, "UNSUPPORTED_EVENT_STATE", str(exc)) from exc
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
    def export_plan(
        plan_id: str, format: Literal["json", "csv", "geojson", "relay_csv"] = "json"
    ):
        with database.session() as session:
            plan = copy.deepcopy(require_row(session, PlanRow, plan_id).content)
        headers = {"Content-Disposition": f'attachment; filename="{plan_id}.{format}"'}
        if format == "json":
            return JSONResponse(content=plan, headers=headers)
        if format == "relay_csv":
            buffer = io.StringIO()
            fields = [
                "relay_sortie_id",
                "drone_id",
                "component_id",
                "station_id",
                "station_agl_m",
                "station_elevation_m",
                "prepare_start_s",
                "takeoff_s",
                "arrival_s",
                "service_start_s",
                "service_end_s",
                "return_s",
                "drone_released_s",
                "charge_start_s",
                "component_released_s",
                "energy_kwh",
                "return_soc",
            ]
            writer = csv.writer(buffer)
            writer.writerow(["plan_id", "snapshot_id", *fields])
            for r in plan.get("relay_sorties", []):
                writer.writerow([plan_id, plan["snapshot_id"], *[r[k] for k in fields]])
            return Response(
                "\ufeff" + buffer.getvalue(),
                media_type="text/csv; charset=utf-8",
                headers={
                    "Content-Disposition": f'attachment; filename="{plan_id}-relays.csv"'
                },
            )
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
            features.extend(
                {
                    "type": "Feature",
                    "properties": {
                        "plan_id": plan_id,
                        "snapshot_id": plan["snapshot_id"],
                        "kind": "relay",
                        **{
                            k: r[k]
                            for k in [
                                "relay_sortie_id",
                                "drone_id",
                                "component_id",
                                "service_start_s",
                                "service_end_s",
                                "energy_kwh",
                            ]
                        },
                    },
                    "geometry": r["route_geometry"],
                }
                for r in plan.get("relay_sorties", [])
            )
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
                "charge_start_s",
                "battery_released_s",
                "drone_released_s",
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
                            r.get("charge_start_s", r["return_s"]),
                            r["battery_released_s"],
                            r["drone_released_s"],
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

    from backend.app.missions import register_missions

    register_missions(app, database, AppError, save_new, snapshot_for)
    from backend.app.executions import register_executions

    register_executions(app, database, AppError, create_job, SolveRequest, snapshot_for)

    frontend = ROOT / "frontend/dist"
    if frontend.is_dir():
        maps = frontend / "maps"
        if maps.is_dir():
            app.mount("/maps", StaticFiles(directory=maps), name="ui-offline-maps")
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
