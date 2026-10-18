import { test, expect, type Page } from '@playwright/test'

test.setTimeout(180000)

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
