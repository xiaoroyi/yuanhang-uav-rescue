"""HTTP views for immutable, frozen-task partition diagnostics (RFC-007)."""

from typing import Literal

from pydantic import BaseModel, ConfigDict


class PartitionDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PartitionAssignment(PartitionDTO):
    task_id: str
    start_s: float
    end_s: float
    original_resource_id: str
    allocated_resource_id: str
    needs_addition: bool


class PartitionResourcePeak(PartitionDTO):
    resource_key: str
    required_count: int
    peak_at_s: float | None
    peak_task_ids: list[str]
    assignments: list[PartitionAssignment]


class PartitionGroup(PartitionDTO):
    group_id: str
    atom_ids: list[str]
    site_ids: list[str]
    transport_sortie_ids: list[str]
    relay_sortie_ids: list[str]
    box_count: int
    workload_s: float
    resources: list[PartitionResourcePeak]


class PartitionConfiguration(PartitionDTO):
    resource_key: str
    inventory: int
    pooled_required: int
    partition_required: int
    extra_vs_pool: int
    shortfall: int
    unallocated_stock: int


class PartitionCandidate(PartitionDTO):
    groups: list[PartitionGroup]
    configuration: list[PartitionConfiguration]
    normalized_deficit: float
    normalized_size: float
    workload_cv2: float
    objective_exact: dict[str, str]
    fits_inventory: bool


class PartitionVariant(PartitionDTO):
    group_count: Literal[2, 3]
    candidate_count: int
    status: Literal["available", "not_possible"]
    reason: str | None
    resource_first: PartitionCandidate | None
    balanced_first: PartitionCandidate | None


class PartitionAtom(PartitionDTO):
    atom_id: str
    site_ids: list[str]
    transport_sortie_ids: list[str]
    relay_sortie_ids: list[str]


class PartitionEdge(PartitionDTO):
    kind: Literal["transport", "relay"]
    task_id: str
    site_ids: list[str]


class PartitionResourceClass(PartitionDTO):
    key: str
    kind: Literal["drone", "battery", "relay_drone", "relay_energy", "prep", "charger"]
    type_id: str
    label: str
    inventory: int


class PartitionPooledRequirement(PartitionDTO):
    resource_key: str
    required_count: int


class PartitionReport(PartitionDTO):
    model_id: Literal["frozen_joint_homogeneous_v1"]
    status: Literal["ready", "limited"]
    reason: str | None
    plan_id: str
    snapshot_id: str
    scenario_state_version: int
    snapshot_content_hash: str
    source_plan_hash: str
    max_atoms: int
    atoms: list[PartitionAtom]
    edges: list[PartitionEdge]
    resource_classes: list[PartitionResourceClass]
    pooled_requirements: list[PartitionPooledRequirement]
    variants: list[PartitionVariant]
    audit_checks: list[str]
    notes: list[str]
