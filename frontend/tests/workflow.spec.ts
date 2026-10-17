import { test, expect, type Page } from '@playwright/test'
import fs from 'node:fs/promises'
import path from 'node:path'

async function solve(page: Page) {
  await page.getByRole('button', { name: /^(生成真实方案|重新求解)$/ }).click()
  await expect(page.locator('.job-banner')).toBeVisible()
  await expect(page.locator('.job-banner')).toBeHidden({ timeout: 45000 })
  await expect(page.getByTestId('sortie-card').first()).toBeVisible()
}

test('单点诊断按快照重算32箱与80箱，余量敏感性和导出不修改场景', async ({ page, request }) => {
  const errors: string[] = []
  const snapshots: string[] = []
  page.on('pageerror', (e) => errors.push(e.message))
  page.on('response', (response) => {
    if (
      response.request().method() === 'POST' &&
      /\/scenarios\/[^/]+\/snapshots$/.test(response.url())
    )
      snapshots.push(response.url())
  })
  await page.getByRole('button', { name: '场景与资源', exact: true }).click()
  await screenshot(page, 'scenario-with-nominal-1440')
  await page.getByRole('button', { name: '单点运输诊断', exact: true }).click()
  const dialog = page.getByRole('dialog')
  await expect(page.getByTestId('nominal-sortie-count')).toHaveText('6架次')
  await expect(dialog).toContainText('完整需求 32 箱')
  await dialog.getByRole('button', { name: '关闭弹窗', exact: true }).click()
  await page.getByRole('button', { name: '更多场景操作', exact: true }).click()
  await page.getByRole('button', { name: '加载原题80箱场景', exact: true }).click()
  await expect(page.locator('.scene-bar')).toContainText('80 箱物资')
  const sid = await page.getByLabel('选择场景').inputValue()
  const original = await (await request.get(`/api/v1/scenarios/${sid}`)).json()
  await page.getByRole('button', { name: '单点运输诊断', exact: true }).click()
  await expect(page.getByTestId('nominal-sortie-count')).toHaveText('18架次')
  await expect(dialog.getByRole('table', { name: '单点安全载重' }).locator('tbody tr')).toHaveCount(
    45,
  )
  await expect(page.locator('.toast')).toHaveCount(0, { timeout: 12000 })
  await dialog.screenshot({
    path: path.resolve('../evidence/browser/verified/nominal-capacity-1440.png'),
  })
  await page.getByLabel('诊断需求点').selectOption('S006')
  await expect(dialog.getByRole('table', { name: '单点安全载重' }).locator('tbody tr')).toHaveCount(
    3,
  )
  await dialog.getByRole('button', { name: '整箱组批', exact: true }).click()
  await page.getByLabel('诊断需求点').selectOption('all')
  await expect(dialog.getByRole('table', { name: '单点整箱组批' }).locator('tbody tr')).toHaveCount(
    18,
  )
  await dialog.screenshot({
    path: path.resolve('../evidence/browser/verified/nominal-batches-1440.png'),
  })
  await page.getByLabel('诊断返航余量').selectOption('0.3')
  await expect(page.getByTestId('nominal-sortie-count')).toHaveText('20架次')
  await dialog.getByRole('button', { name: '敏感性与核查', exact: true }).click()
  await expect(dialog.getByRole('table', { name: '返航余量敏感性' })).toContainText('30.0%')
  await expect(dialog.locator('.nominal-checks span')).toHaveCount(6)
  const download = page.waitForEvent('download')
  await dialog.getByRole('button', { name: '导出诊断', exact: true }).click()
  const file = await download
  const exported = JSON.parse(await fs.readFile((await file.path())!, 'utf8'))
  expect(exported.status).toBe('complete')
  expect(exported.metrics.sortie_count).toBe(20)
  expect(exported.parameters.min_return_soc).toBe(0.3)
  expect(new Set(exported.batches.flatMap((b: { cargo_ids: string[] }) => b.cargo_ids)).size).toBe(
    80,
  )
  expect(
    exported.batches.every(
      (b: Record<string, unknown>) => !('drone_id' in b) && !('battery_id' in b),
    ),
  ).toBe(true)
  await page.getByLabel('诊断返航余量').selectOption('0.4')
  await expect(page.getByTestId('nominal-sortie-count')).toHaveText('—架次')
  await expect(dialog.getByText(/部分站点不满足当前有限组批模型条件/)).toBeVisible()
  await page.getByLabel('诊断返航余量').selectOption('0.3')
  await expect(page.getByTestId('nominal-sortie-count')).toHaveText('20架次')
  for (const [width, height] of [
    [1280, 720],
    [390, 844],
  ]) {
    await page.setViewportSize({ width, height })
    await dialog.getByRole('table', { name: '返航余量敏感性' }).scrollIntoViewIfNeeded()
    await expect(dialog.locator('.nominal-footer')).toBeInViewport()
    await dialog.screenshot({
      path: path.resolve(`../evidence/browser/verified/nominal-sensitivity-${width}.png`),
    })
  }
  expect(await (await request.get(`/api/v1/scenarios/${sid}`)).json()).toEqual(original)
  expect(await (await request.get(`/api/v1/scenarios/${sid}/plans`)).json()).toEqual([])
  expect(snapshots).toHaveLength(2)
  await fs.writeFile(
    path.resolve('../evidence/browser/nominal-diagnostic.json'),
    JSON.stringify(
      {
        scenario_id: sid,
        report: exported,
        snapshot_requests: snapshots.length,
        page_errors: errors,
      },
      null,
      2,
    ) + '\n',
  )
  expect(errors).toEqual([])
})

