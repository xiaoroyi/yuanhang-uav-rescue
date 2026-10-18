# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workflow.spec.ts >> 真实双策略、地图与甘特联动、计划回放、确认导出及历史恢复
- Location: tests\workflow.spec.ts:988:1

# Error details

```
Error: expect(received).toBe(expected) // Object.is equality

Expected: 0
Received: 1

Call Log:
- Timeout 15000ms exceeded while waiting on the predicate
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
        - generic [ref=f1e77]:
          - text: 本机服务
          - generic [ref=f1e79]: 离线可用
        - button "使用教程与常见问题" [ref=f1e80] [cursor=pointer]
        - button "账户与本机档案" [ref=f1e84] [cursor=pointer]:
          - generic [ref=f1e85]: 本
          - generic [ref=f1e86]:
            - strong [ref=f1e87]: 本机调度员
            - generic [ref=f1e88]: 调度负责人 · 本机档案
    - generic [ref=f1e92]:
      - banner [ref=f1e93]:
        - generic [ref=f1e94]:
          - generic [ref=f1e95]: 救援工作空间
          - strong [ref=f1e98]: 调度工作台
        - generic [ref=f1e99]:
          - button "切换浅色主题" [ref=f1e100] [cursor=pointer]
          - button "暂停动态背景" [pressed] [ref=f1e107] [cursor=pointer]
          - button "查看模型说明" [ref=f1e111] [cursor=pointer]
          - button "打开个人档案" [ref=f1e115] [cursor=pointer]: 本
      - main [ref=f1e116]:
        - generic [ref=f1e117]:
          - generic [ref=f1e118]:
            - generic [ref=f1e123]:
              - combobox "选择场景" [ref=f1e124]:
                - option "镇龙乡 · 应急运输演练" [selected]
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
                - option "无可用机体的增配诊断 1792330961108 · 资源增配诊断"
                - option "无可用机体的增配诊断 1792330961108"
                - option "成都合成区域 CSV 救援任务 1792330950326"
                - option "镇龙乡 · 应急运输演练"
                - option "W1 browser exercise 1792330941364"
                - option "Correction exercise 1792330934505"
                - option "地图工作台验收 1792330917944"
                - option "地图工作台验收 1792330916164"
                - option "地图工作台验收 1792330910386"
                - option "地图工作台验收 1792330905347"
                - option "失败完整保留 1792330899357 · 隔离评测"
                - option "无可用机队评测 1792330899243"
                - option "同输入三偏好验收 1792330881871 · 隔离评测"
                - option "浏览器评测输入 1792330880370"
                - option "experience 无DEM输入"
                - option "experience 版本来源检查"
                - option "镇龙乡 · 应急运输演练"
                - option "在途冻结输入的方法对照 1792330822934 · 隔离评测"
                - option "在飞备用电池退出演练 1792330808078 · 在途剩余输入"
                - option "在飞备用电池退出演练 1792330808078"
                - option "在途插单与档案验收 1792330782541 · 在途剩余输入"
                - option "在途插单与档案验收 1792330782541"
                - option "无可用机体的增配诊断 1792330447139 · 资源增配诊断"
                - option "无可用机体的增配诊断 1792330447139"
                - option "同输入三偏好验收 1792330328487 · 隔离评测"
                - option "浏览器评测输入 1792330327185"
                - option "在途冻结输入的方法对照 1792330320790 · 隔离评测"
                - option "在飞备用电池退出演练 1792330305599 · 在途剩余输入"
                - option "在飞备用电池退出演练 1792330305599"
                - option "在途插单与档案验收 1792330285942 · 在途剩余输入"
                - option "在途插单与档案验收 1792330285942"
                - option "在飞备用电池退出演练 1792329697834 · 在途剩余输入"
                - option "在飞备用电池退出演练 1792329697834"
                - option "在途插单与档案验收 1792329669173 · 在途剩余输入"
                - option "在途插单与档案验收 1792329669173"
                - option "在飞备用电池退出演练 1792329587980"
                - option "在途插单与档案验收 1792329403376 · 在途剩余输入"
                - option "在途插单与档案验收 1792329403376"
                - option "成都合成区域 CSV 救援任务 1792328252623"
                - option "镇龙乡 · 应急运输演练"
                - option "在飞备用电池退出演练 1792328236670 · 在途剩余输入"
                - option "在飞备用电池退出演练 1792328236670"
                - option "在途插单与档案验收 1792328206710 · 在途剩余输入"
                - option "在途插单与档案验收 1792328206710"
                - option "地图工作台验收 1792326236521"
                - option "地图工作台验收 1792326229586"
                - option "成都合成区域 CSV 救援任务 1792326144435"
                - option "镇龙乡 · 应急运输演练"
                - option "W1 browser exercise 1792326132930"
                - option "地图工作台验收 1792326127093"
                - option "地图工作台验收 1792326118427"
                - option "地图工作台验收 1792326113085"
                - option "失败完整保留 1792326104940 · 隔离评测"
                - option "无可用机队评测 1792326104783"
                - option "同输入三偏好验收 1792326084158 · 隔离评测"
                - option "浏览器评测输入 1792326082401"
                - option "在途插单与档案验收 1792326056557 · 在途剩余输入"
                - option "在途插单与档案验收 1792326056557"
                - option "成都合成区域 CSV 救援任务 1792325888039"
                - option "镇龙乡 · 应急运输演练"
                - option "W1 browser exercise 1792325876000"
                - option "地图工作台验收 1792325868847"
                - option "地图工作台验收 1792325858214"
                - option "地图工作台验收 1792325829010"
                - option "失败完整保留 1792325820873 · 隔离评测"
                - option "无可用机队评测 1792325820714"
                - option "同输入三偏好验收 1792325801484 · 隔离评测"
                - option "浏览器评测输入 1792325800014"
                - option "在途插单与档案验收 1792325773616 · 在途剩余输入"
                - option "在途插单与档案验收 1792325773616"
                - option "成都合成区域 CSV 救援任务 1792325480691"
                - option "镇龙乡 · 应急运输演练"
                - option "失败完整保留 1792325468522 · 隔离评测"
                - option "无可用机队评测 1792325468337"
                - option "同输入三偏好验收 1792325448096 · 隔离评测"
                - option "浏览器评测输入 1792325446461"
                - option "在途插单与档案验收 1792325419629 · 在途剩余输入"
                - option "在途插单与档案验收 1792325419629"
                - option "失败完整保留 1792325223984 · 隔离评测"
                - option "无可用机队评测 1792325223799"
                - option "同输入三偏好验收 1792325202699 · 隔离评测"
                - option "浏览器评测输入 1792325200782"
                - option "失败完整保留 1792325028306 · 隔离评测"
                - option "无可用机队评测 1792325028127"
                - option "同输入三偏好验收 1792325007379 · 隔离评测"
                - option "浏览器评测输入 1792325005228"
                - option "W1 browser exercise 1792324154625"
                - option "W1 browser exercise 1792324060421"
                - option "地图工作台验收 1792324058236"
                - option "地图工作台验收 1792324049669"
                - option "地图工作台验收 1792324044044"
                - option "在途插单与档案验收 1792324015299 · 在途剩余输入"
                - option "在途插单与档案验收 1792324015299"
                - option "地图工作台验收 1792323961392"
                - option "地图工作台验收 1792323952894"
                - option "地图工作台验收 1792323947318"
                - option "在途插单与档案验收 1792323919166 · 在途剩余输入"
                - option "在途插单与档案验收 1792323919166"
                - option "地图工作台验收 1792323882713"
                - option "地图工作台验收 1792323858061"
                - option "地图工作台验收 1792323849807"
                - option "在途插单与档案验收 1792323820730 · 在途剩余输入"
                - option "在途插单与档案验收 1792323820730"
                - option "地图工作台验收 1792323684604"
                - option "地图工作台验收 1792323672625"
                - option "地图工作台验收 1792323549256"
                - option "在途插单与档案验收 1792323521201 · 在途剩余输入"
                - option "在途插单与档案验收 1792323521201"
                - option "在途插单与档案验收 1792322699262 · 在途剩余输入"
                - option "在途插单与档案验收 1792322699262"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
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
                - option "镇龙乡 · 应急运输演练"
                - option "成都合成区域 CSV 救援任务 1792320187535"
                - option "镇龙乡 · 应急运输演练"
                - option "W1 browser exercise 1792320178641"
                - option "Correction exercise 1792320168831"
                - option "experience 无DEM输入"
                - option "experience 版本来源检查"
                - option "镇龙乡 · 应急运输演练"
                - option "在途插单与档案验收 1792320095579 · 在途剩余输入"
                - option "在途插单与档案验收 1792320095579"
                - option "在途插单与档案验收 1792319666734 · 在途剩余输入"
                - option "在途插单与档案验收 1792319666734"
                - option "成都合成区域 CSV 救援任务 1792319609342"
                - option "镇龙乡 · 应急运输演练"
                - option "W1 browser exercise 1792319599900"
                - option "Correction exercise 1792319589905"
                - option "在途插单与档案验收 1792319564580 · 在途剩余输入"
                - option "在途插单与档案验收 1792319564580"
                - option "在途插单与档案验收 1792319419549 · 在途剩余输入"
                - option "在途插单与档案验收 1792319419549"
                - option "Correction exercise 1792318558129"
                - option "成都合成区域 CSV 救援任务 1792318108983"
                - option "镇龙乡 · 应急运输演练"
                - option "W1 browser exercise 1792318097041"
                - option "W1 browser exercise 1792317971099"
                - option "镇龙乡 · 应急运输演练"
                - option "成都合成区域 CSV 救援任务 1792315895244"
                - option "镇龙乡 · 应急运输演练"
                - option "成都合成区域 CSV 救援任务 1792315220682"
                - option "镇龙乡 · 应急运输演练"
                - option "成都合成区域 CSV 救援任务 1792315135502"
                - option "镇龙乡 · 应急运输演练"
                - option "成都合成区域 CSV 救援任务 1792315059786"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练 · 压力C · 能耗+20%/时长+10%/SOH×90%"
                - option "镇龙乡 · 应急运输演练 · 压力B · 能耗+10%/时长+5%/SOH×95%"
                - option "镇龙乡 · 应急运输演练 · 压力A · 原条件"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练 · 资源与余量试算"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练 · 资源与余量试算"
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
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
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
                - option "镇龙乡 · 应急运输演练"
                - option "experience 无DEM输入"
                - option "experience 版本来源检查"
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
                - option "experience 无DEM输入"
                - option "experience 版本来源检查"
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
                - option "experience 无DEM输入"
                - option "experience 版本来源检查"
                - option "镇龙乡 · 应急运输演练"
                - option "experience 无DEM输入"
                - option "experience 版本来源检查"
                - option "镇龙乡 · 应急运输演练"
                - option "experience 无DEM输入"
                - option "experience 版本来源检查"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
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
                - option "镇龙乡 · 应急运输演练 · 资源与余量试算"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练 · 资源与余量试算"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练 · 资源与余量试算"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练 · 资源与余量试算"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练 · 压力C · 能耗+20%/时长+10%/SOH×90%"
                - option "镇龙乡 · 应急运输演练 · 压力B · 能耗+10%/时长+5%/SOH×95%"
                - option "镇龙乡 · 应急运输演练 · 压力A · 原条件"
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
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练 · 压力C · 能耗+20%/时长+10%/SOH×90%"
                - option "镇龙乡 · 应急运输演练 · 压力B · 能耗+10%/时长+5%/SOH×95%"
                - option "镇龙乡 · 应急运输演练 · 压力A · 原条件"
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
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练 · 压力C · 能耗+20%/时长+10%/SOH×90%"
                - option "镇龙乡 · 应急运输演练 · 压力B · 能耗+10%/时长+5%/SOH×95%"
                - option "镇龙乡 · 应急运输演练 · 压力A · 原条件"
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
                - option "偏好取舍演练（保留硬截止）"
                - option "镇龙乡 · 应急运输演练"
                - option "偏好取舍演练（保留硬截止）"
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
                - option "镇龙乡 · 应急运输演练 · 压力C · 能耗+20%/时长+10%/SOH×90%"
                - option "镇龙乡 · 应急运输演练 · 压力B · 能耗+10%/时长+5%/SOH×95%"
                - option "镇龙乡 · 应急运输演练 · 压力A · 原条件"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练 · 资源与余量试算"
                - option "镇龙乡 · 应急运输演练"
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
                - option "镇龙乡 · 原题运输基准"
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
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练 · 压力C · 能耗+20%/时长+10%/SOH×90%"
                - option "镇龙乡 · 应急运输演练 · 压力B · 能耗+10%/时长+5%/SOH×95%"
                - option "镇龙乡 · 应急运输演练 · 压力A · 原条件"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练 · 资源与余量试算"
                - option "镇龙乡 · 应急运输演练"
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
                - option "镇龙乡 · 原题运输基准"
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
                - option "镇龙乡 · 应急运输演练 · 压力C · 能耗+20%/时长+10%/SOH×90%"
                - option "镇龙乡 · 应急运输演练 · 压力B · 能耗+10%/时长+5%/SOH×95%"
                - option "镇龙乡 · 应急运输演练 · 压力A · 原条件"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练 · 资源与余量试算"
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
                - option "镇龙乡 · 原题运输基准"
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
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练 · 压力C · 能耗+20%/时长+10%/SOH×90%"
                - option "镇龙乡 · 应急运输演练 · 压力B · 能耗+10%/时长+5%/SOH×95%"
                - option "镇龙乡 · 应急运输演练 · 压力A · 原条件"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练 · 资源与余量试算"
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
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练 · 压力C · 能耗+20%/时长+10%/SOH×90%"
                - option "镇龙乡 · 应急运输演练 · 压力B · 能耗+10%/时长+5%/SOH×95%"
                - option "镇龙乡 · 应急运输演练 · 压力A · 原条件"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练 · 资源与余量试算"
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
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练 · 压力C · 能耗+20%/时长+10%/SOH×90%"
                - option "镇龙乡 · 应急运输演练 · 压力B · 能耗+10%/时长+5%/SOH×95%"
                - option "镇龙乡 · 应急运输演练 · 压力A · 原条件"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练 · 资源与余量试算"
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
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练 · 压力C · 能耗+20%/时长+10%/SOH×90%"
                - option "镇龙乡 · 应急运输演练 · 压力B · 能耗+10%/时长+5%/SOH×95%"
                - option "镇龙乡 · 应急运输演练 · 压力A · 原条件"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练 · 资源与余量试算"
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
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练 · 压力C · 能耗+20%/时长+10%/SOH×90%"
                - option "镇龙乡 · 应急运输演练 · 压力B · 能耗+10%/时长+5%/SOH×95%"
                - option "镇龙乡 · 应急运输演练 · 压力A · 原条件"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练 · 资源与余量试算"
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
                - option "镇龙乡 · 应急运输演练 · 压力C · 能耗+20%/时长+10%/SOH×90%"
                - option "镇龙乡 · 应急运输演练 · 压力B · 能耗+10%/时长+5%/SOH×95%"
                - option "镇龙乡 · 应急运输演练 · 压力A · 原条件"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练 · 资源与余量试算"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练 · 压力C · 能耗+20%/时长+10%/SOH×90%"
                - option "镇龙乡 · 应急运输演练 · 压力B · 能耗+10%/时长+5%/SOH×95%"
                - option "镇龙乡 · 应急运输演练 · 压力A · 原条件"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练 · 资源与余量试算"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练 · 压力C · 能耗+20%/时长+10%/SOH×90%"
                - option "镇龙乡 · 应急运输演练 · 压力B · 能耗+10%/时长+5%/SOH×95%"
                - option "镇龙乡 · 应急运输演练 · 压力A · 原条件"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练 · 资源与余量试算"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练"
                - option "镇龙乡 · 应急运输演练 · 资源与余量试算"
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
              - generic [ref=f1e125]: 5 个需求点 32 箱物资 场景起点 08:00
            - generic [ref=f1e128]: 模拟演练
            - generic [ref=f1e129]: v1
          - generic [ref=f1e130]:
            - button "新建演练" [ref=f1e131] [cursor=pointer]
            - button "更多场景操作" [ref=f1e134] [cursor=pointer]
        - generic [ref=f1e139]:
          - generic [ref=f1e140]:
            - generic [ref=f1e141]: MISSION CONTROL
            - heading "每一份物资，都有清晰的下一程" [level=1] [ref=f1e142]
            - paragraph [ref=f1e143]: 从真实输入出发，统筹箱件、机体与电池，生成可核对的运输方案。
          - generic [ref=f1e144]:
            - combobox "选择历史方案" [ref=f1e145]:
              - option "能耗优先 · 快速 · v1 · 已确认" [selected]
              - option "时间优先 · 快速 · v1"
            - button "检查报告" [ref=f1e146] [cursor=pointer]
            - button "查看调度安排" [ref=f1e150] [cursor=pointer]
            - button "深入优化30秒" [ref=f1e155] [cursor=pointer]
            - button "重新求解" [ref=f1e161] [cursor=pointer]
        - generic [ref=f1e164]:
          - button "三维与高度分析" [ref=f1e165] [cursor=pointer]
          - button "卫星地图 / 导入DEM" [ref=f1e170] [cursor=pointer]
          - button "方案对比" [ref=f1e176] [cursor=pointer]
          - button "历史档案" [ref=f1e184] [cursor=pointer]
        - generic [ref=f1e189]:
          - generic [ref=f1e190]:
            - generic [ref=f1e191]: 已安排箱件
            - generic [ref=f1e196]: 32/ 32 箱
            - generic [ref=f1e197]: 完整服务 · 箱件唯一分配
          - generic [ref=f1e199]:
            - generic [ref=f1e200]: 最后交付
            - generic [ref=f1e204]: 3时05分
            - generic [ref=f1e205]: 最后返航 3时12分
          - generic [ref=f1e207]:
            - generic [ref=f1e208]: 预计总能耗
            - generic [ref=f1e211]: 18.95kWh
            - generic [ref=f1e212]: 11 架次 · 已含返航
          - generic [ref=f1e214]:
            - generic [ref=f1e215]: 最低返航电量
            - generic [ref=f1e220]: 36.6%
            - generic [ref=f1e221]: 策略下限 20.0%
        - generic "加权箱秒是每箱期望延期秒乘需求优先级的合计，不是墙钟时长。" [ref=f1e223]:
          - generic [ref=f1e224]: 硬截止已检查
          - generic [ref=f1e225]: 期望延期 8 条 · 加权箱秒 302,921
          - generic [ref=f1e226]: 直接取舍 v2 · 硬截止与完整物资保障始终必选
        - generic [ref=f1e227]:
          - generic [ref=f1e228]:
            - generic [ref=f1e229]:
              - heading "运输任务 11" [level=3] [ref=f1e230]:
                - text: 运输任务
                - generic [ref=f1e231]: "11"
              - button "编辑场景资源" [ref=f1e232] [cursor=pointer]
            - generic [ref=f1e236]:
              - button "架次" [ref=f1e237] [cursor=pointer]
              - button "需求" [ref=f1e238] [cursor=pointer]
              - button "箱件" [ref=f1e239] [cursor=pointer]
            - textbox "搜索任务" [ref=f1e244]:
              - /placeholder: 搜索编号、机体、需求点…
            - generic [ref=f1e245]:
              - button "01 U01 已规划 S001 3 箱 00:06" [ref=f1e246] [cursor=pointer]:
                - generic [ref=f1e247]:
                  - generic [ref=f1e248]: "01"
                  - strong [ref=f1e249]: U01
                  - generic [ref=f1e250]: 已规划
                - paragraph [ref=f1e251]: S001
                - generic [ref=f1e252]:
                  - generic [ref=f1e253]: 3 箱
                  - generic [ref=f1e258]: 00:06
              - button "02 U05 已规划 S006 3 箱 00:06" [ref=f1e263] [cursor=pointer]:
                - generic [ref=f1e264]:
                  - generic [ref=f1e265]: "02"
                  - strong [ref=f1e266]: U05
                  - generic [ref=f1e267]: 已规划
                - paragraph [ref=f1e268]: S006
                - generic [ref=f1e269]:
                  - generic [ref=f1e270]: 3 箱
                  - generic [ref=f1e275]: 00:06
              - button "03 U05 已规划 S007 3 箱 00:27" [ref=f1e280] [cursor=pointer]:
                - generic [ref=f1e281]:
                  - generic [ref=f1e282]: "03"
                  - strong [ref=f1e283]: U05
                  - generic [ref=f1e284]: 已规划
                - paragraph [ref=f1e285]: S007
                - generic [ref=f1e286]:
                  - generic [ref=f1e287]: 3 箱
                  - generic [ref=f1e292]: 00:27
              - button "04 U01 已规划 S010 → S011 3 箱 00:28" [ref=f1e297] [cursor=pointer]:
                - generic [ref=f1e298]:
                  - generic [ref=f1e299]: "04"
                  - strong [ref=f1e300]: U01
                  - generic [ref=f1e301]: 已规划
                - paragraph [ref=f1e302]: S010 → S011
                - generic [ref=f1e303]:
                  - generic [ref=f1e304]: 3 箱
                  - generic [ref=f1e309]: 00:28
              - button "05 U05 已规划 S011 2 箱 00:54" [ref=f1e314] [cursor=pointer]:
                - generic [ref=f1e315]:
                  - generic [ref=f1e316]: "05"
                  - strong [ref=f1e317]: U05
                  - generic [ref=f1e318]: 已规划
                - paragraph [ref=f1e319]: S011
                - generic [ref=f1e320]:
                  - generic [ref=f1e321]: 2 箱
                  - generic [ref=f1e326]: 00:54
              - button "06 U05 已规划 S001 2 箱 01:18" [ref=f1e331] [cursor=pointer]:
                - generic [ref=f1e332]:
                  - generic [ref=f1e333]: "06"
                  - strong [ref=f1e334]: U05
                  - generic [ref=f1e335]: 已规划
                - paragraph [ref=f1e336]: S001
                - generic [ref=f1e337]:
                  - generic [ref=f1e338]: 2 箱
                  - generic [ref=f1e343]: 01:18
              - button "07 U05 已规划 S001 2 箱 01:37" [ref=f1e348] [cursor=pointer]:
                - generic [ref=f1e349]:
                  - generic [ref=f1e350]: "07"
                  - strong [ref=f1e351]: U05
                  - generic [ref=f1e352]: 已规划
                - paragraph [ref=f1e353]: S001
                - generic [ref=f1e354]:
                  - generic [ref=f1e355]: 2 箱
                  - generic [ref=f1e360]: 01:37
              - button "08 U07 已规划 S001 8 箱 00:09" [ref=f1e365] [cursor=pointer]:
                - generic [ref=f1e366]:
                  - generic [ref=f1e367]: "08"
                  - strong [ref=f1e368]: U07
                  - generic [ref=f1e369]: 已规划
                - paragraph [ref=f1e370]: S001
                - generic [ref=f1e371]:
                  - generic [ref=f1e372]: 8 箱
                  - generic [ref=f1e377]: 00:09
              - button "09 U05 已规划 S006 2 箱 01:57" [ref=f1e382] [cursor=pointer]:
                - generic [ref=f1e383]:
                  - generic [ref=f1e384]: "09"
                  - strong [ref=f1e385]: U05
                  - generic [ref=f1e386]: 已规划
                - paragraph [ref=f1e387]: S006
                - generic [ref=f1e388]:
                  - generic [ref=f1e389]: 2 箱
                  - generic [ref=f1e394]: 01:57
              - button "10 U05 已规划 S007 2 箱 02:17" [ref=f1e399] [cursor=pointer]:
                - generic [ref=f1e400]:
                  - generic [ref=f1e401]: "10"
                  - strong [ref=f1e402]: U05
                  - generic [ref=f1e403]: 已规划
                - paragraph [ref=f1e404]: S007
                - generic [ref=f1e405]:
                  - generic [ref=f1e406]: 2 箱
                  - generic [ref=f1e411]: 02:17
              - button "11 U05 已规划 S006 → S010 2 箱 02:43" [ref=f1e416] [cursor=pointer]:
                - generic [ref=f1e417]:
                  - generic [ref=f1e418]: "11"
                  - strong [ref=f1e419]: U05
                  - generic [ref=f1e420]: 已规划
                - paragraph [ref=f1e421]: S006 → S010
                - generic [ref=f1e422]:
                  - generic [ref=f1e423]: 2 箱
                  - generic [ref=f1e428]: 02:43
            - generic [ref=f1e433]: 稳定ID跨视图联动
          - generic [ref=f1e435]:
            - generic [ref=f1e436]:
              - generic [ref=f1e437]:
                - generic:
                  - region "Map" [ref=f1e438]
                  - button "定位凤丹村无人机调度中心" [ref=f1e439] [cursor=pointer]:
                    - generic [ref=f1e440]: O
                    - generic [ref=f1e441]: 凤丹村无人机调度
                  - button "定位那从" [ref=f1e442] [cursor=pointer]:
                    - generic [ref=f1e443]: "1"
                  - button "定位平旺、那龙、镇龙乡" [ref=f1e444] [cursor=pointer]:
                    - generic [ref=f1e445]: "2"
                  - button "定位六昌、木路" [ref=f1e446] [cursor=pointer]:
                    - generic [ref=f1e447]: "3"
                  - button "定位佛子、那桑、银坑" [ref=f1e448] [cursor=pointer]:
                    - generic [ref=f1e449]: "4"
                  - button "定位镇龙乡" [ref=f1e450] [cursor=pointer]:
                    - generic [ref=f1e451]: "5"
                    - generic [ref=f1e452]: S010
                - generic: 1 km
              - generic:
                - generic:
                  - text: 场景地图
                  - generic: WGS84
                - generic: 题设DEM · 离线
              - group "地图底图" [ref=f1e454]:
                - button "离线地形" [pressed] [ref=f1e455] [cursor=pointer]
                - button "卫星影像 联网" [ref=f1e458] [cursor=pointer]:
                  - text: 卫星影像
                  - generic [ref=f1e465]: 联网
              - generic [ref=f1e466]:
                - button "放大地图" [ref=f1e467] [cursor=pointer]
                - button "缩小地图" [ref=f1e469] [cursor=pointer]
                - button "适配全部点位" [ref=f1e471] [cursor=pointer]
                - button "图层管理" [ref=f1e474] [cursor=pointer]
              - generic [ref=f1e479]:
                - text: "N"
                - generic [ref=f1e480]: ↑
              - generic:
                - generic: 调度中心
                - generic: 需求点
                - generic: 运输航线
              - generic [ref=f1e481]:
                - generic [ref=f1e482]:
                  - link "© OpenStreetMap contributors · ODbL" [ref=f1e483] [cursor=pointer]:
                    - /url: https://www.openstreetmap.org/copyright
                  - text: · 历史背景资料
                - text: 离线可用 · 图上路线为任务级建议
            - generic [ref=f1e484]:
              - button "播放计划回放" [ref=f1e485] [cursor=pointer]
              - generic [ref=f1e488]: 00:00:00
              - slider "计划回放时钟" [ref=f1e489]: "0"
              - generic [ref=f1e490]: 计划示意回放
              - generic [ref=f1e491]: 非执行事实
          - complementary [ref=f1e492]:
            - generic [ref=f1e493]:
              - generic [ref=f1e495]:
                - heading "策略方案" [level=3] [ref=f1e496]
                - paragraph [ref=f1e497]: 同一快照 · 相同保障要求 · 直接取舍 v2
              - generic [ref=f1e502]:
                - strong [ref=f1e508]: 时间优先
                - paragraph [ref=f1e509]: 缩短最后返航时间；期望延期作为同分时次目标
                - generic [ref=f1e510]:
                  - generic [ref=f1e511]: 2时00分
                  - generic [ref=f1e512]: 23.43 kWh
                - generic [ref=f1e513]:
                  - generic [ref=f1e514]: 运输指标 · 直接取舍 v2
                  - generic [ref=f1e515]: 期望延期 3 条 / 32 条 · 加权 119,872 箱秒
                  - code [ref=f1e516]: PLAN-D4404B64920348CB
                - button "查看此方案" [ref=f1e517] [cursor=pointer]
              - generic [ref=f1e520]:
                - strong [ref=f1e526]: 能耗优先
                - paragraph [ref=f1e530]: 降低总能耗；期望延期作为同分时次目标
                - generic [ref=f1e531]:
                  - generic [ref=f1e532]: 3时12分
                  - generic [ref=f1e533]: 18.95 kWh
                - generic [ref=f1e534]:
                  - generic [ref=f1e535]: 运输指标 · 直接取舍 v2
                  - generic [ref=f1e536]: 期望延期 8 条 / 32 条 · 加权 302,921 箱秒
                  - code [ref=f1e537]: PLAN-B7C0817FA19047DA
                - button "当前展示方案" [ref=f1e538] [cursor=pointer]
              - generic "最小化返航秒数 + 300 × 能耗(kWh)；期望延期作为同分时次目标" [ref=f1e541]:
                - generic [ref=f1e542]:
                  - strong [ref=f1e547]: 时间能耗折中
                  - generic [ref=f1e548]: 每 1 kWh 折合 300 秒
                - button "真实计算折中策略" [ref=f1e549] [cursor=pointer]
              - generic [ref=f1e552]:
                - strong [ref=f1e553]: 全部卡片使用运输口径
                - paragraph [ref=f1e554]: 硬截止、容量、SOC 与完整物资保障不可突破；期望截止是软目标，节能可能增加延期。折中权重为 300 秒/kWh，不代表服务区保障公平。
                - paragraph [ref=f1e555]: 不同目标可以得到相同结果；请先计算同快照、同规则的三个策略，再核对排程和交付分析。
                - text: 限时搜索的已验证候选，未证明全局最优；费用未配置，不显示人民币。
            - generic [ref=f1e556]:
              - generic [ref=f1e557]:
                - generic [ref=f1e558]:
                  - heading "选中架次" [level=3] [ref=f1e559]
                  - paragraph [ref=f1e560]: SRT-ec30d068be85
                - generic [ref=f1e561]: U01
              - generic [ref=f1e562]:
                - generic [ref=f1e563]:
                  - generic [ref=f1e565]: 基地准备
                  - strong [ref=f1e566]: 00:00:00
                - generic [ref=f1e567]:
                  - generic [ref=f1e569]: S001 · 3箱交接
                  - strong [ref=f1e570]: 00:16:08
                - generic [ref=f1e571]:
                  - generic [ref=f1e573]: 返回基地
                  - strong [ref=f1e574]: 00:21:50
              - generic [ref=f1e575]:
                - generic [ref=f1e576]:
                  - generic [ref=f1e577]: 使用电池
                  - strong [ref=f1e578]: BAT-A-01
                - generic [ref=f1e579]:
                  - generic [ref=f1e580]: 预计能耗
                  - strong [ref=f1e581]: 1.264 kWh
                - generic [ref=f1e582]:
                  - generic [ref=f1e583]: 返航SOC
                  - strong [ref=f1e584]: 71.9%
                - generic [ref=f1e585]:
                  - generic [ref=f1e586]: 装载箱件
                  - strong [ref=f1e587]: 3 箱
              - button "在箱件清单中追踪" [ref=f1e588] [cursor=pointer]
        - generic [ref=f1e591]:
          - generic [ref=f1e592]:
            - generic [ref=f1e593]:
              - heading "资源时间轴 RESOURCE TIMELINE" [level=3] [ref=f1e594]
              - paragraph [ref=f1e595]: 准备、执行与补能，按实体资源核对
            - generic [ref=f1e596]:
              - generic [ref=f1e597]:
                - button "机体" [ref=f1e598] [cursor=pointer]
                - button "电池" [ref=f1e601] [cursor=pointer]
              - button "展开时间轴" [ref=f1e606] [cursor=pointer]
          - generic [ref=f1e616]:
            - generic [ref=f1e617]:
              - generic [ref=f1e618]: 资源 / 型号
              - generic [ref=f1e619]:
                - generic [ref=f1e620]: 00:00
                - generic [ref=f1e621]: 00:33
                - generic [ref=f1e622]: 01:07
                - generic [ref=f1e623]: 01:41
                - generic [ref=f1e624]: 02:15
                - generic [ref=f1e625]: 02:48
                - generic [ref=f1e626]: 03:22
            - generic [ref=f1e627]:
              - generic [ref=f1e628]:
                - strong [ref=f1e630]: U01
                - generic [ref=f1e631]: A型
              - generic [ref=f1e632]:
                - button "3箱" [ref=f1e640] [cursor=pointer]
                - button "3箱" [ref=f1e643] [cursor=pointer]
            - generic [ref=f1e646]:
              - generic [ref=f1e647]:
                - strong [ref=f1e649]: U05
                - generic [ref=f1e650]: B型
              - generic [ref=f1e651]:
                - button "3箱" [ref=f1e659] [cursor=pointer]
                - button "3箱" [ref=f1e662] [cursor=pointer]
                - button "2箱" [ref=f1e665] [cursor=pointer]
                - button "2箱" [ref=f1e668] [cursor=pointer]
                - button "2箱" [ref=f1e671] [cursor=pointer]
                - button "2箱" [ref=f1e674] [cursor=pointer]
                - button "2箱" [ref=f1e677] [cursor=pointer]
                - button "2箱" [ref=f1e680] [cursor=pointer]
            - generic [ref=f1e683]:
              - generic [ref=f1e684]:
                - strong [ref=f1e686]: U07
                - generic [ref=f1e687]: C型
              - button "8箱" [ref=f1e696] [cursor=pointer]
          - generic [ref=f1e699]:
            - generic [ref=f1e700]: 准备
            - generic [ref=f1e702]: 执行架次
            - generic [ref=f1e704]: 相对场景起点 · 区间左闭右开
        - generic [ref=f1e705]:
          - generic [ref=f1e706]:
            - generic [ref=f1e710]: 独立检查已完成 · 仅在声明模型范围内可行
            - button "查看适用范围" [ref=f1e711] [cursor=pointer]
          - generic [ref=f1e712]:
            - link "任务CSV" [ref=f1e713] [cursor=pointer]:
              - /url: /api/v1/plans/PLAN-B7C0817FA19047DA/export?format=csv
            - link "GeoJSON" [ref=f1e716] [cursor=pointer]:
              - /url: /api/v1/plans/PLAN-B7C0817FA19047DA/export?format=geojson
            - link "计划JSON" [ref=f1e722] [cursor=pointer]:
              - /url: /api/v1/plans/PLAN-B7C0817FA19047DA/export?format=json
            - link "打印报告" [ref=f1e727] [cursor=pointer]:
              - /url: /api/v1/plans/PLAN-B7C0817FA19047DA/report
            - button "确认方案" [ref=f1e732] [cursor=pointer]
```

