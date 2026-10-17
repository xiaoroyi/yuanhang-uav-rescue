# AGENTS.md | 援航：所有 Codex 的长期规范模板

> 本仓库适配说明：仅 A（算法/项目负责人）与 B（前端+后端+集成）两人。`C-*` 只保留为后端任务编号。原始 ZIP 留存于 `references/source/original-handoff.zip`。当前缺少旧版机器契约；新建 `0.1.0-draft` 仅为评审草案，状态见 `docs/DECISIONS.md`，不是已批准 V1 或已实现 API。

> 仓库已有 AGENTS.md 时**合并**这些规则，不要盲目覆盖。

## 必读顺序

1. `docs/CODEX_MASTER_HANDOFF.md`（全量功能、设计和无日期任务）。
2. `docs/INTEGRATION_PACT.md`（双方字段与算法/HTTP 接口）。
3. `docs/DECISIONS.md`、`docs/IMPLEMENTATION_STATUS.md`、`docs/08-TASK-BOARD.md`。
4. `contracts/*.schema.json`，当前目录更具体的 `AGENTS.md`。

## 模块责任与权限

A 负责 `solver/` 和项目最终合并；同一位 B 负责 `frontend/`、`backend/` 和部署集成。C-* 只是后端任务编号。公共契约/docs/CI 经 A/B 共同审核，不擅自跨模块重写。两位成员的 Codex 使用同一套 Scenario、Plan、Event 和 SolveJob。

## 单一数据真值

业务对象以已批准的 `contracts/*.schema.json` 为结构真值；FastAPI OpenAPI 是实现后的 HTTP 真值；前端 TS 类型自动生成。几何 EPSG:4326 [经度,纬度]，质量 kg、容积 L、能量 kWh、速度 m/s、相对时间秒、SOC/SOH 为 [0,1]，绝对时刻带时区。未知数用 null 和明确状态，不猜测。

## 诚信与安全边界

该项目是决策支持和模拟，不是飞控/实飞适航认证。Mock 不能显示已验证；历史数模结果不能冒充当前求解；未评估通信/地形不能冒充通过。求解器 UNKNOWN 不是 INFEASIBLE；有限模型 OPTIMAL 不是现实全局最优；任何新结果须有可追溯 Snapshot、Solver 实跑和独立验证。

## 代码与协作

- A 提供纯 Python `solver/public_api.py`，不访问 FastAPI/SQLite。B 只通过稳定接口调用算法。B 只消费后端 API，不在 JS 里计算电池安全或规划目标。
- 每次只领取 1 张小范围任务卡，先计划，再实现，再跑实际测试，再 PR。首次初始化只做规范与契约，不一次性生成全部系统。
- 共享字段变更必须 `RFC → 相关双方同意 → 同一 PR 更新 Schema、Pydantic、fixtures、TS、测试、文档`。
- 禁止 secret/身份信息/私人数据入库；比赛展示素材与源代码按匿名要求检查。

## 每次任务完成报告

TASK ID、修改文件、实现/未实现内容、接口变更、实际运行命令与 PASS/FAIL/未运行、可复现输入/输出、验证范围、后续依赖/阻塞。不得口头宣称测试通过而没有执行证据。