test('紧急需求插入新增真实箱件，全量重算与历史保留，无法满足新截止时不发布旧方案', async ({
  page,
  request,
}) => {
  test.setTimeout(120000)
  const errors: string[] = []
  page.on('pageerror', (e) => errors.push(e.message))
  await solve(page)
  const sid = await page.getByLabel('选择场景').inputValue()
  const original = (await (await request.get(`/api/v1/scenarios/${sid}/plans`)).json())[0]
  const old = await (await request.get(`/api/v1/plans/${original.plan_id}`)).json()
  const oldSnapshot = await (await request.get(`/api/v1/snapshots/${old.snapshot_id}`)).json()
  await page.getByRole('button', { name: '事件复盘', exact: true }).click()
  await page.getByLabel('故障事件类型').selectOption('urgent')
  await expect(page.locator('.toast')).toHaveCount(0, { timeout: 12000 })
  await page.getByRole('button', { name: '填写紧急需求', exact: true }).click()
  const dialog = page.getByRole('dialog')
  await page.getByLabel('紧急箱件数量').fill('2')
  await page.getByLabel('紧急期望截止分钟').fill('90')
  await page.getByLabel('紧急硬截止分钟').fill('300')
  await page.getByLabel('紧急每箱质量').fill('0')
  await expect(dialog.getByRole('button', { name: '保存需求并重规划', exact: true })).toBeDisabled()
  await page.getByLabel('紧急每箱质量').fill('3')
  for (const [width, height] of [
    [1440, 900],
    [1280, 720],
    [390, 844],
  ]) {
    await page.setViewportSize({ width, height })
    await dialog.screenshot({
      path: path.resolve(`../evidence/browser/verified/urgent-demand-form-${width}.png`),
    })
    expect(await dialog.evaluate((e) => e.scrollWidth <= e.clientWidth + 1)).toBe(true)
    if (width === 390) {
      await dialog
        .getByRole('button', { name: '保存需求并重规划', exact: true })
        .scrollIntoViewIfNeeded()
      await expect(
        dialog.getByRole('button', { name: '保存需求并重规划', exact: true }),
      ).toBeInViewport()
      await dialog.screenshot({
        path: path.resolve('../evidence/browser/verified/urgent-demand-form-footer-390.png'),
      })
    }
  }
  await page.setViewportSize({ width: 1440, height: 900 })
  await dialog.getByRole('button', { name: '保存需求并重规划', exact: true }).click()
  await expect(dialog).toBeHidden()
  await expect(page.locator('.job-banner')).toBeHidden({ timeout: 45000 })
  await expect(page.getByLabel('新增需求安排')).toContainText('2 箱')
  await expect(page.locator('.event-history')).toContainText('新增需求')
  const plan = await (
    await request.get(
      `/api/v1/plans/${(await (await request.get(`/api/v1/scenarios/${sid}/plans`)).json())[0].plan_id}`,
    )
  ).json()
  const snapshot = await (await request.get(`/api/v1/snapshots/${plan.snapshot_id}`)).json()
  const events = await (await request.get(`/api/v1/scenarios/${sid}/events`)).json()
  expect(plan.parent_plan_id).toBe(old.plan_id)
  expect(plan.scenario_state_version).toBe(2)
  expect(plan.validation.status).toBe('passed')
  expect(new Set(plan.sorties.flatMap((r: { cargo_ids: string[] }) => r.cargo_ids)).size).toBe(34)
  expect(events[0].event_type).toBe('demand.added')
  expect(events[0].payload.cargo_items).toHaveLength(2)
  expect(snapshot.scenario.data_origin).toBe('user_input')
  expect(await (await request.get(`/api/v1/plans/${old.plan_id}`)).json()).toEqual(old)
  expect(await (await request.get(`/api/v1/snapshots/${old.snapshot_id}`)).json()).toEqual(
    oldSnapshot,
  )
  await screenshot(page, 'urgent-demand-result-1440')
  await page.getByRole('button', { name: '确认方案', exact: true }).click()
  await expect(page.locator('.toast').filter({ hasText: '方案已确认' })).toBeVisible()
  await page.reload()
  await page.getByRole('button', { name: '事件复盘', exact: true }).click()
  await expect(page.getByLabel('新增需求安排')).toContainText('2 箱')
  await page.getByLabel('故障事件类型').selectOption('urgent')
  await page.getByRole('button', { name: '填写紧急需求', exact: true }).click()
  await page.getByLabel('紧急箱件数量').fill('1')
  await page.getByLabel('紧急期望截止分钟').fill('0')
  await page.getByLabel('紧急硬截止分钟').fill('0')
  await dialog.getByRole('button', { name: '保存需求并重规划', exact: true }).click()
  await expect(dialog).toBeHidden()
  await expect(page.locator('.job-banner')).toBeHidden({ timeout: 45000 })
  await expect(page.getByRole('button', { name: '确认方案', exact: true })).toBeDisabled()
  const after = await (await request.get(`/api/v1/scenarios/${sid}`)).json()
  expect(after.state_version).toBe(3)
  expect(after.cargo_items).toHaveLength(35)
  const jobs = await (await request.get(`/api/v1/scenarios/${sid}/solve-jobs`)).json()
  expect(jobs[0].has_validated_plan).toBe(false)
  expect(jobs[0].plan_id).toBeNull()
  expect((await (await request.get(`/api/v1/scenarios/${sid}/plans`)).json()).length).toBe(2)
  await screenshot(page, 'urgent-demand-no-result-1440')
  await fs.writeFile(
    path.resolve('../evidence/browser/urgent-demand.json'),
    JSON.stringify(
      {
        original_snapshot: oldSnapshot,
        original_plan: old,
        event: events[0],
        snapshot,
        plan,
        impossible_job: jobs[0],
        impossible_scene: after,
        page_errors: errors,
      },
      null,
      2,
    ) + '\n',
  )
  expect(errors).toEqual([])
})

