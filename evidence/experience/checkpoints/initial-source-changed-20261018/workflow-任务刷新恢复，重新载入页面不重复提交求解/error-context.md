# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workflow.spec.ts >> 任务刷新恢复，重新载入页面不重复提交求解
- Location: tests\workflow.spec.ts:1381:1

# Error details

```
Error: expect(received).toBeGreaterThan(expected)

Expected: > 1
Received:   1

Call Log:
- Timeout 15000ms exceeded while waiting on the predicate
```

# Page snapshot

```yaml
- generic [ref=f2e3]:
  - complementary [ref=f2e4]:
    - link "援航 YUANHANG RESCUE" [ref=f2e5] [cursor=pointer]:
      - /url: "#"
      - generic [ref=f2e10]:
        - strong [ref=f2e11]: 援航
        - generic [ref=f2e12]: YUANHANG RESCUE
    - generic [ref=f2e13]:
      - generic [ref=f2e14]: 应
      - generic [ref=f2e15]:
        - strong [ref=f2e16]: 援航救援工作组
        - generic [ref=f2e17]: 应急协同 · 本机工作空间
    - generic [ref=f2e20]: 任务协同
    - navigation [ref=f2e21]:
      - button "数据大屏" [ref=f2e22] [cursor=pointer]
      - button "场景与资源" [ref=f2e26] [cursor=pointer]
      - button "地图与地形" [ref=f2e32] [cursor=pointer]
      - button "调度工作台" [ref=f2e39] [cursor=pointer]
      - button "方案对比" [ref=f2e44] [cursor=pointer]
      - button "事件复盘" [ref=f2e53] [cursor=pointer]
      - button "历史档案" [ref=f2e57] [cursor=pointer]
      - button "新手教程" [ref=f2e63] [cursor=pointer]
    - generic [ref=f2e67]:
      - strong [ref=f2e72]: 救援决策，从这里开始
      - paragraph [ref=f2e73]: 准备数据、读取地形、生成方案。跟着教程完成第一次调度。
      - button "打开上手指南" [ref=f2e74] [cursor=pointer]
    - generic [ref=f2e77]:
      - generic [ref=f2e78]:
        - text: 本机服务
        - generic [ref=f2e80]: 离线可用
      - button "使用教程与常见问题" [ref=f2e81] [cursor=pointer]
      - button "账户与本机档案" [ref=f2e85] [cursor=pointer]:
        - generic [ref=f2e86]: 本
        - generic [ref=f2e87]:
          - strong [ref=f2e88]: 本机调度员
          - generic [ref=f2e89]: 调度负责人 · 本机档案
  - generic [ref=f2e93]:
    - banner [ref=f2e94]:
      - generic [ref=f2e95]:
        - generic [ref=f2e96]: 救援工作空间
        - strong [ref=f2e99]: 调度工作台
      - generic [ref=f2e100]:
        - button "切换浅色主题" [ref=f2e101] [cursor=pointer]
        - button "暂停动态背景" [pressed] [ref=f2e108] [cursor=pointer]
        - generic [ref=f2e112]: 本地服务已连接
        - button "查看模型说明" [ref=f2e114] [cursor=pointer]
        - button "打开个人档案" [ref=f2e118] [cursor=pointer]: 本
    - main [ref=f2e119]:
      - generic [ref=f2e120]:
        - generic [ref=f2e121]:
          - generic [ref=f2e126]:
            - combobox "选择场景" [ref=f2e127]:
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
            - generic [ref=f2e128]: 5 个需求点 32 箱物资 场景起点 08:00
          - generic [ref=f2e131]: 模拟演练
          - generic [ref=f2e132]: v1
        - generic [ref=f2e133]:
          - button "新建演练" [ref=f2e134] [cursor=pointer]
          - button "更多场景操作" [ref=f2e137] [cursor=pointer]
      - generic [ref=f2e142]:
        - generic [ref=f2e143]:
          - generic [ref=f2e144]: MISSION CONTROL
          - heading "每一份物资，都有清晰的下一程 LIVE WORKSPACE" [level=1] [ref=f2e145]:
            - text: 每一份物资，都有清晰的下一程
            - generic [ref=f2e146]: LIVE WORKSPACE
          - paragraph [ref=f2e147]: 从真实输入出发，统筹箱件、机体与电池，生成可核对的运输方案。
        - generic [ref=f2e148]:
          - combobox "选择历史方案" [ref=f2e149]
          - button "检查报告" [ref=f2e150] [cursor=pointer]
          - button "深入优化30秒" [ref=f2e154] [cursor=pointer]
          - button "重新求解" [ref=f2e160] [cursor=pointer]
      - generic [ref=f2e163]:
        - generic [ref=f2e164]: 当前方案 · 真实数据联动
        - button "三维与高度分析" [ref=f2e166] [cursor=pointer]
        - button "卫星地图 / 导入DEM" [ref=f2e171] [cursor=pointer]
        - button "方案对比" [ref=f2e177] [cursor=pointer]
        - button "历史档案" [ref=f2e185] [cursor=pointer]
      - generic [ref=f2e190]:
        - generic [ref=f2e191]:
          - generic [ref=f2e192]: 已安排箱件
          - generic [ref=f2e197]: 32/ 32 箱
          - generic [ref=f2e198]: 完整服务 · 箱件唯一分配
        - generic [ref=f2e200]:
          - generic [ref=f2e201]: 最后交付
          - generic [ref=f2e205]: 2时02分
          - generic [ref=f2e206]: 最后返航 2时07分
        - generic [ref=f2e208]:
          - generic [ref=f2e209]: 预计总能耗
          - generic [ref=f2e212]: 23.31kWh
          - generic [ref=f2e213]: 7 架次 · 已含返航
        - generic [ref=f2e215]:
          - generic [ref=f2e216]: 最低返航电量
          - generic [ref=f2e221]: 27.1%
          - generic [ref=f2e222]: 策略下限 20.0%
      - generic "加权箱秒是每箱期望延期秒乘需求优先级的合计，不是墙钟时长。" [ref=f2e224]:
        - generic [ref=f2e225]: 硬截止已检查
        - generic [ref=f2e226]: 期望延期 4 条 · 加权箱秒 78,322
        - generic [ref=f2e227]: 先减少优先级加权期望延期，再比较时间 / 能耗
      - generic [ref=f2e228]:
        - generic [ref=f2e229]:
          - generic [ref=f2e230]:
            - heading "运输任务 7" [level=3] [ref=f2e231]:
              - text: 运输任务
              - generic [ref=f2e232]: "7"
            - button "编辑场景资源" [ref=f2e233] [cursor=pointer]
          - generic [ref=f2e237]:
            - button "架次" [ref=f2e238] [cursor=pointer]
            - button "需求" [ref=f2e239] [cursor=pointer]
            - button "箱件" [ref=f2e240] [cursor=pointer]
          - textbox "搜索任务" [ref=f2e245]:
            - /placeholder: 搜索编号、机体、需求点…
          - generic [ref=f2e246]:
            - button "01 U07 已规划 S001 → S006 8 箱 00:09" [ref=f2e247] [cursor=pointer]:
              - generic [ref=f2e248]:
                - generic [ref=f2e249]: "01"
                - strong [ref=f2e250]: U07
                - generic [ref=f2e251]: 已规划
              - paragraph [ref=f2e252]: S001 → S006
              - generic [ref=f2e253]:
                - generic [ref=f2e254]: 8 箱
                - generic [ref=f2e259]: 00:09
            - button "02 U05 已规划 S007 3 箱 00:06" [ref=f2e264] [cursor=pointer]:
              - generic [ref=f2e265]:
                - generic [ref=f2e266]: "02"
                - strong [ref=f2e267]: U05
                - generic [ref=f2e268]: 已规划
              - paragraph [ref=f2e269]: S007
              - generic [ref=f2e270]:
                - generic [ref=f2e271]: 3 箱
                - generic [ref=f2e276]: 00:06
            - button "03 U01 已规划 S011 → S010 3 箱 00:06" [ref=f2e281] [cursor=pointer]:
              - generic [ref=f2e282]:
                - generic [ref=f2e283]: "03"
                - strong [ref=f2e284]: U01
                - generic [ref=f2e285]: 已规划
              - paragraph [ref=f2e286]: S011 → S010
              - generic [ref=f2e287]:
                - generic [ref=f2e288]: 3 箱
                - generic [ref=f2e293]: 00:06
            - button "04 U07 已规划 S006 → S011 → S001 7 箱 00:47" [ref=f2e298] [cursor=pointer]:
              - generic [ref=f2e299]:
                - generic [ref=f2e300]: "04"
                - strong [ref=f2e301]: U07
                - generic [ref=f2e302]: 已规划
              - paragraph [ref=f2e303]: S006 → S011 → S001
              - generic [ref=f2e304]:
                - generic [ref=f2e305]: 7 箱
                - generic [ref=f2e310]: 00:47
            - button "05 U05 已规划 S001 2 箱 00:33" [ref=f2e315] [cursor=pointer]:
              - generic [ref=f2e316]:
                - generic [ref=f2e317]: "05"
                - strong [ref=f2e318]: U05
                - generic [ref=f2e319]: 已规划
              - paragraph [ref=f2e320]: S001
              - generic [ref=f2e321]:
                - generic [ref=f2e322]: 2 箱
                - generic [ref=f2e327]: 00:33
            - button "06 U07 已规划 S007 → S011 → S001 8 箱 01:29" [ref=f2e332] [cursor=pointer]:
              - generic [ref=f2e333]:
                - generic [ref=f2e334]: "06"
                - strong [ref=f2e335]: U07
                - generic [ref=f2e336]: 已规划
              - paragraph [ref=f2e337]: S007 → S011 → S001
              - generic [ref=f2e338]:
                - generic [ref=f2e339]: 8 箱
                - generic [ref=f2e344]: 01:29
            - button "07 U01 已规划 S010 1 箱 00:43" [ref=f2e349] [cursor=pointer]:
              - generic [ref=f2e350]:
                - generic [ref=f2e351]: "07"
                - strong [ref=f2e352]: U01
                - generic [ref=f2e353]: 已规划
              - paragraph [ref=f2e354]: S010
              - generic [ref=f2e355]:
                - generic [ref=f2e356]: 1 箱
                - generic [ref=f2e361]: 00:43
          - generic [ref=f2e366]: 稳定ID跨视图联动
        - generic [ref=f2e368]:
          - generic [ref=f2e369]:
            - generic [ref=f2e370]:
              - generic:
                - region "Map" [ref=f2e371]
                - button "定位凤丹村无人机调度中心" [ref=f2e372] [cursor=pointer]:
                  - generic [ref=f2e373]: O
                  - generic [ref=f2e374]: 临时调度中心
                - button "定位那从" [ref=f2e375] [cursor=pointer]:
                  - generic [ref=f2e376]: "1"
                  - generic [ref=f2e377]: 那从
                - button "定位平旺、那龙、镇龙乡" [ref=f2e378] [cursor=pointer]:
                  - generic [ref=f2e379]: "2"
                  - generic [ref=f2e380]: 平旺、那龙、镇龙乡
                - button "定位六昌、木路" [ref=f2e381] [cursor=pointer]:
                  - generic [ref=f2e382]: "3"
                  - generic [ref=f2e383]: 六昌、木路
                - button "定位佛子、那桑、银坑" [ref=f2e384] [cursor=pointer]:
                  - generic [ref=f2e385]: "4"
                  - generic [ref=f2e386]: 佛子、那桑、银坑
                - button "定位镇龙乡" [ref=f2e387] [cursor=pointer]:
                  - generic [ref=f2e388]: "5"
                  - generic [ref=f2e389]: 镇龙乡
                - generic "老村 · 原题OSM背景资料": 老村
                - generic "竹瓦 · 原题OSM背景资料": 竹瓦
                - generic "平旺 · 原题OSM背景资料": 平旺
              - generic: 2 km
            - generic:
              - generic:
                - text: 场景地图
                - generic: WGS84
              - generic: 题设DEM · 离线
            - group "地图底图" [ref=f2e391]:
              - button "离线地形" [pressed] [ref=f2e392] [cursor=pointer]
              - button "卫星影像 联网" [ref=f2e395] [cursor=pointer]:
                - text: 卫星影像
                - generic [ref=f2e402]: 联网
            - generic [ref=f2e403]:
              - button "放大地图" [ref=f2e404] [cursor=pointer]
              - button "缩小地图" [ref=f2e406] [cursor=pointer]
              - button "适配全部点位" [ref=f2e408] [cursor=pointer]
              - button "图层管理" [ref=f2e411] [cursor=pointer]
            - generic [ref=f2e416]:
              - text: "N"
              - generic [ref=f2e417]: ↑
            - generic:
              - generic: 调度中心
              - generic: 需求点
              - generic: 运输航线
            - generic [ref=f2e418]:
              - generic [ref=f2e419]:
                - link "© OpenStreetMap contributors · ODbL" [ref=f2e420] [cursor=pointer]:
                  - /url: https://www.openstreetmap.org/copyright
                - text: · 历史背景资料
              - text: 离线可用 · 图上路线为任务级建议
          - generic [ref=f2e421]:
            - button "播放计划回放" [ref=f2e422] [cursor=pointer]
            - generic [ref=f2e425]: 00:00:00
            - slider "计划回放时钟" [ref=f2e426]: "0"
            - generic [ref=f2e427]: 计划示意回放
            - generic [ref=f2e428]: 非执行事实
        - complementary [ref=f2e429]:
          - generic [ref=f2e430]:
            - generic [ref=f2e432]:
              - heading "策略方案" [level=3] [ref=f2e433]
              - paragraph [ref=f2e434]: 同一快照 · 相同保障要求
            - generic [ref=f2e439]:
              - strong [ref=f2e445]: 时间优先
              - paragraph [ref=f2e449]: 先减加权期望延期，再缩短完成时间
              - generic [ref=f2e450]:
                - generic [ref=f2e451]: 2时07分
                - generic [ref=f2e452]: 23.31 kWh
              - button "当前展示方案" [ref=f2e453] [cursor=pointer]
            - generic [ref=f2e456]:
              - strong [ref=f2e462]: 能耗优先
              - paragraph [ref=f2e463]: 先减加权期望延期，再降低能源消耗
              - button "真实计算此策略" [ref=f2e464] [cursor=pointer]
            - generic "延期相同后，比较最后返航秒数 + 300 × 能耗(kWh)；启用通信时使用联合指标" [ref=f2e467]:
              - generic [ref=f2e468]:
                - strong [ref=f2e473]: 均衡偏好
                - generic [ref=f2e474]: 同样先减期望延期
              - button "真实计算均衡策略" [ref=f2e475] [cursor=pointer]
            - paragraph [ref=f2e478]: 费用未配置，不显示人民币。共同延期目标优先，三种偏好可能得到相同方案。
          - generic [ref=f2e479]:
            - generic [ref=f2e480]:
              - generic [ref=f2e481]:
                - heading "选中架次" [level=3] [ref=f2e482]
                - paragraph [ref=f2e483]: SRT-6396ff71573f
              - generic [ref=f2e484]: U07
            - generic [ref=f2e485]:
              - generic [ref=f2e486]:
                - generic [ref=f2e488]: 基地准备
                - strong [ref=f2e489]: 00:00:00
              - generic [ref=f2e490]:
                - generic [ref=f2e492]: S001 · 7箱交接
                - strong [ref=f2e493]: 00:21:18
              - generic [ref=f2e494]:
                - generic [ref=f2e496]: S006 · 1箱交接
                - strong [ref=f2e497]: 00:32:50
              - generic [ref=f2e498]:
                - generic [ref=f2e500]: 返回基地
                - strong [ref=f2e501]: 00:38:43
            - generic [ref=f2e502]:
              - generic [ref=f2e503]:
                - generic [ref=f2e504]: 使用电池
                - strong [ref=f2e505]: BAT-C-01
              - generic [ref=f2e506]:
                - generic [ref=f2e507]: 预计能耗
                - strong [ref=f2e508]: 4.762 kWh
              - generic [ref=f2e509]:
                - generic [ref=f2e510]: 返航SOC
                - strong [ref=f2e511]: 40.5%
              - generic [ref=f2e512]:
                - generic [ref=f2e513]: 装载箱件
                - strong [ref=f2e514]: 8 箱
            - button "在箱件清单中追踪" [ref=f2e515] [cursor=pointer]
      - generic [ref=f2e518]:
        - generic [ref=f2e519]:
          - generic [ref=f2e520]:
            - heading "资源时间轴 RESOURCE TIMELINE" [level=3] [ref=f2e521]
            - paragraph [ref=f2e522]: 准备、执行与补能，按实体资源核对
          - generic [ref=f2e523]:
            - generic [ref=f2e524]:
              - button "机体" [ref=f2e525] [cursor=pointer]
              - button "电池" [ref=f2e528] [cursor=pointer]
            - button "展开时间轴" [ref=f2e533] [cursor=pointer]
        - generic [ref=f2e543]:
          - generic [ref=f2e544]:
            - generic [ref=f2e545]: 资源 / 型号
            - generic [ref=f2e546]:
              - generic [ref=f2e547]: 00:00
              - generic [ref=f2e548]: 00:22
              - generic [ref=f2e549]: 00:44
              - generic [ref=f2e550]: 01:06
              - generic [ref=f2e551]: 01:29
              - generic [ref=f2e552]: 01:51
              - generic [ref=f2e553]: 02:13
          - generic [ref=f2e554]:
            - generic [ref=f2e555]:
              - strong [ref=f2e557]: U01
              - generic [ref=f2e558]: A型
            - generic [ref=f2e559]:
              - button "3箱" [ref=f2e567] [cursor=pointer]
              - button "1箱" [ref=f2e570] [cursor=pointer]
          - generic [ref=f2e573]:
            - generic [ref=f2e574]:
              - strong [ref=f2e576]: U05
              - generic [ref=f2e577]: B型
            - generic [ref=f2e578]:
              - button "3箱" [ref=f2e586] [cursor=pointer]
              - button "2箱" [ref=f2e589] [cursor=pointer]
          - generic [ref=f2e592]:
            - generic [ref=f2e593]:
              - strong [ref=f2e595]: U07
              - generic [ref=f2e596]: C型
            - generic [ref=f2e597]:
              - button "8箱" [ref=f2e605] [cursor=pointer]
              - button "7箱" [ref=f2e608] [cursor=pointer]
              - button "8箱" [ref=f2e611] [cursor=pointer]
        - generic [ref=f2e614]:
          - generic [ref=f2e615]: 准备
          - generic [ref=f2e617]: 执行架次
          - generic [ref=f2e619]: 相对场景起点 · 区间左闭右开
      - generic [ref=f2e620]:
        - generic [ref=f2e621]:
          - generic [ref=f2e625]: 独立检查已完成 · 仅在声明模型范围内可行
          - button "查看适用范围" [ref=f2e626] [cursor=pointer]
        - generic [ref=f2e627]:
          - link "任务CSV" [ref=f2e628] [cursor=pointer]:
            - /url: /api/v1/plans/PLAN-7B617139EE7B4445/export?format=csv
          - link "GeoJSON" [ref=f2e631] [cursor=pointer]:
            - /url: /api/v1/plans/PLAN-7B617139EE7B4445/export?format=geojson
          - link "计划JSON" [ref=f2e637] [cursor=pointer]:
            - /url: /api/v1/plans/PLAN-7B617139EE7B4445/export?format=json
          - link "打印报告" [ref=f2e642] [cursor=pointer]:
            - /url: /api/v1/plans/PLAN-7B617139EE7B4445/report
          - button "确认方案" [ref=f2e647] [cursor=pointer]
```

