"""Strict, additive V2 operation contracts. HTTP types derive from OpenAPI."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from zoneinfo import ZoneInfo

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StrictInt,
    field_validator,
)
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
    Weather,
    Plan,
    Snapshot,
    Diagnostic,
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
    weather: Weather | None = None

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
    availability: Literal["available", "not_ready", "unavailable"] | None = None
    availability_reason: str | None = None
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
    applied_event_ids: list[str] = Field(default_factory=list)
    facts: list[ExecutionFact]
    telemetry: list[TelemetrySample]
    created_at: AwareDatetime
    updated_at: AwareDatetime


class ExecutionEventInput(OperationDTO):
    event_id: str = Field(min_length=1, max_length=128)
    expected_revision: int = Field(ge=1)
    event_type: Literal[
        "drone.unavailable",
        "battery.unavailable",
        "demand.added",
        "site.unavailable",
        "weather.changed",
    ]
    object_id: str | None = None
    demand: Demand | None = None
    cargo_items: list[CargoItem] = Field(default_factory=list, max_length=200)
    weather: Weather | None = None
    reason: str = Field(min_length=1, max_length=500)


class ImpactNode(OperationDTO):
    node_id: str
    plan_id: str
    sortie_id: str
    drone_id: str
    battery_id: str
    cargo_ids: list[str]
    prepare_start_s: float
    takeoff_s: float
    return_s: float
    drone_released_s: float
    battery_released_s: float
    direct: bool
    affected: bool
    committed: bool


class ImpactEdge(OperationDTO):
    from_node_id: str
    to_node_id: str
    resource_kind: Literal["drone", "battery"]
    resource_id: str


class ExecutionImpact(OperationDTO):
    scope: Literal["frozen_transport_resource_precedence"]
    time_s: float
    facts_cursor: int
    ground_model: Literal["unlimited", "conservative_common_release"]
    nodes: list[ImpactNode]
    edges: list[ImpactEdge]


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
    status: Literal["recorded", "requires_manual", "withdrawn"]
    weather: Weather | None = None
    resolved_at: AwareDatetime | None = None
    resolution_reason: str | None = None
    impact: ExecutionImpact | None = None


class EventResolution(OperationDTO):
    expected_revision: int = Field(ge=1)
    idempotency_key: str = Field(min_length=1, max_length=128)
    action: Literal["withdraw_misreport"]
    reason: str = Field(min_length=10, max_length=500)


class RepairRequest(OperationDTO):
    expected_revision: int = Field(ge=1)
    idempotency_key: str = Field(min_length=1, max_length=128)
    objective: Literal["time", "energy", "balanced"] = "time"
    time_limit_s: float = Field(default=10, ge=1, le=120)
    repair_policy: Literal["dependency", "full"] = "dependency"


class DeviceApplication(OperationDTO):
    device_id: str
    desired_plan_id: str | None
    active_plan_id: str
    upload_state: Literal[
        "queued", "acknowledged", "succeeded", "indeterminate", "expired", "rejected"
    ]
    activation_state: Literal["not_started", "active", "indeterminate"]
    command_id: str
    activation_command_id: str | None = None


class CargoRepairDifference(OperationDTO):
    cargo_id: str
    previous_plan_id: str | None
    previous_sortie_id: str | None
    previous_drone_id: str | None
    previous_battery_id: str | None
    candidate_sortie_id: str
    candidate_drone_id: str
    candidate_battery_id: str
    change_kind: Literal["new", "unchanged", "modified"]
    drone_changed: bool | None
    battery_changed: bool | None
    takeoff_delta_s: float | None
    delivery_delta_s: float | None


class RepairDifference(OperationDTO):
    committed_quantity: int = Field(ge=0)
    retained_future_sortie_count: int = Field(ge=0)
    drone_reassigned_quantity: int = Field(ge=0)
    battery_reassigned_quantity: int = Field(ge=0)
    time_shifted_quantity: int = Field(ge=0)
    unchanged_future_quantity: int = Field(ge=0)
    new_quantity: int = Field(ge=0)
    rows: list[CargoRepairDifference]


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
    repair_policy: Literal["dependency", "full"] | None = None
    calculation_method: Literal["dependency_local", "full_recompute"] | None = None
    repair_reference_id: str | None = None
    diff: RepairDifference | None = None


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


class DeviceMissionState(OperationDTO):
    execution_id: str
    device_id: str
    mode: Literal["simulation"] = "simulation"
    revision: int = Field(ge=1)
    active_plan_id: str
    uploaded_plan_id: str | None
    uploaded_content_sha256: str | None = Field(default=None, pattern="^[a-f0-9]{64}$")
    last_upload_command_id: str | None = None
    last_activation_command_id: str | None = None
    updated_at: AwareDatetime
    observed_at: AwareDatetime
    real_device_connected: Literal[False] = False


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
    observed_state: DeviceMissionState | None = None


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
    weather_information: Literal[True] = True
    weather_thresholds: Literal[True] = True
    weather_energy: Literal[False] = False
    learning_search: Literal[False] = False
    position_source: Literal["business_model_phases"] = "business_model_phases"


class FrozenDocument(OperationDTO):
    kind: Literal[
        "plan", "snapshot", "event_input", "event_resolution", "repair_reference"
    ]
    document_id: str = Field(min_length=1, max_length=256)
    # Exact UTF-8 JSON preserves absent fields and original Snapshot content hashes.
    payload_json: str = Field(max_length=4_000_000)
    sha256: str = Field(pattern="^[a-f0-9]{64}$")


class ExecutionBundle(OperationDTO):
    bundle_version: Literal["execution-simulation-v2"]
    source: Literal["simulation"]
    is_flight_controller_file: Literal[False]
    captured_at: AwareDatetime
    mission_name: str = Field(max_length=128)
    execution: ExecutionView
    events: list[ExecutionEventView]
    changes: list[RepairView]
    commands: list[CommandView]
    documents: list[FrozenDocument] = Field(max_length=2000)
    content_sha256: str = Field(pattern="^[a-f0-9]{64}$")


class ExecutionArchiveSummary(OperationDTO):
    archive_id: str
    execution_id: str
    mission_name: str
    imported_at: AwareDatetime
    captured_at: AwareDatetime
    captured_time_s: float
    captured_status: str
    fact_count: int
    plan_count: int
    content_sha256: str
    read_only: Literal[True] = True


class ExecutionArchiveView(OperationDTO):
    summary: ExecutionArchiveSummary
    bundle: ExecutionBundle
    plans: list[Plan]
    snapshots: list[Snapshot]
    analysis: ExecutionAnalysis


class ExperimentRequest(OperationDTO):
    name: str = Field(min_length=1, max_length=160)
    source_snapshot_id: str
    suite: Literal["strategy", "search"]
    objective: Literal["time", "energy", "balanced"] = "time"
    objective_policy: Literal["deadline_first_v1", "tradeoff_v2"] = "tradeoff_v2"
    seeds: list[StrictInt] = Field(min_length=1, max_length=3)
    time_limit_s: float = Field(ge=1, le=30)
    idempotency_key: str = Field(min_length=1, max_length=128)

    @field_validator("seeds")
    @classmethod
    def distinct_seeds(cls, value):
        if len(set(value)) != len(value) or any(v < 0 or v > 2147483647 for v in value):
            raise ValueError("seeds须为不重复的0至2147483647整数。")
        return value


class ExperimentEnvironment(OperationDTO):
    service_source_sha256: str
    git_commit: str | None
    git_worktree_dirty: bool
    python_version: str
    platform: str
    processor: str | None
    logical_cpu_count: int | None
    ortools_version: str
    numpy_version: str
    worker_serial_limit: Literal[1] = 1
    cp_sat_threads: Literal[1] = 1
    cache_policy: str


class ExperimentCase(OperationDTO):
    case_id: str
    method: Literal["quick", "improve"]
    objective: Literal["time", "energy", "balanced"]
    seed: int
    time_limit_s: float
    status: Literal[
        "queued", "dispatching", "running", "completed", "failed", "canceled"
    ]
    job: SolveJob | None
    first_feasible_s: float | None
    candidate_count: int | None
    runtime_s: float | None
    energy_kwh: float | None
    makespan_s: float | None
    last_delivery_s: float | None
    weighted_tardiness_s: float | None
    min_return_soc: float | None
    allocated_quantity: int | None
    model_scope: list[str]
    validation_status: str | None
    diagnostics: list[Diagnostic]
    message: str | None


class ExperimentGroup(OperationDTO):
    method: str
    objective: str
    total: int
    finished: int
    feasible: int
    failed_or_unvalidated: int
    canceled: int
    runtime_sample_count: int
    runtime_p50_s: float | None
    runtime_p95_s: float | None
    feasible_energy_median_kwh: float | None
    feasible_makespan_median_s: float | None


class ExperimentView(OperationDTO):
    experiment_id: str
    name: str
    source_snapshot_id: str
    source_content_hash: str
    snapshot_id: str
    snapshot_content_hash: str
    data_origin: str
    suite: Literal["strategy", "search"]
    objective_policy: Literal["deadline_first_v1", "tradeoff_v2"]
    status: Literal["queued", "running", "completed", "canceled"]
    cancel_requested: bool
    created_at: AwareDatetime
    finished_at: AwareDatetime | None
    environment: ExperimentEnvironment
    cases: list[ExperimentCase]
    groups: list[ExperimentGroup]
    message: str


class ExperimentArtifact(OperationDTO):
    case_id: str
    name: Literal["input.json", "outcome.json", "progress.json", "worker.log"]
    byte_count: int
    content_sha256: str
    content_base64: str


class ExperimentBundle(OperationDTO):
    bundle_version: Literal["experiment-v1"] = "experiment-v1"
    captured_at: AwareDatetime
    run: ExperimentView
    documents: list[FrozenDocument]
    artifacts: list[ExperimentArtifact]
    missing_artifacts: list[str]
    content_sha256: str


class ExecutionRepairReference(OperationDTO):
    reference_version: Literal["execution-remaining-v1"]
    execution_id: str
    execution_revision: int = Field(ge=1)
    facts_cursor: int = Field(ge=0)
    input_snapshot_id: str
    repair_policy: Literal["dependency", "full"]
    force_full: bool
    committed_cargo_ids: list[str]
    future_parts: list[ExecutionSchedulePart]
    documents: list[FrozenDocument]
