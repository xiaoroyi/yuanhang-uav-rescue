# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workflow.spec.ts >> 紧急需求插入新增真实箱件，全量重算与历史保留，无法满足新截止时不发布旧方案
- Location: tests\workflow.spec.ts:116:1

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByTestId('sortie-card').first()
Expected: visible
Timeout: 15000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" getByTestId('sortie-card').first() with timeout 15000ms
  - waiting for getByTestId('sortie-card').first()

```

```yaml
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
  - status:
    - strong: 尚未找到可行解
    - paragraph: 当前预算和候选范围内未找到完整可行方案，可增加预算、设备或调整非关键时限。
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
  - button "定位凤丹村无人机调度中心": O 临时调度中心
  - button "定位那从": 1 那从
  - button "定位平旺、那龙、镇龙乡": 2 平旺、那龙、镇龙乡
  - button "定位六昌、木路": 3 六昌、木路
  - button "定位佛子、那桑、银坑": 4 佛子、那桑、银坑
  - button "定位镇龙乡": 5 镇龙乡
  - text: 竹瓦 佛子 平旺 1 km 场景地图 WGS84 题设DEM · 离线
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
    - paragraph: 同一快照 · 相同保障要求
    - strong: 时间优先
    - paragraph: 先减加权期望延期，再缩短完成时间
    - button "真实计算时间策略"
    - strong: 能耗优先
    - paragraph: 先减加权期望延期，再降低能源消耗
    - button "真实计算此策略"
    - strong: 均衡偏好
    - text: 同样先减期望延期
    - button "真实计算均衡策略"
    - paragraph: 费用未配置，不显示人民币。共同延期目标优先，三种偏好可能得到相同方案。
  - text: 生成真实方案后，将独立复核箱件、资源、能量与时限
  - button "查看适用范围"
