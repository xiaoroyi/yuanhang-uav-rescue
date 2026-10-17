"""Bounded GeoTIFF ingestion into an immutable local terrain registry."""

from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import uuid

import numpy as np
from pydantic import BaseModel, ConfigDict
from rasterio.io import MemoryFile
from rasterio.warp import calculate_default_transform, reproject, Resampling

from backend.app.generated.domain import Terrain
from solver.assets import terrain_data, terrain_info, terrain_store

MAX_PIXELS = 2_000_000
NODATA = -1e30


class TerrainAsset(BaseModel):
    model_config = ConfigDict(extra="forbid")
    asset_id: str
    name: str
    sha256: str
    terrain: Terrain
    bounds: tuple[float, float, float, float]
    dimensions: tuple[int, int]
    valid_fraction: float
    source_sha256: str | None
    source_crs: str
    processing: list[str]


def put_immutable(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError("同内容ID下已有不同文件，已阻止覆盖。")
        return
    temp = path.with_name(uuid.uuid4().hex + ".tmp")
    try:
        temp.write_bytes(data)
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)


def register(directory: Path, data: bytes, name: str, datum: str):
    if len(data) > 16 * 1024 * 1024:
        raise ValueError("DEM文件不能超过16MiB。")
    if data[:4] not in [b"II*\x00", b"MM\x00*", b"II+\x00", b"MM\x00+"]:
        raise ValueError("请输入真正的GeoTIFF文件，不接受VRT、URL或本机路径。")
    datum = datum.strip()
    if not 1 <= len(datum) <= 160:
        raise ValueError("请声明米制高程的垂直基准（1–160字符）。")
    source_hash = hashlib.sha256(data).hexdigest()
    with MemoryFile(data) as mem:
        with mem.open() as ds:
            if ds.driver != "GTiff" or ds.count != 1 or ds.crs is None:
                raise ValueError("需要带CRS的单波段GeoTIFF DEM。")
            if ds.width * ds.height > MAX_PIXELS or min(ds.width, ds.height) < 2:
                raise ValueError("DEM需至少2×2、至多200万像元，请裁剪后导入。")
            unit = (ds.units[0] or "m").lower()
            if unit not in ["m", "meter", "meters", "metre", "metres"]:
                raise ValueError("仅支持米制高程，请先转换高度单位。")
            band = ds.read(1, masked=True)
            raw = np.asarray(band, dtype=float)
            invalid = np.ma.getmaskarray(band) | ~np.isfinite(raw)
            scale, offset = ds.scales[0], ds.offsets[0]
            if not np.isfinite(scale) or not np.isfinite(offset) or scale == 0:
                raise ValueError("DEM scale/offset不合法。")
            z = raw * scale + offset
            if not np.any(~invalid) or np.any(
                (z[~invalid] < -15000) | (z[~invalid] > 100000)
            ):
                raise ValueError(
                    "DEM无有效高程或超出本模型米制高程范围[-15000,100000]。"
                )
            z[invalid] = NODATA
            transform = ds.transform
            operations = ["GeoTIFF单波段，按scale/offset还原米制高程；保留NoData掩码"]
            if (
                ds.crs.to_epsg() != 4326
                or transform.b != 0
                or transform.d != 0
                or transform.a <= 0
                or transform.e >= 0
            ):
                target, width, height = calculate_default_transform(
                    ds.crs, "EPSG:4326", ds.width, ds.height, *ds.bounds
                )
                if width * height > MAX_PIXELS or min(width, height) < 2:
                    raise ValueError("重投影输出超过200万像元或尺寸无效，请先裁剪。")
                destination = np.full((height, width), NODATA, dtype=float)
                mask = np.ones((height, width), dtype="uint8")
                config = dict(
                    src_transform=transform,
                    src_crs=ds.crs,
                    dst_transform=target,
                    dst_crs="EPSG:4326",
                    num_threads=1,
                    warp_mem_limit=64,
                )
                reproject(
                    z,
                    destination,
                    src_nodata=NODATA,
                    dst_nodata=NODATA,
                    resampling=Resampling.max,
                    **config,
                )
                # Unknown source pixels are data=1, not nodata: max propagates any touched unknown.
                reproject(
                    invalid.astype("uint8"),
                    mask,
                    src_nodata=None,
                    dst_nodata=1,
                    resampling=Resampling.max,
                    **config,
                )
                destination[(mask != 0) | ~np.isfinite(destination)] = NODATA
                z, transform = destination, target
                operations.append(
                    "重投影EPSG:4326：高程max；未知掩码独立max传播，输出外部为NoData"
                )
            else:
                operations.append("北向EPSG:4326原网格，未重采样")
            lon = transform.c + (np.arange(z.shape[1]) + 0.5) * transform.a
            lat = transform.f + (np.arange(z.shape[0]) + 0.5) * transform.e
            west, east = transform.c, transform.c + z.shape[1] * transform.a
            north, south = transform.f, transform.f + z.shape[0] * transform.e
            if not (-180 <= west < east <= 180 and -90 <= south < north <= 90):
                raise ValueError("准备栅格范围无效或跨越日期变更线，请拆分区域。")
            valid = (z != NODATA) & np.isfinite(z)
            if not np.any(valid):
                raise ValueError("准备后的DEM没有已知高程。")
            metadata = {
                "name": name.replace("\\", "/").split("/")[-1][:160] or "本地DEM",
                "vertical_datum": datum,
                "horizontal_crs": "EPSG:4326",
                "source": "用户提供GeoTIFF",
                "source_sha256": source_hash,
                "source_crs": ds.crs.to_string(),
                "source_dimensions": [ds.width, ds.height],
                "source_transform": list(ds.transform)[:6],
                "processing": operations,
                "valid_fraction": float(np.mean(valid)),
                "bounds": [west, south, east, north],
            }
    content = io.BytesIO()
    np.savez_compressed(
        content,
        dem=z,
        longitude=lon,
        latitude=lat,
        nodata=np.array(NODATA),
        metadata=json.dumps(metadata, ensure_ascii=False, sort_keys=True),
    )
    packed = content.getvalue()
    digest = hashlib.sha256(packed).hexdigest()
    asset_id = "DEM-" + digest[:20]
    put_immutable(directory / (digest + ".npz"), packed)
    put_immutable(directory / "sources" / (source_hash + ".tif"), data)
    public = {**metadata, "asset_id": asset_id, "sha256": digest}
    put_immutable(
        directory / (digest + ".json"),
        (json.dumps(public, ensure_ascii=False, indent=2) + "\n").encode(),
    )
    with terrain_store(directory):
        return describe(asset_id, digest)


