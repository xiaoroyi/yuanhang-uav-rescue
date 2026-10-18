# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workflow.spec.ts >> 任务刷新恢复，重新载入页面不重复提交求解
- Location: tests\workflow.spec.ts:1381:1

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByTestId('sortie-card').first()
Expected: visible
Timeout: 45000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" getByTestId('sortie-card').first() with timeout 45000ms
  - waiting for getByTestId('sortie-card').first()

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
  - text: 5 个需求点 32 箱物资 场景起点 08:00 模拟演练 v1
  - button "新建演练"
  - button "更多场景操作"
  - text: MISSION CONTROL
  - heading "每一份物资，都有清晰的下一程 LIVE WORKSPACE" [level=1]
  - paragraph: 从真实输入出发，统筹箱件、机体与电池，生成可核对的运输方案。
  - button "检查报告" [disabled]
  - button "生成真实方案"
  - text: 当前方案 · 真实数据联动
  - button "三维与高度分析"
  - button "卫星地图 / 导入DEM"
  - button "方案对比"
  - button "历史档案"
  - text: 已安排箱件 待计算 库存与需求分别管理 最后交付 — 以整站交接完成计时 预计总能耗 —kWh 题设物理模型估计 最低返航电量 — 策略下限 20.0%
  - heading "运输任务 32" [level=3]
  - button "编辑场景资源"
  - button "架次"
  - button "需求"
  - button "箱件"
  - textbox "搜索任务":
    - /placeholder: 搜索编号、机体、需求点…
  - heading "等待生成架次" [level=3]
  - paragraph: 点击生成方案，查看具体的箱件、机体和电池安排。
  - text: 稳定ID跨视图联动
  - region "Map"
  - button "定位凤丹村无人机调度中心": O 凤丹村无人机调度
  - button "定位那从": 1 S011
  - button "定位平旺、那龙、镇龙乡": 2 S001
  - button "定位六昌、木路": 3 S006
  - button "定位佛子、那桑、银坑": 4 S007
  - button "定位镇龙乡": 5 S010
  - text: 1 km 场景地图 WGS84 题设DEM · 离线
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
  - complementary:
    - heading "策略方案" [level=3]
    - paragraph: 同一快照 · 相同保障要求 · 直接取舍 v2
    - strong: 时间优先
    - paragraph: 缩短最后返航时间；期望延期作为同分时次目标
    - button "真实计算时间策略"
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
  - text: 生成真实方案后，将独立复核箱件、资源、能量与时限
  - button "查看适用范围"
