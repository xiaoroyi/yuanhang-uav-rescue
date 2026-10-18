"""Portable archive integrity and isolation from active execution/domain tables."""

import copy
import json

from fastapi.testclient import TestClient
from sqlalchemy import select, func

from backend.app.main import create_app
from backend.app.execution_archive import seal
from backend.app.storage import PlanRow, SnapshotRow, ExecutionRow, OperationRecordRow
from test_execution_v2 import setup, act


def test_archive_roundtrip_is_read_only_lossless_and_rejects_tampering(tmp_path):
    app = create_app(tmp_path / "runtime")
    with TestClient(app) as c:
        m, s, p, e = setup(c)
        finish = max(r["battery_released_s"] for r in p["sorties"]) + 1
        e = act(c, e, "advance", target_time_s=finish)
        endpoint = f"/api/v1/executions/{e['execution_id']}/export"
        assert c.get(endpoint).json()["bundle_version"] == "execution-simulation-v1"
        response = c.get(endpoint + "?version=2")
        assert response.status_code == 200, response.text
        bundle = response.json()
        assert bundle["bundle_version"] == "execution-simulation-v2"

        def counts():
            with app.state.database.session() as session:
                return tuple(
                    session.scalar(select(func.count()).select_from(model))
                    for model in (PlanRow, SnapshotRow, ExecutionRow)
                ), session.scalar(
                    select(func.count())
                    .select_from(OperationRecordRow)
                    .where(OperationRecordRow.namespace == "execution.fact")
                )

        before = counts()

        def upload(value):
            return c.post(
                "/api/v1/execution-archives/import",
                files={
                    "file": (
                        "execution.json",
                        json.dumps(value, ensure_ascii=False).encode("utf-8"),
                        "application/json",
                    )
                },
            )

        imported = upload(bundle)
        assert imported.status_code == 201, imported.text
        summary = imported.json()
        assert (
            summary["read_only"] is True and summary["fact_count"] == e["facts_cursor"]
        )
        assert upload(bundle).json() == summary
        archive = c.get("/api/v1/execution-archives/" + summary["archive_id"]).json()
        assert archive["bundle"] == bundle
        assert (
            archive["analysis"]
            == c.get(f"/api/v1/executions/{e['execution_id']}/analysis").json()
        )
        with app.state.database.session() as session:
            for doc in bundle["documents"]:
                if doc["kind"] == "snapshot":
                    assert (
                        json.loads(doc["payload_json"])
                        == session.get(SnapshotRow, doc["document_id"]).content
                    )
                elif doc["kind"] == "plan":
                    assert (
                        json.loads(doc["payload_json"])
                        == session.get(PlanRow, doc["document_id"]).content
                    )
        assert counts() == before
        assert (
            c.post(
                f"/api/v1/executions/{summary['archive_id']}/simulation/actions",
                json={
                    "action": "start",
                    "expected_revision": 1,
                    "idempotency_key": "cannot-control-archive",
                },
            ).status_code
            == 404
        )
        tampered = copy.deepcopy(bundle)
        tampered["execution"]["delivered_cargo_ids"] = []
        assert upload(tampered).status_code == 422
        assert upload(seal(tampered)).status_code == 422
        missing = copy.deepcopy(bundle)
        missing["documents"] = [
            d for d in missing["documents"] if d["kind"] != "snapshot"
        ]
        assert upload(seal(missing)).status_code == 422
        duplicate = copy.deepcopy(bundle)
        duplicate["execution"]["facts"].append(duplicate["execution"]["facts"][0])
        duplicate["execution"]["facts_cursor"] += 1
        assert upload(seal(duplicate)).status_code == 422
        bad_source = copy.deepcopy(bundle)
        bad_source["source"] = "real"
        assert upload(bad_source).status_code == 422
        assert len(c.get("/api/v1/execution-archives").json()) == 1
        assert counts() == before