test('容量下界绑定真实方案快照，依据与精确见证可导出且适配窄屏', async ({ page, request }) => {
  const errors: string[] = []
  page.on('pageerror', (error) => errors.push(error.message))
  await solve(page)
  const sid = await page.getByLabel('选择场景').inputValue()
  const source = await (await request.get(`/api/v1/scenarios/${sid}`)).json()
  await page.getByRole('button', { name: '事件复盘', exact: true }).click()
  await page.getByRole('button', { name: '资源分析与试算', exact: true }).click()
  const panel = page.getByRole('region', { name: '运输架次容量下界' })
  await expect(page.getByTestId('capacity-sortie-lower-bound')).toHaveText('4架次')
  await panel.locator('summary').click()
  await expect(panel).toContainText('不能按架次差额计算增机数量')
  const download = page.waitForEvent('download')
  await page.getByRole('button', { name: '导出分析JSON', exact: true }).click()
  const exported = JSON.parse(await fs.readFile((await (await download).path())!, 'utf8'))
  const bound = exported.analysis.capacity_bound
  expect(bound.status).toBe('ready')
  expect(bound.sortie_lower_bound).toBe(4)
  expect(
    bound.witnesses.reduce(
      (sum: number, row: { required_quantity: number }) => sum + row.required_quantity,
      0,
    ),
  ).toBe(32)
  expect(bound.exact.mass_ratio).toMatch(/^\d+\/\d+$/)
  const plan = await (await request.get(`/api/v1/plans/${exported.analysis.plan_id}`)).json()
  const snapshot = await (await request.get(`/api/v1/snapshots/${plan.snapshot_id}`)).json()
  expect(bound.snapshot_content_hash).toBe(snapshot.content_hash)
  expect(bound.sortie_lower_bound).toBeLessThanOrEqual(plan.sorties.length)
  for (const [width, height] of [
    [1440, 900],
    [1280, 720],
    [390, 844],
  ]) {
    await page.setViewportSize({ width, height })
    await panel.scrollIntoViewIfNeeded()
    await screenshot(page, `capacity-bound-${width}`)
    expect(await panel.evaluate((element) => element.scrollWidth <= element.clientWidth + 1)).toBe(
      true,
    )
  }
  expect(await (await request.get(`/api/v1/scenarios/${sid}`)).json()).toEqual(source)
  await fs.writeFile(
    path.resolve('../evidence/browser/capacity-bound.json'),
    JSON.stringify({ analysis: exported.analysis, page_errors: errors }, null, 2) + '\n',
  )
  expect(errors).toEqual([])
})

