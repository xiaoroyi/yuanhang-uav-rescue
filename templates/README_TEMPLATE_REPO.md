# 援航 Rescue-UAV

> 本仓库适配说明：仅 A（算法/项目负责人）与 B（前端+后端+集成）两人。`C-*` 只保留为后端任务编号。原始 ZIP 留存于 `references/source/original-handoff.zip`。当前缺少旧版机器契约；新建 `0.1.0-draft` 仅为评审草案，状态见 `docs/DECISIONS.md`，不是已批准 V1 或已实现 API。

**项目目标**：面向灾害应急的无人机物资运输与通信协同调度辅助系统（仿真/规划），不是直接飞控。

## 必读文档

- [`docs/CODEX_MASTER_HANDOFF.md`](../docs/CODEX_MASTER_HANDOFF.md)：唯一全量功能、技术路线与按依赖的任务总纲
- [`docs/INTEGRATION_PACT.md`](../docs/INTEGRATION_PACT.md)：A Solver↔B Backend↔B Frontend 逐字段接口
- [`docs/SOURCE_TRACEABILITY.md`](../docs/SOURCE_TRACEABILITY.md)：与原系统方案的章节对应
- `AGENTS.md`：两位 Codex 的共同约束
- `docs/08-TASK-BOARD.md`：任务当前状态（无按天排期）
- `contracts/*.schema.json`：已批准的当前业务对象结构

## 模块所有权

- A：`solver/`，纯 Python 求解与独立检查
- B：`frontend/`，React、地图、甘特、交互
- B：`backend/`，FastAPI、数据/快照、Worker、事件/导出

## 运行

> **必须由实现者根据实际代码和测试填写启动命令**，不得把尚不存在的模块当已完成。若只有规范包，说明“当前仓库只含开发规则，尚不能运行完整系统”。

## 数据与真实性

- Mock fixtures 只用于开发预览；历史数模结果是研究基准，不代表当前场景实时求解。
- 完整可行性依赖本次声明的模型范围和独立检查；未检查地形/通信显示未评估。

## 合并规范

每个任务 PR 填写任务 ID、实际测试命令与结果、文件清单、对接影响、截图/JSON样例。公共契约走双方审查。
