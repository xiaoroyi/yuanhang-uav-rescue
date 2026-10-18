import type { Plan, Scenario } from '../api/client'

export const analysisPalette = ['#68ddff', '#a59aff', '#ffca80', '#f98fb8', '#79e3bc', '#8eaaff']

export const chartText = (value: string) =>
  value.replace(
    /[&<>"']/g,
    (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]!,
  )

/** Axis tooltips can include a null sample beside another series' known value. */
export const formatChartValue = (value: unknown, digits = 0, unit = '') =>
  typeof value === 'number' && Number.isFinite(value)
    ? `${value.toLocaleString('zh-CN', { maximumFractionDigits: digits })}${unit}`
    : '未知'

/** Display-only sums of saved inputs/results. No energy or scheduling model lives here. */
export function visualAnalysisData(scenario: Scenario, plan: Plan | null) {
  const cargoKinds = [...new Set(scenario.demands.map((d) => d.cargo_type))].sort()
  const sites = scenario.sites.map((site) => {
    const demands = scenario.demands.filter((d) => d.site_id === site.id)
    const demandIds = new Set(demands.map((d) => d.demand_id))
    const cargo = scenario.cargo_items.filter((c) => demandIds.has(c.demand_id))
    return {
      id: site.id,
      name: site.name,
      quantities: cargoKinds.map((kind) =>
        demands.filter((d) => d.cargo_type === kind).reduce((n, d) => n + d.required_quantity, 0),
      ),
      quantity: demands.reduce((n, d) => n + d.required_quantity, 0),
      stock: cargo.length,
      mass: cargo.reduce((n, c) => n + c.mass_kg, 0),
      volume: cargo.reduce((n, c) => n + c.volume_l, 0),
    }
  })
  const materials = cargoKinds.map((kind) => ({
    kind,
    quantity: scenario.demands
      .filter((d) => d.cargo_type === kind)
      .reduce((n, d) => n + d.required_quantity, 0),
    stock: scenario.cargo_items.filter((c) => c.type === kind).length,
  }))
  const flights = (plan?.sorties || []).map((flight, i) => ({
    id: flight.sortie_id,
    label: String(i + 1).padStart(2, '0'),
    drone: flight.drone_id,
    battery: flight.battery_id,
    boxes: flight.cargo_ids.length,
    minutes: (flight.return_s - flight.takeoff_s) / 60,
    energy: flight.energy_kwh,
    soc: flight.return_soc,
    siteIds: flight.visits.map((v) => v.site_id),
  }))
  const droneIds = [...new Set((plan?.sorties || []).map((f) => f.drone_id))].sort()
  const workloads = droneIds.map((id) => {
    const runs = (plan?.sorties || []).filter((f) => f.drone_id === id)
    return {
      id,
      count: runs.length,
      boxes: runs.reduce((n, f) => n + f.cargo_ids.length, 0),
      prepare: runs.reduce((n, f) => n + (f.takeoff_s - f.prepare_start_s) / 60, 0),
      flight: runs.reduce((n, f) => n + (f.return_s - f.takeoff_s) / 60, 0),
      turnaround: runs.reduce((n, f) => n + (f.drone_released_s - f.return_s) / 60, 0),
    }
  })
  const checks = plan?.validation.checks || []
  return {
    cargoKinds,
    sites,
    materials,
    flights,
    workloads,
    quantity: sites.reduce((n, s) => n + s.quantity, 0),
    mass: scenario.cargo_items.reduce((n, c) => n + c.mass_kg, 0),
    volume: scenario.cargo_items.reduce((n, c) => n + c.volume_l, 0),
    batteryCount: new Set(flights.map((f) => f.battery)).size,
    passed: checks.filter((c) => c.status === 'passed').length,
    unevaluated: checks.filter((c) => c.status === 'not_evaluated').length,
    failed: checks.filter((c) => c.status === 'failed').length,
  }
}