for (const joint of [false, true]) {
  test(`${joint ? '联合通信' : '运输'}场景运输电池退出，真实改派、确认和历史恢复`, async ({
    page,
    request,
  }) => {
    test.setTimeout(joint ? 180000 : 90000)
    const errors: string[] = []
    page.on('pageerror', (error) => errors.push(error.message))
    const sid = await page.getByLabel('选择场景').inputValue()
    if (joint) {
      const s = await (await request.get(`/api/v1/scenarios/${sid}`)).json()
      s.communication = await (
        await request.get(`/api/v1/scenarios/${sid}/communication-template`)
      ).json()
      s.policy.requires_communication = true
      expect(
        (
          await request.put(`/api/v1/scenarios/${sid}`, {
            data: { expected_state_version: 1, scenario: s },
          })
        ).ok(),
      ).toBe(true)
      await page.reload()
    }
    await page.getByRole('button', { name: '生成真实方案', exact: true }).click()
    await expect(page.locator('.job-banner')).toBeVisible()
    await expect(page.locator('.job-banner')).toBeHidden({ timeout: 90000 })
    await expect(page.getByTestId('sortie-card').first()).toBeVisible()
    const first = (await (await request.get(`/api/v1/scenarios/${sid}/plans`)).json())[0]
    const old = await (await request.get(`/api/v1/plans/${first.plan_id}`)).json()
    const oldSnapshot = await (await request.get(`/api/v1/snapshots/${old.snapshot_id}`)).json()
    const failed = old.sorties[0].battery_id
    await page.getByRole('button', { name: '确认方案', exact: true }).click()
    await expect(page.locator('.toast').filter({ hasText: '方案已确认' })).toBeVisible()
    await page.getByRole('button', { name: '事件复盘', exact: true }).click()
    await page.getByLabel('故障事件类型').selectOption('battery')
    await page.getByLabel('故障运输电池').selectOption(failed)
    await page.getByRole('button', { name: '记录故障并重规划', exact: true }).click()
    await expect(page.locator('.job-banner')).toBeVisible()
    await expect(page.locator('.job-banner')).toBeHidden({ timeout: 90000 })
    await expect(page.locator('.event-history')).toContainText(`运输电池 ${failed} 退出`)
    await expect(page.locator('.comparison-cards')).toContainText('电池改派箱件')
    const summaries = await (await request.get(`/api/v1/scenarios/${sid}/plans`)).json()
    const plan = await (await request.get(`/api/v1/plans/${summaries[0].plan_id}`)).json()
    expect(plan.plan_id).not.toBe(old.plan_id)
    expect(plan.parent_plan_id).toBe(old.plan_id)
    expect(plan.scenario_state_version).toBe(old.scenario_state_version + 1)
    expect(plan.validation.status).toBe('passed')
    expect(plan.sorties.every((row: { battery_id: string }) => row.battery_id !== failed)).toBe(
      true,
    )
    expect(
      new Set(plan.sorties.flatMap((row: { cargo_ids: string[] }) => row.cargo_ids)).size,
    ).toBe(32)
    if (joint) expect(plan.communication_report.coverage_gap_s).toBe(0)
    expect(await (await request.get(`/api/v1/plans/${old.plan_id}`)).json()).toEqual(old)
    expect(await (await request.get(`/api/v1/snapshots/${old.snapshot_id}`)).json()).toEqual(
      oldSnapshot,
    )
    const events = await (await request.get(`/api/v1/scenarios/${sid}/events`)).json()
    expect(events).toHaveLength(1)
    expect(events[0].event_type).toBe('battery.unavailable')
    expect(events[0].payload).toEqual({ battery_id: failed })
    await page.getByRole('button', { name: '确认方案', exact: true }).click()
    await expect(page.locator('.toast').filter({ hasText: '方案已确认' })).toBeVisible()
    const name = joint ? 'joint-battery-fault' : 'battery-fault'
    await screenshot(page, `${name}-1440`)
    await page.reload()
    await page.getByRole('button', { name: '事件复盘', exact: true }).click()
    await expect(page.locator('.event-history')).toContainText(`运输电池 ${failed} 退出`)
    await expect(page.locator('.comparison-cards')).toContainText('电池改派箱件')
    await page.setViewportSize({ width: 1280, height: 720 })
    await screenshot(page, `${name}-1280`)
    for (const width of [1280, 390]) {
      await page.setViewportSize({ width, height: width === 390 ? 844 : 720 })
      await page.locator('.comparison-cards').scrollIntoViewIfNeeded()
      await page.screenshot({
        path: path.resolve(`../evidence/browser/verified/${name}-changes-${width}.png`),
      })
    }
    await fs.writeFile(
      path.resolve(`../evidence/solver/${joint ? 'joint-' : ''}battery-replan.json`),
      JSON.stringify(
        {
          old_snapshot: oldSnapshot,
          old_plan: old,
          event: events[0],
          snapshot: await (await request.get(`/api/v1/snapshots/${plan.snapshot_id}`)).json(),
          plan,
          page_errors: errors,
        },
        null,
        2,
      ) + '\n',
    )
    expect(errors).toEqual([])
  })
}

