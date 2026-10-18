# RFC-017：任务流程、隔离执行与承诺前缀修复

状态：按用户本轮授权在 feat/mission-workspace-v2 实施，待 A/B 复核；不改变 manifest 的 proposed。

## 兼容边界

原 Scenario/Snapshot/Plan/Event/SolveJob 与 47 个路径含义不变。新增 Mission 聚合与可不完整的 MissionDraft；完整输入仍经原 Scenario 校验与版本接口。草稿不伪装成可求解快照。已有 Scenario 可显式关联 Mission，旧历史只读保留。

新增严格 Pydantic 操作 DTO → 实际 OpenAPI → 生成 HTTP TS；对应 JSON Schema 导出在 contracts/operations/v2.schema.json，正反例覆盖。领域旧 Schema 不加入任意扩展字段。

## 预检与分析

planning_readiness 为输入和必要条件检查，不证明全局有解；simulation_readiness 要求已确认且未过期 Plan。设备执行始终阻断直到受支持适配器、身份和现场许可齐备。地图/天气未知不显示通过。预检持久保存输入指纹，输入变化则失效。

原 PlanAnalysis 保留；新增阶段分析附件独立绑定原 Snapshot/Plan，阶段来自同一物理 leg/leg_values，坐标 WGS84、相对秒、kg/kWh、垂直基准显式。只提供已计算端点 SOC，阶段内未计算值为 null；不线性伪造电量。

## Execution 与事实

只开放 simulation 创建。独立表保存执行、单调事实游标、幂等操作、事件、调整与命令。模拟时间由服务器 wall-clock anchor + speed 推进，暂停/刷新/服务重启后可恢复；读请求推进并原子去重落账，另有服务线程推进，不依赖浏览器动画。重置创建新实例，不删除事实。回放不写账。

事件受理与候选采纳分开。旧零时刻 Event 不承担执行事件。新增需求必须显式提交库存；库存不足保留缺口，不能自动造箱。失联停止可撤销未来动作，并保留最后遥测，不推断设备空闲。

## 在途修复模型 execution_commitment_v1

本轮先支持“保持已开始准备/装载/飞行/交接的完整架次及其补能安排，重排尚未开始的剩余需求”。已发生交付永久保存；在飞箱件不换机、电池不换、位置/SOC/路径/时序不重置。原 Plan 及冻结事实绑定调整对象。

未来求解为独立剩余输入分支：扣除承诺与已完成箱件、减少对应需求；机体最早可用时间为不可撤销架次释放；电池在既定补能完成时才以满 SOC 可用，这一预测释放与当前观测 SOC 分开保存；未使用电池保留原 SOC/SOH。保守地等待所有承诺补能尾部后再开始新排程，确保有限地面资源不被旧新重复占用。调用原真实 Worker、原独立验证器，不调用旧零时刻 replan。允许资源退出影响未来，但不撤销其已开始的返回段。

候选独立 Plan 只覆盖剩余需求，不能冒充完整原任务 Plan。调整投影组合冻结前缀与独立验证的新 Plan，并额外检查箱件唯一、时间/资源互斥、冻结事实哈希和事件版本。通信强制的在途修复先明确不支持，不能静默关闭通信；仍可模拟原联合方案。

采纳要求执行暂停且 facts_cursor/revision/事件摘要与计算截点一致；并发变化返回409。每设备上传/ACK/完成分开，部分失败/超时为 partially_applied/indeterminate。未完成应用不激活新排程；原承诺保留。模拟采用保守全体确认后生效，不宣称真实全机原子切换。

## 指令边界

DeviceAdapter 为明确异步合同；SimulationAdapter 只处理隔离模拟。服务端检查模式、控制权、版本、TTL、幂等内容与适配能力。HTTP202仅创建受理记录；后续轮询/流可见 ACK 与完成证据。超时未确定不自动重试有副作用动作。不连接 SITL/真机，接口不能由 payload 切换真实模式。

数据库只增加表，可重复 initialize；回退旧分支仍读取旧表。新表不改写旧数据，完整映射与回归证据写 evidence/redesign-v2/API_MIGRATION_MAP.md。
