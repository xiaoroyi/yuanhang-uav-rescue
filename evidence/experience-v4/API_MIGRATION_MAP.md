# V4 接口迁移

实际OpenAPI路径模板83→91；领域Schema 11→12。契约状态仍proposed，未替代A/B正式批准。主记录为RFC-032、Schema、生成Pydantic、实际OpenAPI与生成TypeScript。

| 对象/路径 | 兼容扩展与语义 |
|---|---|
| SolveRequest、SolverOptions | 可选engine_type、heuristic_policy_id、heuristic_policy_sha256；缺省保持标准。API和Worker分别核对不可变策略指纹 |
| Plan.engine | 新请求显式选择时记录引擎、策略版本/来源/SHA、实际评分/回退次数；旧JSON不回填 |
| ExperimentRequest/View | 可选固定引擎；旧缺省None字段不改变历史幂等身份；残余修复继承基线引擎 |
| MissionCreate/View | 可选case_id与source_case_id；沿用原创建事务。旧请求身份兼容，新案例创建独立输入，不复制执行事实 |
| GET /case-library、/{case_id}/preview | 版本化案例及输入预览；预览不是计算结果 |
| GET /asset-overview | 本机任务、快照、方案、事件和执行等只读聚合 |
| GET /heuristic-packages | 内置与本地已保存评分包目录；来源、指纹与实际格式 |
| POST /heuristic-packages/import | 严格32KiB、唯一Schema、受限算术AST、数值检查；新ID不可变保存原字节，拒绝重复键/非有限数 |
| GET /heuristic-packages/{policy_id}/export | 返回保存的原始JSON字节，避免JSON重排改变SHA；非任意Python文件下载 |
| GET /integrations、/configuration | 真实适配器能力/实际路径和离线配置模板；密钥为空，真实设备与外部调用关闭 |

以上路径均以`/api/v1`为前缀。Execution、事实账本、DeviceAdapter状态机与原确认预约合同保留。策略只影响候选排序，不改变可行域、独立检查、最终目标或执行承诺。运行目录新增heuristics/*.json纳入既有一致性备份，恢复保持包原字节；普通Git clone不携带个人运行库与导入包。