test('连续通信联合调度、真实中继地图与资源窗口、确认及报告', async ({ page, request }) => {
  test.setTimeout(120000)
  const errors: string[] = []
  page.on('pageerror', (e) => errors.push(e.message))
  page.on('console', (e) => {
    if (e.type() === 'error') errors.push(e.text())
  })
  const sid = await page.getByLabel('选择场景').inputValue()
  await page.getByRole('button', { name: '场景与资源', exact: true }).click()
  await page.getByRole('button', { name: '配置通信资源', exact: true }).click()
  await page.getByLabel('要求全程连续通信，启用运输与中继联合调度').check()
  await expect(page.getByRole('dialog')).toContainText('R-COMP-06')
  await page.setViewportSize({ width: 1280, height: 720 })
  await page.screenshot({
    path: path.resolve('../evidence/browser/verified/communication-config-1280.png'),
  })
  await page.getByRole('button', { name: '保存通信配置', exact: true }).click()
  await expect(page.getByRole('dialog')).toBeHidden()
  await page.setViewportSize({ width: 1440, height: 900 })
  await page.getByRole('button', { name: '调度工作台', exact: true }).click()
  await page.getByRole('button', { name: '生成真实方案', exact: true }).click()
  await expect(page.locator('.job-banner')).toBeVisible()
  await expect(page.locator('.job-banner')).toBeHidden({ timeout: 90000 })
  const panel = page.getByRole('region', { name: '通信协同结果' })
  await expect(panel).toContainText('模型内无通信缺口')
  await expect(page.locator('.map-marker-relay').first()).toBeAttached()
  const summaries = await (await request.get(`/api/v1/scenarios/${sid}/plans`)).json()
  const plan = await (await request.get(`/api/v1/plans/${summaries[0].plan_id}`)).json()
  expect(plan.relay_sorties.length).toBeGreaterThan(0)
  expect(plan.communication_report.coverage_gap_s).toBe(0)
  expect(plan.model_scope).toContain('communication')
  await screenshot(page, 'joint-workspace-1440')
  await panel.scrollIntoViewIfNeeded()
  await panel.getByRole('button', { name: '能源组件', exact: true }).click()
  await page.screenshot({
    path: path.resolve('../evidence/browser/verified/joint-resource-windows-1440.png'),
  })
  await page.getByRole('button', { name: '确认方案', exact: true }).click()
  await expect(page.locator('.toast').filter({ hasText: '方案已确认' })).toBeVisible()
  const report = await page.context().newPage()
  await report.goto(`/api/v1/plans/${plan.plan_id}/report`)
  await expect(report.getByText('通信与中继保障', { exact: true })).toBeVisible()
  await report.pdf({
    path: path.resolve('../evidence/browser/verified/joint-report.pdf'),
    printBackground: true,
    preferCSSPageSize: true,
  })
  await report.close()
  await page.getByRole('button', { name: '事件复盘', exact: true }).click()
  await page.getByRole('button', { name: '资源分析与试算', exact: true }).click()
  await page.getByRole('button', { name: '中继能源', exact: true }).click()
  await expect(page.locator('.analysis-resource-scroll')).toContainText('R-COMP-01')
  await screenshot(page, 'joint-resource-analysis-1440')
  await page.reload()
  await expect(page.getByRole('region', { name: '通信协同结果' })).toContainText('模型内无通信缺口')
  await page.setViewportSize({ width: 1280, height: 720 })
  await screenshot(page, 'joint-workspace-1280')
  expect(errors).toEqual([])
})

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

