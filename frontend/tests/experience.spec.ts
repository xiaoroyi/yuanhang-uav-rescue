import { test, expect, type APIRequestContext, type Page } from '@playwright/test'
import fs from 'node:fs/promises'
import type { Plan, Scenario, Snapshot, SolveJob } from '../src/api/client'

// All scenarios, snapshots and plans below come from the real isolated test API.
// This file does not intercept HTTP or reuse the production demonstration database.
test.setTimeout(120000)

let source: Scenario
let snapshot: Snapshot
let timePlan: Plan
let energyPlan: Plan
const pageErrors = new Map<Page, string[]>()

async function compact(request: APIRequestContext): Promise<Scenario> {
  const response = await request.post('/api/v1/scenarios/examples', {
    data: { example: 'compact' },
  })
  expect(response.status()).toBe(201)
  return response.json()
}

async function compute(
  request: APIRequestContext,
  input: Snapshot,
  objective: 'time' | 'energy',
): Promise<Plan> {
  const created = await request.post('/api/v1/solve-jobs', {
    data: { snapshot_id: input.snapshot_id, objective, time_limit_s: 15, seed: 42 },
  })
  expect(created.status()).toBe(202)
  const initial: SolveJob = await created.json()
  let job = initial
  await expect
    .poll(
      async () => {
        const response = await request.get(`/api/v1/solve-jobs/${initial.job_id}`)
        expect(response.status()).toBe(200)
        job = await response.json()
        return job.job_state
      },
      { timeout: 60000, intervals: [250, 500, 1000], message: `real ${objective} solve` },
    )
    .toBe('completed')
  expect(job.has_validated_plan, JSON.stringify(job)).toBe(true)
  expect(job.plan_id).toBeTruthy()
  const response = await request.get(`/api/v1/plans/${job.plan_id}`)
  expect(response.status()).toBe(200)
  const plan: Plan = await response.json()
  expect(plan.snapshot_id).toBe(input.snapshot_id)
  expect(plan.objective).toBe(objective)
  expect(plan.data_origin).toBe('solver')
  expect(plan.validation.status).toBe('passed')
  expect(new Set(plan.sorties.flatMap((s) => s.cargo_ids)).size).toBe(32)
  return plan
}

async function selectSceneOnLoad(page: Page, scene: Scenario, plan?: Plan) {
  await page.addInitScript(
    ({ id, planId }) => {
      if (!localStorage.getItem('yuanhang-scenario')) localStorage.setItem('yuanhang-scenario', id)
      if (planId && !localStorage.getItem(`yuanhang-plan-${id}`))
        localStorage.setItem(`yuanhang-plan-${id}`, planId)
    },
    { id: scene.scenario_id, planId: plan?.plan_id },
  )
}

async function navigate(page: Page, label: string) {
  if (!(await page.locator('.sidebar').isVisible()))
    await page.getByRole('button', { name: '打开导航', exact: true }).click()
  await page.locator('.sidebar nav').getByRole('button', { name: label, exact: true }).click()
}

test.beforeAll(async ({ request }) => {
  source = await compact(request)
  const response = await request.post(`/api/v1/scenarios/${source.scenario_id}/snapshots`, {
    data: { expected_state_version: source.state_version },
  })
  expect(response.status()).toBe(201)
  snapshot = await response.json()
  timePlan = await compute(request, snapshot, 'time')
  energyPlan = await compute(request, snapshot, 'energy')
  expect(energyPlan.plan_id).not.toBe(timePlan.plan_id)
})

test.beforeEach(async ({ page }) => {
  const errors: string[] = []
  pageErrors.set(page, errors)
  page.on('pageerror', (error) => errors.push(error.stack || error.message))
})

test.afterEach(async ({ page }, testInfo) => {
  const errors = pageErrors.get(page) || []
  await testInfo.attach('experience-page-errors', {
    body: JSON.stringify(errors, null, 2),
    contentType: 'application/json',
  })
  expect(errors).toEqual([])
  pageErrors.delete(page)
})

