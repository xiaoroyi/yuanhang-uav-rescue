# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workflow.spec.ts >> 点击真实架次追溯通信来源，窗口导出与地图联动保持原始快照
- Location: tests\workflow.spec.ts:373:1

# Error details

```
TypeError: Cannot read properties of undefined (reading 'plan_id')
```

# Page snapshot

```yaml
- generic [ref=f1e2]:
  - link "返回新版首页" [ref=f1e3] [cursor=pointer]:
    - /url: "#/home"
  - generic [ref=f1e6]:
    - complementary [ref=f1e7]:
      - link "援航 YUANHANG RESCUE" [ref=f1e8] [cursor=pointer]:
        - /url: "#"
        - generic [ref=f1e13]:
          - strong [ref=f1e14]: 援航
          - generic [ref=f1e15]: YUANHANG RESCUE
      - generic [ref=f1e16]:
        - generic [ref=f1e17]: 应
        - generic [ref=f1e18]:
          - strong [ref=f1e19]: 援航救援工作组
          - generic [ref=f1e20]: 应急协同 · 本机工作空间
      - generic [ref=f1e23]: 任务协同
      - navigation [ref=f1e24]:
        - button "数据大屏" [ref=f1e25] [cursor=pointer]
        - button "场景与资源" [ref=f1e29] [cursor=pointer]
        - button "地图与地形" [ref=f1e35] [cursor=pointer]
        - button "调度工作台" [ref=f1e42] [cursor=pointer]
        - button "调度安排" [ref=f1e47] [cursor=pointer]
        - button "方案对比" [ref=f1e53] [cursor=pointer]
        - button "事件复盘" [ref=f1e62] [cursor=pointer]
        - button "历史档案" [ref=f1e66] [cursor=pointer]
        - button "新手教程" [ref=f1e72] [cursor=pointer]
      - generic [ref=f1e76]:
        - strong [ref=f1e81]: 救援决策，从这里开始
        - paragraph [ref=f1e82]: 准备数据、读取地形、生成方案。跟着教程完成第一次调度。
        - button "打开上手指南" [ref=f1e83] [cursor=pointer]
      - generic [ref=f1e86]:
        - generic [ref=f1e87]:
          - text: 本机服务
          - generic [ref=f1e89]: 离线可用
        - button "使用教程与常见问题" [ref=f1e90] [cursor=pointer]
        - button "账户与本机档案" [ref=f1e94] [cursor=pointer]:
          - generic [ref=f1e95]: 本
          - generic [ref=f1e96]:
            - strong [ref=f1e97]: 本机调度员
            - generic [ref=f1e98]: 调度负责人 · 本机档案
    - generic [ref=f1e102]:
      - banner [ref=f1e103]:
        - generic [ref=f1e104]:
          - generic [ref=f1e105]: 救援工作空间
          - strong [ref=f1e108]: 调度工作台
        - generic [ref=f1e109]:
          - button "切换浅色主题" [ref=f1e110] [cursor=pointer]
          - button "暂停动态背景" [pressed] [ref=f1e117] [cursor=pointer]
          - generic [ref=f1e121]: 本地服务已连接
          - button "查看模型说明" [ref=f1e123] [cursor=pointer]
          - button "打开个人档案" [ref=f1e127] [cursor=pointer]: 本
      - main [ref=f1e128]:
        - generic [ref=f1e129]:
          - generic [ref=f1e130]:
            - generic [ref=f1e135]:
              - combobox "选择场景" [ref=f1e136]:
                - option "镇龙乡 · 应急运输演练" [selected]
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
              - generic [ref=f1e137]: 5 个需求点 32 箱物资 场景起点 08:00
            - generic [ref=f1e140]: 模拟演练
            - generic [ref=f1e141]: v2
          - generic [ref=f1e142]:
            - button "新建演练" [ref=f1e143] [cursor=pointer]
            - button "更多场景操作" [ref=f1e146] [cursor=pointer]
        - generic [ref=f1e151]:
          - generic [ref=f1e152]:
            - generic [ref=f1e153]: MISSION CONTROL
            - heading "每一份物资，都有清晰的下一程 LIVE WORKSPACE" [level=1] [ref=f1e154]:
              - text: 每一份物资，都有清晰的下一程
              - generic [ref=f1e155]: LIVE WORKSPACE
            - paragraph [ref=f1e156]: 从真实输入出发，统筹箱件、机体与电池，生成可核对的运输方案。
          - generic [ref=f1e157]:
            - button "检查报告" [disabled] [ref=f1e158]
            - button "生成真实方案" [ref=f1e162] [cursor=pointer]
        - generic [ref=f1e165]:
          - generic [ref=f1e166]: 当前方案 · 真实数据联动
          - button "三维与高度分析" [ref=f1e168] [cursor=pointer]
          - button "卫星地图 / 导入DEM" [ref=f1e173] [cursor=pointer]
          - button "方案对比" [ref=f1e179] [cursor=pointer]
          - button "历史档案" [ref=f1e187] [cursor=pointer]
        - status [ref=f1e192]:
          - generic [ref=f1e195]:
            - strong [ref=f1e196]: 尚未找到可行解
            - paragraph [ref=f1e197]: 当前候选与预算内未得到可验证的联合方案。当前预算和候选范围内未找到完整可行方案，可增加预算、设备或调整非关键时限。这不证明原问题不可行。
        - generic [ref=f1e198]:
          - generic [ref=f1e199]:
            - generic [ref=f1e200]: 已安排箱件
            - generic [ref=f1e205]: 待计算
            - generic [ref=f1e206]: 库存与需求分别管理
          - generic [ref=f1e208]:
            - generic [ref=f1e209]: 最后交付
            - generic [ref=f1e213]: —
            - generic [ref=f1e214]: 以整站交接完成计时
          - generic [ref=f1e216]:
            - generic [ref=f1e217]: 预计总能耗
            - generic [ref=f1e220]: —kWh
            - generic [ref=f1e221]: 题设物理模型估计
          - generic [ref=f1e223]:
            - generic [ref=f1e224]: 最低返航电量
            - generic [ref=f1e229]: —
            - generic [ref=f1e230]: 策略下限 20.0%
        - generic [ref=f1e232]:
          - generic [ref=f1e233]:
            - generic [ref=f1e234]:
              - heading "运输任务 32" [level=3] [ref=f1e235]:
                - text: 运输任务
                - generic [ref=f1e236]: "32"
              - button "编辑场景资源" [ref=f1e237] [cursor=pointer]
            - generic [ref=f1e241]:
              - button "架次" [ref=f1e242] [cursor=pointer]
              - button "需求" [ref=f1e243] [cursor=pointer]
              - button "箱件" [ref=f1e244] [cursor=pointer]
            - textbox "搜索任务" [ref=f1e249]:
              - /placeholder: 搜索编号、机体、需求点…
            - generic [ref=f1e251]:
              - heading "等待生成架次" [level=3] [ref=f1e255]
              - paragraph [ref=f1e256]: 点击生成方案，查看具体的箱件、机体和电池安排。
            - generic [ref=f1e257]: 稳定ID跨视图联动
          - generic [ref=f1e260]:
            - generic [ref=f1e261]:
              - generic:
                - region "Map" [ref=f1e262]
                - button "定位凤丹村无人机调度中心" [ref=f1e263] [cursor=pointer]:
                  - generic [ref=f1e264]: O
                  - generic [ref=f1e265]: 凤丹村无人机调度
                - button "定位那从" [ref=f1e266] [cursor=pointer]:
                  - generic [ref=f1e267]: "1"
                  - generic [ref=f1e268]: S011
                - button "定位平旺、那龙、镇龙乡" [ref=f1e269] [cursor=pointer]:
                  - generic [ref=f1e270]: "2"
                  - generic [ref=f1e271]: S001
                - button "定位六昌、木路" [ref=f1e272] [cursor=pointer]:
                  - generic [ref=f1e273]: "3"
                  - generic [ref=f1e274]: S006
                - button "定位佛子、那桑、银坑" [ref=f1e275] [cursor=pointer]:
                  - generic [ref=f1e276]: "4"
                  - generic [ref=f1e277]: S007
                - button "定位镇龙乡" [ref=f1e278] [cursor=pointer]:
                  - generic [ref=f1e279]: "5"
                  - generic [ref=f1e280]: S010
              - generic: 1 km
            - generic:
              - generic:
                - text: 场景地图
                - generic: WGS84
              - generic: 题设DEM · 离线
            - group "地图底图" [ref=f1e282]:
              - button "离线地形" [pressed] [ref=f1e283] [cursor=pointer]
              - button "卫星影像 联网" [ref=f1e286] [cursor=pointer]:
                - text: 卫星影像
                - generic [ref=f1e293]: 联网
            - generic [ref=f1e294]:
              - button "放大地图" [ref=f1e295] [cursor=pointer]
              - button "缩小地图" [ref=f1e297] [cursor=pointer]
              - button "适配全部点位" [ref=f1e299] [cursor=pointer]
              - button "图层管理" [ref=f1e302] [cursor=pointer]
            - generic [ref=f1e307]:
              - text: "N"
              - generic [ref=f1e308]: ↑
            - generic:
              - generic: 调度中心
              - generic: 需求点
              - generic: 运输航线
            - generic [ref=f1e309]:
              - generic [ref=f1e310]:
                - link "© OpenStreetMap contributors · ODbL" [ref=f1e311] [cursor=pointer]:
                  - /url: https://www.openstreetmap.org/copyright
                - text: · 历史背景资料
              - text: 离线可用 · 图上路线为任务级建议
          - complementary [ref=f1e312]:
            - generic [ref=f1e313]:
              - generic [ref=f1e315]:
                - heading "策略方案" [level=3] [ref=f1e316]
                - paragraph [ref=f1e317]: 同一快照 · 相同保障要求 · 直接取舍 v2
              - generic [ref=f1e322]:
                - strong [ref=f1e328]: 时间优先
                - paragraph [ref=f1e329]: 缩短最后返航时间；期望延期作为同分时次目标
                - button "真实计算时间策略" [ref=f1e330] [cursor=pointer]
              - generic [ref=f1e333]:
                - strong [ref=f1e339]: 能耗优先
                - paragraph [ref=f1e340]: 降低总能耗；期望延期作为同分时次目标
                - button "真实计算此策略" [ref=f1e341] [cursor=pointer]
              - generic "最小化返航秒数 + 300 × 能耗(kWh)；期望延期作为同分时次目标" [ref=f1e344]:
                - generic [ref=f1e345]:
                  - strong [ref=f1e350]: 时间能耗折中
                  - generic [ref=f1e351]: 每 1 kWh 折合 300 秒
                - button "真实计算折中策略" [ref=f1e352] [cursor=pointer]
              - generic [ref=f1e355]:
                - strong [ref=f1e356]: 全部卡片使用运输口径
                - paragraph [ref=f1e357]: 硬截止、容量、SOC 与完整物资保障不可突破；期望截止是软目标，节能可能增加延期。折中权重为 300 秒/kWh，不代表服务区保障公平。
                - paragraph [ref=f1e358]: 不同目标可以得到相同结果；请先计算同快照、同规则的三个策略，再核对排程和交付分析。
                - text: 限时搜索的已验证候选，未证明全局最优；费用未配置，不显示人民币。
        - generic [ref=f1e360]:
          - generic [ref=f1e364]: 生成真实方案后，将独立复核箱件、资源、能量与时限
          - button "查看适用范围" [ref=f1e365] [cursor=pointer]
```

