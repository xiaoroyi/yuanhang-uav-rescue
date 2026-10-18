# 全量任务板

由 `docs/task-board.json` 生成。两人：A 算法兼项目负责人，B 同一人负责前端、后端与集成。C-* 只是后端任务编号。

阶段表示依赖，不按日期排期。P0/P1/P2 全部保留；done 需要真实验收证据。当前用户已授权单人全栈实现分支，契约仍待团队复核；详见 SOLO_EXECUTION。

## G0

阶段状态：`awaiting_review`。

| ID | 优先级 | Owner | 依赖 | 任务与验收 | 状态 | 分支/PR/证据 |
|---|---|---|---|---|---|---|
| G0-01 | P0 | A+B | — | 检查现有仓库；列已存在文件、代码与测试，记录何处缺失；验收：`IMPLEMENTATION_STATUS.md` 有真实库存，未擅自覆盖 | done | docs/g0-governance; docs/G0_REPORT.md |
| G0-02 | P0 | A+B | G0-01 | 确认 AGENTS、模块 owner、Git PR 规则、决定日志；验收：两人各自 Codex 阅读相同文件，改变规则须 PR | done | docs/g0-governance; docs/G0_REPORT.md |
| G0-03 | P0 | A+B | G0-01 | 评审并冻结首次Scenario/Plan/Event/SolveJob及Python options/outcome契约；验收：schema/fixtures 校验绿；无歧义单位与状态；当前草案通过结构检查，待 A/B 人工确认冻结 | in_progress | docs/g0-governance; docs/G0_REPORT.md |
| G0-04 | P0 | A+B | G0-03 | 确认 `/api/v1` OpenAPI、错误状态、前端 TS 生成方式；验收：已有真实FastAPI OpenAPI、生成Pydantic/TS、success/failure回归和CI漂移检查；正式接口冻结仍待A/B人工复核 | in_progress | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; contracts/http/openapi.generated.json; backend/app/generated/domain.py; frontend/src/api/generated/http.d.ts; evidence/verification/github-ci.json |
| G0-05 | P0 | A | G0-01 | 排查原数模完整入口、数据/依赖许可及可跑程度；验收：原件hash和18份源码AST通过；G0时旧环境缺6个业务包，旧路径与许可证待核验；当前项目依赖已独立安装锁定，适配实跑归A-01，仍不执行历史bootstrap/env | done | docs/g0-governance; docs/LEGACY_BASELINE_AUDIT.md; evidence/governance/legacy-audit.json |
| G0-06 | P0 | B | G0-01 | 确定页面结构、Design Tokens、三页验收流程；验收：页面清单每项有数据源、状态和交互目标 | done | docs/g0-governance; docs/G0_REPORT.md |
| G0-07 | P0 | A+B | G0-03 | CI 契约校验、lint、pytest、前端 build 基础；验收：CI契约、pytest、lint、strict/build、生成类型漂移和两条新浏览器烟测已实际运行；正式契约冻结独立待A/B评审。 | done | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; evidence/verification/github-ci-3a8b8b6.json; evidence/verification/github-browser-smoke-3a8b8b6-39086236549.json; evidence/verification/latest.json |

## G1

阶段状态：`core_verified`。

