# V4 设计与数据来源研究

核查日期：2026-10-19。研究只读公开资料；没有调用外部模型、天气服务或真实设备。

## 首页与界面

- [Magic UI仓库](https://github.com/magicuidesign/magicui)，MIT；实际查看其官网和组件源码：[Particles](https://github.com/magicuidesign/magicui/blob/main/apps/www/registry/magicui/particles.tsx)、[Animated Beam](https://github.com/magicuidesign/magicui/blob/main/apps/www/registry/magicui/animated-beam.tsx)。借鉴稀疏粒子、流动连线、滚动进入、克制的光效与卡片层次。本项目重新编写CSS/Three/Motion实现，没有复制付费Pro模板或其宣传指标。
- [Altnautica Mission Control](https://www.altnautica.com/command)：参考地图主视觉、任务流程和独立操作面板的表达；其开源控制站为GPLv3，本轮没有复制其源码、截图或品牌素材，也不声称援航具备其飞控能力。
- 新首页为原创任务指挥视觉，Three读取项目实际DEM与基地/需求点坐标；高度显示×8、连线为流程示意。首页不显示假遥测、假保障率或编造的效率提升。资产计数来自本机SQLite聚合。
- 动效使用已有Motion、Three和CSS，没有引入第二套动画框架。暂停开关、系统减少动态效果、不可见/后台暂停与资源释放同时处理。

## 字体与离线分发

- [Fontsource](https://github.com/fontsource/fontsource)的`@fontsource-variable/inter`及`@fontsource-variable/noto-sans-sc`，按lock文件固定版本。字体为OFL-1.1，随本地应用分发，不使用运行时字体CDN。许可原文纳入`frontend/public/THIRD_PARTY_NOTICES.txt`。
- 英文/数字Inter Variable，中文Noto Sans SC Variable。按unicode-range加载所需子集；新工作空间默认深蓝主题，保留已有明暗偏好。

## EoH：方法与本项目实现区分

- [官方EoH](https://github.com/FeiLiu36/EoH)，MIT；当前main使用`LLMConfig/EoH/BaseProblem`，区别于旧`Paras/EVOL`。官方方法结合进化与LLM设计启发式，并不等于本项目已完成进化实验。
- 在线实现为本地评分提供器；内置`eoh-seed-v1`明确标为人工规则初始化。`scripts/eoh_offline.py`提供离线适配、候选评估和不可变发布；未执行`--run`或外部API。导入包中的进化记录为提供者声明，本机只核验格式、数值与实际求解，不自动认证模型训练成果。
- 策略只调整可行候选的排序；容量、时间、电池、地形、通信与独立验算仍由原模型处理。不承诺每次优于标准搜索，不引用官方其他问题的提升幅度为援航背书。

## 演练初始化

- 核心计算数据：仓库原题地理、DEM、机型、库存及已有小规模演练；保留原题15点80箱。所有新建任务独立，结果必须重新计算。
- [OpenTopography SRTM目录](https://portal.opentopography.org/datasetMetadata?otCollectionID=OT.042013.4326.1)与[引用政策](https://www.opentopography.org/citations)：作为新增区域DEM资料入口，没有下载/替换本机DEM。导入GeoTIFF仍需显式CRS、高程参考、覆盖和质量检查。
- [Open-Meteo历史气象文档](https://open-meteo.com/en/docs/historical-weather-api)：数据采用CC BY 4.0，服务使用条件另行核对；本轮只提供配置和来源入口，没有请求天气API。现有人工气象模式不代表外部预报或风致能源模型。
- [Copernicus EMSR517](https://mapping.emergency.copernicus.eu/activations/EMSR517/)：2021-07-13激活的德国西部洪灾制图事件，作为洪涝补给需求的背景资料。演练仍用项目区域坐标和合成优先级，不将德国灾情搬成镇龙乡实测数据，不转载影像/矢量。
- 初始化四类：山地断路、洪涝分级补给、运输通信协同、原题多点急送。明确“项目计算数据/公开背景/资料入口”，不称大规模真实业务历史库。
