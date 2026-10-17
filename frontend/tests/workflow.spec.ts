import { test, expect, type Page } from '@playwright/test'
import fs from 'node:fs/promises'
import path from 'node:path'

async function solve(page: Page) {
  await page.getByRole('button', { name: /^(生成真实方案|重新求解)$/ }).click()
  await expect(page.locator('.job-banner')).toBeVisible()
  await expect(page.locator('.job-banner')).toBeHidden({ timeout: 45000 })
  await expect(page.getByTestId('sortie-card').first()).toBeVisible()
}

async function screenshot(page: Page, name: string) {
  await expect(page.locator('.toast')).toHaveCount(0, { timeout: 12000 })
  await page.mouse.move(1100, 50)
  await page.locator('.main-content').evaluate((element) => {
    element.scrollTop = 0
  })
  await page.evaluate(() => document.fonts.ready)
  await fs.mkdir(path.resolve('../evidence/browser/verified'), { recursive: true })
  await page.screenshot({ path: path.resolve(`../evidence/browser/verified/${name}.png`) })
}

test.beforeEach(async ({ request, page }) => {
  const response = await request.post('/api/v1/scenarios/examples', {
    data: { example: 'compact' },
  })
  expect(response.status()).toBe(201)
  const scene = await response.json()
  await page.addInitScript((id) => localStorage.setItem('yuanhang-scenario', id), scene.scenario_id)
  await page.goto('/')
  await expect(page.getByRole('button', { name: '生成真实方案', exact: true })).toBeVisible()
})

test('真实双策略、地图与甘特联动、计划回放、确认导出及历史恢复', async ({ page, request }) => {
  const errors: string[] = []
  page.on('pageerror', (e) => errors.push(e.message))
  page.on('console', (e) => {
    if (e.type() === 'error') errors.push(e.text())
  })
  await solve(page)
  await expect(page.locator('.map-mode')).toHaveText('题设DEM · 离线')
  const sceneId = await page.getByLabel('选择场景').inputValue()
  const plans = await (await request.get(`/api/v1/scenarios/${sceneId}/plans`)).json()
  const plan = await (await request.get(`/api/v1/plans/${plans[0].plan_id}`)).json()
  expect(new Set(plan.sorties.flatMap((s: { cargo_ids: string[] }) => s.cargo_ids)).size).toBe(32)
  await page.getByTestId('sortie-card').nth(1).click()
  await expect(page.locator('.sortie-detail .mono')).toHaveText(plan.sorties[1].sortie_id)
  await expect(page.locator('.timeline-bar.is-selected').first()).toBeVisible()
  await page.getByRole('button', { name: '播放计划回放', exact: true }).click()
  await expect(page.locator('.planned-aircraft').first()).toBeVisible()
  await page.getByRole('button', { name: '暂停计划回放', exact: true }).click()
  await screenshot(page, 'workspace-1440')
  await page.getByRole('button', { name: '真实计算此策略', exact: true }).click()
  await expect(page.locator('.job-banner')).toBeVisible()
  await expect(page.locator('.job-banner')).toBeHidden({ timeout: 45000 })
  await expect(page.locator('.strategy-metrics')).toHaveCount(2)
  const compared = await (await request.get(`/api/v1/scenarios/${sceneId}/plans`)).json()
  expect(compared.length).toBe(2)
  expect(compared[0].snapshot_id).toBe(compared[1].snapshot_id)
  await page.getByRole('button', { name: '检查报告', exact: true }).click()
  await expect(page.getByRole('dialog')).toContainText('声明范围内检查通过')
  await page.getByRole('dialog').getByRole('button', { name: '关闭弹窗' }).click()
  await page.getByRole('button', { name: '确认方案', exact: true }).click()
  await expect(page.locator('.toast').filter({ hasText: '方案已确认' })).toBeVisible()
  const download = page.waitForEvent('download')
  await page.getByRole('link', { name: '计划JSON', exact: true }).click()
  expect((await download).suggestedFilename()).toMatch(/\.json$/)
  await page.reload()
  await expect(page.getByTestId('sortie-card').first()).toBeVisible()
  await page.setViewportSize({ width: 1280, height: 720 })
  await screenshot(page, 'workspace-1280')
  expect(errors).toEqual([])
})

