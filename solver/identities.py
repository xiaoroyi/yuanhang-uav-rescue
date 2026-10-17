"""Opaque sortie identifiers, stable for the same planned assignment and timing."""

import hashlib


def sortie_id(cargo_ids, drone_id, battery_id, start, visits, charge_start=None):
    fields = [
        ",".join(sorted(cargo_ids)),
        drone_id,
        battery_id,
        f"{start:.6f}",
        ",".join(v["site_id"] for v in visits),
    ]
    if charge_start is not None:
        fields.append(f"charge={charge_start:.6f}")
    return "SRT-" + hashlib.sha256("|".join(fields).encode()).hexdigest()[:12]
