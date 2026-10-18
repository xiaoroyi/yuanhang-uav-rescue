import { test, expect } from '@playwright/test'
import fs from 'node:fs/promises'
import type { Scenario, Plan, SolveJob } from '../src/api/client'
import type { Mission, Execution, Repair, ExecutionArchive } from '../src/api/operations'

test.setTimeout(180000)
test.use({ reducedMotion: 'reduce' })

test('V2 in-flight battery exit previews actual dependency repair differences before adopting the future program', async ({
  page,
  request,
}) => {
  const mission: Mission = await (
    await request.post('/api/v1/missions', {
      data: {
        name: '在飞备用电池退出演练 ' + Date.now(),
        template: 'compact',
        idempotency_key: crypto.randomUUID(),
      },
    })
  ).json()
  const scene: Scenario = await (
    await request.get('/api/v1/scenarios/' + mission.current_scenario_id)
  ).json()
  scene.demands = scene.demands.slice(0, 2)
  const dids = new Set(scene.demands.map((d) => d.demand_id))
  scene.cargo_items = scene.cargo_items.filter((c) => dids.has(c.demand_id))
  scene.demands.forEach((d) => {
    d.expected_deadline_s = null
    d.hard_deadline_s = null
  })
  scene.cargo_items.forEach((c) => {
    c.mass_kg = 25
    c.volume_l = 60
  })
  scene.drones = [scene.drones[0]]
  scene.batteries = scene.batteries.filter((b) => b.compatible_type_id === 'A')
  const put = await request.put('/api/v1/scenarios/' + scene.scenario_id, {
    data: { expected_state_version: scene.state_version, scenario: scene },
  })
  expect(put.ok()).toBeTruthy()
  const snap = await (
    await request.post(`/api/v1/scenarios/${scene.scenario_id}/snapshots`, {
      data: { expected_state_version: 2 },
    })
  ).json()
  const submitted: SolveJob = await (
    await request.post('/api/v1/solve-jobs', {
      data: { snapshot_id: snap.snapshot_id, objective_policy: 'tradeoff_v2', time_limit_s: 5 },
    })
  ).json()
  let job = submitted
  await expect
    .poll(
      async () => {
        job = await (await request.get('/api/v1/solve-jobs/' + submitted.job_id)).json()
        return job.job_state
      },
      { timeout: 45000 },
    )
    .toBe('completed')
  expect(job.has_validated_plan).toBeTruthy()
  const plan: Plan = await (await request.get('/api/v1/plans/' + job.plan_id)).json()
  expect(plan.sorties).toHaveLength(2)
  expect(
    (
      await request.post(`/api/v1/plans/${plan.plan_id}/confirm`, {
        data: { expected_state_version: 2, idempotency_key: crypto.randomUUID() },
      })
    ).ok(),
  ).toBeTruthy()
  let e: Execution = await (
    await request.post('/api/v1/executions', {
      data: {
        mission_id: mission.mission_id,
        confirmed_plan_id: plan.plan_id,
        expected_revision: mission.revision,
        idempotency_key: crypto.randomUUID(),
      },
    })
  ).json()
  const first = plan.sorties.toSorted((a, b) => a.prepare_start_s - b.prepare_start_s)[0]
  e = await (
    await request.post(`/api/v1/executions/${e.execution_id}/simulation/actions`, {
      data: {
        action: 'advance',
        target_time_s: first.takeoff_s + 1,
        expected_revision: e.revision,
        idempotency_key: crypto.randomUUID(),
      },
    })
  ).json()
  const future = plan.sorties.find((r) => r.prepare_start_s > e.time_s)!
  const frozenFacts = e.facts
  const original = e.telemetry[0]
  await page.goto('/#/missions/' + mission.mission_id + '/execute')
  await page.getByRole('button', { name: '上报变化', exact: true }).click()
  await page.getByLabel('变化类型').selectOption('battery.unavailable')
  await page.getByLabel('目标对象').selectOption(future.battery_id)
  await page.getByLabel('变化原因').fill('备用电池无法继续使用；首架次正在飞行，保留当前在机物资')
  await page.getByRole('button', { name: '记录事件并分析影响', exact: true }).click()
  await expect(page.getByRole('dialog')).toHaveCount(0)
  await page.getByRole('link', { name: /方案规划/ }).click()
  await expect(page.locator('.v2-validity-notice')).toContainText('待处理 1 项')
  await expect(page.getByRole('button', { name: '原快照检查 通过', exact: true })).toBeVisible()
  await page
    .locator('.v2-validity-notice')
    .getByRole('link', { name: '查看受影响任务与调整' })
    .click()
  await page.getByRole('button', { name: '查看影响链与架次', exact: true }).click()
  const impactDialog = page.getByRole('dialog')
  await expect(impactDialog.getByRole('region', { name: '事件资源依赖影响图' })).toContainText(
    '直接命中 1',
  )
  await impactDialog.getByLabel('显示全部架次').check()
  await expect(impactDialog.locator('.v2-impact-node')).toHaveCount(2)
  await expect(impactDialog.locator('.v2-impact-edge.drone')).toHaveCount(1)
  for (const [width, height] of [
    [1440, 900],
    [1280, 720],
  ]) {
    await page.setViewportSize({ width, height })
    await page.screenshot({
      path: `../evidence/redesign-v2/event-impact-${width}.png`,
      fullPage: true,
    })
  }
  await impactDialog
    .getByRole('button', { name: `核对 ${plan.plan_id} ${future.sortie_id}`, exact: true })
    .click()
  const futureInspector = page.getByRole('complementary', { name: '执行架次安排详情' })
  await expect(futureInspector).toContainText('当前未来安排 · 尚无装载事实')
  await expect(futureInspector).toContainText(future.cargo_ids[0])
  // Short screens deliberately collapse the bottom strip; use its explicit expanded view.
  await page.getByRole('button', { name: '查看完整排程', exact: true }).click()
  await expect(page.getByRole('dialog').locator('.ledger-selected').first()).toBeVisible()
  await page.getByRole('dialog').getByRole('button', { name: '关闭弹窗', exact: true }).click()
  await futureInspector.getByRole('button', { name: '核对原文航线与高程分析' }).click()
  await expect(page.getByRole('dialog')).toContainText('高程')
  await page.getByRole('dialog').getByRole('button', { name: '关闭弹窗', exact: true }).click()
  await futureInspector.getByRole('button', { name: '关闭架次详情' }).click()
  await page.getByLabel('剩余任务修复方法').selectOption('dependency')
  await page.getByRole('button', { name: '生成调整', exact: true }).click()
  const dialog = page.getByRole('dialog')
  await expect(dialog.getByRole('button', { name: '确认采纳模拟调整', exact: true })).toBeEnabled({
    timeout: 60000,
  })
  await expect(dialog.locator('.v2-repair-method')).toContainText('资源依赖局部修复')
  await expect(dialog.locator('.v2-repair-diff')).toContainText('换电池 1 箱')
  await expect(dialog.locator('.v2-repair-diff')).toContainText('时刻变化 1 箱')
  await dialog.getByText(/逐箱核对变化（/).click()
  await dialog.getByRole('button', { name: '核对架次', exact: true }).click()
  await expect(dialog.locator('.v2-repair-sortie')).toContainText(first.battery_id)
  await expect(dialog.locator('.v2-repair-sortie')).toContainText(future.cargo_ids[0])
  for (const [width, height] of [
    [1440, 900],
    [1280, 720],
  ]) {
    await page.setViewportSize({ width, height })
    await dialog.evaluate((el) => {
      el.scrollTop = 0
    })
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(
      width,
    )
    await page.screenshot({
      path: `../evidence/redesign-v2/dependency-battery-diff-${width}.png`,
      fullPage: true,
    })
  }
  const changes: Repair[] = await (
    await request.get(`/api/v1/executions/${e.execution_id}/plan-changes`)
  ).json()
  expect(changes[0].calculation_method).toBe('dependency_local')
  expect(changes[0].diff?.battery_reassigned_quantity).toBe(1)
  await dialog.getByRole('button', { name: '确认采纳模拟调整', exact: true }).click()
  await expect(dialog.locator('.v2-check-summary')).toContainText('状态 applied', {
    timeout: 15000,
  })
  await dialog.getByRole('button', { name: '关闭详情', exact: true }).click()
  e = await (await request.get('/api/v1/executions/' + e.execution_id)).json()
  expect(e.facts).toEqual(frozenFacts)
  expect(e.telemetry[0].coordinates).toEqual(original.coordinates)
  expect(e.telemetry[0].cargo_ids).toEqual(original.cargo_ids)
  expect(e.telemetry[0].active_plan_id).toBe(plan.plan_id)
  expect(e.desired_plan_id).not.toBe(plan.plan_id)
  await page.getByRole('button', { name: '查看影响链与架次', exact: true }).click()
  await page
    .getByRole('dialog')
    .getByRole('button', { name: `核对 ${plan.plan_id} ${future.sortie_id}`, exact: true })
    .click()
  await expect(page.getByRole('complementary', { name: '执行架次安排详情' })).toContainText(
    '历史事件安排 · 已非当前生效任务',
  )
  await page.getByRole('button', { name: '关闭架次详情' }).click()
  await page.locator('.v2-object-scroll > button').first().click()
  await expect(page.locator('.v2-inspector')).toContainText('当前架次来源')
  await expect(page.getByRole('region', { name: '模拟设备程序核对', exact: true })).toContainText(
    e.desired_plan_id,
  )
  await page.screenshot({
    path: '../evidence/redesign-v2/dependency-inflight-adopted-1280.png',
    fullPage: true,
  })
  const candidate: Plan = await (await request.get('/api/v1/plans/' + e.desired_plan_id)).json()
  e = await (
    await request.post(`/api/v1/executions/${e.execution_id}/simulation/actions`, {
      data: {
        action: 'advance',
        target_time_s: Math.max(...candidate.sorties.map((r) => r.battery_released_s)) + 1,
        expected_revision: e.revision,
        idempotency_key: crypto.randomUUID(),
      },
    })
  ).json()
  expect(e.delivered_cargo_ids).toHaveLength(2)
  const bundle: ExecutionArchive['bundle'] = await (
    await request.get(`/api/v1/executions/${e.execution_id}/export?version=2`)
  ).json()
  expect(bundle.documents.some((d) => d.kind === 'repair_reference')).toBeTruthy()
  await fs.mkdir('../evidence/redesign-v2/DEPENDENCY_SMOKE', { recursive: true })
  await fs.writeFile(
    '../evidence/redesign-v2/DEPENDENCY_SMOKE/battery-exit-execution.json',
    JSON.stringify(bundle, null, 2) + '\n',
  )
})
