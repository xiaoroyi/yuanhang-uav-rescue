# HTTP 对接草案

历史设计草案为 `contracts/http/openapi.draft.json`。当前feat/solo-fullstack-v0已有FastAPI应用，真实 `/openapi.json` 固定到 `contracts/http/openapi.generated.json`，前端TS由实际快照生成。兼容补充见RFC-002；实现状态见IMPLEMENTATION_STATUS。所有路径前缀 `/api/v1`，snake_case。B一人负责前后端适配，A审算法语义。

2026-10-18体验迭代见[RFC-015](CONTRACT_RFC_015.md)：新增只读`/map/surface`、`/plans/{plan_id}/flight-profile`、`/scenarios/{scenario_id}/versions`及`/scenarios/{scenario_id}/versions/{version}`，实际OpenAPI共有47个路径。高度分析绑定Plan原Snapshot/资产，输入版本读取不回滚、不创建新版本；新增显示DTO由实际OpenAPI生成，不增加另一套手写领域Schema。运行和验收见[体验交接](EXPERIENCE_RELEASE.md)。

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

原 Word `/planning/jobs` 与 `/planning/replan` 是背景示意；当前选择统一 solve-jobs，不增加别名。上表保留G0的P0设计；后续已实现接口见下方RFC、实际生成快照和IMPLEMENTATION_STATUS，其余P1/P2仍在任务板。

G0最初仅确定JSON草案形态。当前JSON/CSV/XLSX导入、字段映射、错误报告及预览确认已有实际实现：文件预览使用`POST /scenarios/import-file` multipart，确认保存使用生成协议；具体字段与错误形态以实际OpenAPI、ImportPreview及IMPLEMENTATION_STATUS为准。文件上传与完整JSON导入保持独立接口，单位/物理含义由A复核。

## 求解请求

SolveRequest 的完整字段见实际 OpenAPI 组件：snapshot_id、objective、mode、time_limit_s、seed、parent_plan_id、event_id、requested_model_scope、allow_partial_service，以及深入优化可选initial_plan_id。客户端不传 plan_id；B 后端创建 Job 时预分配 reserved_plan_id，再构造 SolverOptions.plan_id。initial_plan_id只在HTTP/Worker加载基线，不混入SolverOptions。

mode=replan 时 parent_plan_id/event_id 同时非空、事件已应用且属于该场景、快照是事件后的新版本。quick/improve 则两个引用均为 null。历史回放使用独立阅读入口，不送入 solve Job，也不改变为 data_origin=solver。

## 错误与幂等

错误统一 `{"error":{"code","message","field_path","details","request_id"}}`，具体 Schema 见 error。404 资源不存在；409 版本、资源或幂等键内容冲突；422 结构/业务/不支持范围；503 服务/Worker 不可用；500 真实内部异常。求解 INFEASIBLE/UNKNOWN 是正常 Job 业务结果，不映射成 HTTP 500。

同 Event ID 同内容重试应先去重再检查版本。确认幂等键存请求摘要与原响应；相同键不同请求 409。POST solve-jobs 暂不承诺请求幂等：前端防重复提交，服务端限并发；如需要网络安全重试，C-03 应明确增加请求幂等键契约。

## 事务与类型生成

确认事务检查当前版本、快照 hash、真实 solver 来源、独立验证、强制范围及预约冲突，一并切换 active Plan 和资源预约；失败回滚。确认属于计划审核，不触发实飞。

C-01：由 JSON Schema 生成受版本控制的 Pydantic 业务类型，生成工具版本锁定，extra=forbid；API DTO 合成这些业务类型，不重写字段。导出实际 OpenAPI 到 `contracts/http/openapi.generated.json` 并做设计差异检查。

B-01：同一成员生成 TypeScript 业务类型，真实 OpenAPI 生成 HTTP client 类型；生成文件不手改，CI 重新生成后必须无差异。当前已经生成Pydantic、实际OpenAPI和HTTP/业务TS类型；生成命令见README，应用CI检查漂移。openapi.draft.json仅保留历史设计目标，实际接口以openapi.generated.json和运行中/openapi.json为准。

## DEM资产接口（RFC-004）

