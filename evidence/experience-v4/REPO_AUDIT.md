# V4 初始审计

- 起点：`f49911e`，V3分支已推送，开始时工作区干净。
- 架构：React/TypeScript/Vite + Motion/Three/MapLibre；FastAPI/SQLite/独立求解子进程；纯Python多起点/约束优化/独立检查。
- 首页：旧SVG示意，淡绿主题，正文1280px限宽；新首页需要独立布局，工作台保持可读。
- 引擎：现有系统没有EoH提供器；SolveRequest、SolverOptions、Plan均需兼容扩展，旧JSON不回填。
- 资产：有真实任务、版本、方案、事件和执行归档；案例库应复用这些记录，避免另一套重复数据库。
- 接入：现有SimulationAdapter和设备指令状态机可复用；不能把HTTP202或仿真状态称为真机连接。
- 保护：不修改main/V2/V3历史，不覆盖生产runtime；开发和检查在`.local/v4/`隔离实例。
- 本轮预算估计：6–8小时，实际持续推进；采用针对性检查与真实页面截图。