| ID | 优先级 | Owner | 依赖 | 任务与验收 | 状态 | 分支/PR/证据 |
|---|---|---|---|---|---|---|
| A-01 | P0 | A | G0-03, G0-05 | 原题 Q1/Q2 物理与装载适配，纯 Python 入口；验收：非Mock运输真实运行；额定单点能力/整箱DP诊断独立复算，原题80箱18批，严格30%余量20批；诊断不冒充实体Plan | done | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; evidence/solver/first-compact.json; solver/physics.py; solver/nominal.py; docs/NOMINAL_ANALYSIS.md; evidence/solver/nominal-contest.json; evidence/browser/nominal-diagnostic.json; tests/solver/test_nominal.py |
| A-02 | P0 | A | A-01, G0-03 | 机体/电池快速可行初解、时间限制与独立检查；验收：Plan 含逐箱、逐机、电池、验证与约束口径 | done | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; tests/solver/test_solver.py; evidence/solver/first-contest.json |
| C-01 | P0 | B | G0-03, G0-04 | JSON/CSV 场景导入、Pydantic 语义校验、业务错误；验收：JSON/CSV/XLSX预览、字段/行错误、Pydantic语义校验、重复引用和版本冲突均有真实API/浏览器验收；复杂自定义映射属C-06后续范围。 | done | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; tests/backend/test_imports.py; frontend/tests/workflow.spec.ts; evidence/verification/latest.json |
| C-02 | P0 | B | C-01 | state_version、不可变 snapshot/hash、SQLite；验收：编辑后旧 Snapshot 不变 | done | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; tests/backend/test_api.py |
| C-03 | P0 | B | A-02, C-02 | 独立 Worker 调 solve/validate，Job 轮询、保存历史 Plan；提供 X-01 所需最小 JSON/CSV/GeoJSON 导出；验收：从 HTTP 得到真实验算 Plan，无请求阻塞 | done | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; tests/backend/test_api.py |
| B-01 | P0 | B | G0-03, G0-04, G0-06 | 前端基建与三页路由、API Provider 与 Mock 分离；验收：Mock 明显提示，正式接口切换无大改 | done | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; frontend/src/App.tsx; frontend/playwright.config.ts |
| B-02 | P0 | B | B-01, C-01 | 场景导入/资源/需求表与地图点位联动；验收：场景导入、六类表格编辑、地图点位定位与版本变更已实际验证；更换输入后重新求解。 | done | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; frontend/src/pages/ScenarioEditor.tsx; frontend/tests/workflow.spec.ts; evidence/browser/verified/scenario-with-nominal-1440.png |
| B-03 | P0 | B | B-01, C-03 | 地图/架次表/摘要指标、真实 Job 状态；验收：用同一 sortie_id 联动，不二次估能耗 | done | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; frontend/tests/workflow.spec.ts; evidence/browser/e2e-results.json |
| X-01 | P0 | A+B | A-02, C-03, B-03 | 首个端到端验收：新数据→真实 Plan→地图→导出；验收：E2E 记录+请求/响应+Git SHA，Mock 不计 | done | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; docs/CHECKPOINT_001.md; evidence/browser/e2e-results.json |
| R00 | P0 | A+B | — | 仓库、截图和能力审计；验收：文件树、实际技术栈、现有入口、已运行测试、功能状态、风险；保留未提交修改 | done | feat/mission-workspace-v2; evidence/redesign-v2/REPO_AUDIT.md |
| R01 | P0 | A+B | R00 | 接口迁移与模型边界；验收：API_MIGRATION_MAP、Mission/Execution 等新增契约、样例及兼容测试；不改旧字段含义 | in_progress | feat/mission-workspace-v2; evidence/redesign-v2/HANDOFF.md; evidence/redesign-v2/FEATURE_TRACEABILITY.md |
| R02 | P0 | A+B | R00 | 设计系统与导航壳；验收：4 个主导航、首页入口、任务页签、tokens、受控滚动、响应式壳；移除业务口号 | in_progress | feat/mission-workspace-v2; evidence/redesign-v2/HANDOFF.md; evidence/redesign-v2/FEATURE_TRACEABILITY.md |
| R03 | P0 | A+B | R01, R02 | 首页和任务管理；验收：创建、继续、复制、搜索、归档、示例演练；不复制实际执行事实 | in_progress | feat/mission-workspace-v2; evidence/redesign-v2/HANDOFF.md; evidence/redesign-v2/FEATURE_TRACEABILITY.md |
| R04 | P0 | A+B | R01, R02 | 任务准备流程；验收：区域/基地、需求/库存、机队/保障、条件检查 4 步；草稿保存与修复定位 | in_progress | feat/mission-workspace-v2; evidence/redesign-v2/HANDOFF.md; evidence/redesign-v2/FEATURE_TRACEABILITY.md |
| R05 | P0 | A+B | R01, R04 | 条件检查服务与界面；验收：planning/execution 检查报告、必检范围、未知/失败/提醒分开；能一键定位问题 | in_progress | feat/mission-workspace-v2; evidence/redesign-v2/HANDOFF.md; evidence/redesign-v2/FEATURE_TRACEABILITY.md |
| R06 | P0 | A+B | R01, R02 | 统一地图与空间资产；验收：真正交互地图、图层、紧凑标签、选中联动、CRS/DEM/离线、限制区编辑和缓存失效 | in_progress | feat/mission-workspace-v2; evidence/redesign-v2/HANDOFF.md; evidence/redesign-v2/FEATURE_TRACEABILITY.md |
| R07 | P0 | A+B | R01, R04 | Solver 适配和计算作业；验收：原算法回归、实际新输入计算、限时/取消、候选、错误语义、独立验证 | in_progress | feat/mission-workspace-v2; evidence/redesign-v2/HANDOFF.md; evidence/redesign-v2/FEATURE_TRACEABILITY.md |
| R08 | P0 | A+B | R06, R07 | 结果数据与分析图；验收：同源 PlanAnalysis、V01—V09、单位和阶段一致；逐箱/机体/电池追踪 | in_progress | feat/mission-workspace-v2; evidence/redesign-v2/HANDOFF.md; evidence/redesign-v2/FEATURE_TRACEABILITY.md |
| R09 | P0 | A+B | R02, R05, R06, R07, R08 | 方案工作台与确认；验收：地图主视图、任务表、资源甘特、比较、确认/导出；同条件与事件差异分开 | in_progress | feat/mission-workspace-v2; evidence/redesign-v2/HANDOFF.md; evidence/redesign-v2/FEATURE_TRACEABILITY.md |

