# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workflow.spec.ts >> 深入优化保留同快照基线，刷新后继续真实计算
- Location: tests\workflow.spec.ts:1476:1

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('.job-banner')
Expected: visible
Timeout: 15000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" locator('.job-banner') with timeout 15000ms
  - waiting for locator('.job-banner')

```

```yaml
- link "返回新版首页":
  - /url: "#/home"
- complementary:
  - link "援航 YUANHANG RESCUE":
    - /url: "#"
    - strong: 援航
    - text: YUANHANG RESCUE
  - text: 应
  - strong: 援航救援工作组
  - text: 应急协同 · 本机工作空间 任务协同
  - navigation:
    - button "数据大屏"
    - button "场景与资源"
    - button "地图与地形"
    - button "调度工作台"
    - button "调度安排"
    - button "方案对比"
    - button "事件复盘"
    - button "历史档案"
    - button "新手教程"
  - strong: 救援决策，从这里开始
  - paragraph: 准备数据、读取地形、生成方案。跟着教程完成第一次调度。
  - button "打开上手指南"
  - text: 本机服务 离线可用
  - button "使用教程与常见问题"
  - button "账户与本机档案":
    - text: 本
    - strong: 本机调度员
    - text: 调度负责人 · 本机档案
- banner:
  - text: 救援工作空间
  - strong: 调度工作台
  - button "切换浅色主题"
  - button "暂停动态背景" [pressed]
  - text: 本地服务已连接
  - button "查看模型说明"
  - button "打开个人档案": 本
