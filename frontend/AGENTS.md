# B 系统线前端模块

用户最新补充见docs/CONTRACT_RFC_016.md和STRATEGY_V2_RELEASE.md：现为九页，增加SchedulePage及schedule-data安排表/CSV/双资源时间轴；真实数据绑定Plan原Snapshot。新计算显式tradeoff_v2，历史缺省deadline_first_v1；策略配对按Snapshot和规则版本，三卡统一联合/运输范围。背景所有动画遵守开关/系统减少动态效果，不驱动业务时钟。

2026-10-18体验迭代将入口扩为8页：数据大屏、场景资源、地图地形、调度、对比、事件、历史、新手教程。分析/3D组件见VisualAnalysis与TerrainScene；只读高度/版本API来自生成OpenAPI，规则见RFC-015。三维视觉倍率、采样孔洞与路线地表投影不得冒充真实飞行；本机档案不是登录权限。卫星显式启用、默认无外网、失败降级，图层归属必须保留。优先读docs/EXPERIENCE_RELEASE.md查看本轮验证，不把下文历史“三页”目标当作当前只有三页。

与 backend owner 为同一位 B。遵守根 AGENTS，先读 docs/04、UI_ACCEPTANCE、总纲第6章。

三页 React/Vite/TypeScript strict 目标架构。API 入口集中，Mock/HTTP Provider 同类型，生成类型不手改。地图、表格、甘特使用后端 sortie_id、drone_id、battery_id 联动，UI 不计算业务能耗/SOC。

Mock 常驻提示，禁确认；null/未评估/失败分别显示。capabilities 没有的功能不假装可用，页面播放不写实际交付。

当前已有React/Vite应用、真实HTTP客户端、生成TS、三页、离线MapLibre、双甘特、策略与重规划。入口src/App.tsx，类型来自api/generated/http.d.ts。用npm.cmd run lint/build/test:unit；E2E由scripts/run-e2e.mjs启动隔离8011/5174，不使用演示数据库。进度与已知问题先读docs/IMPLEMENTATION_STATUS.md，不从G0历史描述重新建项目。目录src/lib/必须提交，不能被Python通用lib忽略规则漏掉。