- text: 当前预算和候选范围内未找到完整可行方案，可增加预算、设备或调整非关键时限。
- button "关闭通知"
```

# Test source

```ts
  1   | import { test, expect, type Page } from '@playwright/test'
  2   | import fs from 'node:fs/promises'
  3   | import path from 'node:path'
  4   | 
  5   | async function solve(page: Page) {
  6   |   await page.getByRole('button', { name: /^(生成真实方案|重新求解)$/ }).click()
  7   |   await expect(page.locator('.job-banner')).toBeVisible()
  8   |   await expect(page.locator('.job-banner')).toBeHidden({ timeout: 45000 })
> 9   |   await expect(page.getByTestId('sortie-card').first()).toBeVisible()
      |                                                         ^ Error: expect(locator).toBeVisible() failed
  10  | }
  11  | 
  12  | test('单点诊断按快照重算32箱与80箱，余量敏感性和导出不修改场景', async ({ page, request }) => {
  13  |   // Several real analyses and four viewport captures; keep individual assertions bounded.
  14  |   test.setTimeout(180000)
  15  |   const errors: string[] = []
  16  |   const snapshots: string[] = []
  17  |   page.on('pageerror', (e) => errors.push(e.message))
  18  |   page.on('response', (response) => {
  19  |     if (
  20  |       response.request().method() === 'POST' &&
  21  |       /\/scenarios\/[^/]+\/snapshots$/.test(response.url())
  22  |     )
  23  |       snapshots.push(response.url())
  24  |   })
  25  |   await page.getByRole('button', { name: '场景与资源', exact: true }).click()
  26  |   await screenshot(page, 'scenario-with-nominal-1440')
  27  |   await page.getByRole('button', { name: '单点运输诊断', exact: true }).click()
  28  |   const dialog = page.getByRole('dialog')
  29  |   await expect(page.getByTestId('nominal-sortie-count')).toHaveText('6架次')
  30  |   await expect(dialog).toContainText('完整需求 32 箱')
  31  |   await dialog.getByRole('button', { name: '关闭弹窗', exact: true }).click()
  32  |   await page.getByRole('button', { name: '更多场景操作', exact: true }).click()
  33  |   await page.getByRole('button', { name: '加载原题80箱场景', exact: true }).click()
  34  |   await expect(page.locator('.scene-bar')).toContainText('80 箱物资')
  35  |   const sid = await page.getByLabel('选择场景').inputValue()
  36  |   const original = await (await request.get(`/api/v1/scenarios/${sid}`)).json()
  37  |   await page.getByRole('button', { name: '单点运输诊断', exact: true }).click()
  38  |   await expect(page.getByTestId('nominal-sortie-count')).toHaveText('18架次')
  39  |   await expect(dialog.getByRole('table', { name: '单点安全载重' }).locator('tbody tr')).toHaveCount(
  40  |     45,
  41  |   )
  42  |   await expect(page.locator('.toast')).toHaveCount(0, { timeout: 12000 })
  43  |   await dialog.screenshot({
  44  |     animations: 'disabled',
  45  |     path: path.resolve('../evidence/browser/verified/nominal-capacity-1440.png'),
  46  |   })
  47  |   await page.getByLabel('诊断需求点').selectOption('S006')
  48  |   await expect(dialog.getByRole('table', { name: '单点安全载重' }).locator('tbody tr')).toHaveCount(
  49  |     3,
  50  |   )
  51  |   await dialog.getByRole('button', { name: '整箱组批', exact: true }).click()
  52  |   await page.getByLabel('诊断需求点').selectOption('all')
  53  |   await expect(dialog.getByRole('table', { name: '单点整箱组批' }).locator('tbody tr')).toHaveCount(
  54  |     18,
  55  |   )
  56  |   await dialog.screenshot({
  57  |     animations: 'disabled',
  58  |     path: path.resolve('../evidence/browser/verified/nominal-batches-1440.png'),
  59  |   })
  60  |   await page.getByLabel('诊断返航余量').selectOption('0.3')
  61  |   await expect(page.getByTestId('nominal-sortie-count')).toHaveText('20架次')
  62  |   await dialog.getByRole('button', { name: '敏感性与核查', exact: true }).click()
  63  |   await expect(dialog.getByRole('table', { name: '返航余量敏感性' })).toContainText('30.0%')
  64  |   await expect(dialog.locator('.nominal-checks span')).toHaveCount(6)
  65  |   const download = page.waitForEvent('download')
  66  |   await dialog.getByRole('button', { name: '导出诊断', exact: true }).click()
  67  |   const file = await download
  68  |   const exported = JSON.parse(await fs.readFile((await file.path())!, 'utf8'))
  69  |   expect(exported.status).toBe('complete')
  70  |   expect(exported.metrics.sortie_count).toBe(20)
  71  |   expect(exported.parameters.min_return_soc).toBe(0.3)
  72  |   expect(new Set(exported.batches.flatMap((b: { cargo_ids: string[] }) => b.cargo_ids)).size).toBe(
  73  |     80,
  74  |   )
  75  |   expect(
  76  |     exported.batches.every(
  77  |       (b: Record<string, unknown>) => !('drone_id' in b) && !('battery_id' in b),
  78  |     ),
  79  |   ).toBe(true)
  80  |   await page.getByLabel('诊断返航余量').selectOption('0.4')
  81  |   await expect(page.getByTestId('nominal-sortie-count')).toHaveText('—架次')
  82  |   await expect(dialog.getByText(/部分站点不满足当前有限组批模型条件/)).toBeVisible()
  83  |   await page.getByLabel('诊断返航余量').selectOption('0.3')
  84  |   await expect(page.getByTestId('nominal-sortie-count')).toHaveText('20架次')
  85  |   for (const [width, height] of [
  86  |     [1280, 720],
  87  |     [390, 844],
  88  |   ]) {
  89  |     await page.setViewportSize({ width, height })
  90  |     await dialog.getByRole('table', { name: '返航余量敏感性' }).scrollIntoViewIfNeeded()
  91  |     await expect(dialog.locator('.nominal-footer')).toBeInViewport()
  92  |     await dialog.screenshot({
  93  |       animations: 'disabled',
  94  |       path: path.resolve(`../evidence/browser/verified/nominal-sensitivity-${width}.png`),
  95  |     })
  96  |   }
  97  |   expect(await (await request.get(`/api/v1/scenarios/${sid}`)).json()).toEqual(original)
  98  |   expect(await (await request.get(`/api/v1/scenarios/${sid}/plans`)).json()).toEqual([])
  99  |   expect(snapshots).toHaveLength(2)
  100 |   await fs.writeFile(
  101 |     path.resolve('../evidence/browser/nominal-diagnostic.json'),
  102 |     JSON.stringify(
  103 |       {
  104 |         scenario_id: sid,
  105 |         report: exported,
  106 |         snapshot_requests: snapshots.length,
  107 |         page_errors: errors,
  108 |       },
  109 |       null,
```