"""Consistent local SQLite/asset backups and non-overwriting restores.

Uses SQLite backup(), never copies a live WAL database file directly. Archives
contain a closed manifest; verification does not extract untrusted ZIP paths.
"""

from datetime import datetime, timezone
from contextlib import closing
import hashlib
import json
import os
import re
from pathlib import Path, PurePosixPath
import sqlite3
import stat
import subprocess
import sys
import tempfile
import uuid
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from shared.build_info import service_fingerprint

MAX_BYTES = 512 * 1024 * 1024
MAX_FILES = 4096


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_database(path):
    return sqlite3.connect(
        Path(path).resolve().as_uri() + "?mode=ro", uri=True, timeout=15
    )


def safe_name(name):
    path = PurePosixPath(name)
    if (
        not name
        or "\\" in name
        or path.is_absolute()
        or ".." in path.parts
        or path.as_posix() != name
        or name.endswith("/")
        or not (
            name in ("manifest.json", "yuanhang.sqlite3")
            or name.startswith("assets/")
            or re.fullmatch(r"heuristics/[A-Za-z0-9_-]{1,80}\.json", name)
        )
    ):
        raise ValueError("备份中包含不允许的文件路径。")


def inspect_archive(archive):
    """Validate paths, sizes, file sets, CRC and streamed bytes before restore."""
    with zipfile.ZipFile(archive) as bundle:
        entries = bundle.infolist()
        names = [entry.filename for entry in entries]
        if len(names) > MAX_FILES or len(set(names)) != len(names):
            raise ValueError("备份文件过多或包含重复条目。")
        for entry in entries:
            safe_name(entry.filename)
            if stat.S_IFMT(entry.external_attr >> 16) == stat.S_IFLNK:
                raise ValueError("备份不接受符号链接。")
        if sum(entry.file_size for entry in entries) > MAX_BYTES:
            raise ValueError("备份展开大小超过512MiB限制。")
        if (
            "manifest.json" not in names
            or bundle.getinfo("manifest.json").file_size > 1024 * 1024
        ):
            raise ValueError("备份清单缺失或过大。")
        manifest = json.loads(bundle.read("manifest.json"))
        if manifest.get("format_version") != 1 or not isinstance(
            manifest.get("files"), list
        ):
            raise ValueError("备份格式版本不受支持。")
        listed = [row["path"] for row in manifest["files"]]
        if (
            len(set(listed)) != len(listed)
            or set(names) != {"manifest.json", *listed}
            or "yuanhang.sqlite3" not in listed
            or "manifest.json" in listed
        ):
            raise ValueError("备份文件集合与清单不一致。")
        for row in manifest["files"]:
            safe_name(row["path"])
            info = bundle.getinfo(row["path"])
            if info.file_size != row["bytes"]:
                raise ValueError("备份文件长度与清单不一致。")
            digest, size = hashlib.sha256(), 0
            with bundle.open(info) as stream:
                while block := stream.read(1024 * 1024):
                    size += len(block)
                    if size > row["bytes"] or size > MAX_BYTES:
                        raise ValueError("备份文件展开大小异常。")
                    digest.update(block)
            if size != row["bytes"] or digest.hexdigest() != row["sha256"]:
                raise ValueError("备份文件hash与清单不一致。")
        return manifest


def create_backup(runtime, output_dir=None):
    runtime = Path(runtime).resolve()
    database = runtime / "yuanhang.sqlite3"
    if not database.is_file():
        raise ValueError("尚未找到本机数据库，请先启动援航并保存场景。")
    output = Path(output_dir).resolve() if output_dir else runtime / "backups"
    output.mkdir(parents=True, exist_ok=True)
    token = (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        + "-"
        + uuid.uuid4().hex[:8]
    )
    target = output / f"yuanhang-backup-{token}.zip"
    partial = output / f".backup-{token}.partial"
    handle = tempfile.NamedTemporaryFile(
        prefix=".backup-db-", suffix=".sqlite3", dir=output, delete=False
    )
    snapshot_path = Path(handle.name)
    handle.close()
    try:
        with closing(read_database(database)) as source, closing(
            sqlite3.connect(snapshot_path)
        ) as snapshot:
            source.backup(snapshot, pages=128, sleep=0.05)
            snapshot.execute("PRAGMA journal_mode=DELETE")
            if snapshot.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                raise ValueError("数据库备份未通过完整性检查。")
            tables = [
                row[0]
                for row in snapshot.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
            ]
            counts = {
                name: snapshot.execute(
                    'SELECT count(*) FROM "' + name.replace('"', '""') + '"'
                ).fetchone()[0]
                for name in tables
            }
        files = [("yuanhang.sqlite3", snapshot_path)]
        assets = runtime / "assets"
        for path in sorted(assets.rglob("*")) if assets.exists() else []:
            if path.is_file():
                if path.is_symlink() or not path.resolve().is_relative_to(
                    assets.resolve()
                ):
                    raise ValueError("资产目录包含外部链接，未将外部文件加入备份。")
                files.append(("assets/" + path.relative_to(assets).as_posix(), path))
        policies = runtime / "heuristics"
        if policies.exists():
            if policies.is_symlink() or not policies.resolve().is_relative_to(
                runtime.resolve()
            ):
                raise ValueError("策略目录包含外部链接。")
            from solver.engines import policy_store, read_policy

            with policy_store(policies):
                for path in sorted(policies.glob("*.json")):
                    name = "heuristics/" + path.name
                    safe_name(name)
                    if path.is_symlink() or not path.resolve().is_relative_to(
                        policies.resolve()
                    ):
                        raise ValueError("策略文件包含外部链接。")
                    read_policy(path.stem)
                    files.append((name, path))
        if (
            len(files) + 1 > MAX_FILES
            or sum(path.stat().st_size for _, path in files) > MAX_BYTES - 1024 * 1024
        ):
            raise ValueError("备份超过4096文件或512MiB限制。")
        try:
            revision = subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=ROOT,
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
            dirty = bool(
                subprocess.check_output(
                    ["git", "status", "--porcelain"],
                    cwd=ROOT,
                    text=True,
                    stderr=subprocess.DEVNULL,
                ).strip()
            )
        except (OSError, subprocess.CalledProcessError):
            revision = None
            dirty = None
        manifest = dict(
            format_version=1,
            created_at_utc=datetime.now(timezone.utc).isoformat(),
            source_commit=revision,
            source_worktree_dirty=dirty,
            service_source_sha256=service_fingerprint(ROOT),
            table_counts=counts,
            notes=[
                "SQLite一致性快照、不可变资产及本地策略包；不包含依赖环境、源码、日志或凭据。",
                "恢复只写入新目录；启动时未完成任务按异常恢复规则处理，不承诺继续原进程。",
            ],
            files=[
                dict(path=name, bytes=path.stat().st_size, sha256=sha256(path))
                for name, path in files
            ],
        )
        with zipfile.ZipFile(partial, "x", compression=zipfile.ZIP_DEFLATED) as bundle:
            for name, path in files:
                bundle.write(path, name)
            bundle.writestr(
                "manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2)
            )
        inspect_archive(partial)
        if target.exists():
            raise ValueError("同名备份已经存在，未覆盖。")
        partial.rename(target)
        return target, manifest
    finally:
        for owned in [snapshot_path, partial]:
            if owned.exists() and owned.resolve().parent == output.resolve():
                owned.unlink()


