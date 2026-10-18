"""Real, isolated solver campaigns preserve failures and immutable input evidence."""

import base64
import copy
import hashlib
import json
import time

from fastapi.testclient import TestClient

from backend.app.main import create_app
from backend.app.storage import (
    ScenarioRow,
    SnapshotRow,
    PlanRow,
    ExecutionRow,
    OperationRecordRow,
)
from shared.contracts import content_hash
from test_execution_v2 import setup, post


def spec(snapshot, key="benchmark", suite="strategy"):
    return {
        "name": "Reproducible comparison",
        "source_snapshot_id": snapshot,
        "suite": suite,
        "objective_policy": "tradeoff_v2",
        "seeds": [7],
        "time_limit_s": 3,
        "idempotency_key": key,
    }


def finished(c, eid):
    for _ in range(600):
        run = c.get("/api/v1/experiments/" + eid).json()
        if run["status"] in ("completed", "canceled"):
            return run
        time.sleep(0.05)
    raise AssertionError(run)


def test_strategy_campaign_uses_real_workers_isolated_input_and_lossless_export(
    tmp_path,
):
    directory = tmp_path / "runtime"
    app = create_app(directory)
    with TestClient(app) as c:
        _, s, p, e = setup(c)
        with app.state.database.session() as session:
            original = [
                copy.deepcopy(session.get(model, key).content)
                for model, key in (
                    (ScenarioRow, s["scenario_id"]),
                    (SnapshotRow, p["snapshot_id"]),
                    (PlanRow, p["plan_id"]),
                    (ExecutionRow, e["execution_id"]),
                )
            ]
        body = spec(p["snapshot_id"])
        run = post(c, "/experiments", body, 202)
        eid = run["experiment_id"]
        assert post(c, "/experiments", body, 202)["experiment_id"] == eid
        assert (
            c.post("/api/v1/experiments", json={**body, "name": "changed"}).status_code
            == 409
        )
        assert run["snapshot_id"] != p["snapshot_id"] and len(run["cases"]) == 3
        done = finished(c, eid)
        assert done["status"] == "completed"
        assert {case["objective"] for case in done["cases"]} == {
            "time",
            "energy",
            "balanced",
        }
        assert all(
            case["job"]
            and case["status"] == "completed"
            and case["job"]["has_validated_plan"]
            for case in done["cases"]
        ), done
        for case in done["cases"]:
            plan = c.get("/api/v1/plans/" + case["job"]["plan_id"]).json()
            assert plan["snapshot_id"] == done["snapshot_id"]
            assert case["energy_kwh"] == plan["metrics"]["energy_kwh"]
            assert case["makespan_s"] == plan["metrics"]["makespan_s"]
            assert (
                case["allocated_quantity"] == 32
                and case["validation_status"] == "passed"
            )
        with app.state.database.session() as session:
            after = [
                session.get(model, key).content
                for model, key in (
                    (ScenarioRow, s["scenario_id"]),
                    (SnapshotRow, p["snapshot_id"]),
                    (PlanRow, p["plan_id"]),
                    (ExecutionRow, e["execution_id"]),
                )
            ]
        assert original == after
        response = c.get("/api/v1/experiments/" + eid + "/export")
        assert response.status_code == 200, response.text
        bundle = response.json()
        assert bundle["content_sha256"] == content_hash(
            {k: v for k, v in bundle.items() if k != "content_sha256"}
        )
        assert bundle["missing_artifacts"] == [] and len(bundle["artifacts"]) == 12
        assert len([d for d in bundle["documents"] if d["kind"] == "snapshot"]) == 2
        for artifact in bundle["artifacts"]:
            raw = base64.b64decode(artifact["content_base64"], validate=True)
            assert (
                len(raw) == artifact["byte_count"]
                and hashlib.sha256(raw).hexdigest() == artifact["content_sha256"]
            )
            if artifact["name"] == "input.json":
                payload = json.loads(raw)
                assert payload["snapshot"]["snapshot_id"] == done["snapshot_id"]
                assert (
                    payload["options"]["seed"] == 7
                    and payload["options"]["time_limit_s"] == 3
                )
        assert done["environment"]["cp_sat_threads"] == 1
    with TestClient(create_app(directory)) as c:
        restored = c.get("/api/v1/experiments/" + eid).json()
        assert (
            restored["cases"] == done["cases"] and restored["groups"] == done["groups"]
        )


