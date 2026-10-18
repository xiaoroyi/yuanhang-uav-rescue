import { test, expect, type APIRequestContext, type Page } from '@playwright/test'
import type { Scenario, Plan } from '../src/api/client'
import type { Mission } from '../src/api/operations'

test.setTimeout(120000)
test.use({ reducedMotion: 'reduce' })

async function compact(request: APIRequestContext) {
  const response = await request.post('/api/v1/missions', {
    data: {
      name: '地图工作台验收 ' + Date.now(),
      template: 'compact',
      idempotency_key: crypto.randomUUID(),
    },
  })
  expect(response.status()).toBe(201)
  const mission: Mission = await response.json()
  const scene: Scenario = await (
    await request.get('/api/v1/scenarios/' + mission.current_scenario_id)
  ).json()
  return { mission, scene }
}

async function camera(page: Page, id: string) {
  return page.evaluate(
    (key) =>
      JSON.parse(sessionStorage.getItem('yuanhang-map-camera:' + key) || 'null') as {
        center: [number, number]
        zoom: number
      } | null,
    id,
  )
}

test('V2 blank mission map accepts coordinates without inventing a saved base or elevation', async ({
  page,
  request,
}) => {
  const mission: Mission = await (
    await request.post('/api/v1/missions', {
      data: {
        name: '空白区域地图 ' + Date.now(),
        template: 'blank',
        idempotency_key: crypto.randomUUID(),
      },
    })
  ).json()
  await page.goto('/#/missions/' + mission.mission_id + '/prepare')
  const canvas = page.locator('.v2-prepare-map canvas')
  await expect(canvas).toBeVisible()
  await expect(page.locator('.v2-prepare-map .map-marker-base')).toHaveCount(0)
  await canvas.click({ button: 'right', position: { x: 250, y: 180 } })
  await expect(page.getByLabel('经度 · WGS84')).not.toHaveValue('')
  await expect(page.getByLabel('纬度 · WGS84')).not.toHaveValue('')
  await expect(page.getByLabel('地面高程 / m')).toHaveValue('')
  const unchanged: Mission = await (
    await request.get('/api/v1/missions/' + mission.mission_id)
  ).json()
  expect(unchanged.draft.base).toBeNull()
  expect(unchanged.current_scenario_id).toBeNull()
  await page.screenshot({
    path: '../evidence/redesign-v2/blank-region-map-1440.png',
    fullPage: true,
  })
  await page.getByLabel('地面高程 / m').fill('480')
  await page.getByRole('button', { name: '保存基地', exact: true }).click()
  await expect(page.locator('.v2-prepare-map .map-marker-base')).toBeVisible()
  await expect.poll(async () => (await camera(page, mission.mission_id))?.zoom).toBeGreaterThan(10)
})

