import { test, expect, type APIRequestContext, type Page } from '@playwright/test'
import fs from 'node:fs/promises'
import path from 'node:path'
import type { Plan, Scenario, Snapshot, SolveJob } from '../src/api/client'

test.setTimeout(120000)
let scene: Scenario, snapshot: Snapshot
let plans: Plan[] = []

async function compute(
  request: APIRequestContext,
  objective: 'time' | 'energy' | 'balanced',
  policy = 'tradeoff_v2',
) {
  const response = await request.post('/api/v1/solve-jobs', {
    data: {
      snapshot_id: snapshot.snapshot_id,
      objective,
      objective_policy: policy,
      time_limit_s: 20,
      seed: 42,
    },
  })
  expect(response.status()).toBe(202)
  let job: SolveJob = await response.json()
  await expect
    .poll(
      async () => {
        job = await (await request.get(`/api/v1/solve-jobs/${job.job_id}`)).json()
        return job.job_state
      },
      { timeout: 45000, intervals: [300, 500] },
    )
    .toBe('completed')
  expect(job.has_validated_plan).toBe(true)
  const plan: Plan = await (await request.get(`/api/v1/plans/${job.plan_id}`)).json()
  expect(plan.validation.status).toBe('passed')
  expect(plan.objective_policy).toBe(policy)
  return plan
}
async function open(page: Page, plan: Plan, destination = 'workspace') {
  await page.addInitScript(
    ({ id, pid }) => {
      if (!localStorage.getItem('yuanhang-scenario')) localStorage.setItem('yuanhang-scenario', id)
      if (!localStorage.getItem(`yuanhang-plan-${id}`))
        localStorage.setItem(`yuanhang-plan-${id}`, pid)
      if (!localStorage.getItem('yuanhang-motion')) localStorage.setItem('yuanhang-motion', 'on')
    },
    { id: scene.scenario_id, pid: plan.plan_id },
  )
  await page.goto(`/#/${destination}`)
  await expect(page.getByLabel('选择场景')).toHaveValue(scene.scenario_id)
}
test.beforeAll(async ({ request }) => {
  scene = await (
    await request.post('/api/v1/scenarios/examples', { data: { example: 'compact' } })
  ).json()
  snapshot = await (
    await request.post(`/api/v1/scenarios/${scene.scenario_id}/snapshots`, {
      data: { expected_state_version: 1 },
    })
  ).json()
  plans = []
  for (const goal of ['time', 'energy', 'balanced'] as const)
    plans.push(await compute(request, goal))
  plans.push(await compute(request, 'time', 'deadline_first_v1'))
  await fs.mkdir(path.resolve('../evidence/strategy-v2'), { recursive: true })
  await fs.writeFile(
    path.resolve('../evidence/strategy-v2/browser-solve.json'),
    JSON.stringify(
      {
        snapshot,
        plans,
        note: 'Four fresh real worker solves in isolated E2E runtime; original soft/hard deadlines retained.',
      },
      null,
      2,
    ) + '\n',
  )
})

test('新规则真实取舍、旧结果说明与共同口径', async ({ page, request }) => {
  await open(page, plans[0])
  const cards = page.locator('.strategy-panel')
  await expect(cards.locator('.strategy-facts')).toHaveCount(3)
  await expect(cards).toContainText('直接取舍 v2')
  await expect(cards).toContainText('节能可能增加延期')
  for (const p of plans.slice(0, 3)) await expect(cards).toContainText(p.plan_id)
  const [t, e, b] = plans
  expect(t.metrics.makespan_s!).toBeLessThan(b.metrics.makespan_s!)
  expect(b.metrics.makespan_s!).toBeLessThan(e.metrics.makespan_s!)
  expect(e.metrics.energy_kwh!).toBeLessThan(b.metrics.energy_kwh!)
  expect(b.metrics.energy_kwh!).toBeLessThan(t.metrics.energy_kwh!)
  expect(snapshot.scenario.demands.some((d) => d.expected_deadline_s != null)).toBe(true)
  const old = plans[3]
  const c = await (
    await request.get(`/api/v1/plans/${old.plan_id}/comparison?other_plan_id=${t.plan_id}`)
  ).json()
  expect(c.comparable).toBe(false)
  await page.locator('.plan-selector').selectOption(old.plan_id)
  await expect(cards).toContainText('旧版延期优先 v1')
  await expect(cards.getByRole('button', { name: '按新规则重新计算' })).toBeVisible()
  await expect(cards.locator('.strategy-facts')).toHaveCount(1)
  await page.locator('.plan-selector').selectOption(t.plan_id)
  await cards.scrollIntoViewIfNeeded()
  await page.screenshot({
    path: path.resolve('../evidence/strategy-v2/strategies-1440.png'),
    animations: 'disabled',
  })
})

