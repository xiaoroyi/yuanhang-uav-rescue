# 展示与分析体验迭代

本轮承接v0的真实计算系统，按用户2026-10-18要求改进视觉、数据分析、地图、历史、新人使用和创新点呈现。长期仍为A算法、B同一人负责前后端。开发分支feat/experience-v1；最终验证后同步候选集成分支feat/solo-fullstack-v0，main仍由负责人评审合并。

本轮功能和完整集成验收已完成。当前八页面、真实高度分析及数据大屏的结果以本报告和evidence/verification/latest.json为准；v0记录保留为历史。

## 八个使用入口

| 入口 | 实际用途 |
|---|---|
| 数据大屏 | 可旋转三维DEM、点位地面高程、DEM分布、逐架次地形/巡航剖面、需求、物资、机体工作量、能耗/时长和SOC；查看精确数据，综合/详细与全屏展示 |
| 场景与资源 | 编辑或导入真实需求、逐箱库存、机体、电池与模型参数；保存产生输入版本 |
| 地图与地形 | 一键底图切换，GeoTIFF和完整资产包管理、覆盖/点位/高程概览；卫星与高程分开 |
| 调度工作台 | 保留真实求解、路线/箱件/甘特联动、确认与导出；快捷进入地图、分析、对比和历史 |
| 方案对比 | 选择/交换两份保存结果；独立时间与能源坐标轴、真实延期等指标、原始JSON；不同快照标为前后变化 |
| 事件复盘 | 保留零时刻资源退出、紧急插单、真实重规划和资源/冻结分区分析 |
| 历史档案 | 方案、输入版本、计算任务、事件和场景库；搜索筛选、打开历史方案、只读查看和下载版本 |
| 新手教程 | 六步流程与跳转、输入自查、三类地图数据说明、创新能力与适用边界、可搜索常见问题 |

左下/右上头像可编辑本机姓名、团队、职责与头像色；只保存在当前浏览器，不冒充已实现服务器登录/权限。主题、动态背景与页面路由可切换；导航支持URL片段、刷新与浏览器返回。历史方案选择按场景保存，缺失或其他场景的无效缓存会回退。

## 图表的数据依据

参考原数模论文的地形、需求、净空、调度、通信与分区图形语义，重新用当前Scenario、Snapshot和真实Plan出图；没有把论文历史数字写成当前计算。论文提取/相关页核对及真实浏览器结果见evidence/experience/analysis。

三维和高度边界见CONTRACT_RFC_015。高程显示资产声明的基准；采样、视觉倍率与地面投影均明确标注。方案分析绑定自己的快照，不套用后来编辑的输入；无方案、无DEM、WebGL不可用均显示实际空态或降级，不生成假结果。

时间/能耗策略可能得到相同方案，比较中保留真实原值；共同首目标为加权箱件期望延期，不用单项能耗差替代整体优劣。未评估指标保持未知。

## 地图来源和联网情况

用户给的“镇龙乡地理空间详情地图.html”是自包含D3/SVG与DEM/道路水系等上下文，内容并非卫星拍摄影像。本轮只读提取其真实坐标与图层，原始数据、数量及hash见evidence/experience/map的来源记录。

