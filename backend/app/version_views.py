"""Stored scenario revisions; timestamps are unknown in the existing version table."""

from pydantic import BaseModel, ConfigDict


class ScenarioVersionSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario_id: str
    state_version: int
    name: str
    content_hash: str
    created_at: str | None
    data_origin: str
    site_count: int
    cargo_count: int
    drone_count: int
    battery_count: int
