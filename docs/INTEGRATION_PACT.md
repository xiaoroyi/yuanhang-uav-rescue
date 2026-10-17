# 援航｜算法与前后端接口细则（A 算法 × B 系统）

> 本仓库适配说明：仅A（算法/项目负责人）与B（前端+后端+集成）两人。C-*只保留为后端任务编号。原始ZIP留存于references/source/original-handoff.zip。未取得旧版机器契约，当前0.1.0-draft仍待正式团队冻结；已授权分支实施，真实能力见IMPLEMENTATION_STATUS、实际OpenAPI与各RFC，不把proposed误读成没有代码。

> 本文是 `CODEX_MASTER_HANDOFF.md` 第 3—5 章的**接口验收附录**。目标是让 A、B 在分别开发时知道每个字段来自哪里，怎样传递，何时允许改变，如何断言错误。
> **不直接覆盖 `contracts/*.schema.json`**。本仓库没有取得旧V1文件；当前草案见 manifest 和 docs/03–05。下文保留的旧格式与扩展目标须经 RFC 评审，不是已实现功能或实测解。

## A. 单一数据流：后端才持久化，算法才算物理，前端才渲染

下表B后端与B前端是同一位系统成员的两个模块。本文保留旧V1背景及P1/P2接口目标；含schema_version=1.0.0的示例不能作为本仓库0.1草案样例发送。当前精确字段/状态/接口以docs/03、04、05、IMPLEMENTATION_STATUS及已实施RFC为准；当前已有RFC-006中继扩展与RFC-010运输电池退出，部分保障和在途执行仍未具备，真实成功候选必须独立验证通过。所有扩展仍保留在任务板。

| 链条 | B 接收/保存 | A 接收/生成 | B 读取/展示 | 禁止事项 |
|---|---|---|---|---|
| 输入场景 | `Scenario`、state_version、校验问题 | 按快照读取箱件/设备，不修改源对象 | 上传、资源表、地图 | 前端自行生成电池/SOC；A 从数据库偷读 |
| 不变快照 | 快照 ID/hash/full-json/地图资产版本 | 读取快照并验证参数 | 显示场景版本，作为调用依据 | 修改旧快照、跨版本对比不警告 |
| 方案计算 | 接受请求并分配 ID/Worker | 生成任务/指标/物理检查 | 等待 job 和计划详情 | 长求解堵塞 HTTP；用缓存冒充新解 |
| 机电池时间 | 保存并回显完整 Plan | 逐实体分配、释放时刻 | 两种时间轴与 Tooltip | B 使用路线长度重算时间/SOC |
| 事件处理 | 幂等更新事实、创建新版本 | 根据有效事实和旧计划重算 | 记录操作、叠加前后计划 | 未起飞/在途状态混淆、重复事件 |
| 确认与导出 | 事务、版本检查、发布与导出 | 只提供有校验证据的方案 | 显示确认状态并下载 | 前端自行修改已确认状态 |

## B. Scenario V1 字段分组与对接

| JSON Path | 类型/示例 | B 后端校验 | A 使用 | B 展示 |
|---|---|---|---|---|
| `scenario_id` | `SCN-001` | 全局稳定 ID | 原样回显 | URL/页面标识 |
| `state_version` | 正整数 | 每次受理编辑 +1 | 冻结版本 | 当前/过期标签 |
| `mode` | `simulation` / `planning_assist` | 枚举 | 标记适用范围 | 顶部模式标签 |
| `data_origin` | `mock/user_input/verified_dataset` | 来源记录 | 不改变来源 | Mock 显示不可消除提示 |
| `start_time`/`timezone` | 带时区 ISO 8601、IANA | 必须明确 | 相对秒参考原点 | UI 本地格式化 |
| `coordinate_system` | `EPSG:4326` | V1 强制 | 投影到合适米制系统 | MapLibre 经纬度 |
| `terrain.status` | `not_evaluated/available/invalid` | 数据是否存在/有效 | 仅有可用资料才做净空 | 地形验证范围 |
| `base`/`sites[]` | `id,coordinates,ground_elevation_m,available` | ID唯一、lon/lat合法、可用状态 | 装卸/停靠与路径节点 | 点位、列表、定位 |
| `demands[]` | `demand_id,site_id,cargo_type,required_quantity,priority,expected_deadline_s,hard_deadline_s,mandatory` | 类型/引用/非负量；需求≠库存 | 硬/软时限、保障水平 | 时限、缺口、紧急排序 |
| `cargo_items[]` | `cargo_id,demand_id,type,mass_kg,volume_l,status,location_id` | 唯一箱号、外键及状态 | 不可拆箱分配及容量 | 箱件流向与库存 |
| `drone_types[]` | 机型、载重、体积、速度、能量模型/充电设置 | 正数、兼容引用 | 飞行时间/能耗/装载 | 参数、能力展示 |
| `drones[]` | `drone_id,type_id,status,location_id,available_after_s` | 实体状态和机型存在 | 占机时段 | 机体状态卡/甘特 |
| `batteries[]` | `battery_id,compatible_type_id,capacity_kwh,soc,soh,status,location_id,available_after_s` | SOC∈[0,1]、位置/兼容 | 电池周转与返航储备 | 电池状态/时间轴 |
| `policy` | 最低 SOC、通信/地形要求、交付口径、费用可用标记 | `requires_*` 为强制要求，不隐式降级 | 决定验收范围 | 标注策略和禁用按钮 |