## G2

阶段状态：`core_verified`。

| ID | 优先级 | Owner | 依赖 | 任务与验收 | 状态 | 分支/PR/证据 |
|---|---|---|---|---|---|---|
| A-03 | P0 | A | A-02 | `time`/`energy` 两策略、硬截止与统一保障要求；验收：同 Snapshot 两次真实计算，指标口径一致 | done | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; tests/solver/test_solver.py; evidence/browser/e2e-results.json |
| A-04 | P0 | A | A-02 | 电池两段充电、逐实体释放时刻、甘特占用验证；验收：不重复占用，充电后再复用 | done | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; tests/solver/test_solver.py; docs/GROUND_RESOURCES.md; tests/solver/test_ground.py; evidence/solver/ground-deep-compact.json |
| C-04 | P0 | B | C-03, A-03 | 方案版本、比较、计划确认事务、冲突码；验收：过期/Mock/验证失败都无法确认 | done | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; tests/backend/test_api.py; tests/backend/test_ground_api.py; docs/GROUND_RESOURCES.md |
| B-04 | P0 | B | B-03, A-04 | 机体+电池甘特、资源/架次联动、方案比较卡；验收：相同方案也诚实显示，不造差异 | done | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; frontend/src/components/ResourceTimeline.tsx; evidence/browser/e2e-results.json; docs/GROUND_RESOURCES.md; evidence/browser/verified/ground-calendars-1440.png |
| X-02 | P0 | A+B | A-03, A-04, C-04, B-04 | 资源/时间验收（重叠、硬截止、空值显示、费用禁用）；验收：自动化负例全部通过 | done | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; tests/solver/test_solver.py; tests/backend/test_api.py |

## G3

阶段状态：`core_verified`。

| ID | 优先级 | Owner | 依赖 | 任务与验收 | 状态 | 分支/PR/证据 |
|---|---|---|---|---|---|---|
| C-05 | P0 | B | C-02 | 事件幂等、事件时刻/版本、状态更新与新 Snapshot；验收：event_id 重试只有一次状态变化 | done | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; tests/backend/test_api.py |
| A-05 | P0 | A | A-02, C-05 | 尚未起飞机体退出→replan；保留旧版本及已执行事实；验收：无故障机未来架次、前后验证均通过 | done | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; tests/backend/test_api.py; evidence/browser/e2e-results.json |
| A-06 | P0 | A | A-05 | 依赖图传播、变更代价、限时修复/全量回退；验收：输出 changed/preserved，可对照修复范围 | done | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; docs/CHECKPOINT_001.md; evidence/browser/e2e-results.json; evidence/solver/replan-comparison.json |
| B-05 | P0 | B | B-04, C-05 | 事件输入、旧新地图叠加、差异清单、时间轴；验收：可清楚定位受影响任务和未完成原因 | done | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; evidence/browser/e2e-results.json |
| X-03 | P0 | A+B | A-05, A-06, C-05, B-05, X-02 | 事件端到端：原计划→事件→新快照→重算→复盘；验收：旧 Plan 未覆盖，重复事件不重复预约 | done | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; docs/CHECKPOINT_001.md; evidence/browser/e2e-results.json |
| R10 | P0 | A+B | R01, R09 | 服务器业务仿真与回放；验收：独立执行实例/时钟/账本，开始暂停倍速恢复，刷新不丢进度；回放不改事实 | in_progress | feat/mission-workspace-v2; evidence/redesign-v2/HANDOFF.md; evidence/redesign-v2/FEATURE_TRACEABILITY.md |
| R11 | P0 | A+B | R01, R10 | 遥测和设备适配合同；验收：SimulationAdapter、能力查询、指令状态、断线/重连；SITL 接入按环境验证 | in_progress | feat/mission-workspace-v2; evidence/redesign-v2/HANDOFF.md; evidence/redesign-v2/FEATURE_TRACEABILITY.md |
| R12 | P0 | A+B | R07, R10, R11 | 执行中事件与计划变更；验收：已装载/在飞事实冻结、依赖影响、真实重算、差异确认、分设备应用及失败状态 | in_progress | feat/mission-workspace-v2; evidence/redesign-v2/HANDOFF.md; evidence/redesign-v2/FEATURE_TRACEABILITY.md |