- main:
  - combobox "选择场景":
    - option "镇龙乡 · 应急运输演练" [selected]
    - option "镇龙乡 · 应急运输演练"
    - option "镇龙乡 · 应急运输演练"
    - option "镇龙乡 · 应急运输演练 · 压力C · 能耗+20%/时长+10%/SOH×90%"
    - option "镇龙乡 · 应急运输演练 · 压力B · 能耗+10%/时长+5%/SOH×95%"
    - option "镇龙乡 · 应急运输演练 · 压力A · 原条件"
    - option "镇龙乡 · 应急运输演练"
    - option "镇龙乡 · 应急运输演练 · 资源与余量试算"
    - option "镇龙乡 · 应急运输演练"
    - option "镇龙乡 · 应急运输演练 · 资源与余量试算"
    - option "镇龙乡 · 应急运输演练"
    - option "偏好取舍演练（保留硬截止）"
    - option "镇龙乡 · 应急运输演练"
    - option "镇龙乡 · 应急运输演练"
    - option "镇龙乡 · 应急运输演练"
    - option "镇龙乡 · 应急运输演练"
    - option "镇龙乡 · 应急运输演练"
    - option "镇龙乡 · 应急运输演练"
    - option "镇龙乡 · 原题运输基准"
    - option "镇龙乡 · 应急运输演练"
    - option "镇龙乡 · 应急运输演练"
    - option "镇龙乡 · 应急运输演练"
    - option "镇龙乡 · 应急运输演练"
    - option "镇龙乡 · 应急运输演练"
    - option "镇龙乡 · 应急运输演练"
    - option "镇龙乡 · 应急运输演练"
    - option "镇龙乡 · 应急运输演练"
    - option "镇龙乡 · 应急运输演练"
    - option "镇龙乡 · 应急运输演练"
    - option "镇龙乡 · 原题运输基准"
    - option "镇龙乡 · 应急运输演练"
    - option "镇龙乡 · 应急运输演练 · 压力C · 能耗+20%/时长+10%/SOH×90%"
    - option "镇龙乡 · 应急运输演练 · 压力B · 能耗+10%/时长+5%/SOH×95%"
    - option "镇龙乡 · 应急运输演练 · 压力A · 原条件"
    - option "镇龙乡 · 应急运输演练 · 资源与余量试算"
    - option "镇龙乡 · 应急运输演练 · 压力C · 能耗+20%/时长+10%/SOH×90%"
    - option "镇龙乡 · 应急运输演练 · 压力B · 能耗+10%/时长+5%/SOH×95%"
    - option "镇龙乡 · 应急运输演练 · 压力A · 原条件"
    - option "镇龙乡 · 应急运输演练 · 资源与余量试算"
    - option "镇龙乡 · 应急运输演练"
    - option "无可用机体的增配诊断 1792332967009 · 资源增配诊断"
    - option "无可用机体的增配诊断 1792332967009"
    - option "成都合成区域 CSV 救援任务 1792332957636"
    - option "镇龙乡 · 应急运输演练"
    - option "W1 browser exercise 1792332948958"
    - option "Correction exercise 1792332942469"
    - option "地图工作台验收 1792332924982"
    - option "地图工作台验收 1792332923517"
    - option "地图工作台验收 1792332917807"
    - option "地图工作台验收 1792332913167"
    - option "失败完整保留 1792332907600 · 隔离评测"
    - option "无可用机队评测 1792332907474"
    - option "同输入三偏好验收 1792332890977 · 隔离评测"
    - option "浏览器评测输入 1792332889694"
    - option "experience 无DEM输入"
    - option "experience 版本来源检查"
    - option "镇龙乡 · 应急运输演练"
    - option "在途冻结输入的方法对照 1792332840540 · 隔离评测"
    - option "在飞备用电池退出演练 1792332826025 · 在途剩余输入"
    - option "在飞备用电池退出演练 1792332826025"
    - option "在途插单与档案验收 1792332806067 · 在途剩余输入"
    - option "在途插单与档案验收 1792332806067"
  - text: 5 个需求点 32 箱物资 场景起点 08:00 模拟演练 v1
  - button "新建演练"
  - button "更多场景操作"
  - text: MISSION CONTROL
  - heading "每一份物资，都有清晰的下一程 LIVE WORKSPACE" [level=1]
  - paragraph: 从真实输入出发，统筹箱件、机体与电池，生成可核对的运输方案。
  - combobox "选择历史方案":
    - option "时间优先 · 快速 · v1" [selected]
  - button "检查报告"
  - button "查看调度安排"
  - button "深入优化30秒"
  - button "重新求解"
  - text: 当前方案 · 真实数据联动
  - button "三维与高度分析"
  - button "卫星地图 / 导入DEM"
  - button "方案对比"
  - button "历史档案"
  - text: 已安排箱件 32/ 32 箱 完整服务 · 箱件唯一分配 最后交付 1时55分 最后返航 2时00分 预计总能耗 23.43kWh 7 架次 · 已含返航 最低返航电量 21.6% 策略下限 20.0% 硬截止已检查 期望延期 3 条 · 加权箱秒 119,872 直接取舍 v2 · 硬截止与完整物资保障始终必选
  - heading "运输任务 7" [level=3]
  - button "编辑场景资源"
  - button "架次"
  - button "需求"
  - button "箱件"
  - textbox "搜索任务":
    - /placeholder: 搜索编号、机体、需求点…
  - button "01 U07 已规划 S001 → S006 8 箱 00:09":
    - text: "01"
    - strong: U07
    - text: 已规划
    - paragraph: S001 → S006
    - text: 8 箱 00:09
  - button "02 U05 已规划 S007 3 箱 00:06":
    - text: "02"
    - strong: U05
    - text: 已规划
    - paragraph: S007
    - text: 3 箱 00:06
  - button "03 U01 已规划 S011 → S010 3 箱 00:06":
    - text: "03"
    - strong: U01
    - text: 已规划
    - paragraph: S011 → S010
    - text: 3 箱 00:06
  - button "04 U07 已规划 S006 → S011 → S001 7 箱 00:47":
    - text: "04"
    - strong: U07
    - text: 已规划
    - paragraph: S006 → S011 → S001
    - text: 7 箱 00:47
  - button "05 U07 已规划 S010 → S001 8 箱 01:29":
    - text: "05"
    - strong: U07
    - text: 已规划
    - paragraph: S010 → S001
    - text: 8 箱 01:29
  - button "06 U05 已规划 S007 2 箱 00:33":
    - text: "06"
    - strong: U05
    - text: 已规划
    - paragraph: S007
    - text: 2 箱 00:33
  - button "07 U01 已规划 S011 1 箱 00:43":
    - text: "07"
    - strong: U01
    - text: 已规划
    - paragraph: S011
    - text: 1 箱 00:43
  - text: 稳定ID跨视图联动
  - region "Map"
  - button "定位凤丹村无人机调度中心": O 凤丹村无人机调度
  - button "定位那从": 1 S011
  - button "定位平旺、那龙、镇龙乡": 2 S001
  - button "定位六昌、木路": 3 S006
  - button "定位佛子、那桑、银坑": 4 S007
  - button "定位镇龙乡": 5 S010
  - text: 2 km 场景地图 WGS84 题设DEM · 离线
  - group "地图底图":
    - button "离线地形" [pressed]
    - button "卫星影像 联网"
  - button "放大地图"
  - button "缩小地图"
  - button "适配全部点位"
  - button "图层管理"
  - text: N ↑ 调度中心 需求点 运输航线
  - link "© OpenStreetMap contributors · ODbL":
    - /url: https://www.openstreetmap.org/copyright
  - text: · 历史背景资料 离线可用 · 图上路线为任务级建议
  - button "播放计划回放"
  - text: 00:00:00
  - slider "计划回放时钟": "0"
  - text: 计划示意回放 非执行事实
  - complementary:
    - heading "策略方案" [level=3]
    - paragraph: 同一快照 · 相同保障要求 · 直接取舍 v2
    - strong: 时间优先
    - paragraph: 缩短最后返航时间；期望延期作为同分时次目标
    - text: 2时00分 23.43 kWh 运输指标 · 直接取舍 v2 期望延期 3 条 / 32 条 · 加权 119,872 箱秒
    - code: PLAN-8B8E2241665444CE
    - button "当前展示方案"
    - strong: 能耗优先
    - paragraph: 降低总能耗；期望延期作为同分时次目标
    - button "真实计算此策略"
    - strong: 时间能耗折中
    - text: 每 1 kWh 折合 300 秒
    - button "真实计算折中策略"
    - strong: 全部卡片使用运输口径
    - paragraph: 硬截止、容量、SOC 与完整物资保障不可突破；期望截止是软目标，节能可能增加延期。折中权重为 300 秒/kWh，不代表服务区保障公平。
    - paragraph: 不同目标可以得到相同结果；请先计算同快照、同规则的三个策略，再核对排程和交付分析。
    - text: 限时搜索的已验证候选，未证明全局最优；费用未配置，不显示人民币。
    - heading "选中架次" [level=3]
    - paragraph: SRT-6396ff71573f
    - text: U07 基地准备
    - strong: 00:00:00
    - text: S001 · 7箱交接
    - strong: 00:21:18
    - text: S006 · 1箱交接
    - strong: 00:32:50
    - text: 返回基地
    - strong: 00:38:43
    - text: 使用电池
    - strong: BAT-C-01
    - text: 预计能耗
    - strong: 4.762 kWh
    - text: 返航SOC
    - strong: 40.5%
    - text: 装载箱件
    - strong: 8 箱
    - button "在箱件清单中追踪"
  - heading "资源时间轴 RESOURCE TIMELINE" [level=3]
  - paragraph: 准备、执行与补能，按实体资源核对
  - button "机体"
  - button "电池"
  - button "展开时间轴"
  - text: 资源 / 型号 00:00 00:21 00:42 01:03 01:24 01:45 02:06
  - strong: U01
  - text: A型
  - button "3箱"
  - button "1箱"
  - strong: U05
  - text: B型
  - button "3箱"
  - button "2箱"
  - strong: U07
  - text: C型
  - button "8箱"
  - button "7箱"
  - button "8箱"
  - text: 准备 执行架次 相对场景起点 · 区间左闭右开 独立检查已完成 · 仅在声明模型范围内可行
  - button "查看适用范围"
  - link "任务CSV":
    - /url: /api/v1/plans/PLAN-8B8E2241665444CE/export?format=csv
  - link "GeoJSON":
    - /url: /api/v1/plans/PLAN-8B8E2241665444CE/export?format=geojson
  - link "计划JSON":
    - /url: /api/v1/plans/PLAN-8B8E2241665444CE/export?format=json
  - link "打印报告":
    - /url: /api/v1/plans/PLAN-8B8E2241665444CE/report
  - button "确认方案"