def restore_backup(archive, destination):
    manifest = inspect_archive(archive)
    destination = Path(destination).resolve()
    if destination.exists():
        raise ValueError("恢复目标已存在；请选择一个尚不存在的新目录，不覆盖当前数据。")
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = destination.parent / (".restore-" + uuid.uuid4().hex)
    staging.mkdir()
    try:
        with zipfile.ZipFile(archive) as bundle:
            for row in manifest["files"]:
                target = staging / row["path"]
                if not target.resolve().is_relative_to(staging.resolve()):
                    raise ValueError("恢复路径超出暂存目录。")
                target.parent.mkdir(parents=True, exist_ok=True)
                digest, size = hashlib.sha256(), 0
                with bundle.open(row["path"]) as source, target.open("xb") as output:
                    while block := source.read(1024 * 1024):
                        size += len(block)
                        if size > row["bytes"]:
                            raise ValueError("恢复文件超过已校验的长度。")
                        digest.update(block)
                        output.write(block)
                if size != row["bytes"] or digest.hexdigest() != row["sha256"]:
                    raise ValueError("恢复过程中来源文件发生变化或损坏。")
        with closing(read_database(staging / "yuanhang.sqlite3")) as database:
            if database.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                raise ValueError("恢复的数据库未通过完整性检查。")
        if destination.exists():
            raise ValueError("恢复目标被其他进程创建，未覆盖。")
        staging.rename(destination)
    except Exception as exc:
        raise ValueError(f"恢复未完成，暂存目录保留于{staging}：{exc}") from exc
    return manifest


def main():
    import argparse

    parser = argparse.ArgumentParser(description="援航本机数据备份、核验与新目录恢复")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--verify", type=Path)
    action.add_argument("--restore", type=Path)
    parser.add_argument("--into", type=Path, help="仅恢复到尚不存在的新数据目录")
    parser.add_argument(
        "--runtime",
        type=Path,
        default=Path(os.environ.get("YUANHANG_RUNTIME", str(ROOT / "runtime"))),
    )
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    if not args.runtime.is_absolute():
        args.runtime = ROOT / args.runtime
    try:
        if args.verify:
            manifest = inspect_archive(args.verify)
            print(
                json.dumps(
                    dict(
                        verified=True,
                        file_count=len(manifest["files"]),
                        table_counts=manifest["table_counts"],
                    ),
                    ensure_ascii=False,
                )
            )
        elif args.restore:
            if not args.into:
                parser.error("恢复时必须指定--into新目录。")
            manifest = restore_backup(args.restore, args.into)
            print(
                json.dumps(
                    dict(
                        restored=True,
                        runtime=str(args.into.resolve()),
                        table_counts=manifest["table_counts"],
                    ),
                    ensure_ascii=False,
                )
            )
        else:
            archive, manifest = create_backup(args.runtime, args.output_dir)
            print(
                json.dumps(
                    dict(
                        backup=str(archive),
                        sha256=sha256(archive),
                        file_count=len(manifest["files"]),
                        table_counts=manifest["table_counts"],
                    ),
                    ensure_ascii=False,
                )
            )
    except (
        OSError,
        ValueError,
        KeyError,
        TypeError,
        zipfile.BadZipFile,
        sqlite3.Error,
    ) as exc:
        print(f"备份操作未完成：{exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
