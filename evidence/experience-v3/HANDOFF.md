# 接手V3

当前分支`feat/mission-experience-v3`，基于V2的58e81df；首个体验提交61ca772，后续修复和交接以分支HEAD为准。main/V2保留。长期两人：A算法兼负责人；B一人维护前后端与集成。

先读根AGENTS、docs/IMPLEMENTATION_STATUS、当前索引、API_MIGRATION_MAP、TEST_REPORT及docs/task-board.json。不要从G0或三人模板重新初始化，不覆盖现有算法/原题材料/旧Plan与Snapshot。

## 代码位置

- operations/App、LandingHome、ExperienceUI、CommandPalette：独立首页、主题/背景、任务导航与搜索。
- ResultsWorkspace / schedule_export：独立结果表、详情、CSV、六表Excel。
- TerrainWorkspace / TerrainScene / StageCharts：真实DEM、阶段升降、净空和能耗剖面。
- CommunicationWorkspace / RadioCoverageExplorer / radio_coverage：联合通信、真实模型空间点。
- TaskResources / ArchiveCenter：任务资源归属、执行导出与外部只读档案。
- FleetOperationsPanel / execution-progress / simulation：运输守恒、每机状态与可解释模型指标。不要只用剩余快照计算总箱数。
- HelpHub和public/help/v3：图文、视频和字幕；生产托管路径见main.py，需保留显式媒体MIME与Range。
- RFC030/031与生成的OpenAPI/操作Schema/HTTP类型：保持同次更新，不手写第二套DTO。

## 运行与开发

正常使用`start.cmd`，8000服务已更新。生产runtime保留13场景/26快照/29方案/3任务/3暂停实例，已做一致备份和原文Hash检查。备份及旧dist位于本机`.local/v3/`，不上传数据库或依赖目录。

改前端时用项目Vite开发环境；正式交付重新构建并检查源码身份。改后端后重启自己启动的服务，先确认PID/路径/启动时刻，不盲杀端口或清理数据。

可复查的快速命令：

```powershell
.venv/Scripts/python -m pytest tests/backend/test_experience_v3.py tests/backend/test_execution_confirmation_v3.py tests/backend/test_ui_media_v3.py -q
npm.cmd --prefix frontend run typecheck
npm.cmd --prefix frontend run lint
node --test frontend/tests/unit/execution-progress.test.mjs
```

需要重录完整流程时，先在8014启动隔离后端（YUANHANG_RUNTIME指向项目.local下的新目录），在5176启动前端并令YUANHANG_API_URL指向8014，再运行`scripts/v3_experience_review.mjs`。脚本固定使用这两个隔离端口；新环境会真正创建并求解通信案例，不依赖私有.local文件或用历史结果顶替。它会写入新截图和教程，不要对生产数据目录运行。

## 后续优先级

按原任务板继续研究、设备、跨基地等工作。模型/验收口径变更先写RFC与迁移映射；不要把后台受理标成设备执行完成，也不要把采样网格或有限最优标成完整认证。正式合并和契约批准由A/B复核。
