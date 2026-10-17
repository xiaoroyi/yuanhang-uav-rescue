# B 系统线后端模块

B 与 frontend owner 是同一人，C-* 为历史任务编号。遵守根 AGENTS，先读 docs/03、04、05。

维护 FastAPI、数据校验、SQLite、不可变快照、独立 Worker、幂等事件、确认事务和导出；不重写算法物理公式。只通过 solver/public_api 调用 A。长求解不能阻塞 HTTP；真实 Worker 停止后才能 canceled。

当前已有backend/app/main.py应用、SQLAlchemy SQLite存储、独立子进程JobManager、JSON/CSV/XLSX导入。生成类型在app/generated/domain.py，来自根contracts Schema；不手改。实际OpenAPI快照由scripts/export_openapi.py输出，前端类型随后生成。外部输入不能自称verified_dataset。版本/快照/事件/确认/取消/重启已有测试，后续修改跑tests/backend，进度见docs/IMPLEMENTATION_STATUS.md。
