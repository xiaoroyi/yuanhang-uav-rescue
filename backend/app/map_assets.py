"""Offline terrain visualization derived from the original DEM, never a synthetic basemap."""

from functools import lru_cache
import hashlib
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.io import loadmat

ROOT = Path(__file__).resolve().parents[2]


@lru_cache(maxsize=1)
def metadata():
    path = next((ROOT / "references/modeling/data/terrain").glob("*DEM.mat"))
    value = loadmat(path)
    lon = value["longitude"].ravel()
    lat = value["latitude"].ravel()
    return {
        "asset_id": "contest-dem-30m",
        "name": "镇龙乡30米DEM",
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "bounds": [
            float(lon.min()),
            float(lat.min()),
            float(lon.max()),
            float(lat.max()),
        ],
        "coordinates": [
            [float(lon.min()), float(lat.max())],
            [float(lon.max()), float(lat.max())],
            [float(lon.max()), float(lat.min())],
            [float(lon.min()), float(lat.min())],
        ],
        "crs": "EPSG:4326",
        "source": "原题提供的数字高程栅格",
        "notice": "仅为DEM高程与晕渲展示，不是卫星图、现势灾情或实飞障碍认证。",
        "image_url": "/api/v1/map/terrain.png",
    }


def image(directory: Path):
    path = directory / "map" / "contest-dem-preview.png"
    if path.is_file():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    source = next((ROOT / "references/modeling/data/terrain").glob("*DEM.mat"))
    z = loadmat(source)["dem"].astype(float)
    # Downsample for display only. Solver keeps original raster and closed-cell maxima.
    stride = max(1, int(max(z.shape) / 1000))
    z = z[::stride, ::stride]
    gy, gx = np.gradient(z)
    slope = np.arctan(np.hypot(gx, gy) / 30)
    aspect = np.arctan2(-gx, gy)
    shade = np.clip(
        np.cos(np.deg2rad(45)) * np.cos(slope)
        + np.sin(np.deg2rad(45)) * np.sin(slope) * np.cos(np.deg2rad(315) - aspect),
        0,
        1,
    )
    low, high = np.percentile(z, [1, 99])
    height = np.clip((z - low) / max(1, high - low), 0, 1)
    base = np.stack([226 - height * 45, 235 - height * 39, 219 - height * 56], axis=-1)
    rgb = np.clip(base * (0.83 + 0.22 * shade[:, :, None]), 0, 255).astype("uint8")
    temp = path.with_suffix(".tmp.png")
    Image.fromarray(rgb).save(temp)
    temp.replace(path)
    return path