test('调度安排完整覆盖箱件，筛选联动、CSV、历史绑定与响应式', async ({ page }) => {
  const errors: string[] = []
  page.on('pageerror', (e) => errors.push(e.message))
  await open(page, plans[0], 'schedule')
  const p = plans[0]
  const table = page.getByRole('table', { name: '运输调度安排表', exact: true })
  await expect(table.locator('tbody tr')).toHaveCount(p.sorties.length)
  const chosen = p.sorties[p.sorties.length - 1]
  await table.getByRole('button', { name: chosen.sortie_id, exact: true }).click()
  await expect(page.locator('.schedule-route-detail')).toContainText(chosen.battery_id)
  await expect(table.locator('tr.selected')).toContainText(chosen.battery_id)
  await expect(page.locator('.schedule-route-detail')).toContainText(chosen.sortie_id)
  await page.getByLabel('筛选执行无人机').selectOption(chosen.drone_id)
  await expect(table.locator('tbody tr')).toHaveCount(
    p.sorties.filter((r) => r.drone_id === chosen.drone_id).length,
  )
  await page.getByLabel('筛选执行无人机').selectOption('all')
  const download = page.waitForEvent('download')
  await page.getByRole('button', { name: '导出当前安排 CSV' }).click()
  const downloaded = await download
  const csv = await fs.readFile((await downloaded.path())!, 'utf8')
  expect(csv).toContain(p.plan_id)
  expect(csv).toContain('电池可复用(s)')
  expect(csv.trim().split('\n')).toHaveLength(p.sorties.length + 1)
  for (const [width, height] of [
    [1440, 900],
    [1280, 720],
    [390, 844],
  ]) {
    await page.setViewportSize({ width, height })
    await page.screenshot({
      path: path.resolve(`../evidence/strategy-v2/schedule-${width}.png`),
      animations: 'disabled',
    })
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
      ),
    ).toBeLessThanOrEqual(2)
  }
  await page.getByRole('button', { name: '逐箱交付', exact: true }).click()
  await expect(page.getByRole('table', { name: '逐箱交付安排表' }).locator('tbody tr')).toHaveCount(
    32,
  )
  await page.getByLabel('搜索调度安排').fill(p.sorties[0].cargo_ids[0])
  await expect(page.getByRole('table', { name: '逐箱交付安排表' }).locator('tbody tr')).toHaveCount(
    1,
  )
  await page.getByLabel('搜索调度安排').fill('')
  await page.getByRole('button', { name: '中继排程', exact: true }).click()
  await expect(page.locator('.schedule-no-rows')).toContainText('当前方案没有中继架次')
  await page.getByLabel('安排表方案').selectOption(plans[1].plan_id)
  await page.reload()
  await expect(page.getByLabel('安排表方案')).toHaveValue(plans[1].plan_id)
  expect(errors).toEqual([])
})

test('背景光流和粒子实际运动，开关与系统减少动态效果有效', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'no-preference' })
  await open(page, plans[0])
  const particle = page.locator('.ambient-particles span').first()
  await expect(particle).toHaveCSS('animation-play-state', 'running')
  const before = await particle.evaluate((e) => getComputedStyle(e).transform)
  await expect.poll(() => particle.evaluate((e) => getComputedStyle(e).transform)).not.toBe(before)
  await page.screenshot({ path: path.resolve('../evidence/strategy-v2/ambient-on.png') })
  await page.getByRole('button', { name: '暂停动态背景', exact: true }).click()
  await expect(particle).toHaveCSS('animation-play-state', 'paused')
  await expect(page.locator('.ambient-beam')).toHaveCSS('animation-play-state', 'paused')
  await page.getByRole('button', { name: '启用动态背景', exact: true }).click()
  await expect(particle).toHaveCSS('animation-play-state', 'running')
  await page.emulateMedia({ reducedMotion: 'reduce' })
  await expect(particle).toHaveCSS('animation-name', 'none')
})
