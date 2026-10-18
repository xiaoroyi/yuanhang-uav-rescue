import type { Plan, Scenario } from '../api/client'

export function scheduleRows(plan: Plan, scenario: Scenario) {
  const cargo = new Map(scenario.cargo_items.map((c) => [c.cargo_id, c]))
  const demands = new Map(scenario.demands.map((d) => [d.demand_id, d]))
  const sorties = [...plan.sorties].sort(
    (a, b) => a.prepare_start_s - b.prepare_start_s || a.sortie_id.localeCompare(b.sortie_id),
  )
  const deliveries = sorties
    .flatMap((r) =>
      r.visits.flatMap((v) =>
        v.cargo_ids.map((id) => {
          const c = cargo.get(id),
            d = c ? demands.get(c.demand_id) : undefined
          return {
            cargo_id: id,
            sortie_id: r.sortie_id,
            site_id: v.site_id,
            drone_id: r.drone_id,
            battery_id: r.battery_id,
            cargo_type: c?.type,
            mass_kg: c?.mass_kg,
            complete_s: v.delivery_complete_s,
            expected_s: d?.expected_deadline_s,
            hard_s: d?.hard_deadline_s,
            delay_s:
              d?.expected_deadline_s == null
                ? null
                : Math.max(0, v.delivery_complete_s - d.expected_deadline_s),
          }
        }),
      ),
    )
    .sort((a, b) => a.complete_s - b.complete_s || a.cargo_id.localeCompare(b.cargo_id))
  return { sorties, deliveries }
}

// User-entered IDs can contain spreadsheet formula prefixes. Escape these in
// CSV exports without changing the on-screen identifiers or saved Plan.
export function scheduleCsv(rows: unknown[][]) {
  const cell = (v: unknown) => {
    let s = v == null ? '' : String(v)
    if (typeof v === 'string' && /^[\s]*[=+\-@\t\r]/.test(s)) s = "'" + s
    return '"' + s.replaceAll('"', '""') + '"'
  }
  return '\ufeff' + rows.map((row) => row.map(cell).join(',')).join('\r\n')
}