## G4

阶段状态：`in_progress`。

| ID | 优先级 | Owner | 依赖 | 任务与验收 | 状态 | 分支/PR/证据 |
|---|---|---|---|---|---|---|
| C-06 | P1 | B | C-01, X-01 | CSV/Excel 映射模板、GeoJSON/GeoTIFF/DEM 资产导入与预处理队列；验收：文件来源与 CRS、有效覆盖、版本可追溯 | in_progress | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; docs/IMPLEMENTATION_STATUS.md; docs/SPATIAL_ROUTING.md; tests/backend/test_spatial.py; evidence/browser/verified/zone-detour-1440.png; docs/TERRAIN_ASSETS.md; tests/backend/test_terrain_assets.py; evidence/browser/verified/terrain-assets-1440.png |
| B-06 | P1 | B | C-06 | 地形/禁入/洪水/通信图层与绘制工具；验收：标注效果与约束校验分开展示 | in_progress | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; docs/IMPLEMENTATION_STATUS.md; docs/SPATIAL_ROUTING.md; tests/backend/test_spatial.py; evidence/browser/verified/zone-detour-1440.png; docs/TERRAIN_ASSETS.md; tests/backend/test_terrain_assets.py; evidence/browser/verified/terrain-assets-1440.png |
| A-07 | P1 | A | A-02, C-06 | 绕行候选 A* 或可见图、净空预检、缓存键与失效；验收：禁入更新后候选重算且有验证 | done | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; docs/SPATIAL_ROUTING.md; solver/routing.py; tests/solver/test_routing.py; evidence/solver/zone-compact.json |
| A-08 | P1 | A | A-02, G0-03 | Q3 中继/两跳链路与时间窗/能源组件完整建模；验收：启用强制通信时无空白认证 | done | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; docs/COMMUNICATION.md; solver/joint.py; tests/solver/test_radio.py; evidence/solver/joint-compact.json; evidence/solver/joint-contest.json; tests/solver/test_joint_patterns.py; evidence/solver/joint-contest-recomputed.json; evidence/solver/joint-replan.json |
| C-07 | P1 | B | A-08 | 中继资源、传播参数、通信检查结果持久化与 API 升级；验收：协议扩展通过版本迁移测试 | done | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; docs/CONTRACT_RFC_006.md; tests/backend/test_joint_api.py; contracts/http/openapi.generated.json |
| B-07 | P1 | B | C-07 | 中继点/服务时间轴、通信来源与缺口高亮；验收：已有通信窗口来源表、链路实体、历史Snapshot参数和地图联动、JSON导出；精确缺口几何/更多图层未由契约提供，仍保留后续。 | in_progress | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; frontend/src/components/CommunicationPanel.tsx; evidence/browser/verified/joint-workspace-1440.png; evidence/browser/e2e-results.json |
| A-09 | P1 | A | A-04, X-02 | 充电端口、起降位与地面工位容量约束；验收：有限准备工位/充电端口、等待与补能、独立容量检查及增配情景已实现；起降坪容量仍未建模，保留部分实现状态。 | in_progress | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; docs/GROUND_RESOURCES.md; tests/solver/test_ground.py; docs/CONTRACT_RFC_014.md; tests/backend/test_analytics.py; evidence/browser/ground-capacity-trial.json; evidence/verification/ground-rfc014.json |
| A-10 | P1 | A | A-05, A-07, C-05 | 电池退出、紧急插单、落点变更、未来封控事件；验收：已实现整个场景未执行时机体/运输电池/中继能源退出、已有点位新增需求+库存，真实新版本重规划；在途/落点/未来封控及执行事实仍待升级。 | in_progress | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; docs/CONTRACT_RFC_010.md; tests/backend/test_battery_events.py; tests/solver/test_battery_event.py; evidence/solver/battery-replan.json; evidence/solver/joint-battery-replan.json; docs/CONTRACT_RFC_012.md; tests/backend/test_demand_events.py; tests/solver/test_demand_event.py; evidence/browser/urgent-demand.json; docs/CONTRACT_RFC_013.md; tests/backend/test_relay_energy_events.py; evidence/solver/relay-energy-replan.json |
| C-08 | P1 | B | A-10, C-05 | 地图/资源新增事件 API 与一致性事务；验收：零时刻严格Event联合、幂等、版本事务、退出与紧急插单/库存已实现；执行中状态与更多未来事件未实现。 | in_progress | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; docs/CONTRACT_RFC_010.md; tests/backend/test_battery_events.py; tests/solver/test_battery_event.py; evidence/solver/battery-replan.json; evidence/solver/joint-battery-replan.json; docs/CONTRACT_RFC_012.md; tests/backend/test_demand_events.py; tests/solver/test_demand_event.py; evidence/browser/urgent-demand.json; docs/CONTRACT_RFC_013.md; tests/backend/test_relay_energy_events.py; evidence/solver/relay-energy-replan.json |
| B-08 | P1 | B | A-10, C-08 | 动态图层与复盘/故障明细页面；验收：失败、未评估、已验证状态可区分 | in_progress | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; evidence/solver/joint-replan.json; frontend/tests/workflow.spec.ts |
| A-11 | P1 | A | A-03, A-07, A-08 | 部分保障、资源缺口/增配试算、可证明下界；验收：已实现机体/电池/准备工位/充电端口真实试算和运输架次容量必要下界；部分保障及可证明最少增配仍待深化。 | in_progress | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; docs/RESOURCE_ANALYSIS.md; tests/backend/test_analytics.py; evidence/browser/e2e-results.json; docs/CAPACITY_BOUNDS.md; tests/solver/test_bounds.py; tests/backend/test_capacity_bound_api.py; evidence/browser/capacity-bound.json; docs/CONTRACT_RFC_014.md; evidence/browser/ground-capacity-trial.json; evidence/verification/ground-rfc014.json |
| A-12 | P1 | A | A-08 | Q4 冻结任务分区、资源峰值与共享损失；验收：分区不冒用可重新分配时的全局最优性 | done | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; docs/FROZEN_PARTITION.md; docs/CONTRACT_RFC_007.md; tests/solver/test_partition.py; tests/backend/test_partition_api.py; evidence/solver/frozen-partition-contest.json; evidence/browser/verified/frozen-partition-1440.png |
| C-09 | P1 | B | A-11, C-04 | 资源增配情景 API，独立分叉快照与打印/导出；验收：增配单独建新场景/快照并真实求解 | done | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; docs/RESOURCE_ANALYSIS.md; tests/backend/test_analytics.py; evidence/browser/e2e-results.json; evidence/browser/print-report-qa.json |
| B-09 | P1 | B | C-09, B-05 | 资源增配前端比较与打印任务单；验收：增配单独建新场景/快照并真实求解 | done | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; docs/RESOURCE_ANALYSIS.md; tests/backend/test_analytics.py; evidence/browser/e2e-results.json; evidence/browser/print-report-qa.json |
| R13 | P1 | A+B | R06, R07, R08 | 通信中继与连续验证；验收：直连与接入/回传、窗口、组件、通信时间轴与剖面；明确连续/采样边界 | in_progress | feat/mission-workspace-v2; evidence/redesign-v2/HANDOFF.md; evidence/redesign-v2/FEATURE_TRACEABILITY.md |
| R14 | P1 | A+B | R01, R05, R07 | 气象、现实电量和地面保障；验收：手工/预报适配、数据年龄、机型阈值、SOC/容量定义、充电端口/起降与装卸能力 | todo | feat/mission-workspace-v2 |
| R15 | P1 | A+B | R08, R12, R13, R14 | 条件变化有效性与增配诊断；验收：I1—I3 可操作界面、受影响对象、真实 what-if 计算、保留原 Plan | in_progress | feat/mission-workspace-v2; evidence/redesign-v2/HANDOFF.md; evidence/redesign-v2/FEATURE_TRACEABILITY.md |
| R16 | P1 | A+B | R07, R10, R12 | 演练评测与算法消融；验收：从 UI 运行场景/事件/方法对比；预算/种子/日志/失败记录；研究功能独立 | in_progress | feat/mission-workspace-v2; evidence/redesign-v2/HANDOFF.md; evidence/redesign-v2/FEATURE_TRACEABILITY.md |

