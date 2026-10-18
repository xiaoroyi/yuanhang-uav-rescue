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
