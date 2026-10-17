"""Typed HTTP views and explicit, reproducible what-if transformations."""

from __future__ import annotations

import copy
from typing import Literal
import uuid

from pydantic import BaseModel, ConfigDict, Field

from backend.app.generated.domain import Scenario, Plan, SolveJob, ResourceLimits
from backend.app.bound_views import CapacityBound


class DTO(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DemandDelivery(DTO):
    demand_id: str
    site_id: str
    required_quantity: int
    served_quantity: int
    complete_s: float | None
    expected_deadline_s: float | None
    hard_deadline_s: float | None
    delay_s: float | None
    hard_satisfied: bool | None


class DeliveryAnalysis(DTO):
    demands: list[DemandDelivery]
    weighted_box_delay_s: float
    late_demand_count: int
    expected_demand_count: int
    hard_violation_count: int


class ResourceUsage(DTO):
    kind: Literal["drone", "battery", "relay_drone", "relay_energy"]
    resource_id: str
    type_id: str
    sortie_count: int
    occupied_s: float
    flight_s: float
    energy_kwh: float
    horizon_s: float
    utilization: float


class ChargeWindow(DTO):
    battery_id: str
    type_id: str
    start_s: float
    end_s: float
    is_initial: bool
    sortie_id: str | None


class PlanAnalysis(DTO):
    plan_id: str
    snapshot_id: str
    scenario_state_version: int
    model_scope: list[str]
    capacity_bound: CapacityBound | None = None
    resource_limits: ResourceLimits | None
    prep_peak: int
    charge_wait_s: float
    delivery: DeliveryAnalysis
    resources: list[ResourceUsage]
    charge_windows: list[ChargeWindow]
    charge_peak: int
    charge_peak_by_type: dict[str, int]
    min_hard_slack_s: float | None
    notes: list[str]


class ResourceAddition(DTO):
    type_id: str
    drones: int = Field(default=0, ge=0, le=4)
    batteries: int = Field(default=0, ge=0, le=8)
    battery_capacity_kwh: float | None = Field(default=None, gt=0)


class WhatIfRequest(DTO):
    expected_state_version: int = Field(ge=1)
    source_plan_id: str | None = None
    name: str = Field(default="资源与余量试算", min_length=1, max_length=120)
    additions: list[ResourceAddition] = Field(default_factory=list, max_length=3)
    energy_multiplier: float = Field(default=1, ge=0.25, le=4)
    flight_time_multiplier: float = Field(default=1, ge=0.25, le=4)
    battery_soh_multiplier: float = Field(default=1, ge=0.1, le=1)
    min_return_soc: float | None = Field(default=None, ge=0, le=1)
    noncritical_deadline_multiplier: float = Field(default=1, ge=1, le=3)


class ScenarioOrigin(DTO):
    kind: Literal["what_if"] = "what_if"
    source_scenario_id: str
    source_state_version: int
    source_content_hash: str
    source_plan_id: str | None
    transformation_version: Literal["what_if_v1"] = "what_if_v1"
    parameters: WhatIfRequest
    changes: list[str]


class WhatIfReceipt(DTO):
    scenario: Scenario
    origin: ScenarioOrigin


class WhatIfHistory(DTO):
    scenario_id: str
    name: str
    scenario_state_version: int
    origin: ScenarioOrigin
    job: SolveJob | None
    plan: Plan | None


def transform(source, request: WhatIfRequest):
    s = copy.deepcopy(source)
    s["name"] = source["name"] + " · " + request.name
    s["name"] = s["name"][:200]
    s["data_origin"] = "user_input"
    types = {t["type_id"]: t for t in s["drone_types"]}
    changes = []
    for addition in request.additions:
        if addition.type_id not in types:
            raise ValueError("增配引用了不存在的机型：" + addition.type_id)
        for _ in range(addition.drones):
            s["drones"].append(
                {
                    "drone_id": "WHAT-U-" + uuid.uuid4().hex[:10].upper(),
                    "type_id": addition.type_id,
                    "status": "available",
                    "location_id": s["base"]["id"],
                    "available_after_s": 0,
                }
            )
        template = next(
            (b for b in s["batteries"] if b["compatible_type_id"] == addition.type_id),
            None,
        )
        capacity = (
            addition.battery_capacity_kwh
            if addition.battery_capacity_kwh is not None
            else template["capacity_kwh"] if template else None
        )
        if addition.batteries and capacity is None:
            raise ValueError(
                "新增电池没有同型参考容量，请明确填写battery_capacity_kwh。"
            )
        for _ in range(addition.batteries):
            s["batteries"].append(
                {
                    "battery_id": "WHAT-B-" + uuid.uuid4().hex[:10].upper(),
                    "compatible_type_id": addition.type_id,
                    "capacity_kwh": capacity,
                    "soc": 1,
                    "soh": 1,
                    "status": "available",
                    "location_id": s["base"]["id"],
                    "available_after_s": 0,
                }
            )
        if addition.drones or addition.batteries:
            changes.append(
                f"{addition.type_id}型增加{addition.drones}架机体、{addition.batteries}块电池；新增实体按满电/健康状态假设。"
            )
    for t in s["drone_types"]:
        parameters = t["energy_model"]["parameters"]
        parameters["energy_scale"] = (
            parameters.get("energy_scale", 1) * request.energy_multiplier
        )
        parameters["flight_time_scale"] = (
            parameters.get("flight_time_scale", 1) * request.flight_time_multiplier
        )
    # Apply the stress factor to every battery, including explicit additions.
    for b in s["batteries"]:
        b["soh"] *= request.battery_soh_multiplier
    for field, value in [
        ("运输能耗倍率", request.energy_multiplier),
        ("运输飞行时长倍率", request.flight_time_multiplier),
        ("运输电池SOH倍率", request.battery_soh_multiplier),
    ]:
        if value != 1:
            changes.append(f"{field}乘以{value:g}，为用户设定情景，不是实测概率。")
    if request.min_return_soc is not None:
        s["policy"]["min_return_soc"] = request.min_return_soc
        changes.append(f"运输返航SOC下限改为{request.min_return_soc:.1%}。")
    altered = 0
    if request.noncritical_deadline_multiplier != 1:
        for d in s["demands"]:
            if d["hard_deadline_s"] is None and d["expected_deadline_s"] is not None:
                d["expected_deadline_s"] *= request.noncritical_deadline_multiplier
                altered += 1
        changes.append(f"仅放宽{altered}条无硬截止需求的期望时限，所有硬截止保持原值。")
    if not changes:
        changes.append("输入参数保持原值，创建独立试算副本用于对照。")
    return s, changes