test('中继机退出保存新版本，真实重规划保留旧方案和连续保障', async ({ page, request }) => {
  test.setTimeout(150000)
  const errors: string[] = []
  page.on('pageerror', (e) => errors.push(e.message))
  const sid = await page.getByLabel('选择场景').inputValue()
  const s = await (await request.get(`/api/v1/scenarios/${sid}`)).json()
  s.communication = await (
    await request.get(`/api/v1/scenarios/${sid}/communication-template`)
  ).json()
  s.policy.requires_communication = true
  expect(
    (
      await request.put(`/api/v1/scenarios/${sid}`, {
        data: { expected_state_version: 1, scenario: s },
      })
    ).ok(),
  ).toBe(true)
  await page.reload()
  await page.getByRole('button', { name: '生成真实方案', exact: true }).click()
  await expect(page.locator('.job-banner')).toBeVisible()
  await expect(page.locator('.job-banner')).toBeHidden({ timeout: 90000 })
  await expect(page.getByRole('region', { name: '通信协同结果' })).toContainText('模型内无通信缺口')
  const before = (await (await request.get(`/api/v1/scenarios/${sid}/plans`)).json())[0]
  const oldPlan = await (await request.get(`/api/v1/plans/${before.plan_id}`)).json()
  expect(oldPlan.relay_sorties.some((r: { drone_id: string }) => r.drone_id === 'R01')).toBe(true)
  await page.getByRole('button', { name: '事件复盘', exact: true }).click()
  await page.getByLabel('故障机体').selectOption('R01')
  await page.getByRole('button', { name: '记录故障并重规划', exact: true }).click()
  await expect(page.locator('.job-banner')).toBeVisible()
  await expect(page.locator('.job-banner')).toBeHidden({ timeout: 90000 })
  const summaries = await (await request.get(`/api/v1/scenarios/${sid}/plans`)).json()
  expect(summaries).toHaveLength(2)
  const newPlan = await (await request.get(`/api/v1/plans/${summaries[0].plan_id}`)).json()
  expect(newPlan.parent_plan_id).toBe(oldPlan.plan_id)
  expect(newPlan.scenario_state_version).toBe(3)
  expect(newPlan.relay_sorties.every((r: { drone_id: string }) => r.drone_id !== 'R01')).toBe(true)
  expect(newPlan.communication_report.coverage_gap_s).toBe(0)
  expect(await (await request.get(`/api/v1/plans/${oldPlan.plan_id}`)).json()).toEqual(oldPlan)
  const snapshot = await (await request.get(`/api/v1/snapshots/${newPlan.snapshot_id}`)).json()
  const events = await (await request.get(`/api/v1/scenarios/${sid}/events`)).json()
  await fs.writeFile(
    path.resolve('../evidence/solver/joint-replan.json'),
    JSON.stringify({ snapshot, event: events[0], previous_plan: oldPlan, plan: newPlan }, null, 2) +
      '\n',
  )
  await expect(page.getByRole('region', { name: '通信协同结果' })).toContainText('模型内无通信缺口')
  await screenshot(page, 'relay-fault-replan-1440')
  await page.reload()
  await expect(page.getByRole('region', { name: '通信协同结果' })).toContainText('模型内无通信缺口')
  await page.getByRole('button', { name: '事件复盘', exact: true }).click()
  await expect(page.getByLabel('中继方案变化')).toContainText('联合能耗变化')
  await page.getByLabel('中继方案变化').scrollIntoViewIfNeeded()
  await page.screenshot({
    path: path.resolve('../evidence/browser/verified/relay-fault-differences-1440.png'),
  })
  expect(errors).toEqual([])
})

test('历史方案等待绑定原始快照，延迟期间不显示混合版本结果', async ({ page, request }) => {
  await solve(page)
  const sid = await page.getByLabel('选择场景').inputValue()
  const s = await (await request.get(`/api/v1/scenarios/${sid}`)).json()
  s.cargo_items[0].mass_kg = 99
  expect(
    (
      await request.put(`/api/v1/scenarios/${sid}`, {
        data: { expected_state_version: 1, scenario: s },
      })
    ).ok(),
  ).toBe(true)
  let release = () => {}
  const gate = new Promise<void>((resolve) => {
    release = resolve
  })
  await page.route('**/api/v1/snapshots/*', async (route) => {
    await gate
    await route.continue()
  })
  await page.reload()
  await expect(page.getByLabel('方案快照绑定')).toContainText('正在加载 v1')
  await expect(page.getByTestId('sortie-card')).toHaveCount(0)
  await expect(page.getByRole('button', { name: '生成真实方案', exact: true })).toBeDisabled()
  await expect(page.getByRole('button', { name: '检查报告', exact: true })).toBeDisabled()
  release()
  await expect(page.getByLabel('方案快照绑定')).toBeHidden()
  await expect(page.getByTestId('sortie-card').first()).toBeVisible()
  await expect(page.locator('.alert').filter({ hasText: '历史方案' })).toContainText(
    '场景已更新为 v2',
  )
  await expect(page.getByRole('button', { name: '确认方案', exact: true })).toBeDisabled()
  await page.unroute('**/api/v1/snapshots/*')
  let failSnapshots = true
  await page.route('**/api/v1/snapshots/*', async (route) => {
    if (failSnapshots)
      await route.fulfill({ status: 503, json: { error: { message: '测试快照读取失败' } } })
    else await route.continue()
  })
  await page.reload()
  await expect(page.getByLabel('方案快照绑定')).toContainText('原始输入加载失败', {
    timeout: 20000,
  })
  await expect(page.getByTestId('sortie-card')).toHaveCount(0)
  failSnapshots = false
  await page.getByRole('button', { name: '重试加载快照', exact: true }).click()
  await expect(page.getByTestId('sortie-card').first()).toBeVisible()
})