## G5

阶段状态：`in_progress`。

| ID | 优先级 | Owner | 依赖 | 任务与验收 | 状态 | 分支/PR/证据 |
|---|---|---|---|---|---|---|
| A-13 | P1 | A | A-07, A-08, A-09 | 能耗/时间/通信情景压力；多情景优化/风险指标；验收：同数据同预算对照，情景说明清楚 | in_progress | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; docs/RESOURCE_ANALYSIS.md; tests/backend/test_analytics.py; evidence/browser/e2e-results.json |
| A-14 | P2 | A | A-06, A-13 | 学习辅助邻域算子；训练集、种子、无泄漏划分；验收：随机/规则/学习同预算消融与泛化实验；真实数据/日志资格门槛不满足则记录 blocked，不伪造训练或精度 | todo | — |
| A-15 | P2 | A | A-13 | 有真实日志后物理+学习能耗误差补偿；验收：训练/校准/独立测试，不能从模拟宣称真机精度；真实数据/日志资格门槛不满足则记录 blocked，不伪造训练或精度 | todo | — |
| C-10 | P2 | B | C-06 | ODM/NodeODM 航摄影像异步建图/质量审批；验收：产生版本化地图，不自动进入安全计算 | todo | — |
| B-10 | P2 | B | C-10 | 地图资产处理进度、审批、正射/地形版本比较；验收：数据新鲜度与限制清晰可见 | todo | — |
| C-11 | P2 | B | X-03, C-07 | PX4 SITL/MAVSDK 仿真适配（可选）；验收：仅宣称仿真任务支持与明确指令子集 | todo | — |
| X-12 | P2 | A+B | X-03, A-07, A-08, C-07 | 多基地、移动补给/补能、跨机构权限与审计；分别拆子任务，全部保留为P2；验收：新约束、输入契约、行为验证独立立项 | todo | — |

