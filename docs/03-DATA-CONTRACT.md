# 数据契约草案

当前版本、审批状态及 Schema 列表见 `contracts/manifest.json`。所有对象默认严格拒绝额外字段；JSON 不能含 NaN/Infinity。相对秒允许小数，保留物理原值，不由前端四舍五入后写回。

## 单位与数据来源

WGS84 `[lon,lat]`，质量 kg、体积 L、能量 kWh、距离/高度 m、速度 m/s、SOC/SOH [0,1]。绝对日期为带时区 ISO8601，场景 timezone 使用 IANA 名称。原始 Excel 的百分数、m³、Wh 要显式转换并记录来源，不能按数值大小猜单位。

Scenario.data_origin 是 mock/user_input/verified_dataset；Plan.data_origin 是 mock/solver/imported_historical。算法对 mock 输入试算也不能发布可确认的真实结果。用户输入“verified_dataset”需后端核验来源，不能由 UI 单方面提升可信度。

## 对象与身份

| 对象 | 格式文件 | 分配/修改者 | 核心语义 |
|---|---|---|---|
| Scenario | scenario.schema.json | B 后端 | 源数据与 state_version；编辑递增版本 |
| Snapshot | snapshot.schema.json | B 后端 | 嵌入完整 Scenario，永久绑定一个版本 |
| SolverOptions | solver-options.schema.json | B 后端传给 A | 后端分配 plan_id；范围、预算、种子与快照绑定 |
| SolverOutcome | solver-outcome.schema.json | A | 求解结果；失败不伪造空 Plan |
| Plan | plan.schema.json | A 生成、B 保存 | 架次、资源、路线、时间、指标、验证；不可覆盖 |
| Event | event.schema.json | 客户端稳定 ID，B 接收 | 首版 drone.unavailable；重复 ID 返回原记录 |
| SolveJob | solve-job.schema.json | B | 计算生命周期与结果身份 |
| Validation | common.schema.json/$defs/validation | A 独立计算 | status 与逐项检查，未评估不可冒充通过 |

Schema 是完整字段清单，本页解释语义，不维护另一套缩减 DTO。所有 ID 区分大小写，数组不能依赖排序决定身份。

## 快照与哈希

`content_hash = SHA256(UTF8(json.dumps(scenario, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)))`。只 hash 完整嵌入 Scenario，不包含 snapshot_id/created_at/hash 本身。B 后端为唯一 hash 生产者；浏览器直接保留后端 hash，不自行用 JS 重建。此算法是项目 Python 约定，不宣称是跨语言 RFC 8785。

接收后要求 scenario_id、scenario_state_version 与嵌入 Scenario 一致。将来有地图/执行事实时，把它们纳入版本化快照与 hash 范围，不能原地替换资产内容或沿用旧 hash。

实现分支在入库前先经生成的Scenario模型规范化数字与带时区时间，然后对同一HTTP可见表示计算hash，避免int/float或UTC日期序列化导致服务端与客户端快照不同。

可选扩展缺省时不补null/默认数组，HTTP及规范化exclude_unset以维持旧Snapshot原字节语义与hash。限制区详见RFC-003：非空restricted_zones始终强制检查，旧数据省略则沿用原模型；字段存在时进入版本/hash，不可只改地图图层而沿用旧方案。

有限地面资源详见RFC-005：resource_limits存在时要求ground_resource，charge_start_s区分排队与真正补能，initial_charges记录初始低SOC补满。它们均为兼容可选字段，旧数据省略时不追加默认值。

连续通信详见RFC-006：可选communication及relay_sorties/communication_report/joint_metrics/joint_search；原metrics仍仅统计运输。来源窗口、双向回传、中继实体与能源组件均独立重建；联合累计通信时长按运输任务相加，不是墙钟时长。配置启用后必检communication；缺口或范围不支持不能发布联合方案。

## P0 数据资格

- 单基地，整箱不可拆；需求 required_quantity 是箱数，与库存箱件数分开。
- 单需求全部完成或未完成；本草案 `allow_partial_service=false`。不支持的部分交付不得塞进未定义字段。
- 机型与机体、电池实体分开；容量、兼容、位置、最早可用时间和 SOC/SOH 不得重置。
- 能耗与充电参数由 model_id 注册。G0 Mock 使用 MOCK_UNSUPPORTED，不可直接拿来当真实求解场景。A-01 需从题目与旧代码固定真实模型参数清单、单位、公式版本，B 依 capabilities 拒绝未知 model_id。
- capabilities 只能广播真实支持的模型、目标、事件与检查范围。balanced 可以在 Schema 中预留，但未实现时拒绝请求。
- terrain.status=available 必须有内容 hash、CRS/垂直基准等资料；是否足够做净空认证仍由 A 资格检查决定。

## 架次与指标

`prepare_start_s <= takeoff_s < return_s <= drone_released_s`；电池释放不早于返航；机体占用 `[prepare_start_s,drone_released_s)`，电池占用 `[prepare_start_s,battery_released_s)`。visit.delivery_complete_s 位于起飞与返航之间，逐箱只出现在一个 visit，目标站点须符合 demand。

路线使用真实计算输出的 GeoJSON LineString，不自动把平滑装饰曲线当规划航路。P0 从 base 出发并返回 base。

`last_delivery_s` 是最后一次交接完成；`makespan_s` 是最后返航，不含电池充满时间。`sortie_count` 只计当前草案运输架次，通信扩展后必须重新明确总数和能耗范围。未知能源、最低 SOC、费用为 null；有值时汇总须与架次一致。所有 metrics 是计划统计，不代表实际事实。

验证最小范围：cargo_unique、capacity、inventory、aircraft、battery、time_window、energy；强制地形/通信时追加相应项。真实 validated Plan 必须提供各必检项 passed 的证据，且字段不能与失败检查矛盾。

## 事件与动态边界

`effective_time_s` 明确新计划的时钟；occurred_at/received_at 分别为发生和接收时刻，由 B 后端设置可信接收时间。去重先查 `(scenario_id,event_id)`；同 ID 同内容返回首个结果，同 ID 不同内容 409。首次应用才检查 expected_state_version 并递增一次。

本草案缺少完整执行事实，当前仅允许**整个场景尚未执行**的零时刻机体或运输电池退出。RFC-010兼容扩展Event为严格联合：drone.unavailable带drone_id，battery.unavailable带battery_id，不能交叉或同时给出。B只改指定资源可用状态、保留能源/位置，先更新Scenario再建Snapshot；A核对完整Event与应用后版本、目标退出状态及父Plan链。处理中途事件须先引入执行事实、冻结区间与箱件占有者，不靠回放推断已经送达。
