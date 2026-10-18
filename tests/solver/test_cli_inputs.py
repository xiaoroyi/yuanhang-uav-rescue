import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]


def run(module, source, output):
    return subprocess.run(
        [
            sys.executable,
            "-m",
            module,
            "--scenario",
            str(source),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        timeout=30,
    )


@pytest.mark.parametrize("module", ["solver", "solver.nominal"])
def test_cli_refuses_to_overwrite_its_input_scene(case, tmp_path, module):
    path = tmp_path / "scene.json"
    original = (
        json.dumps(case[0]["scenario"], ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")
    path.write_bytes(original)
    result = run(module, path, path)
    assert result.returncode == 2
    assert "不能覆盖" in result.stderr
    assert path.read_bytes() == original


@pytest.mark.parametrize("module", ["solver", "solver.nominal"])
def test_cli_rejects_duplicate_json_keys_instead_of_silently_choosing_a_value(
    case, tmp_path, module
):
    path = tmp_path / "ambiguous.json"
    output = tmp_path / "result.json"
    original = (
        '{"name":"duplicate first value",'
        + json.dumps(case[0]["scenario"], ensure_ascii=False)[1:]
    ).encode("utf-8")
    path.write_bytes(original)
    result = run(module, path, output)
    assert result.returncode == 2
    assert "duplicate JSON key" in result.stderr
    assert not output.exists()
    assert path.read_bytes() == original
