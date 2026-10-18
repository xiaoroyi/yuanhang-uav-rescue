import copy

from fastapi.testclient import TestClient

from backend.app.main import create_app
from shared.contracts import content_hash


def test_version_history_returns_exact_immutable_inputs_descending_without_invented_dates(
    tmp_path,
):
    with TestClient(create_app(tmp_path / "runtime")) as client:
        original = client.post(
            "/api/v1/scenarios/examples", json={"example": "compact"}
        ).json()
        sid = original["scenario_id"]
        before_snap = client.post(
            f"/api/v1/scenarios/{sid}/snapshots", json={"expected_state_version": 1}
        ).json()
        changed = copy.deepcopy(original)
        changed["name"] = "revision two"
        changed["cargo_items"][0]["mass_kg"] += 0.25
        response = client.put(
            f"/api/v1/scenarios/{sid}",
            json={"expected_state_version": 1, "scenario": changed},
        )
        assert response.status_code == 200, response.text
        revised = response.json()
        assert revised["state_version"] == 2
        url = f"/api/v1/scenarios/{sid}/versions"
        versions = client.get(url)
        assert versions.status_code == 200
        history = versions.json()
        assert [row["state_version"] for row in history] == [2, 1]
        for row, expected in zip(history, [revised, original]):
            assert row["scenario_id"] == sid and row["name"] == expected["name"]
            assert row["created_at"] is None
            assert row["content_hash"] == content_hash(expected)
            assert row["site_count"] == len(expected["sites"])
            assert row["cargo_count"] == len(expected["cargo_items"])
            assert row["drone_count"] == len(expected["drones"])
            assert row["battery_count"] == len(expected["batteries"])
            assert client.get(f"{url}/{row['state_version']}").json() == expected
        # Read-only downloads/listing never create another revision, nor rewrite a snapshot.
        assert client.get(f"/api/v1/scenarios/{sid}").json() == revised
        assert (
            client.get(f"/api/v1/snapshots/{before_snap['snapshot_id']}").json()
            == before_snap
        )
        assert client.get(url).json() == history
        assert client.get(f"{url}/3").status_code == 404
        assert client.get(f"{url}/0").status_code == 422
        assert client.get(f"{url}/bad").status_code == 422
        assert client.get("/api/v1/scenarios/unknown/versions").status_code == 404
        assert client.get("/api/v1/scenarios/unknown/versions/1").status_code == 404
        paths = client.get("/openapi.json").json()["paths"]
        assert set(paths["/api/v1/scenarios/{scenario_id}/versions"]) == {"get"}
        assert set(paths["/api/v1/scenarios/{scenario_id}/versions/{version}"]) == {
            "get"
        }
