# 两人集成验收 Codex 提示词（每个阶段可重复调用）

> 本仓库适配说明：仅 A（算法/项目负责人）与 B（前端+后端+集成）两人。`C-*` 只保留为后端任务编号。原始 ZIP 留存于 `references/source/original-handoff.zip`。当前缺少旧版机器契约；新建 `0.1.0-draft` 仅为评审草案，状态见 `docs/DECISIONS.md`，不是已批准 V1 或已实现 API。

现在只做【跨模块集成验收】，不要临时新增 UI/算法产品功能来掩盖原来接口的错误。

1. 读 `AGENTS.md`、`docs/CODEX_MASTER_HANDOFF.md`、`docs/INTEGRATION_PACT.md`、`docs/09-TEST-PLAN.md`、`docs/08-TASK-BOARD.md`，根据当前任务板确认验收的是 G1/G2/G3/G4/G5/G6 哪道门槛。
2. 读取最新稳定提交和相关任务 PR，列出结构层字段、请求/响应、版本、模型范围是否一致；禁止私自改合同、借助 TS any/后端 extra allow 隐藏问题。
3. 运行 Schema/fixtures 检查与必要的 solver/backend/frontend 测试；没有的命令要写“未具备/未运行”，不假冒全通过。
4. 端到端：导入一份新的非 Mock 小场景 → 生成 Snapshot → POST 求解任务 → 后端 Worker 真正调用 solver.solve → GET Job/Plan → 地图和箱件/机体/电池甘特联动 → time/energy 比较 → 模拟未起飞设备故障 → Event 幂等/版本更新 → Solver.replan → 原新计划差异 → 任务数据导出与回读。
5. 负例：重叠电池/重复箱件、删除资源、未知电量、未评估通信却要求通信、旧计划确认 409、事件重放、UNKNOWN/INFEASIBLE/ERROR、worker 取消、Mock 不可确认。
6. 记录每步请求 URL/HTTP code/JSON 摘要、实际命令、Python/Node版本、git SHA、方案 ID、快照 hash、求解耗时、已验证范围、截图和 FAIL 的最小复现。
7. 发现错误时按“契约→算法→后端→前端→测试”定位唯一 owner，创建缺陷任务卡；未经 owner 审查不跨目录重构。
8. 给出通过/未通过的 Gate 结论，并列出下一轮按依赖应该先修哪几项。不得因为时间紧，把验证失败替换成静态历史结果或隐藏红色警报。
