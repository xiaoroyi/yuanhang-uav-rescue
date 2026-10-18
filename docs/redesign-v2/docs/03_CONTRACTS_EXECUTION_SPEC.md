# 03｜算法、后端、前端与设备执行对接规范

> 本文定义目标接口与迁移要求，不声称当前仓库已经具备这些对象或端点。Codex 必须先读取真实 Schema、OpenAPI、数据库迁移和代码；保留合理的现有名称与类型，通过明确映射实现本规范，不能为统一命名推倒已验证业务。

## 1. 先保留现有契约，再增加业务流程

现有总纲采用 `Scenario → Snapshot → SolveJob → Plan → Event`，后端保存状态，Solver 计算物理与调度，前端渲染。这条数据流应保留。V2 主要增加：上层救援任务 Mission、条件检查报告、统一分析结果、执行实例、遥测、指令及评测实例。

**产品版本 V2 不等于必须把全部 API 改为 `/api/v2`。** 兼容的新资源可以继续位于 `/api/v1`；改变既有字段含义、必填结构或状态枚举时才制定明确版本与迁移。旧 Plan 和旧 Snapshot 保持不可变，不批量补写伪造的新验证结果。

需要废止的是旧页面布局和宣传文案，不是数据追溯、独立检查、算法与 HTTP 解耦等工程规则。删除冗余页面前，为仍有用的操作和接口登记新入口。

## 2. 新对象如何映射旧系统

| 对象              | 所解决的问题                         | 核心字段                                                     | 所有者                     |
| ----------------- | ------------------------------------ | ------------------------------------------------------------ | -------------------------- |
| Mission           | 一个完整救援行动，而非单架次         | `mission_id,name,mode,timezone,lifecycle,current_scenario_id,active_plan_id,active_execution_id,revision` | 后端                       |
| Scenario          | 可编辑需求与资源配置                 | 保留现有字段、`state_version`；关联 Mission                  | 后端；用户录入             |
| Snapshot          | 本次计算到底依据什么                 | 原配置、执行事实截面、地图/气象/模型版本、快照哈希           | 后端                       |
| PreflightReport   | 是否具备开始指定计算或执行的条件     | `report_id,snapshot_id,check_kind,checks,blocking_count,validity_fingerprint` | 后端组织，算法提供领域检查 |
| SolveJob          | 计算作业，不等同运输架次             | 输入选项、阶段、停止原因、用时、候选 ID                      | 后端 Worker                |
| Plan              | 不可变的机队运输与中继安排           | 保留原 ID/指标/架次/验证，追加兼容引用                       | Solver 生成，后端保存      |
| PlanAnalysis      | 地图、甘特、图表共享同一组解释数据   | 轨迹阶段、资源区间、需求服务、能源分项、通信区间             | 算法导出，后端提供只读投影 |
| Execution         | 一次计划的演练、软件在环或实际执行   | `execution_id,mode,initial_plan_id,desired_plan_id,status,revision,clock,state` | 后端/适配器                |
| ExecutionAnalysis | 某执行事实截点上的实际统计与计划偏差 | `execution_id,facts_cursor,active_plan_revisions,analysis_version` | 后端从事实投影             |
| ExecutionFact     | 已发生且不能被重规划抹掉的事实       | 时间、主体、事实类型、来源、质量、原始事件引用               | 后端事件记录               |
| TelemetrySample   | 设备某时刻的观测                     | 设备、会话、序号、采样/接收时间、坐标、电量、质量            | 适配器                     |
| Command           | 系统向设备申请动作及回执记录         | 请求 ID、设备、执行实例、前提、过期时间、状态                | 后端指令网关               |
| ExperimentRun     | 算法和系统的可复现实验               | 场景集、事件序列、方法、预算、种子、软件版本、结果路径       | 实验 Worker                |

`mission_id` 指救援行动；适配器的 `device_mission_id` 指设备内任务；`sortie_id` 指一次架次。禁止三者同名混用。

Mission 生命周期用于首页与列表：`draft / planning / ready / executing / paused / completed / archived`。它不是 Solver 求解状态，也不是飞控飞行模式。一个 Mission 可以保留多套候选 Plan 和多次仿真实验。

### 2.1 计划与资源的作用域