test('编辑输入使旧方案失效，导入预览创建新场景', async ({ page, request }) => {
  await solve(page)
  const originalId = await page.getByLabel('选择场景').inputValue()
  await page.getByRole('button', { name: '场景与资源', exact: true }).click()
  await page.getByRole('button', { name: /^编辑S001-MED-01$/ }).click()
  await page.getByLabel('质量 / kg', { exact: true }).fill('5.5')
  await page.getByRole('button', { name: '保存修改', exact: true }).click()
  await expect(page.getByRole('dialog')).toBeHidden()
  await screenshot(page, 'scenario-1440')
  await page.getByRole('button', { name: '调度工作台', exact: true }).click()
  await expect(page.locator('.alert-amber')).toContainText('场景已更新为 v2')
  await expect(page.getByRole('button', { name: '确认方案', exact: true })).toBeDisabled()
  await page.getByRole('button', { name: '箱件', exact: true }).click()
  await expect(page.locator('.cargo-row').filter({ hasText: 'S001-MED-01' })).toContainText('3 kg')
  const scene = await (await request.get(`/api/v1/scenarios/${originalId}`)).json()
  expect(scene.cargo_items[0].mass_kg).toBe(5.5)
  await page.getByRole('button', { name: '场景与资源', exact: true }).click()
  await page.locator('.resource-toolbar input[type=file]').setInputFiles({
    name: 'scene.json',
    mimeType: 'application/json',
    buffer: Buffer.from(JSON.stringify(scene)),
  })
  await expect(page.getByRole('dialog')).toContainText('导入预览')
  await page.getByRole('button', { name: '确认导入为新场景', exact: true }).click()
  await expect(page.getByRole('dialog')).toBeHidden()
  await expect(page.getByLabel('选择场景')).not.toHaveValue(originalId)
  const imported = await (
    await request.get('/api/v1/scenarios/' + (await page.getByLabel('选择场景').inputValue()))
  ).json()
  expect(imported.data_origin).toBe('user_input')
  expect(imported.cargo_items[0].mass_kg).toBe(5.5)
})

test('真实故障重规划保留旧方案，展示新旧变化', async ({ page, request }) => {
  await solve(page)
  const sceneId = await page.getByLabel('选择场景').inputValue()
  const initial = await (await request.get(`/api/v1/scenarios/${sceneId}/plans`)).json()
  await page.getByRole('button', { name: '事件复盘', exact: true }).click()
  await page.getByLabel('故障机体').selectOption('U01')
  await page.getByRole('button', { name: '记录故障并重规划', exact: true }).click()
  await expect(page.locator('.job-banner')).toBeVisible()
  await expect(page.locator('.job-banner')).toBeHidden({ timeout: 45000 })
  await expect(page.locator('.comparison-cards')).toBeVisible()
  await expect(page.locator('.event-history')).toContainText('U01 退出')
  const plans = await (await request.get(`/api/v1/scenarios/${sceneId}/plans`)).json()
  expect(plans.length).toBe(2)
  const latest = await (await request.get(`/api/v1/plans/${plans[0].plan_id}`)).json()
  expect(latest.sorties.every((r: { drone_id: string }) => r.drone_id !== 'U01')).toBe(true)
  expect(latest.parent_plan_id).toBe(initial[0].plan_id)
  expect((await request.get(`/api/v1/plans/${initial[0].plan_id}`)).ok()).toBe(true)
  await screenshot(page, 'replan-1440')
  await page.setViewportSize({ width: 1280, height: 720 })
  await screenshot(page, 'replan-1280')
})

test('手机窄屏仍可切页和运行计算', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await solve(page)
  await page.getByRole('button', { name: '打开导航', exact: true }).click()
  await page.getByRole('button', { name: '场景与资源', exact: true }).click()
  await expect(page.locator('.resource-panel')).toBeVisible()
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(
    true,
  )
  await screenshot(page, 'scenario-mobile')
})

