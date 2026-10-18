import json
import os

from backend.app.worker import atomic_json


def test_atomic_progress_survives_temporary_windows_reader_lock(tmp_path, monkeypatch):
    destination = tmp_path / "progress.json"
    destination.write_text('{"candidate_count":1}', encoding="utf-8")
    replace = os.replace
    failures = []

    def briefly_locked(source, target):
        if len(failures) < 2:
            failures.append(True)
            assert json.loads(destination.read_text()) == {"candidate_count": 1}
            raise PermissionError("simulated Windows sharing violation")
        replace(source, target)

    monkeypatch.setattr("backend.app.worker.os.replace", briefly_locked)
    atomic_json(destination, {"candidate_count": 2})
    assert len(failures) == 2
    assert json.loads(destination.read_text()) == {"candidate_count": 2}