真实资源台账属于机构/工作空间，不能每新建一个任务就复制出另一架真实无人机。实际预约至少带 `resource_id,mission_id,execution_id,start,end,reservation_state`，确认时检查跨任务冲突。

复制演练可以复用资源规格，但预约、库存消耗和执行事实必须进入独立模拟命名空间。`simulation` 与 `real` 的账本不得互相修改。尚不支持多任务共享资源时，明确限制为单活动实际任务，不用“每个任务各自通过”冒充全局无冲突。

## 3. 四种版本与时钟必须分开

1. `state_version`：用户修改需求、设备可用性、地图绑定、策略等配置后的版本，不按每条遥测增加。
2. `execution_revision`：计划接管、暂停/恢复等业务状态变更版本；执行事实另有有序事件游标。
3. `plan_id + snapshot_id`：某次计算与输入的不可变身份；新求解不能覆盖旧 Plan。
4. `device_session_id + telemetry_sequence`：设备重启、流重连后的观测顺序，不等同数据库修改版本。

时间使用：绝对事件保存带时区时间，计算使用相对任务原点的 `_s`；回放游标是前端只读展示时间，服务器模拟时钟是演练事实推进时间，设备观测时间是实况时间。三者都可以显示，但不互相冒充。

### 3.1 有效性指纹与过期处理

新增 `validity_fingerprint` 记录本次方案所依赖的：场景状态、资源预约版本、地图/限制区版本、天气快照、机型与能耗模型/标定版本、必检策略、执行事实截点、算法配置。改变任一相关依赖后，旧方案保留但成为待重查候选。

不是任意遥测抖动都让整套 Plan 失效。由规则判断是否越出预先声明的适用区间，例如机体电量低于计划可容忍范围、落点关闭、实际已交付清单变化或气象预报时段更新。规则与容差可配置且有来源；不能只比较每个浮点数是否完全相等。

在执行任务中，“过期”意味着影响分析和必要的调整，不意味着立即撤销在飞任务或直接停机。

## 4. 通用数据口径

- 展示坐标 WGS84 `[longitude,latitude]`；距离/高程米、速度米/秒、质量千克、体积升、能量 kWh、SOC/SOH 为 0—1 比例。
- 垂直参考单独登记，不把 AMSL、椭球高、AGL、相对起飞点高度放进同一个无说明字段。
- 同一停靠交接完成计时沿用 `station_end`，除非用户明确选择另一个已实现模型。最后交付与最后返航分开显示。
- 需求、仓库库存、已分配、已装载、在途、已交付是不同量。部分保障输出数量，不只给一个未满足需求 ID 数组。
- 值未知用 `null + reason`；时间断流用缺测标记，不补零；不能把尚未实现的检测状态写成通过。
- 原始记录保存未舍入值，显示层格式化。地图坐标不因表格排序重新编号。
- 新字段统一通过 JSON Schema/Pydantic/OpenAPI/生成的 TypeScript 类型与正反例测试；不要用 `any` 或“允许所有扩展字段”掩盖对接错误。

## 5. 条件检查：报告要能定位、修复和追踪

### 5.1 两种检查，不得混为一谈

`planning_readiness` 检查数据与模型是否足以进行指定规划。它只排除已发现的必要条件问题，不能保证全局调度必定有解。

`execution_readiness` 在计划确认后进一步检查设备适配、数据时效、当前位置/电量、装载交付、控制权、现场确认及已实现的执行约束。通过规划模型检查不自动通过实飞准备检查。

### 5.2 每条诊断的目标结构

| 字段                      | 内容                                                    | 谁提供            |
| ------------------------- | ------------------------------------------------------- | ----------------- |
| `code`                    | 稳定机器码，如 `BATTERY_INCOMPATIBLE`                   | 领域模块          |
| `status`                  | `passed / warning / blocked / unknown / not_applicable` | 检查模块          |
| `required_for`            | planning / simulation / real_dispatch                   | 策略              |
| `message`                 | 一句话说明问题                                          | 后端字典/领域模块 |
| `affected_objects`        | 设备、箱件、站点、航段、图层 ID                         | 算法/校验器       |
| `field_path`              | 能打开对应表单的字段                                    | 后端              |
| `actual,required,unit`    | 当前值、要求与单位，缺失保留 null                       | 领域模块          |
| `interval_s,geometry_ref` | 时间和地图位置                                          | 算法              |
| `source_ref,checked_at`   | 数据/规则来源及计算时刻                                 | 后端              |
| `action`                  | 受控动作类型与目标 ID，不是任意脚本或 URL               | 后端映射前端      |

