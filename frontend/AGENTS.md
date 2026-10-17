# B 系统线前端模块

与 backend owner 为同一位 B。遵守根 AGENTS，先读 docs/04、UI_ACCEPTANCE、总纲第6章。

三页 React/Vite/TypeScript strict 目标架构。API 入口集中，Mock/HTTP Provider 同类型，生成类型不手改。地图、表格、甘特使用后端 sortie_id、drone_id、battery_id 联动，UI 不计算业务能耗/SOC。

Mock 常驻提示，禁确认；null/未评估/失败分别显示。capabilities 没有的功能不假装可用，页面播放不写实际交付。

当前已有React/Vite应用、真实HTTP客户端、生成TS、三页、离线MapLibre、双甘特、策略与重规划。入口src/App.tsx，类型来自api/generated/http.d.ts。用npm.cmd run lint/build/test:unit；E2E由scripts/run-e2e.mjs启动隔离8011/5174，不使用演示数据库。进度与已知问题先读docs/IMPLEMENTATION_STATUS.md，不从G0历史描述重新建项目。目录src/lib/必须提交，不能被Python通用lib忽略规则漏掉。
