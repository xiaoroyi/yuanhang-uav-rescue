# V2当前可用入口

本机http://127.0.0.1:8000/；双击项目根目录start.cmd。独立分支feat/mission-workspace-v2。按用户最新要求只完成必要基础检查后交付，准确范围见[TEST_REPORT](TEST_REPORT.md)和DELIVERY_CHECKS.json；使用[DEMO_GUIDE](DEMO_GUIDE.md)、[限制](KNOWN_LIMITATIONS.md)、[交接](HANDOFF.md)。原开发需求和剩余研究任务全部保留。

# V2 实施索引

- 输入规范：[产品](../../docs/redesign-v2/docs/01_PRODUCT_UX_SPEC.md)、[地图与 V01—V14](../../docs/redesign-v2/docs/02_MAP_ANALYTICS_SPEC.md)、[契约与执行](../../docs/redesign-v2/docs/03_CONTRACTS_EXECUTION_SPEC.md)、[算法](../../docs/redesign-v2/docs/04_ALGORITHM_REALISM_SPEC.md)、[R00—R24 / U、M、D、E 验收](../../docs/redesign-v2/docs/05_TASKS_ACCEPTANCE.md)、[来源](../../docs/redesign-v2/docs/06_RESEARCH_NOTES.md)。首次已全文阅读，后续按任务精读。
- 现状：[REPO_AUDIT](REPO_AUDIT.md)。任务唯一状态源仍为 docs/task-board.json，保留原任务。
- 顺序：R00 审计 → R01 兼容契约 → R02—R09 首页/准备/检查/实际方案 → R10—R12 执行、适配、在途修复 → R13—R19 通信/气象/资源/复盘/异常 → R20—R21 验收交接；R22—R24 追踪外部依赖。
- 边界：两人职责；默认 simulation；保留旧接口与历史输入；禁止真实设备、收费服务、管理员修改、数据删除和 main 合并。