test('V2 fifty long-name points remain selectable and camera survives inspection, resize, reload and failed imagery', async ({
  page,
  request,
}) => {
  const { mission, scene } = await compact(request)
  const original = scene.sites
  scene.sites = Array.from({ length: 50 }, (_, i) => ({
    ...original[i % original.length],
    id: i < original.length ? original[i].id : `DENSE-${i}`,
    name: `长名称应急医疗物资接收与转运点第${i + 1}号`,
    coordinates: [
      scene.base.coordinates[0] + (i < 2 ? 0.012 : ((i % 8) - 3) * 0.004),
      scene.base.coordinates[1] + (i < 2 ? 0.012 : (Math.floor(i / 8) - 3) * 0.004),
    ],
  }))
  const updated = await request.put('/api/v1/scenarios/' + scene.scenario_id, {
    data: { expected_state_version: scene.state_version, scenario: scene },
  })
  expect(updated.ok()).toBeTruthy()
  await page.goto('/#/missions/' + mission.mission_id + '/plans')
  await expect(page.locator('.v2-map-main .map-marker')).toHaveCount(51)
  const cluster = page
    .locator('.v2-map-main .map-marker[data-cluster-count]:visible')
    .filter({ hasText: '+' })
    .first()
  await cluster.click()
  const chooser = page.getByRole('region', { name: '聚合点位选择', exact: true })
  await expect(chooser).toBeVisible()
  await chooser.locator('li button').first().click()
  await expect(page.locator('.v2-inspector')).toBeVisible()
  await page.getByRole('button', { name: '放大地图', exact: true }).click()
  await expect.poll(async () => (await camera(page, mission.mission_id))?.zoom).toBeGreaterThan(10)
  const before = await camera(page, mission.mission_id)
  expect(before).not.toBeNull()
  for (const [width, height] of [
    [1440, 900],
    [1280, 720],
    [1024, 768],
  ]) {
    await page.setViewportSize({ width, height })
    await expect
      .poll(async () => (await camera(page, mission.mission_id))?.zoom)
      .toBeCloseTo(before!.zoom, 3)
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(
      width,
    )
    const overlap = await page.evaluate(() => {
      const visible = (e: HTMLElement) =>
        e.getClientRects().length > 0 && getComputedStyle(e).visibility !== 'hidden'
      const dots = [...document.querySelectorAll<HTMLElement>('.v2-map-main .map-marker-dot')]
        .filter(visible)
        .map((e) => e.getBoundingClientRect())
      return [...document.querySelectorAll<HTMLElement>('.v2-map-main .map-marker-label')]
        .filter(visible)
        .filter((e) => {
          const a = e.getBoundingClientRect()
          return dots.some(
            (b) => a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top,
          )
        })
        .map((e) => e.textContent)
    })
    expect(overlap).toEqual([])
    const controls = await page.getByRole('button', { name: '放大地图', exact: true }).boundingBox()
    const inspector = await page.locator('.v2-inspector').boundingBox()
    expect(controls!.x + controls!.width).toBeLessThanOrEqual(inspector!.x)
    await page.screenshot({
      path: `../evidence/redesign-v2/dense-map-${width}.png`,
      fullPage: true,
    })
  }
  await page.reload()
  await expect(page.locator('.v2-map-main canvas')).toBeVisible()
  await expect
    .poll(async () => (await camera(page, mission.mission_id))?.zoom)
    .toBeCloseTo(before!.zoom, 3)
  let blockedImageryRequests = 0
  await page.route(/^https:\/\/[^/]*\.arcgisonline\.com\//, (route) => {
    blockedImageryRequests++
    return route.abort()
  })
  await page.getByRole('button', { name: /卫星影像/ }).click()
  await expect(page.locator('.map-satellite-warning')).toBeVisible({ timeout: 20000 })
  expect(blockedImageryRequests).toBeGreaterThan(0)
  expect((await camera(page, mission.mission_id))?.zoom).toBeCloseTo(before!.zoom, 3)
})

