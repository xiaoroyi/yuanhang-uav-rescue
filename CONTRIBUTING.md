# 两人 Git 协作

A 维护算法并最终合并；B 维护前端、后端与系统集成。每人各自 clone，不共享同一个 Git 工作目录。

当前候选在`feat/solo-fullstack-v0`与[草稿PR #1](https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1)，main保留原初始状态。评审前切换到该功能分支；第一次clone可加`--branch feat/solo-fullstack-v0`。先读docs/SOLO_DELIVERY.md与IMPLEMENTATION_STATUS，不从G0重新创建业务模块。

## 每个任务的流程

候选合并main后，按下列正常流程创建任务分支；评审期间从团队已接受的候选提交开分支，并在PR说明基线。

```powershell
git switch main
git pull --ff-only
git switch -c feat/solver-A-01
# 修改后检查文件，避免把资料缓存或密钥一起暂存
git status
git diff
git add solver docs/task-board.json docs/08-TASK-BOARD.md
git commit -m "feat(solver): A-01 适配基础物理输入"
git push -u origin feat/solver-A-01
```

在 GitHub 创建 PR，写任务 ID、验收结果和接口影响，A 审核合并。B 的任务分支例如 `feat/system-C-01` 或 `feat/frontend-B-01`。历史规范初始化分支为`docs/g0-governance`；其规则已包含在当前候选中。

已有未提交改动时先检查，不直接切回主分支拉取；有冲突先保留双方工作并解决，不用 `reset --hard`、强推或复制覆盖规避。更新功能分支可合并最新 `origin/main`，不改写已共享的提交历史。

## 谁改什么

| 路径 | 主要 owner | 审查 |
|---|---|---|
| `solver/`、算法实验 | A | B 检查对接影响 |
| `backend/`、`frontend/`、运行部署 | B | A 检查算法调用与验收 |
| `contracts/`、根规范、CI | A/B | 双方确认公共语义 |
| `references/` | 原文归档 | 只追加来源与核验，不原地修改旧源码 |

小范围文档纠错可直接提 PR。字段、单位、状态、计算含义变更必须 RFC。首次契约冻结要在 `DECISIONS.md` 留下两位成员的明确决定，再更新 manifest 的版本/状态/批准信息；Codex 不能自行签字。

## 状态与证据

任务状态只用 `todo/in_progress/blocked/done`。`done` 必须有验收证据；完成资料复制不等于跑通算法，完成 CI 配置不等于 GitHub CI 已执行。更新 `docs/task-board.json` 后执行 `python scripts/render_task_board.py`，不要只改展示表。

共享字段的 PR 应包括 Schema、fixtures、Python/TS 生成类型、OpenAPI、受影响测试与文档；尚无对应模块时写清未来生成任务，避免声称同步已经完成。

## GitHub 设置

CODEOWNERS 目前只填已知账号 `@xiaoroyi`；B 的用户名待补。它用于请求审查，不能代替分支规则。A 可在仓库设置中配置 PR 和 CI 合并要求；是否支持具体保护选项以仓库实际账户/套餐为准。当前未修改远程设置。
