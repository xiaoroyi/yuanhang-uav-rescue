import copy
from pathlib import Path
import time

from fastapi.testclient import TestClient
import numpy as np
import pytest

from backend.app.flight_profiles import FlightProfile, flight_profile, ground_sample
from backend.app.main import create_app
from shared.contracts import content_hash
from solver.assets import terrain_data
from solver.errors import InputNotReady
from solver.physics import leg, leg_values, parameters


def real_plan(client, scene):
    snap = client.post(
        f"/api/v1/scenarios/{scene['scenario_id']}/snapshots",
        json={"expected_state_version": scene["state_version"]},
    ).json()
    response = client.post(
        "/api/v1/solve-jobs",
        json={"snapshot_id": snap["snapshot_id"], "time_limit_s": 8},
    )
    assert response.status_code == 202, response.text
    jid = response.json()["job_id"]
    for _ in range(300):
        job = client.get("/api/v1/solve-jobs/" + jid).json()
        if job["job_state"] not in ("queued", "running"):
            break
        time.sleep(0.05)
    assert job["job_state"] == "completed" and job["has_validated_plan"], job
    return client.get("/api/v1/plans/" + job["plan_id"]).json(), snap


def test_real_profile_reuses_physics_energy_terrain_and_original_snapshot(tmp_path):
    with TestClient(create_app(tmp_path / "runtime")) as client:
        scene = client.post(
            "/api/v1/scenarios/examples", json={"example": "compact"}
        ).json()
        plan, snap = real_plan(client, scene)
        sortie = plan["sorties"][0]
        url = f"/api/v1/plans/{plan['plan_id']}/flight-profile"
        response = client.get(url, params={"sortie_id": sortie["sortie_id"]})
        assert response.status_code == 200, response.text
        profile = response.json()
        assert profile["snapshot_id"] == snap["snapshot_id"]
        assert profile["terrain_sha256"] == scene["terrain"]["sha256"]
        assert profile["vertical_datum"] == scene["terrain"]["vertical_datum"]
        assert profile["modeled_energy_kwh"] == pytest.approx(
            sortie["energy_kwh"], abs=1e-10
        )
        assert profile["horizontal_energy_kwh"] + profile[
            "climb_energy_kwh"
        ] == pytest.approx(profile["modeled_energy_kwh"])
        assert sum(len(row["samples"]) for row in profile["legs"]) <= 240
        typ = next(
            t for t in scene["drone_types"] if t["type_id"] == profile["drone_type_id"]
        )
        terrain = terrain_data(scene["terrain"]["asset_id"], scene["terrain"]["sha256"])
        distance = 0.0
        for row in profile["legs"]:
            geometry = leg(scene, typ, row["from_id"], row["to_id"])
            seconds, energy = leg_values(typ, geometry, row["payload_kg"])
            assert row["distance_m"] == pytest.approx(geometry.distance_m)
            assert row["start_distance_m"] == pytest.approx(distance)
            assert row["flight_time_s"] == pytest.approx(seconds)
            assert row["energy_kwh"] == pytest.approx(energy)
            assert row["cruise_elevation_m"] == geometry.cruise_m
            assert row["clearance_required_m"] == parameters(typ).get(
                "clearance_m", 50.0
            )
            assert (
                row["terrain_checked"] is True
                and row["cruise_clearance_margin_m"] >= -1e-8
            )
            assert row["samples"][0]["distance_m"] == pytest.approx(distance)
            assert row["samples"][-1]["distance_m"] == pytest.approx(
                row["end_distance_m"]
            )
            for sample in row["samples"]:
                assert sample["ground_elevation_m"] == ground_sample(
                    terrain, (sample["longitude"], sample["latitude"])
                )
            distance += geometry.distance_m
        assert profile["total_distance_m"] == pytest.approx(distance)
        assert profile["legs"][-1]["payload_kg"] == pytest.approx(0.0)
        # A real live scenario edit must never alter a saved Plan's diagnostics.
        scene["drone_types"][0]["energy_model"]["parameters"]["clearance_m"] = 250.0
        changed = client.put(
            f"/api/v1/scenarios/{scene['scenario_id']}",
            json={"expected_state_version": 1, "scenario": scene},
        )
        assert changed.status_code == 200, changed.text
        assert (
            client.get(url, params={"sortie_id": sortie["sortie_id"]}).json() == profile
        )
        assert client.get(f"/api/v1/plans/{plan['plan_id']}").json() == plan
        assert client.get(f"/api/v1/snapshots/{snap['snapshot_id']}").json() == snap
        assert client.get(url).status_code == 422
        assert client.get(url, params={"sortie_id": "unknown"}).status_code == 404
        assert client.get(url, params={"sortie_id": "../escape"}).status_code == 422
        assert (
            client.get(
                "/api/v1/plans/unknown/flight-profile",
                params={"sortie_id": sortie["sortie_id"]},
            ).status_code
            == 404
        )
        # Missing terrain is explicit null data, never a fake flat DEM.
        no_dem_snap = copy.deepcopy(snap)
        no_dem_snap["scenario"]["terrain"] = {"status": "not_provided"}
        no_dem_snap["content_hash"] = content_hash(no_dem_snap["scenario"])
        view = flight_profile(no_dem_snap, plan, sortie["sortie_id"])
        FlightProfile.model_validate(view)
        assert (
            view["terrain_asset_id"]
            is view["terrain_sha256"]
            is view["vertical_datum"]
            is None
        )
        assert all(
            not row["terrain_checked"]
            and row["terrain_maximum_m"] is None
            and row["cruise_clearance_margin_m"] is None
            for row in view["legs"]
        )
        assert all(
            point["ground_elevation_m"] is None
            for row in view["legs"]
            for point in row["samples"]
        )
        broken_snap = copy.deepcopy(snap)
        broken_snap["scenario"]["name"] = "changed without updating hash"
        with pytest.raises(InputNotReady, match="快照"):
            flight_profile(broken_snap, plan, sortie["sortie_id"])
        broken_plan = copy.deepcopy(plan)
        broken_plan["sorties"][0]["route_geometry"]["coordinates"][0][0] += 0.01
        with pytest.raises(InputNotReady, match="历史方案"):
            flight_profile(snap, broken_plan, sortie["sortie_id"])


