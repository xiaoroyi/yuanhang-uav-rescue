# HTTP 对接草案

设计草案为 `contracts/http/openapi.draft.json`，当前没有 FastAPI 应用或真实 `/openapi.json`。所有路径前缀 `/api/v1`，snake_case。B 一人负责前后端适配，A 审算法语义。

## 路由与返回

| 方法与路径 | 请求 | 成功返回 |
|---|---|---|
| GET /health | 无 | 200 status/service_version/solver_ready |
| GET /meta/capabilities | 无 | 200 capabilities schema |
| POST /scenarios/import | application/json 完整 Scenario | 201 新 Scenario；后端重新分配身份/版本并保留输入来源 |
| GET /scenarios/{scenario_id} | ID | 200 Scenario |
| PUT /scenarios/{scenario_id} | expected_state_version + 完整 scenario | 200 新版本；path ID 必须一致，身份/版本只由后端管理 |
| POST /scenarios/{scenario_id}/validate | expected_state_version | 200 validation；passed 仍要区分结构与物理资格 |
| POST /scenarios/{scenario_id}/snapshots | expected_state_version | 201 完整 Snapshot |
| GET /snapshots/{snapshot_id} | ID | 200 Snapshot |
| POST /solve-jobs | SolveRequest | 202 queued Job |
| GET /solve-jobs/{job_id} | ID | 200 Job |
| POST /solve-jobs/{job_id}/cancel | 无正文，重复操作幂等 | 202 当前 Job；未停 Worker 前不能标 canceled |
| GET /plans/{plan_id} | ID | 200 Plan |
| POST /plans/{plan_id}/confirm | expected_state_version + idempotency_key | 200 Confirmation；版本和资源冲突 409 |
| POST /events | Event | 200 EventReceipt；不自动启动求解 |
| GET /scenarios/{scenario_id}/events | ID | 200 Event[] |
| GET /plans/{plan_id}/export?format=json\|csv\|geojson | 格式 | JSON 为 Plan；CSV/GeoJSON 包含身份与来源 |

原 Word `/planning/jobs` 与 `/planning/replan` 是背景示意；当前选择统一 solve-jobs，不增加别名。上表只定义 P0，全部 P1/P2 API 在任务板，不假装已上线。

CSV 文件、字段映射、错误报告与预览确认是 C-01 的验收要求，但本轮 HTTP 草案只冻结 JSON 形态。B 在 C-01 同一 PR 中补 `/scenarios/import-file` multipart 设计、映射表 DTO、预览令牌和逐行报告（A 复核单位/含义）；Excel 为 C-06。不能给 JSON 路由直接塞另一种含糊的文件请求。

## 求解请求

SolveRequest 的完整字段见 OpenAPI 组件：snapshot_id、objective、mode、time_limit_s、seed、parent_plan_id、event_id、requested_model_scope、allow_partial_service。客户端不传 plan_id；B 后端创建 Job 时预分配 reserved_plan_id，再构造 SolverOptions.plan_id。

mode=replan 时 parent_plan_id/event_id 同时非空、事件已应用且属于该场景、快照是事件后的新版本。quick/improve 则两个引用均为 null。历史回放使用独立阅读入口，不送入 solve Job，也不改变为 data_origin=solver。

## 错误与幂等

错误统一 `{"error":{"code","message","field_path","details","request_id"}}`，具体 Schema 见 error。404 资源不存在；409 版本、资源或幂等键内容冲突；422 结构/业务/不支持范围；503 服务/Worker 不可用；500 真实内部异常。求解 INFEASIBLE/UNKNOWN 是正常 Job 业务结果，不映射成 HTTP 500。

同 Event ID 同内容重试应先去重再检查版本。确认幂等键存请求摘要与原响应；相同键不同请求 409。POST solve-jobs 暂不承诺请求幂等：前端防重复提交，服务端限并发；如需要网络安全重试，C-03 应明确增加请求幂等键契约。

## 事务与类型生成

确认事务检查当前版本、快照 hash、真实 solver 来源、独立验证、强制范围及预约冲突，一并切换 active Plan 和资源预约；失败回滚。确认属于计划审核，不触发实飞。

C-01：由 JSON Schema 生成受版本控制的 Pydantic 业务类型，生成工具版本锁定，extra=forbid；API DTO 合成这些业务类型，不重写字段。导出实际 OpenAPI 到 `contracts/http/openapi.generated.json` 并做设计差异检查。

B-01：同一成员生成 TypeScript 业务类型，真实 OpenAPI 生成 HTTP client 类型；MockProvider/HttpProvider 消费同样的业务类型。生成文件不手改，CI 重新生成后必须无差异。当前这些生成物和漂移检查均未具备，不能把草案 OpenAPI 宣称是运行服务器生成的结果。
