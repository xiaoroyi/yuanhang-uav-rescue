"""Snapshot-bound necessary capacity diagnostics, separate from Plan feasibility."""

from typing import Literal
from pydantic import BaseModel, ConfigDict


class BoundDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")


class BoundWitness(BoundDTO):
    demand_id: str
    required_quantity: int
    mass_min_kg: float
    volume_min_l: float
    mass_cargo_ids: list[str]
    volume_cargo_ids: list[str]


class CapacityBound(BoundDTO):
    model_id: Literal["transport_capacity_relaxation_v1"]
    status: Literal["ready", "limited"]
    reason: str | None
    snapshot_id: str
    scenario_state_version: int
    snapshot_content_hash: str
    required_box_count: int
    eligible_type_ids: list[str]
    max_payload_kg: float | None
    max_volume_l: float | None
    mass_min_kg: float | None
    volume_min_l: float | None
    mass_bound: int | None
    volume_bound: int | None
    sortie_lower_bound: int | None
    exact: dict[str, str]
    witnesses: list[BoundWitness]
    numeric_policy: str
    notes: list[str]
