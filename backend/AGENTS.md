# B 系统线后端模块

B 与 frontend owner 是同一人，C-* 为历史任务编号。遵守根 AGENTS，先读 docs/03、04、05。

维护 FastAPI、数据校验、SQLite、不可变快照、独立 Worker、幂等事件、确认事务和导出；不重写算法物理公式。只通过 solver/public_api 调用 A。长求解不能阻塞 HTTP；真实 Worker 停止后才能 canceled。

先做 C-01/C-02，锁定工具版本、生成业务类型和实际 OpenAPI，增加 JSON/CSV 预览与逐行错误、快照 hash 测试。solver 尚未就绪时显示 not_ready，不伪造成功 Plan。当前没有应用或数据库迁移，不报告 API 已通过。
