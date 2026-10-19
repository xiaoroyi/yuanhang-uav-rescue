import time
import json
from pathlib import Path
from fastapi.testclient import TestClient
from backend.app.main import create_app
from shared.contracts import validate_scenario


def test_cases_provenance_idempotency_and_live_assets(tmp_path):
    with TestClient(create_app(tmp_path / "runtime")) as c:
        catalog = c.get("/api/v1/case-library").json()
        assert len(catalog["cases"]) == 4
        assert c.get("/api/v1/asset-overview").json()["mission_count"] == 0
        for case in catalog["cases"]:
            preview = c.get(f"/api/v1/case-library/{case['case_id']}/preview")
            assert preview.status_code == 200, preview.text
            validate_scenario(preview.json())
            body = dict(
                name=case["name"],
                case_id=case["case_id"],
                idempotency_key=case["case_id"],
            )
            first = c.post("/api/v1/missions", json=body)
            assert first.status_code == 201, first.text
            assert first.json()["source_case_id"] == case["case_id"]
            assert (
                c.post("/api/v1/missions", json=body).json()["mission_id"]
                == first.json()["mission_id"]
            )
        assert c.get("/api/v1/asset-overview").json()["mission_count"] == 4
        assert c.get("/api/v1/case-library/missing/preview").status_code == 404
        assert c.get("/api/v1/integrations").json()["real_device_connected"] is False
        config = c.get("/api/v1/integrations/configuration")
        assert "attachment" in config.headers["content-disposition"]
        assert config.json()["external_llm"]["enabled"] is False
        paths = c.get("/openapi.json").json()["paths"]
        assert all(
            e["path"] in paths
            for e in c.get("/api/v1/integrations").json()["endpoints"]
        )


def test_policy_import_export_is_immutable_and_cannot_run_python(tmp_path):
    with TestClient(create_app(tmp_path / "runtime")) as c:
        package = json.loads(
            Path("solver/policies/eoh-seed-v1.json").read_text(encoding="utf-8")
        )
        package["policy_id"] = "review-seed-v1"
        send = lambda p: c.post(
            "/api/v1/heuristic-packages/import",
            files={"file": ("policy.json", json.dumps(p), "application/json")},
        )
        imported = send(package)
        assert imported.status_code == 201, imported.text
        assert imported.json()["origin"] == "rule_initialization"
        assert send(package).status_code == 409
        exported = c.get("/api/v1/heuristic-packages/review-seed-v1/export")
        assert exported.status_code == 200 and exported.json() == package
        for index, expression in enumerate(
            ("__import__('os')", "base_score / 0", "min(base_score)", "9" * 900)
        ):
            bad = {**package, "policy_id": f"bad-{index}", "expression": expression}
            assert send(bad).status_code == 422
        no_record = {**package, "policy_id": "missing-record", "origin": "eoh_offline"}
        assert send(no_record).status_code == 422
        assert len(c.get("/api/v1/heuristic-packages").json()) == 2


def test_engine_subprocess_same_input_and_immutable_plan(tmp_path):
    with TestClient(create_app(tmp_path / "runtime")) as c:
        m = c.post(
            "/api/v1/missions",
            json=dict(
                name="引擎集成验证", case_id="mountain-access-v1", idempotency_key="e"
            ),
        ).json()
        sid = m["current_scenario_id"]
        snap = c.post(
            f"/api/v1/scenarios/{sid}/snapshots", json={"expected_state_version": 1}
        ).json()
        plans = []
        for engine in ("standard", "eoh"):
            body = dict(
                snapshot_id=snap["snapshot_id"],
                engine_type=engine,
                objective_policy="tradeoff_v2",
                time_limit_s=5,
            )
            response = c.post("/api/v1/solve-jobs", json=body)
            assert response.status_code == 202, response.text
            job = response.json()
            for _ in range(400):
                job = c.get("/api/v1/solve-jobs/" + job["job_id"]).json()
                if job["job_state"] not in ("queued", "running"):
                    break
                time.sleep(0.05)
            assert job["job_state"] == "completed" and job["has_validated_plan"], job
            plan = c.get("/api/v1/plans/" + job["plan_id"]).json()
            assert plan["validation"]["status"] == "passed"
            assert plan["engine"]["engine_type"] == engine
            plans.append(plan)
        assert plans[1]["engine"]["ranking_evaluations"] > 0
        assert c.get("/api/v1/plans/" + plans[0]["plan_id"]).json() == plans[0]
        assert (
            c.get(
                "/api/v1/plans/" + plans[0]["plan_id"] + "/comparison",
                params={"other_plan_id": plans[1]["plan_id"]},
            ).status_code
            == 200
        )
        bad = c.post(
            "/api/v1/solve-jobs",
            json=dict(
                snapshot_id=snap["snapshot_id"],
                engine_type="eoh",
                heuristic_policy_id="missing",
            ),
        )
        assert bad.status_code == 422
        bad_hash = c.post(
            "/api/v1/solve-jobs",
            json=dict(
                snapshot_id=snap["snapshot_id"],
                engine_type="eoh",
                heuristic_policy_sha256="0" * 64,
            ),
        )
        assert bad_hash.status_code == 422
        run = c.post(
            "/api/v1/experiments",
            json=dict(
                name="EOH本地搜索对照",
                source_snapshot_id=snap["snapshot_id"],
                suite="search",
                objective="time",
                objective_policy="tradeoff_v2",
                seeds=[7],
                time_limit_s=5,
                idempotency_key="v4-search",
                engine_type="eoh",
            ),
        )
        assert run.status_code == 202, run.text
        campaign = run.json()
        for _ in range(500):
            campaign = c.get("/api/v1/experiments/" + campaign["experiment_id"]).json()
            if campaign["status"] == "completed":
                break
            time.sleep(0.05)
        assert campaign["status"] == "completed", campaign
        assert campaign["heuristic_policy_sha256"] == plans[1]["engine"]["sha256"]
        for case in campaign["cases"]:
            assert case["job"]["has_validated_plan"], case
            assert (
                c.get("/api/v1/plans/" + case["job"]["plan_id"]).json()["engine"][
                    "engine_type"
                ]
                == "eoh"
            )


def test_old_experiment_request_hashes_remain_compatible():
    from backend.app.operation_models import ExperimentRequest
    from backend.app.request_identity import request_hashes
    from shared.contracts import content_hash

    body = ExperimentRequest(
        name="old",
        source_snapshot_id="SNAP-1",
        suite="strategy",
        seeds=[1],
        time_limit_s=5,
        idempotency_key="key",
    )
    legacy = body.model_dump(
        mode="json",
        exclude={"engine_type", "heuristic_policy_id", "heuristic_policy_sha256"},
    )
    assert content_hash(legacy) in request_hashes(body)[1]
