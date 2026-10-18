"""Event-sequence evidence captured when a residual input is frozen, never reconstructed later."""

import copy
import hashlib
import json

from backend.app.operation_models import RepairEvidence, ExecutionEventInput
from backend.app.storage import OperationRecordRow
from shared.contracts import content_hash


def capture_evidence(session, rid, reference, events, facts, applied_event_ids, tick):
    from backend.app.execution_archive import document

    documents = []
    for event in events:
        key = reference["execution_id"] + ":" + event["event_id"]
        raw = session.get(OperationRecordRow, ("execution.event.input", key))
        documents.append(document("event_input", event["event_id"], raw.content))
        resolution = session.get(
            OperationRecordRow, ("execution.event.resolution", key)
        )
        if resolution:
            documents.append(
                document("event_resolution", event["event_id"], resolution.content)
            )
    value = {
        "evidence_version": "repair-event-sequence-v1",
        "reference_id": rid,
        "execution_id": reference["execution_id"],
        "execution_revision": reference["execution_revision"],
        "facts_cursor": reference["facts_cursor"],
        "time_s": tick,
        "event_fingerprint": content_hash(events),
        "pending_event_ids": [
            e["event_id"]
            for e in events
            if e["status"] != "withdrawn" and e["event_id"] not in applied_event_ids
        ],
        "events": copy.deepcopy(events),
        "facts": sorted(
            (
                copy.deepcopy(f)
                for f in facts
                if f["cursor"] <= reference["facts_cursor"]
            ),
            key=lambda f: f["cursor"],
        ),
        "event_documents": documents,
    }
    validate_evidence(value, reference)
    session.add(
        OperationRecordRow(
            namespace="solver.repair.evidence",
            id=rid,
            owner_id=reference["execution_id"],
            request_hash=content_hash(reference),
            content=value,
        )
    )


def validate_evidence(value, reference):
    RepairEvidence.model_validate(value)
    if any(
        value[key] != reference[key]
        for key in ("execution_id", "execution_revision", "facts_cursor")
    ):
        raise ValueError("修复事件证据与冻结引用不匹配。")
    if content_hash(value["events"]) != value["event_fingerprint"]:
        raise ValueError("冻结事件序列指纹不匹配。")
    if [f["cursor"] for f in value["facts"]] != list(
        range(1, value["facts_cursor"] + 1)
    ):
        raise ValueError("冻结事实序列不连续。")
    locked = {
        cid for f in value["facts"] if f["kind"] == "loaded" for cid in f["cargo_ids"]
    }
    if locked != set(reference["committed_cargo_ids"]):
        raise ValueError("冻结事实与承诺箱件不匹配。")
    docs = {}
    for doc in value["event_documents"]:
        key = (doc["kind"], doc["document_id"])
        if (
            doc["kind"] not in ("event_input", "event_resolution")
            or key in docs
            or hashlib.sha256(doc["payload_json"].encode()).hexdigest() != doc["sha256"]
        ):
            raise ValueError("冻结事件原文类型、身份或SHA不匹配。")
        docs[key] = json.loads(doc["payload_json"])
    event_ids = set()
    for event in value["events"]:
        eid = event["event_id"]
        if (
            eid in event_ids
            or event["execution_id"] != value["execution_id"]
            or event["facts_cursor"] > value["facts_cursor"]
            or event["time_s"] > value["time_s"]
        ):
            raise ValueError("冻结事件身份/时间/游标不匹配。")
        event_ids.add(eid)
        raw = docs.get(("event_input", eid))
        if (
            raw is None
            or ExecutionEventInput.model_validate(raw).event_id != eid
            or any(
                raw.get(key) != event.get(key)
                for key in ("event_type", "object_id", "reason")
            )
        ):
            raise ValueError("冻结事件缺少匹配原输入。")
        if event["status"] == "withdrawn" and ("event_resolution", eid) not in docs:
            raise ValueError("冻结误报缺少纠错原文。")
    if not set(value["pending_event_ids"]).issubset(event_ids):
        raise ValueError("冻结待处理事件引用缺失。")


def comparison_input_hash(scenario):
    # The four fields are storage/display identities, not physical constraints.
    return content_hash(
        {
            k: v
            for k, v in scenario.items()
            if k not in ("scenario_id", "state_version", "name", "mode")
        }
    )
