"""File-controlled isolated test server; no Windows process-tree queries are needed."""

import os
from pathlib import Path
import threading
import time
import uvicorn

server = uvicorn.Server(
    uvicorn.Config(
        "backend.app.main:app",
        host="127.0.0.1",
        port=8011,
        log_level="warning",
        access_log=False,
    )
)


def stop_on_request():
    stop = Path(os.environ["YUANHANG_E2E_STOP_FILE"])
    while not stop.exists():
        time.sleep(0.1)
    server.should_exit = True


threading.Thread(target=stop_on_request, daemon=True).start()
server.run()
