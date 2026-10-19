"""One-time RFC-032 additive contract migration; does not touch runtime documents."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def update(name, properties):
    path = ROOT / "contracts" / (name + ".schema.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    data["properties"].update(properties)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


update(
    "solver-options",
    {
        "engine_type": {
            "enum": ["standard", "eoh"],
            "description": "Optional; absence preserves standard engine and old Plan shape.",
        },
        "heuristic_policy_id": {
            "type": ["string", "null"],
            "pattern": "^[A-Za-z0-9_-]{1,80}$",
        },
        "heuristic_policy_sha256": {
            "type": ["string", "null"],
            "pattern": "^[a-f0-9]{64}$",
        },
    },
)
nullable = lambda t: {"type": [t, "null"]}
update(
    "plan",
    {
        "engine": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "engine_type": {"enum": ["standard", "eoh"]},
                "policy_id": nullable("string"),
                "version": nullable("string"),
                "origin": {"enum": ["standard", "rule_initialization", "eoh_offline"]},
                "sha256": {"type": ["string", "null"], "pattern": "^[a-f0-9]{64}$"},
                "ranking_evaluations": {"type": "integer", "minimum": 0},
                "fallback_evaluations": {"type": "integer", "minimum": 0},
            },
            "required": [
                "engine_type",
                "policy_id",
                "version",
                "origin",
                "sha256",
                "ranking_evaluations",
                "fallback_evaluations",
            ],
        }
    },
)