test('80箱冻结联合任务分区，真实资源缺口、峰值分配与JSON导出', async ({ page, request }) => {
  test.setTimeout(150000)
  const errors: string[] = []
  page.on('pageerror', (e) => errors.push(e.message))
  page.on('console', (e) => {
    if (e.type() === 'error') errors.push(e.text())
  })
  await page.getByRole('button', { name: '更多场景操作', exact: true }).click()
  await page.getByRole('button', { name: '加载原题80箱场景', exact: true }).click()
  await expect(page.locator('.scene-bar')).toContainText('80 箱物资')
  const sid = await page.getByLabel('选择场景').inputValue()
  expect((await (await request.get(`/api/v1/scenarios/${sid}`)).json()).cargo_items).toHaveLength(
    80,
  )
  await page.getByRole('button', { name: '场景与资源', exact: true }).click()
  await page.getByRole('button', { name: '配置通信资源', exact: true }).click()
  await page.getByLabel('要求全程连续通信，启用运输与中继联合调度').check()
  await page.getByRole('button', { name: '保存通信配置', exact: true }).click()
  await expect(page.getByRole('dialog')).toBeHidden()
  await page.getByRole('button', { name: '调度工作台', exact: true }).click()
  await page.getByRole('button', { name: '生成真实方案', exact: true }).click()
  await expect(page.locator('.job-banner')).toBeVisible()
  await expect(page.locator('.job-banner')).toBeHidden({ timeout: 90000 })
  await expect(page.getByRole('region', { name: '通信协同结果' })).toContainText('模型内无通信缺口')
  const summary = (await (await request.get(`/api/v1/scenarios/${sid}/plans`)).json())[0]
  const plan = await (await request.get(`/api/v1/plans/${summary.plan_id}`)).json()
  expect(plan.sorties.flatMap((r: { cargo_ids: string[] }) => r.cargo_ids)).toHaveLength(80)
  await page.getByRole('button', { name: '事件复盘', exact: true }).click()
  await page.getByRole('button', { name: '冻结任务分区', exact: true }).click()
  const analysis = page.getByLabel('冻结方案分区分析', { exact: true })
  await expect(analysis).toBeVisible({ timeout: 30000 })
  await expect(page.locator('.partition-atom')).toHaveCount(3)
  await expect(page.locator('.partition-group')).toHaveCount(2)
  await expect(page.locator('.partition-shortage')).toContainText('C型运输机')
  await screenshot(page, 'frozen-partition-1440')
  const download = page.waitForEvent('download')
  await page.getByRole('button', { name: '导出完整分区', exact: true }).click()
  const file = await download
  const report = JSON.parse(await fs.readFile((await file.path())!, 'utf8'))
  expect(report.plan_id).toBe(plan.plan_id)
  expect(report.snapshot_id).toBe(plan.snapshot_id)
  expect(report.status).toBe('ready')
  await page.getByRole('button', { name: '3 个任务组', exact: true }).click()
  await expect(page.locator('.partition-group')).toHaveCount(3)
  await page.getByRole('button', { name: '均衡优先', exact: true }).click()
  await page.locator('.partition-group-grid').scrollIntoViewIfNeeded()
  await page.screenshot({
    path: path.resolve('../evidence/browser/verified/frozen-partition-groups-1440.png'),
  })
  await page
    .locator('.partition-assignment-details')
    .first()
    .getByText('查看峰值见证与实体分配', { exact: true })
    .click()
  await expect(page.locator('.partition-assignment-details').first()).toContainText('同时占用')
  await page
    .locator('.partition-assignment-details')
    .first()
    .getByText('查看峰值见证与实体分配', { exact: true })
    .click()
  await page.setViewportSize({ width: 1280, height: 720 })
  await page.locator('.partition-configuration').scrollIntoViewIfNeeded()
  await page.screenshot({
    path: path.resolve('../evidence/browser/verified/frozen-partition-resources-1280.png'),
  })
  await page.reload()
  await expect(page.getByLabel('选择场景')).toHaveValue(sid)
  await page.getByRole('button', { name: '事件复盘', exact: true }).click()
  await page.getByRole('button', { name: '冻结任务分区', exact: true }).click()
  await expect(page.getByLabel('冻结方案分区分析')).toContainText(plan.plan_id, { timeout: 30000 })
  await page.setViewportSize({ width: 390, height: 844 })
  await expect
    .poll(async () =>
      page.evaluate(
        () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
      ),
    )
    .toBeLessThanOrEqual(2)
  await screenshot(page, 'frozen-partition-mobile')
  expect(errors).toEqual([])
})

