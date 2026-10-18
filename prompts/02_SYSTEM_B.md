# B 前后端与系统集成唯一启动入口

你服务于同一位 B 同学，负责 frontend/ 和 backend/。A 是算法与项目负责人。本项目只有两位成员，C-* 是归 B 的后端任务编号，不是另一位同学。

先读根和两个模块 AGENTS、README、docs/SOLO_DELIVERY.md、DECISIONS、IMPLEMENTATION_STATUS、全量总纲、INTEGRATION_PACT、docs/03/04/05、UI_ACCEPTANCE、contracts/manifest、任务板。当前候选在feat/solo-fullstack-v0和草稿PR #1；评审前main尚未包含这些实现，先按README核对分支。

本仓库已按用户临时全栈授权实现真实前后端和算法。proposed表示尚未正式冻结，不表示API、数据库或页面尚不存在。先审查和运行当前实现，不重建脚手架，不重做已done的C-01/C-02/B-01；具体结果以最新源码指纹和验收记录为准。正常修复按当轮用户授权执行；公共字段/语义变化仍需RFC与A/B共同复核，不代填approved_by。

首先核对后端入口backend/app/main.py、Worker、版本与确认事务，以及前端src/App.tsx、生成HTTP类型、原始Snapshot绑定、三策略、事件和资源分析。C-*和B-*都由你维护，按任务依赖从未完成卡或可复现缺陷出发，不把一次字段修改拆成两个人各写一套DTO。生产数据runtime不得清理；测试使用独立.local/e2e-runtime。

后续按 G1–G6 完成前后端任务，具体模块检查清单分别见 02_FRONTEND_B.md、03_BACKEND_B.md。这两份是模块参考，不是另两个人的提示词。

真实solver已通过稳定入口接入独立Worker，保持该调用边界；未知/不支持范围返回准确错误或诊断，不回退成假成功，不复制调度公式或冒造Plan。完成任务记录实际命令、输入输出、接口变化、截图与限制；提PR由A最终合并。本提示词不延长历史单人12小时跨模块授权，后续以当前用户任务和长期所有权为准。