# Test source

```ts
  296 |         ).ok(),
  297 |       ).toBe(true)
  298 |       await page.reload()
  299 |     }
  300 |     await page.getByRole('button', { name: '生成真实方案', exact: true }).click()
  301 |     await expect(page.locator('.job-banner')).toBeVisible()
  302 |     await expect(page.locator('.job-banner')).toBeHidden({ timeout: 90000 })
  303 |     await expect(page.getByTestId('sortie-card').first()).toBeVisible()
  304 |     const first = (await (await request.get(`/api/v1/scenarios/${sid}/plans`)).json())[0]
  305 |     const old = await (await request.get(`/api/v1/plans/${first.plan_id}`)).json()
  306 |     const oldSnapshot = await (await request.get(`/api/v1/snapshots/${old.snapshot_id}`)).json()
  307 |     const failed = old.sorties[0].battery_id
  308 |     await confirmCurrentPlan(page, old.plan_id)
  309 |     await page.getByRole('button', { name: '事件复盘', exact: true }).click()
  310 |     await page.getByLabel('故障事件类型').selectOption('battery')
  311 |     await page.getByLabel('故障运输电池').selectOption(failed)
  312 |     await page.getByRole('button', { name: '记录故障并重规划', exact: true }).click()
  313 |     await expect(page.locator('.job-banner')).toBeVisible()
  314 |     await expect(page.locator('.job-banner')).toBeHidden({ timeout: 90000 })
  315 |     await expect(page.locator('.event-history')).toContainText(`运输电池 ${failed} 退出`)
  316 |     await expect(page.locator('.comparison-cards')).toContainText('电池改派箱件')
  317 |     const summaries = await (await request.get(`/api/v1/scenarios/${sid}/plans`)).json()
  318 |     const plan = await (await request.get(`/api/v1/plans/${summaries[0].plan_id}`)).json()
  319 |     expect(plan.plan_id).not.toBe(old.plan_id)
  320 |     expect(plan.parent_plan_id).toBe(old.plan_id)
  321 |     expect(plan.scenario_state_version).toBe(old.scenario_state_version + 1)
  322 |     expect(plan.validation.status).toBe('passed')
  323 |     expect(plan.sorties.every((row: { battery_id: string }) => row.battery_id !== failed)).toBe(
  324 |       true,
  325 |     )
  326 |     expect(
  327 |       new Set(plan.sorties.flatMap((row: { cargo_ids: string[] }) => row.cargo_ids)).size,
  328 |     ).toBe(32)
  329 |     if (joint) expect(plan.communication_report.coverage_gap_s).toBe(0)
  330 |     expect(await (await request.get(`/api/v1/plans/${old.plan_id}`)).json()).toEqual(old)
  331 |     expect(await (await request.get(`/api/v1/snapshots/${old.snapshot_id}`)).json()).toEqual(
  332 |       oldSnapshot,
  333 |     )
  334 |     const events = await (await request.get(`/api/v1/scenarios/${sid}/events`)).json()
  335 |     expect(events).toHaveLength(1)
  336 |     expect(events[0].event_type).toBe('battery.unavailable')
  337 |     expect(events[0].payload).toEqual({ battery_id: failed })
  338 |     await confirmCurrentPlan(page, plan.plan_id)
  339 |     const name = joint ? 'joint-battery-fault' : 'battery-fault'
  340 |     await screenshot(page, `${name}-1440`)
  341 |     await page.reload()
  342 |     await page.getByRole('button', { name: '事件复盘', exact: true }).click()
  343 |     await expect(page.locator('.event-history')).toContainText(`运输电池 ${failed} 退出`)
  344 |     await expect(page.locator('.comparison-cards')).toContainText('电池改派箱件')
  345 |     await page.setViewportSize({ width: 1280, height: 720 })
  346 |     await screenshot(page, `${name}-1280`)
  347 |     for (const width of [1280, 390]) {
  348 |       await page.setViewportSize({ width, height: width === 390 ? 844 : 720 })
  349 |       await page.locator('.comparison-cards').scrollIntoViewIfNeeded()
  350 |       await page.screenshot({
  351 |         path: path.resolve(`../evidence/browser/verified/${name}-changes-${width}.png`),
  352 |       })
  353 |     }
  354 |     await fs.writeFile(
  355 |       path.resolve(`../evidence/solver/${joint ? 'joint-' : ''}battery-replan.json`),
  356 |       JSON.stringify(
  357 |         {
  358 |           old_snapshot: oldSnapshot,
  359 |           old_plan: old,
  360 |           event: events[0],
  361 |           snapshot: await (await request.get(`/api/v1/snapshots/${plan.snapshot_id}`)).json(),
  362 |           plan,
  363 |           page_errors: errors,
  364 |         },
  365 |         null,
  366 |         2,
  367 |       ) + '\n',
  368 |     )
  369 |     expect(errors).toEqual([])
  370 |   })
  371 | }
  372 | 
  373 | test('点击真实架次追溯通信来源，窗口导出与地图联动保持原始快照', async ({ page, request }) => {
  374 |   test.setTimeout(150000)
  375 |   const errors: string[] = []
  376 |   page.on('pageerror', (e) => errors.push(e.message))
  377 |   const sid = await page.getByLabel('选择场景').inputValue()
  378 |   const scene = await (await request.get(`/api/v1/scenarios/${sid}`)).json()
  379 |   scene.communication = await (
  380 |     await request.get(`/api/v1/scenarios/${sid}/communication-template`)
  381 |   ).json()
  382 |   scene.policy.requires_communication = true
  383 |   expect(
  384 |     (
  385 |       await request.put(`/api/v1/scenarios/${sid}`, {
  386 |         data: { expected_state_version: 1, scenario: scene },
  387 |       })
  388 |     ).ok(),
  389 |   ).toBe(true)
  390 |   await page.reload()
  391 |   await page.getByRole('button', { name: '生成真实方案', exact: true }).click()
  392 |   await expect(page.locator('.job-banner')).toBeVisible()
  393 |   await expect(page.locator('.job-banner')).toBeHidden({ timeout: 90000 })
  394 |   const plan = await (
  395 |     await request.get(
> 396 |       `/api/v1/plans/${(await (await request.get(`/api/v1/scenarios/${sid}/plans`)).json())[0].plan_id}`,
      |                                                                                                ^ TypeError: Cannot read properties of undefined (reading 'plan_id')
  397 |     )
  398 |   ).json()
  399 |   const snapshot = await (await request.get(`/api/v1/snapshots/${plan.snapshot_id}`)).json()
  400 |   const relayWindow = plan.communication_report.windows.find(
  401 |     (w: { source: string }) => w.source === 'relay',
  402 |   )
  403 |   expect(relayWindow).toBeTruthy()
  404 |   const index = plan.sorties.findIndex(
  405 |     (r: { sortie_id: string }) => r.sortie_id === relayWindow.sortie_id,
  406 |   )
  407 |   await page.getByTestId('sortie-card').nth(index).click()
  408 |   const evidence = page.getByRole('region', { name: '通信来源证据' })
  409 |   await expect(page.getByLabel('通信来源架次')).toHaveValue(relayWindow.sortie_id)
  410 |   await evidence.locator('.coverage-window-button[data-source=relay]').first().click()
  411 |   const download = page.waitForEvent('download')
  412 |   await evidence.getByRole('button', { name: '导出所选窗口', exact: true }).click()
  413 |   const exported = JSON.parse(await fs.readFile((await (await download).path())!, 'utf8'))
  414 |   expect(exported.plan_id).toBe(plan.plan_id)
  415 |   expect(exported.snapshot_id).toBe(plan.snapshot_id)
  416 |   expect(plan.communication_report.windows).toContainEqual(exported.window)
  417 |   const relay = plan.relay_sorties.find(
  418 |     (r: { relay_sortie_id: string }) => r.relay_sortie_id === exported.window.relay_sortie_id,
  419 |   )
  420 |   expect(exported.relay_sortie).toEqual(relay)
  421 |   expect(exported.gateway_at_base).toEqual(snapshot.scenario.base)
  422 |   await expect(evidence.getByLabel('通信链路来源')).toContainText(relay.drone_id)
  423 |   await expect(evidence.getByLabel('通信链路来源')).toContainText(relay.component_id)
  424 |   await expect(page.locator('.toast')).toHaveCount(0, { timeout: 12000 })
  425 |   for (const [width, height] of [
  426 |     [1440, 900],
  427 |     [1280, 720],
  428 |   ]) {
  429 |     await page.setViewportSize({ width, height })
  430 |     await evidence.scrollIntoViewIfNeeded()
  431 |     await evidence.screenshot({
  432 |       path: path.resolve(`../evidence/browser/verified/communication-source-${width}.png`),
  433 |     })
  434 |     if (width === 1280) {
  435 |       await evidence.locator('.coverage-source-detail').scrollIntoViewIfNeeded()
  436 |       await expect(evidence.locator('.coverage-source-provenance')).toBeInViewport()
  437 |       await page.screenshot({
  438 |         path: path.resolve('../evidence/browser/verified/communication-source-detail-1280.png'),
  439 |       })
  440 |     }
  441 |   }
  442 |   await page.setViewportSize({ width: 390, height: 844 })
  443 |   await evidence.scrollIntoViewIfNeeded()
  444 |   expect(
  445 |     await page.evaluate(
  446 |       () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  447 |     ),
  448 |   ).toBeLessThanOrEqual(2)
  449 |   await page.screenshot({
  450 |     path: path.resolve('../evidence/browser/verified/communication-source-mobile.png'),
  451 |   })
  452 |   await evidence.getByLabel('通信链路来源').scrollIntoViewIfNeeded()
  453 |   await page.screenshot({
  454 |     path: path.resolve('../evidence/browser/verified/communication-source-detail-mobile.png'),
  455 |   })
  456 |   await page.setViewportSize({ width: 1440, height: 900 })
  457 |   const direct = plan.sorties.find((r: { sortie_id: string }) =>
  458 |     plan.communication_report.windows
  459 |       .filter((w: { sortie_id: string }) => w.sortie_id === r.sortie_id)
  460 |       .every((w: { source: string }) => w.source === 'gateway'),
  461 |   )
  462 |   expect(direct).toBeTruthy()
  463 |   await page.getByLabel('通信来源架次').selectOption(direct.sortie_id)
  464 |   await expect(page.locator('.sortie-detail .mono')).toHaveText(direct.sortie_id)
  465 |   await expect(evidence.getByLabel('通信链路来源')).toContainText('地面直连')
  466 |   await expect(evidence.locator('.coverage-link-chain')).toHaveClass(/direct-chain/)
  467 |   const changed = structuredClone(snapshot.scenario)
  468 |   changed.communication.frequency_mhz = 5800
  469 |   expect(
  470 |     (
  471 |       await request.put(`/api/v1/scenarios/${sid}`, {
  472 |         data: { expected_state_version: 2, scenario: changed },
  473 |       })
  474 |     ).ok(),
  475 |   ).toBe(true)
  476 |   await page.reload()
  477 |   await expect(page.getByLabel('通信来源架次')).toBeVisible()
  478 |   await expect(evidence.getByLabel('通信链路来源')).toContainText('2,400 MHz')
  479 |   await expect(evidence.getByLabel('通信链路来源')).not.toContainText('5,800 MHz')
  480 |   await expect(page.getByRole('button', { name: '确认方案', exact: true })).toBeDisabled()
  481 |   expect(await (await request.get(`/api/v1/snapshots/${plan.snapshot_id}`)).json()).toEqual(
  482 |     snapshot,
  483 |   )
  484 |   expect(await (await request.get(`/api/v1/plans/${plan.plan_id}`)).json()).toEqual(plan)
  485 |   await fs.writeFile(
  486 |     path.resolve('../evidence/browser/communication-source.json'),
  487 |     JSON.stringify({ snapshot, plan, exported_window: exported, page_errors: errors }, null, 2) +
  488 |       '\n',
  489 |   )
  490 |   expect(errors).toEqual([])
  491 | })
  492 | 
  493 | test('连续通信联合调度、真实中继地图与资源窗口、确认及报告', async ({ page, request }) => {
  494 |   test.setTimeout(120000)
  495 |   const errors: string[] = []
  496 |   page.on('pageerror', (e) => errors.push(e.message))
```