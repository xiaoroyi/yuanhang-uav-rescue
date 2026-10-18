"""Display-only spatial views; solver terrain remains unchanged."""

from pydantic import BaseModel, ConfigDict, Field


class TerrainSurface(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    asset_id: str
    name: str
    sha256: str = Field(pattern="^[a-f0-9]{64}$")
    bounds: tuple[float, float, float, float]
    longitude: list[float] = Field(min_length=2, max_length=73)
    latitude: list[float] = Field(min_length=2, max_length=73)
    elevations_m: list[list[float | None]] = Field(min_length=2, max_length=73)
    min_elevation_m: float
    max_elevation_m: float
    valid_fraction: float = Field(gt=0, le=1)
    notice: str
