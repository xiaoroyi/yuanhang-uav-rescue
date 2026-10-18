# 援航｜完整 Codex 开发交接包（以新建 GitHub 仓库为起点）

**你们的分工已经固定为两条开发线：A（你）独立做算法；B+C（两位队友）共同做系统，其中 B 专注前端可视化、C 专注后端/数据与日常集成。** 不再使用按日排期。所有功能以任务 ID 和依赖推进，合并按可运行的里程碑验收。

## 文件内容

| 文件 | 作用 |
|---|---|
| `docs/CODEX_MASTER_HANDOFF.md` | **唯一全量开发总纲**：需求、功能、算法/前后端、数据、界面、任务、测试、参赛材料 |
| `docs/INTEGRATION_PACT.md` | **算法-后端-前端字段级对接细则**：对象来源、状态、异常、模型范围、协议升级 |
| `docs/SOURCE_TRACEABILITY.md` | 原 37 页方案的章节与任务 ID 映射，区别原研究成果与本次新增功能 |
| `prompts/00_INIT_GOVERNANCE.md` | **第一次交给仓库 Codex 的提示词**：先建立规则，不生成整套系统 |
| `prompts/01_SOLVER_A.md` | A 的长期任务提示词，依赖任务 ID，灵活时间 |
| `prompts/02_FRONTEND_B.md` | B 的长期任务提示词，地图、可视化、组件与接口 |
| `prompts/03_BACKEND_C.md` | C 的长期任务提示词，数据、DB、API、Worker/事件 |
| `prompts/04_INTEGRATION_QA.md` | 三人集成/验收时使用的提示词 |
| `templates/AGENTS.template.md` | 如果仓库还没有 AGENTS.md，用它初始化；否则把缺项合并进去，不覆盖已有项目规约 |
| `templates/IMPLEMENTATION_STATUS.template.md` | 真实完成情况与阻塞登记模板 |
| `templates/CONTRACT_RFC.template.md` | 三方共同审的公共接口变更记录模板 |

## 放入现有 GitHub 仓库的方式

1. 在自己的仓库创建分支 `docs/complete-handoff`（或仓库尚空时直接初始化）。
2. **只新增** `docs/CODEX_MASTER_HANDOFF.md`、`docs/INTEGRATION_PACT.md`、`prompts/` 和 `templates/`。若曾上传早期 `rescue-uav-collab-kit`，保留其中 `contracts/*.schema.json`、fixtures、现有代码/测试。
3. 打开你的仓库工作目录，用 `prompts/00_INIT_GOVERNANCE.md` 内容给 Codex 执行。它将先核对当前状态，建立和修订仓库规则，然后停止等待共同确认。
4. G0 通过后，各人分别创建自己的开发分支；A 给算法 Codex `prompts/01_SOLVER_A.md`；B 给前端 Codex `prompts/02_FRONTEND_B.md`；C 给后端 Codex `prompts/03_BACKEND_C.md`。
5. 三个人每次让 Codex 完成**一张任务卡**并提交 PR，按 `CODEX_MASTER_HANDOFF.md` G0/G1/... 的依赖持续开发，无需另排日期。

### 仓库尚且只有空壳怎么办？

先将本包 `docs/`、`prompts/`、`templates/` 放入，然后运行初始化提示词。Codex 会视仓库情况建立 `AGENTS.md`、模块规范、JSON Schema/fixtures、基础 CI（推荐把你们上次的 `rescue-uav-collab-kit` 作为参考，不必重造相同协议）。

### 怎么避免两个包说法不同？

- 全量产品需求与任务：`CODEX_MASTER_HANDOFF.md`；
- 已生效业务对象机器格式：仓库 `contracts/*.schema.json`（若存在）；
- 已实现 HTTP API：由 FastAPI 生成的 OpenAPI；
- 重大变更：`docs/DECISIONS.md` 和 RFC（经过三人批准才生效）；
- 旧 `docs/08-TASK-BOARD.md` 的**按日计划不再适用**，应按本包 G0–G6 的任务 ID/依赖替换，保留历史信息时移入 `docs/archive/`。

## 必须注意的四件事

- **材料中的完整功能是目标，不是已实现能力**，每项需要代码和实际测试证明。
- **不要在同一个 Codex 指令里要求“立即生成整套系统所有代码”**。第一次只审规则，之后分独立任务卡。否则三个 Codex 会各自随意改契约并制造逻辑冲突。
- 算法输入只能通过不可变 Snapshot；后端只通过 `solver/public_api.py` 调用；前端只通过 `/api/v1` 调用后端。
- 对未评估的地形/通信、无真实费率的费用、没有真机数据的稳健与 AI 结论，界面和参赛材料必须准确说明边界。

## 本包不是

它**不是**完整可运行的 React/FastAPI/Solver 工程，也没有代替原数模的五份 Excel、DEM、全部源码。它是统一规范与可执行任务书，目的是让三位使用 Codex 的成员按同一合同独立开发、反复集成。
