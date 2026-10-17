"""Offline previews of the exact terrain asset bound to a scene."""

from functools import lru_cache
import hashlib
from pathlib import Path
import uuid

import numpy as np
from PIL import Image
from pyproj import Geod

from solver.assets import terrain_data, terrain_info
from solver.errors import InputNotReady

ROOT = Path(__file__).resolve().parents[2]
GEOD = Geod(ellps="WGS84")


@lru_cache(maxsize=1)
def original_identity():
    path = next((ROOT / "references/modeling/data/terrain").glob("*DEM.mat"))
    return "contest-dem-30m", hashlib.sha256(path.read_bytes()).hexdigest()


def metadata(asset_id=None, digest=None):
    if asset_id is None and digest is None:
        asset_id, digest = original_identity()
    if not asset_id or not digest:
        raise InputNotReady("地图资产ID和hash必须一起提供。")
    info = terrain_info(asset_id, digest)
    _, lon, lat, _ = terrain_data(asset_id, digest)
    dx, dy = float(lon[1] - lon[0]), float(lat[0] - lat[1])
    west, east = float(lon[0] - dx / 2), float(lon[-1] + dx / 2)
    north, south = float(lat[0] + dy / 2), float(lat[-1] - dy / 2)
    return {
        "asset_id": asset_id,
        "name": info["name"],
        "sha256": digest,
        "bounds": [west, south, east, north],
        "coordinates": [[west, north], [east, north], [east, south], [west, south]],
        "crs": "EPSG:4326",
        "source": info["source"],
        "notice": "DEM高程与晕渲展示；透明区域为未知高程。不是卫星图、现势灾情或实飞认证。",
        "image_url": f"/api/v1/map/terrain/{asset_id}/{digest}.png",
    }


def image(directory: Path, asset_id=None, digest=None):
    meta = metadata(asset_id, digest)
    asset_id, digest = meta["asset_id"], meta["sha256"]
    path = directory / "map" / (asset_id + "-" + digest + ".png")
    if path.is_file():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    source, lon, lat, nodata = terrain_data(asset_id, digest)
    stride = max(1, int(max(source.shape) / 1000))
    z = source[::stride, ::stride].astype(float)
    valid = np.isfinite(z) & (z != nodata)
    if not np.any(valid):
        raise InputNotReady("DEM预览没有有效高程。")
    filled = np.where(valid, z, np.median(z[valid]))
    mx = (
        abs(
            GEOD.inv(
                float(lon[0]), float(lat.mean()), float(lon[1]), float(lat.mean())
            )[2]
        )
        * stride
    )
    my = (
        abs(
            GEOD.inv(
                float(lon.mean()), float(lat[0]), float(lon.mean()), float(lat[1])
            )[2]
        )
        * stride
    )
    gy = (
        np.gradient(filled, axis=0) / max(my, 1e-9)
        if filled.shape[0] > 1
        else np.zeros_like(filled)
    )
    gx = (
        np.gradient(filled, axis=1) / max(mx, 1e-9)
        if filled.shape[1] > 1
        else np.zeros_like(filled)
    )
    slope = np.arctan(np.hypot(gx, gy))
    aspect = np.arctan2(-gx, gy)
    shade = np.clip(
        np.cos(np.deg2rad(45)) * np.cos(slope)
        + np.sin(np.deg2rad(45)) * np.sin(slope) * np.cos(np.deg2rad(315) - aspect),
        0,
        1,
    )
    low, high = np.percentile(z[valid], [1, 99])
    height = np.clip((filled - low) / max(1, high - low), 0, 1)
    base = np.stack([226 - height * 45, 235 - height * 39, 219 - height * 56], axis=-1)
    rgb = np.clip(base * (0.83 + 0.22 * shade[:, :, None]), 0, 255).astype("uint8")
    rgba = np.concatenate([rgb, (valid * 255).astype("uint8")[:, :, None]], axis=-1)
    temp = path.with_name(uuid.uuid4().hex + ".png")
    try:
        Image.fromarray(rgba).save(temp)
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)
    return path