`warning` 不是用户一点击就可以绕过任何硬约束。某检查是否阻塞，由必检策略和场景模式决定。未知天气可以允许明确标记的参数演练，但不能因此把实际作业显示为已获天气保障。

页面顶部只显示“2 项待处理、1 项提醒”和具体修复入口；详细技术术语、原始值和模型范围收在检查抽屉。

## 6. 地图与天气资产合同

### 6.1 地图资产

`MapAsset` 至少包含 `asset_id,version,kind,source,license_note,captured_at,uploaded_at,horizontal_crs,vertical_datum,resolution_m,bounds,nodata_ratio,processing_status,validation_status,content_hash,display_tiles_ref,analysis_asset_ref`。

浏览器使用授权图层地址，Solver 使用后端解析的只读资产引用。禁止接受用户输入任意服务器路径，禁止把浏览器临时对象 URL 交给算法当永久文件。

资产预处理可以异步，只有经过确认的版本绑定任务。显示图层开关只控制渲染；是否进入约束计算通过策略配置，不能“隐藏限制区”就取消限制。

### 6.2 气象快照

`WeatherSnapshot` 至少包含 `weather_snapshot_id,provider,source_kind,issued_at,fetched_at,valid_time_range,horizontal_resolution_m,variables,spatial_reference,interpolation_method,quality,status`。每个变量注明单位、高度参考、是否观测/预报/人工情景，风向注明 FROM/TO 约定。

`variables` 可含风速、阵风、风向、环境温度、降水、能见度；提供方缺少的变量不造值。对飞行时段和空间范围取样；原始预报在有效期内也不自动代表山谷、山脊或高空真实风。来源与商业使用条件见 S17，机型阈值示例来源见 S18。

气象展示已接入、气象硬阈值检查已接入、气象进入能耗模型是三个分别登记的能力。

## 7. Solver 的稳定入口与返回

继续保留 `solve(snapshot, options)`、`replan(snapshot, previous_plan, event, options)`、`validate(snapshot, plan)` 和 `capabilities()`。按需兼容扩展 `analyze_inputs(snapshot, requested_scope)`。如果当前 `replan` 只接受一个事件，在后端形成事件批次引用或新增版本化请求，不能直接把对象换成数组破坏旧调用。

算法不得依赖 React、HTTP、当前登录用户、数据库连接或设备密钥。后端先冻结输入和执行事实，再传入 Solver。算法不能在求解途中从实时流偷偷获取新状态，导致无法复现。

### 7.1 本次输入最少包含

- 原 Scenario 的全部实体与策略，而不是数量摘要。
- 与该 Snapshot 绑定的地图、天气、标定配置与数据质量。
- 重规划时的 `effective_time_s`、执行事实截点、实际位置/SOC/载货、资源归属、不可撤销任务和可撤销预约。
- 相同快照上的目标、总计算预算、随机种子、线程配置、请求模型范围。
- 已有方案的可行性记录和当前适用范围；发生事件后旧方案不能不重查就作为新可行解。

### 7.2 返回内容

`SolverOutcome` 保留求解状态、停止原因、真实时间、诊断、Plan 或 null。地图/甘特所需的阶段数据由算法按同一个物理模型产生，作为 `PlanAnalysis` 或版本化结果附件。

必须有以下语义：

| 情况                     | 作业状态                      | 业务结果               | 页面动作                     |
| ------------------------ | ----------------------------- | ---------------------- | ---------------------------- |
| 找到并检查通过，未证最优 | completed 或仍 running 有候选 | FEASIBLE + 可读 Plan   | 可比较；满足确认条件后可确认 |
| 在声明有限模型内证最优   | completed                     | OPTIMAL + 检查通过     | 显示有限范围，不写全局最优   |
| 预算耗尽没找到可行候选   | completed                     | UNKNOWN + plan=null    | 增预算、修输入或换策略       |
| 模型明确证明不可行       | completed                     | INFEASIBLE + 证明/范围 | 显示已证原因，不是服务器错误 |
| 必需能力不支持           | rejected/业务校验失败         | UNSUPPORTED_SCOPE      | 定位所缺能力；不静默降级     |
| 程序/资产读取异常        | failed                        | ERROR + request_id     | 查看原因/重试                |
| 用户取消                 | canceled（Worker 已确认停止） | 是否有历史候选另记     | 不冒充完成                   |

