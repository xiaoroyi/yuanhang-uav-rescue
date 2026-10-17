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
| G0-04 | P0 | A+B | G0-03 | 确认 `/api/v1` OpenAPI、错误状态、前端 TS 生成方式；验收：`contracts tests` 覆盖 success/failure 样例；当前仅 HTTP 设计草案，真实生成类型与 OpenAPI 未具备 | in_progress | docs/g0-governance; docs/G0_REPORT.md |
| G0-05 | P0 | A | G0-01 | 排查原数模完整入口、数据/依赖许可及可跑程度；验收：原件hash和18份源码AST通过；实际依赖探测缺6个业务包，明确旧路径与许可证待核验，当前不可直接运行；适配实跑归A-01，不宣称已跑通 | done | docs/g0-governance; docs/LEGACY_BASELINE_AUDIT.md; evidence/governance/legacy-audit.json |
| G0-06 | P0 | B | G0-01 | 确定页面结构、Design Tokens、三页验收流程；验收：页面清单每项有数据源、状态和交互目标 | done | docs/g0-governance; docs/G0_REPORT.md |
| G0-07 | P0 | A+B | G0-03 | CI 契约校验、lint、pytest、前端 build 基础；验收：最小样例脚本本地和 CI 执行一致；当前有 CI 配置与本地检查，远程 CI 待实际运行 | in_progress | docs/g0-governance; docs/G0_REPORT.md |

## G1

阶段状态：`core_verified`。

| ID | 优先级 | Owner | 依赖 | 任务与验收 | 状态 | 分支/PR/证据 |
|---|---|---|---|---|---|---|
| A-01 | P0 | A | G0-03, G0-05 | 原题 Q1/Q2 物理与装载适配，纯 Python 入口；验收：非 Mock 小场景真实运行 | done | feat/solo-fullstack-v0; evidence/solver/first-compact.json; solver/physics.py |
| A-02 | P0 | A | A-01, G0-03 | 机体/电池快速可行初解、时间限制与独立检查；验收：Plan 含逐箱、逐机、电池、验证与约束口径 | done | feat/solo-fullstack-v0; tests/solver/test_solver.py; evidence/solver/first-contest.json |
| C-01 | P0 | B | G0-03, G0-04 | JSON/CSV 场景导入、Pydantic 语义校验、业务错误；验收：更换场景不用改源码；逐行错误可见 | in_progress | feat/solo-fullstack-v0; docs/IMPLEMENTATION_STATUS.md |
| C-02 | P0 | B | C-01 | state_version、不可变 snapshot/hash、SQLite；验收：编辑后旧 Snapshot 不变 | done | feat/solo-fullstack-v0; tests/backend/test_api.py |
| C-03 | P0 | B | A-02, C-02 | 独立 Worker 调 solve/validate，Job 轮询、保存历史 Plan；提供 X-01 所需最小 JSON/CSV/GeoJSON 导出；验收：从 HTTP 得到真实验算 Plan，无请求阻塞 | done | feat/solo-fullstack-v0; tests/backend/test_api.py |
| B-01 | P0 | B | G0-03, G0-04, G0-06 | 前端基建与三页路由、API Provider 与 Mock 分离；验收：Mock 明显提示，正式接口切换无大改 | done | feat/solo-fullstack-v0; frontend/src/App.tsx; frontend/playwright.config.ts |
| B-02 | P0 | B | B-01, C-01 | 场景导入/资源/需求表与地图点位联动；验收：用户编辑看得到版本变更 | in_progress | feat/solo-fullstack-v0; docs/IMPLEMENTATION_STATUS.md |
| B-03 | P0 | B | B-01, C-03 | 地图/架次表/摘要指标、真实 Job 状态；验收：用同一 sortie_id 联动，不二次估能耗 | done | feat/solo-fullstack-v0; frontend/tests/workflow.spec.ts; evidence/browser/e2e-results.json |
| X-01 | P0 | A+B | A-02, C-03, B-03 | 首个端到端验收：新数据→真实 Plan→地图→导出；验收：E2E 记录+请求/响应+Git SHA，Mock 不计 | done | feat/solo-fullstack-v0; docs/CHECKPOINT_001.md; evidence/browser/e2e-results.json |

## G2

阶段状态：`core_verified`。

