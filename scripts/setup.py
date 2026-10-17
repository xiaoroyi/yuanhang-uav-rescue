"""Explicit online setup. All dependencies stay inside this project."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description="安装援航项目依赖并构建离线前端")
    parser.add_argument(
        "--with-browser", action="store_true", help="额外安装浏览器验收所需Chromium"
    )
    args = parser.parse_args()
    if not ((3, 11) <= sys.version_info[:2] < (3, 13)):
        print("请使用 Python 3.11 或 3.12 运行此脚本。")
        return 1
    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    if not npm:
        print("未找到 Node.js/npm。请安装 Node.js 24 LTS 后重试。")
        return 1
    env = dict(os.environ)
    # Do not inherit a disabled TLS check into dependency installation.
    env.pop("NODE_TLS_REJECT_UNAUTHORIZED", None)
    interpreter = ROOT / (
        ".venv/Scripts/python.exe" if os.name == "nt" else ".venv/bin/python"
    )
    if not interpreter.exists():
        venv.create(ROOT / ".venv", with_pip=True)
    commands = [
        [str(interpreter), "-m", "pip", "install", "-r", "requirements.lock.txt"],
        [npm, "ci", "--prefix", "frontend"],
        [npm, "--prefix", "frontend", "run", "build"],
    ]
    if args.with_browser:
        env["PLAYWRIGHT_BROWSERS_PATH"] = str(ROOT / ".local/ms-playwright")
        commands.append(
            [
                shutil.which("node"),
                str(ROOT / "frontend/node_modules/@playwright/test/cli.js"),
                "install",
                "chromium",
            ]
        )
    for command in commands:
        result = subprocess.run(command, cwd=ROOT, env=env)
        if result.returncode:
            return result.returncode
    print(
        "安装与构建完成。Windows 双击 start.cmd，其他系统运行 .venv/bin/python scripts/launch.py --open。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
