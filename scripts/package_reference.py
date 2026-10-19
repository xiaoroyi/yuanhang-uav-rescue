"""Build a private Windows reference delivery with a consistent runtime copy.

Never copies Git credentials, user configuration, a whole Conda environment,
node_modules, model weights or live SQLite/WAL files. The portable interpreter
is assembled from this machine's matching CPython and project dependencies.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.backup import create_backup, restore_backup
from shared.build_info import frontend_fingerprint, service_fingerprint


def digest(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def copy_tree(source, target):
    shutil.copytree(
        source,
        target,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", "~$*"),
    )


def file_row(stage, path):
    return {
        "path": path.relative_to(stage).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": digest(path),
    }


def keep_demo(relative):
    if relative.startswith("frontend/dist/"):
        return True
    if relative.startswith(("portable-python/", "runtime/", "data-backup/")):
        return True
    if Path(relative).name == "AGENTS.md":
        return False
    if (
        relative.endswith(".md")
        and relative not in {"README.md", "docs/PROJECT_DEMO_GUIDE.md"}
        and not relative.startswith(("frontend/src/", "frontend/public/"))
    ):
        return False
    return relative.startswith(
        (
            "portable-python/",
            "runtime/",
            "data-backup/",
            "frontend/",
            "backend/",
            "solver/",
            "shared/",
            "contracts/",
            "references/modeling/data/",
            "docs/demo-images/",
        )
    ) or relative in {
        "start.cmd",
        "backup.cmd",
        "requirements.lock.txt",
        "README.md",
        "先读我.txt",
        "docs/PROJECT_DEMO_GUIDE.md",
        "docs/援航项目介绍与演示指南.docx",
        "scripts/launch.py",
        "scripts/backup.py",
        "scripts/check_reference_bundle.py",
    }


def demo_only(stage):
    stage = stage.resolve()
    if not stage.is_relative_to(ROOT / ".local"):
        raise ValueError("只能整理本仓库.local中的交付目录。")
    manifest_path = stage / "BUNDLE_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = {r["path"]: r for r in manifest["files"]}
    removed = []
    for key in list(rows):
        if keep_demo(key):
            continue
        path = (stage / key).resolve()
        if not path.is_relative_to(stage):
            raise ValueError("交付清单路径超出目录。")
        path.unlink()
        del rows[key]
        removed.append(key)
    build = json.loads(
        (stage / "frontend/dist/assets/build-info.json").read_text(encoding="utf-8")
    )
    for artifact in build["artifacts"]:
        relative = "frontend/dist/" + artifact["path"]
        target = (stage / relative).resolve()
        if not target.is_relative_to(stage / "frontend/dist"):
            raise ValueError("构建清单路径非法。")
        if not target.is_file() or digest(target) != artifact["sha256"]:
            source = ROOT / relative
            if digest(source) != artifact["sha256"]:
                raise ValueError("正式前端与交付构建不一致。")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            rows[relative] = file_row(stage, target)
    # Dependency license/readme files are part of their distribution, not our
    # internal collaboration notes. Retain them even in the compact demo.
    cache = ROOT / ".local/reference-delivery/portable-python"
    for source in cache.rglob("*.md"):
        target = stage / "portable-python" / source.relative_to(cache)
        key = target.relative_to(stage).as_posix()
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            rows[key] = file_row(stage, target)
    for relative in [
        "docs/PROJECT_DEMO_GUIDE.md",
        "docs/援航项目介绍与演示指南.docx",
        "scripts/check_reference_bundle.py",
        "start.cmd",
        "backup.cmd",
    ]:
        target = stage / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, target)
        rows[relative] = file_row(stage, target)
    for source in (ROOT / "docs/demo-images").glob("*"):
        if source.is_file():
            target = stage / "docs/demo-images" / source.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            rows[target.relative_to(stage).as_posix()] = file_row(stage, target)
    readme = "# 援航 V4 项目演示包\n\n完整解压后双击 start.cmd，无需安装Python或Node。浏览器打开 http://127.0.0.1:8000/，保持服务窗口开启；Ctrl+C或关闭窗口停止，重启保留数据。\n\n端口冲突时运行 start.cmd --port 8001。现有任务、方案、地图、调度表和执行记录在包内runtime，演示只修改本包数据。\n\n项目介绍与完整演示方法见 docs/援航项目介绍与演示指南.docx 或 docs/PROJECT_DEMO_GUIDE.md。离线地形、图表、字体、教程和计算已携带；卫星影像需联网。EOH为可选本地评分，内置包为规则初始化。\n\nbackup.cmd用于一致性备份；首次使用可运行 portable-python\\python.exe scripts\\check_reference_bundle.py --initial-data 检查文件。适用于Windows10/11 x64，当前为业务仿真。\n"
    for name, text in [
        ("README.md", readme),
        ("先读我.txt", readme.replace("# 援航 V4 项目演示包", "援航 V4 项目演示包")),
    ]:
        (stage / name).write_text(
            text, encoding="utf-8-sig" if name.endswith(".txt") else "utf-8"
        )
        rows[name] = file_row(stage, stage / name)
    manifest["audience"] = "project_demo"
    manifest["source_note"] = (
        "Application core and frozen runtime data for project demonstration. Internal collaboration documents and research experiment records are excluded."
    )
    manifest["files"] = sorted(rows.values(), key=lambda r: r["path"])
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {"demo_files": len(rows), "removed_internal_files": len(removed)},
            ensure_ascii=False,
        )
    )


def refresh_source(stage):
    """Refresh only source/documents, preserving the frozen runtime and dependencies."""
    stage = stage.resolve()
    if not stage.is_relative_to(ROOT / ".local"):
        raise ValueError("只能更新本仓库.local内的交付目录。")
    manifest_path = stage / "BUNDLE_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = {r["path"]: r for r in manifest["files"]}
    sources = {
        ROOT / p
        for p in subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
        .decode("utf-8")
        .split("\0")
        if p
    }
    sources |= {
        ROOT / p
        for p in [
            "scripts/package_reference.py",
            "scripts/check_reference_bundle.py",
            "docs/REFERENCE_DELIVERY.md",
        ]
    }
    for folder in [
        "docs/current-project/contest-baselines-v1",
        "docs/current-project/contest-baselines-v2",
        "docs/current-project/contest-baselines-v3",
        "evidence/contest-baselines-v1",
        "evidence/contest-baselines-v2",
        "evidence/contest-baselines-v3",
        "scripts/contest_baselines",
    ]:
        sources |= {
            p
            for p in (ROOT / folder).rglob("*")
            if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
        }
    changed = []
    for source in sorted(sources):
        if not source.is_file() or source.is_symlink():
            continue
        key = source.relative_to(ROOT).as_posix()
        if manifest.get("audience") == "project_demo" and (
            not keep_demo(key) or key == "README.md"
        ):
            continue
        value = digest(source)
        if rows.get(key, {}).get("sha256") == value:
            continue
        target = stage / key
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        rows[key] = {"path": key, "bytes": target.stat().st_size, "sha256": value}
        changed.append(key)
    assert manifest["frontend_source_sha256"] == frontend_fingerprint(
        ROOT
    ), "前端已变化，需要重新构建交付包"
    manifest["source_commit"] = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    manifest["service_source_sha256"] = service_fingerprint(ROOT)
    manifest["documents_refreshed_at"] = datetime.now(timezone.utc).isoformat()
    manifest["files"] = sorted(rows.values(), key=lambda r: r["path"])
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"refreshed": changed, "files": len(rows)}, ensure_ascii=False))


def portable_python(target):
    if os.name != "nt" or sys.version_info[:2] != (3, 11):
        raise RuntimeError("当前构建器要求Windows x64的CPython3.11项目环境。")
    base = Path(sys.base_prefix)
    target.mkdir()
    for name in ("python.exe", "pythonw.exe", "LICENSE_PYTHON.txt"):
        shutil.copy2(base / name, target / name)
    for file in base.glob("*.dll"):
        shutil.copy2(file, target / file.name)
    shutil.copytree(
        base / "Lib",
        target / "Lib",
        ignore=shutil.ignore_patterns(
            "site-packages",
            "__pycache__",
            "*.pyc",
            "test",
            "idlelib",
            "tkinter",
            "turtledemo",
            "ensurepip",
        ),
    )
    shutil.copytree(
        base / "DLLs",
        target / "DLLs",
        ignore=shutil.ignore_patterns(
            "*_test*", "_test*", "xxlimited*", "_tkinter*", "*.ico"
        ),
    )
    required = {
        "bzip2.dll",
        "libbz2.dll",
        "expat.dll",
        "libexpat.dll",
        "ffi.dll",
        "ffi-7.dll",
        "ffi-8.dll",
        "libcrypto-3-x64.dll",
        "libssl-3-x64.dll",
        "liblzma.dll",
        "sqlite3.dll",
        "zlib.dll",
    }
    for file in (base / "Library/bin").glob("*.dll"):
        if file.name in required:
            shutil.copy2(file, target / "DLLs" / file.name)
    copy_tree(Path(sys.prefix) / "Lib/site-packages", target / "Lib/site-packages")
    (target / "python311._pth").write_text(
        ".\nLib\nDLLs\nLib/site-packages\n..\nimport site\n", encoding="utf-8"
    )
    (target / "Lib/sitecustomize.py").write_text(
        "import os, sys\nfrom pathlib import Path\n"
        "sys.dont_write_bytecode = True\n"
        "_runtime_dll_handles = []\n"
        "_dlls = Path(__file__).resolve().parents[1] / 'DLLs'\n"
        "if os.name == 'nt' and _dlls.is_dir():\n"
        "    _runtime_dll_handles.append(os.add_dll_directory(str(_dlls)))\n",
        encoding="utf-8",
    )
    licenses = target / "licenses"
    licenses.mkdir()
    names = {
        "python",
        "bzip2",
        "expat",
        "libexpat",
        "libffi",
        "liblzma",
        "xz",
        "openssl",
        "sqlite",
        "libsqlite",
        "zlib",
        "libzlib",
        "vc",
        "vc14_runtime",
        "vs2015_runtime",
        "ucrt",
    }
    packages = []
    cache = base.parents[1] / "pkgs"
    for metadata in (base / "conda-meta").glob("*.json"):
        data = json.loads(metadata.read_text(encoding="utf-8"))
        if data.get("name") not in names:
            continue
        packages.append(
            {
                k: data.get(k)
                for k in ("name", "version", "build", "license", "url", "sha256")
            }
        )
        package_id = f"{data['name']}-{data['version']}-{data['build']}"
        installed_source = Path(data.get("link", {}).get("source", cache / package_id))
        candidates = [
            installed_source / "info/licenses",
            installed_source / "info/LICENSE.txt",
            installed_source / "info/LICENSE",
            cache / package_id / "info/licenses",
            cache / package_id / "info/LICENSE.txt",
            cache / package_id / "info/LICENSE",
        ]
        for source in candidates:
            if source.is_dir():
                copy_tree(source, licenses / package_id)
                break
            if source.is_file():
                shutil.copy2(source, licenses / (package_id + ".txt"))
                break
    (licenses / "RUNTIME_PROVENANCE.json").write_text(
        json.dumps(
            {
                "python": sys.version,
                "method": "local matching CPython runtime plus locked project site-packages, no whole Conda environment",
                "packages": packages,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    installed = sorted(
        {
            f"{d.metadata['Name']}=={d.version}"
            for d in importlib.metadata.distributions()
            if d.metadata.get("Name")
        }
    )
    (target / "INSTALLED_PACKAGES.txt").write_text(
        "\n".join(installed) + "\n", encoding="utf-8"
    )


def build(stage):
    stage = stage.resolve()
    if not stage.is_relative_to(ROOT / ".local") or stage.exists():
        raise ValueError("构建目录必须是本仓库.local内尚不存在的新目录。")
    stage.mkdir(parents=True)
    files = (
        subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
        .decode("utf-8")
        .split("\0")
    )
    for relative in filter(None, files):
        source = ROOT / relative
        if not source.is_file() or source.is_symlink():
            continue
        target = stage / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    # Explicit local research supplements; they are not claimed as deployed UI features.
    for relative in [
        "scripts/package_reference.py",
        "scripts/check_reference_bundle.py",
        "docs/REFERENCE_DELIVERY.md",
    ]:
        source = ROOT / relative
        if source.is_file():
            (stage / relative).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, stage / relative)
    for prefix in [
        "docs/current-project/contest-baselines-v1",
        "docs/current-project/contest-baselines-v2",
        "docs/current-project/contest-baselines-v3",
        "evidence/contest-baselines-v1",
        "evidence/contest-baselines-v2",
        "evidence/contest-baselines-v3",
        "scripts/contest_baselines",
    ]:
        source = ROOT / prefix
        if source.is_dir() and not (stage / prefix).exists():
            copy_tree(source, stage / prefix)
    copy_tree(ROOT / "frontend/dist", stage / "frontend/dist")
    archive, data = create_backup(
        ROOT / "runtime", ROOT / ".local/reference-delivery/backups"
    )
    restore_backup(archive, stage / "runtime")
    for folder in ["jobs", "map"]:
        if (ROOT / "runtime" / folder).is_dir():
            copy_tree(ROOT / "runtime" / folder, stage / "runtime" / folder)
    (stage / "data-backup").mkdir()
    shutil.copy2(archive, stage / "data-backup" / archive.name)
    cached = ROOT / ".local/reference-delivery/portable-python"
    if (cached / "INSTALLED_PACKAGES.txt").is_file():
        copy_tree(cached, stage / "portable-python")
    else:
        portable_python(stage / "portable-python")
    (stage / "先读我.txt").write_text(
        "援航 V4 完整参考包 Windows x64\n\n"
        "1. 请先完整解压ZIP，不要在压缩软件里直接运行。建议解压到较短路径。\n"
        "2. 双击 start.cmd，保持服务窗口开启，浏览器会打开 http://127.0.0.1:8000/。\n"
        "   无需安装Python、Node或联网下载依赖；首次启动允许本机回环访问即可。\n"
        "3. 若8000被占用，在本目录终端运行 start.cmd --port 8001。不会终止已有程序。\n"
        "4. 首页进入救援任务即可查看随包保留的任务、真实方案、调度表和执行复盘。\n"
        "   案例库可另建任务重新计算；标准引擎默认，EOH内置包为规则初始化。\n"
        "5. 地形、图表、路线、字体、教程视频离线可用；在线卫星图和外部网页需要联网。\n"
        "6. 修改和演练只写本包runtime；不连接原作者电脑、不影响原作者任务。\n"
        "7. 关闭窗口或按Ctrl+C停止，重启保留数据。backup.cmd可生成一致性备份。\n\n"
        "项目内容：docs/PROJECT_DOSSIER.md 与 docs/current-project/下的Word。\n"
        "继续开发：prompts/06_CURRENT_PROJECT_HANDOFF.md。\n"
        "详细交付说明：docs/REFERENCE_DELIVERY.md。文件与初始数据清单：BUNDLE_MANIFEST.json。\n"
        "可选首次校验：portable-python\\python.exe scripts\\check_reference_bundle.py --initial-data\n\n"
        "这是内部参考包，含项目原始研究资料与本机任务历史；未携带账号密码、模型密钥、浏览器Cookie或Git凭据。\n"
        "个人浏览器保存的头像/配色不转移；新浏览器使用系统默认深蓝外观。\n",
        encoding="utf-8-sig",
    )
    paths = [p for p in sorted(stage.rglob("*")) if p.is_file()]
    with ThreadPoolExecutor(max_workers=8) as pool:
        rows = list(pool.map(lambda p: file_row(stage, p), paths))
    manifest = {
        "format": "yuanhang-reference-v1",
        "release": "V4-20261019-REF1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "source_note": "Current working source/document snapshot; explicitly included local baseline research supplements are separate from deployed solver",
        "platform": "Windows 10/11 x64",
        "service_source_sha256": service_fingerprint(ROOT),
        "frontend_source_sha256": frontend_fingerprint(ROOT),
        "data": {
            "backup_name": archive.name,
            "backup_sha256": digest(archive),
            "table_counts": data["table_counts"],
        },
        "files": rows,
    }
    (stage / "BUNDLE_MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "stage": str(stage),
                "files": len(rows),
                "bytes": sum(r["bytes"] for r in rows),
                "data": manifest["data"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", required=True, type=Path)
    parser.add_argument("--zip", type=Path, help="仅压缩已构建目录，不重新复制数据")
    parser.add_argument("--refresh-source", action="store_true")
    parser.add_argument(
        "--demo-only", action="store_true", help="整理为仅含项目介绍与演示内容的对外包"
    )
    args = parser.parse_args()
    if args.zip:
        if args.zip.exists():
            raise ValueError("不覆盖已有压缩包。")
        with zipfile.ZipFile(
            args.zip, "w", zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True
        ) as output:
            for file in sorted(args.stage.rglob("*")):
                if (
                    file.is_file()
                    and "__pycache__" not in file.parts
                    and file.suffix != ".pyc"
                ):
                    output.write(
                        file,
                        "Yuanhang-V4-Reference/"
                        + file.relative_to(args.stage).as_posix(),
                    )
        print(
            json.dumps(
                {
                    "zip": str(args.zip),
                    "bytes": args.zip.stat().st_size,
                    "sha256": digest(args.zip),
                },
                ensure_ascii=False,
            )
        )
    elif args.demo_only:
        demo_only(args.stage)
    elif args.refresh_source:
        refresh_source(args.stage)
    else:
        build(args.stage)


if __name__ == "__main__":
    main()
