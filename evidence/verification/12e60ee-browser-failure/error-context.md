# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workflow.spec.ts >> 运输场景运输电池退出，真实改派、确认和历史恢复
- Location: tests\workflow.spec.ts:278:3

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('.toast').filter({ hasText: '方案已确认' })
Expected: visible
Error: strict mode violation: locator('.toast').filter({ hasText: '方案已确认' }) resolved to 2 elements:
    1) <div class="toast toast-success">…</div> aka locator('div').filter({ hasText: '方案已确认并原子预约资源。此操作不会下发飞控指令。' }).nth(3)
    2) <div class="toast toast-success">…</div> aka locator('div').filter({ hasText: '方案已确认并原子预约资源。此操作不会下发飞控指令。' }).nth(4)

Call log:
  - Expect "toBeVisible" locator('.toast').filter({ hasText: '方案已确认' }) with timeout 15000ms
  - waiting for locator('.toast').filter({ hasText: '方案已确认' })

```

# Page snapshot

```yaml
- generic [ref=e3]:
  - complementary [ref=e4]:
    - link "援航 YUANHANG RESCUE" [ref=e5] [cursor=pointer]:
      - /url: "#"
      - generic [ref=e10]:
        - strong [ref=e11]: 援航
        - generic [ref=e12]: YUANHANG RESCUE
    - generic [ref=e13]:
      - generic [ref=e14]: 应
      - generic [ref=e15]:
        - strong [ref=e16]: 应急救援工作空间
        - generic [ref=e17]: 本地演练环境
    - generic [ref=e20]: 任务协同
    - navigation [ref=e21]:
      - button "场景与资源" [ref=e22] [cursor=pointer]
      - button "调度工作台" [ref=e28] [cursor=pointer]
      - button "事件复盘" [ref=e32] [cursor=pointer]
    - generic [ref=e37]:
      - strong [ref=e42]: 有依据的调度
      - paragraph [ref=e43]: 每一箱、每一架次、每一块电池，都可以追溯。
      - button "了解模型与验证范围" [ref=e44] [cursor=pointer]
    - generic [ref=e47]:
      - generic [ref=e48]:
        - text: 本机服务
        - generic [ref=e50]: 离线可用
      - button "使用说明与模型边界" [ref=e51] [cursor=pointer]
      - generic [ref=e55]:
        - generic [ref=e56]: A
        - generic [ref=e57]:
          - strong [ref=e58]: 调度负责人
          - generic [ref=e59]: 模拟 / 规划辅助
  - generic [ref=e63]:
    - banner [ref=e64]:
      - generic [ref=e65]:
        - generic [ref=e66]: 救援工作空间
        - strong [ref=e69]: 事件复盘
      - generic [ref=e70]:
        - generic [ref=e71]: 本地服务已连接
        - button "查看模型说明" [ref=e73] [cursor=pointer]
        - generic [ref=e77]: A
    - main [ref=e78]:
      - generic [ref=e79]:
        - generic [ref=e80]:
          - generic [ref=e85]:
            - combobox "选择场景" [ref=e86]:
              - option "镇龙乡 · 应急运输演练" [selected]
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
            - generic [ref=e87]: 5 个需求点 32 箱物资 场景起点 08:00
          - generic [ref=e90]: 模拟演练
          - generic [ref=e91]: v2
        - generic [ref=e92]:
          - button "新建演练" [ref=e93] [cursor=pointer]
          - button "更多场景操作" [ref=e96] [cursor=pointer]
      - generic [ref=e101]:
        - generic [ref=e102]:
          - generic [ref=e103]: EVENTS & REPLANNING
          - heading "面对变化，让救援继续前行 EVENT REVIEW" [level=1] [ref=e104]:
            - text: 面对变化，让救援继续前行
            - generic [ref=e105]: EVENT REVIEW
          - paragraph [ref=e106]: 保留原计划与事件事实，在新快照上重新计算未来任务。
        - generic [ref=e107]:
          - combobox "选择历史方案" [ref=e108]:
            - option "时间优先 · 重规划 · v2 · 已确认" [selected]
            - option "时间优先 · 快速 · v1 · 已确认"
          - button "检查报告" [ref=e109] [cursor=pointer]
      - generic "复盘工作模式" [ref=e113]:
        - button "动态事件" [ref=e114] [cursor=pointer]
        - button "资源分析与试算" [ref=e117] [cursor=pointer]
        - button "冻结任务分区" [ref=e122] [cursor=pointer]
      - generic [ref=e127]:
        - generic [ref=e128]:
          - generic [ref=e129]: 已安排箱件
          - generic [ref=e134]: 32/ 32 箱
          - generic [ref=e135]: 完整服务 · 箱件唯一分配
        - generic [ref=e137]:
          - generic [ref=e138]: 最后交付
          - generic [ref=e142]: 2时06分
          - generic [ref=e143]: 最后返航 2时11分
        - generic [ref=e145]:
          - generic [ref=e146]: 预计总能耗
          - generic [ref=e149]: 26.24kWh
          - generic [ref=e150]: 10 架次 · 已含返航
        - generic [ref=e152]:
          - generic [ref=e153]: 最低返航电量
          - generic [ref=e158]: 24.5%
          - generic [ref=e159]: 策略下限 20.0%
      - generic [ref=e161]:
        - complementary [ref=e162]:
          - generic [ref=e164]:
            - heading "事件注入" [level=3] [ref=e165]
            - paragraph [ref=e166]: 仅作用于尚未执行的模拟场景
          - generic [ref=e169]:
            - generic [ref=e170]:
              - generic [ref=e171]: 事件类型
              - combobox "故障事件类型" [ref=e172]:
                - option "未起飞机体退出"
                - option "运输电池退出" [selected]
                - option "紧急需求插入"
            - generic [ref=e173]:
              - generic [ref=e174]: 受影响运输电池
              - combobox "故障运输电池" [ref=e175]:
                - option "请选择可退出电池" [selected]
                - option "BAT-A-01 · A型 · 100.0%"
                - option "BAT-A-02 · A型 · 100.0%"
                - option "BAT-B-01 · B型 · 100.0%"
                - option "BAT-B-02 · B型 · 100.0%"
                - option "BAT-C-02 · C型 · 100.0%"
            - generic [ref=e176]: 仅支持尚未执行场景。事件保存新版本并保留原计划，只改变指定资源的可用状态。
            - button "记录故障并重规划" [disabled] [ref=e179]
          - generic [ref=e185]:
            - heading "事件时间线 1" [level=4] [ref=e186]:
              - text: 事件时间线
              - generic [ref=e187]: "1"
            - generic [ref=e190]:
              - strong [ref=e191]: 运输电池 BAT-C-01 退出
              - paragraph [ref=e192]: 模拟演练：运输电池退出
              - generic [ref=e193]: v1 → v2 · 09:02:05
        - generic [ref=e194]:
          - generic [ref=e195]:
            - generic [ref=e196]:
              - generic [ref=e197]:
                - heading "事件前后航线对比" [level=3] [ref=e198]
                - paragraph [ref=e199]: 旧方案虚线 / 新方案实线，均为各自真实计算输出
              - generic [ref=e200]: 不同快照
            - generic [ref=e201]:
              - generic [ref=e202]:
                - generic:
                  - region "Map" [ref=e203]
                  - button "定位凤丹村无人机调度中心" [ref=e204] [cursor=pointer]:
                    - generic [ref=e205]: O
                    - generic [ref=e206]: 临时调度中心
                  - button "定位那从" [ref=e207] [cursor=pointer]:
                    - generic [ref=e208]: "1"
                    - generic [ref=e209]: 那从
                  - button "定位平旺、那龙、镇龙乡" [ref=e210] [cursor=pointer]:
                    - generic [ref=e211]: "2"
                    - generic [ref=e212]: 平旺、那龙、镇龙乡
                  - button "定位六昌、木路" [ref=e213] [cursor=pointer]:
                    - generic [ref=e214]: "3"
                    - generic [ref=e215]: 六昌、木路
                  - button "定位佛子、那桑、银坑" [ref=e216] [cursor=pointer]:
                    - generic [ref=e217]: "4"
                    - generic [ref=e218]: 佛子、那桑、银坑
                  - button "定位镇龙乡" [ref=e219] [cursor=pointer]:
                    - generic [ref=e220]: "5"
                    - generic [ref=e221]: 镇龙乡
                - generic: 1 km
              - generic:
                - generic:
                  - text: 场景地图
                  - generic: WGS84
                - generic: 题设DEM · 离线
              - generic [ref=e223]:
                - button "放大地图" [ref=e224] [cursor=pointer]
                - button "缩小地图" [ref=e226] [cursor=pointer]
                - button "适配全部点位" [ref=e228] [cursor=pointer]
                - button "图层管理" [ref=e231] [cursor=pointer]
              - generic [ref=e236]:
                - text: "N"
                - generic [ref=e237]: ↑
              - generic:
                - generic: 调度中心
                - generic: 需求点
                - generic: 运输航线
              - generic [ref=e238]: 离线可用 · 图上路线为任务级建议
          - generic [ref=e240]:
            - generic [ref=e241]:
              - text: 机体改派箱件
              - strong [ref=e242]: 7箱
            - generic [ref=e243]:
              - text: 返航时间变化
              - strong [ref=e244]: 236秒
            - generic [ref=e245]:
              - text: 保持架次
              - strong [ref=e246]: 4次
            - generic [ref=e247]:
              - text: 电池改派箱件
              - strong [ref=e248]: 17箱
      - generic [ref=e249]:
        - generic [ref=e250]:
          - generic [ref=e251]:
            - heading "资源时间轴 RESOURCE TIMELINE" [level=3] [ref=e252]
            - paragraph [ref=e253]: 准备、执行与补能，按实体资源核对
          - generic [ref=e254]:
            - generic [ref=e255]:
              - button "机体" [ref=e256] [cursor=pointer]
              - button "电池" [ref=e259] [cursor=pointer]
            - button "展开时间轴" [ref=e264] [cursor=pointer]
        - generic [ref=e274]:
          - generic [ref=e275]:
            - generic [ref=e276]: 资源 / 型号
            - generic [ref=e277]:
              - generic [ref=e278]: 00:00
              - generic [ref=e279]: 00:22
              - generic [ref=e280]: 00:45
              - generic [ref=e281]: 01:08
              - generic [ref=e282]: 01:31
              - generic [ref=e283]: 01:54
              - generic [ref=e284]: 02:17
          - generic [ref=e285]:
            - generic [ref=e286]:
              - strong [ref=e288]: U01
              - generic [ref=e289]: A型
            - generic [ref=e290]:
              - button "3箱" [ref=e298] [cursor=pointer]
              - button "1箱" [ref=e301] [cursor=pointer]
              - button "2箱" [ref=e304] [cursor=pointer]
              - button "1箱" [ref=e307] [cursor=pointer]
          - generic [ref=e310]:
            - generic [ref=e311]:
              - strong [ref=e313]: U05
              - generic [ref=e314]: B型
            - generic [ref=e315]:
              - button "3箱" [ref=e323] [cursor=pointer]
              - button "2箱" [ref=e326] [cursor=pointer]
              - button "2箱" [ref=e329] [cursor=pointer]
              - button "2箱" [ref=e332] [cursor=pointer]
          - generic [ref=e335]:
            - generic [ref=e336]:
              - strong [ref=e338]: U07
              - generic [ref=e339]: C型
            - generic [ref=e340]:
              - button "10箱" [ref=e348] [cursor=pointer]
              - button "6箱" [ref=e351] [cursor=pointer]
        - generic [ref=e354]:
          - generic [ref=e355]: 准备
          - generic [ref=e357]: 执行架次
          - generic [ref=e359]: 相对场景起点 · 区间左闭右开
      - generic [ref=e360]:
        - generic [ref=e361]:
          - generic [ref=e365]: 独立检查已完成 · 仅在声明模型范围内可行
          - button "查看适用范围" [ref=e366] [cursor=pointer]
        - generic [ref=e367]:
          - link "任务CSV" [ref=e368] [cursor=pointer]:
            - /url: /api/v1/plans/PLAN-B6DC7353D77542E8/export?format=csv
          - link "GeoJSON" [ref=e371] [cursor=pointer]:
            - /url: /api/v1/plans/PLAN-B6DC7353D77542E8/export?format=geojson
          - link "计划JSON" [ref=e377] [cursor=pointer]:
            - /url: /api/v1/plans/PLAN-B6DC7353D77542E8/export?format=json
          - link "打印报告" [ref=e382] [cursor=pointer]:
            - /url: /api/v1/plans/PLAN-B6DC7353D77542E8/report
          - button "确认方案" [ref=e387] [cursor=pointer]
  - generic [ref=e390]:
    - generic [ref=e391]:
      - generic [ref=e395]: 方案已确认并原子预约资源。此操作不会下发飞控指令。
      - button "关闭通知" [ref=e396] [cursor=pointer]
    - generic [ref=e400]:
      - generic [ref=e404]: 运输电池 BAT-C-01已退出，新版本正在真实重规划。
      - button "关闭通知" [ref=e405] [cursor=pointer]
    - generic [ref=e409]:
      - generic [ref=e413]: 真实计算完成 · 0分01秒 · 独立检查通过
      - button "关闭通知" [ref=e414] [cursor=pointer]
    - generic [ref=e418]:
      - generic [ref=e422]: 方案已确认并原子预约资源。此操作不会下发飞控指令。
      - button "关闭通知" [ref=e423] [cursor=pointer]
