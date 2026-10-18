import { test, expect } from '@playwright/test'
import type { Mission, Execution, ExecutionArchive } from '../src/api/operations'
import type { Scenario, Plan } from '../src/api/client'

test.setTimeout(180000)
test.use({ reducedMotion: 'reduce' })

test('V2 in-flight insertion is adopted, reviewed and reloaded as an immutable multi-plan archive', async ({
  page,
  request,
}) => {
  const mission: Mission = await (
    await request.post('/api/v1/missions', {
      data: {
        name: '在途插单与档案验收 ' + Date.now(),
        template: 'compact',
        idempotency_key: crypto.randomUUID(),
      },
    })
  ).json()
  const scene: Scenario = await (
    await request.get('/api/v1/scenarios/' + mission.current_scenario_id)
  ).json()
  const snap = await (
    await request.post(`/api/v1/scenarios/${scene.scenario_id}/snapshots`, {
      data: { expected_state_version: scene.state_version },
    })
  ).json()
  const job = await (
    await request.post('/api/v1/solve-jobs', {
      data: { snapshot_id: snap.snapshot_id, time_limit_s: 5, objective_policy: 'tradeoff_v2' },
    })
  ).json()
  let pid = ''
  await expect
    .poll(
      async () => {
        const j = await (await request.get('/api/v1/solve-jobs/' + job.job_id)).json()
        pid = j.plan_id || ''
        return j.job_state
      },
      { timeout: 45000 },
    )
    .toBe('completed')
  const plan: Plan = await (await request.get('/api/v1/plans/' + pid)).json()
  expect(
    (
      await request.post(`/api/v1/plans/${pid}/confirm`, {
        data: { expected_state_version: scene.state_version, idempotency_key: crypto.randomUUID() },
      })
    ).ok(),
  ).toBeTruthy()
  let e: Execution = await (
    await request.post('/api/v1/executions', {
      data: {
        mission_id: mission.mission_id,
        confirmed_plan_id: pid,
        expected_revision: mission.revision,
        idempotency_key: crypto.randomUUID(),
      },
    })
  ).json()
  const first =
    Math.min(...plan.sorties.flatMap((r) => r.visits.map((v) => v.delivery_complete_s))) + 1
  e = await (
    await request.post(`/api/v1/executions/${e.execution_id}/simulation/actions`, {
      data: {
        action: 'advance',
        target_time_s: first,
        expected_revision: e.revision,
        idempotency_key: crypto.randomUUID(),
      },
    })
  ).json()
  expect(e.delivered_cargo_ids.length).toBeGreaterThan(0)
  const originalFacts = e.facts
  const demand = {
    ...scene.demands[0],
    demand_id: 'BROWSER-URGENT',
    required_quantity: 1,
    expected_deadline_s: null,
    hard_deadline_s: null,
  }
  const event = await request.post(`/api/v1/executions/${e.execution_id}/events`, {
    data: {
      event_id: crypto.randomUUID(),
      event_type: 'demand.added',
      expected_revision: e.revision,
      reason: '新增一箱急需物资，有明确基地库存',
      demand,
      cargo_items: [
        {
          cargo_id: 'BROWSER-URGENT-BOX',
          demand_id: demand.demand_id,
          type: demand.cargo_type,
          mass_kg: 1,
          volume_l: 1,
          status: 'available',
          location_id: scene.base.id,
        },
      ],
    },
  })
  expect(event.status()).toBe(201)
  await page.goto('/#/missions/' + mission.mission_id + '/execute')
  await page.getByRole('button', { name: '生成调整', exact: true }).click()
  const dialog = page.getByRole('dialog')
  await expect(dialog.getByRole('button', { name: '确认采纳模拟调整', exact: true })).toBeEnabled({
    timeout: 60000,
  })
  await page.screenshot({
    path: '../evidence/redesign-v2/archive-event-diff-1440.png',
    fullPage: true,
  })
  await dialog.getByRole('button', { name: '确认采纳模拟调整', exact: true }).click()
  await expect(dialog.locator('.v2-check-summary')).toContainText('状态 applied', {
    timeout: 15000,
  })
  await dialog.getByRole('button', { name: '关闭详情', exact: true }).click()
  e = await (await request.get('/api/v1/executions/' + e.execution_id)).json()
  expect(e.facts).toEqual(originalFacts)
  expect(e.schedule_parts.length).toBeGreaterThan(1)
  await page.getByRole('button', { name: '查看完整排程', exact: true }).click()
  await expect(page.getByRole('dialog')).toContainText('生效排程与模拟事实')
  await page.screenshot({
    path: '../evidence/redesign-v2/execution-active-gantt-1440.png',
    fullPage: true,
  })
  await page.getByRole('dialog').getByRole('button', { name: '关闭弹窗', exact: true }).click()
  const candidate: Plan = await (await request.get('/api/v1/plans/' + e.desired_plan_id)).json()
  e = await (
    await request.post(`/api/v1/executions/${e.execution_id}/simulation/actions`, {
      data: {
        action: 'advance',
        target_time_s:
          Math.max(
            ...plan.sorties.map((r) => r.battery_released_s),
            ...candidate.sorties.map((r) => r.battery_released_s),
          ) + 1,
        expected_revision: e.revision,
        idempotency_key: crypto.randomUUID(),
      },
    })
  ).json()
  expect(e.status).toBe('completed')
  expect(e.delivered_cargo_ids).toContain('BROWSER-URGENT-BOX')
  await page.goto('/#/missions/' + mission.mission_id + '/review')
  await expect(
    page.getByRole('img', { name: '初始计划与模拟交付阶梯图', exact: true }),
  ).toBeVisible()
  await expect(page.locator('.v2-review')).toContainText('BROWSER-URGENT-BOX')
  await expect(page.locator('.v2-review')).toContainText('无初始基准')
  expect(
    await page
      .locator('.v2-review button.ledger-flight')
      .first()
      .evaluate((element) => getComputedStyle(element).backgroundColor),
  ).not.toBe('rgba(0, 0, 0, 0)')
  for (const [width, height] of [
    [1440, 900],
    [1280, 720],
  ]) {
    await page.setViewportSize({ width, height })
    await page.screenshot({
      path: `../evidence/redesign-v2/retrospective-${width}.png`,
      fullPage: true,
    })
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(
      width,
    )
  }
  const bundle: ExecutionArchive['bundle'] = await (
    await request.get(`/api/v1/executions/${e.execution_id}/export?version=2`)
  ).json()
  const before = e.facts
  await page
    .getByRole('navigation', { name: '主要导航' })
    .getByRole('link', { name: '资源中心', exact: true })
    .click()
  await page.getByRole('button', { name: '运行档案', exact: true }).click()
  await page.getByLabel('导入只读运行档案').setInputFiles({
    name: 'simulation-archive.json',
    mimeType: 'application/json',
    buffer: Buffer.from(JSON.stringify(bundle), 'utf8'),
  })
  await expect(page.locator('.v2-archive-detail')).toContainText(mission.name, { timeout: 15000 })
  await expect(page.locator('.v2-archive-readonly')).toContainText('不创建实例或预约')
  await page.getByLabel('档案事实时刻').focus()
  await page.getByLabel('档案事实时刻').press('Home')
  await expect(page.locator('.v2-archive-clock')).toContainText('此时模拟交付 0 箱')
  await page.getByLabel('档案事实时刻').press('End')
  await expect(page.locator('.v2-archive-clock')).toContainText('此时模拟交付 33 箱')
  for (const [width, height] of [
    [1440, 900],
    [1280, 720],
  ]) {
    await page.setViewportSize({ width, height })
    await page.screenshot({
      path: `../evidence/redesign-v2/readonly-archive-${width}.png`,
      fullPage: true,
    })
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(
      width,
    )
  }
  expect((await (await request.get('/api/v1/executions/' + e.execution_id)).json()).facts).toEqual(
    before,
  )
  await expect(page.getByRole('button', { name: '开始演练', exact: true })).toHaveCount(0)
})