# Test source

```ts
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
  1386 |   await expect(page.getByTestId('sortie-card').first()).toBeVisible({ timeout: 45000 })
  1387 |   const jobs = await (await request.get(`/api/v1/scenarios/${sceneId}/solve-jobs`)).json()
  1388 |   expect(jobs.length).toBe(1)
  1389 |   expect(jobs[0].job_state).toBe('completed')
  1390 |   expect(jobs[0].has_validated_plan).toBe(true)
  1391 | 
  1392 |   // A plans read can precede the worker commit while job metadata follows it.
  1393 |   // Only the first list response is stale; the stored result remains real.
  1394 |   let planReads = 0
  1395 |   await page.route(`**/api/v1/scenarios/${sceneId}/plans`, async (route) => {
  1396 |     planReads++
  1397 |     if (planReads === 1) await route.fulfill({ json: [] })
  1398 |     else await route.continue()
  1399 |   })
  1400 |   await page.route(`**/api/v1/scenarios/${sceneId}/solve-jobs`, async (route) => {
  1401 |     await new Promise((resolve) => setTimeout(resolve, 250))
  1402 |     await route.continue()
  1403 |   })
  1404 |   await page.reload()
  1405 |   await expect(page.getByTestId('sortie-card').first()).toBeVisible()
> 1406 |   await expect.poll(() => planReads).toBeGreaterThan(1)
       |                                      ^ Error: expect(received).toBeGreaterThan(expected)
  1407 |   await expect(page.locator('.toast').filter({ hasText: '真实计算完成' })).toHaveCount(0)
  1408 |   const recovered = await (await request.get(`/api/v1/scenarios/${sceneId}/solve-jobs`)).json()
  1409 |   expect(recovered).toHaveLength(1)
  1410 |   expect(recovered[0].job_id).toBe(jobs[0].job_id)
  1411 | })
  1412 | 
  1413 | test('打印报告包含真实任务并可离线保存PDF', async ({ page }) => {
  1414 |   await solve(page)
  1415 |   const popup = page.waitForEvent('popup')
  1416 |   await page.getByRole('link', { name: '打印报告', exact: true }).click()
  1417 |   const report = await popup
  1418 |   await expect(report.getByRole('heading', { level: 1 })).toHaveText('援航 · 运输调度与资源报告')
  1419 |   await expect(report.locator('table')).toHaveCount(4)
  1420 |   await expect(report.locator('body')).toContainText('逐箱物资追踪')
  1421 |   await expect(report.locator('.identity')).toContainText('输入Hash')
  1422 |   await report.screenshot({
  1423 |     path: path.resolve('../evidence/browser/verified/print-report-screen.png'),
  1424 |   })
  1425 |   await report.pdf({
  1426 |     path: path.resolve('../evidence/browser/verified/print-report.pdf'),
  1427 |     format: 'A4',
  1428 |     landscape: true,
  1429 |     printBackground: true,
  1430 |     preferCSSPageSize: true,
  1431 |   })
  1432 |   await report.close()
  1433 | })
  1434 | 
  1435 | test('深入优化保留同快照基线，刷新后继续真实计算', async ({ page, request }) => {
  1436 |   await solve(page)
  1437 |   const sceneId = await page.getByLabel('选择场景').inputValue()
  1438 |   const old = (await (await request.get(`/api/v1/scenarios/${sceneId}/plans`)).json())[0]
  1439 |   await page.getByRole('button', { name: '深入优化30秒', exact: true }).click()
  1440 |   await expect(page.locator('.job-banner')).toBeVisible()
  1441 |   await page.reload()
  1442 |   await expect(page.locator('.job-banner')).toBeVisible()
  1443 |   await expect(page.locator('.job-banner')).toBeHidden({ timeout: 45000 })
  1444 |   await expect(page.getByTestId('sortie-card').first()).toBeVisible()
  1445 |   const plans = await (await request.get(`/api/v1/scenarios/${sceneId}/plans`)).json()
  1446 |   expect(plans).toHaveLength(2)
  1447 |   expect(plans[0].snapshot_id).toBe(old.snapshot_id)
  1448 |   expect(plans[0].algorithm_mode).toBe('improve')
  1449 |   expect(plans[0].source_plan_id).toBe(old.plan_id)
  1450 |   const jobs = await (await request.get(`/api/v1/scenarios/${sceneId}/solve-jobs`)).json()
  1451 |   expect(jobs).toHaveLength(2)
  1452 |   expect(jobs.every((j: { job_state: string }) => j.job_state === 'completed')).toBe(true)
  1453 |   const current = await (await request.get(`/api/v1/plans/${plans[0].plan_id}`)).json()
  1454 |   expect(current.validation.status).toBe('passed')
  1455 |   await screenshot(page, 'deep-optimization-1440')
  1456 | })
  1457 | 
  1458 | test('限制区保存新版本，真实绕行并沿折线回放', async ({ page, request }) => {
  1459 |   const errors: string[] = []
  1460 |   page.on('pageerror', (e) => errors.push(e.message))
  1461 |   await solve(page)
  1462 |   const sceneId = await page.getByLabel('选择场景').inputValue()
  1463 |   const old = (await (await request.get(`/api/v1/scenarios/${sceneId}/plans`)).json())[0]
  1464 |   await page.getByRole('button', { name: '场景与资源', exact: true }).click()
  1465 |   await page.getByRole('button', { name: '管理限制区', exact: true }).click()
  1466 |   await expect(page.getByRole('dialog')).toBeVisible()
  1467 |   await page.getByRole('button', { name: '加入草稿', exact: true }).click()
  1468 |   await expect(page.getByLabel('限制区JSON')).toContainText('临时限制区')
  1469 |   await page.screenshot({ path: path.resolve('../evidence/browser/verified/zone-editor-1440.png') })
  1470 |   await page.getByRole('button', { name: '保存限制区', exact: true }).click()
  1471 |   await expect(page.getByRole('dialog')).toBeHidden()
  1472 |   await expect(page.locator('.zone-saved-list')).toContainText('临时限制区')
  1473 |   await page.getByRole('button', { name: '调度工作台', exact: true }).click()
  1474 |   await expect(page.getByRole('button', { name: '确认方案', exact: true })).toBeDisabled()
  1475 |   await solve(page)
  1476 |   const plans = await (await request.get(`/api/v1/scenarios/${sceneId}/plans`)).json()
  1477 |   expect(plans).toHaveLength(2)
  1478 |   expect(plans[0].snapshot_id).not.toBe(old.snapshot_id)
  1479 |   const plan = await (await request.get(`/api/v1/plans/${plans[0].plan_id}`)).json()
  1480 |   expect(plan.model_scope).toContain('restricted_zone')
  1481 |   expect(
  1482 |     plan.sorties.some(
  1483 |       (r: { visits: unknown[]; route_geometry: { coordinates: unknown[] } }) =>
  1484 |         r.route_geometry.coordinates.length > r.visits.length + 2,
  1485 |     ),
  1486 |   ).toBe(true)
  1487 |   expect(
  1488 |     plan.validation.checks.some(
  1489 |       (c: { code: string; status: string }) =>
  1490 |         c.code === 'restricted_zone' && c.status === 'passed',
  1491 |     ),
  1492 |   ).toBe(true)
  1493 |   await page.getByRole('button', { name: '检查报告', exact: true }).click()
  1494 |   await expect(page.getByRole('dialog')).toContainText('限制区与缓冲')
  1495 |   await page.getByRole('dialog').getByRole('button', { name: '关闭弹窗' }).click()
  1496 |   await screenshot(page, 'zone-detour-1440')
  1497 |   await page.getByRole('button', { name: '播放计划回放', exact: true }).click()
  1498 |   await expect(page.locator('.planned-aircraft').first()).toBeVisible()
  1499 |   await page.getByRole('button', { name: '暂停计划回放', exact: true }).click()
  1500 |   expect(errors).toEqual([])
  1501 | })
  1502 | 
  1503 | test('GeoTIFF资产上传绑定，真实Worker使用新DEM并恢复历史', async ({ page, request }) => {
  1504 |   const errors: string[] = []
  1505 |   page.on('pageerror', (e) => errors.push(e.message))
  1506 |   await solve(page)
```