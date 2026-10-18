# 06｜调研依据、成熟度判断与借鉴边界

研究日期：2026-10-18。下列来源为产品官方文档、项目作者仓库或论文原始页面。产品自述不等于本项目已验证的性能；开源 README 的测试数和“production-grade”称呼不作为可靠性结论。本次未对外部仓库安装、运行或安全审计。

## 1. 用户提供的四个参考

| 编号 | 参考                                  | 可据来源确认的内容                                           | 本项目借鉴                                   | 不照搬什么                                                   |
| ---- | ------------------------------------- | ------------------------------------------------------------ | -------------------------------------------- | ------------------------------------------------------------ |
| S01  | Fuselab UAV Mission Control Dashboard | 页面索引文本明确称为 concept，介绍中央三维地图、机队列表、遥测与状态面板；正文直接抓取受限 | 地图居中、信息优先级、等宽数值、克制的状态色 | 不当作可下载生产模板；不把概念图的漂亮程度当作工程可用性     |
| S02  | SpaqiTechnologies/DroneAI             | README 展示仿真启动、航点编辑、遥测、事件和多模块入口；存在合成回退相关自述 | 明确的开始步骤、地图对象编辑、仿真与接口分层 | 不沿用其未经本次审计的安全实现或“生产级”声明；不复制整库     |
| S03  | Nihara-D/autonomous-drone-sar         | 作者定位为基于 ArduPilot SITL 的搜索救援仿真，描述 WebSocket 遥测及 Next.js/FastAPI 界面 | 仿真先行、遥测驱动、接入与任务状态可见       | 视觉搜救不等于物资物流；不为追随 Next.js/Leaflet 重写现有 React/MapLibre |
| S04  | Altnautica Mission Control            | 官方介绍分离 Plan/Simulate/Configure/Fly/Review，并有协议适配、SITL 说明；称代码为 GPLv3 | 业务阶段分区、同一机队上下文、适配器能力     | 不做全部飞控参数配置/摇杆驾驶；复制代码前先核对许可证和依赖  |

S01 https://fuselabcreative.com/get-inspired/uav-mission-control-dashboard/  
S02 https://github.com/SpaqiTechnologies/DroneAI  
S03 https://github.com/Nihara-D/autonomous-drone-sar  
S04 https://www.altnautica.com/command

Nihara 仓库 README 写明 MIT License，但本次未审查所有文件、素材和依赖的许可；DroneAI 的完整复用许可同样需在实施前核对。这里“可参考”指交互思路，不表示对全部代码和素材作了许可或安全审计。Altnautica 的成熟度也只依据公开介绍，不称其已经通过真实灾害救援验证。

## 2. 成熟地面站和商业任务平台

**S05 QGroundControl Plan View**：规划页以地图、任务条目、地理围栏、备降点与地形剖面构成；规划与上传、飞行是不同动作。援航采用“准备—检查—方案—执行”的阶段分离，但上层是多机物资资源调度，不能把单机航点编辑当作全部优化。  
https://docs.qgroundcontrol.com/master/en/qgc-user-guide/plan_view/plan_view.html

**S06 QGroundControl Fly View**：监控和控制有单独视图，操作需要确认；Continue/Resume 语义不同，恢复航线可能需要重建相关设置。援航借鉴执行态独立与指令反馈；不泛化为所有机型均能原地悬停。  
https://docs.qgroundcontrol.com/master/en/qgc-user-guide/fly_view/fly_view.html

**S07 DJI FlightHub 2**：官方提供地图、任务、数据与协同能力介绍；单机场任务库文档区分计划/实际时间及未完成/已结束任务。援航应把地图放入任务上下文，计划与实绩分别保存，不能以“地图+任务管理”作为独创点。  
https://enterprise.dji.com/flighthub-2  
https://fh.dji.com/user-manual/en/task-plan-library/single-dock-plan-library.html

以上参考共同支持“功能按工作阶段组织、空间视图承载业务、计划与执行区分”。本包的救援任务向导、资源依赖修复、缺口归因和检查失效机制是面向援航的设计推导，不是逐字复刻这些产品。

