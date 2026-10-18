"""Persisted simulated mission state, independent of command request/receipt rows."""

import copy

from backend.app.jobs import now
from backend.app.storage import OperationRecordRow, PlanRow, SnapshotRow
from backend.app.operation_models import DeviceMissionState
from shared.contracts import content_hash


class SimulationDeviceStore:
    def __init__(self, session, execution, error):
        self.session, self.execution, self.error = session, execution, error

    def _row(self, device_id):
        p = self.session.get(PlanRow, self.execution.content["initial_plan_id"])
        snap = self.session.get(SnapshotRow, p.snapshot_id).content
        if device_id not in {d["drone_id"] for d in snap["scenario"]["drones"]}:
            raise self.error(403, "CONTROL_NOT_OWNED", "当前执行不拥有此模拟机体。")
        key = ("simulation.device_state", self.execution.id + ":" + device_id)
        row = self.session.get(OperationRecordRow, key)
        if row is None:
            value = {
                "execution_id": self.execution.id,
                "device_id": device_id,
                "mode": "simulation",
                "revision": 1,
                "active_plan_id": self.execution.content["desired_plan_id"],
                "uploaded_plan_id": None,
                "uploaded_content_sha256": None,
                "last_upload_command_id": None,
                "last_activation_command_id": None,
                "updated_at": now(),
                "real_device_connected": False,
            }
            row = OperationRecordRow(
                namespace=key[0],
                id=key[1],
                owner_id=self.execution.id,
                request_hash=content_hash(
                    {"execution_id": self.execution.id, "device_id": device_id}
                ),
                content=value,
            )
            self.session.add(row)
            self.session.flush()
        return row

    def read(self, device_id):
        row = self._row(device_id)
        return DeviceMissionState.model_validate(
            {**row.content, "observed_at": now()}
        ).model_dump(mode="json")

    def write(self, device_id, patch):
        row = self._row(device_id)
        forbidden = set(patch) - {
            "active_plan_id",
            "uploaded_plan_id",
            "uploaded_content_sha256",
            "last_upload_command_id",
            "last_activation_command_id",
        }
        if forbidden:
            raise ValueError("Device state update contains unsupported fields")
        value = {
            **row.content,
            **copy.deepcopy(patch),
            "revision": row.content["revision"] + 1,
            "updated_at": now(),
        }
        DeviceMissionState.model_validate({**value, "observed_at": now()})
        row.content = value
        return self.read(device_id)
