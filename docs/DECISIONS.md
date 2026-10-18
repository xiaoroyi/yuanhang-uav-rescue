# 决策记录

决策必须注明来源和状态。提议不等于批准，Codex 不替成员签字。

| ID | 状态 | 内容 | 依据 |
|---|---|---|---|
| D001 | confirmed | 两人：A 算法兼负责人；B 同一人承担前后端和集成 | 用户 2026-10-17 明确更正 |
| D002 | confirmed | 以开发方案为范围，G0 先建规则、接口、全量任务，不大规模实现业务 | 用户本次授权与初始化提示词 |
| D003 | confirmed | 资料放在同一项目仓库内，保留来源，筛选数模有用文件 | 用户提供路径及整理要求 |
| D004 | adopted_for_G0 | 保留旧 A/B/C 任务编号；C 只指后端任务，owner 为 B | 整理选择，便于追踪原总纲 |
| D005 | adopted_for_G0 | 只复制资料，不执行旧数模求解；`20260926_v4_excel1` 为历史主发布 | CURRENT_RELEASE、纸面和答案 SHA-256 一致 |
| D006 | proposed | Python 3.11/3.12、React/Vite/TS、FastAPI/Pydantic、SQLite、独立 Worker | G0技术建议；目前已按分支授权实现并锁定依赖，正式团队批准仍待复核 |
| D007 | proposed | 首次契约 `0.1.0-draft`，P0 单基地、整箱、完整服务、station_end；事件仅场景尚未执行时机体退出 | RFC-001；比未来完整执行状态更严格 |
| D008 | proposed | 后端预分配 Plan ID；统一 `/api/v1/solve-jobs`，重规划也走该入口 | RFC-001；消除 Word 与 ZIP 的不同路由 |
| D009 | proposed | success outcome 必须独立验证通过；验证失败进入 ERROR，无 Plan 可发布 | RFC-001，消除原文含糊组合 |
| D010 | proposed | JSON Schema 派生业务类型，实现 OpenAPI 派生 HTTP 类型；双向结构检查而非手写重复模型 | C-01/B-01 实现，G0 仅固定流程 |
| D011 | confirmed | 本轮在feat/solo-fullstack-v0临时跨算法、前端、后端和工程集成持续实现候选版本，不改写main；长期A/B两人职责不变 | 用户随后明确授予12小时单人全栈开发范围，覆盖G0历史停止条款 |
| D012 | confirmed | 默认这台Windows电脑本地离线演示、无需登录；较小真实场景优先展示动态调度，保留原题入口 | 用户对两项环境/演示选择的明确答复 |
| D013 | adopted_for_branch | RFC-003至014已按用户授权在候选分支实施并测试；机器Schema和生成消费者同步，正式契约批准与main合并仍待A/B | CONTRACT_CHANGELOG、对应RFC与真实验收；不代填approved_by |
| D014 | confirmed | 完善视觉、动态背景、实用高度分析与数据大屏、地图导入/分析、历史、方案对比、教程和简单本机档案；卫星影像允许联网；main不改写 | 用户2026-10-18的新一轮功能要求，以及“可以，卫星图允许联网”的明确答复；长期仍为A算法、B一人前后端 |
| D015 | adopted_for_branch | 在feat/experience-v1按RFC-015增加只读DEM表面、原Plan高度剖面与输入版本读取，生成OpenAPI/TS；本机档案仅浏览器资料，卫星仅显示底图；最终验证后同步候选集成分支 | RFC-015及EXPERIENCE_RELEASE；不改核心Scenario/Snapshot/Plan或数据库结构，不代签契约冻结；浏览器卫星实际显示仍受环境网络策略限制 |

## 本次需要 A/B 确认的六项

以下为G0留下的正式审批项，不代表当前没有实现，也不是当前能力清单。用户随后明确授权单人全栈分支开发及本轮体验完善；当前技术栈、真实OpenAPI/生成类型和兼容扩展的事实见IMPLEMENTATION_STATUS及RFC-003至015。D006至D010仍未代替A/B签字，正式冻结与最终合并留待双方复核；不要因本节历史提议重新搭建或停止已授权开发。

1. **P0 范围**：单基地、完整服务、两种目标（time/energy）；部分保障、费用、中继和执行事实后续版本。全部后续功能仍在任务板。
2. **事件范围**：首版只允许整个场景尚无已装载/在途/已交付事实的 `drone.unavailable`；事件时钟显式 `effective_time_s`。要处理中途退出，先增加执行事实契约。
3. **数据格式**：审核 `contracts/` 草案，特别是 `drone_released_s`、`reserved_plan_id` 和能耗/充电 `model_id + parameters` 的注册与能力协商。
4. **结果与任务状态**：采用 RFC-001 的成功、无解、未知、异常、取消映射；成功只发布已验证候选。
5. **接口与类型**：采用 HTTP/Python 草案和类型生成职责；CSV/Excel 上传采用单独文件导入接口，不与 JSON 请求混成含糊 DTO。
6. **工程与合并**：确认建议技术栈、A 最终合并，补 B 的 GitHub 用户名。账号未补前 CODEOWNERS 不宣称已覆盖 B。

确认后由维护者附原话/PR 评论链接和决定，再将 `contracts/manifest.json` 改为 approved，选择正式版本并同步所有 fixtures。未收到答复不视作批准。
