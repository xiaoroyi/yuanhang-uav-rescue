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
  await page.locator('input[type=file]').setInputFiles({
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
