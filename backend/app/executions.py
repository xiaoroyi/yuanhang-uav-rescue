"""Simulation, event, repair and command routes. No real device transport exists."""

from __future__ import annotations
import copy
from datetime import datetime, timezone, timedelta
import json

from fastapi import Request, Query
from starlette.concurrency import run_in_threadpool
from fastapi.responses import StreamingResponse
from sqlalchemy import select

from backend.app.operation_models import (
    ExecutionCreate,
    ExecutionView,
    SimulationAction,
    ExecutionEventInput,
    ExecutionEventView,
    EventResolution,
    RepairRequest,
    RepairView,
    ApplyRepair,
    DeviceCapabilities,
    CommandRequest,
    CommandView,
    ExecutionAnalysis,
    OperationCapabilities,
    ExecutionBundle,
    DeviceMissionState,
    ExecutionRepairReference,
)
from backend.app.storage import (
    MissionRow,
    ExecutionRow,
    OperationRecordRow,
    ScenarioRow,
    SnapshotRow,
    PlanRow,
    JobRow,
    VersionRow,
)
from backend.app.jobs import now
from backend.app.missions import identity, require, revision
from backend.app.simulation import timestamp
from shared.contracts import content_hash, validate_scenario, ContractError
from solver.public_api import validate
from solver.dependencies import affected_closure
from backend.app.device_adapter import SimulationAdapter
from backend.app.device_state import SimulationDeviceStore
from solver.weather import eligible_types as weather_eligible_types


