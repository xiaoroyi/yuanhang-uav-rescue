"""Production media must be served as media, not the SPA index fallback."""

import importlib
from fastapi.testclient import TestClient


def test_help_media_range_and_notices_do_not_fall_back_to_html(tmp_path, monkeypatch):
    main = importlib.import_module("backend.app.main")
    frontend = tmp_path / "project/frontend/dist"
    media = frontend / "help/v3"
    media.mkdir(parents=True)
    (frontend / "index.html").write_text("<html>APP</html>", encoding="utf-8")
    (media / "prepare.webp").write_bytes(b"RIFF-image-data")
    (media / "walkthrough.webm").write_bytes(b"0123456789-video-data")
    (media / "walkthrough.vtt").write_text("WEBVTT\n\n", encoding="utf-8")
    (frontend / "THIRD_PARTY_NOTICES.txt").write_text("MIT License", encoding="utf-8")
    monkeypatch.setattr(main, "ROOT", tmp_path / "project")
    with TestClient(main.create_app(tmp_path / "runtime")) as c:
        image = c.get("/help/v3/prepare.webp")
        assert image.status_code == 200
        assert image.headers["content-type"].startswith("image/webp")
        assert image.content == b"RIFF-image-data"
        video = c.get("/help/v3/walkthrough.webm", headers={"Range": "bytes=2-5"})
        assert video.status_code == 206 and video.content == b"2345"
        assert video.headers["content-type"].startswith("video/webm")
        assert (
            c.get("/help/v3/walkthrough.vtt")
            .headers["content-type"]
            .startswith("text/vtt")
        )
        notices = c.get("/THIRD_PARTY_NOTICES.txt")
        assert notices.text == "MIT License"
        assert notices.headers["content-type"].startswith("text/plain")
        assert c.get("/help/v3/missing.webp").status_code == 404
        assert c.get("/").text == "<html>APP</html>"
