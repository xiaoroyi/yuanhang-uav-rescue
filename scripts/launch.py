"""Run the built local app as one service; never install or contact external hosts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import socket
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser

ROOT = Path(__file__).resolve().parents[1]


def workspace_id():
    return hashlib.sha256(str(ROOT).casefold().encode()).hexdigest()[:12]


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
    if not (ROOT / "frontend/dist/index.html").exists():
        print(
            "前端尚未构建。请先运行 setup.cmd，或 npm.cmd --prefix frontend run build。"
        )
        return 1
    url = f"http://127.0.0.1:{args.port}"
    running = local_health(args.port)
    if running and running.get("workspace_id") == workspace_id():
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
            if local_health(args.port):
                print(
                    f"援航已启动：{url}\n数据保存在项目 runtime/ 中。关闭此窗口或 Ctrl+C 可停止服务。",
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