```

# Test source

```ts
  241 |   await page.getByRole('button', { name: '导出分析JSON', exact: true }).click()
  242 |   const exported = JSON.parse(await fs.readFile((await (await download).path())!, 'utf8'))
  243 |   const bound = exported.analysis.capacity_bound
  244 |   expect(bound.status).toBe('ready')
  245 |   expect(bound.sortie_lower_bound).toBe(4)
  246 |   expect(
  247 |     bound.witnesses.reduce(
  248 |       (sum: number, row: { required_quantity: number }) => sum + row.required_quantity,
  249 |       0,
  250 |     ),
  251 |   ).toBe(32)
  252 |   expect(bound.exact.mass_ratio).toMatch(/^\d+\/\d+$/)
  253 |   const plan = await (await request.get(`/api/v1/plans/${exported.analysis.plan_id}`)).json()
  254 |   const snapshot = await (await request.get(`/api/v1/snapshots/${plan.snapshot_id}`)).json()
  255 |   expect(bound.snapshot_content_hash).toBe(snapshot.content_hash)
  256 |   expect(bound.sortie_lower_bound).toBeLessThanOrEqual(plan.sorties.length)
  257 |   for (const [width, height] of [
  258 |     [1440, 900],
  259 |     [1280, 720],
  260 |     [390, 844],
  261 |   ]) {
  262 |     await page.setViewportSize({ width, height })
  263 |     await panel.scrollIntoViewIfNeeded()
  264 |     await screenshot(page, `capacity-bound-${width}`)
  265 |     expect(await panel.evaluate((element) => element.scrollWidth <= element.clientWidth + 1)).toBe(
  266 |       true,
  267 |     )
  268 |   }
  269 |   expect(await (await request.get(`/api/v1/scenarios/${sid}`)).json()).toEqual(source)
  270 |   await fs.writeFile(
  271 |     path.resolve('../evidence/browser/capacity-bound.json'),
  272 |     JSON.stringify({ analysis: exported.analysis, page_errors: errors }, null, 2) + '\n',
  273 |   )
  274 |   expect(errors).toEqual([])
  275 | })
  276 | 
  277 | for (const joint of [false, true]) {
  278 |   test(`${joint ? '联合通信' : '运输'}场景运输电池退出，真实改派、确认和历史恢复`, async ({
  279 |     page,
  280 |     request,
  281 |   }) => {
  282 |     test.setTimeout(joint ? 180000 : 90000)
  283 |     const errors: string[] = []
  284 |     page.on('pageerror', (error) => errors.push(error.message))
  285 |     const sid = await page.getByLabel('选择场景').inputValue()
  286 |     if (joint) {
  287 |       const s = await (await request.get(`/api/v1/scenarios/${sid}`)).json()
  288 |       s.communication = await (
  289 |         await request.get(`/api/v1/scenarios/${sid}/communication-template`)
  290 |       ).json()
  291 |       s.policy.requires_communication = true
  292 |       expect(
  293 |         (
  294 |           await request.put(`/api/v1/scenarios/${sid}`, {
  295 |             data: { expected_state_version: 1, scenario: s },
  296 |           })
  297 |         ).ok(),
  298 |       ).toBe(true)
  299 |       await page.reload()
  300 |     }
  301 |     await page.getByRole('button', { name: '生成真实方案', exact: true }).click()
  302 |     await expect(page.locator('.job-banner')).toBeVisible()
  303 |     await expect(page.locator('.job-banner')).toBeHidden({ timeout: 90000 })
  304 |     await expect(page.getByTestId('sortie-card').first()).toBeVisible()
  305 |     const first = (await (await request.get(`/api/v1/scenarios/${sid}/plans`)).json())[0]
  306 |     const old = await (await request.get(`/api/v1/plans/${first.plan_id}`)).json()
  307 |     const oldSnapshot = await (await request.get(`/api/v1/snapshots/${old.snapshot_id}`)).json()
  308 |     const failed = old.sorties[0].battery_id
  309 |     await page.getByRole('button', { name: '确认方案', exact: true }).click()
  310 |     await expect(page.locator('.toast').filter({ hasText: '方案已确认' })).toBeVisible()
  311 |     await page.getByRole('button', { name: '事件复盘', exact: true }).click()
  312 |     await page.getByLabel('故障事件类型').selectOption('battery')
  313 |     await page.getByLabel('故障运输电池').selectOption(failed)
  314 |     await page.getByRole('button', { name: '记录故障并重规划', exact: true }).click()
  315 |     await expect(page.locator('.job-banner')).toBeVisible()
  316 |     await expect(page.locator('.job-banner')).toBeHidden({ timeout: 90000 })
  317 |     await expect(page.locator('.event-history')).toContainText(`运输电池 ${failed} 退出`)
  318 |     await expect(page.locator('.comparison-cards')).toContainText('电池改派箱件')
  319 |     const summaries = await (await request.get(`/api/v1/scenarios/${sid}/plans`)).json()
  320 |     const plan = await (await request.get(`/api/v1/plans/${summaries[0].plan_id}`)).json()
  321 |     expect(plan.plan_id).not.toBe(old.plan_id)
  322 |     expect(plan.parent_plan_id).toBe(old.plan_id)
  323 |     expect(plan.scenario_state_version).toBe(old.scenario_state_version + 1)
  324 |     expect(plan.validation.status).toBe('passed')
  325 |     expect(plan.sorties.every((row: { battery_id: string }) => row.battery_id !== failed)).toBe(
  326 |       true,
  327 |     )
  328 |     expect(
  329 |       new Set(plan.sorties.flatMap((row: { cargo_ids: string[] }) => row.cargo_ids)).size,
  330 |     ).toBe(32)
  331 |     if (joint) expect(plan.communication_report.coverage_gap_s).toBe(0)
  332 |     expect(await (await request.get(`/api/v1/plans/${old.plan_id}`)).json()).toEqual(old)
  333 |     expect(await (await request.get(`/api/v1/snapshots/${old.snapshot_id}`)).json()).toEqual(
  334 |       oldSnapshot,
  335 |     )
  336 |     const events = await (await request.get(`/api/v1/scenarios/${sid}/events`)).json()
  337 |     expect(events).toHaveLength(1)
  338 |     expect(events[0].event_type).toBe('battery.unavailable')
  339 |     expect(events[0].payload).toEqual({ battery_id: failed })
  340 |     await page.getByRole('button', { name: '确认方案', exact: true }).click()
> 341 |     await expect(page.locator('.toast').filter({ hasText: '方案已确认' })).toBeVisible()
      |                                                                       ^ Error: expect(locator).toBeVisible() failed
  342 |     const name = joint ? 'joint-battery-fault' : 'battery-fault'
  343 |     await screenshot(page, `${name}-1440`)
  344 |     await page.reload()
  345 |     await page.getByRole('button', { name: '事件复盘', exact: true }).click()
  346 |     await expect(page.locator('.event-history')).toContainText(`运输电池 ${failed} 退出`)
  347 |     await expect(page.locator('.comparison-cards')).toContainText('电池改派箱件')
  348 |     await page.setViewportSize({ width: 1280, height: 720 })
  349 |     await screenshot(page, `${name}-1280`)
  350 |     for (const width of [1280, 390]) {
  351 |       await page.setViewportSize({ width, height: width === 390 ? 844 : 720 })
  352 |       await page.locator('.comparison-cards').scrollIntoViewIfNeeded()
  353 |       await page.screenshot({
  354 |         path: path.resolve(`../evidence/browser/verified/${name}-changes-${width}.png`),
  355 |       })
  356 |     }
  357 |     await fs.writeFile(
  358 |       path.resolve(`../evidence/solver/${joint ? 'joint-' : ''}battery-replan.json`),
  359 |       JSON.stringify(
  360 |         {
  361 |           old_snapshot: oldSnapshot,
  362 |           old_plan: old,
  363 |           event: events[0],
  364 |           snapshot: await (await request.get(`/api/v1/snapshots/${plan.snapshot_id}`)).json(),
  365 |           plan,
  366 |           page_errors: errors,
  367 |         },
  368 |         null,
  369 |         2,
  370 |       ) + '\n',
  371 |     )
  372 |     expect(errors).toEqual([])
  373 |   })
  374 | }
  375 | 
  376 | test('点击真实架次追溯通信来源，窗口导出与地图联动保持原始快照', async ({ page, request }) => {
  377 |   test.setTimeout(150000)
  378 |   const errors: string[] = []
  379 |   page.on('pageerror', (e) => errors.push(e.message))
  380 |   const sid = await page.getByLabel('选择场景').inputValue()
  381 |   const scene = await (await request.get(`/api/v1/scenarios/${sid}`)).json()
  382 |   scene.communication = await (
  383 |     await request.get(`/api/v1/scenarios/${sid}/communication-template`)
  384 |   ).json()
  385 |   scene.policy.requires_communication = true
  386 |   expect(
  387 |     (
  388 |       await request.put(`/api/v1/scenarios/${sid}`, {
  389 |         data: { expected_state_version: 1, scenario: scene },
  390 |       })
  391 |     ).ok(),
  392 |   ).toBe(true)
  393 |   await page.reload()
  394 |   await page.getByRole('button', { name: '生成真实方案', exact: true }).click()
  395 |   await expect(page.locator('.job-banner')).toBeVisible()
  396 |   await expect(page.locator('.job-banner')).toBeHidden({ timeout: 90000 })
  397 |   const plan = await (
  398 |     await request.get(
  399 |       `/api/v1/plans/${(await (await request.get(`/api/v1/scenarios/${sid}/plans`)).json())[0].plan_id}`,
  400 |     )
  401 |   ).json()
  402 |   const snapshot = await (await request.get(`/api/v1/snapshots/${plan.snapshot_id}`)).json()
  403 |   const relayWindow = plan.communication_report.windows.find(
  404 |     (w: { source: string }) => w.source === 'relay',
  405 |   )
  406 |   expect(relayWindow).toBeTruthy()
  407 |   const index = plan.sorties.findIndex(
  408 |     (r: { sortie_id: string }) => r.sortie_id === relayWindow.sortie_id,
  409 |   )
  410 |   await page.getByTestId('sortie-card').nth(index).click()
  411 |   const evidence = page.getByRole('region', { name: '通信来源证据' })
  412 |   await expect(page.getByLabel('通信来源架次')).toHaveValue(relayWindow.sortie_id)
  413 |   await evidence.locator('.coverage-window-button[data-source=relay]').first().click()
  414 |   const download = page.waitForEvent('download')
  415 |   await evidence.getByRole('button', { name: '导出所选窗口', exact: true }).click()
  416 |   const exported = JSON.parse(await fs.readFile((await (await download).path())!, 'utf8'))
  417 |   expect(exported.plan_id).toBe(plan.plan_id)
  418 |   expect(exported.snapshot_id).toBe(plan.snapshot_id)
  419 |   expect(plan.communication_report.windows).toContainEqual(exported.window)
  420 |   const relay = plan.relay_sorties.find(
  421 |     (r: { relay_sortie_id: string }) => r.relay_sortie_id === exported.window.relay_sortie_id,
  422 |   )
  423 |   expect(exported.relay_sortie).toEqual(relay)
  424 |   expect(exported.gateway_at_base).toEqual(snapshot.scenario.base)
  425 |   await expect(evidence.getByLabel('通信链路来源')).toContainText(relay.drone_id)
  426 |   await expect(evidence.getByLabel('通信链路来源')).toContainText(relay.component_id)
  427 |   await expect(page.locator('.toast')).toHaveCount(0, { timeout: 12000 })
  428 |   for (const [width, height] of [
  429 |     [1440, 900],
  430 |     [1280, 720],
  431 |   ]) {
  432 |     await page.setViewportSize({ width, height })
  433 |     await evidence.scrollIntoViewIfNeeded()
  434 |     await evidence.screenshot({
  435 |       path: path.resolve(`../evidence/browser/verified/communication-source-${width}.png`),
  436 |     })
  437 |     if (width === 1280) {
  438 |       await evidence.locator('.coverage-source-detail').scrollIntoViewIfNeeded()
  439 |       await expect(evidence.locator('.coverage-source-provenance')).toBeInViewport()
  440 |       await page.screenshot({
  441 |         path: path.resolve('../evidence/browser/verified/communication-source-detail-1280.png'),
```