进度只报真实阶段、用时、候选数量与当前最优可行目标。离总预算还有一半，不意味着求解进度完成 50%。

### 7.3 独立验证与分析图

验证器按原始输入重算箱件覆盖、载重/容积、逐段能源、时间窗、机体/电池/地面资源互斥、已声明的地形/通信/天气/冲突规则。不要读取优化器的 `passed=true` 直接转发。

图表数据必须与验证使用的架次阶段相符。若原模型只能返回起终点电量，先显示端点数值；不要让前端自行生成连续电量曲线。需要连续曲线时，补算法采样或解析阶段接口。

## 8. 前后端 API 目标清单

所有新增端点都是目标设计，现有同义端点可复用，通过 `API_MIGRATION_MAP.md` 登记。HTTP 路由带 `/api/v1` 前缀，表内省略。

| 方法/路径                                    | 关键请求                                       | 返回与主要界面                    |
| -------------------------------------------- | ---------------------------------------------- | --------------------------------- |
| GET `/missions`                              | 分页、状态、关键字                             | 首页最近任务、救援任务列表        |
| POST `/missions`                             | 名称、mode、时区、模板引用；幂等键             | 201；Mission + 初始 Scenario      |
| GET/PATCH `/missions/{id}`                   | PATCH 带 expected_revision                     | 详情/当前阶段；冲突 409           |
| POST `/missions/{id}/clone`                  | 仅复制配置、目标模式                           | 新任务；不复制实际预约/已发生事实 |
| GET/PUT `/scenarios/{id}`                    | 保留现有协议，写入带 expected_state_version    | 配置/新版本                       |
| POST `/scenarios/import`                     | 文件、映射、单位策略                           | 导入预览或新草稿；错误定位行列    |
| POST `/scenarios/{id}/snapshots`             | expected_state_version、必要事实游标           | 不可变快照                        |
| POST `/preflight-jobs`                       | snapshot_id、check_kind、请求范围              | 202 + job_id                      |
| GET `/preflight-reports/{id}`                | 只读                                           | 检查、修复入口、有效性指纹        |
| POST/GET `/solve-jobs`、`/{id}`              | 复用原计算协议                                 | 202/作业状态、真实候选            |
| POST `/solve-jobs/{id}/cancel`               | 幂等请求                                       | 接受取消；终态以 Worker 为准      |
| GET `/plans/{id}`                            | 只读                                           | 原 Plan，不在读取时修改           |
| GET `/plans/{id}/analysis`                   | 范围、可选分页/降采样                          | 与 Plan 绑定的图表/轨迹/诊断      |
| POST `/plans/{id}/confirm`                   | expected_state_version、资源预约版本、幂等键   | 原子确认与预约；不是飞控起飞      |
| POST `/plan-comparisons`                     | plan_ids、比较类型                             | 相同条件/事件差异/实验对比及范围  |
| POST `/executions`                           | confirmed_plan_id、mode、expected_revision     | 创建服务器模拟/SITL/真实执行实例  |
| GET `/executions/{id}`                       | 当前状态/事实游标                              | 执行视图首次加载及重连恢复        |
| GET `/executions/{id}/analysis`              | facts_cursor、相应plan_id                      | 该事实截点的执行统计及计划对照    |
| POST `/executions/{id}/simulation/actions`   | start/pause/resume/reset、幂等键               | 仅 simulation 的可持久化状态      |
| POST `/executions/{id}/events`               | 事件、expected_revision、发生时间              | 幂等记录、影响摘要；不暗中下发    |
| POST `/executions/{id}/replan-jobs`          | 事件集合、事实截点、变更偏好                   | 新快照、新 Job                    |
| POST `/executions/{id}/plan-changes`         | candidate_plan_id、expected_revision、确认记录 | 分设备下发/采纳过程，可部分失败   |
| GET `/devices/{id}/capabilities`             | 设备实例/适配器                                | 真实支持范围、连接和鉴权状态      |
| POST `/commands`                             | 下文 CommandEnvelope                           | 202；网关受理不是执行成功         |
| GET `/commands/{id}`                         | 只读                                           | 设备 ACK、观测完成/失败/未确定    |
| GET `/executions/{id}/telemetry/latest`      | 设备筛选                                       | 最新观测与数据年龄                |
| WS `/executions/{id}/stream`                 | token、游标                                    | 遥测/事实/指令/告警事件流         |
| POST `/assets/uploads`、GET `/assets/{id}`   | 内容及元数据                                   | 异步资产处理/状态/版本            |
| POST `/weather-snapshots`                    | 区域、时段、已配置 provider/manual             | 标注来源的天气快照                |
| POST `/experiments`、GET `/experiments/{id}` | 场景/事件/方法/预算                            | 批量实验及真实记录                |
| GET `/missions/{id}/exports`                 | plan/execution、格式、脱敏选项                 | 任务包、CSV/GeoJSON/报告/日志     |

