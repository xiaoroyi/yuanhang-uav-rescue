# B 的长期开发提示词｜React 前端、地图和比赛展示

> 本仓库适配说明：仅 A（算法/项目负责人）与 B（前端+后端+集成）两人。`C-*` 只保留为后端任务编号。原始 ZIP 留存于 `references/source/original-handoff.zip`。当前缺少旧版机器契约；新建 `0.1.0-draft` 仅为评审草案，状态见 `docs/DECISIONS.md`，不是已批准V1；当前已实现能力与实际API以docs/IMPLEMENTATION_STATUS.md、docs/SOLO_DELIVERY.md和实际OpenAPI为准。先核对候选分支与最新验收，不从G0重复搭建已有模块。

这是 B 的前端模块检查清单；B 同时负责后端，统一启动入口为 `prompts/02_SYSTEM_B.md`。你要把算法产生的真正计划和验证结果做成清晰可交互的应急调度工作台。不能在前端重新计算业务优化或造“实时算法结果”。

## 必读

`AGENTS.md`、`frontend/AGENTS.md`、`docs/CODEX_MASTER_HANDOFF.md`（特别是第 1/3/5/6/9/10/11 章）、`docs/INTEGRATION_PACT.md`、`docs/04-API-CONTRACT.md`、`contracts/` 和 `fixtures/`、`docs/08-TASK-BOARD.md`。

## 权限与开发模式

主要只改 `frontend/`；如要改 Schema/后端，请提交接口 RFC 给 B/A，不跨模块擅自修。技术栈默认 React + Vite + TypeScript strict + MapLibre；应用层服务按 OpenAPI 生成类型，UI 不直接拼后端路径。开发期 MockProvider 可以读取 `fixtures/`，但每个 Mock 页面必须明确标记“开发样例”，正式演示切换 HttpProvider，不能把回放称为当前求解。

## 全部功能（按任务依赖灵活完成）

1. 基础工程、路由、Design tokens、统一导航/提示/加载/错误态；专业简洁配色、布局兼容 1440×900/1280×720。
2. 页面一：创建/导入/编辑场景；模板与上传校验；基地/站点/需求/箱件/机型/机体/电池分类管理；点位 ↔ 表格高亮；地形/数据可用状态。
3. 页面二：调度工作台。真实 `Plan` 指标，地图实际 GeoJSON 航路、停靠、路线选择与资源联动；架次/箱件详情；Job queued/running/failed/completed/canceled 和错误解释。
4. 策略对比：同一快照下 time/energy，费用/均衡仅在后端 capabilities 和模型支持时启用；缺数据用 `—`，不要将 null 当 0。
5. 机体与电池甘特、充电/可用时间线；选中任意路线/箱件/资源互相高亮；中继机与能源组件时间轴在通信模块准备好后接入。
6. 页面三：事件上报、版本变化、故障机退出的前后方案、改派/延期/保留任务说明、资源增配 what-if、事件时间轴、计划回放。
7. P1 地图：GeoJSON 限制区绘制、DEM/GeoTIFF/正射图层、来源/有效期/NoData、通信保障来源及缺口；图层存在不等于安全已验证。
8. P2 地图影像建图进度、仿真遥测等扩展，由后端真实能力决定显示，不得先伪造服务状态。
9. 导出和可访问性：任务单/CSV/JSON/GeoJSON 按后台结果下载，防重复点击，保存筛选；无外网情况下核心底图/线路仍可展示。
10. 比赛输出：统一视觉素材、截图、演示视频、可选 PPT；展示真实交互和真实性标签。

## 阶段验收

- Mock Fixture 单独能渲染，但绝不能点击成“已验证可执行”；
- 用 B/A 的真实小场景 Plan 可以渲染同一架次在地图、任务表、机体甘特、电池甘特中精确联动；
- 事件后新旧计划 snapshot/version 不同，展示差异且旧结果不被覆盖；
- UNKNOWN/INFEASIBLE/ERROR/未检查/部分保障可被准确解释；
- 每次任务提交可复现 screenshot、构建命令、PASS/FAIL/未运行、接口变化需求。

首次开始先执行 B-01/B-02：基础工程、三页骨架、导入与 MockProvider；不要一口气生成全部图表代码。之后根据任务板继续做完所有可用功能。
