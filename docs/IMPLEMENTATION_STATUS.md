# 真实实现状态

截至本次 G0 初始化，**完整系统不能启动**。两人分工：A 算法兼负责人，B 同一人负责前后端/集成。逐任务状态以 task-board.json 为准。

| 项目 | Owner | 状态 | 实际证据 | 限制 |
|---|---|---|---|---|
| 仓库库存、分工、Git规则、模块约定 | A/B | done | README、AGENTS、CONTRIBUTING、模块AGENTS | GitHub分支保护未配置；B账号待补 |
| 原文/数模必要资料归档 | A | done | references/SOURCES.json，42份原件hash | 只是复制与静态核对 |
| 原数模可运行性及适配 | A | in_progress | LEGACY_BASELINE_AUDIT，18份源码AST | 没有跑Q1–Q4；业务依赖和路径未适配 |
| 公共Schema与样例 | A/B | in_progress | 10份Schema、12份Mock、契约检查 | proposed；未获A/B冻结确认 |
| HTTP接口规范 | B | in_progress | openapi.draft.json，16项操作 | 设计草案，无运行服务器 |
| Pydantic/TS业务类型与OpenAPI生成 | B | todo | docs/04规定C-01/B-01交付 | 尚无生成物或漂移测试 |
| 页面/视觉/交互验收规格 | B | done | UI_ACCEPTANCE、总纲第6章 | 只有设计规格，无React页面 |
| G0检查与CI | A/B | in_progress | 本地检查日志，contracts.yml | 本地Python3.13通过；GitHub3.11/3.12待跑 |
| Solver public API/初解/独立验证 | A | todo | docs/05与A-01/A-02任务 | 没有public_api.py |
| Solver重规划/中继/稳健/学习 | A | todo | A-05–A-15完整保留 | 无本项目算法运行证据 |
| 后端导入/快照/Job/确认/事件/导出 | B | todo | C-01–C-11，owner均B | 无FastAPI、数据库或Worker |
| 前端三页/地图/甘特/复盘 | B | todo | B-01–B-10，owner均B | 无package.json，未运行build/typecheck |
| 真实端到端及离线演示 | A/B | todo | X-01–X-03、Q-05 | 不能把Mock检查当E2E |
| 正式参赛材料与条款核验 | A/B | todo | S-01–S-04 | 未取得官方指南原件、模板及最新通知 |

## 当前运行能力

仅可运行契约与规范检查。capabilities Mock 的 solver_ready=false，功能标记全部false；当前没有已批准的模型检查能力。七项P0检查范围只是实现要求，不代表已经验证过真实飞行物理。

## 阻塞与下一步

1. A/B 人工评审 RFC-001，决定正式字段与状态；manifest不自动改approved。
2. A-01 核验物理模型、依赖与旧算法适配，产出真实小场景；B按同一契约开展C-01/C-02/B-01。
3. B账号、依赖工具版本、正式类型生成/运行OpenAPI及远程CI需后续实际落实。完整P1/P2仍为todo，不删除、不预报完成。
