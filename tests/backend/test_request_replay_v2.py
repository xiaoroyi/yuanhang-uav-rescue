"""Upgrade-safe receipts and durable admission at the real worker dispatch boundary."""

import copy
from concurrent.futures import ThreadPoolExecutor
import threading

from fastapi.testclient import TestClient
from sqlalchemy import select
from backend.app.main import create_app
from backend.app.operation_models import (
    ExperimentRequest,
    ExecutionEventInput,
    RepairRequest,
)
from backend.app.storage import OperationRecordRow, JobRow
from shared.contracts import content_hash
from test_execution_v2 import setup, post, act, await_job


def prepare(c):
    _, s, p, e = setup(c)
    e = act(c, e, "advance", target_time_s=1)
    event = {
        "event_id": "replay-exit",
        "expected_revision": e["revision"],
        "event_type": "drone.unavailable",
        "object_id": s["drones"][-1]["drone_id"],
        "reason": "Isolated future resource exit for receipt checks",
    }
    post(c, f"/executions/{e['execution_id']}/events", event, 201)
    return p, c.get("/api/v1/executions/" + e["execution_id"]).json(), event


def test_old_static_experiment_receipt_replays_but_changed_input_still_conflicts(
    tmp_path,
):
    app = create_app(tmp_path / "runtime")
    with TestClient(app) as c:
        m = post(
            c,
            "/missions",
            {
                "name": "Old receipt replay",
                "template": "compact",
                "idempotency_key": "m",
            },
            201,
        )
        snap = post(
            c,
            f"/scenarios/{m['current_scenario_id']}/snapshots",
            {"expected_state_version": 1},
            201,
        )
        body = {
            "name": "Legacy static campaign",
            "source_snapshot_id": snap["snapshot_id"],
            "suite": "strategy",
            "seeds": [7],
            "time_limit_s": 1,
            "idempotency_key": "exp",
        }
        created = post(c, "/experiments", body, 202)
        old = ExperimentRequest.model_validate(body).model_dump(mode="json")
        old.pop("repair_reference_id")
        with app.state.database.session(immediate=True) as session:
            session.get(
                OperationRecordRow, ("experiment.create", "exp")
            ).request_hash = content_hash(old)
        assert (
            post(c, "/experiments", body, 202)["experiment_id"]
            == created["experiment_id"]
        )
        assert (
            c.post("/api/v1/experiments", json={**body, "name": "changed"}).status_code
            == 409
        )
        post(c, "/experiments/" + created["experiment_id"] + "/cancel", {}, 202)


def test_old_event_and_full_repair_receipts_keep_semantics_after_additive_fields(
    tmp_path,
):
    app = create_app(tmp_path / "runtime")
    with TestClient(app) as c:
        _, e, event = prepare(c)
        old = ExecutionEventInput.model_validate(event).model_dump(mode="json")
        old.pop("weather")
        event_url = f"/executions/{e['execution_id']}/events"
        with app.state.database.session(immediate=True) as session:
            session.get(
                OperationRecordRow,
                ("execution.event", e["execution_id"] + ":" + event["event_id"]),
            ).request_hash = content_hash(old)
        assert post(c, event_url, event, 201)["event_id"] == event["event_id"]
        assert (
            c.post(
                "/api/v1" + event_url, json={**event, "reason": "changed"}
            ).status_code
            == 409
        )
        body = {
            "expected_revision": e["revision"],
            "idempotency_key": "legacy-full",
            "time_limit_s": 8,
            "repair_policy": "full",
        }
        repair_url = f"/executions/{e['execution_id']}/replan-jobs"
        created = post(c, repair_url, body, 202)
        old = RepairRequest.model_validate(body).model_dump(mode="json")
        old.pop("repair_policy")
        with app.state.database.session(immediate=True) as session:
            session.get(
                OperationRecordRow,
                ("execution.repair.request", e["execution_id"] + ":legacy-full"),
            ).request_hash = content_hash(old)
        legacy = {k: v for k, v in body.items() if k != "repair_policy"}
        assert post(c, repair_url, legacy, 202)["change_id"] == created["change_id"]
        assert post(c, repair_url, body, 202)["change_id"] == created["change_id"]
        assert (
            c.post(
                "/api/v1" + repair_url, json={**body, "repair_policy": "dependency"}
            ).status_code
            == 409
        )
        assert (
            c.post(
                "/api/v1" + repair_url, json={**legacy, "objective": "energy"}
            ).status_code
            == 409
        )
        assert await_job(c, created["job"])["has_validated_plan"]