```

# Test source

```ts
  1383 |   // The creation indicator can precede submission while the Snapshot is being
  1384 |   // saved. Refresh recovery starts from an actual server-accepted SolveJob.
  1385 |   const accepted = page.waitForResponse(
  1386 |     (r) =>
  1387 |       new URL(r.url()).pathname === '/api/v1/solve-jobs' &&
  1388 |       r.request().method() === 'POST' &&
  1389 |       r.status() === 202,
  1390 |   )
  1391 |   await page.getByRole('button', { name: '生成真实方案', exact: true }).click()
  1392 |   await expect(page.locator('.job-banner')).toBeVisible()
  1393 |   const submitted = await (await accepted).json()
  1394 |   expect(submitted.job_id).toBeTruthy()
  1395 |   await page.reload()
  1396 |   await expect(page.getByTestId('sortie-card').first()).toBeVisible({ timeout: 45000 })
  1397 |   const jobs = await (await request.get(`/api/v1/scenarios/${sceneId}/solve-jobs`)).json()
  1398 |   expect(jobs.length).toBe(1)
  1399 |   expect(jobs[0].job_state).toBe('completed')
  1400 |   expect(jobs[0].has_validated_plan).toBe(true)
  1401 |   const storedPlan = await (await request.get(`/api/v1/plans/${jobs[0].plan_id}`)).json()
  1402 |   const storedSnapshot = await (
  1403 |     await request.get(`/api/v1/snapshots/${storedPlan.snapshot_id}`)
  1404 |   ).json()
  1405 |   expect(storedPlan.validation.status).toBe('passed')
  1406 |   expect(storedPlan.snapshot_id).toBe(jobs[0].snapshot_id)
  1407 | 
  1408 |   // A plans read can precede the worker commit while job metadata follows it.
  1409 |   // A persisted selection can load its real Plan directly despite that stale list.
  1410 |   // Assert the displayed identity and immutable input, not redundant list reads.
  1411 |   let planReads = 0
  1412 |   await page.route(`**/api/v1/scenarios/${sceneId}/plans`, async (route) => {
  1413 |     planReads++
  1414 |     if (planReads === 1) await route.fulfill({ json: [] })
  1415 |     else await route.continue()
  1416 |   })
  1417 |   await page.route(`**/api/v1/scenarios/${sceneId}/solve-jobs`, async (route) => {
  1418 |     await new Promise((resolve) => setTimeout(resolve, 250))
  1419 |     await route.continue()
  1420 |   })
  1421 |   const submittedJobs: string[] = []
  1422 |   page.on('request', (r) => {
  1423 |     if (r.method() === 'POST' && new URL(r.url()).pathname === '/api/v1/solve-jobs')
  1424 |       submittedJobs.push(r.url())
  1425 |   })
  1426 |   const staleListResponse = page.waitForResponse(
  1427 |     (r) => new URL(r.url()).pathname === `/api/v1/scenarios/${sceneId}/plans`,
  1428 |   )
  1429 |   const restoredPlanResponse = page.waitForResponse(
  1430 |     (r) => new URL(r.url()).pathname === `/api/v1/plans/${storedPlan.plan_id}`,
  1431 |   )
  1432 |   const restoredSnapshotResponse = page.waitForResponse(
  1433 |     (r) => new URL(r.url()).pathname === `/api/v1/snapshots/${storedPlan.snapshot_id}`,
  1434 |   )
  1435 |   await page.reload()
  1436 |   await expect(page.getByTestId('sortie-card').first()).toBeVisible()
  1437 |   expect(await (await staleListResponse).json()).toEqual([])
  1438 |   expect(await (await restoredPlanResponse).json()).toEqual(storedPlan)
  1439 |   expect(await (await restoredSnapshotResponse).json()).toEqual(storedSnapshot)
  1440 |   await expect(page.getByRole('link', { name: '计划JSON', exact: true })).toHaveAttribute(
  1441 |     'href',
  1442 |     new RegExp(`/plans/${storedPlan.plan_id}/export`),
  1443 |   )
  1444 |   await expect(page.getByRole('status', { name: '方案快照绑定', exact: true })).toHaveCount(0)
  1445 |   await expect(page.locator('.toast').filter({ hasText: '真实计算完成' })).toHaveCount(0)
  1446 |   const recovered = await (await request.get(`/api/v1/scenarios/${sceneId}/solve-jobs`)).json()
  1447 |   expect(recovered).toHaveLength(1)
  1448 |   expect(recovered[0].job_id).toBe(jobs[0].job_id)
  1449 |   expect(recovered[0].plan_id).toBe(storedPlan.plan_id)
  1450 |   expect(recovered[0].snapshot_id).toBe(storedSnapshot.snapshot_id)
  1451 |   expect(submittedJobs).toEqual([])
  1452 | })
  1453 | 
  1454 | test('打印报告包含真实任务并可离线保存PDF', async ({ page }) => {
  1455 |   await solve(page)
  1456 |   const popup = page.waitForEvent('popup')
  1457 |   await page.getByRole('link', { name: '打印报告', exact: true }).click()
  1458 |   const report = await popup
  1459 |   await expect(report.getByRole('heading', { level: 1 })).toHaveText('援航 · 运输调度与资源报告')
  1460 |   await expect(report.locator('table')).toHaveCount(4)
  1461 |   await expect(report.locator('body')).toContainText('逐箱物资追踪')
  1462 |   await expect(report.locator('.identity')).toContainText('输入Hash')
  1463 |   await report.screenshot({
  1464 |     path: path.resolve('../evidence/browser/verified/print-report-screen.png'),
  1465 |   })
  1466 |   await report.pdf({
  1467 |     path: path.resolve('../evidence/browser/verified/print-report.pdf'),
  1468 |     format: 'A4',
  1469 |     landscape: true,
  1470 |     printBackground: true,
  1471 |     preferCSSPageSize: true,
  1472 |   })
  1473 |   await report.close()
  1474 | })
  1475 | 
  1476 | test('深入优化保留同快照基线，刷新后继续真实计算', async ({ page, request }) => {
  1477 |   await solve(page)
  1478 |   const sceneId = await page.getByLabel('选择场景').inputValue()
  1479 |   const old = (await (await request.get(`/api/v1/scenarios/${sceneId}/plans`)).json())[0]
  1480 |   await page.getByRole('button', { name: '深入优化30秒', exact: true }).click()
  1481 |   await expect(page.locator('.job-banner')).toBeVisible()
  1482 |   await page.reload()
> 1483 |   await expect(page.locator('.job-banner')).toBeVisible()
       |                                             ^ Error: expect(locator).toBeVisible() failed
  1484 |   await expect(page.locator('.job-banner')).toBeHidden({ timeout: 45000 })
  1485 |   await expect(page.getByTestId('sortie-card').first()).toBeVisible()
  1486 |   const plans = await (await request.get(`/api/v1/scenarios/${sceneId}/plans`)).json()
  1487 |   expect(plans).toHaveLength(2)
  1488 |   expect(plans[0].snapshot_id).toBe(old.snapshot_id)
  1489 |   expect(plans[0].algorithm_mode).toBe('improve')
  1490 |   expect(plans[0].source_plan_id).toBe(old.plan_id)
  1491 |   const jobs = await (await request.get(`/api/v1/scenarios/${sceneId}/solve-jobs`)).json()
  1492 |   expect(jobs).toHaveLength(2)
  1493 |   expect(jobs.every((j: { job_state: string }) => j.job_state === 'completed')).toBe(true)
  1494 |   const current = await (await request.get(`/api/v1/plans/${plans[0].plan_id}`)).json()
  1495 |   expect(current.validation.status).toBe('passed')
  1496 |   await screenshot(page, 'deep-optimization-1440')
  1497 | })
  1498 | 
  1499 | test('限制区保存新版本，真实绕行并沿折线回放', async ({ page, request }) => {
  1500 |   const errors: string[] = []
  1501 |   page.on('pageerror', (e) => errors.push(e.message))
  1502 |   await solve(page)
  1503 |   const sceneId = await page.getByLabel('选择场景').inputValue()
  1504 |   const old = (await (await request.get(`/api/v1/scenarios/${sceneId}/plans`)).json())[0]
  1505 |   await page.getByRole('button', { name: '场景与资源', exact: true }).click()
  1506 |   await page.getByRole('button', { name: '管理限制区', exact: true }).click()
  1507 |   await expect(page.getByRole('dialog')).toBeVisible()
  1508 |   await page.getByRole('button', { name: '加入草稿', exact: true }).click()
  1509 |   await expect(page.getByLabel('限制区JSON')).toContainText('临时限制区')
  1510 |   await page.screenshot({ path: path.resolve('../evidence/browser/verified/zone-editor-1440.png') })
  1511 |   await page.getByRole('button', { name: '保存限制区', exact: true }).click()
  1512 |   await expect(page.getByRole('dialog')).toBeHidden()
  1513 |   await expect(page.locator('.zone-saved-list')).toContainText('临时限制区')
  1514 |   await page.getByRole('button', { name: '调度工作台', exact: true }).click()
  1515 |   await expect(page.getByRole('button', { name: '确认方案', exact: true })).toBeDisabled()
  1516 |   await solve(page)
  1517 |   const plans = await (await request.get(`/api/v1/scenarios/${sceneId}/plans`)).json()
  1518 |   expect(plans).toHaveLength(2)
  1519 |   expect(plans[0].snapshot_id).not.toBe(old.snapshot_id)
  1520 |   const plan = await (await request.get(`/api/v1/plans/${plans[0].plan_id}`)).json()
  1521 |   expect(plan.model_scope).toContain('restricted_zone')
  1522 |   expect(
  1523 |     plan.sorties.some(
  1524 |       (r: { visits: unknown[]; route_geometry: { coordinates: unknown[] } }) =>
  1525 |         r.route_geometry.coordinates.length > r.visits.length + 2,
  1526 |     ),
  1527 |   ).toBe(true)
  1528 |   expect(
  1529 |     plan.validation.checks.some(
  1530 |       (c: { code: string; status: string }) =>
  1531 |         c.code === 'restricted_zone' && c.status === 'passed',
  1532 |     ),
  1533 |   ).toBe(true)
  1534 |   await page.getByRole('button', { name: '检查报告', exact: true }).click()
  1535 |   await expect(page.getByRole('dialog')).toContainText('限制区与缓冲')
  1536 |   await page.getByRole('dialog').getByRole('button', { name: '关闭弹窗' }).click()
  1537 |   await screenshot(page, 'zone-detour-1440')
  1538 |   await page.getByRole('button', { name: '播放计划回放', exact: true }).click()
  1539 |   await expect(page.locator('.planned-aircraft').first()).toBeVisible()
  1540 |   await page.getByRole('button', { name: '暂停计划回放', exact: true }).click()
  1541 |   expect(errors).toEqual([])
  1542 | })
  1543 | 
  1544 | test('GeoTIFF资产上传绑定，真实Worker使用新DEM并恢复历史', async ({ page, request }) => {
  1545 |   const errors: string[] = []
  1546 |   page.on('pageerror', (e) => errors.push(e.message))
  1547 |   await solve(page)
  1548 |   const sceneId = await page.getByLabel('选择场景').inputValue()
  1549 |   const old = (await (await request.get(`/api/v1/scenarios/${sceneId}/plans`)).json())[0]
  1550 |   await page.getByRole('button', { name: '场景与资源', exact: true }).click()
  1551 |   await page.getByRole('button', { name: '管理DEM资产', exact: true }).click()
  1552 |   await page.getByLabel('垂直基准 / 数据说明').fill('contest_provided_elevation_reference')
  1553 |   await page.getByLabel('我确认高程值为米，基准声明与来源一致').check()
  1554 |   const folder = path.resolve('../references/modeling/data/terrain')
  1555 |   const filename = (await fs.readdir(folder)).find((name) => name.endsWith('.tif'))!
  1556 |   await page.getByTestId('terrain-file').setInputFiles(path.join(folder, filename))
  1557 |   await expect(page.getByLabel('DEM资产', { exact: true })).toHaveValue(/^DEM-/, { timeout: 30000 })
  1558 |   await page.getByLabel('绑定时从DEM提取基地与需求点高程').uncheck()
  1559 |   await expect(page.locator('.toast')).toHaveCount(0, { timeout: 12000 })
  1560 |   await page.screenshot({
  1561 |     path: path.resolve('../evidence/browser/verified/terrain-assets-1440.png'),
  1562 |   })
  1563 |   await page.setViewportSize({ width: 1280, height: 720 })
  1564 |   await expect(
  1565 |     page.getByRole('button', { name: '绑定DEM并保存新版本', exact: true }),
  1566 |   ).toBeInViewport({ ratio: 0.95 })
  1567 |   await page.screenshot({
  1568 |     path: path.resolve('../evidence/browser/verified/terrain-assets-1280.png'),
  1569 |   })
  1570 |   await page.setViewportSize({ width: 1440, height: 900 })
  1571 |   const download = page.waitForEvent('download')
  1572 |   await page.getByRole('link', { name: '下载完整资产包', exact: true }).click()
  1573 |   const savedPackage = await download
  1574 |   expect(savedPackage.suggestedFilename()).toMatch(/\.yuanhang-dem\.zip$/)
  1575 |   const packagePath = await savedPackage.path()
  1576 |   const receipt = page.waitForResponse(
  1577 |     (r) => r.url().endsWith('/terrain-assets/import-package') && r.request().method() === 'POST',
  1578 |   )
  1579 |   await page.getByTestId('terrain-package-file').setInputFiles(packagePath!)
  1580 |   expect((await receipt).status()).toBe(201)
  1581 |   await page.getByRole('button', { name: '绑定DEM并保存新版本', exact: true }).click()
  1582 |   await expect(page.getByRole('dialog')).toBeHidden()
  1583 |   const updated = await (await request.get(`/api/v1/scenarios/${sceneId}`)).json()
```