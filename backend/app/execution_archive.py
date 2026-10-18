"""Lossless simulation archives. Import never creates controllable domain rows."""

from __future__ import annotations
import copy
import hashlib
import json

from fastapi import File, UploadFile
from pydantic import ValidationError
from sqlalchemy import select

from backend.app.jobs import now
from backend.app.operation_models import (
    ExecutionBundle,
    ExecutionArchiveView,
    ExecutionArchiveSummary,
    ExecutionEventInput,
)
from backend.app.storage import OperationRecordRow
from shared.contracts import (
    content_hash,
    validate_snapshot,
    validate_plan,
    ContractError,
)

MAX_BYTES = 20 * 1024 * 1024


def document(kind, document_id, value):
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return {
        "kind": kind,
        "document_id": document_id,
        "payload_json": payload,
        "sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
    }


def seal(value):
    normalized = ExecutionBundle.model_validate(
        {**value, "content_sha256": "0" * 64}
    ).model_dump(mode="json", exclude_unset=True)
    normalized["content_sha256"] = content_hash(
        {k: v for k, v in normalized.items() if k != "content_sha256"}
    )
    return normalized


def unpack(value):
    result = {}
    for item in value["documents"]:
        key = (item["kind"], item["document_id"])
        if key in result:
            raise ValueError("重复的文档kind/id。")
        if (
            hashlib.sha256(item["payload_json"].encode("utf-8")).hexdigest()
            != item["sha256"]
        ):
            raise ValueError("文档SHA256不匹配。")
        decoded = json.loads(
            item["payload_json"],
            parse_constant=lambda v: (_ for _ in ()).throw(
                ValueError("不允许非有限数字。")
            ),
        )
        if not isinstance(decoded, dict):
            raise ValueError("文档必须为JSON对象。")
        result[key] = decoded
    return result


def analyze(value, docs):
    e = value["execution"]
    initial = docs["plan", e["initial_plan_id"]]
    scene = docs["snapshot", initial["snapshot_id"]]["scenario"]
    required = sum(d["required_quantity"] for d in scene["demands"])
    for event in value["events"]:
        if event["event_type"] == "demand.added" and event["status"] != "withdrawn":
            required += docs["event_input", event["event_id"]]["demand"][
                "required_quantity"
            ]
    allocated = {
        cid
        for part in e["schedule_parts"]
        for r in docs["plan", part["plan_id"]]["sorties"]
        if r["sortie_id"] in part["sortie_ids"]
        for cid in r["cargo_ids"]
    }
    expected = {
        cid: v["delivery_complete_s"]
        for r in initial["sorties"]
        for v in r["visits"]
        for cid in v["cargo_ids"]
    }
    deliveries = [f for f in e["facts"] if f["kind"] == "delivered"]
    return {
        "execution_id": e["execution_id"],
        "facts_cursor": e["facts_cursor"],
        "source": "simulation",
        "allocated_quantity": len(allocated),
        "delivered_quantity": len(e["delivered_cargo_ids"]),
        "unserved_quantity": max(0, required - len(e["delivered_cargo_ids"])),
        "delivery_rows": deliveries,
        "initial_plan_id": e["initial_plan_id"],
        "active_plan_ids": [p["plan_id"] for p in e["schedule_parts"]],
        "event_count": len(value["events"]),
        "change_count": len(value["changes"]),
        "deviation_rows": [
            {
                "cargo_id": cid,
                "plan_id": f["plan_id"],
                "sortie_id": f["sortie_id"],
                "initial_expected_s": expected.get(cid),
                "delivered_s": f["time_s"],
                "difference_s": (
                    f["time_s"] - expected[cid] if cid in expected else None
                ),
            }
            for f in deliveries
            for cid in f["cargo_ids"]
        ],
    }