**V1 使用限制**：标准测试场景原题默认初始可用/满电/单基地；项目输入可以改变数量、库存、时限、位置，但如果算法尚不能正确处理部分电量/充电/地形，就要通过 `capabilities` 拒绝或让用户选择明确限定的基准模型，不能默默把输入强制变为全满。

## B. Plan V1 字段级显示映射

| JSON Path | 谁计算/记录 | 前端组件 | 应检查的不变量 |
|---|---|---|---|
| `plan_id`,`snapshot_id`,`scenario_state_version` | B 分配，A 回显 | 页面/版本历史/导出 | 所有架次来自同一快照 |
| `objective`,`solver_status`,`data_origin` | A 求解状态，B 保存 | 方案卡和警告标签 | FEASIBLE ≠现实安全；mock≠solver |
| `model_scope[]` | A 描述真实检查范围 | 验证抽屉 | 未检查功能不可显示通过 |
| `sorties[].sortie_id` | A | 地图/表格/甘特通用 selection key | 不得前端重编号 |
| `sorties[].kind` | A | 运输/中继不同线型 | 中继资源扩展前不得假装存在 |
| `sorties[].cargo_ids` | A | 载荷详情/箱件列表 | 不存在或已交付箱不可再次装运 |
| `sorties[].drone_id` | A | 机体甘特与筛选 | 引用存在/状态可用 |
| `sorties[].battery_id` | A | 电池甘特 | 兼容且区间不重叠 |
| `sorties[].route_geometry` | A | 地图 LineString | 顺序为 lon/lat，不能画“虚构曲线”冒充计算路由 |
| `sorties[].prepare_start_s` | A | 机体/电池预留起点 | 不晚于 takeoff |
| `sorties[].takeoff_s` | A | 起飞事件标记 | < return |
| `sorties[].return_s` | A | 机体释放边界 | 机体下次准备不早于释放 |
| `sorties[].battery_released_s` | A | 电池时间轴释放 | 不能早于上次电池使用结束，补充充电语义 |
| `sorties[].visits[].site_id/cargo_ids` | A | 站点停靠弹窗 | 箱件去向与 demand 一致 |
| `sorties[].visits[].delivery_complete_s` | A | 需求按期情况/播放 | `station_end` 按本站全部箱交接结束 |
| `sorties[].energy_kwh,return_soc` | A | 能源卡、详情 | 单位 kWh 与比例 0～1；null 为未算 |
| `sorties[].terrain_status,communication_status` | A | 约束范围标签 | `not_evaluated` 不可显示为 passed |
| `metrics.last_delivery_s` | A | 最晚投送指标 | 不等于所有设备返航时间 |
| `metrics.makespan_s` | A | 最后返航指标 | 以声明模型范围解释是否含中继 |
| `metrics.energy_kwh` | A | 目标卡、能耗统计 | 与所有受本计划计入的架次总耗能一致 |
| `metrics.cost_cny` | A 配合费率/B 持久化 | 费用指标 | 无费率则 null，不能自动人民币转换 |
| `validation.checks[]` | A | 展开验证报告 | 错误带 affected ids、当前/要求值 |
| `unserved_demand_ids` | A | 缺口清单 | 用数量级扩展后区分部分服务 |
| `change_summary` | A/B 协作 | 动态计划 diff | ID 映射准确，旧 Plan 不变 |

## D. 动态事件：具体 JSON 与版本链

以下来自既有 V1 格式的**开发模拟示例**：

```json
{
  "schema_version":"1.0.0",
  "event_id":"EVT-TEST-001",
  "scenario_id":"SCN-TEST-001",
  "expected_state_version":1,
  "event_type":"drone.unavailable",
  "occurred_at":"2026-10-17T09:02:00+08:00",
  "received_at":"2026-10-17T09:02:01+08:00",
  "actor":"simulation",
  "payload":{"drone_id":"U02"},
  "reason":"测试：未起飞机体退出"
}
```

1. B 校验 ID、版本，确定此事件能否对当前机体状态应用；**在途实体不属于首版自动修复**。
2. B 在事务中插入事件（唯一键 `scenario_id,event_id`）→更新机体状态及 `state_version=2`→提交；相同事件 ID 第二次重复请求返回第一次记录，不能再升级到 3。
3. B 为版本 2 生成快照，带前一个计划 `parent_plan_id` 和 `event_id` 提交新 Job。
4. A 的 `replan` 只能读已更新快照与旧 Plan，不得修改旧 Plan 或认为既有箱件凭空返库；故障机未来任务被移除或改派，不能在途/已完成任务时光倒流。
5. B 保存新 Plan；B 对比两 Plan 时要显示不同 `snapshot_id`，解释为何不应作为“同条件多目标对比”。

