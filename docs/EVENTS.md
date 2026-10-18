# 零时刻动态事件与重规划

事件页支持运输机、中继机或运输电池退出。先生成真实方案，在“事件复盘 → 动态事件”选择事件类型和资源，再点击“记录故障并重规划”。系统保存新版本、生成不可变快照并真正重算，原Plan、原Snapshot和确认历史保留。

## 事件范围

当前只支持整个场景尚未执行、effective_time_s=0。存在已装载、预留、在途、已交付箱件，在飞机体或使用中电池等事实时，拒绝通过重新规划覆盖它们。页面回放始终是计划示意，不创建这些事实。

| event_type | payload精确形状 | 可退出目标 |
|---|---|---|
| drone.unavailable | {"drone_id":"U01"} | Scenario.drones或communication.relay_drones中的available机体 |
| battery.unavailable | {"battery_id":"BAT-A-01"} | Scenario.batteries中的available或初始charging电池 |

Event使用四个互斥Schema分支，旧机体事件JSON保持有效。不存在额外root包装；Pydantic/实际OpenAPI/TS由同一契约生成。混用负载、未知ID、非零事件时钟或用新事件ID重复退出已不可用目标均拒绝。

## 后端顺序与事务

POST /api/v1/events收到完整Event后，先按Scenario和event_id去重。相同请求重试返回首个结果、applied=false，即使当前版本已经增加；相同ID不同内容409。received_at由服务端写入，不参与幂等摘要。首次应用用实际接收时间验证occurred_at，未来发生时间不能留下接收早于发生的记录。

首次应用检查当前版本与整个场景执行事实，只改变目标status为unavailable，保留SOC、SOH、位置、available_after_s及其他资源。事务保存Scenario新版本和Event，清除当前规划预约及active_plan_id；不会删除原Plan或旧确认记录。失败时没有半个事件或新版本。

之后读取新Scenario、POST /scenarios/{id}/snapshots，再POST /solve-jobs，mode=replan、parent_plan_id=原Plan、event_id=刚应用的事件。后端核对Event应用后的版本等于新Snapshot，原Plan属于同一Scenario且版本更早。

## 纯Python与独立检查

replan(snapshot,previous_plan,event,options)同样要求完整Event，不接受历史试验中省字段的最小字典。核对Schema、Snapshot hash、Scenario、应用后版本、目标退出状态、真实已验证父Plan及Options身份链，失败返回UNKNOWN/input_not_ready，不进入搜索。

运输局部修复的直接影响集同时识别不可用机体和运输电池，再沿两类资源前序边扩大修复。每个候选重新独立验证当前输入；固定任务不能通过保留旧ID绕过资源可用性、能源或时限检查。局部不适用或未成功时用剩余预算全量回退；非满SOC初始状态走此回退，连续通信走完整联合重算。启发式没有最小变动证明。

新Plan不得引用退出电池或机体，必须完成全部必须保障需求并通过声明范围的独立检查后才可确认。未找到新方案时保留旧方案作为历史，不能用它确认新状态。

## 页面与证据

事件时间线标明资源类型与实际ID；新旧路线、保持架次、机体/电池改派箱件和指标变化来自各自真实Plan。刷新后恢复父Plan比较，加载原Snapshot期间不混入当前可变输入。

evidence/solver/battery-replan.json和joint-battery-replan.json保存浏览器真实退出前后Snapshot、Plan与Event。普通运输及连续通信两条流程均通过，联合新Plan模型内缺口为0，原Plan/hash保持。1440/1280截图位于evidence/browser/verified/*battery-fault*。

专项检查涵盖完整版本链、旧JSON兼容、负载互斥、接收时钟、幂等与事务、确认预约释放/重新确认、初始补能电池不被重置、其他资源执行事实，以及独立检查拒绝重新引用退出电池。完整测试计数见IMPLEMENTATION_STATUS。

已有点位的零时刻紧急插单已按RFC-012实现。中继能源组件退出已按RFC-013实现。落点变更、未来封控及执行中重规划尚未实现，保留在A-10/C-08，不能用当前事件负载自行追加字段。

## 紧急需求插入

“动态事件”选择“紧急需求插入”，打开表单，选择已有救援点和物资类型，填写1至32箱、每箱kg/L、优先级与相对场景零点的截止分钟。可留空截止，不把当前电脑时间当相对零点。新增需求为必须保障，同时登记同等数量的基地available实物箱件。新输入标为user_input，Mock仍为Mock。

Event类型demand.added，payload为demand与cargo_items，引用Scenario现有结构。新需求与箱件ID必须独立、类型/引用/位置/数量一致；未执行与零时刻限制不变。共享apply_event_to_scenario为纯函数，后端在同一事务保存新版本与事件、释放预约，旧记录不改。详见CONTRACT_RFC_012。

算法对这种事件直接全量重算全部需求，不能只修复旧任务而遗漏新货。页面新增“新增已安排箱件”，机体与电池改派仅比较两版共有箱件。原方案保留。若新增硬截止无法满足，新Job没有Plan；页面明确旧版，确认禁用。

本轮22项算法专项、12项新增API检查通过，连同旧电池/契约共46项通过、8 subtests passed；1条真实浏览器流程完成32→34箱、确认、刷新恢复，以及继续插入零秒硬截止后未发布旧方案。证据为evidence/browser/urgent-demand.json；专项计数不替代下一轮完整检查。

## 中继能源组件退出

启用通信时，在事件类型中选择“中继能源组件退出”，再选择精确component_id。Event为relay_energy.unavailable，payload仅component_id；运输电池ID不能代替组件。目标可为available或初始charging，状态转移只退出该组件，保留全部能源/位置参数。通信新方案全量重算，必须独立检查不引用已退出组件并保持要求的连续保障。见CONTRACT_RFC_013。

实际10项专项检查与1条联合浏览器流程通过；新方案模型内通信缺口0，旧快照/方案不变，新版本可确认和刷新恢复。1440/1280事件页及新能源窗口已查看，evidence/solver/relay-energy-replan.json保存完整前后输入、Event与Plan。专项首次运行有两项测试用法错误（coverage_gap_s字段名、可选communication应省略而不是null），已修正测试，未放宽业务检查。