def test_concurrent_identical_repairs_share_one_admission_and_one_real_job(tmp_path):
    app = create_app(tmp_path / "runtime")
    with TestClient(app) as c:
        _, e, _ = prepare(c)
        entered = threading.Event()
        release = threading.Event()
        lock = threading.Lock()
        calls = [0]
        original = app.state.jobs.submit

        def delayed(*args, **kwargs):
            with lock:
                calls[0] += 1
                first = calls[0] == 1
            if first:
                entered.set()
                assert release.wait(8)
            return original(*args, **kwargs)

        app.state.jobs.submit = delayed
        body = {
            "expected_revision": e["revision"],
            "idempotency_key": "same-dispatch",
            "repair_policy": "full",
            "time_limit_s": 8,
        }
        url = f"/executions/{e['execution_id']}/replan-jobs"
        with ThreadPoolExecutor(max_workers=1) as pool:
            first = pool.submit(c.post, "/api/v1" + url, json=body)
            assert entered.wait(8)
            try:
                second = post(c, url, body, 202)
                assert second["status"] == "computing" and second["job"] is None
            finally:
                release.set()
            response = first.result(timeout=12)
            assert response.status_code == 202, response.text
        created = response.json()
        assert created["change_id"] == second["change_id"] and calls[0] == 1
        assert await_job(c, created["job"])["has_validated_plan"]
        replay = post(c, url, body, 202)
        assert replay["job"]["job_id"] == created["job"]["job_id"]
        with app.state.database.session() as session:
            rows = list(
                session.scalars(
                    select(OperationRecordRow).where(
                        OperationRecordRow.namespace == "execution.change",
                        OperationRecordRow.owner_id == e["execution_id"],
                    )
                )
            )
            assert len(rows) == 1
            jobs = list(
                session.scalars(
                    select(JobRow).where(
                        JobRow.scenario_id == created["job"]["scenario_id"]
                    )
                )
            )
            assert len(jobs) == 1


def test_restart_marks_unbound_admission_uncertain_without_redispatching(tmp_path):
    directory = tmp_path / "runtime"
    app = create_app(directory)
    with TestClient(app) as c:
        _, e, _ = prepare(c)
        body = {
            "expected_revision": e["revision"],
            "idempotency_key": "interrupted-admission",
            "repair_policy": "full",
            "time_limit_s": 8,
        }
        url = f"/executions/{e['execution_id']}/replan-jobs"
        created = post(c, url, body, 202)
        await_job(c, created["job"])
        with app.state.database.session(immediate=True) as session:
            row = session.get(
                OperationRecordRow, ("execution.change", created["change_id"])
            )
            # Model a lost bind after a durable Job was created. Its original row
            # stays in the audit history; restart must not infer or resend it.
            value = copy.deepcopy(row.content)
            value.update(job=None, candidate_plan_id=None, status="computing")
            row.content = value
            before = len(list(session.scalars(select(JobRow))))
    with TestClient(create_app(directory)) as c:
        recovered = c.get(
            f"/api/v1/executions/{e['execution_id']}/plan-changes/{created['change_id']}"
        ).json()
        assert (
            recovered["status"] == "failed"
            and "未确认" in recovered["message"]
            and recovered["job"] is None
        )
        assert post(c, url, body, 202)["status"] == "failed"
        with c.app.state.database.session() as session:
            assert len(list(session.scalars(select(JobRow)))) == before
