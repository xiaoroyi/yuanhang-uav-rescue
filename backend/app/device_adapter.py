"""Device boundary. Only the isolated business-simulation adapter is installed."""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from shared.contracts import content_hash

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
    def __init__(
        self, state_reader=None, mission_state_reader=None, mission_state_writer=None
    ):
        self.state_reader = state_reader
        self.mission_state_reader = mission_state_reader
        self.mission_state_writer = mission_state_writer

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
            and bool(compiled_mission.get("plan_id"))
            and isinstance(compiled_mission.get("sorties"), list)
            and all(r.get("drone_id") == device_id for r in compiled_mission["sorties"])
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
        if self.mission_state_reader:
            value = self.mission_state_reader(device_id)
            if value.get("device_id") != device_id:
                raise ValueError("Device readback identity mismatch")
            return value
        return {
            "device_id": device_id,
            "mode": "simulation",
            "real_device_connected": False,
        }

    async def execute_command(self, device_id, command, request_context):
        if (
            request_context.get("mode") != "simulation"
            or not self.mission_state_reader
            or not self.mission_state_writer
        ):
            raise ValueError("A persisted simulation state store is required")
        state = await self.read_mission_state(device_id)
        kind = command["command_type"]
        if kind == "mission.upload":
            compiled = command["compiled_mission"]
            if not await self.validate_compiled_mission(device_id, compiled):
                raise ValueError("Invalid compiled mission")
            self.mission_state_writer(
                device_id,
                {
                    "uploaded_plan_id": compiled["plan_id"],
                    "uploaded_content_sha256": content_hash(compiled),
                    "last_upload_command_id": command["command_id"],
                },
            )
        elif kind == "mission.activate":
            if not request_context.get("approved"):
                raise ValueError("Activation approval required")
            target = command["desired_plan_id"]
            if (
                state["uploaded_plan_id"] != target
                and state["active_plan_id"] != target
            ):
                raise ValueError("Target mission has not been uploaded")
            self.mission_state_writer(
                device_id,
                {
                    "active_plan_id": target,
                    "last_activation_command_id": command["command_id"],
                },
            )
        elif kind != "state.query":
            raise ValueError("Unsupported simulated command")
        return {
            "accepted": True,
            "completed": False,
            "device_id": device_id,
            "observed_at": datetime.now(timezone.utc).isoformat(),
        }
