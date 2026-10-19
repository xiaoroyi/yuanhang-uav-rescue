# V4 专项检查报告

2026-10-19，核心提交3ff456e及本分支收尾修复。用户要求基础与专项检查，不重复无关全量回归。下列结果均为实际运行；旧版本长回归不累加到本轮。

| 命令/检查 | 结果与范围 |
|---|---|
| `.venv\Scripts\python.exe -m pytest tests/backend/test_v4_assets_engines.py tests/solver/test_offline_engines.py tests/engineering/test_v4_policy_backup.py -q` | 最终16 passed，32.08秒；有1项Starlette/httpx弃用提示。包含真实独立求解子进程、同快照双引擎、快速/深入搜索、旧请求身份、策略限制与SHA往返、案例与幂等、备份恢复 |
| `npm.cmd --prefix frontend run lint` | 通过 |
| `YUANHANG_BUILD_DIR=.local/v4/dist`后`npm.cmd --prefix frontend run build` | 严格TypeScript与隔离构建通过，129个构建产物；离线字体包含在内 |
| `scripts/check_contracts.py` | 12份领域Schema、18个Mock样例及16个草案HTTP操作结构/引用检查通过；不代表Mock物理可行 |
| `node scripts/v4_experience_review.mjs` | 最终browser-review.json为passed；5组关键流程、4个首页尺寸、真实地图/安排表/机队/复盘、策略导入与配置下载；浏览器和API错误均为空 |
| 本地EoH候选评估 | 三例实际小场景独立检查通过，包含SOH变化。未请求LLM；结果仅证明接入，不作为性能提升或留出实验 |
| 项目总文档 | 24章、7项原生公式、18张含目录表、35页，主文档与提示词对齐；见DOCUMENT_REVIEW与project-document-audit.json |

原始运行日志保留在忽略目录`.local/v4/`：pytest-final.log、lint-final.log、build-final.log、browser-review-final.log。机器可读浏览器结果和最终页面截图提交到本目录。策略导入/导出测试额外验证跨两个独立runtime保持同一原始字节SHA。

过程中曾发现：API返回默认字段未保留、系统减少动画设置未实时生效、滚动进入后区域不可见、手机标签重叠。均修正并复跑相关检查；早期failure.png留作过程证据。一次默认构建提前替换了生产前端，已恢复V3后改用隔离构建；数据库未被该操作修改。最终生产切换与只读数据保全检查另见release-smoke.json及production-data-after_deployment.json。

未运行：本轮全部旧Python/浏览器长回归、外部模型/天气API、真实设备/SITL、学习性能消融。原题与通信历史真实案例保留V3证据范围，不伪称本轮重新全量跑过。
