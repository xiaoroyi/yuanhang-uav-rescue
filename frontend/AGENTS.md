# B 系统线前端模块

与 backend owner 为同一位 B。遵守根 AGENTS，先读 docs/04、UI_ACCEPTANCE、总纲第6章。

三页 React/Vite/TypeScript strict 目标架构。API 入口集中，Mock/HTTP Provider 同类型，生成类型不手改。地图、表格、甘特使用后端 sortie_id、drone_id、battery_id 联动，UI 不计算业务能耗/SOC。

Mock 常驻提示，禁确认；null/未评估/失败分别显示。capabilities 没有的功能不假装可用，页面播放不写实际交付。先做 B-01/C-01 的契约类型与路由骨架，再接真实结果。当前无 package.json，不声称 build/typecheck 已通过。
