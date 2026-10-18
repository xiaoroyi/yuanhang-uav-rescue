"""Export the additive operation contract from its strict runtime models."""

import inspect
import json
from pathlib import Path
import sys
from pydantic.json_schema import models_json_schema

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.app import operation_models as ops

models = [
    (m, "validation")
    for _, m in inspect.getmembers(ops, inspect.isclass)
    if m.__module__ == ops.__name__ and m is not ops.OperationDTO
]
_, schema = models_json_schema(models, title="Yuanhang additive operations v2")
schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
schema["$id"] = "https://yuanhang.example/contracts/operations/v2.schema.json"
target = ROOT / "contracts/operations/v2.schema.json"
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(
    json.dumps(schema, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
    newline="\n",
)
print(f"Exported {len(models)} strict operation models")
