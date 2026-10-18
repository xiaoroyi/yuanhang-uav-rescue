import hashlib
import io
import json
from urllib.parse import parse_qs, urlsplit

from fastapi.testclient import TestClient
import numpy as np
from PIL import Image
import pytest

from backend.app.main import create_app
from backend.app import map_assets
from backend.app.map_assets import RENDER_VERSION, image
from solver.assets import terrain_store


def write_asset(directory, shape=(91, 105), all_missing=False):
    directory.mkdir(parents=True, exist_ok=True)
    values = np.arange(np.prod(shape), dtype=float).reshape(shape)
    values[0, 0] = -9999
    values[-1, -1] = np.nan
    if all_missing:
        values[:] = -9999
    buffer = io.BytesIO()
    np.savez_compressed(
        buffer,
        dem=values,
        longitude=np.linspace(108, 109, shape[1]),
        latitude=np.linspace(24, 23, shape[0]),
        nodata=-9999.0,
        metadata=json.dumps({"name": "test DEM", "source": "test"}),
    )
    digest = hashlib.sha256(buffer.getvalue()).hexdigest()
    (directory / (digest + ".npz")).write_bytes(buffer.getvalue())
    return {"asset_id": "DEM-" + digest[:20], "sha256": digest}, values


def test_surface_is_bounded_hash_bound_preserves_nodata_and_full_grid_statistics(
    tmp_path,
):
    runtime = tmp_path / "runtime"
    ref, values = write_asset(runtime / "assets")
    with TestClient(create_app(runtime)) as client:
        response = client.get("/api/v1/map/surface", params=ref)
        assert response.status_code == 200, response.text
        result = response.json()
        assert (
            result["asset_id"] == ref["asset_id"] and result["sha256"] == ref["sha256"]
        )
        assert len(result["longitude"]) == len(result["latitude"]) == 73
        assert len(result["elevations_m"]) == 73
        assert all(len(row) == 73 for row in result["elevations_m"])
        assert result["longitude"][0] == 108 and result["longitude"][-1] == 109
        assert result["latitude"][0] == 24 and result["latitude"][-1] == 23
        assert result["elevations_m"][0][0] is None
        assert result["elevations_m"][-1][-1] is None
        valid = np.isfinite(values) & (values != -9999)
        assert result["valid_fraction"] == pytest.approx(valid.mean())
        assert result["min_elevation_m"] == values[valid].min()
        assert result["max_elevation_m"] == values[valid].max()
        assert "NoData" in result["notice"]
        model = client.get("/openapi.json").json()["paths"]["/api/v1/map/surface"][
            "get"
        ]
        assert model["responses"]["200"]["content"]["application/json"]["schema"][
            "$ref"
        ].endswith("/TerrainSurface")
        # Exact same reference cannot access another app's asset directory.
    with TestClient(create_app(tmp_path / "other")) as client:
        assert client.get("/api/v1/map/surface", params=ref).status_code == 422


@pytest.mark.parametrize(
    "parameters",
    [
        {},
        {"asset_id": "contest-dem-30m"},
        {"sha256": "a" * 64},
        {"asset_id": "../../escape", "sha256": "a" * 64},
        {"asset_id": "DEM-" + "a" * 20, "sha256": "b" * 64},
        {"asset_id": "contest-dem-30m", "sha256": "A" * 64},
        {"asset_id": "contest-dem-30m", "sha256": "a" * 65},
    ],
)
def test_surface_rejects_missing_invalid_or_mismatched_identity(tmp_path, parameters):
    with TestClient(create_app(tmp_path)) as client:
        response = client.get("/api/v1/map/surface", params=parameters)
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "SCHEMA_INVALID"


def test_surface_rechecks_hash_and_rejects_all_unknown_raster(tmp_path):
    runtime = tmp_path / "runtime"
    ref, _ = write_asset(runtime / "assets", (3, 4))
    missing, _ = write_asset(runtime / "assets", (4, 4), all_missing=True)
    with TestClient(create_app(runtime)) as client:
        assert client.get("/api/v1/map/surface", params=ref).status_code == 200
        path = runtime / "assets" / (ref["sha256"] + ".npz")
        path.write_bytes(path.read_bytes() + b"changed")
        assert client.get("/api/v1/map/surface", params=ref).status_code == 422
        response = client.get("/api/v1/map/surface", params=missing)
        assert (
            response.status_code == 422
            and "有效高程" in response.json()["error"]["message"]
        )


def test_stone_preview_is_render_versioned_and_nodata_transparent(tmp_path):
    ref, _ = write_asset(tmp_path / "assets", (3, 4))
    with terrain_store(tmp_path / "assets"):
        rendered = image(tmp_path, ref["asset_id"], ref["sha256"])
    assert RENDER_VERSION in rendered.parts
    with Image.open(rendered) as preview:
        pixels = np.asarray(preview)
    assert pixels[0, 0, 3] == pixels[-1, -1, 3] == 0
    assert np.all(pixels[:, :, 0] >= pixels[:, :, 1])


def test_http_preview_render_revision_busts_browser_cache_without_changing_dem_identity(
    tmp_path, monkeypatch
):
    """A v0 user's year-long immutable green PNG must not mask the new renderer."""
    runtime = tmp_path / "runtime"
    ref, _ = write_asset(runtime / "assets", (3, 4))
    with TestClient(create_app(runtime)) as client:
        first = client.get("/api/v1/map/terrain", params=ref)
        assert first.status_code == 200, first.text
        first_meta = first.json()
        first_url = first_meta["image_url"]
        parsed = urlsplit(first_url)
        assert parse_qs(parsed.query) == {"v": [map_assets.RENDER_VERSION]}
        assert parsed.path.endswith(f"/{ref['asset_id']}/{ref['sha256']}.png")
        first_image = client.get(first_url)
        assert first_image.status_code == 200
        assert first_image.headers["content-type"] == "image/png"
        assert "immutable" in first_image.headers["cache-control"]
        with Image.open(io.BytesIO(first_image.content)) as preview:
            pixels = np.asarray(preview)
        assert pixels[0, 0, 3] == pixels[-1, -1, 3] == 0

        # A display-only renderer update changes the actual browser cache key,
        # while keeping the exact same solver asset and geospatial binding.
        monkeypatch.setattr(map_assets, "RENDER_VERSION", "display-next-test")
        next_meta = client.get("/api/v1/map/terrain", params=ref).json()
        assert next_meta["image_url"] != first_url
        assert parse_qs(urlsplit(next_meta["image_url"]).query) == {
            "v": ["display-next-test"]
        }
        assert {k: v for k, v in next_meta.items() if k != "image_url"} == {
            k: v for k, v in first_meta.items() if k != "image_url"
        }
        assert next_meta["asset_id"] == ref["asset_id"]
        assert next_meta["sha256"] == ref["sha256"]
        next_image = client.get(next_meta["image_url"])
        assert next_image.status_code == 200
        assert next_image.content == first_image.content