错误包复用现有 `error.code/message/details/request_id`。补充 `affected_objects,action` 为可选结构。401/403 权限、409 版本/幂等内容冲突、422 输入/状态不允许、429/503 任务容量、500 程序错误；算法证明无解仍是正常计算结果。

页面 QueryKey 至少包含实际依赖的 Mission、Snapshot、Plan、Execution 与分析版本。切换任务取消旧请求或检查响应归属，防止上一任务的结果闪入新地图。

## 9. 地图、图表和前端状态合同

只维护一套共享选中状态：`mission_id,plan_id,execution_id,object_type,object_id,sortie_id,active_time_s,time_source`。地图点、列表行、甘特条、诊断点击都通过同一个 selection store，不各自维护冲突的高亮。

**计划分析与执行分析分开**：`GET /plans/{id}/analysis` 仅由不可变计划、输入和模型版本生成，不在执行后偷偷补入新事实。`GET /executions/{id}/analysis` 绑定 execution_id、facts_cursor 和相关计划版本，产生实际交付、实测轨迹与偏差。前端可以组合两份视图，但每条序列保留来源及事实截点；不能把实时实际值写进旧 Plan 或其不可变分析附件。

`PlanAnalysis` 至少逐步补齐（表内实际量仅由配套 ExecutionAnalysis 提供）：

| 数组                      | 每条必要字段                                                 |
| ------------------------- | ------------------------------------------------------------ |
| `service_rows`            | demand_id、所需/可用/分配/计划交付/实际交付/剩余数量、时限、来源 |
| `resource_intervals`      | resource_id/type、sortie_id、阶段、start_s/end_s、来源       |
| `trajectory_segments`     | sortie_id、phase、t0/t1、坐标/高程基准、载荷、能耗模型结果   |
| `energy_breakdown`        | sortie_id、transport/relay、飞行/爬升/驻留/其他项、kWh       |
| `communication_intervals` | sortie_id、时间段、直连/中继、接入/回传状态与余量、验证方式  |
| `diagnostics`             | 约束、受影响对象、区间、几何引用、实际/阈值                  |
| `change_summary`          | 保留/改派/新增/取消任务、匹配依据、时间变化、箱件重新装载要求 |

纯视图汇总可以由后端从持久化结果投影；能源、净空、通信、可行性不得在前端重新发明。图表下采样只改变渲染，极小余量和异常点不得因此丢失，导出仍保留原数据。

## 10. 三种运行模式和执行账本

### 10.1 计划回放（只读）

拖动时间轴只是读取 Plan 的阶段轨迹，不创建交付记录，不扣库存，不触发真实指令。播放结束只能表示“回放结束”。

### 10.2 服务器业务仿真

实现可持久化的离散事件模拟器，使用 Plan 阶段和事件规则推进 `simulated_execution_facts`。支持开始、暂停、倍速、事件注入、保存/恢复与重新开始。新执行实例或重置版本必须清楚，不能复用旧事实造成重复交付。

浏览器刷新后从后端恢复模拟时间和事实，不是从 UI 动画计时重新算一遍。所有设备、箱件及统计显著标为模拟。环境可采用模型参数或人工情景；不冒充动力学实测。

### 10.3 软件在环/真实设备

SITL 是实际飞控软件在模拟环境中运行，不能与业务离散事件仿真混为一谈。真实适配器需要明确设备/固件支持、现场配置、操作者权限、失联与返航策略等边界。无硬件时交付可运行模拟适配器和合同测试，真实适配器可显示“未配置/未验证”，不填虚假的在线遥测。