def test_unvalidated_cases_are_preserved_in_counts_and_logs_not_zero_metrics(tmp_path):
    app = create_app(tmp_path / "runtime")
    with TestClient(app) as c:
        m = post(
            c,
            "/missions",
            {
                "name": "No fleet case",
                "template": "compact",
                "idempotency_key": "source",
            },
            201,
        )
        s = c.get("/api/v1/scenarios/" + m["current_scenario_id"]).json()
        for d in s["drones"]:
            d["status"] = "unavailable"
        changed = c.put(
            "/api/v1/scenarios/" + s["scenario_id"],
            json={"expected_state_version": 1, "scenario": s},
        )
        assert changed.status_code == 200
        snapshot = post(
            c,
            f"/scenarios/{s['scenario_id']}/snapshots",
            {"expected_state_version": 2},
            201,
        )
        queued = post(
            c, "/experiments", spec(snapshot["snapshot_id"], suite="search"), 202
        )
        done = finished(c, queued["experiment_id"])
        assert done["status"] == "completed" and len(done["cases"]) == 2
        assert all(
            case["job"]
            and not case["job"]["has_validated_plan"]
            and case["energy_kwh"] is None
            for case in done["cases"]
        )
        assert sum(g["failed_or_unvalidated"] for g in done["groups"]) == 2
        assert sum(g["feasible"] for g in done["groups"]) == 0
        assert all(g["feasible_energy_median_kwh"] is None for g in done["groups"])
        bundle = c.get(f"/api/v1/experiments/{done['experiment_id']}/export").json()
        outcomes = [
            json.loads(base64.b64decode(a["content_base64"]))
            for a in bundle["artifacts"]
            if a["name"] == "outcome.json"
        ]
        assert len(outcomes) == 2 and all(o["plan"] is None for o in outcomes)


def test_queued_cancellation_and_dispatch_interruption_never_blindly_resubmit(tmp_path):
    directory = tmp_path / "runtime"
    app = create_app(directory)
    with TestClient(app) as c:
        # Stop only the campaign dispatcher to inspect the durable pre-dispatch state.
        app.state.experiments.close()
        m = post(
            c,
            "/missions",
            {
                "name": "Queued comparison",
                "template": "compact",
                "idempotency_key": "source",
            },
            201,
        )
        sid = m["current_scenario_id"]
        snapshot = post(
            c, f"/scenarios/{sid}/snapshots", {"expected_state_version": 1}, 201
        )
        body = spec(snapshot["snapshot_id"])
        for seeds in ([1, 1], [True], [-1], [1, 2, 3, 4]):
            assert (
                c.post("/api/v1/experiments", json={**body, "seeds": seeds}).status_code
                == 422
            )
        run = post(c, "/experiments", body, 202)
        canceled = post(c, f"/experiments/{run['experiment_id']}/cancel", {}, 202)
        assert canceled["status"] == "canceled" and all(
            case["status"] == "canceled" and case["job"] is None
            for case in canceled["cases"]
        )
        interrupted = post(
            c, "/experiments", {**body, "idempotency_key": "interrupted"}, 202
        )
        with app.state.database.session(immediate=True) as session:
            row = session.get(
                OperationRecordRow, ("experiment.run", interrupted["experiment_id"])
            )
            value = copy.deepcopy(row.content)
            value["cases"][0]["status"] = "dispatching"
            row.content = value
    with TestClient(create_app(directory)) as c:
        state = c.get("/api/v1/experiments/" + interrupted["experiment_id"]).json()
        assert (
            state["cases"][0]["status"] == "failed" and state["cases"][0]["job"] is None
        )
        assert "不自动重发" in state["cases"][0]["message"]
        post(c, f"/experiments/{interrupted['experiment_id']}/cancel", {}, 202)


def test_dispatched_queued_job_is_really_canceled_and_busy_queue_retries_without_failing_case(
    tmp_path,
):
    from backend.app.main import AppError

    app = create_app(tmp_path / "runtime")
    with TestClient(app) as c:
        m = post(
            c,
            "/missions",
            {
                "name": "Queue resilience",
                "template": "compact",
                "idempotency_key": "source",
            },
            201,
        )
        snap = post(
            c,
            f"/scenarios/{m['current_scenario_id']}/snapshots",
            {"expected_state_version": 1},
            201,
        )
        app.state.jobs.limit.acquire()
        try:
            run = post(
                c, "/experiments", spec(snap["snapshot_id"], suite="search"), 202
            )
            for _ in range(100):
                run = c.get("/api/v1/experiments/" + run["experiment_id"]).json()
                if run["cases"][0]["job"]:
                    break
                time.sleep(0.05)
            job = run["cases"][0]["job"]
            assert job and job["job_state"] == "queued"
            stopped = post(c, f"/experiments/{run['experiment_id']}/cancel", {}, 202)
            assert stopped["status"] == "canceled"
            assert stopped["cases"][0]["job"]["job_state"] == "canceled"
            assert job["job_id"] not in app.state.jobs.processes
        finally:
            app.state.jobs.limit.release()
        coordinator = app.state.experiments
        dispatch = coordinator.create_job
        attempts = [0]

        def busy_twice(body):
            attempts[0] += 1
            if attempts[0] <= 2:
                raise AppError(503, "SOLVER_BUSY", "Injected queue pressure")
            return dispatch(body)

        coordinator.create_job = busy_twice
        run = post(
            c,
            "/experiments",
            spec(snap["snapshot_id"], key="queue-pressure", suite="search"),
            202,
        )
        done = finished(c, run["experiment_id"])
        assert attempts[0] >= 4
        assert done["status"] == "completed" and all(
            case["status"] == "completed" and case["job"] for case in done["cases"]
        )
