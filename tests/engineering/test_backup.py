from contextlib import closing
import sqlite3
import time
import warnings
import zipfile

from fastapi.testclient import TestClient
import pytest

from backend.app.main import create_app
from scripts.backup import create_backup, inspect_archive, restore_backup


@pytest.fixture
def small_backup(tmp_path):
    runtime = tmp_path / "source"
    (runtime / "assets" / "DEM-test").mkdir(parents=True)
    (runtime / "assets/DEM-test/source.json").write_text(
        '{"example": true}', encoding="utf-8"
    )
    with closing(sqlite3.connect(runtime / "yuanhang.sqlite3")) as database:
        database.execute("CREATE TABLE sample(value TEXT)")
        database.execute("INSERT INTO sample VALUES ('original')")
        database.commit()
    archive, manifest = create_backup(runtime)
    return runtime, archive, manifest


def test_live_wal_database_backup_preserves_committed_rows_and_can_be_restored(
    tmp_path,
):
    runtime = tmp_path / "live"
    with TestClient(create_app(runtime)) as client:
        scene = client.post(
            "/api/v1/scenarios/examples", json={"example": "compact"}
        ).json()
        sid = scene["scenario_id"]
        snapshot = client.post(
            f"/api/v1/scenarios/{sid}/snapshots", json={"expected_state_version": 1}
        ).json()
        job = client.post(
            "/api/v1/solve-jobs",
            json={"snapshot_id": snapshot["snapshot_id"], "time_limit_s": 5},
        ).json()
        until = time.monotonic() + 30
        while time.monotonic() < until:
            job = client.get(f"/api/v1/solve-jobs/{job['job_id']}").json()
            if job["job_state"] not in ("queued", "running"):
                break
            time.sleep(0.05)
        assert job["has_validated_plan"], job
        plan = client.get(f"/api/v1/plans/{job['plan_id']}").json()
        with closing(sqlite3.connect(runtime / "yuanhang.sqlite3")) as live:
            live.execute("PRAGMA journal_mode=WAL")
            live.execute("CREATE TABLE latest_wal(value TEXT)")
            live.execute("INSERT INTO latest_wal VALUES ('committed-in-WAL')")
            live.commit()
            assert (runtime / "yuanhang.sqlite3-wal").exists()
            archive, manifest = create_backup(runtime)
            assert manifest["table_counts"]["latest_wal"] == 1
            assert manifest["table_counts"]["plans"] == 1
            assert not list((runtime / "backups").glob(".backup-db-*"))
            restored = tmp_path / "restored"
            restore_backup(archive, restored)
            with closing(sqlite3.connect(restored / "yuanhang.sqlite3")) as copy:
                assert (
                    copy.execute("SELECT value FROM latest_wal").fetchone()[0]
                    == "committed-in-WAL"
                )
        with TestClient(create_app(restored)) as restored_client:
            assert restored_client.get(f"/api/v1/scenarios/{sid}").json() == scene
            assert (
                restored_client.get(
                    f"/api/v1/snapshots/{snapshot['snapshot_id']}"
                ).json()
                == snapshot
            )
            assert (
                restored_client.get(f"/api/v1/plans/{plan['plan_id']}").json() == plan
            )


def test_asset_bytes_and_database_counts_roundtrip_without_recursive_backups(
    small_backup, tmp_path
):
    source, archive, manifest = small_backup
    assert inspect_archive(archive) == manifest
    assert {row["path"] for row in manifest["files"]} == {
        "yuanhang.sqlite3",
        "assets/DEM-test/source.json",
    }
    second, again = create_backup(source)
    assert archive != second and len(again["files"]) == len(manifest["files"])
    destination = tmp_path / "new-runtime"
    restore_backup(archive, destination)
    assert (destination / "assets/DEM-test/source.json").read_bytes() == (
        source / "assets/DEM-test/source.json"
    ).read_bytes()


def test_restore_never_overwrites_an_existing_data_directory(small_backup, tmp_path):
    _, archive, _ = small_backup
    destination = tmp_path / "existing"
    destination.mkdir()
    sentinel = destination / "keep.txt"
    sentinel.write_text("preserve", encoding="utf-8")
    with pytest.raises(ValueError, match="已存在"):
        restore_backup(archive, destination)
    assert sentinel.read_text(encoding="utf-8") == "preserve"


@pytest.mark.parametrize("problem", ["hash", "traversal", "duplicate", "unlisted"])
def test_malformed_archives_are_rejected_before_any_restore_write(
    small_backup, tmp_path, problem
):
    _, archive, _ = small_backup
    bad = tmp_path / "bad.zip"
    with zipfile.ZipFile(archive) as source, zipfile.ZipFile(bad, "w") as output:
        for info in source.infolist():
            content = source.read(info.filename)
            if problem == "hash" and info.filename == "yuanhang.sqlite3":
                content += b"altered"
            output.writestr(info.filename, content)
        if problem == "traversal":
            output.writestr("../escaped.txt", "never extract")
        elif problem == "duplicate":
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                output.writestr("manifest.json", "{}")
        elif problem == "unlisted":
            output.writestr("assets/unlisted.txt", "not in manifest")
    destination = tmp_path / "should-not-exist"
    with pytest.raises(ValueError):
        restore_backup(bad, destination)
    assert not destination.exists() and not (tmp_path / "escaped.txt").exists()