| ID | 优先级 | Owner | 依赖 | 任务与验收 | 状态 | 分支/PR/证据 |
|---|---|---|---|---|---|---|
| A-03 | P0 | A | A-02 | `time`/`energy` 两策略、硬截止与统一保障要求；验收：同 Snapshot 两次真实计算，指标口径一致 | done | feat/solo-fullstack-v0; tests/solver/test_solver.py; evidence/browser/e2e-results.json |
| A-04 | P0 | A | A-02 | 电池两段充电、逐实体释放时刻、甘特占用验证；验收：不重复占用，充电后再复用 | done | feat/solo-fullstack-v0; tests/solver/test_solver.py |
| C-04 | P0 | B | C-03, A-03 | 方案版本、比较、计划确认事务、冲突码；验收：过期/Mock/验证失败都无法确认 | done | feat/solo-fullstack-v0; tests/backend/test_api.py |
| B-04 | P0 | B | B-03, A-04 | 机体+电池甘特、资源/架次联动、方案比较卡；验收：相同方案也诚实显示，不造差异 | done | feat/solo-fullstack-v0; frontend/src/components/ResourceTimeline.tsx; evidence/browser/e2e-results.json |
| X-02 | P0 | A+B | A-03, A-04, C-04, B-04 | 资源/时间验收（重叠、硬截止、空值显示、费用禁用）；验收：自动化负例全部通过 | done | feat/solo-fullstack-v0; tests/solver/test_solver.py; tests/backend/test_api.py |

## G3

阶段状态：`core_verified`。

| ID | 优先级 | Owner | 依赖 | 任务与验收 | 状态 | 分支/PR/证据 |
|---|---|---|---|---|---|---|
| C-05 | P0 | B | C-02 | 事件幂等、事件时刻/版本、状态更新与新 Snapshot；验收：event_id 重试只有一次状态变化 | done | feat/solo-fullstack-v0; tests/backend/test_api.py |
| A-05 | P0 | A | A-02, C-05 | 尚未起飞机体退出→replan；保留旧版本及已执行事实；验收：无故障机未来架次、前后验证均通过 | done | feat/solo-fullstack-v0; tests/backend/test_api.py; evidence/browser/e2e-results.json |
| A-06 | P0 | A | A-05 | 依赖图传播、变更代价、限时修复/全量回退；验收：输出 changed/preserved，可对照修复范围 | done | feat/solo-fullstack-v0; docs/CHECKPOINT_001.md; evidence/browser/e2e-results.json; evidence/solver/replan-comparison.json |
| B-05 | P0 | B | B-04, C-05 | 事件输入、旧新地图叠加、差异清单、时间轴；验收：可清楚定位受影响任务和未完成原因 | done | feat/solo-fullstack-v0; evidence/browser/e2e-results.json |
| X-03 | P0 | A+B | A-05, A-06, C-05, B-05, X-02 | 事件端到端：原计划→事件→新快照→重算→复盘；验收：旧 Plan 未覆盖，重复事件不重复预约 | done | feat/solo-fullstack-v0; docs/CHECKPOINT_001.md; evidence/browser/e2e-results.json |

## G4

阶段状态：`in_progress`。

| ID | 优先级 | Owner | 依赖 | 任务与验收 | 状态 | 分支/PR/证据 |
|---|---|---|---|---|---|---|
| C-06 | P1 | B | C-01, X-01 | CSV/Excel 映射模板、GeoJSON/GeoTIFF/DEM 资产导入与预处理队列；验收：文件来源与 CRS、有效覆盖、版本可追溯 | in_progress | feat/solo-fullstack-v0; docs/IMPLEMENTATION_STATUS.md; docs/SPATIAL_ROUTING.md; tests/backend/test_spatial.py; evidence/browser/verified/zone-detour-1440.png; docs/TERRAIN_ASSETS.md; tests/backend/test_terrain_assets.py; evidence/browser/verified/terrain-assets-1440.png |
| B-06 | P1 | B | C-06 | 地形/禁入/洪水/通信图层与绘制工具；验收：标注效果与约束校验分开展示 | in_progress | feat/solo-fullstack-v0; docs/IMPLEMENTATION_STATUS.md; docs/SPATIAL_ROUTING.md; tests/backend/test_spatial.py; evidence/browser/verified/zone-detour-1440.png; docs/TERRAIN_ASSETS.md; tests/backend/test_terrain_assets.py; evidence/browser/verified/terrain-assets-1440.png |
| A-07 | P1 | A | A-02, C-06 | 绕行候选 A* 或可见图、净空预检、缓存键与失效；验收：禁入更新后候选重算且有验证 | done | feat/solo-fullstack-v0; docs/SPATIAL_ROUTING.md; solver/routing.py; tests/solver/test_routing.py; evidence/solver/zone-compact.json |
| A-08 | P1 | A | A-02, G0-03 | Q3 中继/两跳链路与时间窗/能源组件完整建模；验收：启用强制通信时无空白认证 | todo | — |
| C-07 | P1 | B | A-08 | 中继资源、传播参数、通信检查结果持久化与 API 升级；验收：协议扩展通过版本迁移测试 | todo | — |
| B-07 | P1 | B | C-07 | 中继点/服务时间轴、通信来源与缺口高亮；验收：点击航段显示接入/回传来源与证据 | todo | — |
| A-09 | P1 | A | A-04, X-02 | 充电端口、起降位与地面工位容量约束；验收：同刻容量超限可检测 | todo | — |
| A-10 | P1 | A | A-05, A-07, C-05 | 电池退出、紧急插单、落点变更、未来封控事件；验收：作用范围、发生/接收时间、旧事实可追踪 | todo | — |
| C-08 | P1 | B | A-10, C-05 | 地图/资源新增事件 API 与一致性事务；验收：版本冲突返回结构化错误 | todo | — |
| B-08 | P1 | B | A-10, C-08 | 动态图层与复盘/故障明细页面；验收：失败、未评估、已验证状态可区分 | todo | — |
| A-11 | P1 | A | A-03, A-07, A-08 | 部分保障、资源缺口/增配试算、可证明下界；验收：明确“证明无解”与“预算未找到” | in_progress | feat/solo-fullstack-v0; docs/RESOURCE_ANALYSIS.md; tests/backend/test_analytics.py; evidence/browser/e2e-results.json |
| A-12 | P1 | A | A-08 | Q4 冻结任务分区、资源峰值与共享损失；验收：分区不冒用可重新分配时的全局最优性 | todo | — |
| C-09 | P1 | B | A-11, C-04 | 资源增配情景 API，独立分叉快照与打印/导出；验收：增配单独建新场景/快照并真实求解 | done | feat/solo-fullstack-v0; docs/RESOURCE_ANALYSIS.md; tests/backend/test_analytics.py; evidence/browser/e2e-results.json; evidence/browser/print-report-qa.json |
| B-09 | P1 | B | C-09, B-05 | 资源增配前端比较与打印任务单；验收：增配单独建新场景/快照并真实求解 | done | feat/solo-fullstack-v0; docs/RESOURCE_ANALYSIS.md; tests/backend/test_analytics.py; evidence/browser/e2e-results.json; evidence/browser/print-report-qa.json |

