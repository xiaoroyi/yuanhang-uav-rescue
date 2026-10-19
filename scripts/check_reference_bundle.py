"""Verify an extracted reference delivery without installing anything."""

import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description="核对援航参考包文件与初始数据")
    parser.add_argument(
        "--initial-data",
        action="store_true",
        help="仅首次演示前：同时检查数据库与打包快照完全一致",
    )
    args = parser.parse_args()
    manifest = json.loads((ROOT / "BUNDLE_MANIFEST.json").read_text(encoding="utf-8"))

    def check(row):
        relative = Path(row["path"])
        path = (ROOT / relative).resolve()
        if (
            relative.is_absolute()
            or not path.is_relative_to(ROOT)
            or not path.is_file()
        ):
            raise ValueError("文件缺失或路径非法：" + row["path"])
        if row["path"].startswith("runtime/") and not args.initial_data:
            return 0
        with path.open("rb") as source:
            actual = hashlib.file_digest(source, "sha256").hexdigest()
        if path.stat().st_size != row["bytes"] or actual != row["sha256"]:
            raise ValueError("文件内容与交付清单不同：" + row["path"])
        return 1

    with ThreadPoolExecutor(max_workers=8) as pool:
        checked = sum(pool.map(check, manifest["files"]))
    db = sqlite3.connect(
        (ROOT / "runtime/yuanhang.sqlite3").as_uri() + "?mode=ro", uri=True
    )
    assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert not db.execute("PRAGMA foreign_key_check").fetchall()
    counts = {
        t: db.execute('SELECT COUNT(*) FROM "' + t + '"').fetchone()[0]
        for t in manifest["data"]["table_counts"]
    }
    db.close()
    if args.initial_data:
        assert counts == manifest["data"]["table_counts"]
    print(
        json.dumps(
            {
                "passed": True,
                "checked_files": checked,
                "initial_data": args.initial_data,
                "table_counts": counts,
                "python": sys.version.split()[0],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
