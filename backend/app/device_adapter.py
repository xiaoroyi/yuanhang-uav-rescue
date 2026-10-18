"""Device boundary. Only the isolated business-simulation adapter is installed."""

from abc import ABC, abstractmethod
from datetime import datetime, timezone

from backend.app.operation_models import DeviceCapabilities


class DeviceAdapter(ABC):
    @abstractmethod
    async def capabilities(self, device_id): ...

    @abstractmethod
    async def telemetry_stream(self, device_id):
        yield None

    @abstractmethod
    async def compile_mission(self, device_id, validated_sorties, context): ...

    @abstractmethod
    async def validate_compiled_mission(self, device_id, compiled_mission): ...

    @abstractmethod
    async def upload_mission(self, device_id, compiled_mission, request_context): ...

    @abstractmethod
    async def read_mission_state(self, device_id): ...

    @abstractmethod
    async def execute_command(self, device_id, command, request_context): ...


class SimulationAdapter(DeviceAdapter):
    def __init__(self, state_reader=None):
        self.state_reader = state_reader

    async def capabilities(self, device_id):
        return DeviceCapabilities(
            device_id=device_id,
            command_types=["mission.upload", "mission.activate", "state.query"],
        ).model_dump(mode="json")

    async def telemetry_stream(self, device_id):
        # The execution service supplies persisted samples, not a fabricated device feed.
        if self.state_reader:
            for sample in self.state_reader(device_id):
                yield sample

    async def compile_mission(self, device_id, validated_sorties, context):
        if context.get("mode") != "simulation" or not context.get("validated"):
            raise ValueError(
                "Only independently validated simulation schedules are accepted"
            )
        return {
            "device_id": device_id,
            "format": "business-simulation-v1",
            "sorties": validated_sorties,
            "plan_id": context["plan_id"],
        }

    async def validate_compiled_mission(self, device_id, compiled_mission):
        return (
            compiled_mission.get("device_id") == device_id
            and compiled_mission.get("format") == "business-simulation-v1"
        )

    async def upload_mission(self, device_id, compiled_mission, request_context):
        if not await self.validate_compiled_mission(device_id, compiled_mission):
            raise ValueError("Invalid simulation schedule")
        return {
            "accepted": True,
            "completed": False,
            "device_id": device_id,
            "evidence": "simulation upload ACK",
        }

    async def read_mission_state(self, device_id):
        return {
            "device_id": device_id,
            "mode": "simulation",
            "real_device_connected": False,
        }

    async def execute_command(self, device_id, command, request_context):
        return {
            "accepted": True,
            "completed": False,
            "device_id": device_id,
            "observed_at": datetime.now(timezone.utc).isoformat(),
        }