def register_executions(app, database, error, create_job, solve_request, snapshot_for):
    def engine():
        return app.state.simulation

    @app.get(
        "/api/v1/meta/operations-capabilities", response_model=OperationCapabilities
    )
    def operation_capabilities():
        return {"modes": ["simulation"]}

    def receipt(session, namespace, key, body, owner):
        digest = content_hash(body.model_dump(mode="json"))
        previous = session.get(OperationRecordRow, (namespace, key))
        if previous:
            if previous.owner_id != owner or previous.request_hash != digest:
                raise error(409, "IDEMPOTENCY_CONFLICT", "幂等键内容或所属执行冲突。")
            return previous.content, digest
        return None, digest

    def store(session, namespace, key, owner, digest, content):
        session.add(
            OperationRecordRow(
                namespace=namespace,
                id=key,
                owner_id=owner,
                request_hash=digest,
                content=copy.deepcopy(content),
            )
        )

    def events_for(session, execution_id):
        """Project append-only corrections without rewriting the original event/input."""
        row = require(session, ExecutionRow, execution_id, error)
        raw = {
            v["event_id"]: v
            for v in engine().records(session, execution_id, "execution.event")
        }
        resolutions = {
            v["event_id"]: v
            for v in engine().records(
                session, execution_id, "execution.event.resolution"
            )
        }
        result = []
        for eid in row.content["event_ids"]:
            v = copy.deepcopy(raw[eid])
            if eid in resolutions:
                v.update(
                    status="withdrawn",
                    resolved_at=resolutions[eid]["created_at"],
                    resolution_reason=resolutions[eid]["reason"],
                )
            result.append(v)
        return result

    def device_adapter(session, row):
        devices = SimulationDeviceStore(session, row, error)
        return SimulationAdapter(
            mission_state_reader=devices.read, mission_state_writer=devices.write
        )

    @app.get(
        "/api/v1/executions/{execution_id}/devices/{device_id}/mission-state",
        response_model=DeviceMissionState,
    )
    def device_mission_state(execution_id: str, device_id: str):
        with database.session(immediate=True) as session:
            row = require(session, ExecutionRow, execution_id, error)
            if not row.content["connected"]:
                raise error(
                    422,
                    "TELEMETRY_UNAVAILABLE",
                    "模拟链路已断开，当前只能查看最后遥测，不能确认设备任务状态。",
                )
            return SimulationDeviceStore(session, row, error).read(device_id)

    def finish_device_command(session, value):
        import asyncio

        row = require(session, ExecutionRow, value["execution_id"], error)
        if not row.content["connected"]:
            raise ValueError("Simulation telemetry link disconnected")
        if (
            value["command_type"] == "mission.activate"
            and value["desired_plan_id"] != row.content["desired_plan_id"]
        ):
            raise ValueError("Target schedule is not approved/current")
        adapter = device_adapter(session, row)

        async def observe():
            await adapter.execute_command(
                value["device_id"],
                value,
                {
                    "mode": "simulation",
                    "approved": value["command_type"] == "mission.activate",
                },
            )
            return await adapter.read_mission_state(value["device_id"])

        observed = asyncio.run(observe())
        if value["command_type"] == "mission.upload" and (
            observed["uploaded_plan_id"] != value["desired_plan_id"]
            or observed["uploaded_content_sha256"]
            != content_hash(value["compiled_mission"])
        ):
            raise ValueError("Uploaded mission readback mismatch")
        if (
            value["command_type"] == "mission.activate"
            and observed["active_plan_id"] != value["desired_plan_id"]
        ):
            raise ValueError("Active mission readback mismatch")
        return observed

    @app.post("/api/v1/executions", response_model=ExecutionView, status_code=201)
    def create_execution(body: ExecutionCreate):
        with database.session(immediate=True) as session:
            old, digest = receipt(
                session, "execution.create", body.idempotency_key, body, body.mission_id
            )
            if old:
                return old
            m = require(session, MissionRow, body.mission_id, error)
            revision(m.content, body.expected_revision, error)
            if m.content["mode"] != "simulation":
                raise error(
                    422, "SIMULATION_ONLY", "请复制为演练任务后启动；本机不连接设备。"
                )
            p = require(session, PlanRow, body.confirmed_plan_id, error)
            s = require(session, ScenarioRow, m.scenario_id, error)
            if (
                p.scenario_id != s.id
                or p.version != s.version
                or not p.confirmed_at
                or s.active_plan_id != p.id
            ):
                raise error(
                    409, "PLAN_NOT_CURRENT_CONFIRMED", "请先确认当前输入版本的方案。"
                )
            if m.content["active_execution_id"]:
                active = require(
                    session, ExecutionRow, m.content["active_execution_id"], error
                )
                if active.content["status"] in ("running", "paused", "ready"):
                    raise error(
                        409,
                        "EXECUTION_ACTIVE",
                        "该任务已有活动演练，请继续原记录或复制输入。",
                    )
            snap = require(session, SnapshotRow, p.snapshot_id, error).content
            if validate(snap, p.content)["status"] != "passed":
                raise error(422, "VALIDATION_FAILED", "方案未通过启动前独立复核。")
            eid = identity("EXE")
            value = {
                "execution_id": eid,
                "mission_id": m.id,
                "mode": "simulation",
                "initial_plan_id": p.id,
                "desired_plan_id": p.id,
                "status": "ready",
                "revision": 1,
                "facts_cursor": 0,
                "time_s": 0.0,
                "speed": 1.0,
                "seed": body.seed,
                "connected": True,
                "schedule_parts": [
                    {
                        "plan_id": p.id,
                        "sortie_ids": [r["sortie_id"] for r in p.content["sorties"]],
                        "relay_sortie_ids": [
                            r["relay_sortie_id"]
                            for r in p.content.get("relay_sorties", [])
                        ],
                        "role": "initial",
                    }
                ],
                "created_at": now(),
                "updated_at": now(),
                "anchor_sim_s": 0.0,
                "anchor_wall_at": now(),
                "session_id": identity("SIM"),
                "last_telemetry": [],
                "event_ids": [],
                "applied_event_ids": [],
            }
            row = ExecutionRow(id=eid, mission_id=m.id, content=value)
            session.add(row)
            m.content = {
                **m.content,
                "active_execution_id": eid,
                "revision": m.content["revision"] + 1,
                "updated_at": now(),
            }
            view = engine().view(session, row, advance=False)
            store(session, "execution.create", body.idempotency_key, m.id, digest, view)
            return view

    @app.get(
        "/api/v1/missions/{mission_id}/executions", response_model=list[ExecutionView]
    )
    def list_executions(mission_id: str):
        with database.session(immediate=True) as session:
            require(session, MissionRow, mission_id, error)
            return [
                engine().view(session, r)
                for r in session.scalars(
                    select(ExecutionRow).where(ExecutionRow.mission_id == mission_id)
                )
            ]

    @app.get("/api/v1/executions/{execution_id}", response_model=ExecutionView)
    def get_execution(execution_id: str):
        with database.session(immediate=True) as session:
            return engine().view(
                session, require(session, ExecutionRow, execution_id, error)
            )

    @app.post(
        "/api/v1/executions/{execution_id}/simulation/actions",
        response_model=ExecutionView,
    )
    def action(execution_id: str, body: SimulationAction):
        with database.session(immediate=True) as session:
            old, digest = receipt(
                session, "simulation.action", body.idempotency_key, body, execution_id
            )
            if old:
                return old
            row = require(session, ExecutionRow, execution_id, error)
            engine().advance(session, row)
            revision(row.content, body.expected_revision, error)
            mission = require(session, MissionRow, row.mission_id, error)
            if mission.content["lifecycle"] == "archived":
                raise error(
                    409, "MISSION_ARCHIVED", "已归档任务仅可读取，请先取消归档。"
                )
            value = copy.deepcopy(row.content)
            current = value["status"]
            pending_events = any(
                v["status"] != "withdrawn"
                and v["event_id"] not in value["applied_event_ids"]
                for v in events_for(session, execution_id)
            )
            if body.action in ("start", "resume", "advance") and pending_events:
                raise error(
                    409,
                    "PENDING_EVENTS",
                    "仍有未处理变化；请采纳调整或核实误报，不能推进未来排程。",
                )
            if body.action in ("start", "resume"):
                expected = "ready" if body.action == "start" else "paused"
                if current != expected:
                    raise error(
                        422, "EXECUTION_STATE_INVALID", "当前执行状态不能开始或恢复。"
                    )
                value["status"] = "running"
            elif body.action == "pause":
                if current != "running":
                    raise error(
                        422, "EXECUTION_STATE_INVALID", "仅运行中的演练可以暂停。"
                    )
                value["status"] = "paused"
            elif body.action == "advance":
                if (
                    current not in ("paused", "ready")
                    or body.target_time_s is None
                    or body.target_time_s < value["time_s"]
                ):
                    raise error(
                        422,
                        "EXECUTION_STATE_INVALID",
                        "暂停后可向前推进，不允许倒退或重放写账。",
                    )
                row.content = value
                value = copy.deepcopy(
                    engine().advance(session, row, body.target_time_s)
                )
                if value["status"] != "completed":
                    value["status"] = "paused"
            elif body.action == "speed":
                if body.speed is None:
                    raise error(422, "SCHEMA_INVALID", "请选择模拟倍速。")
                value["speed"] = body.speed
            elif body.action in ("disconnect", "reconnect"):
                value["connected"] = body.action == "reconnect"
                if body.action == "reconnect":
                    value.update(session_id=identity("SIM"), telemetry_sequence=0)
            value.update(
                revision=value["revision"] + 1,
                anchor_sim_s=value["time_s"],
                anchor_wall_at=now(),
                updated_at=now(),
            )
            row.content = copy.deepcopy(value)
            view = engine().view(session, row)
            store(
                session,
                "simulation.action",
                body.idempotency_key,
                execution_id,
                digest,
                view,
            )
            return view

    def current_schedule(session, row):
        return engine().schedule(session, row.content)

    @app.post(
        "/api/v1/executions/{execution_id}/events",
        response_model=ExecutionEventView,
        status_code=201,
    )
    def event(execution_id: str, body: ExecutionEventInput):
        with database.session(immediate=True) as session:
            old, digest = receipt(
                session,
                "execution.event",
                execution_id + ":" + body.event_id,
                body,
                execution_id,
            )
            if old:
                return old
            row = require(session, ExecutionRow, execution_id, error)
            engine().advance(session, row)
            revision(row.content, body.expected_revision, error)
            if row.content["status"] not in ("paused", "ready"):
                raise error(
                    422, "PAUSE_REQUIRED", "请先暂停模拟排程，冻结事实后记录变化。"
                )
            schedule = current_schedule(session, row)
            tick = row.content["time_s"]
            initial, snap, _ = engine().plan_data(
                session, row.content["initial_plan_id"]
            )
            s = snap["scenario"]
            all_sorties = [{**r, "_plan_id": p["plan_id"]} for p, _, r, _ in schedule]
            started = engine().started(session, execution_id)
            direct = set()
            manual = False
            missing = 0
            if body.event_type == "weather.changed":
                if (
                    body.weather is None
                    or body.object_id is not None
                    or body.demand is not None
                    or body.cargo_items
                ):
                    raise error(
                        422,
                        "SCHEMA_INVALID",
                        "气象变化只接受完整人工weather情景，不混用其它事件字段。",
                    )
                probe = copy.deepcopy(s)
                probe["weather"] = body.weather.model_dump(mode="json")
                try:
                    validate_scenario(probe)
                except ContractError as exc:
                    raise error(422, "WEATHER_INVALID", str(exc)) from exc
                eligible = weather_eligible_types(probe)
                types = {d["drone_id"]: d["type_id"] for d in s["drones"]}
                for r in all_sorties:
                    if (
                        r["return_s"] > tick
                        and r["return_s"] > probe["weather"]["valid_from_s"]
                    ):
                        direct.add(r["sortie_id"])
                        if (r["_plan_id"], r["sortie_id"]) in started and (
                            types[r["drone_id"]] not in eligible
                            or r["return_s"] > probe["weather"]["valid_until_s"]
                        ):
                            manual = True
            elif body.event_type == "demand.added":
                if (
                    body.object_id is not None
                    or body.demand is None
                    or body.weather is not None
                ):
                    raise error(
                        422,
                        "SCHEMA_INVALID",
                        "新增需求需提供 demand 和显式库存，不能混用 object_id。",
                    )
                d = body.demand.model_dump(mode="json")
                if d["site_id"] not in {n["id"] for n in s["sites"]}:
                    raise error(
                        422, "REFERENCE_INVALID", "执行中插单仅支持已有需求点。"
                    )
                if d["demand_id"] in {x["demand_id"] for x in s["demands"]}:
                    raise error(409, "REFERENCE_INVALID", "新增需求编号已存在。")
                previous = events_for(session, execution_id)
                for e in previous:
                    raw = require(
                        session,
                        OperationRecordRow,
                        ("execution.event.input", execution_id + ":" + e["event_id"]),
                        error,
                    ).content
                    if (
                        raw.get("demand")
                        and raw["demand"]["demand_id"] == d["demand_id"]
                    ):
                        raise error(
                            409, "REFERENCE_INVALID", "新增需求编号已在事件中使用。"
                        )
                cargos = [c.model_dump(mode="json") for c in body.cargo_items]
                known = {c["cargo_id"] for c in s["cargo_items"]}
                for e in previous:
                    raw = require(
                        session,
                        OperationRecordRow,
                        ("execution.event.input", execution_id + ":" + e["event_id"]),
                        error,
                    ).content
                    known.update(c["cargo_id"] for c in raw["cargo_items"])
                if len({c["cargo_id"] for c in cargos}) != len(cargos) or any(
                    c["cargo_id"] in known
                    or c["demand_id"] != d["demand_id"]
                    or c["type"] != d["cargo_type"]
                    or c["status"] != "available"
                    or c["location_id"] != s["base"]["id"]
                    for c in cargos
                ):
                    raise error(
                        422,
                        "REFERENCE_INVALID",
                        "新库存必须是独立编号、匹配需求、可用且位于基地的真实箱件。",
                    )
                missing = max(0, d["required_quantity"] - len(cargos))
            else:
                if (
                    not body.object_id
                    or body.demand is not None
                    or body.cargo_items
                    or body.weather is not None
                ):
                    raise error(422, "SCHEMA_INVALID", "退出事件只接受目标 object_id。")
                if body.event_type == "drone.unavailable":
                    known = {x["drone_id"] for x in s["drones"]}
                    key = "drone_id"
                elif body.event_type == "battery.unavailable":
                    known = {x["battery_id"] for x in s["batteries"]}
                    key = "battery_id"
                else:
                    known = {x["id"] for x in s["sites"]}
                    key = None
                if body.object_id not in known:
                    raise error(422, "REFERENCE_INVALID", "变化目标不属于当前演练。")
                for r in all_sorties:
                    hit = (
                        r[key] == body.object_id
                        if key
                        else any(v["site_id"] == body.object_id for v in r["visits"])
                    )
                    if hit and r["drone_released_s"] > tick:
                        direct.add(r["sortie_id"])
                        if (r["_plan_id"], r["sortie_id"]) in started:
                            manual = True
            propagated, _ = affected_closure(all_sorties, direct)
            committed = [
                r["sortie_id"]
                for r in all_sorties
                if (r["_plan_id"], r["sortie_id"]) in started
            ]
            value = {
                "event_id": body.event_id,
                "execution_id": execution_id,
                "event_type": body.event_type,
                "object_id": body.object_id,
                "reason": body.reason,
                "time_s": tick,
                "facts_cursor": row.content["facts_cursor"],
                "affected_sortie_ids": sorted(direct),
                "propagated_sortie_ids": sorted(propagated),
                "preserved_sortie_ids": [
                    r["sortie_id"]
                    for r in all_sorties
                    if r["sortie_id"] not in propagated
                ],
                "committed_sortie_ids": committed,
                "missing_inventory": missing,
                **(
                    {"weather": body.weather.model_dump(mode="json")}
                    if body.weather is not None
                    else {}
                ),
                "status": "requires_manual" if manual else "recorded",
            }
            store(
                session,
                "execution.event",
                execution_id + ":" + body.event_id,
                execution_id,
                digest,
                value,
            )
            store(
                session,
                "execution.event.input",
                execution_id + ":" + body.event_id,
                execution_id,
                digest,
                body.model_dump(mode="json"),
            )
            row.content = {
                **row.content,
                "revision": row.content["revision"] + 1,
                "event_ids": [*row.content["event_ids"], body.event_id],
                "updated_at": now(),
            }
            return value

    @app.get(
        "/api/v1/executions/{execution_id}/events",
        response_model=list[ExecutionEventView],
    )
    def list_events(execution_id: str):
        with database.session() as session:
            require(session, ExecutionRow, execution_id, error)
            return events_for(session, execution_id)

    @app.post(
        "/api/v1/executions/{execution_id}/events/{event_id}/resolve",
        response_model=ExecutionEventView,
    )
    def resolve_event(execution_id: str, event_id: str, body: EventResolution):
        with database.session(immediate=True) as session:
            old, digest = receipt(
                session,
                "execution.event.resolve",
                execution_id + ":" + body.idempotency_key,
                body,
                execution_id,
            )
            if old:
                if old["event_id"] != event_id:
                    raise error(409, "IDEMPOTENCY_CONFLICT", "纠错键已用于其它事件。")
                return old
            row = require(session, ExecutionRow, execution_id, error)
            revision(row.content, body.expected_revision, error)
            if row.content["status"] not in ("paused", "ready"):
                raise error(422, "PAUSE_REQUIRED", "请先暂停，再核实并纠正误报。")
            if not body.reason.strip() or len(body.reason.strip()) < 10:
                raise error(
                    422, "REASON_REQUIRED", "请明确说明误报的核实依据，至少10个字符。"
                )
            event = next(
                (
                    v
                    for v in events_for(session, execution_id)
                    if v["event_id"] == event_id
                ),
                None,
            )
            if not event:
                raise error(404, "REFERENCE_INVALID", "事件不存在。")
            if (
                event_id in row.content["applied_event_ids"]
                or event["status"] == "withdrawn"
            ):
                raise error(
                    409, "EVENT_ALREADY_RESOLVED", "已采纳或已纠正事件不能再次撤销。"
                )
            if any(
                v["status"] in ("applying", "partially_applied")
                for v in engine().records(session, execution_id, "execution.change")
            ):
                raise error(
                    409,
                    "APPLICATION_UNRESOLVED",
                    "存在应用中或未确定的指令，先核对设备状态。",
                )
            at = now()
            value = {
                **event,
                "status": "withdrawn",
                "resolved_at": at,
                "resolution_reason": body.reason.strip(),
            }
            store(
                session,
                "execution.event.resolution",
                execution_id + ":" + event_id,
                execution_id,
                digest,
                {
                    "event_id": event_id,
                    "created_at": at,
                    "reason": body.reason.strip(),
                    "action": body.action,
                    "actor": "local_simulation_operator",
                    "facts_cursor": row.content["facts_cursor"],
                },
            )
            store(
                session,
                "execution.event.resolve",
                execution_id + ":" + body.idempotency_key,
                execution_id,
                digest,
                value,
            )
            row.content = {
                **row.content,
                "revision": row.content["revision"] + 1,
                "updated_at": at,
            }
            return value

    @app.post(
        "/api/v1/executions/{execution_id}/replan-jobs",
        response_model=RepairView,
        status_code=202,
    )
    def repair(execution_id: str, body: RepairRequest):
        with database.session(immediate=True) as session:
            old, digest = receipt(
                session,
                "execution.repair.request",
                execution_id + ":" + body.idempotency_key,
                body,
                execution_id,
            )
            if old:
                return old
            row = require(session, ExecutionRow, execution_id, error)
            revision(row.content, body.expected_revision, error)
            if (
                row.content["status"] not in ("paused", "ready")
                or not row.content["connected"]
            ):
                raise error(
                    422,
                    "PAUSE_AND_TELEMETRY_REQUIRED",
                    "请暂停并恢复可信模拟遥测后生成调整。",
                )
            _, original, _ = engine().plan_data(session, row.content["initial_plan_id"])
            s = copy.deepcopy(original["scenario"])
            if s["policy"]["requires_communication"]:
                raise error(
                    422,
                    "UNSUPPORTED_SCOPE",
                    "当前承诺前缀修复尚未覆盖中继联合窗口；请保留原计划并人工协调，不关闭通信约束。",
                )
            events = events_for(session, execution_id)
            if not any(e["status"] != "withdrawn" for e in events):
                raise error(422, "EVENT_REQUIRED", "请先记录执行中的变化。")
            if any(
                e["status"] == "requires_manual"
                for e in events
                if e["event_id"] not in row.content["applied_event_ids"]
            ):
                raise error(
                    422,
                    "COMMITMENT_REQUIRES_MANUAL",
                    "变化涉及已开始架次，不能自动撤销或换机；请先人工协调现有承诺。",
                )
            for e in events:
                if e["status"] == "withdrawn":
                    continue
                raw = require(
                    session,
                    OperationRecordRow,
                    ("execution.event.input", execution_id + ":" + e["event_id"]),
                    error,
                ).content
                if e["event_type"] == "demand.added":
                    s["demands"].append(copy.deepcopy(raw["demand"]))
                    s["cargo_items"].extend(copy.deepcopy(raw["cargo_items"]))
                elif e["event_type"] == "drone.unavailable":
                    next(d for d in s["drones"] if d["drone_id"] == e["object_id"])[
                        "status"
                    ] = "unavailable"
                elif e["event_type"] == "battery.unavailable":
                    next(
                        b for b in s["batteries"] if b["battery_id"] == e["object_id"]
                    )["status"] = "unavailable"
                elif e["event_type"] == "site.unavailable":
                    next(n for n in s["sites"] if n["id"] == e["object_id"])[
                        "available"
                    ] = False
                elif e["event_type"] == "weather.changed":
                    s["weather"] = copy.deepcopy(raw["weather"])
            tick = row.content["time_s"]
            schedule = current_schedule(session, row)
            started = engine().started(session, execution_id)
            committed = [
                item
                for item in schedule
                if (item[0]["plan_id"], item[2]["sortie_id"]) in started
            ]
            locked = {c for _, _, r, _ in committed for c in r["cargo_ids"]}
            # Conservative common boundary also preserves all finite preparation/charging occupancy.
            floor = (
                max(
                    [tick]
                    + [
                        max(r["drone_released_s"], r["battery_released_s"])
                        for _, _, r, _ in committed
                    ]
                )
                if s.get("resource_limits")
                else tick
            )
            by_cargo = {c["cargo_id"]: c for c in s["cargo_items"]}
            for d in s["demands"]:
                d["required_quantity"] -= sum(
                    by_cargo[c]["demand_id"] == d["demand_id"] for c in locked
                )
            s["demands"] = [d for d in s["demands"] if d["required_quantity"] > 0]
            remaining_demands = {d["demand_id"] for d in s["demands"]}
            s["cargo_items"] = [
                c
                for c in s["cargo_items"]
                if c["cargo_id"] not in locked and c["demand_id"] in remaining_demands
            ]
            for d in s["drones"]:
                releases = [
                    r["drone_released_s"]
                    for _, _, r, _ in committed
                    if r["drone_id"] == d["drone_id"]
                ]
                d["available_after_s"] = max([d["available_after_s"], floor, *releases])
            for b in s["batteries"]:
                uses = [
                    r for _, _, r, _ in committed if r["battery_id"] == b["battery_id"]
                ]
                if uses:
                    b["soc"] = (
                        1.0  # A forecast only at the preserved, explicit full-charge release boundary.
                    )
                b["available_after_s"] = max(
                    [
                        b["available_after_s"],
                        floor,
                        *[r["battery_released_s"] for r in uses],
                    ]
                )
            parts = []
            for p, _, r, _ in committed:
                part = next((x for x in parts if x["plan_id"] == p["plan_id"]), None)
                if part is None:
                    part = {
                        "plan_id": p["plan_id"],
                        "sortie_ids": [],
                        "role": "commitment",
                    }
                    parts.append(part)
                part["sortie_ids"].append(r["sortie_id"])
            change = {
                "change_id": identity("CHG"),
                "execution_id": execution_id,
                "execution_revision": row.content["revision"],
                "facts_cursor": row.content["facts_cursor"],
                "event_fingerprint": content_hash(events),
                "committed_parts": parts,
                "committed_cargo_ids": sorted(locked),
                "future_not_before_s": floor,
                "job": None,
                "candidate_plan_id": None,
                "status": "no_remaining" if not s["demands"] else "computing",
                "message": "保留所有已开始架次，剩余排程在承诺资源释放后开始；未重置在飞状态。",
                "changed_cargo_ids": [],
                "retained_cargo_ids": sorted(locked),
                "repair_policy": body.repair_policy,
                "calculation_method": None,
                "repair_reference_id": None,
            }
            snap = None
            if s["demands"]:
                s.update(
                    scenario_id=identity("SCN"),
                    name=s["name"] + " · 在途剩余输入",
                    state_version=1,
                    data_origin="user_input",
                    mode="simulation",
                )
                validate_scenario(s)
                fork = ScenarioRow(
                    id=s["scenario_id"],
                    name=s["name"],
                    version=1,
                    content=s,
                    active_plan_id=None,
                    updated_at=now(),
                )
                session.add(fork)
                session.add(
                    VersionRow(
                        scenario_id=fork.id,
                        version=1,
                        content=s,
                        content_hash=content_hash(s),
                    )
                )
                snap = snapshot_for(session, fork)
                from backend.app.execution_archive import document

                future_parts = []
                for source_plan, _, route, _ in schedule:
                    if (source_plan["plan_id"], route["sortie_id"]) in started:
                        continue
                    part = next(
                        (
                            p
                            for p in future_parts
                            if p["plan_id"] == source_plan["plan_id"]
                        ),
                        None,
                    )
                    if part is None:
                        part = {
                            "plan_id": source_plan["plan_id"],
                            "sortie_ids": [],
                            "role": "future",
                        }
                        future_parts.append(part)
                    part["sortie_ids"].append(route["sortie_id"])
                originals = {
                    p["plan_id"]: (p, original) for p, original, _, _ in schedule
                }
                documents = [
                    document("plan", pid, p)
                    for pid, (p, _) in sorted(originals.items())
                ]
                original_snapshots = {
                    original["snapshot_id"]: original
                    for _, original in originals.values()
                }
                documents.extend(
                    document("snapshot", sid, original)
                    for sid, original in sorted(original_snapshots.items())
                )
                change["repair_reference_id"] = identity("RRF")
                reference = {
                    "reference_version": "execution-remaining-v1",
                    "execution_id": execution_id,
                    "execution_revision": row.content["revision"],
                    "facts_cursor": row.content["facts_cursor"],
                    "input_snapshot_id": snap["snapshot_id"],
                    "repair_policy": body.repair_policy,
                    "force_full": any(
                        e["status"] != "withdrawn"
                        and e["event_id"] not in row.content["applied_event_ids"]
                        and e["event_type"]
                        not in ("drone.unavailable", "battery.unavailable")
                        for e in events
                    ),
                    "committed_cargo_ids": sorted(locked),
                    "future_parts": future_parts,
                    "documents": documents,
                }
                ExecutionRepairReference.model_validate(reference)
                store(
                    session,
                    "solver.repair.reference",
                    change["repair_reference_id"],
                    execution_id,
                    content_hash(reference),
                    reference,
                )
            store(
                session,
                "execution.change",
                change["change_id"],
                execution_id,
                digest,
                change,
            )
            session.flush()
        if snap:
            parent = require_plan(row.content["desired_plan_id"])
            try:
                job = create_job(
                    solve_request(
                        snapshot_id=snap["snapshot_id"],
                        objective=body.objective,
                        objective_policy=parent.get(
                            "objective_policy", "deadline_first_v1"
                        ),
                        time_limit_s=body.time_limit_s,
                        repair_reference_id=change["repair_reference_id"],
                    )
                )
                change["job"] = job
            except Exception as exc:
                change.update(
                    status="failed",
                    message=getattr(
                        exc,
                        "message",
                        "剩余求解任务未能创建，输入与承诺保留，请稍后重试。",
                    ),
                )
        with database.session(immediate=True) as session:
            require(
                session,
                OperationRecordRow,
                ("execution.change", change["change_id"]),
                error,
            ).content = copy.deepcopy(change)
            store(
                session,
                "execution.repair.request",
                execution_id + ":" + body.idempotency_key,
                execution_id,
                digest,
                change,
            )
        return change

    def require_plan(plan_id):
        with database.session() as session:
            return require(session, PlanRow, plan_id, error).content

    def change_view(session, record):
        v = copy.deepcopy(record.content)
        if v["job"]:
            job_row = require(session, JobRow, v["job"]["job_id"], error)
            job = job_row.content
            v["job"] = job
            if v["status"] == "computing" and job["job_state"] not in (
                "queued",
                "running",
            ):
                v["candidate_plan_id"] = job["plan_id"]
                v["status"] = "ready" if job["has_validated_plan"] else "failed"
                codes = {
                    d["code"] for d in (job_row.outcome or {}).get("diagnostics", [])
                }
                if "REPAIR_LOCAL_APPLIED" in codes:
                    v["calculation_method"] = "dependency_local"
                elif "REPAIR_FULL_RECOMPUTE" in codes:
                    v["calculation_method"] = "full_recompute"
                if job["has_validated_plan"] and v.get("repair_reference_id"):
                    from backend.app.repair_diff import (
                        reference_sorties,
                        compare_future,
                    )

                    reference = require(
                        session,
                        OperationRecordRow,
                        ("solver.repair.reference", v["repair_reference_id"]),
                        error,
                    ).content
                    candidate = require(session, PlanRow, job["plan_id"], error).content
                    v["diff"] = compare_future(
                        reference_sorties(reference),
                        candidate,
                        v["committed_cargo_ids"],
                    )
                    v["message"] = (
                        "依赖局部修复已通过残余任务独立检查；原承诺与事实保留。"
                        if v["calculation_method"] == "dependency_local"
                        else "剩余任务全量重算已通过独立检查；原承诺与事实保留。"
                    )
                if not job["has_validated_plan"]:
                    v["message"] = (
                        "当前预算未得到可验证剩余方案；原承诺和事实保留。请查看库存/资源缺口或增加预算。"
                    )
                record.content = copy.deepcopy(v)
        if v["status"] == "applying":
            for application in v["applications"]:
                command_row = require(
                    session,
                    OperationRecordRow,
                    ("command", application["command_id"]),
                    error,
                )
                command = command_view(session, command_row)
                application["upload_state"] = (
                    command["status"]
                    if command["status"]
                    in (
                        "acknowledged",
                        "succeeded",
                        "indeterminate",
                        "expired",
                        "rejected",
                    )
                    else "queued"
                )
            states = [a["upload_state"] for a in v["applications"]]
            if any(
                state in ("indeterminate", "expired", "rejected") for state in states
            ):
                v.update(
                    status="partially_applied",
                    message="部分模拟设备 ACK 未确定；尚未激活新排程，旧承诺和资源保护保留。请查询设备状态后重新生成调整。",
                )
                for a in v["applications"]:
                    if a["upload_state"] in ("indeterminate", "expired", "rejected"):
                        a["activation_state"] = "indeterminate"
            elif all(x == "succeeded" for x in states):
                row = require(session, ExecutionRow, v["execution_id"], error)
                events = events_for(session, row.id)
                if (
                    row.content["revision"] != v["execution_revision"]
                    or row.content["facts_cursor"] != v["facts_cursor"]
                    or row.content["status"] not in ("paused", "ready")
                    or content_hash(events) != v["event_fingerprint"]
                ):
                    v.update(
                        status="failed",
                        message="上传期间执行条件已变化，未激活新排程；请重新计算。",
                    )
                else:
                    pending = require(
                        session,
                        OperationRecordRow,
                        ("execution.change.activation", v["change_id"]),
                        error,
                    ).content
                    import asyncio

                    adapter = device_adapter(session, row)
                    target = pending["desired_plan_id"]
                    for application in v["applications"]:
                        state = asyncio.run(
                            adapter.read_mission_state(application["device_id"])
                        )
                        uploaded = require(
                            session,
                            OperationRecordRow,
                            ("command", application["command_id"]),
                            error,
                        ).content
                        if state["uploaded_plan_id"] != target or state[
                            "uploaded_content_sha256"
                        ] != content_hash(uploaded["compiled_mission"]):
                            v.update(
                                status="partially_applied",
                                message="已上传程序的当前读回发生变化，未激活新排程；请核对设备后重新确认。",
                            )
                            application["activation_state"] = "indeterminate"
                            record.content = copy.deepcopy(v)
                            return v
                    for application in v["applications"]:
                        cid = identity("CMD")
                        application["activation_command_id"] = cid
                        activation = {
                            "command_id": cid,
                            "execution_id": row.id,
                            "device_id": application["device_id"],
                            "command_type": "mission.activate",
                            "mode": "simulation",
                            "status": "queued",
                            "desired_plan_id": target,
                            "created_at": now(),
                            "expires_at": (
                                datetime.now(timezone.utc) + timedelta(seconds=30)
                            ).isoformat(),
                            "acknowledged_at": None,
                            "completed_at": None,
                            "evidence": None,
                            "fault": "none",
                            "protocol_version": 2,
                        }
                        try:
                            asyncio.run(
                                adapter.execute_command(
                                    application["device_id"],
                                    activation,
                                    {
                                        "mode": "simulation",
                                        "approved": True,
                                        "change_id": v["change_id"],
                                    },
                                )
                            )
                            state = asyncio.run(
                                adapter.read_mission_state(application["device_id"])
                            )
                            if state["active_plan_id"] != target:
                                raise ValueError("Activation readback mismatch")
                            activation.update(
                                status="succeeded",
                                acknowledged_at=now(),
                                completed_at=now(),
                                observed_state=state,
                                evidence="Approved simulation activation confirmed by persisted device state",
                            )
                            application.update(
                                activation_state="active", active_plan_id=target
                            )
                        except (ValueError, KeyError, TypeError) as exc:
                            activation.update(
                                status="indeterminate",
                                acknowledged_at=now(),
                                evidence="Activation not confirmed: " + str(exc)[:200],
                            )
                            application["activation_state"] = "indeterminate"
                            v.update(
                                status="partially_applied",
                                message="设备启用结果未全部确认；模拟保持暂停，保留原承诺与新旧可能占用。",
                            )
                        store(
                            session,
                            "command",
                            cid,
                            row.id,
                            content_hash(
                                {
                                    "change_id": v["change_id"],
                                    "device_id": application["device_id"],
                                }
                            ),
                            activation,
                        )
                        if v["status"] == "partially_applied":
                            record.content = copy.deepcopy(v)
                            return v
                    value = copy.deepcopy(row.content)
                    value.update(
                        schedule_parts=pending["schedule_parts"],
                        desired_plan_id=pending["desired_plan_id"],
                        revision=value["revision"] + 1,
                        applied_event_ids=[
                            e["event_id"] for e in events if e["status"] != "withdrawn"
                        ],
                        updated_at=now(),
                    )
                    row.content = value
                    v.update(
                        status="applied",
                        message="模拟设备上传、ACK 与状态核对完成，未来排程已激活；既有事实与承诺保留。",
                    )
                    for a in v["applications"]:
                        a.update(
                            activation_state="active",
                            active_plan_id=pending["desired_plan_id"],
                        )
            record.content = copy.deepcopy(v)
        return v

    @app.get(
        "/api/v1/executions/{execution_id}/plan-changes",
        response_model=list[RepairView],
    )
    def list_changes(execution_id: str):
        with database.session(immediate=True) as session:
            require(session, ExecutionRow, execution_id, error)
            return [
                change_view(session, r)
                for r in session.scalars(
                    select(OperationRecordRow).where(
                        OperationRecordRow.namespace == "execution.change",
                        OperationRecordRow.owner_id == execution_id,
                    )
                )
            ]

    @app.get(
        "/api/v1/executions/{execution_id}/plan-changes/{change_id}",
        response_model=RepairView,
    )
    def get_change(execution_id: str, change_id: str):
        with database.session(immediate=True) as session:
            r = require(
                session, OperationRecordRow, ("execution.change", change_id), error
            )
            if r.owner_id != execution_id:
                raise error(404, "REFERENCE_INVALID", "调整记录不属于当前执行。")
            return change_view(session, r)

    @app.post(
        "/api/v1/executions/{execution_id}/plan-changes/{change_id}/apply",
        response_model=RepairView,
    )
    def apply_change(execution_id: str, change_id: str, body: ApplyRepair):
        with database.session(immediate=True) as session:
            old, digest = receipt(
                session,
                "execution.apply",
                execution_id + ":" + body.idempotency_key,
                body,
                execution_id,
            )
            if old:
                return old
            row = require(session, ExecutionRow, execution_id, error)
            revision(row.content, body.expected_revision, error)
            rec = require(
                session, OperationRecordRow, ("execution.change", change_id), error
            )
            if rec.owner_id != execution_id:
                raise error(404, "REFERENCE_INVALID", "调整不属于当前执行。")
            v = change_view(session, rec)
            events = events_for(session, execution_id)
            if (
                row.content["status"] not in ("paused", "ready")
                or row.content["revision"] != v["execution_revision"]
                or row.content["facts_cursor"] != v["facts_cursor"]
                or content_hash(events) != v["event_fingerprint"]
            ):
                raise error(
                    409,
                    "EXECUTION_SNAPSHOT_STALE",
                    "执行事实或事件已变化，请重新生成调整。",
                )
            if v["status"] not in ("ready", "no_remaining"):
                raise error(422, "CHANGE_NOT_READY", "调整尚未通过独立检查或已处理。")
            known = {
                d["device_id"]
                for d in engine().view(session, row, advance=False)["telemetry"]
            }
            if set(body.ack_timeout_device_ids) - known:
                raise error(422, "REFERENCE_INVALID", "超时目标不属于当前模拟设备。")
            future = []
            if v["candidate_plan_id"]:
                p = require(session, PlanRow, v["candidate_plan_id"], error)
                snap = require(session, SnapshotRow, p.snapshot_id, error).content
                if validate(snap, p.content)["status"] != "passed":
                    raise error(422, "VALIDATION_FAILED", "剩余候选重新检查失败。")
                # Independently check the composite ledger boundary and cargo/resource continuity.
                if any(
                    r["prepare_start_s"] < v["future_not_before_s"] - 1e-6
                    for r in p.content["sorties"]
                ):
                    raise error(
                        422, "COMMITMENT_CONFLICT", "新架次侵入已保留资源区间。"
                    )
                new_cargo = [c for r in p.content["sorties"] for c in r["cargo_ids"]]
                if set(new_cargo) & set(v["committed_cargo_ids"]):
                    raise error(
                        422, "COMMITMENT_CONFLICT", "新方案重复使用在途或已交付箱件。"
                    )
                fixed = []
                for part in v["committed_parts"]:
                    old_plan = require(session, PlanRow, part["plan_id"], error).content
                    fixed.extend(
                        r
                        for r in old_plan["sorties"]
                        if r["sortie_id"] in part["sortie_ids"]
                    )
                for a in fixed:
                    for b in p.content["sorties"]:
                        for key, end in [
                            ("drone_id", "drone_released_s"),
                            ("battery_id", "battery_released_s"),
                        ]:
                            if (
                                a[key] == b[key]
                                and max(a["prepare_start_s"], b["prepare_start_s"])
                                < min(a[end], b[end]) - 1e-6
                            ):
                                raise error(
                                    422,
                                    "COMMITMENT_CONFLICT",
                                    "新旧计划的同一资源发生占用重叠。",
                                )
                future = [
                    {
                        "plan_id": p.id,
                        "sortie_ids": [r["sortie_id"] for r in p.content["sorties"]],
                        "role": "future",
                    }
                ]
                before = {
                    c: r["drone_id"]
                    for _, _, r, _ in current_schedule(session, row)
                    for c in r["cargo_ids"]
                }
                v["changed_cargo_ids"] = [
                    c
                    for r in p.content["sorties"]
                    for c in r["cargo_ids"]
                    if before.get(c) != r["drone_id"]
                ]
                v["retained_cargo_ids"] = sorted(
                    set(v["committed_cargo_ids"])
                    | {
                        c
                        for r in p.content["sorties"]
                        for c in r["cargo_ids"]
                        if before.get(c) == r["drone_id"]
                    }
                )
            desired = v["candidate_plan_id"] or row.content["desired_plan_id"]
            store(
                session,
                "execution.change.activation",
                v["change_id"],
                execution_id,
                digest,
                {
                    "schedule_parts": [*v["committed_parts"], *future],
                    "desired_plan_id": desired,
                },
            )
            applications = []
            # A simulated device must acknowledge upload and confirm state before activation.
            # Only future work is compiled; no in-flight route replacement is attempted.
            import asyncio

            adapter = SimulationAdapter()
            for device in sorted(known):
                future_sorties = [
                    r
                    for part in future
                    for r in require(session, PlanRow, part["plan_id"], error).content[
                        "sorties"
                    ]
                    if r["drone_id"] == device
                ]
                compiled = asyncio.run(
                    adapter.compile_mission(
                        device,
                        future_sorties,
                        {"mode": "simulation", "validated": True, "plan_id": desired},
                    )
                )
                ack = asyncio.run(
                    adapter.upload_mission(
                        device, compiled, {"execution_id": execution_id}
                    )
                )
                cid = identity("CMD")
                cmd = {
                    "command_id": cid,
                    "execution_id": execution_id,
                    "device_id": device,
                    "command_type": "mission.upload",
                    "mode": "simulation",
                    "status": "queued",
                    "desired_plan_id": desired,
                    "created_at": now(),
                    "expires_at": (
                        datetime.now(timezone.utc) + timedelta(seconds=30)
                    ).isoformat(),
                    "acknowledged_at": None,
                    "completed_at": None,
                    "evidence": None,
                    "fault": (
                        "ack_timeout"
                        if device in body.ack_timeout_device_ids
                        else "none"
                    ),
                    "compiled_mission": compiled,
                    "adapter_ack": ack,
                }
                store(session, "command", cid, execution_id, digest, cmd)
                applications.append(
                    {
                        "device_id": device,
                        "desired_plan_id": desired,
                        "active_plan_id": row.content["desired_plan_id"],
                        "upload_state": "queued",
                        "activation_state": "not_started",
                        "command_id": cid,
                    }
                )
            v.update(
                status="applying",
                applications=applications,
                message="模拟上传已受理；等待逐设备 ACK 与状态确认，尚未激活新排程。",
            )
            rec.content = copy.deepcopy(v)
            store(
                session,
                "execution.apply",
                execution_id + ":" + body.idempotency_key,
                execution_id,
                digest,
                v,
            )
            return v

    @app.get(
        "/api/v1/devices/{device_id}/capabilities", response_model=DeviceCapabilities
    )
    def device_capabilities(device_id: str):
        return {
            "device_id": device_id,
            "command_types": ["mission.upload", "mission.activate", "state.query"],
        }

    @app.post("/api/v1/commands", response_model=CommandView, status_code=202)
    def command(body: CommandRequest, request: Request):
        # Local simulation is the only service-side permission. Client actor/role is not accepted.
        with database.session(immediate=True) as session:
            old, digest = receipt(
                session,
                "command.request",
                body.idempotency_key,
                body,
                body.execution_id,
            )
            if old:
                return old
            row = require(session, ExecutionRow, body.execution_id, error)
            revision(row.content, body.expected_execution_revision, error)
            _, snap, _ = engine().plan_data(session, row.content["initial_plan_id"])
            if body.device_id not in {
                d["drone_id"] for d in snap["scenario"]["drones"]
            }:
                raise error(403, "CONTROL_NOT_OWNED", "当前执行不拥有此模拟机体。")
            p = require(session, PlanRow, body.desired_plan_id, error)
            permitted = {x["plan_id"] for x in row.content["schedule_parts"]}
            permitted.update(
                c["candidate_plan_id"]
                for c in engine().records(session, row.id, "execution.change")
                if c.get("candidate_plan_id")
            )
            if p.id not in permitted:
                raise error(403, "PLAN_NOT_OWNED", "指令不能使用其它执行的方案。")
            if (
                body.command_type == "mission.activate"
                and p.id != row.content["desired_plan_id"]
            ):
                raise error(
                    409,
                    "ACTIVATION_APPROVAL_REQUIRED",
                    "新候选须经过差异确认与逐设备采纳，不能用通用指令绕过。",
                )
            if body.command_type != "state.query" and not row.content["connected"]:
                raise error(422, "TELEMETRY_REQUIRED", "失联时不能上传或启用任务。")
            expires = body.expires_at.timestamp()
            if expires <= timestamp(now()) or expires > timestamp(now()) + 300:
                raise error(422, "COMMAND_EXPIRED", "指令有效期应在未来五分钟内。")
            value = {
                "command_id": identity("CMD"),
                "execution_id": row.id,
                "device_id": body.device_id,
                "command_type": body.command_type,
                "mode": "simulation",
                "status": "queued",
                "desired_plan_id": p.id,
                "created_at": now(),
                "expires_at": body.expires_at.isoformat(),
                "acknowledged_at": None,
                "completed_at": None,
                "evidence": None,
            }
            adapter = device_adapter(session, row)
            compiled = None
            if body.command_type == "mission.upload":
                snapshot = require(session, SnapshotRow, p.snapshot_id, error).content
                if validate(snapshot, p.content)["status"] != "passed":
                    raise error(
                        422,
                        "PLAN_VALIDATION_FAILED",
                        "方案未通过当前独立检查，不能编译上传。",
                    )
                loaded = {
                    (f["plan_id"], f["sortie_id"])
                    for f in engine().records(session, row.id, "execution.fact")
                    if f["kind"] == "loaded"
                }
                future = [
                    r
                    for r in p.content["sorties"]
                    if r["drone_id"] == body.device_id
                    and (p.id, r["sortie_id"]) not in loaded
                    and r["prepare_start_s"] >= row.content["time_s"] - 1e-6
                ]
                import asyncio

                compiled = asyncio.run(
                    adapter.compile_mission(
                        body.device_id,
                        future,
                        {"mode": "simulation", "validated": True, "plan_id": p.id},
                    )
                )
                asyncio.run(
                    adapter.upload_mission(
                        body.device_id, compiled, {"execution_id": row.id}
                    )
                )
            store(
                session,
                "command",
                value["command_id"],
                row.id,
                digest,
                {
                    **value,
                    "fault": body.simulation_fault,
                    "compiled_mission": compiled,
                    "protocol_version": 2,
                },
            )
            store(
                session, "command.request", body.idempotency_key, row.id, digest, value
            )
            return value

    @app.get("/api/v1/commands/{command_id}", response_model=CommandView)
    def get_command(command_id: str):
        with database.session(immediate=True) as session:
            r = require(session, OperationRecordRow, ("command", command_id), error)
            return command_view(session, r)

    def command_view(session, r):
        v = copy.deepcopy(r.content)
        elapsed = timestamp(now()) - timestamp(v["created_at"])
        terminal = {"succeeded", "rejected", "expired", "indeterminate"}
        if v["status"] not in terminal:
            execution = require(session, ExecutionRow, v["execution_id"], error)
            if timestamp(now()) >= timestamp(v["expires_at"]):
                v.update(
                    status="expired" if v["status"] == "queued" else "indeterminate",
                    evidence="TTL elapsed; no confirmed completion",
                )
            elif not execution.content["connected"] and elapsed >= 0.4:
                v.update(
                    status="indeterminate",
                    evidence="Simulation link disconnected; no ACK or completion readback",
                )
            elif elapsed >= 0.8 and v["fault"] == "ack_timeout":
                v.update(
                    status="indeterminate",
                    evidence="SimulationAdapter: ACK timeout; no automatic retry",
                )
            elif elapsed >= 0.8 and v["fault"] == "reject":
                v.update(
                    status="rejected", evidence="SimulationAdapter rejected upload"
                )
            elif elapsed >= 1.2 and v["fault"] == "completion_timeout":
                if not v.get("action_dispatched"):
                    try:
                        finish_device_command(session, v)
                    except (ValueError, KeyError, TypeError):
                        pass
                    v["action_dispatched"] = True
                v.update(
                    status="indeterminate",
                    acknowledged_at=v["acknowledged_at"] or now(),
                    evidence="ACK received but completion not observed",
                )
            elif elapsed >= 1.2:
                try:
                    observed = finish_device_command(session, v)
                    v.update(
                        status="succeeded",
                        acknowledged_at=v["acknowledged_at"] or now(),
                        completed_at=now(),
                        observed_state=observed,
                        evidence="Persisted SimulationAdapter mission state readback confirmed",
                    )
                except (ValueError, KeyError, TypeError) as exc:
                    v.update(
                        status="indeterminate",
                        acknowledged_at=v["acknowledged_at"] or now(),
                        evidence="No confirmed device state: " + str(exc)[:200],
                    )
            elif elapsed >= 0.4:
                v.update(
                    status="acknowledged",
                    acknowledged_at=v["acknowledged_at"] or now(),
                    evidence="SimulationAdapter ACK; action completion pending",
                )
            else:
                v["status"] = "sent"
            r.content = v
        return {k: x for k, x in v.items() if k in CommandView.model_fields}

    @app.get(
        "/api/v1/executions/{execution_id}/analysis", response_model=ExecutionAnalysis
    )
    def analysis(execution_id: str):
        with database.session(immediate=True) as session:
            row = require(session, ExecutionRow, execution_id, error)
            v = engine().view(session, row)
            schedule = current_schedule(session, row)
            allocated = {c for _, _, r, _ in schedule for c in r["cargo_ids"]}
            initial, snap, _ = engine().plan_data(session, v["initial_plan_id"])
            required = sum(d["required_quantity"] for d in snap["scenario"]["demands"])
            events = events_for(session, row.id)
            for e in events:
                if e["event_type"] == "demand.added" and e["status"] != "withdrawn":
                    raw = require(
                        session,
                        OperationRecordRow,
                        ("execution.event.input", row.id + ":" + e["event_id"]),
                        error,
                    ).content
                    required += raw["demand"]["required_quantity"]
            expected = {
                cid: visit["delivery_complete_s"]
                for sortie in initial["sorties"]
                for visit in sortie["visits"]
                for cid in visit["cargo_ids"]
            }
            deviations = [
                {
                    "cargo_id": cid,
                    "plan_id": fact["plan_id"],
                    "sortie_id": fact["sortie_id"],
                    "initial_expected_s": expected.get(cid),
                    "delivered_s": fact["time_s"],
                    "difference_s": (
                        fact["time_s"] - expected[cid] if cid in expected else None
                    ),
                }
                for fact in v["facts"]
                if fact["kind"] == "delivered"
                for cid in fact["cargo_ids"]
            ]
            return {
                "execution_id": row.id,
                "facts_cursor": v["facts_cursor"],
                "source": "simulation",
                "allocated_quantity": len(allocated),
                "delivered_quantity": len(v["delivered_cargo_ids"]),
                "unserved_quantity": max(0, required - len(v["delivered_cargo_ids"])),
                "delivery_rows": [f for f in v["facts"] if f["kind"] == "delivered"],
                "initial_plan_id": v["initial_plan_id"],
                "active_plan_ids": [p["plan_id"] for p in v["schedule_parts"]],
                "event_count": len(events),
                "change_count": len(
                    engine().records(session, row.id, "execution.change")
                ),
                "deviation_rows": deviations,
            }

    @app.get("/api/v1/executions/{execution_id}/stream")
    async def stream(
        execution_id: str, request: Request, cursor: int = Query(default=0, ge=0)
    ):
        # SSE reconnect is snapshot + ordered immutable facts; duplicate cursors are safe.
        import asyncio

        if "cursor" not in request.query_params and request.headers.get(
            "last-event-id"
        ):
            try:
                cursor = int(request.headers["last-event-id"])
            except ValueError:
                raise error(422, "CURSOR_INVALID", "Last-Event-ID必须是事实游标整数。")
        first = await run_in_threadpool(get_execution, execution_id)
        if cursor < 0 or cursor > first["facts_cursor"]:
            raise error(
                409, "CURSOR_INVALID", "事实游标超出当前执行记录，先重新读取快照。"
            )

        async def messages():
            current = cursor
            snapshot = first
            while not await request.is_disconnected():
                v = (
                    snapshot
                    if snapshot is not None
                    else await run_in_threadpool(get_execution, execution_id)
                )
                snapshot = None
                new = [f for f in v["facts"] if f["cursor"] > current]
                if new:
                    current = max(f["cursor"] for f in new)
                yield "id: " + str(current) + "\nevent: execution\ndata: " + json.dumps(
                    {
                        "execution_id": execution_id,
                        "facts_cursor": current,
                        "facts": new,
                        "telemetry": v["telemetry"],
                        "time_s": v["time_s"],
                        "revision": v["revision"],
                        "status": v["status"],
                        "connected": v["connected"],
                    },
                    ensure_ascii=False,
                ) + "\n\n"
                await asyncio.sleep(1)

        return StreamingResponse(
            messages(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache"},
        )

    @app.get("/api/v1/executions/{execution_id}/export")
    def export_execution(
        execution_id: str, version: int = Query(default=1, ge=1, le=2)
    ):
        with database.session(immediate=True) as session:
            row = require(session, ExecutionRow, execution_id, error)
            changes = [
                change_view(session, r)
                for r in session.scalars(
                    select(OperationRecordRow).where(
                        OperationRecordRow.namespace == "execution.change",
                        OperationRecordRow.owner_id == row.id,
                    )
                )
            ]
            view = engine().view(session, row)
            if version == 2:
                from backend.app.execution_archive import (
                    document,
                    seal,
                    validate_bundle,
                )

                commands = [
                    command_view(session, r)
                    for r in session.scalars(
                        select(OperationRecordRow).where(
                            OperationRecordRow.namespace == "command",
                            OperationRecordRow.owner_id == row.id,
                        )
                    )
                ]
                references = {
                    c["repair_reference_id"]: require(
                        session,
                        OperationRecordRow,
                        ("solver.repair.reference", c["repair_reference_id"]),
                        error,
                    ).content
                    for c in changes
                    if c.get("repair_reference_id")
                }
                plan_ids = {view["initial_plan_id"], view["desired_plan_id"]}
                plan_ids.update(
                    d["document_id"]
                    for ref in references.values()
                    for d in ref["documents"]
                    if d["kind"] == "plan"
                )
                plan_ids.update(p["plan_id"] for p in view["schedule_parts"])
                plan_ids.update(f["plan_id"] for f in view["facts"])
                plan_ids.update(
                    c["candidate_plan_id"] for c in changes if c["candidate_plan_id"]
                )
                plan_ids.update(c["desired_plan_id"] for c in commands)
                for command in commands:
                    observed = command.get("observed_state")
                    if observed:
                        plan_ids.add(observed["active_plan_id"])
                        if observed["uploaded_plan_id"]:
                            plan_ids.add(observed["uploaded_plan_id"])
                plan_ids.update(t["active_plan_id"] for t in view["telemetry"])
                plans = [
                    require(session, PlanRow, pid, error) for pid in sorted(plan_ids)
                ]
                documents = [document("plan", p.id, p.content) for p in plans]
                snapshot_ids = {p.snapshot_id for p in plans}
                snapshot_ids.update(
                    ref["input_snapshot_id"] for ref in references.values()
                )
                snapshot_ids.update(
                    d["document_id"]
                    for ref in references.values()
                    for d in ref["documents"]
                    if d["kind"] == "snapshot"
                )
                snapshot_ids.update(
                    c["job"]["snapshot_id"] for c in changes if c["job"]
                )
                for sid in sorted(snapshot_ids):
                    documents.append(
                        document(
                            "snapshot",
                            sid,
                            require(session, SnapshotRow, sid, error).content,
                        )
                    )
                documents.extend(
                    document("repair_reference", rid, ref)
                    for rid, ref in references.items()
                )
                events = events_for(session, row.id)
                for event in events:
                    eid = event["event_id"]
                    documents.append(
                        document(
                            "event_input",
                            eid,
                            require(
                                session,
                                OperationRecordRow,
                                ("execution.event.input", row.id + ":" + eid),
                                error,
                            ).content,
                        )
                    )
                    resolved = session.get(
                        OperationRecordRow,
                        ("execution.event.resolution", row.id + ":" + eid),
                    )
                    if resolved:
                        documents.append(
                            document("event_resolution", eid, resolved.content)
                        )
                bundle = seal(
                    {
                        "bundle_version": "execution-simulation-v2",
                        "source": "simulation",
                        "is_flight_controller_file": False,
                        "captured_at": now(),
                        "mission_name": require(
                            session, MissionRow, row.mission_id, error
                        ).content["name"],
                        "execution": view,
                        "events": events,
                        "changes": changes,
                        "commands": commands,
                        "documents": documents,
                    }
                )
                validate_bundle(ExecutionBundle.model_validate(bundle))
                return bundle
            return {
                "bundle_version": "execution-simulation-v1",
                "execution": view,
                "events": events_for(session, row.id),
                "changes": changes,
                "source": "simulation",
                "is_flight_controller_file": False,
            }

    def tick_commands(session):
        for command_row in session.scalars(
            select(OperationRecordRow).where(OperationRecordRow.namespace == "command")
        ):
            if command_row.content["status"] not in (
                "succeeded",
                "rejected",
                "expired",
                "indeterminate",
            ):
                command_view(session, command_row)
        for change in session.scalars(
            select(OperationRecordRow).where(
                OperationRecordRow.namespace == "execution.change"
            )
        ):
            if change.content["status"] == "applying":
                change_view(session, change)

    app.state.simulation_commands_tick = tick_commands

    from backend.app.execution_archive import register_archives

    register_archives(app, database, error)