设备实况与箱件交付分别记录。设备到达一个坐标不等于所有箱件已交接；交付由明确的投送系统回执、工作人员确认或仿真事件产生，并保存来源。

## 11. DeviceAdapter：为真实接入留出可执行的边界

建议 Python 接口以异步 I/O 实现，名称可适配现有结构：

```python
# 接口示意；实现时使用仓库类型，不复制另一套模型。
class DeviceAdapter:
    async def capabilities(self, device_id): ...
    async def telemetry_stream(self, device_id): ...
    async def compile_mission(self, device_id, validated_sortie, context): ...
    async def validate_compiled_mission(self, device_id, compiled_mission): ...
    async def upload_mission(self, device_id, compiled_mission, request_context): ...
    async def read_mission_state(self, device_id): ...
    async def execute_command(self, device_id, command, request_context): ...
```

必须有 `SimulationAdapter`；下一层可接 `MavsdkAdapter` 或厂商 Cloud/WPML 适配器。按机体查询能力，不靠机型名称模糊匹配。

每个动作返回支持范围：例如当前模式能否上传、是否支持在途更新、哪些指令支持 ACK、能否从设备读取已上传任务哈希、是否能暂停/恢复、装载释放是否有独立回执。

**GeoJSON 是展示/交换几何，不是可直接起飞的飞控任务文件。** 编译需要处理高度参考、起降行为、航点/航段、速度、停靠、投送动作、返航点、地理围栏及设备限制。MAVLink、MAVSDK 与 DJI WPML 支持边界分别见 S19—S23。不能因为某厂商提供 Cloud API 就声称其所有运输机均支持该接口。

不实现浏览器直接发电机控制/刷写固件的通用入口；本产品是上层运输调度，不复制完整驾驶舱或万能地面站。

## 12. 指令生命周期：三个“成功”一定分开

MAVLink 的 ACK 表示接受/拒绝及可能的进度，并不能把“已接受”解释为动作完成。[S19]

建议网关状态：

```text
created → validated → queued → sent → acknowledged → in_progress → succeeded
                     ↘ rejected / expired / canceled
                               ↘ failed / indeterminate
```

实际设备不提供进度时不能虚构 `in_progress` 百分比。状态可以根据协议能力跳过部分阶段，但原始 ACK 与观测证据要保留。

- HTTP 202：后端受理。
- 设备 ACK：设备接受或拒绝。
- 业务完成：来自明确设备状态或动作回执的完成证据。

超时且不能确定设备是否执行时是 `indeterminate`，不是简单“失败”。不能自动重复投放物资、重复起飞或重启任务。只对适配器明确认为可幂等的动作做受控重试；其他动作先查询和人工协调。

### 12.1 指令信封示例

下面是合成协议样例，不是可发往真实设备的请求：

```json
{
  "schema_version": "2.0-proposal",
  "request_id": "CMD-DEMO-001",
  "mission_id": "MIS-DEMO-001",
  "execution_id": "EXE-SIM-001",
  "device_id": "U02",
  "mode": "simulation",
  "command_type": "mission.upload",
  "idempotency_key": "DEMO-UPLOAD-U02-P02",
  "expected_execution_revision": 4,
  "expected_device_mission_revision": 1,
  "desired_plan_id": "PLAN-DEMO-002",
  "expires_at": "2026-10-18T10:01:00+08:00",
  "payload": {"compiled_mission_ref": "ASSET-DEMO-MISSION-002"},
  "approval_ref": "APPROVAL-DEMO-001"
}
```

发起者身份从认证上下文获得，不信任客户端填入的 `actor=admin`。同一幂等键同一内容返回原记录；相同键不同内容返回 409。原协议未提供持久化命令 ID 时，由网关维护映射，不能声称底层天然“恰好执行一次”。

控制前检查权限、模式、设备控制权、适配器能力、最近可信遥测、任务和设备版本、前置计划验证、命令有效期。禁止为了让按钮可用自动切到真实模式。

## 13. 中途修改计划的可靠流程

### 13.1 事实优先，不从头重置

