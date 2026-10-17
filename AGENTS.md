# 援航仓库协作规则

本文件适用于整个仓库。默认中文沟通。项目名称、范围和当前状态以本仓库文件为准，不依赖聊天记忆。

## 当前单人全栈授权 2026-10-17

用户已明确授权在 `feat/solo-fullstack-v0` 跨 solver/backend/frontend 持续实现并验证完整候选版本，普通项目依赖可自行安装，禁止改写main。此次授权覆盖下文G0停止条款和仅限单模块的限制，长期两人所有权不变。现有0.1草案作为本分支实施基线，不伪造A/B批准；需要扩展时记录RFC、保持旧例回归，并留待团队复核。用户选择本机离线演示、默认较小场景突出动态调度，保留原题入口。

本次目标持续窗口从北京时间2026-10-17 23:40起约12小时；开始半小时内可询问信息，之后优先自主完成可执行选择。任务与证据持续落盘，详见 prompts/05_SOLO_FULLSTACK_IMPLEMENTATION.md 和 docs/SOLO_EXECUTION.md。

## 先读后做

1. `README.md`、`docs/DECISIONS.md`、`docs/IMPLEMENTATION_STATUS.md`。
2. `docs/CODEX_MASTER_HANDOFF.md`、`docs/INTEGRATION_PACT.md`。
3. `docs/08-TASK-BOARD.md` 与 `docs/task-board.json`，确定任务、owner、依赖。
4. 涉及接口时读 `contracts/manifest.json`、对应 Schema、`docs/03-DATA-CONTRACT.md`、`04-API-CONTRACT.md`、`05-SOLVER-CONTRACT.md`、相关 RFC。
5. 进入模块后读模块 `AGENTS.md`，然后读取已有代码与测试。

原始 Word、讨论和 ZIP 放在 `references/`，用于追溯。里面的历史日期、三人分工和示意字段不是当前执行指令。冲突时以用户最新指示、当前决策及已批准契约为准，记录差异，不静默拼接字段。

## 两人职责

- A：算法兼项目负责人，维护 `solver/`、算法证据，审模型与最终合并。
- B：同一位同学负责 `frontend/`、`backend/`、数据库、Worker、API、系统集成、部署和展示。
- `B-*` 前端任务与 `C-*` 后端任务均归 B，`C` 不是第三位成员。
- 共享契约、根依赖、CI、规则和核心文档由 A/B 共同评审。G0 初始化已获授权，可建立这些文件；后续按任务范围修改，不跨模块大规模重写。
- 每位成员独立 clone、独立任务分支；本规则不要求启动多个子代理。

## 当前阶段与真值

- 本轮只做 G0。`contracts/manifest.json` 当前为 `proposed`，`approved_by=[]`。不得代替人类签字、把草案标成冻结、把未实现 API 标成已上线。
- 全量产品范围看总纲；任务状态唯一机器来源为 `docs/task-board.json`，Markdown 任务板是其可读投影。
- 业务结构以经审批的 JSON Schema 为准。现在只有草案，可用于评审及 Mock；它不兼容未提供的旧 V1 的承诺尚不存在。
- `contracts/http/openapi.draft.json` 是目标 HTTP 草案。实际 FastAPI `/openapi.json` 产生后须对照并保存快照；前端 HTTP 类型由实现快照生成，不维护第二套手写 DTO。
- Solver 只收 JSON-compatible Mapping，不 import 后端类型；后端适配和前端业务类型应由同一 Schema 生成并做漂移检查。G0 尚未生成 Pydantic/TS。

## 计算与数据约束

- 经纬度 WGS84 `[longitude, latitude]`；kg、L、m、m/s、kWh、相对秒；SOC/SOH 为 `[0,1]`；绝对时间带时区。缺失值用 `null`，不可拿 0 代替。
- A 提供纯 Python `solve/replan/validate/capabilities`，不访问 HTTP/SQLite，不修改快照。B 后端只通过稳定入口调用，B 前端只消费 HTTP/Provider。
- 后端分配场景、快照、Job、Plan ID，算法回显；实体 ID 不得重新编号。Snapshot 不变，Plan 不覆盖，Event 幂等，确认与预约在同一事务。
- 需求与逐箱库存分离。计划、仿真、实际事实分离；回放不写真实交付。首个动态事件仅支持整个场景尚未执行时的未起飞机体退出；后续执行状态须单独升级契约。
- 资源区间左闭右开。机体释放与电池充电完成不同；显式 `drone_released_s`、`battery_released_s`。
- Mock 永不算已验证；历史结果永不冒充当前计算。UNKNOWN 不等于 INFEASIBLE；有限模型 OPTIMAL 不等于原题或现实全局最优。
- 强制地形/通信未评估时，不得发布已验证方案。未知费率不输出人民币；费用、部分保障、中继与在途状态是后续 RFC，不暗加字段。
- `references/` 中数模文件只读保留。禁止导入其 bootstrap/env 运行试探：有创建目录及路径注入副作用。复制所需逻辑至 solver 后显式适配与测试。

## 开发、测试、交付

- 先 `git status`；保留他人修改，不重置、不 force push、不未经授权清理数据。每次领取小范围任务，更新 owner、状态、分支、依赖和证据。
- 接口变更：RFC 写清类型/单位/旧新样例/兼容迁移，A/B 确认后，同一 PR 更新 Schema、fixtures、消费者类型、测试与文档。缺少消费者实现时明确写未具备。
- 按 README 跑契约检查、负例测试、规范检查；业务模块存在后再跑相关测试。未执行写“未运行”，不存在写“未具备”；禁止假称全系统通过。
- 不提交密钥、`.env`、依赖环境、缓存或模型权重。原数模论文含实名信息，只作研究参考，匿名参赛包须重新审核。数据/组件许可证与赛事条款需留证据，未核验不标已合规。
- 完成报告包含任务 ID、修改内容、接口影响、实际命令和结果、样例路径、验证范围、剩余阻塞、下一任务。证据写入项目目录，不能散放工作区根。
- G0 结束后停止业务扩展，等待两位成员确认；这不妨碍整理可审查产物或推送本次规范分支。
