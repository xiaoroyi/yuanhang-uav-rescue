"""A Windows progress-file sharing race must not erase known search progress or return 500."""

import json
from pathlib import Path

from fastapi.testclient import TestClient
import pytest

from backend.app.main import create_app
from backend.app.storage import JobRow


@pytest.mark.parametrize("failure", ["sharing_violation", "missing", "incomplete_json"])
def test_advisory_progress_keeps_last_valid_sample_without_failing_job(
    tmp_path, monkeypatch, failure
):
    app = create_app(tmp_path / "runtime")
    with TestClient(app, raise_server_exceptions=False) as client:
        with app.state.database.session(immediate=True) as session:
            session.add(
                JobRow(
                    id="JOB-ADVISORY-TEST",
                    scenario_id="TEST-ONLY",
                    state="running",
                    content={},
                    options={},
                )
            )
        path = tmp_path / "runtime/jobs/JOB-ADVISORY-TEST/progress.json"
        path.parent.mkdir(parents=True)
        known = {"stage": "正在搜索真实候选", "elapsed_s": 12.5, "candidate_count": 4}
        path.write_text(json.dumps(known), encoding="utf-8")
        endpoint = "/api/v1/solve-jobs/JOB-ADVISORY-TEST/progress"
        first = client.get(endpoint)
        assert first.status_code == 200, first.text
        assert first.json()["candidate_count"] == 4
        read = Path.read_text

        def unstable(self, *args, **kwargs):
            if self == path:
                if failure == "sharing_violation":
                    raise PermissionError(13, "Windows sharing violation")
                if failure == "missing":
                    raise FileNotFoundError("Progress file replacement window")
                return "{"
            return read(self, *args, **kwargs)

        with monkeypatch.context() as patch:
            patch.setattr(Path, "read_text", unstable)
            response = client.get(endpoint)
        assert response.status_code == 200, response.text
        current = response.json()
        assert (
            current["candidate_count"] == 4
            and current["elapsed_s"] == known["elapsed_s"]
        )
        assert "暂不可读" in current["stage"]
        assert client.get(endpoint).json()["stage"] == known["stage"]
        with app.state.database.session() as session:
            assert session.get(JobRow, "JOB-ADVISORY-TEST").state == "running"
