import json
from pathlib import Path
import shutil
import subprocess
import sys
from types import SimpleNamespace

import pytest

from scripts import launch
from shared.build_info import (
    frontend_fingerprint,
    service_fingerprint,
    verification_fingerprint,
)

BUILDER = Path(__file__).resolve().parents[2] / "frontend/scripts/build-info.mjs"


@pytest.fixture
def project(tmp_path, monkeypatch):
    for folder in ["frontend/src", "frontend/dist/assets", "solver", "shared", "tests"]:
        (tmp_path / folder).mkdir(parents=True, exist_ok=True)
    for name, value in {
        "frontend/src/main.ts": "console.log('源代码')",
        "frontend/index.html": "<main></main>",
        "frontend/package.json": "{}",
        "frontend/dist/index.html": '<script src="/assets/app.js"></script>',
        "frontend/dist/assets/app.js": "console.log('built')",
        "solver/example.py": "VALUE = 1\n",
    }.items():
        (tmp_path / name).write_text(value, encoding="utf-8")
    monkeypatch.setattr(launch, "ROOT", tmp_path)
    monkeypatch.delenv("YUANHANG_RUNTIME", raising=False)
    return tmp_path


def build(project):
    node = shutil.which("node")
    if not node:
        pytest.skip("Node is required for cross-runtime build identity verification.")
    return subprocess.run(
        [node, str(BUILDER), "--write", str(project)],
        check=True,
        capture_output=True,
        text=True,
    )


def test_node_and_python_source_identities_match_for_unicode_files(project):
    (project / "frontend/src/中文😀.ts").write_text(
        "export const value = '地图'", encoding="utf-8"
    )
    build(project)
    info = json.loads(
        (project / "frontend/dist/assets/build-info.json").read_text(encoding="utf-8")
    )
    assert info["frontend_source_sha256"] == frontend_fingerprint(project)
    assert launch.current_frontend()


def test_valid_build_is_usable_without_node_or_network(project, monkeypatch):
    build(project)

    def forbidden(*args, **kwargs):
        raise AssertionError("A valid offline build must not resolve or run npm.")

    monkeypatch.setattr(launch.shutil, "which", forbidden)
    monkeypatch.setattr(launch.subprocess, "run", forbidden)
    assert launch.ensure_frontend()


@pytest.mark.parametrize("problem", ["source", "artifact", "outside_path"])
def test_source_changes_and_incomplete_or_invalid_builds_are_detected(project, problem):
    build(project)
    if problem == "source":
        (project / "frontend/src/main.ts").write_text("CHANGED", encoding="utf-8")
    elif problem == "artifact":
        (project / "frontend/dist/assets/app.js").write_text(
            "CORRUPTED", encoding="utf-8"
        )
    else:
        path = project / "frontend/dist/assets/build-info.json"
        info = json.loads(path.read_text(encoding="utf-8"))
        info["artifacts"][0]["path"] = "../../solver/example.py"
        path.write_text(json.dumps(info), encoding="utf-8")
    assert not launch.current_frontend()


def test_runtime_outputs_are_ignored_but_acceptance_inputs_and_tests_are_tracked(
    project,
):
    initial = (
        service_fingerprint(project),
        frontend_fingerprint(project),
        verification_fingerprint(project),
    )
    (project / "runtime").mkdir()
    (project / "runtime/log.json").write_text('{"progress": 1}', encoding="utf-8")
    assert initial == (
        service_fingerprint(project),
        frontend_fingerprint(project),
        verification_fingerprint(project),
    )
    examples = project / "submission/examples"
    examples.mkdir(parents=True)
    (examples / "solve-result.json").write_text(
        '{"plan_id":"GENERATED"}', encoding="utf-8"
    )
    assert verification_fingerprint(project) == initial[2]
    (examples / "scenario-demo.json").write_text(
        '{"scenario_id":"INPUT"}', encoding="utf-8"
    )
    before_tests = verification_fingerprint(project)
    assert before_tests != initial[2]
    assert service_fingerprint(project) == initial[0]
    (project / "tests/new_test.py").write_text(
        "def test_case(): pass\n", encoding="utf-8"
    )
    assert verification_fingerprint(project) != before_tests
    assert service_fingerprint(project) == initial[0]
    (project / "solver/example.py").write_text("VALUE = 2\n", encoding="utf-8")
    assert service_fingerprint(project) != initial[0]


@pytest.mark.parametrize(
    "problem,expected", [("old_source", 1), ("other_runtime", 1), ("fresh", 0)]
)
def test_existing_service_is_reused_only_with_matching_code_and_data(
    project, monkeypatch, capsys, problem, expected
):
    identity = dict(
        service_id="yuanhang-rescue",
        workspace_id=launch.workspace_id(),
        runtime_id=launch.runtime_id(),
        service_source_sha256=service_fingerprint(project),
    )
    if problem == "old_source":
        identity["service_source_sha256"] = "outdated"
    elif problem == "other_runtime":
        identity["runtime_id"] = "another-dataset"
    monkeypatch.setattr(launch, "local_health", lambda port: identity)
    monkeypatch.setattr(launch, "ensure_frontend", lambda: True)

    def forbidden(*args, **kwargs):
        raise AssertionError("No existing service may be killed or respawned here.")

    monkeypatch.setattr(launch.subprocess, "Popen", forbidden)
    monkeypatch.setattr(sys, "argv", ["launch.py", "--port", "8123"])
    assert launch.main() == expected
    output = capsys.readouterr().out
    assert (
        "已在运行"
        if problem == "fresh"
        else "旧版" if problem == "old_source" else "数据目录"
    ) in output


def test_stale_frontend_rebuild_uses_installed_dependencies_without_installing(
    project, monkeypatch
):
    build(project)
    (project / "frontend/src/main.ts").write_text("NEW SOURCE", encoding="utf-8")
    (project / "frontend/node_modules/vite").mkdir(parents=True)
    node, original_run = shutil.which("node"), subprocess.run
    calls = []
    monkeypatch.setattr(launch.shutil, "which", lambda name: "npm")

    def local_build(command, **kwargs):
        calls.append(command)
        assert kwargs["env"]["npm_config_offline"] == "true"
        assert "install" not in command and "ci" not in command
        original_run(
            [node, str(BUILDER), "--write", str(project)],
            check=True,
            capture_output=True,
        )
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(launch.subprocess, "run", local_build)
    assert launch.ensure_frontend() and len(calls) == 1


def test_relative_runtime_is_resolved_against_project(project, monkeypatch):
    monkeypatch.setenv("YUANHANG_RUNTIME", ".local/another-runtime")
    assert launch.runtime_directory() == (project / ".local/another-runtime").resolve()