## 3. 地图、图表与测试实施依据

**S08 MapLibre GL JS**：官方提供地形渲染、悬停弹窗和 feature-state 交互能力。援航优先保留单一 MapLibre 主地图，通过分层数据和选择状态提高可用性。  
https://maplibre.org/maplibre-gl-js/docs/examples/3d-terrain/  
https://maplibre.org/maplibre-gl-js/docs/examples/display-a-popup-on-hover/  
https://maplibre.org/maplibre-gl-js/docs/API/classes/Map/  
https://maplibre.org/maplibre-gl-js/docs/API/classes/Popup/

**S09 PMTiles/Protomaps**：PMTiles 可作为浏览器地图的底图、专题及地形瓦片来源，MapLibre 有对应协议插件。支持形式不代表任何来源瓦片都允许离线分发。  
https://docs.protomaps.com/pmtiles/maplibre

**S10 OpenStreetMap 公共瓦片政策**：`tile.openstreetmap.org` 不允许批量预抓及离线包用途。援航离线包应使用许可适当的数据和自托管/允许离线的服务，不能用脚本批量抓公共端点。  
https://operations.osmfoundation.org/policies/tiles/

**S11 CesiumJS**：官方 flight tracker 和 SampledPositionProperty 提供带时间的位置播放能力。仅当确实需要绝对高度三维航迹时，再懒加载独立三维审查器；不要将模型地形夸张用于净空计算。  
https://cesium.com/learn/cesiumjs-learn/cesiumjs-flight-tracker/  
https://cesium.com/learn/cesiumjs/ref-doc/SampledPositionProperty.html

**S12 Apache ECharts**：dataset 支持数据与渲染配置分离及多序列复用。援航由后端/算法给出统一数据集，图表只映射，避免页面各算一遍业务指标。  
https://echarts.apache.org/handbook/en/concepts/dataset/

**S13 shadcn/ui**：可使用 Sidebar、Dialog、Tabs、Sheet 等现成构件和 Blocks 作为外壳；不能直接采用营销模板作为调度布局。优先复用当前组件库，不并装三套 UI 框架。  
https://ui.shadcn.com/blocks  
https://ui.shadcn.com/docs/components/sidebar

**S14 Playwright**：官方提供截图断言/视觉比较。本项目增加可操作的业务 E2E、DOM 几何检测和人工视觉验收；自动更新快照不等于界面合格。  
https://playwright.dev/docs/test-snapshots

**S15 OpenDroneMap**：官方输出包含正射影像与 DSM/DTM 等。航测建图是异步数据处理链，不是“换一张底图”，输出仍要质量与坐标基准检查。  
https://docs.opendronemap.org/outputs/

**S16 高德坐标转换**：官方区分 WGS84/GCJ-02 等坐标及转换接口。若接入国内底图，必须用适配层处理展示坐标与计算坐标，不能简单叠加。  
https://developer.amap.com/api/javascript-api-v2/guide/transform/convertfrom

## 4. 气象、真机与协议依据

**S17 Open-Meteo**：文档提供温度、降水、风速风向、不同高度风变量等；支持变量随模型不同。免费托管 API 用于非商业用途，商业部署需核当前服务条款；数据署名要求与服务使用范围分别检查。数值模式网格预报不能当作山谷航段现场实测。  
https://open-meteo.com/en/docs  
https://open-meteo.com/  
https://open-meteo.com/en/docs/single-runs-api

**S18 DJI FlyCart 30 规格**：厂家提供机型、风、温度、载荷等参数及测试条件。援航只用它证明应保存机型适用条件与参数来源，不把某个机型限值复制给所有设备。  
https://www.dji.com/flycart-30/specs

**S19 MAVLink Command Protocol**：ACK 的 accepted 表示飞控受理并尝试执行，不是动作已完成。界面必须分离受理、设备应答、状态确认。  
https://mavlink.io/en/services/command.html

