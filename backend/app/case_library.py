"""Versioned exercise recipes and live asset summaries, never fictional business history."""

from __future__ import annotations
from typing import Literal
import tempfile
from pathlib import Path
from pydantic import BaseModel, ConfigDict, ValidationError
from fastapi import File, UploadFile
from fastapi.responses import Response
from sqlalchemy import select, func
from backend.app.generated.domain import Scenario, HeuristicArtifact as PolicyArtifact
from backend.app.storage import (
    MissionRow,
    ScenarioRow,
    SnapshotRow,
    PlanRow,
    JobRow,
    EventRow,
    ExecutionRow,
    OperationRecordRow,
)
from solver.adapters.contest import (
    compact_scenario,
    contest_scenario,
    contest_communication,
)
from solver.engines import (
    BUILTIN,
    catalog,
    policy_store,
    read_policy,
    checked_expression,
    policy_bytes,
)


class SourceReference(BaseModel):
    source_id: str
    name: str
    kind: Literal["project", "terrain", "weather", "disaster"]
    url: str | None
    usage: str
    license_note: str


class ExerciseCase(BaseModel):
    case_id: str
    version: str
    name: str
    subtitle: str
    category: Literal["mountain", "flood", "communication", "urgent"]
    template: Literal["compact", "contest", "compact_joint", "contest_joint"]
    description: str
    learning_goals: list[str]
    source_ids: list[str]
    site_count: int
    cargo_count: int
    communication: bool
    data_statement: str


SOURCES = [
    SourceReference(
        source_id="project",
        name="镇龙乡数模与项目数据",
        kind="project",
        url=None,
        usage="演练计算使用仓库原题坐标、DEM、箱件与机型参数；场景变体为合成任务。",
        license_note="项目研究资料，保留原题来源；不是实际救援记录。",
    ),
    SourceReference(
        source_id="srtm",
        name="OpenTopography · SRTM 全球地形目录",
        kind="terrain",
        url="https://portal.opentopography.org/datasetMetadata?otCollectionID=OT.042013.4326.1",
        usage="新增区域可从公开目录获取DEM，再经资源中心导入GeoTIFF；本机计算仍用已绑定项目DEM。",
        license_note="按选定数据集许可与OpenTopography引用政策署名；没有下载或替换本机DEM。",
    ),
    SourceReference(
        source_id="meteo",
        name="Open-Meteo · 历史气象文档",
        kind="weather",
        url="https://open-meteo.com/en/docs/historical-weather-api",
        usage="提供区域气象初始化的接口配置参考；当前演练使用人工气象条件，未自动联网采集。",
        license_note="API数据CC BY 4.0；免费服务有非商业使用等条款，部署前核对。",
    ),
    SourceReference(
        source_id="emsr517",
        name="Copernicus EMS · 2021德国西部洪灾",
        kind="disaster",
        url="https://mapping.emergency.copernicus.eu/activations/EMSR517/",
        usage="EMSR517，2021-07-13激活；仅作为洪灾应急补给的历史背景。演练地点仍是项目区域，不是德国实测灾情。",
        license_note="背景摘要与来源链接；不转载其影像/矢量或声称复现真实救援。",
    ),
]

CASES = [
    ExerciseCase(
        case_id="mountain-access-v1",
        version="1.0",
        name="山地断路 · 物资空中接力",
        subtitle="从地形条件到逐箱安排",
        category="mountain",
        template="compact",
        description="道路阻断条件下，从中心基地向5个山地需求点配送。检查起降高度、满载能源、充电排程和保障完成时间。",
        learning_goals=["地形与高度剖面", "逐箱分配与Excel", "机体/电池双时序"],
        source_ids=["project", "srtm"],
        site_count=5,
        cargo_count=32,
        communication=False,
        data_statement="项目地理与原题模型 + 合成演练需求",
    ),
    ExerciseCase(
        case_id="flood-supply-v1",
        version="1.0",
        name="洪涝救援 · 分级补给保障",
        subtitle="先保急需，再看时间与能耗",
        category="flood",
        template="compact",
        description="参考公开洪灾背景设计补给演练；在项目地理区域内设置分级需求优先级，比较不同目标的保障安排。",
        learning_goals=["需求优先级", "多目标方案比较", "事件与动态修复"],
        source_ids=["project", "emsr517", "meteo"],
        site_count=5,
        cargo_count=32,
        communication=False,
        data_statement="公开灾情背景 + 项目区域合成演练，不是历史实况",
    ),
    ExerciseCase(
        case_id="relay-coverage-v1",
        version="1.0",
        name="通信恢复 · 运输与中继协同",
        subtitle="中继驻点、服务窗口与通信覆盖",
        category="communication",
        template="compact_joint",
        description="为山地运输任务配置中继无人机与独立能源组件，实际求解运输和中继联合排程，并分析覆盖与链路。",
        learning_goals=["运输—通信联合计算", "通信覆盖与高程", "中继能源时序"],
        source_ids=["project"],
        site_count=5,
        cargo_count=32,
        communication=True,
        data_statement="项目地形与通信模型；覆盖为模型计算结果",
    ),
    ExerciseCase(
        case_id="multi-site-deadline-v1",
        version="1.0",
        name="多点急送 · 原题规模压力演练",
        subtitle="15个需求点的机队协作",
        category="urgent",
        template="contest",
        description="使用原题15点80箱输入，检查多机、多电池、期望/硬截止及完整物资保障。适合验证不同引擎与目标。",
        learning_goals=["原题规模回归", "资源占用与充电", "标准/EOH同输入对比"],
        source_ids=["project"],
        site_count=15,
        cargo_count=80,
        communication=False,
        data_statement="原题研究案例，不是已执行的救援任务",
    ),
]


