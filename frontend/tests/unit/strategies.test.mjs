import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import {
  equalityExplanation,
  policyOf,
  scheduleSignature,
  strategyMetrics,
} from '../../src/lib/strategies.ts'
import { scheduleRows, scheduleCsv } from '../../src/pages/schedule-data.ts'

const saved = JSON.parse(
  await readFile(
    new URL('../../../submission/examples/solve-result.json', import.meta.url),
    'utf8',
  ),
)
const base = saved.outcome.plan

test('legacy policy is explicit and joint metrics consistently include relay scope', () => {
  assert.equal(policyOf(base), 'deadline_first_v1')
  const p = structuredClone(base)
  p.joint_metrics = { joint_energy_kwh: 99, joint_makespan_s: 1234 }
  assert.deepEqual(strategyMetrics(p), { energy_kwh: 99, makespan_s: 1234 })
})
test('same metrics do not imply the same schedule or the same objective policy', () => {
  const plans = ['time', 'energy', 'balanced'].map((objective) => ({
    ...structuredClone(base),
    objective,
    objective_policy: 'tradeoff_v2',
  }))
  assert.match(equalityExplanation(plans), /三份实际排程相同/)
  plans[1].sorties[0].takeoff_s += 0.01
  assert.notEqual(scheduleSignature(plans[0]), scheduleSignature(plans[1]))
  assert.match(equalityExplanation(plans), /显示精度相同/)
  plans[2].objective_policy = 'deadline_first_v1'
  assert.equal(equalityExplanation(plans), '')
})
test('manifest covers each real cargo once and preserves source data and unknown deadlines', () => {
  const before = JSON.stringify(saved)
  const rows = scheduleRows(base, saved.snapshot.scenario)
  assert.equal(
    rows.deliveries.length,
    base.sorties.reduce((n, r) => n + r.cargo_ids.length, 0),
  )
  assert.equal(new Set(rows.deliveries.map((d) => d.cargo_id)).size, rows.deliveries.length)
  for (const d of rows.deliveries) {
    const r = base.sorties.find((r) => r.sortie_id === d.sortie_id)
    assert.equal(d.battery_id, r.battery_id)
    assert.equal(
      d.complete_s,
      r.visits.find((v) => v.cargo_ids.includes(d.cargo_id)).delivery_complete_s,
    )
  }
  assert.equal(JSON.stringify(saved), before)
  const csv = scheduleCsv([['=SUM(1,2)', 'a"b', null, 0, -1, '站点\n换行']])
  assert.match(csv, /"'=SUM\(1,2\)"/)
  assert.ok(csv.includes('"a""b"'))
  assert.ok(csv.includes('"","0","-1"'))
})
