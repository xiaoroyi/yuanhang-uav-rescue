from fastapi.testclient import TestClient

from backend.app.main import create_app


def test_nominal_endpoint_binds_frozen_input_and_reserve_does_not_mutate_policy(
    tmp_path,
):
    with TestClient(create_app(tmp_path / "runtime")) as client:
        s = client.post(
            "/api/v1/scenarios/examples", json={"example": "contest"}
        ).json()
        sid = s["scenario_id"]
        snap = client.post(
            f"/api/v1/scenarios/{sid}/snapshots", json={"expected_state_version": 1}
        ).json()
        url = f"/api/v1/snapshots/{snap['snapshot_id']}/single-site-analysis"
        first = client.get(url)
        assert first.status_code == 200, first.text
        report = first.json()
        assert (
            report["status"] == "complete" and report["metrics"]["sortie_count"] == 18
        )
        assert report["snapshot_content_hash"] == snap["content_hash"]
        stricter = client.get(url, params={"min_return_soc": 0.3})
        assert stricter.status_code == 200, stricter.text
        assert stricter.json()["metrics"]["sortie_count"] == 20
        assert stricter.json()["analysis_input_hash"] != report["analysis_input_hash"]
        assert client.get(f"/api/v1/scenarios/{sid}").json() == s
        s["cargo_items"][0]["mass_kg"] += 1.0
        saved = client.put(
            f"/api/v1/scenarios/{sid}",
            json={"expected_state_version": 1, "scenario": s},
        )
        assert saved.status_code == 200, saved.text
        second = client.get(url).json()
        report.pop("runtime_s")
        second.pop("runtime_s")
        assert second == report
        assert client.get(f"/api/v1/snapshots/{snap['snapshot_id']}").json() == snap
        assert client.get(f"/api/v1/scenarios/{sid}/plans").json() == []
        assert client.get(f"/api/v1/scenarios/{sid}/solve-jobs").json() == []
        assert client.get(url, params={"min_return_soc": 1.1}).status_code == 422
        assert (
            client.get(
                "/api/v1/snapshots/DOES-NOT-EXIST/single-site-analysis"
            ).status_code
            == 404
        )