```

# Test source

```ts
  1286 |   await expect(page.locator('.toast')).toHaveCount(0, { timeout: 12000 })
  1287 |   for (const [width, height] of [
  1288 |     [1440, 900],
  1289 |     [1280, 720],
  1290 |     [390, 844],
  1291 |   ]) {
  1292 |     await page.setViewportSize({ width, height })
  1293 |     await page.locator('.what-if-panel').screenshot({
  1294 |       path: path.resolve(`../evidence/browser/verified/ground-trial-form-${width}.png`),
  1295 |       animations: 'disabled',
  1296 |     })
  1297 |     const submit = page.getByRole('button', { name: '创建场景并真实试算', exact: true })
  1298 |     await submit.scrollIntoViewIfNeeded()
  1299 |     await expect(submit).toBeInViewport()
  1300 |     if (width === 1280)
  1301 |       await page.screenshot({
  1302 |         path: path.resolve('../evidence/browser/verified/ground-trial-form-footer-1280.png'),
  1303 |         animations: 'disabled',
  1304 |       })
  1305 |   }
  1306 |   await page.setViewportSize({ width: 1280, height: 720 })
  1307 |   await page
  1308 |     .locator('.trial-result')
  1309 |     .screenshot({ path: path.resolve('../evidence/browser/verified/ground-trial-result-1280.png') })
  1310 |   await page.setViewportSize({ width: 1440, height: 900 })
  1311 |   await page.reload()
  1312 |   await page.getByRole('button', { name: '事件复盘', exact: true }).click()
  1313 |   await page.getByRole('button', { name: '资源分析与试算', exact: true }).click()
  1314 |   const row = page.getByTestId('experiment-row')
  1315 |   await expect(row).toHaveCount(1)
  1316 |   await row.getByRole('button', { name: '打开场景', exact: true }).click()
  1317 |   await expect(page.getByLabel('选择场景')).toHaveValue(receipt.scenario.scenario_id)
  1318 |   await expect(page.getByTestId('sortie-card').first()).toBeVisible()
  1319 |   expect(errors).toEqual([])
  1320 |   await fs.writeFile(
  1321 |     path.resolve('../evidence/browser/ground-capacity-trial.json'),
  1322 |     JSON.stringify(
  1323 |       { sourceSnapshot, baseline, receipt, snapshot, plan, analysis, page_errors: errors },
  1324 |       null,
  1325 |       2,
  1326 |     ) + '\n',
  1327 |   )
  1328 | })
  1329 | 
  1330 | test('三档压力测试分别真实计算，刷新后保留各情景历史', async ({ page, request }) => {
  1331 |   await solve(page)
  1332 |   const sourceId = await page.getByLabel('选择场景').inputValue()
  1333 |   const before = await (await request.get('/api/v1/scenarios/' + sourceId)).json()
  1334 |   await page.getByRole('button', { name: '事件复盘', exact: true }).click()
  1335 |   await page.getByRole('button', { name: '资源分析与试算', exact: true }).click()
  1336 |   await page.getByRole('button', { name: '运行3档压力测试', exact: true }).click()
  1337 |   await expect(page.getByTestId('experiment-row')).toHaveCount(3, { timeout: 30000 })
  1338 |   await expect
  1339 |     .poll(
  1340 |       async () => {
  1341 |         const rows = await (await request.get(`/api/v1/scenarios/${sourceId}/what-if`)).json()
  1342 |         return (
  1343 |           rows.length === 3 &&
  1344 |           rows.every(
  1345 |             (r: { job: { job_state: string } | null }) =>
  1346 |               r.job && ['completed', 'failed', 'canceled'].includes(r.job.job_state),
  1347 |           )
  1348 |         )
  1349 |       },
  1350 |       { timeout: 45000 },
  1351 |     )
  1352 |     .toBe(true)
  1353 |   const history = await (await request.get(`/api/v1/scenarios/${sourceId}/what-if`)).json()
  1354 |   expect(new Set(history.map((r: { scenario_id: string }) => r.scenario_id)).size).toBe(3)
  1355 |   expect(
  1356 |     history
  1357 |       .map(
  1358 |         (r: { origin: { parameters: { energy_multiplier: number } } }) =>
  1359 |           r.origin.parameters.energy_multiplier,
  1360 |       )
  1361 |       .sort(),
  1362 |   ).toEqual([1, 1.1, 1.2])
  1363 |   expect(
  1364 |     history.every(
  1365 |       (r: { job: { job_state: string }; plan: { data_origin: string } | null }) =>
  1366 |         r.job.job_state === 'completed' && (!r.plan || r.plan.data_origin === 'solver'),
  1367 |     ),
  1368 |   ).toBe(true)
  1369 |   expect(await (await request.get('/api/v1/scenarios/' + sourceId)).json()).toEqual(before)
  1370 |   await page.locator('.experiment-history').scrollIntoViewIfNeeded()
  1371 |   await expect(page.locator('.toast')).toHaveCount(0, { timeout: 12000 })
  1372 |   await page.screenshot({
  1373 |     path: path.resolve('../evidence/browser/verified/stress-history-1440.png'),
  1374 |   })
  1375 |   await page.reload()
  1376 |   await page.getByRole('button', { name: '事件复盘', exact: true }).click()
  1377 |   await page.getByRole('button', { name: '资源分析与试算', exact: true }).click()
  1378 |   await expect(page.getByTestId('experiment-row')).toHaveCount(3)
  1379 | })
  1380 | 
  1381 | test('任务刷新恢复，重新载入页面不重复提交求解', async ({ page, request }) => {
  1382 |   const sceneId = await page.getByLabel('选择场景').inputValue()
  1383 |   await page.getByRole('button', { name: '生成真实方案', exact: true }).click()
  1384 |   await expect(page.locator('.job-banner')).toBeVisible()
  1385 |   await page.reload()
> 1386 |   await expect(page.getByTestId('sortie-card').first()).toBeVisible({ timeout: 45000 })
       |                                                         ^ Error: expect(locator).toBeVisible() failed
  1387 |   const jobs = await (await request.get(`/api/v1/scenarios/${sceneId}/solve-jobs`)).json()
  1388 |   expect(jobs.length).toBe(1)
  1389 |   expect(jobs[0].job_state).toBe('completed')
  1390 |   expect(jobs[0].has_validated_plan).toBe(true)
  1391 |   const storedPlan = await (await request.get(`/api/v1/plans/${jobs[0].plan_id}`)).json()
  1392 |   const storedSnapshot = await (
  1393 |     await request.get(`/api/v1/snapshots/${storedPlan.snapshot_id}`)
  1394 |   ).json()
  1395 |   expect(storedPlan.validation.status).toBe('passed')
  1396 |   expect(storedPlan.snapshot_id).toBe(jobs[0].snapshot_id)
  1397 | 
  1398 |   // A plans read can precede the worker commit while job metadata follows it.
  1399 |   // A persisted selection can load its real Plan directly despite that stale list.
  1400 |   // Assert the displayed identity and immutable input, not redundant list reads.
  1401 |   let planReads = 0
  1402 |   await page.route(`**/api/v1/scenarios/${sceneId}/plans`, async (route) => {
  1403 |     planReads++
  1404 |     if (planReads === 1) await route.fulfill({ json: [] })
  1405 |     else await route.continue()
  1406 |   })
  1407 |   await page.route(`**/api/v1/scenarios/${sceneId}/solve-jobs`, async (route) => {
  1408 |     await new Promise((resolve) => setTimeout(resolve, 250))
  1409 |     await route.continue()
  1410 |   })
  1411 |   const submittedJobs: string[] = []
  1412 |   page.on('request', (r) => {
  1413 |     if (r.method() === 'POST' && new URL(r.url()).pathname === '/api/v1/solve-jobs')
  1414 |       submittedJobs.push(r.url())
  1415 |   })
  1416 |   const staleListResponse = page.waitForResponse(
  1417 |     (r) => new URL(r.url()).pathname === `/api/v1/scenarios/${sceneId}/plans`,
  1418 |   )
  1419 |   const restoredPlanResponse = page.waitForResponse(
  1420 |     (r) => new URL(r.url()).pathname === `/api/v1/plans/${storedPlan.plan_id}`,
  1421 |   )
  1422 |   const restoredSnapshotResponse = page.waitForResponse(
  1423 |     (r) => new URL(r.url()).pathname === `/api/v1/snapshots/${storedPlan.snapshot_id}`,
  1424 |   )
  1425 |   await page.reload()
  1426 |   await expect(page.getByTestId('sortie-card').first()).toBeVisible()
  1427 |   expect(await (await staleListResponse).json()).toEqual([])
  1428 |   expect(await (await restoredPlanResponse).json()).toEqual(storedPlan)
  1429 |   expect(await (await restoredSnapshotResponse).json()).toEqual(storedSnapshot)
  1430 |   await expect(page.getByRole('link', { name: '计划JSON', exact: true })).toHaveAttribute(
  1431 |     'href',
  1432 |     new RegExp(`/plans/${storedPlan.plan_id}/export`),
  1433 |   )
  1434 |   await expect(page.getByRole('status', { name: '方案快照绑定', exact: true })).toHaveCount(0)
  1435 |   await expect(page.locator('.toast').filter({ hasText: '真实计算完成' })).toHaveCount(0)
  1436 |   const recovered = await (await request.get(`/api/v1/scenarios/${sceneId}/solve-jobs`)).json()
  1437 |   expect(recovered).toHaveLength(1)
  1438 |   expect(recovered[0].job_id).toBe(jobs[0].job_id)
  1439 |   expect(recovered[0].plan_id).toBe(storedPlan.plan_id)
  1440 |   expect(recovered[0].snapshot_id).toBe(storedSnapshot.snapshot_id)
  1441 |   expect(submittedJobs).toEqual([])
  1442 | })
  1443 | 
  1444 | test('打印报告包含真实任务并可离线保存PDF', async ({ page }) => {
  1445 |   await solve(page)
  1446 |   const popup = page.waitForEvent('popup')
  1447 |   await page.getByRole('link', { name: '打印报告', exact: true }).click()
  1448 |   const report = await popup
  1449 |   await expect(report.getByRole('heading', { level: 1 })).toHaveText('援航 · 运输调度与资源报告')
  1450 |   await expect(report.locator('table')).toHaveCount(4)
  1451 |   await expect(report.locator('body')).toContainText('逐箱物资追踪')
  1452 |   await expect(report.locator('.identity')).toContainText('输入Hash')
  1453 |   await report.screenshot({
  1454 |     path: path.resolve('../evidence/browser/verified/print-report-screen.png'),
  1455 |   })
  1456 |   await report.pdf({
  1457 |     path: path.resolve('../evidence/browser/verified/print-report.pdf'),
  1458 |     format: 'A4',
  1459 |     landscape: true,
  1460 |     printBackground: true,
  1461 |     preferCSSPageSize: true,
  1462 |   })
  1463 |   await report.close()
  1464 | })
  1465 | 
  1466 | test('深入优化保留同快照基线，刷新后继续真实计算', async ({ page, request }) => {
  1467 |   await solve(page)
  1468 |   const sceneId = await page.getByLabel('选择场景').inputValue()
  1469 |   const old = (await (await request.get(`/api/v1/scenarios/${sceneId}/plans`)).json())[0]
  1470 |   await page.getByRole('button', { name: '深入优化30秒', exact: true }).click()
  1471 |   await expect(page.locator('.job-banner')).toBeVisible()
  1472 |   await page.reload()
  1473 |   await expect(page.locator('.job-banner')).toBeVisible()
  1474 |   await expect(page.locator('.job-banner')).toBeHidden({ timeout: 45000 })
  1475 |   await expect(page.getByTestId('sortie-card').first()).toBeVisible()
  1476 |   const plans = await (await request.get(`/api/v1/scenarios/${sceneId}/plans`)).json()
  1477 |   expect(plans).toHaveLength(2)
  1478 |   expect(plans[0].snapshot_id).toBe(old.snapshot_id)
  1479 |   expect(plans[0].algorithm_mode).toBe('improve')
  1480 |   expect(plans[0].source_plan_id).toBe(old.plan_id)
  1481 |   const jobs = await (await request.get(`/api/v1/scenarios/${sceneId}/solve-jobs`)).json()
  1482 |   expect(jobs).toHaveLength(2)
  1483 |   expect(jobs.every((j: { job_state: string }) => j.job_state === 'completed')).toBe(true)
  1484 |   const current = await (await request.get(`/api/v1/plans/${plans[0].plan_id}`)).json()
  1485 |   expect(current.validation.status).toBe('passed')
  1486 |   await screenshot(page, 'deep-optimization-1440')
```