# V2 测试记录（持续更新）

本轮使用 Windows / Python 3.11.15 / Node 24.16.0，隔离临时 SQLite。V1 历史计数不当作 V2 结果。

## R00 / R01 首批

- `.venv\Scripts\python -m pytest tests/backend/test_operations.py -q`：3 passed，8.79s；覆盖不完整草稿、版本冲突、发布阻断、创建幂等、归档保留原输入、真实子进程求解后的阶段时间/能源/SOC合计。原始本机日志 `.local/v2-operations-pass.log`（忽略目录）。
- 首轮 2 passed / 1 failed：测试把浮点加法后的最后时刻按精确相等比较，差 1e-12s。改为绝对 1e-6s 容差；能源/SOC断言保留。失败日志未删除。
- `scripts/check_contracts.py`：10 旧领域 schemas、18 Mock fixtures、16 历史草案 HTTP 通过；不包含算法认证。
- `scripts/check_governance.py`：89 任务依赖无环、42 原件哈希、18 历史源码 AST、67 本地文档链接通过。
- `scripts/export_operations.py`、`scripts/export_openapi.py`、`node frontend/scripts/generate-types.mjs`：已执行，初批实际 API 54 路径。新增操作 Schema 位于子目录，避免改变旧领域生成器。

执行仿真、指令、在途修复、V2 浏览器和完整回归：尚未运行，不标记通过。实际后续运行结果追加至此。
