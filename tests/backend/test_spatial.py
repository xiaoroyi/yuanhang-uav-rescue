from fastapi.testclient import TestClient

from backend.app.main import create_app
from shared.contracts import content_hash


def test_old_snapshot_wire_identity_and_new_zone_template_roundtrip(tmp_path):
    with TestClient(create_app(tmp_path / "runtime")) as client:
        scene = client.post(
            "/api/v1/scenarios/examples", json={"example": "compact"}
        ).json()
        assert "restricted_zones" not in scene
        snap = client.post(
            f"/api/v1/scenarios/{scene['scenario_id']}/snapshots",
            json={"expected_state_version": 1},
        ).json()
        assert snap["content_hash"] == content_hash(scene)
        zone = {
            "zone_id": "ZONE-001",
            "name": "Detached test zone",
            "buffer_m": 25.0,
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [108.0, 23.0],
                        [108.001, 23.0],
                        [108.001, 23.001],
                        [108.0, 23.001],
                        [108.0, 23.0],
                    ]
                ],
            },
        }
        updated = client.put(
            f"/api/v1/scenarios/{scene['scenario_id']}",
            json={
                "expected_state_version": 1,
                "scenario": {**scene, "restricted_zones": [zone]},
            },
        )
        assert updated.status_code == 200, updated.text
        new = updated.json()
        assert new["state_version"] == 2 and new["restricted_zones"] == [zone]
        assert client.get(f"/api/v1/snapshots/{snap['snapshot_id']}").json() == snap
        template = client.get(
            f"/api/v1/scenarios/{scene['scenario_id']}/template?format=xlsx"
        )
        preview = client.post(
            f"/api/v1/scenarios/import-file?scenario_id={scene['scenario_id']}&entity=cargo_items",
            files={
                "file": (
                    "test.xlsx",
                    template.content,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            },
        )
        assert preview.status_code == 200, preview.text
        assert preview.json()["scenario"]["restricted_zones"] == [zone]
        no_fields = client.post("/api/v1/scenarios/import", json=scene)
        assert (
            no_fields.status_code == 201 and "restricted_zones" not in no_fields.json()
        )
