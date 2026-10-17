import { chromium } from '@playwright/test'
import assert from 'node:assert/strict'
import fs from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..')
const base = process.argv[2] || 'http://127.0.0.1:8000'
assert.equal(new URL(base).hostname, '127.0.0.1')
const response = await fetch(base + '/api/v1/scenarios/examples', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ example: 'compact' }),
})
assert.equal(response.status, 201)
const scene = await response.json()
const browser = await chromium.launch({
  headless: true,
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'],
})
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
const errors = [],
  external = []
page.on('pageerror', (error) => errors.push(error.message))
page.on('console', (message) => {
  if (message.type() === 'error') errors.push(message.text())
})
await page.route('**/*', (route) => {
  const url = new URL(route.request().url())
  if (url.origin === base || ['blob:', 'data:'].includes(url.protocol)) return route.continue()
  external.push(url.href)
  return route.abort()
})
await page.addInitScript((id) => localStorage.setItem('yuanhang-scenario', id), scene.scenario_id)
let report
try {
  await page.goto(base, { waitUntil: 'networkidle' })
  await page.getByRole('button', { name: '生成真实方案', exact: true }).click()
  await page.locator('.job-banner').waitFor({ state: 'visible' })
  await page.locator('.job-banner').waitFor({ state: 'hidden', timeout: 45000 })
  await page.getByTestId('sortie-card').first().waitFor()
  await page.locator('.toast').last().waitFor({ state: 'hidden', timeout: 12000 })
  const list = await (await fetch(base + `/api/v1/scenarios/${scene.scenario_id}/plans`)).json()
  const plan = await (await fetch(base + `/api/v1/plans/${list[0].plan_id}`)).json()
  assert.equal(plan.data_origin, 'solver')
  assert.equal(plan.validation.status, 'passed')
  assert.equal(new Set(plan.sorties.flatMap((r) => r.cargo_ids)).size, 32)
  const out = path.join(root, 'evidence/browser/verified')
  await fs.mkdir(out, { recursive: true })
  for (const [width, height] of [
    [1440, 900],
    [1280, 720],
  ]) {
    await page.setViewportSize({ width, height })
    await page.screenshot({ path: path.join(out, `production-${width}.png`) })
  }
  assert.deepEqual(external, [])
  assert.deepEqual(errors, [])
  report = {
    passed: true,
    at_utc: new Date().toISOString(),
    base,
    scenario_id: scene.scenario_id,
    plan_id: plan.plan_id,
    snapshot_id: plan.snapshot_id,
    metrics: plan.metrics,
    external_requests: external,
    console_errors: errors,
    viewports: [
      [1440, 900],
      [1280, 720],
    ],
    note: 'Built static frontend served by the local backend. External network requests were blocked.',
  }
  await fs.writeFile(
    path.join(root, 'evidence/browser/production-smoke.json'),
    JSON.stringify(report, null, 2) + '\n',
  )
  console.log(JSON.stringify(report, null, 2))
} finally {
  await browser.close()
}
