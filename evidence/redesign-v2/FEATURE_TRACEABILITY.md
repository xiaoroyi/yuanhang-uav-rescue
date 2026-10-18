# 功能迁移追踪（中间检查点）

R00—R24唯一状态源为docs/task-board.json；本表是迁移索引。复用旧代码不自动等于本轮全量通过。

| 功能 | 当前实现 / 新入口 | 本轮验证与缺口 |
|---|---|---|
| F01 创建复制版本 | missions.py + 原Scenario版本；首页/准备 | 新建/并发/版本已测，复制继续验 |
| F02 文件导入模板 | input-preview/template、InputImport | CSV/XLSX往返与GUI导入通过 |
| F03 需求库存箱件 | 原协议 + preflight/ExecutionFact | 库存缺口不造箱，事实与分配分离 |
| F04 机型实体电池 | 准备机队/资源中心视图 | 不兼容阻断、初始0.8SOC保留已测 |
| F05 地图联动 | RescueMap/MissionWorkspace | 点位抢选修复已测，50点/重合线待验 |
| F06 真实静态求解 | 原Worker/public_api | 新地区2箱和原小场景已算，原题回归待跑 |
| F07 超时取消 | 原Worker + 新作业条 | 实际2s UNKNOWN失败保留，非已证无解 |
| F08 时间能源比较 | 同快照Job/CompareCenter | 原双策略浏览器回归已过 |
| F09 甘特追踪 | ResourceTimeline/SchedulePage/stages | 原双资源保留，多源执行图深化中 |
| F10 动态事件 | 旧/events + 新/executions事件 | 命名空间/时钟严格分开 |
| F11 独立验证 | 原validate + preflight/采纳复核 | 剩余Plan和阶段合计已测 |
| F12 导出启动 | 原export/report/launch + 执行export | 原导出恢复已验；执行包重载待做 |
| F13 限制区 | 原routing/ZoneManager；准备区域 | 保留静态约束，时高扩展未具备 |
| F14 DEM资产 | terrain-assets/TerrainManager | 生产/maps修复，高级3D迁移继续 |
| F15 通信协同 | 原joint/radio + RFC018阶段/账本/模拟 | 静态联合模拟11项组合已验；联合在途窗口修复待做 |
| F16 多事件 | 旧4分支 + 执行退出/需求/落点 | 新库存/承诺阻断已测，气象事件待做 |
| F17 依赖修复 | affected_closure + 承诺前缀 | 实际剩余求解，未证明最小改动 |
| F18 地面容量 | 原resource_limits/what-if | 有限地面在途模型保守冻结，专项待验 |
| F19 多目标 | RFC016 | 新v2/旧v1不混配；费用无费率不启用 |
| F20 资源增配 | ResourceAnalysis；复盘资源 | 原真实反事实复用，新入口继续验 |
| F21 复盘差异 | ExecutionAnalysis/变更/事实 | 原事实保留、新箱交付已测；图与重载深化 |
| F22 Q4配置 | 原partition；复盘通信分区 | 冻结同版Plan模式保留，待本轮回归 |
| F23 压力稳健 | ScenarioExperiments；复盘资源 | 确定性试验不称概率；气象待做 |
| F24 学习模块 | R22保留 | 无新训练/消融，不显示AI成功 |
| F25 自动建图 | R23保留 | 缺航片/ODM运行链，不以底图充当建图 |
| F26 SITL遥测 | DeviceAdapter/SimulationAdapter/stream | 业务模拟已运行，SITL真机未配置 |
| F27 多基地 | R24保留 | 当前仍单基地，不以表单冒充模型支持 |
| F28 试用材料 | 新帮助/浏览器/截图 | 自动脚本不是3人试用，官方材料未完成 |

## V01—V14

| 图 | 当前数据/页面，限制 |
|---|---|
| V01 | 准备需求/库存/缺口；独立结构图待深化 |
| V02 | 条件检查NominalDiagnostics；单点不保证全局 |
| V03 | stages.sortie_loads → PlanInsights双利用率；无几何装箱 |
| V04 | ResourceTimeline/stages；多源执行对照深化 |
| V05 | 原电池/充电甘特，保留补能尾部 |
| V06 | PlanAnalysis.delivery/保障阶梯/截止余量 |
| V07 | FlightProfile/stages；高程载荷与SOC端点 |
| V08 | CompareCenter散点/表，不画虚假完整前沿 |
| V09 | 阶段能耗合计，当前运输口径，联合待补 |
| V10 | CommunicationPanel/Evidence来源窗口，模拟待补 |
| V11 | 现有压力试算；RFC-019人工W1情景/窗口与各机型限值，非概率或风致能源模型 |
| V12 | 依赖传播与真实增配，关系图深化中 |
| V13 | deviation_rows后端投影；新增箱基准null，图待接 |
| V14 | 原搜索日志与R16/R22，学习证据未具备 |
