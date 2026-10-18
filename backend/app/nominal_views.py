"""RFC-009 diagnostic DTOs. These are deliberately separate from executable Plans."""

from typing import Literal

from pydantic import BaseModel, ConfigDict


class NominalDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")


class NominalMetrics(NominalDTO):
    sortie_count: int
    energy_kwh: float
    operation_s: float
    min_return_soc: float | None


class NominalParameters(NominalDTO):
    min_return_soc: float
    nominal_soc: float
    nominal_soh: float
    max_count_states_per_site: int
    priority: list[str]


class NominalCapacity(NominalDTO):
    site_id: str
    type_id: str
    capacity_kg: float | None
    max_volume_l: float
    nominal_energy_kwh: float | None
    allowed_energy_kwh: float | None
    empty_energy_kwh: float | None
    full_energy_kwh: float | None
    roundtrip_distance_m: float | None
    terrain_evaluated: bool
    limit: Literal["empty_infeasible", "rated_payload", "energy", "unavailable"]
    root_width_kg: float | None
    residual_kwh: float | None
    reason: str | None


class NominalBatch(NominalDTO):
    batch_id: str
    site_id: str
    type_id: str
    cargo_ids: list[str]
    mass_kg: float
    volume_l: float
    duration_s: float
    energy_kwh: float
    return_soc: float


class NominalSite(NominalDTO):
    site_id: str
    status: Literal["complete", "limited", "infeasible"]
    reason: str | None
    count_states: int
    box_count: int
    metrics: NominalMetrics | None


class NominalSensitivity(NominalDTO):
    min_return_soc: float
    status: Literal["complete", "partial"]
    metrics: NominalMetrics | None


class NominalReport(NominalDTO):
    model_id: Literal["single_site_nominal_transport_v1"]
    status: Literal["limited", "partial", "complete"]
    reason: str | None
    snapshot_id: str
    scenario_id: str
    scenario_state_version: int
    snapshot_content_hash: str
    required_box_count: int
    available_box_count: int
    parameters: NominalParameters
    analysis_input_hash: str
    capacities: list[NominalCapacity]
    sites: list[NominalSite]
    batches: list[NominalBatch]
    metrics: NominalMetrics | None
    single_box_baseline: NominalMetrics | None
    greedy_baseline: NominalMetrics | None
    sensitivity: list[NominalSensitivity]
    audit_checks: list[str]
    runtime_s: float
    notes: list[str]
