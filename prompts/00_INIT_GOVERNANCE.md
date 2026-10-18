# 第一次交给 Codex：建立规则、冻结契约、生成任务板（**只做这一阶段**）

> 本仓库适配说明：仅 A（算法/项目负责人）与 B（前端+后端+集成）两人。`C-*` 只保留为后端任务编号。原始 ZIP 留存于 `references/source/original-handoff.zip`。当前缺少旧版机器契约；新建 `0.1.0-draft` 仅为评审草案，状态见 `docs/DECISIONS.md`，不是已批准 V1 或已实现 API。

你是“援航 Rescue-UAV”项目的**仓库规范与软件架构工程师**。现在的 GitHub 仓库可能是空的，也可能已经包含先前初始化包 `rescue-uav-collab-kit` 和部分代码。你的任务首先是建立团队可以并行开发的统一规则，而不是马上把全部业务代码写完。

## 必须先读

1. `docs/CODEX_MASTER_HANDOFF.md` **完整读取，尤其第 0/2/3/4/5/9/10/12 章**；
2. `docs/INTEGRATION_PACT.md`；
3. 仓库现有 `AGENTS.md`、`README.md`、`docs/DECISIONS.md`、`contracts/`、`fixtures/`、`.github/`（存在则读）；
4. `templates/AGENTS.template.md`、`templates/IMPLEMENTATION_STATUS.template.md`、`templates/CONTRACT_RFC.template.md`；
5. 浏览已有 `solver/`、`backend/`、`frontend/` 的目录与测试，但**不能未经授权改写已有真实源码**。

## 团队组织（硬性约束）

- A：算法线 owner，只负责 `solver/`；
- B：同一位系统负责人，同时维护 `frontend/`、`backend/`、地图可视化、DB、HTTP、Worker、部署与展示材料；
- 两位成员的 Codex 使用同一份业务 Schema、接口文档和 AGENTS；跨组更改必须先 RFC/PR 确认。

## 本次要实际做的工作

**第一步：只读审计。** 运行 git status，查看文件树与依赖，输出已有/缺失/冲突列表；如果工作区有未提交修改，先报告风险，不要擅自清理或覆盖。不得初始化第二个 Git 仓库、不得删除已有源代码/数据。检查是否已具有 JSON Schema/fixture 和 `scripts/check_contracts.py`。

**第二步：建立团队规则。** 若没有 `AGENTS.md`，参考模板创建；若已有，保留规则并增加本总纲的新要求。为 `solver/`、`backend/`、`frontend/` 建立或修订模块 `AGENTS.md`，写明各自职责、禁止跨目录大改、测试与完成汇报。明确 `docs/CODEX_MASTER_HANDOFF.md` 为需求与任务唯一总纲，`contracts/*.schema.json` 为当前业务对象真值，FastAPI `/openapi.json` 为已实现 HTTP 真值。确保 README 清楚指向总纲。

**第三步：整理接口与命名空间。** 审核当前 V1 Scenario/Plan/Event/SolveJob 是否覆盖最低 P0 输入输出；重点检查：`snapshot_id/plan_id` 由谁分配、SolverOutcome 的成功/失败一致性、SOC 0-1、时间单位、`model_scope`、中继扩展缺口、需求部分完成、错误码/Job状态。不要一边审计一边随意改字段；先创建 `docs/CONTRACT_RFC_001.md` 列差距、兼容/版本方案、需两人确认项。已有 fixtures 不改数据来源标记。

**第四步：任务看板改为不按日期。** 创建或更新 `docs/08-TASK-BOARD.md`：按总纲 G0→G1→G2→G3→G4→G5→G6 分组，含所有任务 ID、owner、依赖、验收、状态 `todo/in_progress/blocked/done`、PR/证据链接；清除旧的按天截止安排（需要留档放 `docs/archive/`）。不要删 P1/P2 任务；它们全部应写清目标，但实际编码由依赖与优先级推动。

**第五步：建立可持续交付机制。** 创建 `docs/IMPLEMENTATION_STATUS.md`（每项状态根据文件/命令真实判断，不能想当然标 done）、`docs/CONTRACT_CHANGELOG.md`、`.github/pull_request_template.md`、建议的 CODEOWNERS、CI 的 schema/fixture 检查。已存在的自动化和规则要兼容，不要引入无必要依赖。核心 Schema 检查若已有就真实运行并记录结果；前后端尚不存在时不要假称构建通过。

**第六步：给两人准备首任务。** A 核验原数模源码/数据与纯 Python 适配；同一位 B 以 C-01/C-02+B-01 任务组协调后端导入/快照、类型生成与前端骨架。两人围绕同一合同，不按天拆期。

## 结束要求（必须执行）

1. 汇报检查了哪些真实文件、现有模块状态、发现什么协议风险；
2. 列出本次新增/修改文件、是否有任何破坏性变更；
3. **真实运行**现有契约校验/静态检查，逐项说明 PASS/FAIL/未运行；
4. 明确需要团队确认的 RFC 决策（不超过 8 项，按影响排序）；
5. 给 A、B 各出一张最先可做的任务卡；
6. **此轮到此暂停，不继续自动实现全部功能**。等待我确认合同后，才由两人独立分支执行长期任务提示词。

禁止生成虚构的基准数据、假的算法“成功结果”或相互矛盾的 JSON Schema。禁止擅自推送 main 或使用 force push。
