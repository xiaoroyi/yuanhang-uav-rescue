# V2 测试记录（持续更新）

本轮使用 Windows / Python 3.11.15 / Node 24.16.0，隔离临时 SQLite。V1 历史计数不当作 V2 结果。

## R00 / R01 首批

- `.venv\Scripts\python -m pytest tests/backend/test_operations.py -q`：3 passed，8.79s；覆盖不完整草稿、版本冲突、发布阻断、创建幂等、归档保留原输入、真实子进程求解后的阶段时间/能源/SOC合计。原始本机日志 `.local/v2-operations-pass.log`（忽略目录）。
- 首轮 2 passed / 1 failed：测试把浮点加法后的最后时刻按精确相等比较，差 1e-12s。改为绝对 1e-6s 容差；能源/SOC断言保留。失败日志未删除。
- `scripts/check_contracts.py`：10 旧领域 schemas、18 Mock fixtures、16 历史草案 HTTP 通过；不包含算法认证。
- `scripts/check_governance.py`：89 任务依赖无环、42 原件哈希、18 历史源码 AST、67 本地文档链接通过。
- `scripts/export_operations.py`、`scripts/export_openapi.py`、`node frontend/scripts/generate-types.mjs`：已执行，初批实际 API 54 路径。新增操作 Schema 位于子目录，避免改变旧领域生成器。

执行仿真、指令、在途修复、V2 浏览器和完整回归：尚未运行，不标记通过。实际后续运行结果追加至此。

## 首个纵向闭环（中间检查点）

- test_operations.py + test_execution_v2.py：最近9项核心测试通过，41.77s；覆盖真实 Worker、服务器时钟/持久化恢复、幂等事实、断流位置冻结、独立遥测会话、在途承诺和未来资源释放、逐设备上传/ACK/激活、超时未确定保留原排程、陈旧候选409、无库存与已装载退出阻断、空白CSV/XLSX往返、并发创建无孤立输入。测试后继续加入的断言不冒充已运行。
- `node scripts/v2_visual_review.mjs`：第二轮 passed=true，截图14张，源码当时完整闭环通过；见 browser-review.json。首轮因过度保守的共同资源边界导致默认案例调整未找到方案，已改为无有限地面模型时各资源独立释放并独立检查新旧互斥；原失败截图 failure.png 与日志保留。不是完整回归或当前全部能力完成。
- 正式Playwright `node frontend/scripts/run-e2e.mjs --grep "V2 new user"`：1 passed，13.0s；见 blank-browser-results.json。含成都合成区域空白任务、CSV逐步导入、不兼容电池阻断/修复、刷新恢复预检、实际计算与点位详情、双尺寸地图面积。先前失败分别是空态按钮重名、测试未等待异步路由、发布导致页签重置、点位点击冒泡被航线抢选，均记录并修复，不把失败轮改为通过。
- 原旧 workflow 测试入口显式改为 #/workspace，保留旧业务断言；新根地址由V2用例覆盖，未删除旧流程测试。

完整 Python/原题回归、完整浏览器、当前源码最终lint/build与视觉复验仍待后续执行。
