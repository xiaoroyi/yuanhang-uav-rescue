# 契约变更记录

## 0.1.0-draft 2026-10-17 proposed

首次新建 10 份 JSON Schema、12 份明确 Mock 样例、HTTP 目标草案。旧初始化包未提供，本次没有继承或宣称恢复已批准 1.0.0。

提出 Snapshot/hash、SolverOptions/Outcome、严格状态映射、机体释放时刻、预分配结果 ID、事件相对时钟。P0 明确暂不承载中继、部分保障或真实执行事实。详见 RFC-001。结构检查通过不等于人工批准或算法运行验证。

每次变更须补：版本、RFC/决定链接、兼容范围、迁移方式、受影响消费者与实际检查结果。

## 2026-10-18 实现分支兼容扩展（待团队复核）

- RFC-002：只读资源/回放/报告、what-if来源、任务恢复、深入优化基线与历史DTO；原核心对象保持兼容。已生成实际OpenAPI及TS，真实Worker/浏览器回归通过。
- RFC-003：Scenario可选restricted_zones，model_scope与检查code扩展restricted_zone；旧数据无此字段仍有效。HTTP与入库exclude_unset防止给旧快照补默认值，显式null不伪装缺省。消费者原子升级Schema→Pydantic→OpenAPI→TS，并补旧快照hash、Excel往返、绕行/穿越/边界/缓冲与浏览器版本链检查。规则状态仍为proposed，不代表A/B签字。
- RFC-004：复用原Scenario.terrain字段注册本地GeoTIFF资产；新增资产/绑定/地图独立HTTP DTO、生成类型与只读Solver资产上下文。旧题设引用不变，未知像元不补齐，绑定创建新版本。通过真实GeoTIFF→Worker→独立检查→确认/地图/来源下载、CRS/NoData/损坏/隔离与浏览器刷新检查；完整状态见IMPLEMENTATION_STATUS。
- RFC-005：可选resource_limits、charge_start_s和initial_charges，强制ground_resource范围。有限准备/充电排程、初始补能、独立峰值检查、等待甘特、分析/CSV/报告与确认预约同批实现；缺省旧对象不补字段，旧Snapshot/hash与原无限模型保留。详见GROUND_RESOURCES。Pydantic/OpenAPI/TS同步生成，状态仍待团队复核。