def case_scenario(case_id):
    case = next((c for c in CASES if c.case_id == case_id), None)
    if case is None:
        raise ValueError("请选择案例库中有效的演练案例。")
    s = (
        compact_scenario()
        if case.template.startswith("compact")
        else contest_scenario()
    )
    if case.communication:
        s["communication"] = contest_communication(s)
        s["policy"]["requires_communication"] = True
    if case.category == "flood":
        # Change only priorities, preserving all physical inputs and hard deadlines.
        for i, demand in enumerate(s["demands"]):
            demand["priority"] = 3 if i % 3 == 0 else 2 if i % 3 == 1 else 1
        s["data_origin"] = "user_input"
    s["name"] = case.name
    return s


class CaseCatalog(BaseModel):
    cases: list[ExerciseCase]
    sources: list[SourceReference]


class AssetOverview(BaseModel):
    mission_count: int
    active_mission_count: int
    archived_mission_count: int
    scenario_count: int
    snapshot_count: int
    plan_count: int
    execution_count: int
    event_count: int
    completed_job_count: int
    average_solve_s: float | None
    scope: Literal["local_workspace"] = "local_workspace"


class HeuristicPackage(BaseModel):
    model_config = ConfigDict(extra="forbid")
    policy_id: str
    name: str
    version: str
    origin: Literal["rule_initialization", "eoh_offline"]
    description: str
    sha256: str
    online_network_required: Literal[False]
    evolution_record: dict | None


def register_case_library(app, database, error):
    @app.get("/api/v1/case-library", response_model=CaseCatalog)
    def cases():
        return {"cases": CASES, "sources": SOURCES}

    @app.get("/api/v1/case-library/{case_id}/preview", response_model=Scenario)
    def preview(case_id: str):
        try:
            return case_scenario(case_id)
        except ValueError as exc:
            raise error(404, "REFERENCE_INVALID", str(exc)) from exc

    @app.get("/api/v1/heuristic-packages", response_model=list[HeuristicPackage])
    def heuristic_packages():
        with policy_store(database.directory / "heuristics"):
            return catalog()

    @app.get("/api/v1/heuristic-packages/{policy_id}/export", response_class=Response)
    def export_policy(policy_id: str):
        try:
            with policy_store(database.directory / "heuristics"):
                read_policy(policy_id)
                raw = policy_bytes(policy_id)
        except (ValueError, KeyError, OSError, SyntaxError) as exc:
            raise error(404, "REFERENCE_INVALID", str(exc)) from exc
        return Response(
            raw,
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{policy_id}.json"'},
        )

    @app.post(
        "/api/v1/heuristic-packages/import",
        response_model=HeuristicPackage,
        status_code=201,
    )
    async def import_policy(file: UploadFile = File(...)):
        raw = await file.read(32_769)
        if len(raw) > 32_768:
            raise error(422, "SCHEMA_INVALID", "离线策略包超出32KiB限制。")
        try:
            package = PolicyArtifact.model_validate_json(raw)
            normalized = package.model_dump(mode="json")
            if normalized["origin"] == "eoh_offline" and not package.evolution_record:
                raise ValueError(
                    "EOH离线包需附带原始进化记录；初始化规则请选择规则来源。"
                )
            checked_expression(package.expression)
            # Preserve exact bytes so export/import never breaks Plan's pinned SHA256.
            content = raw
            directory = database.directory / "heuristics"
            directory.mkdir(exist_ok=True)
            # Validate in a private scratch directory before publishing an immutable version.
            with tempfile.TemporaryDirectory(dir=directory) as scratch:
                (Path(scratch) / (package.policy_id + ".json")).write_bytes(content)
                with policy_store(scratch):
                    read_policy(package.policy_id)
            if (BUILTIN / (package.policy_id + ".json")).exists():
                raise FileExistsError("内置策略ID不可覆盖；请为新版本使用新ID。")
            with (directory / (package.policy_id + ".json")).open("xb") as stream:
                stream.write(content)
            with policy_store(directory):
                return next(p for p in catalog() if p["policy_id"] == package.policy_id)
        except FileExistsError as exc:
            raise error(
                409, "IDEMPOTENCY_CONFLICT", "该策略ID已存在，请使用新版本ID。"
            ) from exc
        except (ValidationError, ValueError, KeyError, OSError, SyntaxError) as exc:
            raise error(
                422, "SCHEMA_INVALID", "策略包检查失败：" + str(exc)[:400]
            ) from exc

    @app.get("/api/v1/asset-overview", response_model=AssetOverview)
    def overview():
        with database.session() as session:
            count = lambda table: session.scalar(
                select(func.count()).select_from(table)
            )
            missions = list(session.scalars(select(MissionRow)))
            from backend.app.missions import mission_view

            mission_states = [mission_view(session, m)["lifecycle"] for m in missions]
            jobs = [
                j
                for j in session.scalars(select(JobRow))
                if j.state == "completed" and j.content.get("runtime_s") is not None
            ]
            return dict(
                mission_count=len(missions),
                active_mission_count=sum(
                    state not in ("completed", "archived") for state in mission_states
                ),
                archived_mission_count=sum(
                    state == "archived" for state in mission_states
                ),
                scenario_count=count(ScenarioRow),
                snapshot_count=count(SnapshotRow),
                plan_count=count(PlanRow),
                execution_count=count(ExecutionRow),
                event_count=count(EventRow)
                + session.scalar(
                    select(func.count())
                    .select_from(OperationRecordRow)
                    .where(OperationRecordRow.namespace == "execution.event")
                ),
                completed_job_count=len(jobs),
                average_solve_s=(
                    sum(j.content["runtime_s"] for j in jobs) / len(jobs)
                    if jobs
                    else None
                ),
            )
