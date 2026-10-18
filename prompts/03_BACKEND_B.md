# B 的长期开发提示词｜FastAPI 后端、版本、数据与集成

> 本仓库适配说明：仅 A（算法/项目负责人）与 B（前端+后端+集成）两人。`C-*` 只保留为后端任务编号。原始 ZIP 留存于 `references/source/original-handoff.zip`。当前缺少旧版机器契约；新建 `0.1.0-draft` 仅为评审草案，状态见 `docs/DECISIONS.md`，不是已批准V1；当前已实现能力与实际API以docs/IMPLEMENTATION_STATUS.md、docs/SOLO_DELIVERY.md和实际OpenAPI为准。先核对候选分支与最新验收，不从G0重复搭建已有模块。

这是 B 的后端模块检查清单；B 与前端负责人是同一人，统一启动入口为 `prompts/02_SYSTEM_B.md`，A 负责最终合并。系统必须支持真实输入、统一快照、后台算法调用、计划历史、幂等事件、事务确认和可复现导出。

## 必读

`AGENTS.md`、`backend/AGENTS.md`、`docs/CODEX_MASTER_HANDOFF.md`（重点第 2/3/4/5/8/9/10/11 章）、`docs/INTEGRATION_PACT.md`、`contracts/*.schema.json`、`docs/03-DATA-CONTRACT.md`、`docs/04-API-CONTRACT.md`、`docs/05-SOLVER-CONTRACT.md`、`docs/08-TASK-BOARD.md`。

## 权限

主要只改 `backend/`、明确归你负责的通用运行/部署脚本。跨模块字段改动先 RFC，经 A 确认数学语义、B 确认 UI 对接后由 B 统一升级 Schema/Pydantic/OpenAPI/fixtures/生成的前端类型。你不能复制另一套调度/能耗计算，也不能擅自更改 solver 返回的物理数据。

## 全部功能（按依赖完成，而非日期）

- G0：检查现有仓库与契约，建立 FastAPI/Pydantic/SQLite、OpenAPI 和 Schema 交叉校验，公共错误码/请求 ID/CI。
- G1：JSON/CSV 上传、三层校验、场景 CRUD、版本历史、不可变 Snapshot/hash、Job 的排队/运行/完成/失败/取消；独立 Worker 通过 `solver/public_api.py` 调用 A 的真实 solve/validate，保存 Plan/日志、发布 `/api/v1`。
- G2：time/energy 方案存储、版本对比、导出、原子确认/资源预约、冲突 409、Mock/过期/未验证确认拒绝；向 B 提供 OpenAPI 和真实接口示例。
- G3：Event `(scenario_id,event_id)` 唯一约束、实际状态/版本变更、创建新快照、调用 A replan、计划差异/事件记录；同一事件多次网络重试不能重复影响库存。
- G4：Excel/GeoJSON/DEM/GeoTIFF 资产版本与坐标质量、地形数据预处理、中继/链路/能源组件协议扩展、限制区/新事件、资源增配 what-if 的新快照任务。
- G5：ODM/NodeODM 异步影像处理（验质量后入库）、可选飞控仿真接口，只有真实验证后声明可用；必要时升级数据库/任务队列但不预先复杂化。
- G6：并发、取消/超时、重启恢复、源代码打包、无需外网的本地示例启动、匿名参赛材料统稿、API 与算法集成证据。

## 特别注意的协议与可靠性

- `snapshot_id/plan_id` 由 B 预分配，A 回显；Plan 永不覆盖；请求时场景变更不会偷偷影响旧 Job 输入。
- FastAPI 不同步长时间运行 CP-SAT；Job 202 后台处理，状态不能凭页面时间计数伪造完成百分比。
- `job_state=completed` 不代表有计划；必须看 solver_status、has_validated_plan、Validation 和输入快照。
- 版本确认和资源预约同一数据库事务；事件与确认均幂等，前端不能改变后端执行事实。
- 原始五份 Excel/DEM/算法包缺失时，暂用明确 Mock Adapter 让 B 开发，而真实 Job 返回 `503/UNSUPPORTED_SCOPE` 等准确状态，不得伪造 solver 成功。
- 每次公共接口改动，同步 Schema、Pydantic、OpenAPI、fixtures、TS 类型与测试，不让两位成员的 Codex 各维护一套字段。

首次开始先执行 C-01/C-02：后端骨架、场景导入/快照、错误响应与 OpenAPI；之后依据任务板继续。结束必须实际运行 API/契约测试并报告结果及阻塞。
