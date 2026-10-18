# V2 接口迁移映射

实施依据 RFC-017。旧 47 路径、10 领域 Schema 不改含义；全部新 DTO extra=forbid，未知数值 null。实际 OpenAPI 与生成 TS 是 HTTP 真值；新增操作 JSON Schema 由 scripts/export_operations.py 导出。

| 旧对象/入口 | V2 复用/新增 | 兼容、证据与回退 |
|---|---|---|
| Scenario 创建/版本/导入 | Mission 聚合、可不完整 MissionDraft；发布后仍为原 Scenario | 新增 missions 表；不原地改写旧数据；tests/backend/test_operations.py |
| 零时刻 Event | 继续原 POST /events；执行事件另走 /executions/{id}/events | 不把旧 actor/payload 偷换为执行状态 |
| GET /plans/{id}/analysis、flight-profile、playback | 原接口保留；新增 /stages 阶段投影 | 同一 leg/leg_values；只读附件，不写 Plan |
| 旧确认/预约 | 原 /plans/{id}/confirm | 与启动执行是独立请求；过期仍409 |
| 前端 #/workspace 等 | 任务四阶段；旧视图保留兼容入口 | 根地址新首页；旧 Plan/Scenario 可以从任务关联浏览 |
| 无服务器执行 | Execution + facts + SimulationAdapter + commands | 新表，simulation 命名空间；不读写实际库存；回退旧分支忽略新表 |

迁移为可重复的 SQLAlchemy create_all 增表，无删除/列重写。验证用隔离数据库；正式本机服务切换前保存 SQLite backup 与原 Plan/Snapshot 哈希清单。详细端点及错误形态以实际生成 OpenAPI 为准，未实现部分不列已完成。
# RFC-019增量

Scenario与MissionDraft可选weather；旧输入不强制补字段，原Snapshot/Plan不重写。weather_window加入领域范围枚举，真实Worker对携带weather的新请求补齐必检范围。操作气象信息/阈值能力为true，weather_energy保持false。执行事件新增weather.changed完整严格对象，服务端拒绝混合字段；风险涉及已开始架次时保留承诺并阻断自动修复。JSON Schema、Pydantic、实际OpenAPI与HTTP TypeScript同批生成。现有HTTP路径与无气象调用兼容。

# RFC-020增量

ExecutionView兼容增加applied_event_ids；事件投影增加withdrawn/纠错时间与依据，原事件原输入只读保留。新增POST `/executions/{id}/events/{event_id}/resolve`，只允许未采纳的本机误报；状态/幂等/版本检查和独立审计记录。SSE支持cursor/Last-Event-ID、超前游标409与连接状态，同步读取转线程池。旧控制路由继续保留，但advance与start/resume统一阻断未处理事件。

## RFC-021增量

execution export默认v1保留；version=2新增严格执行包/文档封装。3条execution-archives路径提供只读导入/列表/详情，存储仅OperationRecordRow新命名空间，不创建可控执行/领域行。整体及原文SHA256、Snapshot哈希、Plan结构、事实游标/箱件归属与事件/指令/Job快照引用均检查；不重跑独立物理验证冒充认证。运行时间筛选是只读，不调用simulation/actions。新HTTP/OpenAPI/操作Schema/TypeScript同步，见RFC-021。


## RFC-022—024增量

进度读取暂态Windows共享错误保留最近有效样本，不变更Job领域接口。新增GET `/executions/{execution_id}/devices/{device_id}/mission-state`，CommandView可选observed_state，DeviceApplication可选activation_command_id及expired/rejected上传状态。状态独立持久化simulation.device_state；ACK不代表完成，完成必须实际执行模拟动作并独立读回。通用activate只可核对当前已批准目标，候选走差异确认/逐机上传启用。档案同步检查observed_state的执行、机体和Plan引用；旧缺字段不补造。

TelemetrySample新增可空availability/reason；当前阶段与未来资源可用性分开。0秒/暂停承诺按loaded/relay_started事实判定，只读不推进账本。Pydantic/操作Schema/OpenAPI/TS已同步。地图MapScene只为前端空间视图允许未设基地，未引入伪造Scenario或变更领域契约。

## RFC-025评测增量

新增4个HTTP路径（创建/列表共一路径，详情、取消、导出），实际API共82路径/43严格操作模型。运行存OperationRecordRow的experiment.run/create，原领域表不改列。每轮从不可变源Snapshot复制独立分析Scenario/Snapshot，所有例共用，原任务状态/预约/事实不更新。后台协调器调用既有create_job/JobManager，保留UNKNOWN/ERROR/取消/派发未确定及原始日志。取消真实终止已派发Job，503暂退队列不算失败；完成例不因重启重发。输出Pydantic归一化后封装总SHA，原始文档/字节各自SHA。前端由实际OpenAPI生成，未用any。

## RFC-026执行残余增量

RepairRequest可选repair_policy=dependency/full，省略优先依赖修复；RepairView可选实际calculation_method、repair_reference_id和逐箱diff。SolveRequest可选repair_reference_id属于后端元数据，不进入SolverOptions；只允许服务端严格冻结Reference且input Snapshot匹配，客户端不可注入任意原文/路径。纯Python repair_remaining不导入后端。参考工件solver.repair.reference独立于change记录，含原Plan/Snapshot原文SHA与承诺/未来分段。

操作Schema/实际OpenAPI/TS同批生成：82路径、46操作模型。完整v2执行包增加repair_reference冻结文档及其原文依赖，导入检查SHA、锁定箱件与事实游标、逐箱差异重建；旧包字段省略继续兼容。原Plan/Snapshot、零时刻Event和旧replan含义不变。

## RFC027影响图增量

ExecutionEventView可空impact是记录时刻的运输资源图，节点同时保留Plan/Sortie身份，旧事件缺图不补造；旧原始ID数组仍兼容。图与引用原文随完整执行包保存，导入重建资源后继/闭包/事实承诺并核对直接事件目标。49严格操作模型、82HTTP路径，Schema/OpenAPI/TS同步。没有新增真机或控制权限。