test('experience 本机档案与主题持久化，教程hash刷新/返回和390导航可用', async ({ page }) => {
  await selectSceneOnLoad(page, source)
  await page.goto('/#/guide')
  await expect(page.locator('.guide-page')).toBeVisible()
  await page.getByRole('button', { name: '账户与本机档案', exact: true }).click()
  const dialog = page.getByRole('dialog', { name: '我的本机档案' })
  await expect(dialog).toContainText('不创建服务器账户')
  await dialog.locator('input[name="displayName"]').fill('  林舟  ')
  await dialog.locator('input[name="team"]').fill('援航体验组')
  await dialog.locator('input[name="role"]').fill('算法调度')
  await dialog.getByRole('button', { name: '曙光琥珀', exact: true }).click()
  await dialog.getByRole('button', { name: '保存档案', exact: true }).click()
  await expect(page.locator('.profile strong')).toHaveText('林舟')
  await page.getByRole('button', { name: '切换浅色主题', exact: true }).click()
  await page.getByRole('button', { name: '暂停动态背景', exact: true }).click()
  await expect(page.locator('.guide-hero-orbits')).toHaveCSS('animation-play-state', 'paused')
  await page.reload()
  await expect(page).toHaveURL(/#\/guide$/)
  await expect(page.locator('.guide-page')).toBeVisible()
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'light')
  await expect(page.locator('html')).toHaveAttribute('data-motion', 'off')
  await expect(page.locator('.profile strong')).toHaveText('林舟')
  await expect(page.locator('.workspace-switch strong')).toHaveText('援航体验组')
  await page.getByLabel('搜索使用问题', { exact: true }).fill('卫星')
  await expect(page.locator('.guide-faq-list article')).toHaveCount(1)
  await page.locator('.guide-faq-list h4 button').click()
  await expect(page.locator('.guide-faq-list article > p')).toBeVisible()
  await page.getByRole('tab', { name: 'GeoTIFF DEM', exact: true }).click()
  await expect(page.getByRole('tabpanel')).toContainText('16 MiB')
  await page.locator('.guide-step-nav button').nth(1).click()
  await page.locator('.guide-step-bottom .button-primary').click()
  await expect(page).toHaveURL(/#\/scenario$/)
  await page.goBack()
  await expect(page).toHaveURL(/#\/guide$/)
  await expect(page.locator('.guide-page')).toBeVisible()

  await page.setViewportSize({ width: 390, height: 844 })
  await page.getByRole('button', { name: '打开导航', exact: true }).click()
  await expect(page.locator('.sidebar.mobile-open')).toBeVisible()
  await expect(page.locator('.sidebar .profile strong')).toBeVisible()
  await expect(page.locator('.sidebar .profile small')).toContainText('算法调度')
  await page.keyboard.press('Escape')
  await expect(page.locator('.sidebar')).toBeHidden()
  await page.getByRole('button', { name: '打开导航', exact: true }).click()
  await page.getByRole('button', { name: '关闭导航', exact: true }).click({
    position: { x: 370, y: 250 },
  })
  await expect(page.locator('.sidebar')).toBeHidden()
  await navigate(page, '历史档案')
  await expect(page).toHaveURL(/#\/history$/)
  await expect(page.locator('.sidebar')).toBeHidden()
  expect(await page.locator('body').evaluate((e) => e.scrollWidth <= innerWidth + 1)).toBe(true)
})

test('experience 真实同快照双策略保存到历史，JSON导出与方案交换保持身份', async ({
  page,
  request,
}, testInfo) => {
  await selectSceneOnLoad(page, source)
  await page.goto('/#/history')
  await expect(page.locator('.archive-plan-card')).toHaveCount(2)
  await page.getByLabel('搜索历史方案', { exact: true }).fill(timePlan.plan_id)
  await expect(page.locator('.archive-plan-card')).toHaveCount(1)
  const url = await page.locator('.archive-download').getAttribute('href')
  expect(url).toBeTruthy()
  const exported = await request.get(url!)
  expect(exported.status()).toBe(200)
  const exportedPlan: Plan = await exported.json()
  // The raw JSON export preserves Python's +00:00 suffix; the typed GET uses Z.
  // Normalize only that equivalent UTC spelling, retaining fractional precision
  // and deep-checking every other Plan field (including all entity identities).
  const canonicalUtc = (value: string) => {
    expect(value).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|\+00:00)$/)
    expect(Number.isFinite(Date.parse(value))).toBe(true)
    return value.replace(/\+00:00$/, 'Z')
  }
  expect({ ...exportedPlan, generated_at: canonicalUtc(exportedPlan.generated_at) }).toEqual({
    ...timePlan,
    generated_at: canonicalUtc(timePlan.generated_at),
  })
  await page.getByLabel('搜索历史方案', { exact: true }).fill('not-an-existing-plan')
  await expect(page.getByText('没有匹配的方案', { exact: true })).toBeVisible()
  await page.getByLabel('搜索历史方案', { exact: true }).fill('')
  for (const tab of ['计算记录', '事件时间线', '场景库', '输入版本', '方案档案']) {
    await page.getByRole('tab', { name: tab, exact: true }).click()
    await expect(page.getByRole('tab', { name: tab, exact: true })).toHaveAttribute(
      'aria-selected',
      'true',
    )
  }
  await navigate(page, '方案对比')
  await expect(page.getByRole('button', { name: '导出完整对比', exact: true })).toBeEnabled()
  await expect(page.locator('.comparison-notice')).toContainText('同快照')
  const before = [
    await page.getByLabel('方案对比A', { exact: true }).inputValue(),
    await page.getByLabel('方案对比B', { exact: true }).inputValue(),
  ]
  expect(new Set(before)).toEqual(new Set([timePlan.plan_id, energyPlan.plan_id]))
  await page.getByRole('button', { name: '交换对比方案', exact: true }).click()
  await expect(page.getByLabel('方案对比A', { exact: true })).toHaveValue(before[1])
  await expect(page.getByLabel('方案对比B', { exact: true })).toHaveValue(before[0])
  const ready = page.waitForEvent('download')
  await page.getByRole('button', { name: '导出完整对比', exact: true }).click()
  const download = await ready
  const output = JSON.parse(await fs.readFile((await download.path())!, 'utf8'))
  expect(output.plan_a.plan_id).toBe(before[1])
  expect(output.plan_b.plan_id).toBe(before[0])
  expect(output.plan_a.snapshot_id).toBe(snapshot.snapshot_id)
  expect(output.plan_b.snapshot_id).toBe(snapshot.snapshot_id)
  expect(output.plan_a.validation.status).toBe('passed')
  expect(output.plan_b.validation.status).toBe('passed')
  expect(output.comparison.same_snapshot).toBe(true)
  expect(output.comparison.comparable).toBe(true)
  await testInfo.attach('experience-real-plan-comparison', {
    body: JSON.stringify(output, null, 2),
    contentType: 'application/json',
  })
  expect(await (await request.get(`/api/v1/scenarios/${source.scenario_id}`)).json()).toEqual(
    source,
  )
})

test('experience 实际保存输入版本后，只读预览和下载旧JSON不覆盖当前版本', async ({
  page,
  request,
}) => {
  const original = await compact(request)
  const edited = structuredClone(original)
  edited.name = 'experience 版本来源检查'
  edited.cargo_items[0].mass_kg += 0.25
  const saved = await request.put(`/api/v1/scenarios/${original.scenario_id}`, {
    data: { expected_state_version: original.state_version, scenario: edited },
  })
  expect(saved.status()).toBe(200)
  const current: Scenario = await saved.json()
  expect(current.state_version).toBe(2)
  const versions = await request.get(`/api/v1/scenarios/${original.scenario_id}/versions`)
  expect(versions.status()).toBe(200)
  const summaries = await versions.json()
  expect(summaries.map((v: { state_version: number }) => v.state_version).sort()).toEqual([1, 2])
  expect(new Set(summaries.map((v: { content_hash: string }) => v.content_hash)).size).toBe(2)
  expect(
    await (await request.get(`/api/v1/scenarios/${original.scenario_id}/versions/1`)).json(),
  ).toEqual(original)
  await selectSceneOnLoad(page, current)
  const writes: string[] = []
  page.on('request', (r) => {
    if (r.url().includes('/api/') && !['GET', 'HEAD', 'OPTIONS'].includes(r.method()))
      writes.push(`${r.method()} ${r.url()}`)
  })
  await page.goto('/#/history')
  await page.getByRole('tab', { name: '输入版本', exact: true }).click()
  await expect(page.locator('.archive-table tbody tr')).toHaveCount(2)
  const oldRow = page.locator('.archive-table tbody tr').filter({
    has: page.getByText('v1', { exact: true }),
  })
  await oldRow.getByRole('button', { name: '查看版本', exact: true }).click()
  const dialog = page.getByRole('dialog', { name: '输入版本 v1 · 只读预览' })
  await expect(dialog).toBeVisible()
  await expect(dialog).toContainText('不执行恢复、不写入当前场景')
  await expect(dialog.locator('.archive-version-summary strong')).toHaveText(original.name)
  await dialog.locator('summary').click()
  const preview = JSON.parse(await dialog.locator('pre').innerText())
  expect(preview).toEqual(original)
  const ready = page.waitForEvent('download')
  await dialog.getByRole('button', { name: '下载该版本JSON', exact: true }).click()
  const download = await ready
  expect(JSON.parse(await fs.readFile((await download.path())!, 'utf8'))).toEqual(original)
  await dialog.getByRole('button', { name: '关闭弹窗', exact: true }).click()
  await page.reload()
  await expect(page).toHaveURL(/#\/history$/)
  expect(await (await request.get(`/api/v1/scenarios/${original.scenario_id}`)).json()).toEqual(
    current,
  )
  expect(writes).toEqual([])
})

test('experience 选择非最新历史Plan后刷新，保留原Plan和快照身份', async ({ page, request }) => {
  await selectSceneOnLoad(page, source)
  await page.goto('/#/workspace')
  const selector = page.getByLabel('选择历史方案', { exact: true })
  await expect(selector).toHaveValue(energyPlan.plan_id)
  await selector.selectOption(timePlan.plan_id)
  await expect(selector).toHaveValue(timePlan.plan_id)
  await expect(page.getByTestId('sortie-card')).toHaveCount(timePlan.sorties.length)
  expect(
    await page.evaluate((id) => localStorage.getItem(`yuanhang-plan-${id}`), source.scenario_id),
  ).toBe(timePlan.plan_id)
  await page.reload()
  await expect(selector).toHaveValue(timePlan.plan_id)
  await expect(page.getByTestId('sortie-card')).toHaveCount(timePlan.sorties.length)
  await navigate(page, '新手教程')
  await page.goBack()
  await expect(page).toHaveURL(/#\/workspace$/)
  await expect(selector).toHaveValue(timePlan.plan_id)
  expect(await (await request.get(`/api/v1/plans/${timePlan.plan_id}`)).json()).toEqual(timePlan)
  expect(await (await request.get(`/api/v1/snapshots/${snapshot.snapshot_id}`)).json()).toEqual(
    snapshot,
  )
})

test('experience 大屏真实DEM与架次剖面切换，无DEM无Plan时保留明确空态', async ({
  page,
  request,
}, testInfo) => {
  await selectSceneOnLoad(page, source, timePlan)
  await page.goto('/#/workspace')
  await expect(page.getByLabel('选择历史方案', { exact: true })).toHaveValue(timePlan.plan_id)
  const firstProfile = page.waitForResponse(
    (r) =>
      r.status() === 200 &&
      r.url().includes(`/plans/${timePlan.plan_id}/flight-profile?`) &&
      new URL(r.url()).searchParams.get('sortie_id') === timePlan.sorties[0].sortie_id,
  )
  await navigate(page, '数据大屏')
  await expect(page.getByRole('button', { name: '放大三维地形', exact: true })).toBeEnabled()
  await expect(page.locator('.terrain-scene-canvas canvas')).toBeVisible()
  await expect(page.locator('.va-chart canvas')).toHaveCount(8)
  const profile1 = await (await firstProfile).json()
  expect(profile1.plan_id).toBe(timePlan.plan_id)
  expect(profile1.snapshot_id).toBe(snapshot.snapshot_id)
  expect(profile1.terrain_sha256).toBe(snapshot.scenario.terrain.sha256)
  expect(profile1.legs.some((l: { terrain_checked: boolean }) => l.terrain_checked)).toBe(true)
  const summary = page.locator('.va-profile-summary')
  await expect(summary).toBeVisible()
  const before = await summary.innerText()
  const secondSortie = timePlan.sorties.find((s) => s.sortie_id !== profile1.sortie_id)!
  const secondProfile = page.waitForResponse(
    (r) =>
      r.status() === 200 &&
      r.url().includes(`/plans/${timePlan.plan_id}/flight-profile?`) &&
      new URL(r.url()).searchParams.get('sortie_id') === secondSortie.sortie_id,
  )
  await page.getByLabel('高程分析架次', { exact: true }).selectOption(secondSortie.sortie_id)
  const profile2 = await (await secondProfile).json()
  expect(profile2.sortie_id).toBe(secondSortie.sortie_id)
  expect(profile2.snapshot_id).toBe(snapshot.snapshot_id)
  await expect(summary).not.toHaveText(before)
  await expect(page.locator('.va-profile-note')).toContainText('不是实飞记录')
  await expect(page.locator('.va-profile-note')).toContainText('采样展示不替代完整净空检查')
  await testInfo.attach('experience-flight-profiles', {
    body: JSON.stringify({ first: profile1, second: profile2 }, null, 2),
    contentType: 'application/json',
  })

  const empty = structuredClone(source)
  empty.name = 'experience 无DEM输入'
  empty.data_origin = 'user_input'
  empty.policy.requires_terrain = false
  empty.terrain = {
    status: 'not_evaluated',
    asset_id: null,
    sha256: null,
    horizontal_crs: null,
    vertical_datum: null,
  }
  const imported = await request.post('/api/v1/scenarios/import', { data: empty })
  expect(imported.status()).toBe(201)
  const noDem: Scenario = await imported.json()
  await page.evaluate((id) => localStorage.setItem('yuanhang-scenario', id), noDem.scenario_id)
  // Already on this URL: goto would be a same-document navigation and would not
  // re-read the selected scene from localStorage. Exercise a real application load.
  await page.reload()
  await expect(page).toHaveURL(/#\/analysis$/)
  await expect(page.getByRole('combobox', { name: '选择场景', exact: true })).toHaveValue(
    noDem.scenario_id,
  )
  await expect(page.getByText('为场景导入真实地形', { exact: true })).toBeVisible()
  await expect(page.getByText('调度结果图将在真实计算后解锁', { exact: true })).toBeVisible()
  await expect(page.locator('.terrain-scene-canvas canvas')).toHaveCount(0)
  await expect(page.locator('.va-profile-panel')).toHaveCount(0)
  await expect(page.locator('.va-chart canvas')).toHaveCount(3)
  expect(await (await request.get(`/api/v1/scenarios/${noDem.scenario_id}/plans`)).json()).toEqual(
    [],
  )
})