def validate_bundle(model):
    value = model.model_dump(mode="json", exclude_unset=True)
    digest = content_hash({k: v for k, v in value.items() if k != "content_sha256"})
    if digest != value["content_sha256"]:
        raise ValueError("执行包整体校验不匹配。")
    docs = unpack(value)
    plans = {key[1]: raw for key, raw in docs.items() if key[0] == "plan"}
    snapshots = {key[1]: raw for key, raw in docs.items() if key[0] == "snapshot"}
    for sid, snapshot in snapshots.items():
        if snapshot["snapshot_id"] != sid:
            raise ValueError("快照文档身份不匹配。")
        validate_snapshot(snapshot)
    for pid, plan in plans.items():
        if plan["plan_id"] != pid or plan["snapshot_id"] not in snapshots:
            raise ValueError("方案文档身份/快照引用缺失。")
        validate_plan(plan, snapshots[plan["snapshot_id"]])
    e = value["execution"]
    referenced = {e["initial_plan_id"], e["desired_plan_id"]}
    referenced.update(p["plan_id"] for p in e["schedule_parts"])
    referenced.update(f["plan_id"] for f in e["facts"])
    referenced.update(
        c["candidate_plan_id"] for c in value["changes"] if c["candidate_plan_id"]
    )
    referenced.update(c["desired_plan_id"] for c in value["commands"])
    for command in value["commands"]:
        observed = command.get("observed_state")
        if observed:
            referenced.add(observed["active_plan_id"])
            if observed["uploaded_plan_id"]:
                referenced.add(observed["uploaded_plan_id"])
    referenced.update(t["active_plan_id"] for t in e["telemetry"])
    if not referenced.issubset(plans):
        raise ValueError("执行/候选/指令引用的方案未完整封装。")
    for change in value["changes"]:
        if change["execution_id"] != e["execution_id"]:
            raise ValueError("调整归属的执行不符。")
        if change["job"] and change["job"]["snapshot_id"] not in snapshots:
            raise ValueError("缺少调整Job原输入快照。")
        if change.get("repair_reference_id"):
            from backend.app.operation_models import ExecutionRepairReference

            ref = docs.get(("repair_reference", change["repair_reference_id"]))
            if ref is None:
                raise ValueError("缺少残余修复原始引用。")
            ExecutionRepairReference.model_validate(ref)
            if (
                ref["execution_id"] != e["execution_id"]
                or ref["input_snapshot_id"] not in snapshots
                or ref["facts_cursor"] != change["facts_cursor"]
                or ref["execution_revision"] != change["execution_revision"]
                or ref["committed_cargo_ids"] != change["committed_cargo_ids"]
            ):
                raise ValueError("修复引用的执行/输入/承诺与变更不一致。")
            loaded = {
                cid
                for fact in e["facts"]
                if fact["kind"] == "loaded" and fact["cursor"] <= ref["facts_cursor"]
                for cid in fact["cargo_ids"]
            }
            if loaded != set(ref["committed_cargo_ids"]):
                raise ValueError("修复承诺与该游标之前的装载事实不符。")
            for item in ref["documents"]:
                if (
                    item["kind"] not in ("plan", "snapshot")
                    or (item["kind"], item["document_id"]) not in docs
                ):
                    raise ValueError("缺少修复原文的领域文档。")
                if (
                    document(
                        item["kind"],
                        item["document_id"],
                        docs[item["kind"], item["document_id"]],
                    )
                    != item
                ):
                    raise ValueError("修复原文与封装的领域文档不符。")
            if change.get("diff") and change["candidate_plan_id"]:
                from backend.app.repair_diff import reference_sorties, compare_future

                expected = compare_future(
                    reference_sorties(ref),
                    plans[change["candidate_plan_id"]],
                    change["committed_cargo_ids"],
                )
                if expected != change["diff"]:
                    raise ValueError("修复差异与冻结的来源/候选不符。")
    for command in value["commands"]:
        if command["execution_id"] != e["execution_id"]:
            raise ValueError("指令归属的执行不符。")
        observed = command.get("observed_state")
        if observed and (
            observed["execution_id"] != e["execution_id"]
            or observed["device_id"] != command["device_id"]
            or observed["device_id"]
            not in {d["drone_id"] for d in scene_drones(plans, snapshots, e)}
        ):
            raise ValueError("设备观测的执行/机体归属不符。")
    for part in e["schedule_parts"]:
        p = plans[part["plan_id"]]
        if not set(part["sortie_ids"]).issubset({r["sortie_id"] for r in p["sorties"]}):
            raise ValueError("执行段引用未知运输架次。")
        if not set(part.get("relay_sortie_ids", [])).issubset(
            {r["relay_sortie_id"] for r in p.get("relay_sorties", [])}
        ):
            raise ValueError("执行段引用未知中继架次。")
    facts = e["facts"]
    if [f["cursor"] for f in facts] != list(range(1, e["facts_cursor"] + 1)) or len(
        {f["fact_id"] for f in facts}
    ) != len(facts):
        raise ValueError("事实游标不连续或事实重复。")
    delivered = []
    for fact in facts:
        if fact["time_s"] > e["time_s"] + 1e-6 or fact["time_s"] < 0:
            raise ValueError("事实时刻超出截取窗口。")
        if fact["kind"] != "plan_adopted" and fact["sortie_id"] is None:
            raise ValueError("任务事实缺少来源架次。")
        if fact["sortie_id"] is not None:
            p = plans[fact["plan_id"]]
            transport = next(
                (r for r in p["sorties"] if r["sortie_id"] == fact["sortie_id"]), None
            )
            relay = next(
                (
                    r
                    for r in p.get("relay_sorties", [])
                    if r["relay_sortie_id"] == fact["sortie_id"]
                ),
                None,
            )
            r = transport or relay
            if (
                not r
                or fact["drone_id"] != r["drone_id"]
                or not set(fact["cargo_ids"]).issubset(r.get("cargo_ids", []))
            ):
                raise ValueError("事实的架次/机体/箱件归属不符。")
        if fact["kind"] == "delivered":
            delivered.extend(fact["cargo_ids"])
    if len(set(delivered)) != len(delivered) or sorted(delivered) != sorted(
        e["delivered_cargo_ids"]
    ):
        raise ValueError("重复交付或交付汇总不符。")
    event_ids = set()
    for event in value["events"]:
        eid = event["event_id"]
        if eid in event_ids or event["execution_id"] != e["execution_id"]:
            raise ValueError("事件编号/执行归属不符。")
        event_ids.add(eid)
        raw = docs.get(("event_input", eid))
        if (
            raw is None
            or ExecutionEventInput.model_validate(raw).event_id != eid
            or raw["event_type"] != event["event_type"]
            or raw["reason"] != event["reason"]
            or raw.get("object_id") != event.get("object_id")
        ):
            raise ValueError("缺少匹配的事件原输入。")
        if event["facts_cursor"] > e["facts_cursor"] or event["time_s"] > e["time_s"]:
            raise ValueError("事件超出截取窗口。")
        if event["status"] == "withdrawn" and ("event_resolution", eid) not in docs:
            raise ValueError("缺少纠错审计。")
    if not set(e.get("applied_event_ids", [])).issubset(event_ids):
        raise ValueError("采纳事件引用缺失。")
    return value, docs


