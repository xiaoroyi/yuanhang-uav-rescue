"""Describe installed adapters and export a non-secret deployment configuration."""

from typing import Literal
from pydantic import BaseModel
from fastapi.responses import JSONResponse


class IntegrationEndpoint(BaseModel):
    name: str
    method: Literal["GET", "POST"]
    path: str
    description: str


class IntegrationOverview(BaseModel):
    runtime_mode: Literal["simulation"] = "simulation"
    installed_adapter: Literal["SimulationAdapter"] = "SimulationAdapter"
    real_device_connected: Literal[False] = False
    external_model_calls_enabled: Literal[False] = False
    telemetry_transport: Literal["server_sent_events"] = "server_sent_events"
    command_states: list[str]
    endpoints: list[IntegrationEndpoint]
    adapter_methods: list[str]


def register_integrations(app):
    @app.get("/api/v1/integrations", response_model=IntegrationOverview)
    def overview():
        return IntegrationOverview(
            command_states=[
                "queued",
                "sent",
                "acknowledged",
                "succeeded",
                "rejected",
                "expired",
                "indeterminate",
            ],
            adapter_methods=[
                "capabilities",
                "telemetry_stream",
                "compile_mission",
                "validate_compiled_mission",
                "upload_mission",
                "read_mission_state",
                "execute_command",
            ],
            endpoints=[
                IntegrationEndpoint(
                    name="遥测事件流",
                    method="GET",
                    path="/api/v1/executions/{execution_id}/stream",
                    description="服务器业务仿真状态；断流后重新读取执行账本。",
                ),
                IntegrationEndpoint(
                    name="模拟指令",
                    method="POST",
                    path="/api/v1/commands",
                    description="带执行版本、幂等键、有效期的模拟指令。",
                ),
                IntegrationEndpoint(
                    name="指令状态",
                    method="GET",
                    path="/api/v1/commands/{command_id}",
                    description="分别记录服务受理、设备ACK与动作完成。",
                ),
                IntegrationEndpoint(
                    name="任务状态回读",
                    method="GET",
                    path="/api/v1/executions/{execution_id}/devices/{device_id}/mission-state",
                    description="核对计划下发、机载激活与设备观测状态。",
                ),
            ],
        ).model_dump(mode="json")

    @app.get("/api/v1/integrations/configuration", response_class=JSONResponse)
    def configuration():
        return JSONResponse(
            {
                "format": "yuanhang-adapter-config-v1",
                "mode": "simulation",
                "adapter": "SimulationAdapter",
                "real_device_enabled": False,
                "device_adapter_contract": "backend/app/device_adapter.py",
                "external_llm": {
                    "enabled": False,
                    "api_endpoint": None,
                    "api_key_env": "YUANHANG_EOH_API_KEY",
                    "model_env": "YUANHANG_EOH_MODEL",
                    "online_solver_calls": False,
                },
                "weather": {
                    "enabled": False,
                    "provider": "Open-Meteo",
                    "documentation": "https://open-meteo.com/en/docs/historical-weather-api",
                    "units": {"wind_speed": "m/s", "precipitation": "mm"},
                },
                "command_requirements": [
                    "execution_revision",
                    "idempotency_key",
                    "expires_at",
                    "mode",
                    "permission",
                    "readback",
                ],
            },
            headers={
                "Content-Disposition": 'attachment; filename="yuanhang-integration-config.json"'
            },
        )