test('资源分析绑定基线快照，增配试算创建独立场景并真实求解', async ({ page, request }) => {
  const errors: string[] = []
  page.on('pageerror', (error) => errors.push(error.message))
  await solve(page)
  const sceneId = await page.getByLabel('选择场景').inputValue()
  const before = await (await request.get('/api/v1/scenarios/' + sceneId)).json()
  await page.getByRole('button', { name: '事件复盘', exact: true }).click()
  await page.getByRole('button', { name: '资源分析与试算', exact: true }).click()
  await expect(page.locator('.utilization-chart canvas')).toBeVisible()
  await expect(page.locator('.analysis-kpis')).toContainText('硬截止检查')
  const receiptResponse = page.waitForResponse(
    (response) => response.url().endsWith('/what-if') && response.request().method() === 'POST',
  )
  await page.getByRole('button', { name: '创建场景并真实试算', exact: true }).click()
  const receipt = await (await receiptResponse).json()
  expect(receipt.scenario.scenario_id).not.toBe(sceneId)
  await expect(page.locator('.trial-result')).toContainText('已真实计算', { timeout: 45000 })
  expect(await (await request.get('/api/v1/scenarios/' + sceneId)).json()).toEqual(before)
  expect(receipt.scenario.drones.length).toBe(before.drones.length + 1)
  expect(receipt.scenario.batteries.length).toBe(before.batteries.length + 1)
  await screenshot(page, 'resource-analysis-1440')
  await page.setViewportSize({ width: 1280, height: 720 })
  await screenshot(page, 'resource-analysis-1280')
  await page.getByRole('button', { name: '打开试算场景', exact: true }).click()
  await expect(page.getByLabel('选择场景')).toHaveValue(receipt.scenario.scenario_id)
  await expect(page.getByTestId('sortie-card').first()).toBeVisible()
  expect(errors).toEqual([])
})

test('三档压力测试分别真实计算，刷新后保留各情景历史', async ({ page, request }) => {
  await solve(page)
  const sourceId = await page.getByLabel('选择场景').inputValue()
  const before = await (await request.get('/api/v1/scenarios/' + sourceId)).json()
  await page.getByRole('button', { name: '事件复盘', exact: true }).click()
  await page.getByRole('button', { name: '资源分析与试算', exact: true }).click()
  await page.getByRole('button', { name: '运行3档压力测试', exact: true }).click()
  await expect(page.getByTestId('experiment-row')).toHaveCount(3, { timeout: 30000 })
  await expect
    .poll(
      async () => {
        const rows = await (await request.get(`/api/v1/scenarios/${sourceId}/what-if`)).json()
        return (
          rows.length === 3 &&
          rows.every(
            (r: { job: { job_state: string } | null }) =>
              r.job && ['completed', 'failed', 'canceled'].includes(r.job.job_state),
          )
        )
      },
      { timeout: 45000 },
    )
    .toBe(true)
  const history = await (await request.get(`/api/v1/scenarios/${sourceId}/what-if`)).json()
  expect(new Set(history.map((r: { scenario_id: string }) => r.scenario_id)).size).toBe(3)
  expect(
    history
      .map(
        (r: { origin: { parameters: { energy_multiplier: number } } }) =>
          r.origin.parameters.energy_multiplier,
      )
      .sort(),
  ).toEqual([1, 1.1, 1.2])
  expect(
    history.every(
      (r: { job: { job_state: string }; plan: { data_origin: string } | null }) =>
        r.job.job_state === 'completed' && (!r.plan || r.plan.data_origin === 'solver'),
    ),
  ).toBe(true)
  expect(await (await request.get('/api/v1/scenarios/' + sourceId)).json()).toEqual(before)
  await page.locator('.experiment-history').scrollIntoViewIfNeeded()
  await expect(page.locator('.toast')).toHaveCount(0, { timeout: 12000 })
  await page.screenshot({
    path: path.resolve('../evidence/browser/verified/stress-history-1440.png'),
  })
  await page.reload()
  await page.getByRole('button', { name: '事件复盘', exact: true }).click()
  await page.getByRole('button', { name: '资源分析与试算', exact: true }).click()
  await expect(page.getByTestId('experiment-row')).toHaveCount(3)
})

test('任务刷新恢复，重新载入页面不重复提交求解', async ({ page, request }) => {
  const sceneId = await page.getByLabel('选择场景').inputValue()
  await page.getByRole('button', { name: '生成真实方案', exact: true }).click()
  await expect(page.locator('.job-banner')).toBeVisible()
  await page.reload()
  await expect(page.getByTestId('sortie-card').first()).toBeVisible({ timeout: 45000 })
  const jobs = await (await request.get(`/api/v1/scenarios/${sceneId}/solve-jobs`)).json()
  expect(jobs.length).toBe(1)
  expect(jobs[0].job_state).toBe('completed')
  expect(jobs[0].has_validated_plan).toBe(true)
})