# Test source

```ts
  503 |   await page.getByLabel('要求全程连续通信，启用运输与中继联合调度').check()
  504 |   await expect(page.getByRole('dialog')).toContainText('R-COMP-06')
  505 |   await page.setViewportSize({ width: 1280, height: 720 })
  506 |   await page.screenshot({
  507 |     path: path.resolve('../evidence/browser/verified/communication-config-1280.png'),
  508 |   })
  509 |   await page.getByRole('button', { name: '保存通信配置', exact: true }).click()
  510 |   await expect(page.getByRole('dialog')).toBeHidden()
  511 |   await page.setViewportSize({ width: 1440, height: 900 })
  512 |   await page.getByRole('button', { name: '调度工作台', exact: true }).click()
  513 |   await page.getByRole('button', { name: '生成真实方案', exact: true }).click()
  514 |   await expect(page.locator('.job-banner')).toBeVisible()
  515 |   await expect(page.locator('.job-banner')).toBeHidden({ timeout: 90000 })
  516 |   const panel = page.getByRole('region', { name: '通信协同结果' })
  517 |   await expect(panel).toContainText('模型内无通信缺口')
  518 |   await expect(page.locator('.map-marker-relay').first()).toBeAttached()
  519 |   const summaries = await (await request.get(`/api/v1/scenarios/${sid}/plans`)).json()
  520 |   const plan = await (await request.get(`/api/v1/plans/${summaries[0].plan_id}`)).json()
  521 |   expect(plan.relay_sorties.length).toBeGreaterThan(0)
  522 |   expect(plan.communication_report.coverage_gap_s).toBe(0)
  523 |   expect(plan.model_scope).toContain('communication')
  524 |   await screenshot(page, 'joint-workspace-1440')
  525 |   await panel.scrollIntoViewIfNeeded()
  526 |   await panel.getByRole('button', { name: '能源组件', exact: true }).click()
  527 |   await page.screenshot({
  528 |     path: path.resolve('../evidence/browser/verified/joint-resource-windows-1440.png'),
  529 |   })
  530 |   await confirmCurrentPlan(page)
  531 |   const report = await page.context().newPage()
  532 |   await report.goto(`/api/v1/plans/${plan.plan_id}/report`)
  533 |   await expect(report.getByText('通信与中继保障', { exact: true })).toBeVisible()
  534 |   await report.pdf({
  535 |     path: path.resolve('../evidence/browser/verified/joint-report.pdf'),
  536 |     printBackground: true,
  537 |     preferCSSPageSize: true,
  538 |   })
  539 |   await report.close()
  540 |   await page.getByRole('button', { name: '事件复盘', exact: true }).click()
  541 |   await page.getByRole('button', { name: '资源分析与试算', exact: true }).click()
  542 |   await page.getByRole('button', { name: '中继能源', exact: true }).click()
  543 |   await expect(page.locator('.analysis-resource-scroll')).toContainText('R-COMP-01')
  544 |   await screenshot(page, 'joint-resource-analysis-1440')
  545 |   await page.reload()
  546 |   await expect(page.getByRole('region', { name: '通信协同结果' })).toContainText('模型内无通信缺口')
  547 |   await page.setViewportSize({ width: 1280, height: 720 })
  548 |   await screenshot(page, 'joint-workspace-1280')
  549 |   expect(errors).toEqual([])
  550 | })
  551 | 
  552 | async function confirmCurrentPlan(page: Page, expectedPlanId?: string) {
  553 |   const pending = page.waitForResponse(
  554 |     (r) => /\/plans\/[^/]+\/confirm$/.test(r.url()) && r.request().method() === 'POST',
  555 |   )
  556 |   await page.getByRole('button', { name: '确认方案', exact: true }).click()
  557 |   const response = await pending
  558 |   expect(response.status()).toBe(200)
  559 |   const confirmation = await response.json()
  560 |   expect(confirmation.confirmation_state).toBe('confirmed')
  561 |   expect(confirmation.state_version).toBe(response.request().postDataJSON().expected_state_version)
  562 |   expect(new URL(response.url()).pathname).toBe(`/api/v1/plans/${confirmation.plan_id}/confirm`)
  563 |   if (expectedPlanId) expect(confirmation.plan_id).toBe(expectedPlanId)
  564 |   await expect(page.getByRole('link', { name: '计划JSON', exact: true })).toHaveAttribute(
  565 |     'href',
  566 |     new RegExp(`/plans/${confirmation.plan_id}/export`),
  567 |   )
  568 |   // Consecutive successful confirmations can legitimately coexist for 6.5 seconds.
  569 |   await expect(page.locator('.toast').filter({ hasText: '方案已确认' }).last()).toBeVisible()
  570 | }
  571 | 
  572 | async function uncoveredMapSites(page: Page) {
  573 |   await expect(page.locator('.map-marker-dot')).toHaveCount(6)
  574 |   let nodes: { name: string; covered: boolean; outside: boolean; rect: number[] }[] = []
  575 |   await expect
  576 |     .poll(async () => {
  577 |       nodes = await page.locator('.map-marker-dot').evaluateAll((dots) => {
  578 |         const legend = document.querySelector('.map-legend')?.getBoundingClientRect()
  579 |         const canvas = document.querySelector('.maplibregl-canvas')?.getBoundingClientRect()
  580 |         if (!legend || !canvas)
  581 |           return [{ name: 'map loading', covered: true, outside: true, rect: [] }]
  582 |         return dots.map((dot) => {
  583 |           const r = dot.getBoundingClientRect()
  584 |           return {
  585 |             name: dot.parentElement?.getAttribute('aria-label') || '',
  586 |             covered: !(
  587 |               r.right <= legend.left ||
  588 |               r.left >= legend.right ||
  589 |               r.bottom <= legend.top ||
  590 |               r.top >= legend.bottom
  591 |             ),
  592 |             outside:
  593 |               r.left < canvas.left ||
  594 |               r.right > canvas.right ||
  595 |               r.top < canvas.top ||
  596 |               r.bottom > canvas.bottom,
  597 |             rect: [r.x, r.y, r.width, r.height],
  598 |           }
  599 |         })
  600 |       })
  601 |       return nodes.filter((r) => r.covered || r.outside).length
  602 |     })
> 603 |     .toBe(0)
      |      ^ Error: expect(received).toBe(expected) // Object.is equality
  604 |   return { viewport: page.viewportSize(), nodes }
  605 | }
  606 | 
  607 | async function screenshot(page: Page, name: string) {
  608 |   await expect(page.locator('.toast')).toHaveCount(0, { timeout: 12000 })
  609 |   await page.mouse.move(1100, 50)
  610 |   await page.locator('.main-content').evaluate((element) => {
  611 |     element.scrollTop = 0
  612 |   })
  613 |   await page.locator('.strategy-column').evaluateAll((elements) =>
  614 |     elements.forEach((e) => {
  615 |       e.scrollTop = 0
  616 |     }),
  617 |   )
  618 |   await page.evaluate(() => document.fonts.ready)
  619 |   await fs.mkdir(path.resolve('../evidence/browser/verified'), { recursive: true })
  620 |   await page.screenshot({ path: path.resolve(`../evidence/browser/verified/${name}.png`) })
  621 | }
  622 | 
  623 | test('中继能源组件退出精确保存状态，联合重算不引用退出组件且刷新恢复', async ({
  624 |   page,
  625 |   request,
  626 | }) => {
  627 |   test.setTimeout(180000)
  628 |   const errors: string[] = []
  629 |   page.on('pageerror', (e) => errors.push(e.message))
  630 |   const sid = await page.getByLabel('选择场景').inputValue()
  631 |   const scene = await (await request.get(`/api/v1/scenarios/${sid}`)).json()
  632 |   scene.communication = await (
  633 |     await request.get(`/api/v1/scenarios/${sid}/communication-template`)
  634 |   ).json()
  635 |   scene.policy.requires_communication = true
  636 |   expect(
  637 |     (
  638 |       await request.put(`/api/v1/scenarios/${sid}`, {
  639 |         data: { expected_state_version: 1, scenario: scene },
  640 |       })
  641 |     ).ok(),
  642 |   ).toBe(true)
  643 |   await page.reload()
  644 |   await page.getByRole('button', { name: '生成真实方案', exact: true }).click()
  645 |   await expect(page.locator('.job-banner')).toBeVisible()
  646 |   await expect(page.locator('.job-banner')).toBeHidden({ timeout: 90000 })
  647 |   const old = await (
  648 |     await request.get(
  649 |       `/api/v1/plans/${(await (await request.get(`/api/v1/scenarios/${sid}/plans`)).json())[0].plan_id}`,
  650 |     )
  651 |   ).json()
  652 |   const oldSnapshot = await (await request.get(`/api/v1/snapshots/${old.snapshot_id}`)).json()
  653 |   const failed = old.relay_sorties[0].component_id
  654 |   await confirmCurrentPlan(page)
  655 |   await page.getByRole('button', { name: '事件复盘', exact: true }).click()
  656 |   await page.getByLabel('故障事件类型').selectOption('relay_energy')
  657 |   await page.getByLabel('故障中继能源组件').selectOption(failed)
  658 |   await page.getByRole('button', { name: '记录故障并重规划', exact: true }).click()
  659 |   await expect(page.locator('.job-banner')).toBeVisible()
  660 |   await expect(page.locator('.job-banner')).toBeHidden({ timeout: 90000 })
  661 |   await expect(page.locator('.event-history')).toContainText(`中继能源组件 ${failed} 退出`)
  662 |   await expect(page.getByLabel('中继方案变化')).toContainText('联合能耗变化')
  663 |   const plan = await (
  664 |     await request.get(
  665 |       `/api/v1/plans/${(await (await request.get(`/api/v1/scenarios/${sid}/plans`)).json())[0].plan_id}`,
  666 |     )
  667 |   ).json()
  668 |   const snapshot = await (await request.get(`/api/v1/snapshots/${plan.snapshot_id}`)).json()
  669 |   const events = await (await request.get(`/api/v1/scenarios/${sid}/events`)).json()
  670 |   expect(plan.parent_plan_id).toBe(old.plan_id)
  671 |   expect(plan.scenario_state_version).toBe(3)
  672 |   expect(plan.communication_report.coverage_gap_s).toBe(0)
  673 |   expect(plan.relay_sorties.every((r: { component_id: string }) => r.component_id !== failed)).toBe(
  674 |     true,
  675 |   )
  676 |   expect(events[0].event_type).toBe('relay_energy.unavailable')
  677 |   expect(events[0].payload).toEqual({ component_id: failed })
  678 |   const expected = structuredClone(oldSnapshot.scenario)
  679 |   expected.state_version = 3
  680 |   expected.communication.relay_energy.find(
  681 |     (b: { component_id: string }) => b.component_id === failed,
  682 |   ).status = 'unavailable'
  683 |   expect(snapshot.scenario).toEqual(expected)
  684 |   expect(await (await request.get(`/api/v1/plans/${old.plan_id}`)).json()).toEqual(old)
  685 |   expect(await (await request.get(`/api/v1/snapshots/${old.snapshot_id}`)).json()).toEqual(
  686 |     oldSnapshot,
  687 |   )
  688 |   await screenshot(page, 'relay-energy-fault-1440')
  689 |   await page.setViewportSize({ width: 1280, height: 720 })
  690 |   await screenshot(page, 'relay-energy-fault-1280')
  691 |   await confirmCurrentPlan(page)
  692 |   await page.reload()
  693 |   await page.getByRole('button', { name: '事件复盘', exact: true }).click()
  694 |   await expect(page.locator('.event-history')).toContainText(`中继能源组件 ${failed} 退出`)
  695 |   await expect(page.getByRole('region', { name: '通信协同结果' })).toContainText('模型内无通信缺口')
  696 |   await page
  697 |     .getByRole('region', { name: '通信协同结果' })
  698 |     .getByRole('button', { name: '能源组件', exact: true })
  699 |     .click()
  700 |   await page.getByRole('region', { name: '通信协同结果' }).scrollIntoViewIfNeeded()
  701 |   await page.screenshot({
  702 |     path: path.resolve('../evidence/browser/verified/relay-energy-windows-1280.png'),
  703 |   })
```