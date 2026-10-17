# 援航

面向灾害应急的无人机运输与通信协同调度系统。根据需求、逐箱库存和实际机队状态，生成任务安排、比较取舍、处理动态事件并解释资源缺口。首期用于模拟和规划辅助。

**当前状态：G0 规范初始化。尚无可运行的 Solver、后端或前端。契约版本为 `0.1.0-draft`，等待 A/B 共同评审，不能当作已批准 V1。**

## 新成员与无记忆 Codex 从这里开始

1. 阅读 [AGENTS.md](AGENTS.md)，确认本次工作属于 A 或 B。
2. 阅读 [完整开发总纲](docs/CODEX_MASTER_HANDOFF.md)、[接口细则](docs/INTEGRATION_PACT.md)。
3. 查看 [决策与待确认项](docs/DECISIONS.md)、[真实实现状态](docs/IMPLEMENTATION_STATUS.md)、[任务板](docs/08-TASK-BOARD.md)。
4. 阅读 [数据契约](docs/03-DATA-CONTRACT.md)、[HTTP 契约](docs/04-API-CONTRACT.md)、[算法接口](docs/05-SOLVER-CONTRACT.md) 和模块 AGENTS。
5. 按任务 ID 开分支，每次完成一张或一组相关任务；记录测试证据再提 PR。

## 两人分工

| 人员 | 目录与职责 | 启动提示词 |
|---|---|---|
| A：算法兼项目负责人 | `solver/`、算法实验、模型与最终合并 | [算法入口](prompts/01_SOLVER_A.md) |
| B：同一位前后端同学 | `frontend/`、`backend/`、数据、Worker、部署与系统集成 | [系统入口](prompts/02_SYSTEM_B.md) |

`B-*` 为前端任务编号，`C-*` 为保留的后端任务编号；两类均由 B 负责，没有第三位开发人员。共享契约 A/B 共同评审。

## 目录

| 目录 | 内容 |
|---|---|
| `docs/` | 全量需求、接口、任务、决策、测试与 G0 报告 |
| `contracts/` | JSON Schema 草案、版本清单、HTTP 设计草案 |
| `fixtures/` | 明确标为 mock 的开发样例，无真实算法成功样例 |
| `solver/`、`backend/`、`frontend/` | 当前只有模块约定，业务实现待开发 |
| `references/source/` | 原开发方案、初步讨论、原始对接 ZIP |
| `references/modeling/` | 原题、论文、答案、精选源码、5 张输入表与 DEM、发布依据 |
| `scripts/`、`tests/contracts/` | 契约及规范检查、负例回归 |
| `evidence/` | 本项目实际检查与未来实验记录 |
| `submission/` | 未来匿名交付，不直接复制含身份的原数模材料 |

原文与导入来源见 [资料索引](references/README.md) 和 [SHA-256 清单](references/SOURCES.json)。旧算法是参考源码，不属于新系统已实现能力。

## 当前可执行的检查

Python 3.11 或 3.12，使用项目独立环境：

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements-dev.txt
.venv\Scripts\python scripts/check_contracts.py
.venv\Scripts\python -m unittest discover -s tests/contracts -v
.venv\Scripts\python scripts/check_governance.py
```

需要保存本轮检查日志时，执行 `.venv\Scripts\python scripts/run_checks.py`。它检查暂存区空白并更新 evidence/governance；提交前应重新暂存这些证据。

Linux/macOS 将 `.venv\Scripts\python` 换成 `.venv/bin/python`。这些命令检查草案与仓库规范，**不启动业务系统，也不证明物理可行性**。当前没有 `npm run dev` 或 `uvicorn` 启动入口；由 B 在相应任务完成后补充实测命令。

## 协作与确认

遵循 [CONTRIBUTING.md](CONTRIBUTING.md)。`main` 保持可运行或可验证，功能分支通过 PR 合并，A 负责最终合并。当前 G0 评审清单见 [CONTRACT_RFC_001.md](docs/CONTRACT_RFC_001.md) 和 [初始化报告](docs/G0_REPORT.md)。评审前先做源码核验、界面设计等不依赖冻结字段的准备，暂不大规模实现业务。
