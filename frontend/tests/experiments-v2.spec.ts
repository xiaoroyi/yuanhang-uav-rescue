import { test, expect } from '@playwright/test'
import { createHash } from 'node:crypto'
import fs from 'node:fs/promises'
import type { Mission, ExperimentBundle } from '../src/api/operations'
import type { Scenario } from '../src/api/client'

test.setTimeout(180000)
test.use({ reducedMotion: 'reduce' })

test('V2 experiment page runs genuine strategy jobs, restores history and exports the exact worker evidence', async ({
  page,
  request,
}) => {
  const m: Mission = await (
    await request.post('/api/v1/missions', {
      data: {
        name: '浏览器评测输入 ' + Date.now(),
        template: 'compact',
        idempotency_key: crypto.randomUUID(),
      },
    })
  ).json()
  const original: Scenario = await (
    await request.get('/api/v1/scenarios/' + m.current_scenario_id)
  ).json()
  await page.goto('/#/experiments')
  await expect(page.getByRole('heading', { name: '演练评测', exact: true })).toBeVisible()
  await page.getByLabel('评测输入任务').selectOption(m.mission_id)
  await page.getByLabel('每例求解预算').selectOption('3')
  await page.getByLabel('评测随机种子').fill('11')
  const name = '同输入三偏好验收 ' + Date.now()
  await page.getByLabel('评测名称', { exact: true }).fill(name)
  await page.getByRole('button', { name: '开始真实评测', exact: true }).click()
  const heading = page.locator('.v2-experiment-heading')
  await expect(heading).toContainText(name)
  await expect(heading).toContainText('已完成', { timeout: 90000 })
  await expect(page.getByTestId('experiment-case')).toHaveCount(3)
  await expect(page.getByTestId('experiment-case').filter({ hasText: '已验证可行' })).toHaveCount(3)
  await expect(
    page.getByRole('img', { name: '评测真实候选时间能耗散点图', exact: true }),
  ).toBeVisible()
  expect(await (await request.get('/api/v1/scenarios/' + m.current_scenario_id)).json()).toEqual(
    original,
  )
  await page.locator('.v2-experiment-evidence summary').click()
  await expect(page.locator('.v2-experiment-evidence')).toContainText('CP-SAT 1 线程')
  for (const [width, height] of [
    [1440, 900],
    [1280, 720],
    [1024, 768],
  ]) {
    await page.setViewportSize({ width, height })
    await page.locator('.v2-experiments').evaluate((element) => {
      element.scrollTop = 0
    })
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(
      width,
    )
    await page.screenshot({
      path: `../evidence/redesign-v2/experiment-results-${width}.png`,
      fullPage: true,
    })
  }
  await page.getByRole('button', { name: '核对方案', exact: true }).first().click()
  await expect(page.getByRole('dialog')).toContainText('验证 passed')
  await expect(page.getByRole('dialog').locator('.map-canvas canvas')).toBeVisible()
  await expect(page.getByRole('dialog')).toHaveClass(/v2-dialog/)
  await expect(page.getByRole('dialog').locator('.rescue-map')).toHaveAttribute(
    'data-context',
    'true',
  )
  expect(
    await page
      .getByRole('dialog')
      .locator('.map-header')
      .evaluate((element) => getComputedStyle(element).backgroundImage),
  ).toBe('none')
  await page.screenshot({
    path: '../evidence/redesign-v2/experiment-plan-audit.png',
    fullPage: true,
  })
  await page.getByRole('dialog').getByRole('button', { name: '关闭弹窗', exact: true }).click()
  await page.getByRole('button', { name: '原始记录', exact: true }).click()
  await expect(page.getByRole('dialog').locator('pre')).toContainText('snapshot_id')
  await page.getByLabel('评测原始文件').selectOption({ index: 1 })
  await expect(page.getByRole('dialog').locator('pre')).toContainText('candidate_count')
  await page.getByRole('dialog').getByRole('button', { name: '关闭弹窗', exact: true }).click()
  const download = page.waitForEvent('download')
  await page.getByRole('link', { name: '完整证据', exact: true }).click()
  const file = await download
  const path = '../evidence/redesign-v2/EXPERIMENT_SMOKE/strategy-benchmark.json'
  await fs.mkdir('../evidence/redesign-v2/EXPERIMENT_SMOKE', { recursive: true })
  await file.saveAs(path)
  const bundle: ExperimentBundle = JSON.parse(await fs.readFile(path, 'utf8'))
  expect(bundle.run.cases).toHaveLength(3)
  expect(bundle.missing_artifacts).toEqual([])
  for (const a of bundle.artifacts) {
    const bytes = Buffer.from(a.content_base64, 'base64')
    expect(createHash('sha256').update(bytes).digest('hex')).toBe(a.content_sha256)
    expect(bytes.length).toBe(a.byte_count)
  }
  await page.reload()
  await expect(page.locator('.v2-experiment-heading')).toContainText(name)
  await expect(page.locator('.v2-experiment-heading')).toContainText('已完成')
})

test('V2 experiment failures keep their denominator and unknown metrics in the interface', async ({
  page,
  request,
}) => {
  const m: Mission = await (
    await request.post('/api/v1/missions', {
      data: {
        name: '无可用机队评测 ' + Date.now(),
        template: 'compact',
        idempotency_key: crypto.randomUUID(),
      },
    })
  ).json()
  const scene: Scenario = await (
    await request.get('/api/v1/scenarios/' + m.current_scenario_id)
  ).json()
  scene.drones.forEach((d) => (d.status = 'unavailable'))
  expect(
    (
      await request.put('/api/v1/scenarios/' + scene.scenario_id, {
        data: { expected_state_version: scene.state_version, scenario: scene },
      })
    ).ok(),
  ).toBeTruthy()
  const snap = await (
    await request.post(`/api/v1/scenarios/${scene.scenario_id}/snapshots`, {
      data: { expected_state_version: 2 },
    })
  ).json()
  const response = await request.post('/api/v1/experiments', {
    data: {
      name: '失败完整保留 ' + Date.now(),
      source_snapshot_id: snap.snapshot_id,
      suite: 'search',
      objective: 'time',
      objective_policy: 'tradeoff_v2',
      seeds: [2],
      time_limit_s: 3,
      idempotency_key: crypto.randomUUID(),
    },
  })
  expect(response.status()).toBe(202)
  const run = await response.json()
  await page.goto('/#/experiments')
  await expect(page.locator('.v2-experiment-heading')).toContainText(run.name)
  await expect(page.locator('.v2-experiment-heading')).toContainText('已完成', { timeout: 60000 })
  await expect(page.getByTestId('experiment-case')).toHaveCount(2)
  await expect(page.locator('.v2-experiment-chart')).toContainText('当前没有可验证方案')
  await expect(
    page.getByRole('img', { name: '评测真实候选时间能耗散点图', exact: true }),
  ).toHaveCount(0)
  await expect(page.getByRole('button', { name: '核对方案', exact: true }).first()).toBeDisabled()
  await expect(page.locator('.v2-experiment-metrics > div').nth(2)).toContainText('2')
  await page.screenshot({
    path: '../evidence/redesign-v2/experiment-failed-cases.png',
    fullPage: true,
  })
})
