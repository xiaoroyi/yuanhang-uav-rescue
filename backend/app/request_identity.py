"""Explicit compatibility for additive request fields, without relaxing changed payloads."""

from backend.app.operation_models import (
    ExperimentRequest,
    ExecutionEventInput,
    RepairRequest,
)
from shared.contracts import content_hash


def request_hashes(body):
    value = body.model_dump(mode="json")
    primary = content_hash(value)
    compatible = {primary}
    if isinstance(body, ExperimentRequest) and body.repair_reference_id is None:
        compatible.add(
            content_hash({k: v for k, v in value.items() if k != "repair_reference_id"})
        )
    if isinstance(body, ExecutionEventInput) and body.weather is None:
        compatible.add(content_hash({k: v for k, v in value.items() if k != "weather"}))
    if isinstance(body, RepairRequest) and (
        "repair_policy" not in body.model_fields_set or body.repair_policy == "full"
    ):
        # Pre-RFC026 repairs always recomputed fully. An explicit new dependency
        # request cannot reinterpret that old receipt, even when other fields match.
        compatible.add(
            content_hash({k: v for k, v in value.items() if k != "repair_policy"})
        )
    return primary, compatible