test('生产构建只允许本机请求，真实求解与事件闭环离线可用', async ({ page, context, request }) => {
  test.setTimeout(120000)
  const external: string[] = [],
    errors: string[] = []
  page.on('pageerror', (error) => errors.push(error.message))
  page.on('console', (message) => {
    if (message.type() === 'error') errors.push(message.text())
  })
  await context.route('**/*', async (route) => {
    const url = new URL(route.request().url())
    if (
      ['http:', 'https:'].includes(url.protocol) &&
      !['127.0.0.1', 'localhost', '[::1]'].includes(url.hostname)
    ) {
      external.push(url.origin)
      await route.abort('internetdisconnected')
    } else await route.continue()
  })
  await page.goto('http://127.0.0.1:8011/')
  await expect(page.getByRole('button', { name: '生成真实方案', exact: true })).toBeVisible()
  await solve(page)
  await expect(page.locator('.map-mode')).toHaveText('题设DEM · 离线')
  const sid = await page.getByLabel('选择场景').inputValue()
  const initial = (await (await request.get(`/api/v1/scenarios/${sid}/plans`)).json())[0]
  await page.getByRole('button', { name: '确认方案', exact: true }).click()
  await expect(page.locator('.toast').filter({ hasText: '方案已确认' })).toBeVisible()
  await page.getByRole('button', { name: '事件复盘', exact: true }).click()
  await page.getByLabel('故障机体').selectOption('U01')
  await page.getByRole('button', { name: '记录故障并重规划', exact: true }).click()
  await expect(page.locator('.job-banner')).toBeVisible()
  await expect(page.locator('.job-banner')).toBeHidden({ timeout: 45000 })
  const latest = (await (await request.get(`/api/v1/scenarios/${sid}/plans`)).json())[0]
  const plan = await (await request.get(`/api/v1/plans/${latest.plan_id}`)).json()
  expect(plan.parent_plan_id).toBe(initial.plan_id)
  expect(plan.validation.status).toBe('passed')
  expect(plan.sorties.every((route: { drone_id: string }) => route.drone_id !== 'U01')).toBe(true)
  await screenshot(page, 'production-offline-1440')
  const download = page.waitForEvent('download')
  await page.getByRole('link', { name: '计划JSON', exact: true }).click()
  const file = await download
  expect(JSON.parse(await fs.readFile((await file.path())!, 'utf8')).plan_id).toBe(plan.plan_id)
  await page.setViewportSize({ width: 1280, height: 720 })
  await screenshot(page, 'production-offline-1280')
  await fs.writeFile(
    path.resolve('../evidence/browser/production-offline.json'),
    JSON.stringify(
      {
        origin: 'http://127.0.0.1:8011',
        policy: 'Block all non-loopback HTTP(S) requests in the browser context.',
        scenario_id: sid,
        plan_id: plan.plan_id,
        parent_plan_id: initial.plan_id,
        snapshot_id: plan.snapshot_id,
        validation: plan.validation.status,
        external_requests: external,
        console_errors: errors,
      },
      null,
      2,
    ) + '\n',
  )
  expect(external).toEqual([])
  expect(errors).toEqual([])
})

test.beforeEach(async ({ request, page }) => {
  const response = await request.post('/api/v1/scenarios/examples', {
    data: { example: 'compact' },
  })
  expect(response.status()).toBe(201)
  const scene = await response.json()
  await page.addInitScript((id) => {
    if (!localStorage.getItem('yuanhang-scenario')) localStorage.setItem('yuanhang-scenario', id)
  }, scene.scenario_id)
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