def describe(asset_id, digest):
    info = terrain_info(asset_id, digest)
    dem, lon, lat, nodata = terrain_data(asset_id, digest)
    dx, dy = float(lon[1] - lon[0]), float(lat[0] - lat[1])
    return {
        "asset_id": asset_id,
        "name": info["name"],
        "sha256": digest,
        "terrain": {
            "status": "available",
            "asset_id": asset_id,
            "sha256": digest,
            "horizontal_crs": "EPSG:4326",
            "vertical_datum": info["vertical_datum"],
        },
        "bounds": [
            float(lon[0] - dx / 2),
            float(lat[-1] - dy / 2),
            float(lon[-1] + dx / 2),
            float(lat[0] + dy / 2),
        ],
        "dimensions": [dem.shape[1], dem.shape[0]],
        "valid_fraction": info.get(
            "valid_fraction", float(np.mean(np.isfinite(dem) & (dem != nodata)))
        ),
        "source_sha256": info.get("source_sha256"),
        "source_crs": info.get("source_crs", "EPSG:4326"),
        "processing": info.get("processing", ["只读原题MAT栅格，无重采样"]),
    }


def catalog(directory):
    from backend.app.map_assets import original_identity

    asset_id, digest = original_identity()
    with terrain_store(directory):
        result = [describe(asset_id, digest)]
        for path in sorted(directory.glob("*.json")):
            try:
                info = json.loads(path.read_text(encoding="utf-8"))
                result.append(describe(info["asset_id"], info["sha256"]))
            except (OSError, ValueError, KeyError):
                # Corrupt entries cannot be selected; direct lookup still yields an explicit error.
                continue
    return result