## G5

阶段状态：`in_progress`。

| ID | 优先级 | Owner | 依赖 | 任务与验收 | 状态 | 分支/PR/证据 |
|---|---|---|---|---|---|---|
| A-13 | P1 | A | A-07, A-08, A-09 | 能耗/时间/通信情景压力；多情景优化/风险指标；验收：同数据同预算对照，情景说明清楚 | in_progress | feat/solo-fullstack-v0; docs/RESOURCE_ANALYSIS.md; tests/backend/test_analytics.py; evidence/browser/e2e-results.json |
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
| Q-01 | P0 | A | A-02, A-08, A-12 | 原题回归：Q1 18架次、Q2 23架次/时间/能耗、Q3 运输+中继基准作结构/约束核查；验收：版本、输入、模型口径、预算一致；不强制相同的可行分配序列 | in_progress | feat/solo-fullstack-v0; docs/IMPLEMENTATION_STATUS.md |
| Q-02 | P0 | A | A-06, A-13 | 多场景/多随机种子、算法 baseline、动态全量/局部对照、消融与性能；验收：`evidence/` 保存数据 hash、commit、配置、原始运行记录 | in_progress | feat/solo-fullstack-v0; docs/IMPLEMENTATION_STATUS.md |
| Q-03 | P0 | B | C-03, C-04, C-05 | 自动契约/数据库/HTTP/并发/重启/导出/离线/安全测试；验收：CI + 本地复现命令 | in_progress | feat/solo-fullstack-v0; docs/IMPLEMENTATION_STATUS.md |
| Q-04 | P0 | B | B-03, B-04, B-05 | UI 交互/响应/颜色可读性/异常态/地图离线显示；验收：实测截图与操作验收 | in_progress | feat/solo-fullstack-v0; docs/IMPLEMENTATION_STATUS.md |
| Q-05 | P0 | A+B | X-01, X-02, X-03, Q-03, Q-04 | 端到端回归脚本与最小真实演示包；验收：任一队友可重新安装并完成全部关键流程 | in_progress | feat/solo-fullstack-v0; docs/IMPLEMENTATION_STATUS.md |
| S-01 | P0 | B | X-01 | 项目简表（官方模板）和项目说明书；验收：每条宣称对应代码与试验证据，按字数上限 | todo | — |
| S-02 | P0 | B | X-03 | 演示视频、系统截图、答辩 PPT（可选但建议）；验收：真实操作镜头，标注加速/历史回放 | todo | — |
| S-03 | P0 | B | — | 商业计划书（可选）、竞品对比/用户访谈；验收：实际验证与假设分开，无虚构合同/收入 | todo | — |
| S-04 | P0 | A+B | S-01, Q-05 | 匿名、许可证、原创新增贡献、源代码与原型证明；取得官方指南/模板与最新通知，核对截止及复用条款；验收：不透露培养单位/导师/身份信息，除官方必须实名栏目 | todo | — |

## 当前执行入口

- 先读 IMPLEMENTATION_STATUS 与 SOLO_EXECUTION，沿用 feat/solo-fullstack-v0 的已验证结果。
- 优先完成当前 in_progress 任务的剩余验收，再推进下一项依赖。不同任务的部分实现不能自动算 done。
- 两人接手前共同复核 RFC-001/RFC-002、现有运行接口、测试证据和 Git 差异；不伪造契约批准记录。
