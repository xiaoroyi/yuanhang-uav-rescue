import json
from pathlib import Path

from jsonschema import Draft202012Validator
from pydantic import ValidationError
import pytest

from backend.app import operation_models


def test_operation_examples_match_strict_python_and_json_schema():
    root = Path(__file__).resolve().parents[1]
    schema = json.loads(
        (root / "contracts/operations/v2.schema.json").read_text(encoding="utf-8")
    )
    fixtures = json.loads(
        (root / "fixtures/operations/v2.json").read_text(encoding="utf-8")
    )
    assert fixtures["meta"]["data_origin"] == "mock"
    for valid, cases in [(True, fixtures["valid"]), (False, fixtures["invalid"])]:
        for case in cases:
            model = getattr(operation_models, case["model"])
            scoped = {**schema, "$ref": "#/$defs/" + case["model"]}
            errors = list(Draft202012Validator(scoped).iter_errors(case["data"]))
            assert (not errors) == valid, case
            if valid:
                model.model_validate(case["data"])
            else:
                with pytest.raises(ValidationError):
                    model.model_validate(case["data"])