| 方法与路径 | 输入 | 实际行为 |
|---|---|---|
| GET /terrain-assets | 无 | TerrainAsset[]，原题只读与本机准备资产 |
| POST /terrain-assets | multipart file + vertical_datum | 201准备资产；16MiB/200万像元限制，未自动绑定场景 |
| GET /terrain-assets/{asset_id}/source | sha256 | 下载已核验来源文件 |
| GET /terrain-assets/{asset_id}/package | sha256 | 下载完整用户DEM资产包，精确保留准备hash |
| POST /terrain-assets/import-package | multipart file，最多40MiB | 201核验后的TerrainAsset；不自动绑定，跨实例与重复导入保持身份 |
| POST /scenarios/{scenario_id}/terrain | expected_state_version、asset_id、sha256、update_dem_elevations | 检查点位覆盖，创建新版本，可从DEM提取高程，409保护并发编辑 |
| GET /map/terrain | asset_id + sha256，缺省保留原题兼容入口 | 同绑定栅格的TerrainMap元数据 |
| GET /map/terrain/{asset_id}/{sha256}.png | 内容身份 | 本地晕渲PNG，NoData透明；不是外部瓦片 |

来源、垂直基准、重投影和Worker上下文见TERRAIN_ASSETS.md；未支持的CRS/损坏文件/覆盖外以结构化422反馈，真实求解无法认证时保持UNKNOWN而非伪造已验证方案。

## 通信接口（RFC-006）

GET /scenarios/{scenario_id}/communication-template只读返回原题链路/中继参数和按当前点位生成的有限悬停候选，不自动启用或保存。常规PUT Scenario保存communication及policy.requires_communication并创建新版本；Job自动补communication必检范围。Plan包含独立验证的relay_sorties、communication_report、joint_metrics及结构化joint_search。确认事务预约运输与中继实体及共同地面容量。原任务CSV继续按运输箱件输出，format=relay_csv单独导出中继任务；JSON保存完整联合Plan，GeoJSON加入kind=relay的路线。模板Excel包含通信配置并支持往返。

## 冻结分区接口（RFC-007）

GET /plans/{plan_id}/partition返回绑定原Snapshot的PartitionReport，独立检查原联合Plan后完整枚举2/3组；不修改Plan和当前场景。状态ready表示完成冻结模型分析，limited明确说明模型/规模/来源限制；每个K单独给available或not_possible。分配、缺口、峰值见证、来源hash和精确排序分数随JSON返回。详细边界见FROZEN_PARTITION.md。

## 单点诊断接口（RFC-009）

GET /snapshots/{snapshot_id}/single-site-analysis?min_return_soc=0.2，返回严格NominalReport，绑定不可变Snapshot。诊断参数不改场景策略，省略时使用快照策略。complete表示额定单点有限模型完成，不是Plan验证状态；partial/limited不给出完整场景metrics。报告没有实际机体、电池或执行时刻，不能传给确认API。实际OpenAPI统一生成TS，当前路径数量见本文顶部与生成快照。模型边界与CLI见NOMINAL_ANALYSIS.md。

## 退出事件扩展（RFC-010）

POST /events接受严格Event联合：drone.unavailable携带drone_id，battery.unavailable携带运输battery_id。旧机体JSON有效，负载不能混用，不增加root层。服务端received_at校验发生时刻；幂等重试先于版本检查。只允许零时刻未执行场景，目标状态退出后保持能源/位置，事务保存版本并清除当前预约，原Plan保留。新Snapshot与父Plan/Event链经HTTP与纯Solver双重核对，详见EVENTS.md。

## 容量诊断（RFC-011）

PlanAnalysis新增可选capacity_bound，绑定原Snapshot，包含质量/体积必要下界、精确分数与箱件见证；旧分析JSON省略该字段仍可解析。不改变Plan可行性或确认接口，详见CAPACITY_BOUNDS。

RFC-012复用POST /events，新增demand.added；原退出JSON兼容，事务追加需求与实物箱件，保存新版本并清除预约。其后mode=replan全量求解。详情见EVENTS/CONTRACT_RFC_012，HTTP类型仍统一生成。

RFC-013复用POST /events精确退出中继能源组件，保留SOC/SOH/位置，完整版本链与通信联合重算；详见EVENTS。