test('打印报告包含真实任务并可离线保存PDF', async ({ page }) => {
  await solve(page)
  const popup = page.waitForEvent('popup')
  await page.getByRole('link', { name: '打印报告', exact: true }).click()
  const report = await popup
  await expect(report.getByRole('heading', { level: 1 })).toHaveText('援航 · 运输调度与资源报告')
  await expect(report.locator('table')).toHaveCount(4)
  await expect(report.locator('body')).toContainText('逐箱物资追踪')
  await expect(report.locator('.identity')).toContainText('输入Hash')
  await report.screenshot({
    path: path.resolve('../evidence/browser/verified/print-report-screen.png'),
  })
  await report.pdf({
    path: path.resolve('../evidence/browser/verified/print-report.pdf'),
    format: 'A4',
    landscape: true,
    printBackground: true,
    preferCSSPageSize: true,
  })
  await report.close()
})

test('深入优化保留同快照基线，刷新后继续真实计算', async ({ page, request }) => {
  await solve(page)
  const sceneId = await page.getByLabel('选择场景').inputValue()
  const old = (await (await request.get(`/api/v1/scenarios/${sceneId}/plans`)).json())[0]
  await page.getByRole('button', { name: '深入优化30秒', exact: true }).click()
  await expect(page.locator('.job-banner')).toBeVisible()
  await page.reload()
  await expect(page.locator('.job-banner')).toBeVisible()
  await expect(page.locator('.job-banner')).toBeHidden({ timeout: 45000 })
  await expect(page.getByTestId('sortie-card').first()).toBeVisible()
  const plans = await (await request.get(`/api/v1/scenarios/${sceneId}/plans`)).json()
  expect(plans).toHaveLength(2)
  expect(plans[0].snapshot_id).toBe(old.snapshot_id)
  expect(plans[0].algorithm_mode).toBe('improve')
  expect(plans[0].source_plan_id).toBe(old.plan_id)
  const jobs = await (await request.get(`/api/v1/scenarios/${sceneId}/solve-jobs`)).json()
  expect(jobs).toHaveLength(2)
  expect(jobs.every((j: { job_state: string }) => j.job_state === 'completed')).toBe(true)
  const current = await (await request.get(`/api/v1/plans/${plans[0].plan_id}`)).json()
  expect(current.validation.status).toBe('passed')
  await screenshot(page, 'deep-optimization-1440')
})

test('限制区保存新版本，真实绕行并沿折线回放', async ({ page, request }) => {
  const errors: string[] = []
  page.on('pageerror', (e) => errors.push(e.message))
  await solve(page)
  const sceneId = await page.getByLabel('选择场景').inputValue()
  const old = (await (await request.get(`/api/v1/scenarios/${sceneId}/plans`)).json())[0]
  await page.getByRole('button', { name: '场景与资源', exact: true }).click()
  await page.getByRole('button', { name: '管理限制区', exact: true }).click()
  await expect(page.getByRole('dialog')).toBeVisible()
  await page.getByRole('button', { name: '加入草稿', exact: true }).click()
  await expect(page.getByLabel('限制区JSON')).toContainText('临时限制区')
  await page.screenshot({ path: path.resolve('../evidence/browser/verified/zone-editor-1440.png') })
  await page.getByRole('button', { name: '保存限制区', exact: true }).click()
  await expect(page.getByRole('dialog')).toBeHidden()
  await expect(page.locator('.zone-saved-list')).toContainText('临时限制区')
  await page.getByRole('button', { name: '调度工作台', exact: true }).click()
  await expect(page.getByRole('button', { name: '确认方案', exact: true })).toBeDisabled()
  await solve(page)
  const plans = await (await request.get(`/api/v1/scenarios/${sceneId}/plans`)).json()
  expect(plans).toHaveLength(2)
  expect(plans[0].snapshot_id).not.toBe(old.snapshot_id)
  const plan = await (await request.get(`/api/v1/plans/${plans[0].plan_id}`)).json()
  expect(plan.model_scope).toContain('restricted_zone')
  expect(
    plan.sorties.some(
      (r: { visits: unknown[]; route_geometry: { coordinates: unknown[] } }) =>
        r.route_geometry.coordinates.length > r.visits.length + 2,
    ),
  ).toBe(true)
  expect(
    plan.validation.checks.some(
      (c: { code: string; status: string }) =>
        c.code === 'restricted_zone' && c.status === 'passed',
    ),
  ).toBe(true)
  await page.getByRole('button', { name: '检查报告', exact: true }).click()
  await expect(page.getByRole('dialog')).toContainText('限制区与缓冲')
  await page.getByRole('dialog').getByRole('button', { name: '关闭弹窗' }).click()
  await screenshot(page, 'zone-detour-1440')
  await page.getByRole('button', { name: '播放计划回放', exact: true }).click()
  await expect(page.locator('.planned-aircraft').first()).toBeVisible()
  await page.getByRole('button', { name: '暂停计划回放', exact: true }).click()
  expect(errors).toEqual([])
})

