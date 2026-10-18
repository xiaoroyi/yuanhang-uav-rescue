# V2 仓库审计

日期：2026-10-18。基线 `d571853e375f7caf66bbd57985abed2362232fe8`；独立实施分支 `feat/mission-workspace-v2`。开始时工作树干净，没有重置、删除或覆盖用户修改。main 与 V1 分支保留。

## 已核实

- React / Vite / TypeScript strict、TanStack Query、MapLibre、ECharts、Three；FastAPI / Pydantic、SQLAlchemy / SQLite WAL、独立 Python 求解子进程。沿用锁文件和项目 `.venv`，不新增重复框架。
- 既有 Scenario→Snapshot→Job→Plan 已运行；Plan、Snapshot 不变，版本与事件有幂等检查，确认与预约在事务中。10 个领域 Schema，实际 OpenAPI 47 路径，HTTP 类型自动生成。
- 现有九个并列页面由 App.tsx 组织。真实路线、逐箱安排、机体/电池甘特、DEM 与高度剖面、通信联合排程、Q4 冻结配置、增配/压力试算可复用；导航不符合 V2 任务流程。
- 现有回放是只读计划阶段插值，非服务器业务执行。旧 Event 明确限全场景零时刻；不能直接用于在飞重规划。无 Execution、独立交付事实账本、DeviceAdapter 或设备指令网关。
- 本机运行数据位于 runtime，测试使用独立目录。新表采用增量 create_all，不改写既有 Plan/Snapshot JSON；V2 验证先用隔离 runtime。
- 资料原件与历史建模代码在 references，只读保留，不运行旧 bootstrap/env。

## 规范输入与差异

合订版按显式 source 标记导入唯一目录 docs/redesign-v2，来源与 SHA 见 SOURCE_IMPORT.json；六份规范与执行提示词已完整阅读。桌面仅发现旧 G0 ZIP，没有 V2 ZIP 或规范所述六张 0722xx 截图，因此不声称已查看它们。重构前视觉基线使用仓库既有 V1 截图及隔离浏览器实拍。

原包仍有 A/B/C、恢复三人职责的历史文字；本项目始终两人：A 算法与负责人，B 同一人前后端。用户最新授权覆盖旧模块范围和 G0 等待条款；不代签契约批准。

## 验证现状

V1 历史证据：dc6e8f5 完整 279 Python + 8 子测试、12 前端单元、36 浏览器；d571853 另跑 12 单元与 8 受影响浏览器。它们不代表 V2 已验证。V2 尚未运行的检查均不算通过，后续写 TEST_REPORT。

## 实施方向

先建立兼容 Mission、分组预检与独立 Execution/Fact/Command 契约，随后替换默认导航与任务工作区。保留已装载/在飞不可撤销前缀，以实际资源释放时刻对未来剩余需求重新求解并独立检查；不把旧零时刻 replan 偷换成执行接口。默认仅业务仿真，SITL/真机不连接。R00—R24 与 V01—V14 逐项追踪，外部数据/硬件依赖单列阻塞。
