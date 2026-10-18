import { test, expect } from '@playwright/test'
import type { Mission } from '../src/api/operations'
import type { Scenario } from '../src/api/client'

test.setTimeout(90000)
test.use({ reducedMotion: 'reduce' })

test('V2 resource diagnosis computes an isolated addition before any feasible baseline exists', async ({
  page,
  request,
}) => {
  const m: Mission = await (
    await request.post('/api/v1/missions', {
      data: {
        name: '无可用机体的增配诊断 ' + Date.now(),
        template: 'compact',
        idempotency_key: crypto.randomUUID(),
      },
    })
  ).json()
  const s: Scenario = await (await request.get('/api/v1/scenarios/' + m.current_scenario_id)).json()
  s.demands = s.demands.slice(0, 2)
  const ids = new Set(s.demands.map((d) => d.demand_id))
  s.cargo_items = s.cargo_items.filter((b) => ids.has(b.demand_id))
  s.demands.forEach((d) => {
    d.hard_deadline_s = null
    d.expected_deadline_s = null
  })
  s.drones.forEach((d) => {
    d.status = 'unavailable'
  })
  const put = await request.put('/api/v1/scenarios/' + s.scenario_id, {
    data: { expected_state_version: 1, scenario: s },
  })
  expect(put.ok()).toBeTruthy()
  const original: Scenario = await put.json()
  await page.goto('/#/missions/' + m.mission_id + '/plans')
  await page.getByRole('button', { name: '资源诊断与增配', exact: true }).click()
  const dialog = page.getByRole('dialog')
  await expect(dialog).toContainText('尚无可行基线')
  await dialog.getByLabel('诊断增配机型').selectOption('A')
  await dialog.getByLabel('诊断新增机体').fill('1')
  await dialog.getByLabel('诊断新增电池').fill('0')
  await dialog.getByRole('button', { name: '增配并真实求解', exact: true }).click()
  await expect(dialog.locator('.v2-metrics-line')).toContainText('验证 passed', { timeout: 45000 })
  await expect(dialog).toContainText('原基线 未取得')
  await expect(dialog.locator('.map-canvas canvas')).toBeVisible()
  expect(await (await request.get('/api/v1/scenarios/' + s.scenario_id)).json()).toEqual(original)
  expect(
    await (await request.get('/api/v1/scenarios/' + s.scenario_id + '/plans')).json(),
  ).toHaveLength(0)
  await page.setViewportSize({ width: 1280, height: 720 })
  await page.screenshot({
    path: '../evidence/redesign-v2/resource-without-baseline-1280.png',
    fullPage: true,
  })
  await dialog.getByRole('button', { name: '作为独立任务打开此增配场景', exact: true }).click()
  await expect(page).toHaveURL(/\/plans$/)
  await expect(page.getByLabel('选择调度方案')).not.toHaveValue('')
  await expect(page.locator('.v2-mission')).toContainText('资源增配诊断')
})
