# 后端模块

Owner B，同时负责前端。已有FastAPI/SQLite/独立Worker实现。根目录执行 `.venv\Scripts\python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000`。接口文档为 /docs，实际机器快照见contracts/http/openapi.generated.json，历史设计草案仍保留作对照。日常演示可直接根start.cmd。运行数据runtime/不提交；HTTP只调用solver/public_api边界。