## G6

阶段状态：`in_progress`。

| ID | 优先级 | Owner | 依赖 | 任务与验收 | 状态 | 分支/PR/证据 |
|---|---|---|---|---|---|---|
| Q-01 | P0 | A | A-02, A-08, A-12 | 原题回归：Q1 18架次、Q2 23架次/时间/能耗、Q3 运输+中继基准作结构/约束核查；验收：版本、输入、模型口径、预算一致；不强制相同的可行分配序列 | in_progress | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; docs/IMPLEMENTATION_STATUS.md |
| Q-02 | P0 | A | A-06, A-13 | 多场景/多随机种子、算法 baseline、动态全量/局部对照、消融与性能；验收：`evidence/` 保存数据 hash、commit、配置、原始运行记录 | in_progress | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; docs/IMPLEMENTATION_STATUS.md |
| Q-03 | P0 | B | C-03, C-04, C-05 | 自动契约/数据库/HTTP/并发/重启/导出/离线/安全测试；验收：实际Linux CI与本机完整业务/数据库/HTTP/队列取消恢复/导出/离线/上传负例检查通过；命令和范围按对应提交记录。 | done | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; evidence/verification/latest.json; evidence/verification/github-ci-3a8b8b6.json; evidence/browser/production-offline.json; evidence/engineering/backup-smoke.json |
| Q-04 | P0 | B | B-03, B-04, B-05 | UI 交互/响应/颜色可读性/异常态/地图离线显示；验收：实际操作及截图覆盖1440×900、1280×720、390宽窄屏、异常/历史快照重试和离线地图；不是只验证页面可打开。 | done | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; evidence/browser/e2e-results.json; evidence/browser/verified/workspace-1440.png; evidence/browser/production-offline.json |
| Q-05 | P0 | A+B | X-01, X-02, X-03, Q-03, Q-04 | 端到端回归脚本与最小真实演示包；验收：任一队友可重新安装并完成全部关键流程 | in_progress | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; docs/IMPLEMENTATION_STATUS.md |
| S-01 | P0 | B | X-01 | 项目简表（官方模板）和项目说明书；验收：通用操作说明与演示稿已生成，来源hash可复核；官方项目简表/完整模板适配仍待提供赛事材料，不冒充正式提交件 | in_progress | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; docs/DEMO_RUNBOOK.md; docs/DEMO_SCRIPT.md; deliverables/README.md; deliverables/yuanhang-demo.html; deliverables/yuanhang-demo.pdf; evidence/demo/manifest.json; evidence/demo/pdf-qa.json |
| S-02 | P0 | B | X-03 | 演示视频、系统截图、答辩 PPT（可选但建议）；验收：真实系统截图、15页离线HTML/PDF演示稿逐页检查通过；70.52秒实际操作录像含12章中文字幕，实际解码、字幕/跳转和6处画面检查通过。PPTX仍因官方artifact-tool运行时缺失未导出，正式官方模板未核验，故整卡保持部分完成。 | in_progress | feat/solo-fullstack-v0; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; docs/DEMO_RUNBOOK.md; docs/DEMO_SCRIPT.md; deliverables/README.md; deliverables/yuanhang-demo.html; deliverables/yuanhang-demo.pdf; evidence/demo/manifest.json; evidence/demo/pdf-qa.json; deliverables/walkthrough.html; deliverables/yuanhang-walkthrough.webm; deliverables/yuanhang-walkthrough.zh.vtt; evidence/video/recording.json; evidence/video/playback-qa.json |
| S-03 | P0 | B | — | 商业计划书（可选）、竞品对比/用户访谈；验收：实际验证与假设分开，无虚构合同/收入 | todo | — |
| S-04 | P0 | A+B | S-01, Q-05 | 匿名、许可证、原创新增贡献、源代码与原型证明；取得官方指南/模板与最新通知，核对截止及复用条款；验收：不透露培养单位/导师/身份信息，除官方必须实名栏目 | todo | — |
| UX-01 | P0 | B | Q-04 | 夜蓝/浅色视觉体系、动态背景与本机档案；验收：主题和动态偏好可持久化；档案修改/刷新/坏JSON/跨标签同步；手机导航可关闭且姓名可读 | done | feat/experience-v1; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; evidence/experience/onboarding/browser-qa.json; evidence/experience/onboarding/navigation-versions-final.json |
| UX-02 | P0 | B | Q-04 | 真实地图、地形导入与离线地理背景；验收：独立地图入口；真实GeoTIFF/包绑定、覆盖统计、原题道路水系村镇边界来源；卫星显式启用与失败降级，不批量缓存 | done | feat/experience-v1; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; evidence/experience/map/context-source.json; evidence/experience/map/context-browser-check.json |
| UX-03 | P0 | B | Q-04 | 真实DEM三维与高度/能源数据大屏；验收：原Snapshot与资产绑定，NoData孔洞、真实航段高度与能耗分解；八图六KPI综合看板、精确数据、全屏与小屏/WebGL降级 | done | feat/experience-v1; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; evidence/experience/analysis/overview-qa.json; evidence/experience/analysis/flight-profile-responses.json; evidence/experience/analysis/fallback-qa.json; evidence/experience/final-review/analysis-review.json; frontend/tests/chart-null.spec.ts; evidence/experience/production/visual-review.json |
| UX-04 | P0 | B | Q-04 | 历史档案、输入版本与方案比较；验收：真实Plan/Job/Event/版本可查；旧版本只读预览下载；同快照可比性、交换、时间/能量分轴和延期指标，历史选择刷新保留 | done | feat/experience-v1; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; frontend/tests/experience.spec.ts; tests/backend/test_scenario_versions.py; evidence/experience/onboarding/comparison-export.json |
| UX-05 | P0 | B | Q-04 | 新手教程与创新能力说明；验收：六步跳转、地图数据区别、FAQ搜索与键盘可达；创新点标明当前依据和边界，不伪造优越性/实飞能力 | done | feat/experience-v1; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; frontend/src/pages/GuidePage.tsx; evidence/experience/onboarding/browser-qa.json |
| UX-06 | P0 | B | Q-04 | 体验迭代的完整集成回归；验收：新专项与原工作流统一回归；实际生成接口类型无漂移；固定源码指纹、截图、可用启动和远端CI分别留证 | done | feat/experience-v1; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; frontend/tests/experience.spec.ts; docs/EXPERIENCE_RELEASE.md; evidence/experience/qa-finish/results.json; evidence/experience/release-audit.json; evidence/experience/production/browser-check.json; evidence/verification/latest.json; evidence/browser/e2e-results.json; evidence/experience/handoff-audit.json |
| UX-07 | P0 | B | Q-04 | 地图/论文追溯与候选版本交接；验收：只读参考论文图形语义，当前图只用真实输入结果；明确卫星联网限制/未知日期、旧材料归档、两人交接与剩余范围 | done | feat/experience-v1; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; docs/CONTRACT_RFC_015.md; docs/EXPERIENCE_RELEASE.md; evidence/experience/map/source-review.json |
| FIX-01 | P0 | A+B | UX-06 | 版本化策略取舍、动态背景与调度安排；验收：保留期限/硬约束的真实三策略，旧规则兼容，统一联合口径，明确相同结果，调度表/箱件/资源时间轴与背景开关真实验收 | done | feat/experience-v1; https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1; docs/CONTRACT_RFC_016.md; docs/STRATEGY_V2_RELEASE.md; tests/solver/test_strategy_policy.py; frontend/src/pages/SchedulePage.tsx; frontend/tests/strategy-manifest.spec.ts; evidence/verification/latest.json; evidence/strategy-v2/final-verification.json; evidence/strategy-v2/final-browser.json; evidence/strategy-v2/production-service.json; evidence/strategy-v2/production-browser.json; evidence/strategy-v2/trial-policy-v1.json; evidence/strategy-v2/trial-policy-v2.json |
| R17 | P1 | A+B | R08, R10, R12 | 复盘、档案与导出；验收：计划/模拟/实况分开、轨迹/服务/能源/通信分析、可重载任务包 | in_progress | feat/mission-workspace-v2; evidence/redesign-v2/HANDOFF.md; evidence/redesign-v2/FEATURE_TRACEABILITY.md |
| R18 | P1 | A+B | R06, R09, R10 | 离线、性能与异常降级；验收：授权地图包、字体图标本地化、无网/无 WebGL 降级、订阅清理和任务限流 | in_progress | feat/mission-workspace-v2; evidence/redesign-v2/HANDOFF.md; evidence/redesign-v2/FEATURE_TRACEABILITY.md |
| R19 | P1 | A+B | R01, R11 | 安全、隐私与权限；验收：模式隔离、认证、指令审批/幂等/TTL、敏感信息与 XSS/上传路径防护 | in_progress | feat/mission-workspace-v2; evidence/redesign-v2/HANDOFF.md; evidence/redesign-v2/FEATURE_TRACEABILITY.md |
| R20 | P1 | A+B | R03, R04, R05, R06, R07, R08, R09, R10, R11, R12, R13, R14, R15, R16, R17, R18, R19 | 全流程和视觉验收；验收：真实浏览器操作、指定尺寸截图、数据/日志、失败态测试、重复运行 | in_progress | feat/mission-workspace-v2; evidence/redesign-v2/HANDOFF.md; evidence/redesign-v2/FEATURE_TRACEABILITY.md |
| R21 | P1 | A+B | R16, R17, R20 | 演示与参赛交付；验收：项目说明书实况更新、真实图表、视频/PPT素材、运行包、许可/匿名检查 | todo | feat/mission-workspace-v2 |
| R22 | P2 | A | R16 | 学习辅助搜索；验收：规则基线、训练/测试隔离、消融、开销；无证据不显示 AI 成功 | todo | feat/mission-workspace-v2 |
| R23 | P2 | A+B | R06 | 影像测绘与高级三维；验收：ODM 异步处理、质量确认；必要时 Cesium 的真三维剖面与轨迹 | todo | feat/mission-workspace-v2 |
| R24 | P2 | A+B | R01, R12, R14, R19 | 多基地/移动补能/协作扩展；验收：真实模型与跨任务预约检查，不止配置表单 | todo | feat/mission-workspace-v2 |

## 当前执行入口

- 当前 V2 入口为 evidence/redesign-v2/INDEX.md，分支 feat/mission-workspace-v2；旧发布证据只代表对应历史版本。
- 优先完成当前 in_progress 任务的剩余验收，再推进下一项依赖。不同任务的部分实现不能自动算 done。
- 两人接手前共同复核 RFC-001/RFC-002、现有运行接口、测试证据和 Git 差异；不伪造契约批准记录。