**S20 MAVLink Mission Protocol**：任务上传和执行进度有独立协议；部分上传存在飞控差异，不能假设所有设备支持通用的空中任务热替换。  
https://mavlink.io/en/services/mission.html

**S21 MAVSDK Missions**：提供任务上传、开始、暂停和进度相关接口，任务插件支持范围有边界。援航先实现能力可检测的 SITL/适配测试。  
https://mavsdk.mavlink.io/main/en/cpp/guide/missions.html

**S22 PX4 Safety**：飞控有任务可行性、失效保护与返航等机制。调度平台不能取代飞控底层保护；停止排程、暂停任务与停止电机不是同一动作。  
https://docs.px4.io/main/en/config/safety

**S23 DJI Cloud API / WPML**：提供 MQTT/HTTPS/WebSocket 接入与航线文件规范，支持设备/动作需查兼容表。不能由 Cloud API 支持某些 Matrice 推断必然支持 FlyCart 或任意运输平台。  
https://developer.dji.com/cloud-api/  
https://developer.dji.com/doc/cloud-api-tutorial/en/api-reference/dji-wpml/overview.html  
https://developer.dji.com/doc/cloud-api-tutorial/en/api-reference/dji-wpml/waylines-wpml.html

## 5. 创新定位所需的研究参照

**S24 LENS（2024 预印本）**，Learning-Enhanced Neighborhood Selection for the Vehicle Routing Problem with Time Windows：用学习选择大邻域搜索的破坏/修复区域。援航可参考这一机制，用轻量模型选择修复动作；不能宣称“ML+LNS”由本项目首次提出。  
https://arxiv.org/abs/2403.08839

**S25 HDNF（2026 预印本）**，A Heterogeneous Dual-Network Framework for Emergency Delivery UAVs: Communication Assurance and Path Planning Coordination：摘要描述应急配送、通信支撑网络与路径的联合优化。说明“运输+中继通信”已有近邻研究，援航需强调实体电池/执行状态/依赖修复及其真实实验。本文仅用其摘要定位，不复述未经阅读全文核验的细节或代码可用性。  
https://arxiv.org/abs/2604.12501

**S26 BER（2026 预印本）**，Robust Energy-Aware Routing for Air-Ground Cooperative Multi-UAV Delivery in Wind-Uncertain Environments：摘要讨论时变风下的能量与返航可行性。援航增加返航可达约束，但不称“考虑风”本身就是新颖研究。本文没有把该工作认定为已录用顶会或已复现基线。  
https://arxiv.org/abs/2604.13441

**S27 Codex 官方工程经验**：给出明确上下文、可验证任务和可运行环境，比笼统要求“一次做成商业级”更可操作。本包提供自动拆任务、真实测试、截图与继续执行规则。  
https://openai.com/business/guides-and-resources/how-openai-uses-codex/

## 6. 用户材料的使用位置

- 六张界面截图：信息架构、首屏占用、地图/时间轴位置、提示文字、场景上下文的观察依据。未从截图推断后台故障。
- `INTEGRATION_PACT.md`：保留快照、实体 ID、纯 Python 求解入口、单位与状态原则；改变默认导航和计划/执行组织。
- `CODEX_MASTER_HANDOFF.md`：F01–F28 功能范围继续追踪，本包给出迁移/补充与验收。
- 《D26106140150(1).pdf》：图3.7、3.8、4.4、4.6–4.11、5.5–5.13、6.2–6.8等转化为交互分析视图。论文数值属于原题固定条件下结果，不植入新任务页面作为计算输出。
- 原题第2–4问及论文7.2节：用于区分单基地、同型电池、简化能耗/气象、连续通信模型与现实执行边界。

## 7. 调研结论

最值得吸收的是成熟系统的“工作顺序、上下文、状态与地图联动”，而不是首页特效或面板数量。援航不必成为另一款完整地面站；其价值是把救援需求、整箱物资、有限机体、电池与中继转换成有依据的多机资源计划，并在执行环境改变时帮助人快速做可核验的调整。