test('GeoTIFF资产上传绑定，真实Worker使用新DEM并恢复历史', async ({ page, request }) => {
  const errors: string[] = []
  page.on('pageerror', (e) => errors.push(e.message))
  await solve(page)
  const sceneId = await page.getByLabel('选择场景').inputValue()
  const old = (await (await request.get(`/api/v1/scenarios/${sceneId}/plans`)).json())[0]
  await page.getByRole('button', { name: '场景与资源', exact: true }).click()
  await page.getByRole('button', { name: '管理DEM资产', exact: true }).click()
  await page.getByLabel('垂直基准 / 数据说明').fill('contest_provided_elevation_reference')
  await page.getByLabel('我确认高程值为米，基准声明与来源一致').check()
  const folder = path.resolve('../references/modeling/data/terrain')
  const filename = (await fs.readdir(folder)).find((name) => name.endsWith('.tif'))!
  await page.getByTestId('terrain-file').setInputFiles(path.join(folder, filename))
  await expect(page.getByLabel('DEM资产', { exact: true })).toHaveValue(/^DEM-/, { timeout: 30000 })
  await page.getByLabel('绑定时从DEM提取基地与需求点高程').uncheck()
  await expect(page.locator('.toast')).toHaveCount(0, { timeout: 12000 })
  await page.screenshot({
    path: path.resolve('../evidence/browser/verified/terrain-assets-1440.png'),
  })
  await page.setViewportSize({ width: 1280, height: 720 })
  await expect(
    page.getByRole('button', { name: '绑定DEM并保存新版本', exact: true }),
  ).toBeInViewport({ ratio: 0.95 })
  await page.screenshot({
    path: path.resolve('../evidence/browser/verified/terrain-assets-1280.png'),
  })
  await page.setViewportSize({ width: 1440, height: 900 })
  const download = page.waitForEvent('download')
  await page.getByRole('link', { name: '下载完整资产包', exact: true }).click()
  const savedPackage = await download
  expect(savedPackage.suggestedFilename()).toMatch(/\.yuanhang-dem\.zip$/)
  const packagePath = await savedPackage.path()
  const receipt = page.waitForResponse(
    (r) => r.url().endsWith('/terrain-assets/import-package') && r.request().method() === 'POST',
  )
  await page.getByTestId('terrain-package-file').setInputFiles(packagePath!)
  expect((await receipt).status()).toBe(201)
  await page.getByRole('button', { name: '绑定DEM并保存新版本', exact: true }).click()
  await expect(page.getByRole('dialog')).toBeHidden()
  const updated = await (await request.get(`/api/v1/scenarios/${sceneId}`)).json()
  expect(updated.state_version).toBe(2)
  expect(updated.terrain.asset_id).toMatch(/^DEM-/)
  await page.getByRole('button', { name: '调度工作台', exact: true }).click()
  await solve(page)
  await expect(page.locator('.map-mode')).toHaveText('本地DEM · 离线')
  const plans = await (await request.get(`/api/v1/scenarios/${sceneId}/plans`)).json()
  expect(plans).toHaveLength(2)
  expect(plans[0].snapshot_id).not.toBe(old.snapshot_id)
  const plan = await (await request.get(`/api/v1/plans/${plans[0].plan_id}`)).json()
  expect(
    plan.validation.checks.some(
      (c: { code: string; status: string }) => c.code === 'terrain' && c.status === 'passed',
    ),
  ).toBe(true)
  await screenshot(page, 'terrain-bound-workspace-1440')
  await page.reload()
  await expect(page.locator('.map-mode')).toHaveText('本地DEM · 离线')
  expect(errors).toEqual([])
})

