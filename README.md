# 援航 · 无人机救援调度

当前正在 `feat/mission-workspace-v2` 实施新版任务流程与服务器仿真。根地址为独立首页，任务内部按准备/规划/执行/复盘组织；V1兼容入口保留。继续开发先读 [V2索引](evidence/redesign-v2/INDEX.md)、[准确进度](evidence/redesign-v2/HANDOFF.md)；下文V1发布与测试是历史证据，不能代替V2最终验收。两人A算法、B一人前后端不变，main不改写。

本地运行的灾害应急运输与通信规划系统。编辑逐箱物资、需求与实际机队，真实求解，查看地图、三维地形、飞行高度剖面、调度安排与资源甘特，比较时间/能耗/时间能耗折中策略，并在资源退出或紧急插单后重新规划。默认5点32箱动态演练，保留原题15点80箱入口。

候选集成分支为 [feat/solo-fullstack-v0](https://github.com/xiaoroyi/yuanhang-uav-rescue/tree/feat/solo-fullstack-v0)，由[草稿PR #1](https://github.com/xiaoroyi/yuanhang-uav-rescue/pull/1)供A/B评审；main保留原状态。本轮在 `feat/experience-v1` 完善九页面与分析体验，验证和同步情况见 [体验迭代交接](docs/EXPERIENCE_RELEASE.md)，已推送提交以PR为准。范围、测试与未完成功能以 [真实实现状态](docs/IMPLEMENTATION_STATUS.md) 为准。输出是在声明模型内的规划辅助，不发送飞控指令。

## 本机直接使用

Windows双击 **start.cmd**，浏览器打开 **http://127.0.0.1:8000/**。已有依赖和构建时无需联网，不需登录。关闭服务窗口停止运行；数据保存在项目 runtime/，重启保留。

本轮新增 **调度安排**：逐架次、逐箱交付、中继排程，支持机体筛选、CSV、逐站时间/箱件、甘特与地图联动。新版计算直接取舍时间/能耗，并显示期望延期代价；旧方案保留v1标记，可点击“按新规则重新计算”。动态光流/粒子可用顶部星光图标暂停。规则、真实实测与验收见[策略与调度补充交付](docs/STRATEGY_V2_RELEASE.md)。

更新代码后启动器会识别旧后端和过期前端；本机数据可用backup.cmd备份并恢复到独立目录。安装检测、版本检查、备份/恢复见 [本机运维](docs/LOCAL_OPERATIONS.md)。

第一次使用先打开左侧 **新手教程**，跟随六步指引；也可阅读 [本机操作手册](docs/DEMO_RUNBOOK.md)。演示顺序：生成真实方案 → 点击架次/甘特联动 → 计算能耗策略 → 检查报告/确认/导出 → 事件复盘选择机体 → 记录故障并重规划。场景页可编辑物资重量、电池SOC/SOH或导入JSON/CSV/XLSX，再重新计算。

左侧共九个入口：**数据大屏、场景与资源、地图与地形、调度工作台、调度安排、方案对比、事件复盘、历史档案、新手教程**。数据大屏提供可旋转三维DEM、点位高程、地形分布、逐架次地形/巡航高度剖面、需求与库存、工作量、能耗/时长和SOC分析，支持综合看板、详细图表与全屏。图表使用当前输入或方案绑定的原始快照；无DEM、无方案和未知值会明确显示，不套用论文历史结果。

在 **地图与地形** 上传GeoTIFF或导入完整资产包，查看覆盖与点位高程，切换离线底图和联网卫星影像。卫星需主动开启，只作观察，不参与高程和净空求解；浏览器外网受限时回退离线图。本环境尚未验证完整卫星影像在浏览器中成功显示，具体检查边界见 [体验交接](docs/EXPERIENCE_RELEASE.md)。原题道路、水系与村镇图层可离线查看；原HTML地图并非卫星照片。

在 **历史档案** 搜索方案、输入版本、计算任务与事件，打开历史方案，或只读查看/下载某一输入版本；在 **方案对比** 选择两份真实结果查看时间、能耗、延期等指标。同快照才作策略比较，不同快照明确标为前后变化。左下头像可编辑本机姓名、团队、职责和头像色，仅保存在当前浏览器；系统不需要登录，也未实现多用户认证。顶部可切换深浅主题与动态背景。

另有可离线放映的 [v0系统演示材料](deliverables/README.md)：双击demo.cmd打开单文件HTML，或阅读PDF。这些HTML/PDF和录像保留初版界面，归档提交为 `8942a1d`，没有重新录制本轮八页面；当前界面截图见 [体验交接](docs/EXPERIENCE_RELEASE.md)。正式比赛模板和PPTX仍需后续整理。

事件复盘中的“资源分析与试算”提供真实占用图、期望延期/硬截止余量、增配与能耗/SOH情景、有限准备工位/充电端口增配、三档压力测试和可恢复历史；每个试算均保存独立输入并真实计算，见 [统计口径](docs/RESOURCE_ANALYSIS.md)。

已有方案可继续“深入优化30秒”，沿用同一快照并保留有效基线，见 [算法范围](docs/DEEP_OPTIMIZATION.md)。场景页可管理静态限制区，真实绕行见 [空间模型](docs/SPATIAL_ROUTING.md)；也可上传本地GeoTIFF，地图与净空使用同一绑定栅格。交接给队友时一并下载/导入完整DEM资产包以保留hash，见 [资产说明](docs/TERRAIN_ASSETS.md)。

场景设置可启用有限准备工位与充电端口，真实安排初始补能、返航排队与资源预约。甘特图展开后可查看完整等待/充电窗口，口径见 [地面资源](docs/GROUND_RESOURCES.md)。未启用时保留原题允许并行充电的模型。

场景页“配置通信资源”可开启连续通信与中继联合求解，提供真实中继位置、服务窗口、能源组件和独立覆盖检查。32箱和原题80箱均已有当前模型下的完整可行解；80箱使用历史分组候选并重新排程、验算，未宣称全局最优。用法和有限模型边界见 [通信协同](docs/COMMUNICATION.md)。

联合方案可在“事件复盘 → 冻结任务分区”比较2/3组的专用资源、工作量和共享损失，展开峰值证据及实体分配。它保持原任务与通信关系，资源不足时明确列出需增配数量；见 [分区口径](docs/FROZEN_PARTITION.md)。

场景页“单点运输诊断”提供额定安全载重、真实箱件组批、基线和返航余量敏感性。它对应单点运输物理模型，未分配实际机体/电池；执行前仍须正式求解。模型和独立CLI见 [诊断说明](docs/NOMINAL_ANALYSIS.md)。

事件现支持整个场景尚未执行时的零时刻机体、运输电池或中继能源组件退出，以及已有点位的紧急需求与实物库存插入。普通运输和联合通信均真实重规划，保留原方案；页面区分新增安排与原箱件的机体/电池改派。事件范围、完整版本链和能源状态保留见 [事件说明](docs/EVENTS.md)。Linux CI增加类型漂移和两条浏览器烟测，范围见 [自动化检查](docs/CI_CHECKS.md)。

新电脑首次需要Python3.11或3.12、Node.js24；联网运行 setup.cmd。若没有 py 启动器，使用相应Python执行 `python scripts/setup.py`。Linux/macOS运行 `python3.11 scripts/setup.py` 后 `.venv/bin/python scripts/launch.py --open`。安装不修改全局Python环境。

## 开发和验收

在仓库根目录执行；Windows用 npm.cmd 避免PowerShell脚本策略问题。Linux/macOS将 `.venv\Scripts\python` 换为 `.venv/bin/python`，npm.cmd 换为 npm。

```powershell
# 开发模式，分别在两个终端运行
.venv\Scripts\python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
npm.cmd --prefix frontend run dev
# 开发界面 http://127.0.0.1:5173/

# 业务与契约回归
.venv\Scripts\python -m pytest tests -q
.venv\Scripts\python scripts/check_contracts.py
.venv\Scripts\python scripts/check_governance.py
npm.cmd --prefix frontend run lint
npm.cmd --prefix frontend run test:unit
npm.cmd --prefix frontend run build

# 浏览器验收：首次需安装项目内Chromium
.venv\Scripts\python scripts/setup.py --with-browser
npm.cmd --prefix frontend run test:e2e
```

E2E使用独立8011/5174端口与 .local/e2e-runtime/ 数据库，不覆盖演示数据。报告和截图在 evidence/browser/。日志、依赖环境、缓存和数据库不提交。

修改共享契约或HTTP接口后重新生成：

```powershell
.venv\Scripts\python scripts/generate_models.py
.venv\Scripts\python scripts/export_openapi.py
node frontend/scripts/generate-types.mjs
```

算法可独立执行：`.venv\Scripts\python -m solver --example compact --seconds 15 --output evidence/solver/run.json`。`--example contest` 为原题完整运输实例；没有HTTP或数据库依赖。

## 无前置记忆的协作入口

先读 [AGENTS.md](AGENTS.md)、[完整开发总纲](docs/CODEX_MASTER_HANDOFF.md)、[接口细则](docs/INTEGRATION_PACT.md)、[真实实现状态](docs/IMPLEMENTATION_STATUS.md)、[任务板](docs/08-TASK-BOARD.md)。然后读模块AGENTS、数据/HTTP/算法契约和相关RFC。

长期两人分工：A算法和最终合并；B同一人负责前端、后端、数据与集成。B-*是前端任务号，C-*是后端任务号。初版单人跨模块授权见 [实施记录](docs/SOLO_EXECUTION.md)，本轮体验完善授权与边界见 [决策记录](docs/DECISIONS.md)；未把草案契约标为团队已批准。

| 目录 | 内容 |
|---|---|
| solver/ | 纯Python物理、调度、独立验证、只读展示数据 |
| backend/ | FastAPI、SQLite、版本/Job/Worker/确认/事件/导出 |
| frontend/ | React/TypeScript、八页面、离线/卫星地图、三维地形、图表与甘特 |
| shared/、contracts/ | 同一套Schema检查、生成类型、HTTP实际快照与历史设计草案 |
| fixtures/ | 明确标为mock的开发样例，不冒充算法结果 |
| tests/、evidence/ | 自动化回归与真实运行证据 |
| references/ | 原方案、讨论、论文/答案/题设数据与只读源码，含来源hash |
| docs/、prompts/ | 全量任务、决策、规范和两人接手提示词 |

原数模历史结果不是当前优化器输出。资料来源见 [索引](references/README.md)；Git协作见 [CONTRIBUTING.md](CONTRIBUTING.md)。使用功能分支和PR，保留 main，不force push。

资源分析现提供[运输架次容量必要下界](docs/CAPACITY_BOUNDS.md)，绑定原快照并导出精确比值与箱件见证；它不能用于推算最少机体/电池数量。

初版 [操作录像说明](deliverables/README.md)包含v0生产构建的真实求解、策略对照、电池退出重规划和导出，附中文章节与字幕。原始视频为WebM，模型内规划演示，不是实飞记录；它不代表本轮新界面已经录制。

工作台另有“均衡偏好”，与时间/能耗方案共用当前快照。可导入submission/examples/scenario-preferences.json演示清空软截止但保留硬截止的取舍，实际原始结果与范围见 [策略实验](docs/EXPERIMENT_RESULTS.md)。接手先看 [当前体验交接](docs/EXPERIENCE_RELEASE.md)，初版算法、运行和验收历史见 [v0全栈交接报告](docs/SOLO_DELIVERY.md)。
