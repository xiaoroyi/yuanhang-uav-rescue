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
- RFC-006：可选通信参数/中继实体/能源组件与联合Plan对象；既有metrics不改变运输含义，额外joint_metrics统计联合结果，joint_search保存有限搜索证据。解析连续区间检查、共享地面容量、Worker/确认/Excel/CSV/GeoJSON/报告和界面同批接入。首次32箱通过、一般80箱搜索UNKNOWN；后续增加历史分组候选并全量重算，80箱已得到独立验证可行解，原失败保留。正式团队批准仍待复核。
- RFC-007：绑定Plan/Snapshot的只读冻结分区DTO；2/3组有限完整枚举、专用实体与资源峰值见证。只在同质满SOC、最多10连通单元的冻结模型内使用，不改变原Plan。
- RFC-008：本机Health增加服务/工作区/数据目录身份；构建文件hash与备份清单独立于业务对象。启动仅复用匹配身份的服务，恢复只到新目录；不改旧Snapshot字段。
- RFC-009：单点诊断只读HTTP DTO与纯Python CLI；额定满SOC模型、完整计数DP、基线、敏感性和独立检查，不生成Plan/Job或改写策略。
- RFC-010：Event严格机体/运输电池退出联合，payload各自只收drone_id或battery_id；完整事件、父Plan、新Snapshot链验证。旧机体退出形状保留，禁止混合字段；事件客户端须识别新增类型。
- RFC-011：PlanAnalysis新增可选capacity_bound报告，缺省旧Analysis仍可读；精确分数、库存见证和保守容差放松给出运输架次必要下界，不改变Plan/metrics。
- RFC-012：Event新增demand.added严格分支，payload包含已有点位的新Demand及等量基地实物Cargo。只能整个场景未执行、零时刻插入；新版本data_origin转user_input（Mock保持），全量重算，原Plan/Snapshot保留。
- RFC-013：Event新增relay_energy.unavailable分支，仅component_id，与运输battery_id区分。仅退出中继能源可用性，不改SOC/SOH/位置，联合全量重算并独立拒绝引用退出组件。

- RFC-014：WhatIfRequest增加可选ground_addition，有限准备工位/充电端口仅增配且保留原输入；ScenarioOrigin新增what_if_v2_ground_capacity标签，旧缺省/null保持v1。只扩展HTTP DTO并同步实际OpenAPI/TS，不改核心Scenario/Plan Schema；严格整数、无限容量/越界拒绝、真实重算/导出/刷新已有专项检查。
- [RFC-015](CONTRACT_RFC_015.md)：新增四个只读HTTP路径：绑定资产ID/hash的DEM表面、绑定原Plan/Snapshot的架次高度剖面、输入版本列表及版本明细。真实OpenAPI由43增至47路径并生成前端TS；不改核心Scenario/Snapshot/Plan、Solver边界或数据库结构。NoData/未知值保留null，高度区分地面、模型作业/巡航高程及显示倍率；历史版本无创建时间时不编造时间。卫星底图与本机档案不进入求解或认证契约。专项检查及最终统一验收范围见 [体验迭代交接](EXPERIENCE_RELEASE.md)，不沿用v0计数宣称新UI通过。状态为adopted_for_branch，正式批准仍待A/B。

上述扩展在本功能分支按影响范围同步Schema/fixture、生成类型、实际OpenAPI/TS、消费者和测试。Event严格联合和新的变换版本标签需要A/B共同升级消费者；不能因JSON结构向后可读就假定旧客户端具备新增处理能力。所有RFC仍待团队复核，未代填approved_by。
