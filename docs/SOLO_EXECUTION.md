# 单人全栈实施记录

用户2026-10-17明确授权在feat/solo-fullstack-v0跨模块开发并安装普通项目依赖，持续12小时推进高质量系统。起点为3319ad5，main保持不变。两人长期分工仍为A算法、B同一人负责前后端。

默认本机Windows离线演示，无登录和外部服务依赖；较小真实场景展示动态调度，保留原题15站80箱入口。现有0.1.0-draft作为本分支实施基线，不代替团队审批。新增接口/兼容扩展随实现记录，并留团队复核。

实施顺序：环境→纯算法与真实小场景→SQLite/API/独立Worker→三页前端真实闭环→双策略、确认、事件/重规划/导出→浏览器精修与负例→按数据条件深化地形/诊断/稳健等→完整回归、启动与交接。

环境：Windows x64；选择已有Python3.11.15创建仓库.venv，Node24.16.0/npm11.13.0。禁止修改共享Conda环境。UI按React/Vite/TS、Radix、Tailwind、MapLibre、ECharts与lucide统一；后端FastAPI/Pydantic/SQLAlchemy+SQLite，独立子进程；算法保留题设能耗与充电公式，限时搜索+独立检查。

外部软件文档参考：FastAPI官方后台任务/部署说明、Vite官方Getting Started、MapLibre官方Style Specification与GeoJSON API、Google OR-Tools官方CP-SAT状态说明。具体安装版本与运行结果以锁文件和evidence记录为准。
