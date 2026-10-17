# RFC-001 首次公共契约与缺口评审

状态：**proposed，A 待审，B 待审**。当前仓库没有旧契约消费者，不需要迁移已有新系统数据；也不能声称兼容从未取得的旧 V1。

## 实际发现

原 ZIP 只有 13 份 Markdown，没有它声称已经检查过的 4 份 Schema、5 份 fixtures 或早期初始化包。仓库也没有这些文件。此次 `0.1.0-draft` 是新建评审草案，校验通过仅表明草案与样例一致。

| 冲突/缺口 | 具体处理草案 | 影响 |
|---|---|---|
| 原文三人，用户实际两人 | A 算法，B 前后端；保留 C-* 任务编号 | 所有活动规范/提示词/任务 |
| Word `/planning/jobs`、`/planning/replan`；ZIP `/solve-jobs` | 统一 `/api/v1/solve-jobs`，mode=replan 且关联 parent/event；不实现两套路由 | HTTP、UI client |
| Word `type`、`cargo_item_ids`；ZIP `event_type`、`cargo_ids` | 采用后者；旧原文留档，不直接作为可发送 JSON | Event、Plan |
| 快照格式和 hash 不完整 | Snapshot 完整嵌入 Scenario；hash 算法见数据契约；事件时钟写入 Event，G0 不夹带未定义执行状态 | Python、存储 |
| ID 与 Job 未完成状态混淆 | 后端预分配 `reserved_plan_id`，只有结果存储后 `plan_id` 才可读；queued/running 为空 | Worker、UI |
| FEASIBLE 与验证失败组合含糊 | API 发布成功必须 Plan+passed，失败验证归 ERROR/validation_failed；未验证候选留内部日志 | Outcome/Job |
| 机体周转、充电释放不清楚 | 新建 `drone_released_s`；电池 `battery_released_s` 含本轮补能到可复用，均为 [start,end) | Plan、甘特、独立检查 |
| 在途事实/部分交付没有模型 | 首版事件收紧为场景尚未执行；中途事件、部分保障、服务数量明细须新 RFC | P0 能力限制 |
| P0 没有费用参数或中继实体 | cost=null，cost_model_available=false；kind 仅 transport；强制通信而未支持则拒绝 | 不冒称具备 P1 |
| 能耗和充电公式缺少通用参数协议 | `model_id` 注册、数值参数包；A 声明支持的 ID，未知 ID 返回 INPUT_NOT_READY；不得忽略参数或默认满电 | A-01、capabilities |

`drone_released_s`、`reserved_plan_id`、`effective_time_s` 均为本次明确提出的新字段，未伪装为旧 V1。P0 不声明多角色机、中继、部分充电、真实在途状态、有限充电端口已实现。

## 结果状态的唯一映射草案

| 条件 | Outcome | Job 终态 | 可确认 |
|---|---|---|---|
| 有独立校验通过的真实候选 | FEASIBLE/OPTIMAL + Plan + passed | completed，同状态，plan_id 非空 | 另需当前版本与强制范围满足 |
| 证明指定模型无解 | INFEASIBLE + null | completed | 否 |
| 预算内无候选，未证明无解 | UNKNOWN + null/time_limit | completed | 否 |
| 未支持范围、输入不具计算条件 | UNKNOWN + null/unsupported_scope 或 input_not_ready | completed；请求预检阶段也可 422 | 否 |
| 独立检查失败或执行异常 | ERROR + null，validation_failed/exception | failed + ERROR + error | 否 |
| 用户取消且 Worker 已停止 | UNKNOWN + null/canceled（内部 Outcome） | canceled，solver_status=null，无发布计划 | 否 |

running 期间不通过 Job 发布中间候选。后续如需流式已验证候选，增加版本化字段，避免 `plan_id` 既表示临时对象又表示最终对象。

## 后续兼容路线

- RFC-002：`service_by_demand`、实际执行事实、在途/已装载状态和资源预约。
- RFC-003：中继机、能源组件、网关、双跳通信、服务窗口与中继指标。
- RFC-004：资产版本、地形/限制区、NoData/CRS/垂直基准及缓存失效。
- RFC-005：费率/均衡/余量策略、复杂事件、多基地与权限。

正式 1.0 前允许草案显式修改并联动更新样例；冻结后改变必填、含义或拆分对象必须 major 升级，并保留旧 Schema 和转换器。严格 Schema 不允许通过随手加字段实现伪兼容。

## 评审与验收

先跑 README 中三组检查，逐字段对照 docs/03、04、05；正负样例只证明结构与基本不变量，真实物理验证由 A-02 实现。后端、前端尚不存在，Pydantic/OpenAPI/TS 的实际漂移测试待 C-01/B-01，不能声称已通过。

- A 算法与项目负责人：待审。
- B 前端/后端/集成（同一人）：待审。
- 批准记录与实施 PR：待填写真实记录，不预填。