test('有限准备工位与充电端口真实排程，等待在甘特与分析中分开显示', async ({ page, request }) => {
  await solve(page)
  const sceneId = await page.getByLabel('选择场景').inputValue()
  await page.getByRole('button', { name: '场景与资源', exact: true }).click()
  await page.getByRole('button', { name: '场景设置', exact: true }).click()
  await page.getByLabel('限制准备工位与充电端口').check()
  await page.getByLabel('准备工位 / 个', { exact: true }).fill('1')
  await page.getByLabel('充电端口 / 个', { exact: true }).fill('1')
  await page.getByRole('button', { name: '保存设置', exact: true }).click()
  await expect(page.getByRole('dialog')).toBeHidden()
  await page.getByRole('button', { name: '调度工作台', exact: true }).click()
  await solve(page)
  const summaries = await (await request.get(`/api/v1/scenarios/${sceneId}/plans`)).json()
  const plan = await (await request.get(`/api/v1/plans/${summaries[0].plan_id}`)).json()
  expect(plan.model_scope).toContain('ground_resource')
  const analysis = await (await request.get(`/api/v1/plans/${plan.plan_id}/analysis`)).json()
  expect(analysis.prep_peak).toBeLessThanOrEqual(1)
  expect(analysis.charge_peak).toBeLessThanOrEqual(1)
  expect(analysis.charge_wait_s).toBeGreaterThan(0)
  await page.locator('.timeline-panel').getByRole('button', { name: '电池', exact: true }).click()
  await expect(page.locator('.timeline-legend')).toContainText('等待充电端口')
  expect(
    await page
      .locator('.bar-wait')
      .evaluateAll((nodes) => nodes.some((n) => n.getBoundingClientRect().width > 1)),
  ).toBe(true)
  await screenshot(page, 'ground-calendars-1440')
  await page.getByTitle('展开时间轴', { exact: true }).click()
  await expect
    .poll(async () => (await page.locator('.timeline-expanded').boundingBox())?.height || 0)
    .toBeGreaterThan(400)
  await page.screenshot({
    path: path.resolve('../evidence/browser/verified/ground-timeline-expanded-1440.png'),
  })
  await page.getByTitle('收起', { exact: true }).click()
  await page.getByRole('button', { name: '检查报告', exact: true }).click()
  await expect(page.getByRole('dialog')).toContainText('准备峰值1/1')
  await page.getByRole('dialog').getByRole('button', { name: '关闭弹窗' }).click()
  await page.getByRole('button', { name: '确认方案', exact: true }).click()
  await expect(page.locator('.toast').filter({ hasText: '方案已确认' })).toBeVisible()
  await page.getByRole('button', { name: '事件复盘', exact: true }).click()
  await page.getByRole('button', { name: '资源分析与试算', exact: true }).click()
  await expect(page.locator('.analysis-kpis')).toContainText('实际并发 / 1个端口')
})

test('低SOC初始补能使用端口，并在甘特和打印报告保留窗口', async ({ page, request }) => {
  const sceneId = await page.getByLabel('选择场景').inputValue()
  const s = await (await request.get(`/api/v1/scenarios/${sceneId}`)).json()
  s.resource_limits = { prep_slots: 1, charging_ports: 1 }
  s.batteries[0].soc = 0.6
  for (const d of s.demands) if (d.hard_deadline_s !== null) d.hard_deadline_s = 100000
  const saved = await request.put(`/api/v1/scenarios/${sceneId}`, {
    data: { expected_state_version: 1, scenario: s },
  })
  expect(saved.ok()).toBe(true)
  await page.reload()
  await solve(page)
  await page.locator('.timeline-panel').getByRole('button', { name: '电池', exact: true }).click()
  await expect(page.locator('.initial-charge-bar')).toHaveCount(1)
  await screenshot(page, 'initial-charge-1440')
  await page.getByTitle('展开时间轴', { exact: true }).click()
  await page.screenshot({
    path: path.resolve('../evidence/browser/verified/initial-charge-timeline-1440.png'),
  })
  await page.getByTitle('收起', { exact: true }).click()
  const popup = page.waitForEvent('popup')
  await page.getByRole('link', { name: '打印报告', exact: true }).click()
  const report = await popup
  await expect(report.locator('body')).toContainText('初始补能与排队')
  await expect(report.locator('body')).toContainText('准备工位1个')
  await report.pdf({
    path: path.resolve('../evidence/browser/verified/initial-charge-report.pdf'),
    format: 'A4',
    landscape: true,
    printBackground: true,
    preferCSSPageSize: true,
  })
  await report.close()
})