1. 记录新需求、设备异常、落点变化或气象事件，保存 `occurred_at/received_at` 和唯一事件 ID。
2. 冻结执行事实截面，识别已交付、已装载、在飞、正在交接、正在充电等不可忽略状态。
3. 沿未来资源依赖关系计算受影响范围；已完成事实保留，在飞物资保持原载机。
4. 生成新的候选计划并检查完成后剩余电量、可用备用点、通信和时限；无法自动处理的状态交给操作者，而非传送回基地。
5. 前端展示本次哪些任务保留/改派/延迟、哪些要卸货、哪些无法保障、哪些设备将收到更新。
6. 人工确认后进行分设备准备、上传、状态核对和激活；完成后记录设备实际采用版本。

### 13.2 不假设全机队原子切换

网络中的多架设备不可能仅因一次数据库事务就同时采用新计划。执行实例需要保存每台设备的 `desired_plan_revision,active_plan_revision,upload_state,activation_state,last_verified_at`。

在更新窗口内，资源和航路检查应覆盖旧计划仍可能执行的部分以及新计划预留部分；不能先把旧资源全部释放。某台更新失败而其他台已接受时，进入 `partially_applied`，对当前实际组合重新检查并提示人工处理。回滚不能撤销已经发生的飞行或交付。

MAVLink 部分任务更新并非通用标准能力，各飞控支持不同。[S20] 在途更新只对经过验证的设备能力启用；不支持则规划下一个可控交接点之后的未来任务，或提供人工协调建议。

## 14. 遥测流、告警和断线恢复

建议流消息统一封装 `stream_sequence,type,execution_id,device_id,device_session_id,device_sequence,observed_at,received_at,payload,quality`。

质量至少区分 `observed / simulated / stale / missing / invalid`，值域错误或无有效定位不能在地图跳到 `(0,0)`。展示“最后收到 8 秒前”等数据年龄；超时策略来自设备接入配置，不能对全部设备硬编码同一采样周期。

地图可以平滑已收到样本之间的移动；超出观测范围的预测轨迹必须单独虚线、注明预测，不让断网设备继续沿计划假飞。无可靠位置时保持最后观测点并显示失联。

连接恢复：鉴权→读取执行快照和最新事实游标→补齐可重放事件→订阅增量；服务端有序游标与设备序号分别处理。设备重启改变 session，不把新序号 1 当成过时消息永久丢弃。

WebSocket/SSE/轮询按现有工程选一种主方案。求解进度与遥测逻辑分离，不能因高频位置更新反复查询整个 Plan。前端节流、批量图层更新、有界历史缓冲、卸载时清理订阅；设备数和实际采样频率由测量决定。

## 15. 权限、隔离与失败安全

- 首版默认本机/模拟，外部访问显式配置；涉及真实操作时必须有服务端认证与权限控制。
- 至少区分查看者、调度员、操作确认者/管理员；用户身份不由前端字符串决定。
- 设备密钥、厂商令牌在服务端安全存储，前端只接收脱敏连接状态。日志不能暴露密钥或现场个人信息。
- 重要实际指令要求明确二次确认、目标机体和当前版本；快捷键不能直接无确认起飞或投放。
- 上传限制文件大小、类型、路径、压缩解包范围；GeoJSON 文本经安全渲染，不把点名直接传入未清洗的 HTML。
- 指令有效期、幂等记录、审计、速率限制、控制权和跨任务资源冲突都由服务端实施，不只禁用前端按钮。
- 飞控自身失联/低电量保护独立运行，不依赖浏览器连接或调度服务器；本系统不能替代设备已有安全逻辑。[S22]
- 自动化测试只能触发 SimulationAdapter 或明确的测试 SITL 环境，不扫描网络自动发现并控制真实设备。

## 16. 迁移与对接验收

先输出 `API_MIGRATION_MAP.md`：旧路由、旧对象、复用方式、新接口、是否破坏兼容、测试与回滚方法。数据备份及迁移脚本可重复运行；失败时不破坏原数据。

必须完成：旧场景能加载；旧 Plan 可只读浏览且新增未知项不显示通过；旧算法 CLI 回归仍可运行；前端生成类型与后端 OpenAPI 一致；所有新增模拟事实隔离；确认与命令是不同请求；WebSocket 重连不会重复交付；陈旧方案不能被静默确认；多设备部分更新被真实表示。

完成状态不写“控制接口已预留”就结束：无真实硬件时仍应提供一个可以跑通上传、ACK、失败、超时未确定和事实完成的模拟适配器测试。真实厂家未支持的能力列入阻塞清单，并保持 UI 不可误用。
