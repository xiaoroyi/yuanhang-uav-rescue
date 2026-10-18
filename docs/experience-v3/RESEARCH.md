# 参考调研与实现取舍

2026-10-19已访问用户4个来源，并查QGroundControl与现有组件的原始资料。第三方内容只作参考，不执行其安装/飞控指令。以下不是独立审计或竞品性能测评，不在首页声称同行缺少功能或虚构领先百分比。

| 来源 | 可借鉴 | 本项目实施 |
|---|---|---|
| [Fuselab Drone Forge](https://fuselabcreative.com/our-projects/drone-forge-uav-mission-control/)、[用户参考](https://fuselabcreative.com/get-inspired/uav-mission-control-dashboard/) | 地图为主、机队/飞行状态分层、天气准备与通信拓扑 | 自主实现布局；案例图片版权保留，不复制其成品素材；原参考页正文抓取受限，相关官方案例可读 |
| [DroneAI](https://github.com/SpaqiTechnologies/DroneAI) | 飞行状态、下一航点、事件日志、仿真与飞控分层 | 仅参考信息组织；README自称MIT而许可证文件待证，未复制代码/媒体，不把README功能数当已验证质量 |
| [autonomous-drone-sar](https://github.com/Nihara-D/autonomous-drone-sar) | 地图、实时状态、搜索与任务动作分离 | 仿真优先及运输阶段呈现；不复制未知许可代码 |
| [Altnautica Command](https://www.altnautica.com/command) | 规划/飞行/三维分视图、逐机记录与导出 | 参考公开交互组织，自主代码；GPLv3项目代码未复制，不连接飞控 |
| [QGroundControl稳定版Plan View](https://docs.qgroundcontrol.com/Stable_V5.1/en/qgc-user-guide/plan_view/plan_view.html) | 地形剖面与统计切换，计划与飞行来源分开 | 原始DEM/航段爬升下降可见；计划、模拟、未知值清晰 |
| [Ant Design Steps](https://ant.design/components/steps/)、[Tour](https://ant.design/components/tour/) | 显眼步骤、完成状态、引导定位 | 复用现有Radix，无需引入重复大框架 |
| [shadcn/ui](https://github.com/shadcn-ui/ui/blob/main/LICENSE.md)、[Lucide](https://lucide.dev/license) | 组件层级/图标一致性 | 使用现有Radix/Lucide/ECharts/Three；CSS/SVG动效自主实现、尊重减少动态效果；无复制模板源码 |
| [shadcn-admin](https://github.com/satnaing/shadcn-admin)（MIT） | 侧栏、统一留白、命令搜索、表格与内容分层 | 参考真实开源后台的信息架构，继续使用现有Vite/Radix组件；新增Ctrl K任务/功能导航。不整库复制，不替换正确业务架构 |
| [Tabler](https://github.com/tabler/tabler)（MIT）、[官方预览](https://tabler.io/preview) | 清晰卡片层级、简洁行表、轻量摘要和图标语义 | 实际查看官方预览图，采用浅色操作面、深色侧栏、克制强调色。未引入Bootstrap或复制商业模板 |
| [Motion React](https://motion.dev/docs/react-animation)、[Radix Colors](https://www.radix-ui.com/colors/docs/overview/usage) | 成熟动效与语义色阶 | 安装项目依赖并保留锁文件；动态主页/计算反馈尊重减少动态效果。未安装收费服务 |

现有库的实际版本以frontend/package-lock.json为准；涉及使用的素材和许可随本文件更新。Fuselab浏览器页面自动截图遇到超时，未声称看过不可读的完整实景；Tabler官方预览通过图像查询实际查看。本项目界面必须实际截图查看。代码及SVG/CSS素材自主实现，帮助截图与录屏来自本项目，不下载别人的界面图充当产品。