def test_profile_ground_sampling_preserves_nodata_nan_and_out_of_bounds():
    grid = np.array([[100.0, -9999.0], [np.nan, 200.0]])
    terrain = grid, np.array([108.0, 109.0]), np.array([24.0, 23.0]), -9999.0
    assert ground_sample(terrain, (108.0, 24.0)) == 100.0
    assert ground_sample(terrain, (109.0, 23.0)) == 200.0
    assert ground_sample(terrain, (109.0, 24.0)) is None
    assert ground_sample(terrain, (108.0, 23.0)) is None
    assert ground_sample(terrain, (106.0, 23.0)) is None
    assert ground_sample(None, (108.0, 24.0)) is None


def test_profile_uses_private_uploaded_asset_and_rejects_changed_bound_hash(tmp_path):
    runtime = tmp_path / "runtime"
    source = next(
        (Path(__file__).resolve().parents[2] / "references/modeling/data/terrain").glob(
            "*.tif"
        )
    ).read_bytes()
    with TestClient(create_app(runtime)) as client:
        scene = client.post(
            "/api/v1/scenarios/examples", json={"example": "compact"}
        ).json()
        response = client.post(
            "/api/v1/terrain-assets",
            files={"file": ("local-copy.tif", source, "image/tiff")},
            data={"vertical_datum": "contest_provided_elevation_reference"},
        )
        assert response.status_code == 201, response.text
        asset = response.json()
        assigned = client.post(
            f"/api/v1/scenarios/{scene['scenario_id']}/terrain",
            json={
                "expected_state_version": 1,
                "asset_id": asset["asset_id"],
                "sha256": asset["sha256"],
                "update_dem_elevations": False,
            },
        )
        assert assigned.status_code == 200, assigned.text
        plan, _ = real_plan(client, assigned.json())
        url = f"/api/v1/plans/{plan['plan_id']}/flight-profile"
        query = {"sortie_id": plan["sorties"][0]["sortie_id"]}
        profile = client.get(url, params=query)
        assert profile.status_code == 200, profile.text
        assert profile.json()["terrain_asset_id"] == asset["asset_id"]
        assert profile.json()["terrain_sha256"] == asset["sha256"]
        assert all(
            sample["ground_elevation_m"] is not None
            for row in profile.json()["legs"]
            for sample in row["samples"]
        )
        # No cross-instance fallback to the archived contest DEM after a private asset changes.
        path = runtime / "assets" / (asset["sha256"] + ".npz")
        path.write_bytes(path.read_bytes() + b"corrupted only in this temporary test")
        refused = client.get(url, params=query)
        assert (
            refused.status_code == 422 and "hash" in refused.json()["error"]["message"]
        )
        assert client.get(f"/api/v1/plans/{plan['plan_id']}").json() == plan
