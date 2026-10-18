import { test, expect, type Page } from '@playwright/test'
import type { Scenario, Plan } from '../src/api/client'
import type { Mission, Execution } from '../src/api/operations'

test.setTimeout(180000)

test('V2 pending events freeze manual advance and an audited misreport correction restores the simulation', async ({
  page,
  request,
}) => {
  const mission: Mission = await (
    await request.post('/api/v1/missions', {
      data: {
        name: 'Correction exercise ' + Date.now(),
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
      data: { snapshot_id: snap.snapshot_id, time_limit_s: 5 },
    })
  ).json()
  let pid = ''
  await expect
    .poll(
      async () => {
        const result = await (await request.get('/api/v1/solve-jobs/' + job.job_id)).json()
        pid = result.plan_id || ''
        return result.job_state
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
  let execution: Execution = await (
    await request.post('/api/v1/executions', {
      data: {
        mission_id: mission.mission_id,
        confirmed_plan_id: pid,
        expected_revision: mission.revision,
        idempotency_key: crypto.randomUUID(),
      },
    })
  ).json()
  execution = await (
    await request.post(`/api/v1/executions/${execution.execution_id}/simulation/actions`, {
      data: {
        action: 'advance',
        target_time_s: 1,
        expected_revision: execution.revision,
        idempotency_key: crypto.randomUUID(),
      },
    })
  ).json()
  const committed = plan.sorties.find((r) => r.prepare_start_s <= 1)!
  const event = await request.post(`/api/v1/executions/${execution.execution_id}/events`, {
    data: {
      event_id: crypto.randomUUID(),
      event_type: 'drone.unavailable',
      object_id: committed.drone_id,
      expected_revision: execution.revision,
      reason: '演练上报需要核实',
    },
  })
  expect(event.status()).toBe(201)
  await page.goto('/#/missions/' + mission.mission_id + '/execute')
  await expect(page.getByRole('button', { name: '推进至下一事件', exact: true })).toBeDisabled()
  await expect(page.getByRole('button', { name: '继续演练', exact: true })).toBeDisabled()
  await expect(page.locator('.v2-event-list')).toContainText('需人工协调')
  await page.screenshot({ path: '../evidence/redesign-v2/event-manual-1440.png', fullPage: true })
  await page.getByRole('button', { name: '核实误报', exact: true }).click()
  await page
    .getByLabel('核实依据（至少10个字符）')
    .fill('模拟演练操作人员已重新核实，机体正常，此前为测试误报')
  await page.getByRole('button', { name: '记录纠错', exact: true }).click()
  await expect(page.getByRole('dialog')).toHaveCount(0)
  await expect(page.locator('.v2-event-list')).toContainText('已核实误报')
  await expect(page.getByRole('button', { name: '继续演练', exact: true })).toBeEnabled()
  const unchanged: Execution = await (
    await request.get('/api/v1/executions/' + execution.execution_id)
  ).json()
  expect(unchanged.facts).toEqual(execution.facts)
  await page.getByRole('button', { name: '继续演练', exact: true }).click()
  await expect(page.getByRole('button', { name: '暂停演练', exact: true })).toBeVisible()
  await page.getByRole('button', { name: '暂停演练', exact: true }).click()
  await expect(page.getByRole('button', { name: '继续演练', exact: true })).toBeVisible()
})

test('V2 manual weather input changes real type selection and remains traceable on the map', async ({
  page,
  request,
}) => {
  const response = await request.post('/api/v1/missions', {
    data: {
      name: 'W1 browser exercise ' + Date.now(),
      template: 'compact',
      idempotency_key: crypto.randomUUID(),
    },
  })
  expect(response.status()).toBe(201)
  const mission = await response.json()
  const scene: Scenario = await (
    await request.get('/api/v1/scenarios/' + mission.current_scenario_id)
  ).json()
  scene.cargo_items = scene.cargo_items.slice(0, 2).map((c) => ({ ...c, mass_kg: 1, volume_l: 1 }))
  scene.demands = scene.demands
    .filter((d) => scene.cargo_items.some((c) => c.demand_id === d.demand_id))
    .map((d) => ({
      ...d,
      required_quantity: scene.cargo_items.filter((c) => c.demand_id === d.demand_id).length,
      hard_deadline_s: null,
      expected_deadline_s: null,
    }))
  expect(
    (
      await request.put('/api/v1/scenarios/' + scene.scenario_id, {
        data: { expected_state_version: scene.state_version, scenario: scene },
      })
    ).ok(),
  ).toBeTruthy()
  await page.goto('/#/missions/' + mission.mission_id + '/prepare')
  await page.getByRole('button', { name: /机队保障/ }).click()
  await page.getByRole('button', { name: '配置人工气象情景', exact: true }).click()
  const dialog = page.getByRole('dialog')
  await dialog.getByLabel('情景来源 / 假设说明').fill('Browser test uniform manual assumption')
  await dialog.getByLabel('机型限值来源').fill('Synthetic limits for regression only')
  await dialog.getByLabel('起始 / 相对分钟').fill('10')
  await dialog.getByLabel('结束 / 相对分钟').fill('300')
  await dialog.getByLabel('风速 / m/s', { exact: true }).fill('8')
  await dialog.getByLabel('A 最大风速 / m/s', { exact: true }).fill('4')
  await dialog.getByLabel('B 最大风速 / m/s', { exact: true }).fill('12')
  await dialog.getByRole('checkbox').check()
  await dialog.getByRole('button', { name: '保存气象条件', exact: true }).click()
  await expect(dialog).toHaveCount(0)
  await page.getByRole('button', { name: /条件检查/ }).click()
  await page.getByRole('button', { name: '运行检查', exact: true }).click()
  await expect(page.locator('.v2-check-summary')).toContainText('0 项待处理')
  await expect(page.locator('.v2-check-list')).toContainText('A')
  await page.screenshot({
    path: '../evidence/redesign-v2/weather-preflight-1440.png',
    fullPage: true,
  })
  await page.getByRole('button', { name: /进入方案计算/ }).click()
  await page.getByRole('button', { name: '生成方案', exact: true }).click()
  await expect(page.locator('.v2-metrics-line')).toContainText('2 箱', { timeout: 60000 })
  const plan: Plan = await (
    await request.get('/api/v1/plans/' + (await page.getByLabel('选择调度方案').inputValue()))
  ).json()
  expect(plan.model_scope).toContain('weather_window')
  expect(
    plan.sorties.every(
      (r) =>
        r.takeoff_s >= 600 && scene.drones.find((d) => d.drone_id === r.drone_id)?.type_id === 'B',
    ),
  ).toBeTruthy()
  await expect(page.locator('.map-weather-context')).toContainText('8 m/s')
  await page.screenshot({ path: '../evidence/redesign-v2/weather-plan-1440.png', fullPage: true })
  await page.getByRole('button', { name: '图层管理', exact: true }).click()
  await page.getByLabel('人工气象信息（仅显隐）').uncheck()
  await expect(page.locator('.map-weather-context')).toHaveCount(0)
  expect((await (await request.get('/api/v1/plans/' + plan.plan_id)).json()).model_scope).toContain(
    'weather_window',
  )
})

function csv(rows: Record<string, unknown>[]) {
  const keys = Object.keys(rows[0])
  const cell = (v: unknown) =>
    `"${(typeof v === 'object' && v !== null ? JSON.stringify(v) : String(v ?? '')).replaceAll('"', '""')}"`
  return Buffer.from(
    keys.map(cell).join(',') +
      '\n' +
      rows.map((r) => keys.map((k) => cell(r[k])).join(',')).join('\n'),
    'utf8',
  )
}
async function upload(page: Page, group: string, rows: Record<string, unknown>[]) {
  await page.getByLabel('导入实体表').selectOption(group)
  await page
    .locator('.v2-input-import input[type=file]')
    .setInputFiles({ name: group + '.csv', mimeType: 'text/csv', buffer: csv(rows) })
  await page.getByRole('button', { name: '确认更新任务输入', exact: true }).click()
  await expect(page.getByRole('dialog')).toHaveCount(0)
}

test('V2 new user creates a non-contest task, imports CSV, fixes readiness and computes a real plan', async ({
  page,
  request,
}) => {
  await page.goto('/')
  await expect(page.getByRole('heading', { name: '救援工作首页', exact: true })).toBeVisible()
  for (const name of ['首页', '救援任务', '资源中心', '演练评测'])
    await expect(
      page.getByRole('navigation', { name: '主要导航' }).getByRole('link', { name, exact: true }),
    ).toBeVisible()
  await page.getByRole('button', { name: '新建救援任务', exact: true }).click()
  await page
    .getByPlaceholder('例如：镇龙乡山洪应急运输')
    .fill('成都合成区域 CSV 救援任务 ' + Date.now())
  await page.getByRole('button', { name: /创建并准备任务/ }).click()
  await expect(page).toHaveURL(/missions\/MIS-[^/]+\/prepare/)
  const mid = page.url().match(/missions\/([^/]+)/)![1]
  await page.getByLabel('经度 · WGS84').fill('104.20')
  await page.getByLabel('纬度 · WGS84').fill('30.70')
  await page.getByLabel('地面高程 / m').fill('480')
  await page.getByRole('button', { name: '保存基地', exact: true }).click()
  await expect(page.locator('.v2-prepare-map .map-marker-base')).toBeVisible()
  await page.getByRole('button', { name: /需求物资/ }).click()
  await upload(page, 'sites', [
    {
      id: 'CD-S1',
      name: '合成医疗接收点',
      coordinates: [104.22, 30.72],
      ground_elevation_m: 500,
      available: true,
    },
  ])
  await upload(page, 'demands', [
    {
      demand_id: 'CD-D1',
      site_id: 'CD-S1',
      cargo_type: 'MED',
      required_quantity: 2,
      priority: 1,
      expected_deadline_s: null,
      hard_deadline_s: null,
      mandatory: true,
    },
  ])
  await upload(
    page,
    'cargo_items',
    [1, 2].map((n) => ({
      cargo_id: 'CD-BOX-' + n,
      demand_id: 'CD-D1',
      type: 'MED',
      mass_kg: 1,
      volume_l: 1,
      status: 'available',
      location_id: 'BASE',
    })),
  )
  await page.getByRole('button', { name: /机队保障/ }).click()
  await upload(page, 'drones', [
    {
      drone_id: 'CD-U1',
      type_id: 'A',
      status: 'available',
      location_id: 'BASE',
      available_after_s: 0,
    },
  ])
  const example = await (
    await request.post('/api/v1/scenarios/examples', { data: { example: 'compact' } })
  ).json()
  const source = example.batteries.find(
    (b: { compatible_type_id: string }) => b.compatible_type_id === 'A',
  )
  await upload(page, 'batteries', [
    { ...source, battery_id: 'CD-B1', compatible_type_id: 'B', location_id: 'BASE' },
  ])
  await page.getByRole('button', { name: /条件检查/ }).click()
  await page.getByRole('button', { name: '发布输入并准备检查', exact: true }).click()
  await expect(page.getByRole('button', { name: '运行检查', exact: true })).toBeVisible()
  await page.getByRole('button', { name: '运行检查', exact: true }).click()
  await expect(page.locator('.v2-check-list .check-blocked')).toContainText(
    'CD-U1 有 0 块可用兼容电池',
  )
  await expect(page.getByRole('button', { name: /进入方案计算/ })).toBeDisabled()
  await page.getByRole('button', { name: /机队保障/ }).click()
  await upload(page, 'batteries', [
    { ...source, battery_id: 'CD-B1', soc: 0.8, location_id: 'BASE' },
  ])
  await page.getByRole('button', { name: /条件检查/ }).click()
  await page.getByRole('button', { name: '运行检查', exact: true }).click()
  await expect(page.locator('.v2-check-summary')).toContainText('0 项待处理')
  await page.reload()
  await page.getByRole('button', { name: /条件检查/ }).click()
  await expect(page.locator('.v2-check-summary')).toContainText('0 项待处理')
  await page.getByRole('button', { name: /进入方案计算/ }).click()
  await page.getByRole('button', { name: '生成方案', exact: true }).click()
  await expect(page.locator('.v2-metrics-line')).toContainText('2 箱', { timeout: 60000 })
  const pid = await page.getByLabel('选择调度方案').inputValue()
  const plan = await (await request.get('/api/v1/plans/' + pid)).json()
  expect(plan.validation.status).toBe('passed')
  expect(plan.sorties.flatMap((r: { cargo_ids: string[] }) => r.cargo_ids).sort()).toEqual([
    'CD-BOX-1',
    'CD-BOX-2',
  ])
  const mission = await (await request.get('/api/v1/missions/' + mid)).json()
  const scene = await (await request.get('/api/v1/scenarios/' + mission.current_scenario_id)).json()
  expect(scene.base.coordinates).toEqual([104.2, 30.7])
  expect(scene.batteries[0].soc).toBe(0.8)
  await page.getByRole('button', { name: '定位合成医疗接收点', exact: true }).click()
  await expect(page.locator('.v2-inspector')).toContainText('需求点详情')
  await expect(page.locator('.v2-inspector')).toContainText('医疗物资 · 2 箱')
  await page.getByRole('button', { name: '关闭详情', exact: true }).click()
  for (const [width, height] of [
    [1440, 900],
    [1280, 720],
  ]) {
    await page.setViewportSize({ width, height })
    const bounds = await page.locator('.v2-map-main').boundingBox()
    expect(bounds!.height).toBeGreaterThanOrEqual(width === 1440 ? 440 : 340)
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(
      width,
    )
  }
})