### P1 事件扩展前先问清楚

`battery.unavailable`：是否已装机？是否在飞？是否可以撤销预约？`site.unavailable`：影响投送方式还是空域？`demand.created`：新箱件是否已有库存？以上问题没有答案时，不允许 Codex 自行猜测 `Event.payload`。

## E. 能力协商：避免界面展示尚未完成的功能

建议新增 GET `/api/v1/meta/capabilities`，响应草案：

```json
{
  "api_version":"v1",
  "schema_versions":["1.0.0"],
  "solver_ready":false,
  "supported_objectives":[],
  "supported_events":[],
  "supported_model_scope":[],
  "maps":{"points":true,"geofences":false,"dem_validation":false,"orthomosaic_import":false},
  "features":{"partial_service":false,"relay_coordination":false,"what_if":false,"execution_state":false}
}
```

这是**未连接求解器时**的开发示意响应，字段属 API 建议扩展而非当前 V1 的已存在端点。前端应根据真实可用能力显示功能，而不是永远显示可点击的“AI优化”“中继验证通过”。`solver_ready=true` 仍不意味着所有场景都可执行，必须检查输入就绪。

## F. 算法的异常与状态，请前后端逐一处理

| A/Worker 结果 | B 的 Job 语义 | B 应显示 | 能否确认 |
|---|---|---|---|
| 已找到并通过独立验证的候选、未证明最优 | `completed + FEASIBLE + has_validated_plan=true` | 当前模型内可行、计算耗时和限制 | 仅当前快照+满足强制模型范围时 |
| 已证明有限模型目标最优、且独立验证通过 | `completed + OPTIMAL + true` | 标注“在指定模型/候选范围内最优” | 条件同上 |
| 指定有限模型证明无解 | `completed + INFEASIBLE + false` | “当前模型/候选范围内无解” | 否 |
| 计算预算耗尽无可验证候选 | `completed + UNKNOWN + false` | “在预算内未找到”，给出进一步尝试建议 | 否 |
| `requires_communication=true` 而引擎不支持 | `completed + UNKNOWN` 或任务拒绝（按 API 定义）+ 明确 `UNSUPPORTED_SCOPE` | “该能力当前未接入，不能求解该请求” | 否 |
| Worker 抛异常/磁盘读取失败 | `failed + ERROR + false` | 计算失败+请求 ID，便于重试 | 否 |
| 用户取消且 Worker 停止 | `canceled + ...` | 已取消，已存历史候选按真实验证范围说明 | 默认否；另行确认业务策略 |
| Plan 验证失败 | `completed/failed` 与 `validation.failed` 的一致组合（G0 冻结具体规则） | 列出冲突对象，禁止假成功 | 否 |

**关键一致性测试**：`has_validated_plan=true` 的 Job 必须引用一份 `data_origin=solver`、Snapshot 一致且 `validation.status=passed` 的 Plan；Mock plan 从不允许 confirm；Job 正常完成不代表业务成功。

## G. 两个人每次变更必须做的契约测试

1. A 修改 Solver 输出：用当前 `contracts/plan.schema.json` 校验，再跑后端真实 Adapter test，最后由 B 验证地图/甘特的选择联动。
2. B 修改接口：运行 `pytest tests/backend`，按README导出实际OpenAPI并生成前端TypeScript类型；B运行lint/typecheck/build；必要时A确认语义。
3. B 修改 UI：使用 `fixture` 和真实 Plan 两条数据路径，至少验证 `mock` 标签、`null`/`not_evaluated`、时间线及点击高亮。
4. 修改共享字段：单 PR 含 Schema、fixture、Pydantic、TS 生成类型、文档、测试和版本迁移说明；禁止先合并其中一半。
5. 每次集成将 Scenario/Job/Plan/Event 的实际响应保存到已匿名的 `evidence/contract-smoke/`，标注 commit SHA、来源和是否 Mock。

## H. 对现有 V1 契约的补全顺序（防止一次冲垮项目）

**C1 必需优先统一（开始写业务代码前）**：SolverOutcome 的成功/失败不变量、snapshot 传参结构、错误包、ID分配、Job状态、`model_scope` 的必检策略、Pydantic↔Schema↔TS 类型生成。
**C2 首个真实闭环后**：`service_by_demand`、实际/模拟执行状态、计划确认与资源预约记录。
**C3 需要实现中继/GeoTIFF时**：中继独立能源组件类型、双跳链路、通信服务时段、地图资产版本与障碍/限制区数据。
**C4 在 AI/费用/多基地前**：目标/费率与结果级置信度/来源、训练数据和预测校准、复杂执行事实与用户权限。

*记住：这些字段与端点是基于团队方案的工程细化建议，并非原数模论文已提供的可运行生产接口。*

当前实施扩展RFC-012：demand.added支持整个场景未执行时向已有点位插入需求与等量基地实物箱件，事务/版本/幂等和真实全量重算已接通；两种旧退出负载保持，参见EVENTS。
