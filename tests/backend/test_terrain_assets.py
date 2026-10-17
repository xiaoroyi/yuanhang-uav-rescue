import hashlib
from pathlib import Path
import time

from fastapi.testclient import TestClient
import numpy as np
import pytest
from rasterio.io import MemoryFile
from rasterio.transform import from_origin

from backend.app.main import create_app
from backend.app.terrain_assets import register
from solver.assets import terrain_data, terrain_store
from solver.errors import InputNotReady
from solver.physics import terrain_maximum
from shared.contracts import content_hash

ROOT = Path(__file__).resolve().parents[2]


def tiff(crs="EPSG:4326", nodata=False):
    grid = np.full((30, 30), 100.0, dtype="float32")
    if nodata:
        grid[12:16, 12:16] = -9999.0
    transform = (
        from_origin(108.0, 23.02, 0.001, 0.001)
        if crs != "EPSG:3857"
        else from_origin(12000000, 2635000, 30, 30)
    )
    with MemoryFile() as mem:
        with mem.open(
            driver="GTiff",
            width=30,
            height=30,
            count=1,
            dtype="float32",
            crs=crs,
            transform=transform,
            nodata=-9999.0,
        ) as ds:
            ds.write(grid, 1)
        return mem.read()


def test_real_original_geotiff_upload_bind_worker_confirm_and_map(tmp_path):
    with TestClient(create_app(tmp_path / "runtime")) as client:
        source = next(
            (ROOT / "references/modeling/data/terrain").glob("*.tif")
        ).read_bytes()
        scene = client.post(
            "/api/v1/scenarios/examples", json={"example": "compact"}
        ).json()
        old_snap = client.post(
            f"/api/v1/scenarios/{scene['scenario_id']}/snapshots",
            json={"expected_state_version": 1},
        ).json()
        uploaded = client.post(
            "/api/v1/terrain-assets",
            files={"file": ("contest-copy.tif", source, "image/tiff")},
            data={"vertical_datum": "contest_provided_elevation_reference"},
        )
        assert uploaded.status_code == 201, uploaded.text
        asset = uploaded.json()
        assert asset["source_sha256"] == hashlib.sha256(source).hexdigest()
        assert asset["asset_id"].startswith("DEM-") and asset["valid_fraction"] > 0
        assert len(client.get("/api/v1/terrain-assets").json()) == 2
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
        new = assigned.json()
        assert new["state_version"] == 2 and new["terrain"] == asset["terrain"]
        assert new["data_origin"] == "user_input"
        assert (
            client.get(f"/api/v1/snapshots/{old_snap['snapshot_id']}").json()
            == old_snap
        )
        snap = client.post(
            f"/api/v1/scenarios/{scene['scenario_id']}/snapshots",
            json={"expected_state_version": 2},
        ).json()
        assert snap["content_hash"] == content_hash(new)
        response = client.post(
            "/api/v1/solve-jobs",
            json={"snapshot_id": snap["snapshot_id"], "time_limit_s": 10},
        )
        assert response.status_code == 202, response.text
        job = response.json()
        for _ in range(220):
            job = client.get(f"/api/v1/solve-jobs/{job['job_id']}").json()
            if job["job_state"] not in ["queued", "running"]:
                break
            time.sleep(0.05)
        assert job["job_state"] == "completed" and job["has_validated_plan"], job
        plan = client.get(f"/api/v1/plans/{job['plan_id']}").json()
        assert plan["validation"]["status"] == "passed"
        confirmed = client.post(
            f"/api/v1/plans/{plan['plan_id']}/confirm",
            json={"expected_state_version": 2, "idempotency_key": "CONFIRM-TERRAIN"},
        )
        assert confirmed.status_code == 200, confirmed.text
        meta = client.get(
            "/api/v1/map/terrain",
            params={"asset_id": asset["asset_id"], "sha256": asset["sha256"]},
        ).json()
        png = client.get(meta["image_url"])
        assert png.status_code == 200 and png.content.startswith(b"\x89PNG")
        download = client.get(
            f"/api/v1/terrain-assets/{asset['asset_id']}/source",
            params={"sha256": asset["sha256"]},
        )
        assert download.status_code == 200 and download.content == source


@pytest.mark.parametrize("crs", ["EPSG:4326", "EPSG:3857"])
def test_nodata_survives_preparation_and_registry_context_isolated(tmp_path, crs):
    asset = register(tmp_path, tiff(crs, True), "test.tif", "test_meter_datum")
    with terrain_store(tmp_path):
        z, lon, lat, nodata = terrain_data(asset["asset_id"], asset["sha256"])
        assert np.any(z == nodata) and 0 < asset["valid_fraction"] < 1
        r, c = np.argwhere(z == nodata)[0]
        point = (float(lon[c]), float(lat[r]))
        with pytest.raises(InputNotReady):
            terrain_maximum(asset["asset_id"], asset["sha256"], point, point)
    with terrain_store(tmp_path / "another-instance"):
        with pytest.raises(InputNotReady):
            terrain_data(asset["asset_id"], asset["sha256"])


def test_registry_hash_is_rechecked_after_file_changes(tmp_path):
    asset = register(tmp_path, tiff(), "test.tif", "test_meter_datum")
    with terrain_store(tmp_path):
        terrain_data(asset["asset_id"], asset["sha256"])
        path = tmp_path / (asset["sha256"] + ".npz")
        path.write_bytes(path.read_bytes() + b"corruption")
        with pytest.raises(InputNotReady, match="hash"):
            terrain_data(asset["asset_id"], asset["sha256"])


def test_invalid_raster_and_missing_crs_are_structured_and_do_not_bind_scene(tmp_path):
    with TestClient(create_app(tmp_path / "runtime")) as client:
        for data in [b"<VRTDataset/>\n", tiff(None)]:
            response = client.post(
                "/api/v1/terrain-assets",
                files={"file": ("bad.tif", data, "image/tiff")},
                data={"vertical_datum": "test_meter_datum"},
            )
            assert response.status_code == 422, response.text
        assert len(client.get("/api/v1/terrain-assets").json()) == 1
        missing = client.get(
            "/api/v1/map/terrain",
            params={"asset_id": "../../outside", "sha256": "a" * 64},
        )
        assert missing.status_code == 422
