"""Real paired workers use one immutable residual and never apply benchmark outcomes."""

import base64
import copy
import json
from fastapi.testclient import TestClient
from backend.app.main import create_app
from backend.app.storage import (
    OperationRecordRow,
    ExecutionRow,
    PlanRow,
    SnapshotRow,
    JobRow,
)
from backend.app.repair_evidence import comparison_input_hash
from shared.contracts import content_hash
from solver.public_api import validate
from test_execution_v2 import setup, post, act
from test_dependency_repair_v2 import change
from test_experiments_v2 import finished


def prepare(c):
    _, s, p, e = setup(c)
    e = act(c, e, "advance", target_time_s=1)
    post(
        c,
        f"/executions/{e['execution_id']}/events",
        {
            "event_id": "bench-exit",
            "expected_revision": e["revision"],
            "event_type": "drone.unavailable",
            "object_id": s["drones"][-1]["drone_id"],
            "reason": "Real future availability event for paired worker comparison",
        },
        201,
    )
    e = c.get("/api/v1/executions/" + e["execution_id"]).json()
    repair = change(c, e, "reference-for-method-comparison", budget=5)
    return p, e, repair


def spec(repair, key="pair"):
    return {
        "name": "Dependency and full paired residual",
        "suite": "repair",
        "source_snapshot_id": repair["job"]["snapshot_id"],
        "repair_reference_id": repair["repair_reference_id"],
        "objective_policy": "tradeoff_v2",
        "objective": "time",
        "seeds": [7, 11],
        "time_limit_s": 8,
        "idempotency_key": key,
    }


def test_dynamic_campaign_pairs_constraints_and_frozen_evidence_without_changing_execution(
    tmp_path,
):
    app = create_app(tmp_path / "runtime")
    with TestClient(app) as c:
        p, e, repair = prepare(c)
        with app.state.database.session() as session:
            original = copy.deepcopy(
                session.get(ExecutionRow, e["execution_id"]).content
            )
            old_plan = copy.deepcopy(session.get(PlanRow, p["plan_id"]).content)
            original_snap = copy.deepcopy(
                session.get(SnapshotRow, repair["job"]["snapshot_id"]).content
            )
        body = spec(repair)
        assert (
            c.post(
                "/api/v1/experiments",
                json={**body, "source_snapshot_id": p["snapshot_id"]},
            ).status_code
            == 409
        )
        assert (
            c.post("/api/v1/experiments", json={**body, "suite": "search"}).status_code
            == 422
        )
        run = post(c, "/experiments", body, 202)
        assert (
            post(c, "/experiments", body, 202)["experiment_id"] == run["experiment_id"]
        )
        assert run["repair_context"]["committed_quantity"] == len(
            repair["committed_cargo_ids"]
        )
        assert run["repair_context"]["facts_cursor"] == e["facts_cursor"]
        done = finished(c, run["experiment_id"])
        assert len(done["cases"]) == 4
        assert {x["method"] for x in done["cases"]} == {"dependency", "full_recompute"}
        assert all(x["job"]["has_validated_plan"] for x in done["cases"]), done
        with app.state.database.session() as session:
            analysis = copy.deepcopy(
                session.get(SnapshotRow, run["snapshot_id"]).content
            )
            assert (
                comparison_input_hash(analysis["scenario"])
                == comparison_input_hash(original_snap["scenario"])
                == run["repair_context"]["comparison_input_sha256"]
            )
            assert session.get(ExecutionRow, e["execution_id"]).content == original
            assert session.get(PlanRow, p["plan_id"]).content == old_plan
            assert (
                session.get(SnapshotRow, repair["job"]["snapshot_id"]).content
                == original_snap
            )
            refs = []
            for case in done["cases"]:
                job = session.get(JobRow, case["job"]["job_id"])
                assert (
                    job.options["seed"] == case["seed"]
                    and job.options["time_limit_s"] == 8
                )
                candidate = session.get(PlanRow, case["job"]["plan_id"]).content
                assert candidate["snapshot_id"] == run["snapshot_id"]
                assert validate(analysis, candidate)["status"] == "passed"
                assert case["repair_difference"] is not None
                codes = {d["code"] for d in job.outcome["diagnostics"]}
                expected = (
                    "dependency_local"
                    if "REPAIR_LOCAL_APPLIED" in codes
                    else "full_recompute"
                )
                assert case["calculation_method"] == expected
                assert ("REPAIR_LOCAL_APPLIED" in codes) != (
                    "REPAIR_FULL_RECOMPUTE" in codes
                )
                if case["method"] == "full_recompute":
                    assert expected == "full_recompute"
                assert not set(repair["committed_cargo_ids"]).intersection(
                    cid for r in candidate["sorties"] for cid in r["cargo_ids"]
                )
                ref = copy.deepcopy(
                    session.get(
                        OperationRecordRow,
                        ("solver.repair.reference", case["repair_reference_id"]),
                    ).content
                )
                ref.pop("repair_policy")
                refs.append(ref)
            assert all(ref == refs[0] for ref in refs)
        bundle = c.get("/api/v1/experiments/" + run["experiment_id"] + "/export").json()
        assert len({(d["kind"], d["document_id"]) for d in bundle["documents"]}) == len(
            bundle["documents"]
        )
        evidence = json.loads(
            next(
                d["payload_json"]
                for d in bundle["documents"]
                if d["kind"] == "repair_evidence"
            )
        )
        assert (
            evidence["events"][0]["event_id"] == "bench-exit"
            and evidence["event_fingerprint"] == repair["event_fingerprint"]
        )
        assert evidence["facts"] == e["facts"]
        assert len(bundle["artifacts"]) == 16 and not bundle["missing_artifacts"]
        for artifact in bundle["artifacts"]:
            if artifact["name"] == "input.json":
                payload = json.loads(base64.b64decode(artifact["content_base64"]))
                assert payload["snapshot"]["snapshot_id"] == run["snapshot_id"]
                assert (
                    payload["repair_reference"]["committed_cargo_ids"]
                    == repair["committed_cargo_ids"]
                )
        assert bundle["content_sha256"] == content_hash(
            {k: v for k, v in bundle.items() if k != "content_sha256"}
        )


def test_old_reference_without_captured_events_is_explicitly_rejected_without_fabricating_history(
    tmp_path,
):
    app = create_app(tmp_path / "runtime")
    with TestClient(app) as c:
        _, _, repair = prepare(c)
        with app.state.database.session(immediate=True) as session:
            record = session.get(
                OperationRecordRow,
                ("solver.repair.evidence", repair["repair_reference_id"]),
            )
            session.delete(
                record
            )  # Isolated test fixture simulates a pre-RFC028 database.
        response = c.post("/api/v1/experiments", json=spec(repair))
        assert (
            response.status_code == 422
            and response.json()["error"]["code"] == "EVIDENCE_NOT_CAPTURED"
        )
