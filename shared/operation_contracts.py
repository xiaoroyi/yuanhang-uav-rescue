"""Pure operation-contract validation without importing HTTP or database modules."""

from functools import lru_cache
import json

from jsonschema import Draft202012Validator

from shared.contracts import ROOT, FORMAT, ContractError


@lru_cache(maxsize=16)
def validator(name):
    path = ROOT / "contracts" / "operations" / "v2.schema.json"
    schema = json.loads(path.read_text(encoding="utf-8"))
    if name not in schema["$defs"]:
        raise ContractError("未知操作合同：" + name)
    return Draft202012Validator(
        {"$ref": "#/$defs/" + name, "$defs": schema["$defs"]},
        format_checker=FORMAT,
    )


def validate_operation(name, value):
    failure = next(validator(name).iter_errors(value), None)
    if failure:
        raise ContractError(f"{name}: {failure.message}")
