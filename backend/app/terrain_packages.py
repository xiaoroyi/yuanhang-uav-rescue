"""Portable terrain packages preserve the exact prepared hash across computers."""

import hashlib
import io
import json
import math
from pathlib import Path
import re
import zipfile

import numpy as np

from backend.app.terrain_assets import (
    describe,
    prepare,
    put_immutable,
    MAX_PIXELS,
    NODATA,
    put_catalog_entry,
)
from solver.assets import terrain_info, terrain_token, terrain_store

FORMAT = "yuanhang-dem-v1"
MEMBERS = {"manifest.json", "terrain.npz", "source.tif"}
ARRAYS = {"dem.npy", "longitude.npy", "latitude.npy", "nodata.npy", "metadata.npy"}


def export_package(directory: Path, asset_id, digest):
    if not asset_id.startswith("DEM-"):
        raise ValueError("原题只读DEM已随仓库提供，无需另行打包。")
    with terrain_store(directory):
        info = terrain_info(asset_id, digest)
        packed = Path(terrain_token(asset_id, digest)[0]).read_bytes()
        source_hash = info["source_sha256"]
        if not re.fullmatch("[a-f0-9]{64}", source_hash):
            raise ValueError("来源hash无效。")
        source = (directory / "sources" / (source_hash + ".tif")).read_bytes()
        if hashlib.sha256(source).hexdigest() != source_hash:
            raise ValueError("来源文件hash不一致。")
    manifest = {
        "format": FORMAT,
        "asset_id": asset_id,
        "sha256": digest,
        "source_sha256": source_hash,
    }
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", json.dumps(manifest, sort_keys=True))
        archive.writestr("terrain.npz", packed)
        archive.writestr("source.tif", source)
    return output.getvalue()


def validate_array_headers(packed):
    with zipfile.ZipFile(io.BytesIO(packed)) as archive:
        entries = archive.infolist()
        if (
            len(entries) != 5
            or set(archive.namelist()) != ARRAYS
            or sum(e.file_size for e in entries) > 20 * 1024 * 1024
        ):
            raise ValueError("准备栅格包含不支持的数组或解压规模过大。")
        for entry in entries:
            with archive.open(entry) as data:
                version = np.lib.format.read_magic(data)
                reader = {
                    (1, 0): np.lib.format.read_array_header_1_0,
                    (2, 0): np.lib.format.read_array_header_2_0,
                }.get(version)
                if reader is None:
                    raise ValueError("不支持的NPY格式版本。")
                shape, _, dtype = reader(data)
                count = math.prod(shape)
                size = count * dtype.itemsize
                if (
                    len(shape) > 2
                    or any(v < 0 for v in shape)
                    or count > MAX_PIXELS
                    or size > 16 * 1024 * 1024
                    or dtype.hasobject
                    or size + data.tell() > entry.file_size
                ):
                    raise ValueError("准备栅格数组头超出限制。")
                if entry.filename == "metadata.npy":
                    if shape or dtype.kind not in "US" or size > 65536:
                        raise ValueError("栅格元数据无效。")
                elif dtype.kind not in "ifu" or dtype.itemsize > 8:
                    raise ValueError("DEM只接受有界实数数组。")


def import_package(directory: Path, data: bytes):
    if len(data) > 40 * 1024 * 1024:
        raise ValueError("完整DEM资产包不能超过40MiB。")
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            entries = archive.infolist()
            if (
                len(entries) != 3
                or set(archive.namelist()) != MEMBERS
                or any(e.flag_bits & 1 for e in entries)
            ):
                raise ValueError(
                    "请输入援航导出的完整DEM资产包，不能含额外路径或加密项。"
                )
            limits = {
                "manifest.json": 65536,
                "terrain.npz": 20 * 1024 * 1024,
                "source.tif": 16 * 1024 * 1024,
            }
            if any(e.file_size > limits[e.filename] for e in entries):
                raise ValueError("资产包解压规模超出限制。")
            manifest = json.loads(archive.read("manifest.json"))
            packed = archive.read("terrain.npz")
            source = archive.read("source.tif")
        if (
            not isinstance(manifest, dict)
            or manifest.get("format") != FORMAT
            or any(
                not isinstance(manifest.get(k), str)
                or not re.fullmatch("[a-f0-9]{64}", manifest[k])
                for k in ["sha256", "source_sha256"]
            )
        ):
            raise ValueError("资产包版本或hash字段无效。")
        digest, source_hash = manifest["sha256"], manifest["source_sha256"]
        asset_id = "DEM-" + digest[:20]
        if (
            manifest.get("asset_id") != asset_id
            or hashlib.sha256(packed).hexdigest() != digest
            or hashlib.sha256(source).hexdigest() != source_hash
        ):
            raise ValueError("资产包内容hash与清单不一致。")
        validate_array_headers(packed)
        with np.load(io.BytesIO(packed), allow_pickle=False) as arrays:
            info = json.loads(str(arrays["metadata"].item()))
            if not isinstance(info, dict) or not all(
                isinstance(info.get(k), str) for k in ["name", "vertical_datum"]
            ):
                raise ValueError("资产包缺少名称或垂直基准。")
            z, lon, lat, expected_info, _ = prepare(
                source, info["name"], info["vertical_datum"]
            )
            if info != expected_info or float(arrays["nodata"].item()) != NODATA:
                raise ValueError("准备栅格元数据与来源文件不一致，请使用相同处理版本。")
            for key, expected in [("dem", z), ("longitude", lon), ("latitude", lat)]:
                actual = arrays[key]
                if (
                    actual.shape != expected.shape
                    or not np.all(np.isfinite(actual))
                    or not np.allclose(actual, expected, rtol=1e-11, atol=1e-6)
                    or not np.array_equal(actual == NODATA, expected == NODATA)
                ):
                    raise ValueError(
                        "准备栅格与源文件重算不一致，请重新准备并新建场景版本。"
                    )
        # No files are written until the entire package and source recalculation pass.
        put_immutable(directory / (digest + ".npz"), packed)
        put_immutable(directory / "sources" / (source_hash + ".tif"), source)
        public = {**info, "asset_id": asset_id, "sha256": digest}
        put_catalog_entry(directory / (digest + ".json"), public)
        with terrain_store(directory):
            return describe(asset_id, digest)
    except (
        zipfile.BadZipFile,
        KeyError,
        TypeError,
        UnicodeError,
        RuntimeError,
        NotImplementedError,
    ) as exc:
        raise ValueError("完整DEM资产包损坏或字段不完整。") from exc