卫星使用Esri公开World_Imagery底图，显式开启并保留服务实际归属；不批量下载缓存，不标未核验拍摄日期。服务来源与条款：[服务元数据](https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer?f=pjson)、[Esri服务条款](https://www.esri.com/en-us/legal/terms/web-site-service)。卫星只用于观察，不替代DEM或灾后现势数据。外网受限时回退到离线底图，功能与实际联网验证的范围分别记录，不能把回退截图称为卫星加载截图。

三维运行时来自项目锁定的Three.js，沿用其[安装与附加组件方式](https://threejs.org/manual/pages/installation.html)，没有依赖外部CDN。首次新电脑安装需要联网，本机已经准备的计算与离线地图仍能断网运行。

## 验收与交接

最终统一命令：`.venv\Scripts\python scripts/verify.py --browser`。七项检查全部退出0，源码前后指纹一致，`passed=true`。此处只报告最后一次完整运行，不累加前面专项/失败/复测的计数。

| 检查 | 结果 | 实际耗时/秒 | 原始输出 |
|---|---|---:|---|
| Python业务/后端/算法测试 | 273通过、8项子测试通过；10条第三方弃用警告 | 383.452 | `evidence/verification/check-01.txt` |
| 契约检查 | 通过 | 0.683 | `evidence/verification/check-02.txt` |
| 协作规范检查 | 通过 | 0.948 | `evidence/verification/check-03.txt` |
| 前端ESLint | 通过 | 5.059 | `evidence/verification/check-04.txt` |
| 前端单元测试 | 9通过 | 0.649 | `evidence/verification/check-05.txt` |
| TypeScript与生产构建 | 通过 | 8.381 | `evidence/verification/check-06.txt` |
| 完整浏览器验收 | 33通过；unexpected/flaky/skipped均为0 | 897.07 | `evidence/verification/check-07.txt` |

原始浏览器报告为`evidence/browser/e2e-results.json`。最终文档和证据提交可晚于受测提交0f9e17b；功能、测试、契约和输入示例指纹保持不变，后续提交只整理交接与验收材料。

当前功能源码检查点为`fac7f62658a92ef7b25565499b02914e973f5096`。独立审查发现的高程tooltip空值误显示为0问题已修复，并增加真实ECharts回归；真实0仍显示0。审查记录在`evidence/experience/final-review/analysis-review.json`，另有独立只读接口/绑定审查`evidence/experience/release-audit.json`。

最终验收冻结在`0f9e17b88b91d1ad7157e9ff9101c90cd0aa408a`，相对fac7f626只加强刷新恢复测试。固定验证指纹为`d95f0d2e09503544e72961a6ef659a7e3b787444c45743394cb78188d56b913b`；前端指纹`fc30a7841a727df6041bde78d5c10ca3c2743809cd764c1f9ac44953f22d9256`与后端/算法指纹`ebd999da9fa9c62e65730ca38bd977e159c71f54723cb6ba542caec68eec0fd6`保持不变。原始冻结记录见`evidence/experience/source-freeze.json`。

功能检查点fac7f626的[Linux Application checks](https://github.com/xiaoroyi/yuanhang-uav-rescue/actions/runs/39092052081)已成功：273项Python、8项子测试、契约/治理、lint、前端单测/生产构建、生成类型漂移与两条生产浏览器烟测。CI浏览器unexpected/flaky/skipped均为0；原始下载报告为`evidence/verification/github-ci-fac7f62.json`及同目录带run编号的browser-smoke文件。远端烟测覆盖范围不代替本机完整浏览器回归。

首轮完整检查在tooltip修正期间启动，源码前后不同，且浏览器31通过、2失败，因此保留为失败检查点`evidence/experience/checkpoints/initial-source-changed-20261018`。其中一次15秒真实求解在形成完整候选前达到时限，正确返回UNKNOWN且没有Plan；页面再等待不会生成结果，也没有把历史结果当作新结果。另一条旧测试要求重复读取方案列表，已用原Plan/原Snapshot完整内容及导出身份一致、唯一原Job、零新增求解POST等更直接的断言替换。两条原始错误上下文/截图、trace hash及Job/Outcome核查均保留。

单独复测这两条流程已2/2通过，仍是原来的15秒预算，没有自动重试、降低业务断言或更改Solver状态，报告为`evidence/experience/workflow-recheck/results.json`。原因和边界见`workflow-review.json`及`solver-timeout-review.json`；历史耗时只用于排查，不构成性能保证，当前证据不能确诊一次超时是否由系统竞争导致。普通快速求解仍是有限15秒预算，通信默认60秒；UNKNOWN与无解严格区分，长预算可由算法/API参数指定。

本机生产版已通过`setup.py --check`、有效构建身份和已运行服务复用检查。`evidence/experience/production/browser-check.json`记录实际8000服务上的默认离线浏览：外部请求0、页面异常0、既有场景及方案读取前后未变，1440/1280/390均无页面横向溢出。八张实际生产截图已逐张目视检查，hash与范围见同目录`visual-review.json`；全屏六KPI与八图还由`analysis/overview-qa.json`提供独立元素尺寸记录。

### 立即查看新版

在本机打开`http://127.0.0.1:8000/#/analysis`，已有页面刷新即可。需要重新启动时双击仓库`start.cmd`；新电脑先按README安装依赖。建议选择已有方案的“默认演练 · 32箱动态调度”，进入“数据大屏”，点击“进入数据大屏”查看综合看板；“详细分析”可逐图查看准确数据与逐架次剖面。新导入场景先在“场景与资源”保存、按需到“地图与地形”绑定DEM，再运行真实求解。

新人直接打开`/#/guide`。左下头像编辑本机档案；地图页“管理DEM资产”导入GeoTIFF/完整资产包；“历史档案→输入版本”查看旧输入；“方案对比”挑选两份保存结果。需要同条件策略比较时，先在同一个快照运行不同偏好，不能把不同输入的前后变化解释为策略优化。

团队拿到仓库后先切到已验证的候选分支，再从它创建各自任务分支；默认main尚未自动合并本轮代码：

```powershell
git fetch origin
git switch feat/solo-fullstack-v0
git pull --ff-only
# 接手开发时，另建自己的任务分支，例如：
git switch -c feat/solver-next
```

A接算法，B同一人接前后端；先读AGENTS、IMPLEMENTATION_STATUS、任务板和RFC-015。本轮新增四接口均只读，旧Plan/Snapshot不迁移、不覆盖；本机数据库和DEM运行资产不靠git提交同步，已有导出/完整资产包与备份恢复流程继续使用。

预览：[全屏数据大屏](../evidence/experience/production/overview-1440.png)、[高度剖面](../evidence/experience/analysis/flight-profile-final.png)、[地图与导入](../evidence/experience/production/map-1440.png)、[使用教程](../evidence/experience/production/guide-1440.png)。

v0的15页HTML/PDF与录像保留为2026-10-18初版演示，原来源在Git提交8942a1d中可精确取得。本轮界面预览和证据位于evidence/experience，不把旧录像标为新界面实录。原算法/通信/事件模型范围及研究待办继续保留在IMPLEMENTATION_STATUS和任务板。
