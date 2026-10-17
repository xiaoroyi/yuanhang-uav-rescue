"""Exact capacity scheduling and interval coloring for interchangeable resources.

Different initial release times are represented by fixed [0,available_after)
occupancy. Callers must establish equal physical capabilities before pooling.
Publication uses real entity IDs and independently reconstructed intervals.
"""

import math


class InterchangeablePool:
    def __init__(self, model, records, identity_key, prefix, horizon, scale):
        if not records:
            raise ValueError("Interchangeable resource pool is empty.")
        self.model, self.prefix, self.horizon = model, prefix, horizon
        self.available = {r[identity_key]: r["available_after_s"] for r in records}
        self.intervals = []
        self.last_start = -math.inf
        for i, resource in enumerate(records):
            release = math.ceil(resource["available_after_s"] * scale - 1e-8)
            if release > 0:
                self.intervals.append(
                    model.new_fixed_size_interval_var(
                        0, release, f"{prefix}_initial_{i}"
                    )
                )

    def add(self, start, end, present, label):
        duration = self.model.new_int_var(
            0, self.horizon, f"{self.prefix}_size_{label}"
        )
        self.model.add(duration == end - start).only_enforce_if(present)
        self.intervals.append(
            self.model.new_optional_interval_var(
                start, duration, end, present, f"{self.prefix}_{label}"
            )
        )

    def constrain(self):
        self.model.add_cumulative(
            self.intervals, [1] * len(self.intervals), len(self.available)
        )

    def assign(self, start, end):
        if start < self.last_start - 1e-8:
            raise ValueError("Pool coloring requires nondecreasing starts.")
        self.last_start = start
        candidates = [
            (ready, identity)
            for identity, ready in self.available.items()
            if ready <= start + 1e-8
        ]
        if not candidates:
            raise ValueError(
                "Capacity solution cannot be colored with its real entities."
            )
        _, identity = min(candidates)
        self.available[identity] = end
        return identity
