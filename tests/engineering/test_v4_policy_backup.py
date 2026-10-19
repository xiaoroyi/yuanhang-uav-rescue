import json
from pathlib import Path
import sqlite3
from scripts.backup import create_backup, inspect_archive, restore_backup
from solver.engines import read_policy, policy_store


def test_local_policy_identity_survives_backup_and_restore(tmp_path):
    source = tmp_path / "runtime"
    policies = source / "heuristics"
    policies.mkdir(parents=True)
    value = json.loads(
        Path("solver/policies/eoh-seed-v1.json").read_text(encoding="utf-8")
    )
    value["policy_id"] = "saved-v1"
    (policies / "saved-v1.json").write_text(json.dumps(value), encoding="utf-8")
    with sqlite3.connect(source / "yuanhang.sqlite3") as db:
        db.execute("CREATE TABLE sample(value TEXT)")
    with policy_store(policies):
        digest = read_policy("saved-v1")[1]
    archive, manifest = create_backup(source)
    assert "heuristics/saved-v1.json" in {r["path"] for r in manifest["files"]}
    assert inspect_archive(archive) == manifest
    destination = tmp_path / "restored"
    restore_backup(archive, destination)
    with policy_store(destination / "heuristics"):
        assert read_policy("saved-v1")[1] == digest
