"""Run the built local app as one service; never install or contact external hosts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from shared.build_info import frontend_fingerprint, service_fingerprint


def workspace_id():
    return hashlib.sha256(str(ROOT).casefold().encode()).hexdigest()[:12]


def runtime_directory():
    directory = Path(os.environ.get("YUANHANG_RUNTIME", str(ROOT / "runtime")))
    return (directory if directory.is_absolute() else ROOT / directory).resolve()


def runtime_id():
    return hashlib.sha256(str(runtime_directory()).casefold().encode()).hexdigest()[:12]


def current_frontend():
    """Verify both source identity and built bytes; valid builds need no Node."""
    dist = ROOT / "frontend/dist"
    try:
        info = json.loads((dist / "assets/build-info.json").read_text(encoding="utf-8"))
        if info["fingerprint_version"] != 1 or info[
            "frontend_source_sha256"
        ] != frontend_fingerprint(ROOT):
            return False
        if not any(row["path"] == "index.html" for row in info["artifacts"]):
            return False
        for row in info["artifacts"]:
            path = (dist / row["path"]).resolve()
            if not path.is_relative_to(dist.resolve()) or not path.is_file():
                return False
            if (
                path.stat().st_size != row["bytes"]
                or hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"]
            ):
                return False
        return True
    except (OSError, ValueError, KeyError, TypeError):
        return False


def ensure_frontend():
    if current_frontend():
        return True
    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    if not npm or not (ROOT / "frontend/node_modules/vite").is_dir():
        print("前端尚未构建或已过期，缺少本地构建依赖。请先运行 setup.cmd。")
        return False
    print("前端需要更新，正在使用已安装依赖离线重建…", flush=True)
    env = {
        **os.environ,
        "npm_config_offline": "true",
        "npm_config_audit": "false",
        "npm_config_fund": "false",
    }
    env.pop("NODE_TLS_REJECT_UNAUTHORIZED", None)
    result = subprocess.run(
        [npm, "--prefix", "frontend", "run", "build"], cwd=ROOT, env=env
    )
    if result.returncode != 0 or not current_frontend():
        print("前端构建未完成，尚未启动服务；请查看上面的构建错误。")
        return False
    return True


def local_health(port):
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(
            f"http://127.0.0.1:{port}/api/v1/health", timeout=1
        ) as response:
            return json.load(response)
    except (OSError, ValueError):
        return None


def main():
    parser = argparse.ArgumentParser(description="援航离线调度系统")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--open", action="store_true", help="启动后在默认浏览器打开")
    args = parser.parse_args()
    if not (1 <= args.port <= 65535):
        parser.error("端口必须在1–65535之间")
    url = f"http://127.0.0.1:{args.port}"
    running = local_health(args.port)
    expected_source = service_fingerprint(ROOT)
    if (
        running
        and running.get("service_id") == "yuanhang-rescue"
        and running.get("workspace_id") == workspace_id()
    ):
        if running.get("runtime_id") != runtime_id():
            print(
                f"{args.port}端口上的援航服务使用其他数据目录或旧版身份协议。请关闭对应旧服务窗口后重启，或使用 --port 8001。"
            )
            return 1
        if running.get("service_source_sha256") != expected_source:
            print(
                "检测到仍在运行的旧版援航服务。请先在旧服务窗口按Ctrl+C，再重新运行start.cmd；当前服务不会被自动终止。"
            )
            return 1
        if not ensure_frontend():
            return 1
        print(f"援航已在运行：{url}")
        if args.open:
            webbrowser.open(url)
        return 0
    with socket.socket() as probe:
        if probe.connect_ex(("127.0.0.1", args.port)) == 0:
            print(
                f"{args.port}端口已被其他程序或旧服务占用。可用 --port 8001 指定其他端口。"
            )
            return 1
    if not ensure_frontend():
        return 1
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "backend.app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(args.port),
        ],
        cwd=ROOT,
    )

    def ready():
        for _ in range(100):
            if process.poll() is not None:
                return
            identity = local_health(args.port)
            if (
                identity
                and identity.get("service_source_sha256") == expected_source
                and identity.get("runtime_id") == runtime_id()
            ):
                print(
                    f"援航已启动：{url}\n数据目录：{runtime_directory()}\n关闭此窗口或 Ctrl+C 可停止服务。",
                    flush=True,
                )
                if args.open:
                    webbrowser.open(url)
                return
            time.sleep(0.2)

    threading.Thread(target=ready, daemon=True).start()
    try:
        return process.wait()
    except KeyboardInterrupt:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
