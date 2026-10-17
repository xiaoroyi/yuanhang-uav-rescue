"""Read-only content-addressed terrain access, scoped per request or pure-Python call."""

from contextlib import contextmanager
from contextvars import ContextVar
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re

import numpy as np

from solver.errors import InputNotReady

ROOT = Path(__file__).resolve().parents[1]
STORE = ContextVar("yuanhang_terrain_store", default=ROOT / "runtime/assets")


@contextmanager
def terrain_store(directory):
    token = STORE.set(Path(directory).resolve())
    try:
        yield
    finally:
        STORE.reset(token)


def terrain_token(asset_id, digest):
    if not isinstance(digest, str) or not re.fullmatch("[a-f0-9]{64}", digest):
        raise InputNotReady("地形资产缺少有效SHA256。")
    if asset_id == "contest-dem-30m":
        path = next((ROOT / "references/modeling/data/terrain").glob("*DEM.mat"))
    elif asset_id == "DEM-" + digest[:20]:
        root = STORE.get().resolve()
        path = (root / (digest + ".npz")).resolve()
        if path.parent != root:
            raise InputNotReady("地形资产路径越界。")
    else:
        raise InputNotReady("地形资产ID未注册或与hash不一致。")
    try:
        stat = path.stat()
    except OSError as exc:
        raise InputNotReady("找不到绑定的本地DEM资产，请重新导入对应文件。") from exc
    return str(path), digest, stat.st_mtime_ns, stat.st_size


@lru_cache(maxsize=8)
def arrays_for_token(token):
    filename, digest, _, _ = token
    path = Path(filename)
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise InputNotReady("地形资产内容hash与快照不一致。")
    if path.suffix == ".mat":
        from scipy.io import loadmat

        data = loadmat(path)
        dem, lon, lat, nodata = (
            data["dem"],
            data["longitude"].ravel(),
            data["latitude"].ravel(),
            float(data["nodata"].item()),
        )
        info = {
            "asset_id": "contest-dem-30m",
            "name": "镇龙乡30米DEM",
            "vertical_datum": "contest_provided_elevation_reference",
            "horizontal_crs": "EPSG:4326",
            "source": "原题提供的数字高程栅格",
        }
    else:
        try:
            with np.load(path, allow_pickle=False) as data:
                dem, lon, lat, nodata = (
                    data["dem"],
                    data["longitude"],
                    data["latitude"],
                    float(data["nodata"].item()),
                )
                info = json.loads(str(data["metadata"].item()))
        except (ValueError, KeyError, OSError) as exc:
            raise InputNotReady("本地DEM准备栅格已损坏。") from exc
    if (
        dem.ndim != 2
        or min(dem.shape) < 2
        or lon.shape != (dem.shape[1],)
        or lat.shape != (dem.shape[0],)
    ):
        raise InputNotReady("DEM栅格与坐标轴尺寸不一致。")
    if not (
        np.all(np.isfinite(lon))
        and np.all(np.isfinite(lat))
        and np.all(np.diff(lon) > 0)
        and np.all(np.diff(lat) < 0)
    ):
        raise InputNotReady("DEM必须具有递增经度与递减纬度。")
    for array in [dem, lon, lat]:
        array.setflags(write=False)
    return dem, lon, lat, nodata, info


def terrain_data(asset_id, digest):
    return arrays_for_token(terrain_token(asset_id, digest))[:4]


def terrain_info(asset_id, digest):
    return {
        **arrays_for_token(terrain_token(asset_id, digest))[4],
        "asset_id": asset_id,
        "sha256": digest,
    }


def validate_reference(ref):
    info = terrain_info(ref["asset_id"], ref["sha256"])
    if (
        ref["horizontal_crs"] != "EPSG:4326"
        or ref["vertical_datum"] != info["vertical_datum"]
    ):
        raise InputNotReady("场景DEM的CRS/垂直基准与注册资产不一致。")
    return info
