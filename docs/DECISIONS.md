# 决策记录

决策必须注明来源和状态。提议不等于批准，Codex 不替成员签字。

| ID | 状态 | 内容 | 依据 |
|---|---|---|---|
| D001 | confirmed | 两人：A 算法兼负责人；B 同一人承担前后端和集成 | 用户 2026-10-17 明确更正 |
| D002 | confirmed | 以开发方案为范围，G0 先建规则、接口、全量任务，不大规模实现业务 | 用户本次授权与初始化提示词 |
| D003 | confirmed | 资料放在同一项目仓库内，保留来源，筛选数模有用文件 | 用户提供路径及整理要求 |
| D004 | adopted_for_G0 | 保留旧 A/B/C 任务编号；C 只指后端任务，owner 为 B | 整理选择，便于追踪原总纲 |
| D005 | adopted_for_G0 | 只复制资料，不执行旧数模求解；`20260926_v4_excel1` 为历史主发布 | CURRENT_RELEASE、纸面和答案 SHA-256 一致 |
| D006 | proposed | Python 3.11/3.12、React/Vite/TS、FastAPI/Pydantic、SQLite、独立 Worker | 原方案建议；业务依赖尚未安装和锁定 |
| D007 | proposed | 首次契约 `0.1.0-draft`，P0 单基地、整箱、完整服务、station_end；事件仅场景尚未执行时机体退出 | RFC-001；比未来完整执行状态更严格 |
| D008 | proposed | 后端预分配 Plan ID；统一 `/api/v1/solve-jobs`，重规划也走该入口 | RFC-001；消除 Word 与 ZIP 的不同路由 |
| D009 | proposed | success outcome 必须独立验证通过；验证失败进入 ERROR，无 Plan 可发布 | RFC-001，消除原文含糊组合 |
| D010 | proposed | JSON Schema 派生业务类型，实现 OpenAPI 派生 HTTP 类型；双向结构检查而非手写重复模型 | C-01/B-01 实现，G0 仅固定流程 |

## 本次需要 A/B 确认的六项

1. **P0 范围**：单基地、完整服务、两种目标（time/energy）；部分保障、费用、中继和执行事实后续版本。全部后续功能仍在任务板。
2. **事件范围**：首版只允许整个场景尚无已装载/在途/已交付事实的 `drone.unavailable`；事件时钟显式 `effective_time_s`。要处理中途退出，先增加执行事实契约。
3. **数据格式**：审核 `contracts/` 草案，特别是 `drone_released_s`、`reserved_plan_id` 和能耗/充电 `model_id + parameters` 的注册与能力协商。
4. **结果与任务状态**：采用 RFC-001 的成功、无解、未知、异常、取消映射；成功只发布已验证候选。
5. **接口与类型**：采用 HTTP/Python 草案和类型生成职责；CSV/Excel 上传采用单独文件导入接口，不与 JSON 请求混成含糊 DTO。
6. **工程与合并**：确认建议技术栈、A 最终合并，补 B 的 GitHub 用户名。账号未补前 CODEOWNERS 不宣称已覆盖 B。

确认后由维护者附原话/PR 评论链接和决定，再将 `contracts/manifest.json` 改为 approved，选择正式版本并同步所有 fixtures。未收到答复不视作批准。
