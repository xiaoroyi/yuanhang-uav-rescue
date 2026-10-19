# V4 接手与交付

分支`feat/mission-command-v4`，起点f49911e，核心功能3ff456e，最新收尾提交见Git日志。不要切回旧分支覆盖当前数据；main/V2/V3未合并或重写。

本轮交付：全宽动态指挥首页与真实地形、离线中英文字体；可选标准/EOH本地评分、不可变包导入导出与同输入比较；有来源的四类演练、最近/历史任务资产及输入复用；实际模拟适配器与API接入目录。原调度安排表、Excel、地形剖面、通信、执行承诺与独立检查继续保留。

内置EOH包来源为rule_initialization。它确实参与候选评分，不代表已经完成LLM进化、训练或普遍提升实验。默认标准引擎；普通计算不调用模型。官方框架离线适配入口是scripts/eoh_offline.py，后续实施真实进化前需明确预算、数据划分和模型配置，不能把接入检查当研究成果。

接手先读docs/PROJECT_DOSSIER.md，再读根/模块AGENTS、docs/IMPLEMENTATION_STATUS.md、本目录限制、唯一任务板、RFC-032及相关Schema/实际OpenAPI。可复制提示词为prompts/06_CURRENT_PROJECT_HANDOFF.md。Word由主Markdown生成，本轮已同步1.1/V4；不要单独维护第二套事实。

主要实现位置：

- 前端operations/CommandHome、TerrainCommandScene、CaseLibrary、EngineCenter、IntegrationCenter；MissionWorkspace/CompareCenter接入引擎与对比，command-home/workspace.css负责独立首页和共享外观。
- backend/app/case_library.py、integrations.py、models/jobs/worker/experiments及执行重排继承；runtime/heuristics是导入包存放位置。
- solver/engines.py与policies/eoh-seed-v1.json；AST仅有限数值表达式，纯求解器不依赖后端。策略trace记录实际调用和回退。
- scripts/backup.py新增策略包备份与原字节恢复，旧清单兼容；scripts/eoh_offline.py默认无网络。

基本运行见DEMO_GUIDE。本机8000已切至V4，实际后端源码与前端构建身份匹配，129个静态产物核对通过。升级前31份Plan、34份Snapshot的原文hash全部保留，各表数量不变，4个执行实例保留3暂停与1完成。备份在.local/v4/production-backup/，清单及SHA记录在production-data-after_deployment.json。个人任务、数据库、备份和导入策略不会随GitHub克隆；需用一致性备份另行交接。生产只读页面检查见release-smoke.json。开发验证使用.local/v4/runtime，与生产隔离。

工作区同时出现了独立传统基线实验材料及EXP-C01任务。其目录与任务内容保留，本轮提交仅包含V4自身修改；不代替该项的作者提交、核验或结论。

后续按用户目标选择任务：真实离线进化数据划分/消融、联合在途通信修复、更多地形/气象适用组合、真机/SITL等。外部依赖与尚未验证边界详见KNOWN_LIMITATIONS。不要从G0重建，不把提供者声明或公开灾情背景当项目实测数据。
