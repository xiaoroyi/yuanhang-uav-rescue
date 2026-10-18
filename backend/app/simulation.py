"""Persistent, deterministic simulation ledger with a server-owned clock."""

from __future__ import annotations
import copy
from datetime import datetime, timezone
import threading

from sqlalchemy import select

from backend.app.jobs import now
from backend.app.storage import ExecutionRow, OperationRecordRow, PlanRow, SnapshotRow
from backend.app.operation_models import ExecutionView
from backend.app.missions import identity, require
from solver.assets import terrain_store
from solver.stages import stage_analysis, position


def timestamp(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


class SimulationEngine:
    def __init__(self, database, error):
        self.db, self.error = database, error
        self.cache = {}
        self.stop_event = threading.Event()
        self.thread = threading.Thread(
            target=self.run, name="simulation-clock", daemon=True
        )
        self.thread.start()

    def close(self):
        self.stop_event.set()
        self.thread.join(timeout=3)

    def run(self):
        while not self.stop_event.wait(0.5):
            try:
                with terrain_store(self.db.directory / "assets"):
                    with self.db.session(immediate=True) as session:
                        for row in session.scalars(select(ExecutionRow)):
                            if row.content["status"] == "running":
                                self.advance(session, row)
            except Exception:
                # Preserve the clock/ledger transaction on error; requests expose the actual failure.
                import logging

                logging.getLogger(__name__).exception(
                    "Simulation clock transaction failed"
                )

    def plan_data(self, session, plan_id):
        if plan_id not in self.cache:
            p = require(session, PlanRow, plan_id, self.error)
            snap = require(session, SnapshotRow, p.snapshot_id, self.error).content
            stages = stage_analysis(snap, p.content)
            if len(self.cache) >= 64:
                self.cache.pop(next(iter(self.cache)))
            self.cache[plan_id] = (p.content, snap, stages)
        return self.cache[plan_id]

    def records(self, session, eid, namespace):
        return [
            r.content
            for r in session.scalars(
                select(OperationRecordRow).where(
                    OperationRecordRow.namespace == namespace,
                    OperationRecordRow.owner_id == eid,
                )
            )
        ]

    def schedule(self, session, value):
        result = []
        for part in value["schedule_parts"]:
            p, snap, stages = self.plan_data(session, part["plan_id"])
            for r in p["sorties"]:
                if r["sortie_id"] in part["sortie_ids"]:
                    result.append(
                        (
                            p,
                            snap,
                            r,
                            [
                                x
                                for x in stages["trajectory_segments"]
                                if x["sortie_id"] == r["sortie_id"]
                            ],
                        )
                    )
        return result

    def advance(self, session, row, target=None):
        value = copy.deepcopy(row.content)
        if value["status"] == "ready" and target is None:
            if value["connected"]:
                value["last_telemetry"] = self.telemetry(
                    session, value, self.schedule(session, value)
                )
                for sample in value["last_telemetry"]:
                    sample.update(
                        phase="ready",
                        cargo_ids=[],
                        sortie_id=None,
                        battery_id=None,
                        soc=None,
                        soc_sample_time_s=None,
                    )
            row.content = value
            return value
        tick = value["time_s"]
        if target is not None:
            tick = target
        elif value["status"] == "running":
            tick = max(
                tick,
                value["anchor_sim_s"]
                + (timestamp(now()) - timestamp(value["anchor_wall_at"]))
                * value["speed"],
            )
        schedule = self.schedule(session, value)
        horizon = max(
            [
                max(r["drone_released_s"], r["battery_released_s"])
                for _, _, r, _ in schedule
            ]
            + [0]
        )
        tick = min(tick, horizon)
        events = []
        for p, _, r, _ in schedule:
            for kind, t, ids in [
                ("loaded", r["prepare_start_s"], r["cargo_ids"]),
                ("takeoff", r["takeoff_s"], r["cargo_ids"]),
                *[
                    ("delivered", v["delivery_complete_s"], v["cargo_ids"])
                    for v in r["visits"]
                ],
                ("returned", r["return_s"], []),
                ("released", r["drone_released_s"], []),
                ("battery_ready", r["battery_released_s"], []),
            ]:
                if t <= tick + 1e-8:
                    events.append((t, p["plan_id"], r, kind, ids))
        for t, pid, r, kind, ids in sorted(
            events, key=lambda e: (e[0], e[1], e[2]["sortie_id"], e[3])
        ):
            key = f"{row.id}:{pid}:{r['sortie_id']}:{kind}:{','.join(ids)}"
            if session.get(OperationRecordRow, ("execution.fact", key)) is None:
                value["facts_cursor"] += 1
                fact = {
                    "fact_id": key,
                    "cursor": value["facts_cursor"],
                    "time_s": t,
                    "kind": kind,
                    "plan_id": pid,
                    "sortie_id": r["sortie_id"],
                    "drone_id": r["drone_id"],
                    "battery_id": r["battery_id"],
                    "cargo_ids": ids,
                    "source": "simulation",
                }
                session.add(
                    OperationRecordRow(
                        namespace="execution.fact",
                        id=key,
                        owner_id=row.id,
                        request_hash="deterministic",
                        content=fact,
                    )
                )
                session.flush()
        value["time_s"] = tick
        if (
            (value["status"] == "running" or target is not None)
            and tick >= horizon
            and horizon > 0
        ):
            value.update(
                status="completed", revision=value["revision"] + 1, updated_at=now()
            )
        if value["connected"]:
            value["last_telemetry"] = self.telemetry(session, value, schedule)
        row.content = value
        session.flush()
        return value

    def telemetry(self, session, value, schedule):
        tick = value["time_s"]
        value["telemetry_sequence"] = value.get("telemetry_sequence", 0) + 1
        unavailable = {
            e["object_id"]
            for e in self.records(session, value["execution_id"], "execution.event")
            if e["event_type"] == "drone.unavailable"
        }
        initial, snapshot, _ = self.plan_data(session, value["initial_plan_id"])
        result = []
        for drone in snapshot["scenario"]["drones"]:
            uses = [
                item for item in schedule if item[2]["drone_id"] == drone["drone_id"]
            ]
            active = next(
                (
                    item
                    for item in uses
                    if item[2]["prepare_start_s"] <= tick < item[2]["drone_released_s"]
                ),
                None,
            )
            coords = snapshot["scenario"]["base"]["coordinates"]
            elevation = snapshot["scenario"]["base"]["ground_elevation_m"]
            phase = "unavailable" if drone["drone_id"] in unavailable else "available"
            soc = None
            soc_time = None
            sid = None
            bid = None
            loaded = []
            pid = initial["plan_id"]
            if active:
                p, snap, r, stages = active
                pid = p["plan_id"]
                sid = r["sortie_id"]
                bid = r["battery_id"]
                segment = next(
                    (x for x in stages if x["start_s"] <= tick < x["end_s"]), None
                )
                if segment:
                    coords, elevation = position(segment, tick)
                    phase = segment["phase"]
                    loaded = segment["cargo_ids"]
                    # Last computed endpoint, never an invented continuous SOC reading.
                    soc, soc_time = segment["soc_start"], segment["start_s"]
            else:
                past = sorted(
                    [item for item in uses if item[2]["return_s"] <= tick],
                    key=lambda x: x[2]["return_s"],
                )
                if past:
                    p, _, r, _ = past[-1]
                    pid = p["plan_id"]
                    soc = r["return_soc"]
                    soc_time = r["return_s"]
                    if tick >= r["battery_released_s"]:
                        soc, soc_time = 1.0, r["battery_released_s"]
            result.append(
                {
                    "device_id": drone["drone_id"],
                    "device_session_id": value["session_id"],
                    "device_sequence": value["telemetry_sequence"],
                    "observed_at": now(),
                    "received_at": now(),
                    "time_s": tick,
                    "coordinates": coords,
                    "elevation_m": elevation,
                    "vertical_datum": snapshot["scenario"]["terrain"].get(
                        "vertical_datum"
                    ),
                    "soc": soc,
                    "soc_sample_time_s": soc_time,
                    "phase": phase,
                    "sortie_id": sid,
                    "battery_id": bid,
                    "cargo_ids": loaded,
                    "quality": "simulated",
                    "active_plan_id": pid,
                }
            )
        return result

    def view(self, session, row, advance=True):
        value = self.advance(session, row) if advance else row.content
        facts = sorted(
            self.records(session, row.id, "execution.fact"), key=lambda x: x["cursor"]
        )
        telemetry = copy.deepcopy(value.get("last_telemetry", []))
        if not value["connected"]:
            for sample in telemetry:
                sample["quality"] = "stale"
        fields = {k: v for k, v in value.items() if k in ExecutionView.model_fields}
        fields.update(
            facts=facts,
            telemetry=telemetry,
            delivered_cargo_ids=sorted(
                {c for f in facts if f["kind"] == "delivered" for c in f["cargo_ids"]}
            ),
        )
        return fields
