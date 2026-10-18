"""Strict, additive V2 operation contracts. HTTP types derive from OpenAPI."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from zoneinfo import ZoneInfo

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator
from backend.app.generated.domain import (
    Base,
    Site,
    Demand,
    CargoItem,
    DroneType,
    Drone,
    Battery,
    Terrain,
    Policy,
    RestrictedZone,
    ResourceLimits,
    Communication,
    Scenario,
    SolveJob,
)


class OperationDTO(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class MissionDraft(OperationDTO):
    start_time: AwareDatetime
    timezone: str
    base: Base | None
    sites: list[Site]
    demands: list[Demand]
    cargo_items: list[CargoItem]
    drone_types: list[DroneType]
    drones: list[Drone]
    batteries: list[Battery]
    terrain: Terrain
    policy: Policy
    restricted_zones: list[RestrictedZone] | None = None
    resource_limits: ResourceLimits | None = None
    communication: Communication | None = None

    @field_validator("timezone")
    @classmethod
    def valid_zone(cls, value):
        ZoneInfo(value)
        return value


class MissionCreate(OperationDTO):
    name: str = Field(min_length=1, max_length=120)
    mode: Literal["simulation", "planning_assist"] = "simulation"
    template: Literal["blank", "compact", "contest"] = "blank"
    scenario_id: str | None = None
    idempotency_key: str = Field(min_length=1, max_length=128)


class MissionUpdate(OperationDTO):
    expected_revision: int = Field(ge=1)
    name: str | None = Field(default=None, min_length=1, max_length=120)
    archived: bool | None = None


class MissionDraftUpdate(OperationDTO):
    expected_revision: int = Field(ge=1)
    draft: MissionDraft
    publish: bool = False


class DraftImportPreview(OperationDTO):
    draft: MissionDraft
    row_count: int
    notices: list[str]


class MissionView(OperationDTO):
    mission_id: str
    name: str
    mode: Literal["simulation", "planning_assist"]
    timezone: str
    lifecycle: Literal[
        "draft", "planning", "ready", "executing", "paused", "completed", "archived"
    ]
    revision: int
    current_scenario_id: str | None
    active_plan_id: str | None
    active_execution_id: str | None
    draft: MissionDraft
    updated_at: AwareDatetime
    site_count: int
    cargo_count: int
    next_action: Literal["prepare", "plans", "execute", "review"]


class CheckItem(OperationDTO):
    code: str
    group: Literal[
        "map", "inventory", "fleet", "weather", "communication", "model", "execution"
    ]
    status: Literal["passed", "warning", "blocked", "unknown", "not_applicable"]
    message: str
    affected_objects: list[str] = Field(default_factory=list)
    field_path: str | None = None
    actual: float | None = None
    required: float | None = None
    unit: str | None = None
    action: Literal["region", "demand", "fleet", "checks", "plans", "settings"]
    source_ref: str


class PreflightRequest(OperationDTO):
    expected_revision: int = Field(ge=1)
    check_kind: Literal[
        "planning_readiness", "simulation_readiness", "real_dispatch"
    ] = "planning_readiness"
    plan_id: str | None = None


class PreflightReport(OperationDTO):
    report_id: str
    mission_id: str
    scenario_id: str | None
    state_version: int | None
    snapshot_id: str | None
    check_kind: str
    checks: list[CheckItem]
    blocking_count: int
    warning_count: int
    validity_fingerprint: str
    checked_at: AwareDatetime


class TrajectorySegment(OperationDTO):
    sortie_id: str
    drone_id: str
    phase_id: str
    phase: Literal[
        "prepare",
        "climb",
        "cruise",
        "descent",
        "handover",
        "turnaround",
        "charge_wait",
        "charge",
        "relay_link",
        "relay_service",
    ]
    start_s: float
    end_s: float
    from_coordinates: tuple[float, float]
    to_coordinates: tuple[float, float]
    start_elevation_m: float | None
    end_elevation_m: float | None
    vertical_datum: str | None
    payload_kg: float
    energy_kwh: float
    soc_start: float | None
    soc_end: float | None
    cargo_ids: list[str]


class SortieLoad(OperationDTO):
    sortie_id: str
    drone_id: str
    type_id: str
    cargo_count: int
    mass_kg: float
    volume_l: float
    max_payload_kg: float
    max_volume_l: float
    mass_utilization: float
    volume_utilization: float


class StageAnalysis(OperationDTO):
    plan_id: str
    snapshot_id: str
    analysis_version: Literal["stages-v1"] = "stages-v1"
    position_semantics: Literal["model_phase_geodesic"] = "model_phase_geodesic"
    soc_semantics: Literal["computed_phase_endpoints_only"] = (
        "computed_phase_endpoints_only"
    )
    trajectory_segments: list[TrajectorySegment]
    sortie_loads: list[SortieLoad] = Field(default_factory=list)


class ExecutionCreate(OperationDTO):
    mission_id: str
    confirmed_plan_id: str
    expected_revision: int = Field(ge=1)
    mode: Literal["simulation"] = "simulation"
    seed: int = Field(default=42, ge=0)
    idempotency_key: str = Field(min_length=1, max_length=128)


class SimulationAction(OperationDTO):
    action: Literal[
        "start", "pause", "resume", "speed", "advance", "disconnect", "reconnect"
    ]
    expected_revision: int = Field(ge=1)
    idempotency_key: str = Field(min_length=1, max_length=128)
    speed: float | None = Field(default=None, ge=0.1, le=100)
    target_time_s: float | None = Field(default=None, ge=0)


class ExecutionFact(OperationDTO):
    fact_id: str
    cursor: int
    time_s: float
    kind: Literal[
        "loaded",
        "takeoff",
        "delivered",
        "returned",
        "released",
        "battery_ready",
        "plan_adopted",
        "relay_started",
        "relay_arrived",
        "relay_service_started",
        "relay_service_ended",
        "relay_returned",
        "relay_released",
        "relay_energy_ready",
    ]
    plan_id: str
    sortie_id: str | None
    drone_id: str | None
    battery_id: str | None
    component_id: str | None = None
    cargo_ids: list[str]
    source: Literal["simulation"] = "simulation"


class TelemetrySample(OperationDTO):
    device_id: str
    device_session_id: str
    device_sequence: int
    observed_at: AwareDatetime
    received_at: AwareDatetime
    time_s: float
    coordinates: tuple[float, float] | None
    elevation_m: float | None
    vertical_datum: str | None
    soc: float | None
    soc_sample_time_s: float | None
    phase: str
    sortie_id: str | None
    battery_id: str | None = None
    component_id: str | None = None
    cargo_ids: list[str]
    quality: Literal["simulated", "stale", "missing"]
    active_plan_id: str


class ExecutionSchedulePart(OperationDTO):
    plan_id: str
    sortie_ids: list[str]
    relay_sortie_ids: list[str] = Field(default_factory=list)
    role: Literal["initial", "commitment", "future"]


class ExecutionView(OperationDTO):
    execution_id: str
    mission_id: str
    mode: Literal["simulation"]
    initial_plan_id: str
    desired_plan_id: str
    status: Literal["ready", "running", "paused", "completed"]
    revision: int
    facts_cursor: int
    time_s: float
    speed: float
    seed: int
    connected: bool
    schedule_parts: list[ExecutionSchedulePart]
    delivered_cargo_ids: list[str]
    facts: list[ExecutionFact]
    telemetry: list[TelemetrySample]
    created_at: AwareDatetime
    updated_at: AwareDatetime


class ExecutionEventInput(OperationDTO):
    event_id: str = Field(min_length=1, max_length=128)
    expected_revision: int = Field(ge=1)
    event_type: Literal[
        "drone.unavailable", "battery.unavailable", "demand.added", "site.unavailable"
    ]
    object_id: str | None = None
    demand: Demand | None = None
    cargo_items: list[CargoItem] = Field(default_factory=list, max_length=200)
    reason: str = Field(min_length=1, max_length=500)


class ExecutionEventView(OperationDTO):
    event_id: str
    execution_id: str
    event_type: str
    object_id: str | None
    reason: str
    time_s: float
    facts_cursor: int
    affected_sortie_ids: list[str]
    propagated_sortie_ids: list[str]
    preserved_sortie_ids: list[str]
    committed_sortie_ids: list[str]
    missing_inventory: int
    status: Literal["recorded", "requires_manual"]


class RepairRequest(OperationDTO):
    expected_revision: int = Field(ge=1)
    idempotency_key: str = Field(min_length=1, max_length=128)
    objective: Literal["time", "energy", "balanced"] = "time"
    time_limit_s: float = Field(default=10, ge=1, le=120)


class DeviceApplication(OperationDTO):
    device_id: str
    desired_plan_id: str | None
    active_plan_id: str
    upload_state: Literal["queued", "acknowledged", "succeeded", "indeterminate"]
    activation_state: Literal["not_started", "active", "indeterminate"]
    command_id: str


class RepairView(OperationDTO):
    change_id: str
    execution_id: str
    execution_revision: int
    facts_cursor: int
    event_fingerprint: str
    committed_parts: list[ExecutionSchedulePart]
    committed_cargo_ids: list[str]
    future_not_before_s: float
    job: SolveJob | None
    candidate_plan_id: str | None
    status: Literal[
        "computing",
        "ready",
        "no_remaining",
        "applying",
        "failed",
        "partially_applied",
        "applied",
    ]
    message: str
    changed_cargo_ids: list[str]
    retained_cargo_ids: list[str]
    applications: list[DeviceApplication] = Field(default_factory=list)


class ApplyRepair(OperationDTO):
    expected_revision: int = Field(ge=1)
    idempotency_key: str = Field(min_length=1, max_length=128)
    # Fault injection is restricted to the SimulationAdapter.
    ack_timeout_device_ids: list[str] = Field(default_factory=list, max_length=20)


class DeviceCapabilities(OperationDTO):
    device_id: str
    adapter: Literal["simulation"] = "simulation"
    mode: Literal["simulation"] = "simulation"
    supports_upload: Literal[True] = True
    supports_inflight_replacement: Literal[False] = False
    supports_future_schedule_update: Literal[True] = True
    command_types: list[Literal["mission.upload", "mission.activate", "state.query"]]
    real_device_connected: Literal[False] = False


class CommandRequest(OperationDTO):
    execution_id: str
    device_id: str
    command_type: Literal["mission.upload", "mission.activate", "state.query"]
    desired_plan_id: str
    expected_execution_revision: int = Field(ge=1)
    idempotency_key: str = Field(min_length=1, max_length=128)
    expires_at: AwareDatetime
    simulation_fault: Literal["none", "reject", "ack_timeout", "completion_timeout"] = (
        "none"
    )


class CommandView(OperationDTO):
    command_id: str
    execution_id: str
    device_id: str
    command_type: str
    mode: Literal["simulation"] = "simulation"
    status: Literal[
        "queued",
        "sent",
        "acknowledged",
        "succeeded",
        "rejected",
        "expired",
        "indeterminate",
    ]
    desired_plan_id: str
    created_at: AwareDatetime
    expires_at: AwareDatetime
    acknowledged_at: AwareDatetime | None
    completed_at: AwareDatetime | None
    evidence: str | None


class DeliveryDeviation(OperationDTO):
    cargo_id: str
    plan_id: str
    sortie_id: str
    initial_expected_s: float | None
    delivered_s: float
    difference_s: float | None


class ExecutionAnalysis(OperationDTO):
    execution_id: str
    facts_cursor: int
    source: Literal["simulation"] = "simulation"
    allocated_quantity: int
    delivered_quantity: int
    unserved_quantity: int
    delivery_rows: list[ExecutionFact]
    initial_plan_id: str
    active_plan_ids: list[str]
    event_count: int
    change_count: int
    deviation_rows: list[DeliveryDeviation] = Field(default_factory=list)


class OperationCapabilities(OperationDTO):
    modes: list[Literal["simulation"]]
    real_dispatch: Literal[False] = False
    sitl: Literal[False] = False
    persistent_simulation: Literal[True] = True
    commitment_repair: Literal["transport_committed_prefix_future_only"] = (
        "transport_committed_prefix_future_only"
    )
    relay_simulation: Literal[True] = True
    weather_information: Literal[False] = False
    weather_thresholds: Literal[False] = False
    weather_energy: Literal[False] = False
    learning_search: Literal[False] = False
    position_source: Literal["business_model_phases"] = "business_model_phases"