test('V2 real computed overlapping flights offer a choice and keep the camera when opening details', async ({
  page,
  request,
}) => {
  const { mission, scene } = await compact(request)
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
        const value = await (await request.get('/api/v1/solve-jobs/' + job.job_id)).json()
        pid = value.plan_id || ''
        return value.job_state
      },
      { timeout: 45000 },
    )
    .toBe('completed')
  const plan: Plan = await (await request.get('/api/v1/plans/' + pid)).json()
  const site = scene.sites.find(
    (n) => plan.sorties.filter((r) => r.visits.some((v) => v.site_id === n.id)).length > 1,
  )
  expect(site).toBeTruthy()
  await page.goto('/#/missions/' + mission.mission_id + '/plans')
  await expect(page.getByLabel('选择调度方案')).toHaveValue(pid)
  const base = page.locator('.v2-map-main .map-marker-base .map-marker-dot')
  const target = page.locator(
    `.v2-map-main .map-marker[data-site-id="${site!.id}"] .map-marker-dot`,
  )
  await expect(base).toBeVisible()
  await expect(target).toBeVisible()
  const centers = () =>
    page.evaluate((siteId) => {
      const a = document
        .querySelector('.v2-map-main .map-marker-base .map-marker-dot')
        ?.getBoundingClientRect()
      const b = document
        .querySelector(`.v2-map-main .map-marker[data-site-id="${siteId}"] .map-marker-dot`)
        ?.getBoundingClientRect()
      if (!a?.width || !b?.width) return null
      return {
        a: { x: a.x + a.width / 2, y: a.y + a.height / 2 },
        b: { x: b.x + b.width / 2, y: b.y + b.height / 2 },
      }
    }, site!.id)
  await expect.poll(centers).not.toBeNull()
  const location = await centers()
  if (!location) throw new Error('Map markers changed while locating route geometry')
  await page.mouse.click((location.a.x + location.b.x) / 2, (location.a.y + location.b.y) / 2)
  const chooser = page.getByRole('region', { name: '重叠航线选择', exact: true })
  await expect(chooser).toBeVisible()
  expect(await chooser.locator('li button').count()).toBeGreaterThan(1)
  await page.screenshot({
    path: '../evidence/redesign-v2/overlapping-routes-1440.png',
    fullPage: true,
  })
  const before = await camera(page, mission.mission_id)
  const chosenId = await chooser.locator('li code').last().innerText()
  await chooser.locator('li button').last().click()
  await expect(page.locator('.v2-inspector')).toContainText(chosenId)
  const chosen = plan.sorties.find((sortie) => sortie.sortie_id === chosenId)
  expect(chosen).toBeTruthy()
  await expect(page.locator('.v2-inspector')).toContainText(chosen!.cargo_ids[0])
  await expect(chooser).toHaveCount(0)
  expect((await camera(page, mission.mission_id))?.zoom).toBeCloseTo(before!.zoom, 3)
  // Short-height CSS hides the inline panel; real analysis must still open.
  await page.setViewportSize({ width: 1280, height: 720 })
  await page.getByRole('button', { name: '查看高程 / 载荷 / 电量', exact: true }).click()
  const profile = page.getByRole('dialog', { name: '架次完整分析' })
  await expect(profile).toContainText(chosenId)
  await expect(profile.getByRole('button', { name: '高程剖面', exact: true })).toBeVisible()
  await expect(profile.locator('canvas').first()).toBeVisible()
  await page.screenshot({ path: '../evidence/redesign-v2/profile-modal-1280.png' })
  await profile.getByRole('button', { name: '关闭弹窗', exact: true }).click()
  await page.getByRole('button', { name: '机体 / 电池排程', exact: true }).click()
  const timeline = page.getByRole('dialog', { name: '完整资源排程' })
  await expect(timeline.locator('.timeline-row').first()).toBeVisible()
  await expect(timeline).toContainText(chosen!.drone_id)
  await page.screenshot({ path: '../evidence/redesign-v2/timeline-modal-1280.png' })
  await timeline.getByRole('button', { name: '关闭弹窗', exact: true }).click()
  expect(
    await page.locator('.v2-map-main').evaluate((e) => e.getBoundingClientRect().height),
  ).toBeGreaterThanOrEqual(340)
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(1280)
})

test('V2 unavailable WebGL keeps input and table controls usable', async ({ page, request }) => {
  const { mission } = await compact(request)
  await page.addInitScript(() => {
    const original = HTMLCanvasElement.prototype.getContext
    Object.defineProperty(HTMLCanvasElement.prototype, 'getContext', {
      value: function (this: HTMLCanvasElement, name: string, ...args: unknown[]) {
        return name.includes('webgl') ? null : Reflect.apply(original, this, [name, ...args])
      },
    })
  })
  await page.goto('/#/missions/' + mission.mission_id + '/prepare')
  await expect(page.locator('.map-error')).toContainText('地图渲染不可用')
  await expect(page.getByRole('button', { name: '保存基地', exact: true })).toBeEnabled()
  await page.getByRole('button', { name: /需求物资/ }).click()
  await expect(page.getByLabel('导入实体表')).toBeVisible()
  await page.screenshot({
    path: '../evidence/redesign-v2/map-webgl-unavailable.png',
    fullPage: true,
  })
})

test('V2 stalled imagery is not declared ready from source metadata and falls back after the loading deadline', async ({
  page,
  request,
}) => {
  const { mission } = await compact(request)
  const held: import('@playwright/test').Route[] = []
  await page.route(/^https:\/\/[^/]*\.arcgisonline\.com\//, (route) => {
    held.push(route)
  })
  try {
    await page.goto('/#/missions/' + mission.mission_id + '/plans')
    await expect(page.locator('.rescue-map')).toHaveAttribute('data-context', 'true')
    await page.getByRole('button', { name: /卫星影像/ }).click()
    await expect(page.locator('.rescue-map')).toHaveAttribute('data-imagery-state', 'loading')
    await expect(page.locator('.map-satellite-warning')).toBeVisible({ timeout: 17000 })
    expect(held.length).toBeGreaterThan(0)
    await expect(page.locator('.rescue-map')).toHaveAttribute('data-basemap', 'offline')
    await page.screenshot({
      path: '../evidence/redesign-v2/map-imagery-stalled.png',
      fullPage: true,
    })
  } finally {
    await Promise.all(held.map((route) => route.abort().catch(() => {})))
  }
})
