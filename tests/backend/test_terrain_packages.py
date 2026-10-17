import hashlib
import io
import json
import zipfile

from fastapi.testclient import TestClient
import numpy as np
import pytest

from backend.app.main import create_app
from backend.app.terrain_assets import register
from backend.app.terrain_packages import export_package, import_package
from test_terrain_assets import tiff


def test_portable_package_preserves_exact_hash_in_second_instance(tmp_path):
    source = tiff(nodata=True)
    first = tmp_path / "one/assets"
    asset = register(first, source, "shared.tif", "test_meter_datum")
    package = export_package(first, asset["asset_id"], asset["sha256"])
    sidecar = first / (asset["sha256"] + ".json")
    metadata = json.loads(sidecar.read_text(encoding="utf-8"))
    sidecar.write_text(
        json.dumps(dict(reversed(list(metadata.items())))), encoding="utf-8"
    )
    assert import_package(first, package) == asset
    with TestClient(create_app(tmp_path / "two")) as client:
        response = client.post(
            "/api/v1/terrain-assets/import-package",
            files={"file": ("shared.zip", package, "application/zip")},
        )
        assert response.status_code == 201, response.text
        assert response.json() == asset
        repeated = client.post(
            "/api/v1/terrain-assets/import-package",
            files={"file": ("shared.zip", package, "application/zip")},
        )
        assert repeated.status_code == 201 and repeated.json() == asset
        copied = client.get(
            f"/api/v1/terrain-assets/{asset['asset_id']}/source",
            params={"sha256": asset["sha256"]},
        )
        assert copied.content == source
        exported = client.get(
            f"/api/v1/terrain-assets/{asset['asset_id']}/package",
            params={"sha256": asset["sha256"]},
        )
        assert exported.status_code == 200
        with zipfile.ZipFile(io.BytesIO(exported.content)) as archive:
            assert (
                hashlib.sha256(archive.read("terrain.npz")).hexdigest()
                == asset["sha256"]
            )


@pytest.mark.parametrize("broken", ["hash", "extra_path", "large_array_header"])
def test_invalid_package_is_rejected_before_any_registry_write(tmp_path, broken):
    first = tmp_path / "one/assets"
    asset = register(first, tiff(), "shared.tif", "test_meter_datum")
    package = export_package(first, asset["asset_id"], asset["sha256"])
    with zipfile.ZipFile(io.BytesIO(package)) as archive:
        members = {name: archive.read(name) for name in archive.namelist()}
    if broken == "hash":
        members["source.tif"] += b"corruption"
    elif broken == "extra_path":
        members["../escape.txt"] = b"not allowed"
    else:
        with zipfile.ZipFile(io.BytesIO(members["terrain.npz"])) as archive:
            arrays = {name: archive.read(name) for name in archive.namelist()}
        header = io.BytesIO()
        np.lib.format.write_array_header_1_0(
            header,
            {
                "descr": "<f8",
                "fortran_order": False,
                "shape": (100_000_000, 100_000_000),
            },
        )
        arrays["dem.npy"] = header.getvalue()
        bad = io.BytesIO()
        with zipfile.ZipFile(bad, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for key, value in arrays.items():
                archive.writestr(key, value)
        packed = bad.getvalue()
        members["terrain.npz"] = packed
        manifest = json.loads(members["manifest.json"])
        manifest["sha256"] = hashlib.sha256(packed).hexdigest()
        manifest["asset_id"] = "DEM-" + manifest["sha256"][:20]
        members["manifest.json"] = json.dumps(manifest).encode()
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for key, value in members.items():
            archive.writestr(key, value)
    with TestClient(create_app(tmp_path / "two")) as client:
        response = client.post(
            "/api/v1/terrain-assets/import-package",
            files={"file": ("bad.zip", output.getvalue(), "application/zip")},
        )
        assert response.status_code == 422, response.text
        assert not (tmp_path / "two/assets").exists()
        assert not (tmp_path / "escape.txt").exists()