def scene_drones(plans, snapshots, execution):
    initial = plans[execution["initial_plan_id"]]
    return snapshots[initial["snapshot_id"]]["scenario"]["drones"]


def register_archives(app, database, error):
    def summary(rec):
        b = rec.content["bundle"]
        e = b["execution"]
        return {
            "archive_id": rec.id,
            "execution_id": e["execution_id"],
            "mission_name": b["mission_name"],
            "imported_at": rec.content["imported_at"],
            "captured_at": b["captured_at"],
            "captured_time_s": e["time_s"],
            "captured_status": e["status"],
            "fact_count": e["facts_cursor"],
            "plan_count": sum(d["kind"] == "plan" for d in b["documents"]),
            "content_sha256": b["content_sha256"],
            "read_only": True,
        }

    @app.post(
        "/api/v1/execution-archives/import",
        response_model=ExecutionArchiveSummary,
        status_code=201,
    )
    def import_archive(file: UploadFile = File(...)):
        raw = file.file.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise error(413, "UPLOAD_TOO_LARGE", "运行档案上限20 MiB。")
        try:
            model = ExecutionBundle.model_validate_json(raw)
            value, _ = validate_bundle(model)
        except (
            ValidationError,
            ContractError,
            ValueError,
            KeyError,
            TypeError,
            RecursionError,
        ) as exc:
            raise error(422, "ARCHIVE_INVALID", str(exc)[:1000]) from exc
        aid = "ARC-" + value["content_sha256"][:24].upper()
        with database.session(immediate=True) as session:
            rec = session.get(OperationRecordRow, ("execution.archive", aid))
            if rec is None:
                rec = OperationRecordRow(
                    namespace="execution.archive",
                    id=aid,
                    owner_id=aid,
                    request_hash=value["content_sha256"],
                    content={"bundle": value, "imported_at": now()},
                )
                session.add(rec)
            return summary(rec)

    @app.get("/api/v1/execution-archives", response_model=list[ExecutionArchiveSummary])
    def list_archives():
        with database.session() as session:
            return sorted(
                [
                    summary(r)
                    for r in session.scalars(
                        select(OperationRecordRow).where(
                            OperationRecordRow.namespace == "execution.archive"
                        )
                    )
                ],
                key=lambda v: v["imported_at"],
                reverse=True,
            )

    @app.get(
        "/api/v1/execution-archives/{archive_id}", response_model=ExecutionArchiveView
    )
    def get_archive(archive_id: str):
        with database.session() as session:
            rec = session.get(OperationRecordRow, ("execution.archive", archive_id))
            if rec is None:
                raise error(404, "REFERENCE_INVALID", "运行档案不存在。")
            b = rec.content["bundle"]
            docs = unpack(b)
            return {
                "summary": summary(rec),
                "bundle": b,
                "plans": [v for k, v in docs.items() if k[0] == "plan"],
                "snapshots": [v for k, v in docs.items() if k[0] == "snapshot"],
                "analysis": analyze(b, docs),
            }
