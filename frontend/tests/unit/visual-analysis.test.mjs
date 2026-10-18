import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import {
  chartText,
  formatChartValue,
  visualAnalysisData,
} from '../../src/pages/visual-analysis-data.ts'
import { terrainMeshIndices } from '../../src/components/terrain-scene-data.ts'

const saved = JSON.parse(
  await readFile(
    new URL('../../../submission/examples/solve-result.json', import.meta.url),
    'utf8',
  ),
)

test('imported entity IDs stay inert inside an HTML chart tooltip', () => {
  assert.equal(
    chartText('<img src=x onerror="alert(1)"> & drone'),
    '&lt;img src=x onerror=&quot;alert(1)&quot;&gt; &amp; drone',
  )
})

test('numeric tooltips distinguish unknown samples from an actual zero', () => {
  for (const value of [null, undefined, NaN, Infinity, -Infinity, '', '0', [0, null]])
    assert.equal(formatChartValue(value, 2, ' m'), '未知')
  assert.equal(formatChartValue(0, 2, ' m'), '0 m')
  assert.equal(formatChartValue(1234.567, 2, ' m'), '1,234.57 m')
  assert.equal(formatChartValue(-5.25, 1, '%'), '-5.3%')
})

test('analysis preserves demand versus actual stock and unknown energy without changing inputs', () => {
  const scenario = structuredClone(saved.snapshot.scenario)
  const plan = structuredClone(saved.outcome.plan)
  scenario.demands[0].required_quantity += 3
  plan.sorties[0].energy_kwh = null
  plan.sorties[0].return_soc = null
  const input = JSON.stringify({ scenario, plan })
  const result = visualAnalysisData(scenario, plan)
  assert.equal(
    result.quantity,
    saved.snapshot.scenario.demands.reduce((n, d) => n + d.required_quantity, 0) + 3,
  )
  assert.equal(
    result.materials.reduce((n, m) => n + m.stock, 0),
    scenario.cargo_items.length,
  )
  assert.notEqual(result.quantity, scenario.cargo_items.length)
  assert.equal(result.flights[0].energy, null)
  assert.equal(result.flights[0].soc, null)
  assert.equal(
    result.workloads.reduce((n, d) => n + d.boxes, 0),
    plan.sorties.reduce((n, d) => n + d.cargo_ids.length, 0),
  )
  assert.equal(JSON.stringify({ scenario, plan }), input)
})

test('empty Plan keeps real input totals and does not invent result series', () => {
  const result = visualAnalysisData(saved.snapshot.scenario, null)
  assert.ok(result.quantity > 0)
  assert.ok(result.mass > 0)
  assert.deepEqual(result.flights, [])
  assert.deepEqual(result.workloads, [])
  assert.equal(result.passed, 0)
})

test('a missing DEM sample removes every touching cell, including an internal hole', () => {
  assert.equal(
    terrainMeshIndices([
      [0, 0],
      [0, 0],
    ]).length,
    6,
  )
  assert.deepEqual(
    terrainMeshIndices([
      [100, 100],
      [100, null],
    ]),
    [],
  )
  assert.deepEqual(
    terrainMeshIndices([
      [100, 100, 100],
      [100, null, 100],
      [100, 100, 100],
    ]),
    [],
  )
  const grid = Array.from({ length: 4 }, () => Array(4).fill(200))
  grid[0][0] = null
  const indices = terrainMeshIndices(grid)
  assert.equal(indices.length, 8 * 6)
  assert.ok(!indices.includes(0))
})
