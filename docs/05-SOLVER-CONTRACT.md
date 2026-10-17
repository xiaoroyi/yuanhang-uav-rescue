# 算法与后端 Python 接口草案

A维护 `solver/public_api.py`，B的Worker通过该入口调用。目前已实现并有真实回归；本页规定稳定边界，实际范围见IMPLEMENTATION_STATUS与capabilities。只读playback辅助接口见RFC-002。

```python
def solve(snapshot, options, progress_callback=None, *, initial_plan=None) -> dict: ...
def replan(snapshot, previous_plan, event, options, progress_callback=None) -> dict: ...
def validate(snapshot, plan) -> dict: ...
def capabilities() -> dict: ...
```

参数为只读 JSON-compatible Mapping，输出为 JSON-compatible dict；validate 返回 common/$defs/validation，其余分别按 solver-outcome/capabilities Schema。Solver 不访问数据库、HTTP、浏览器、不修改输入，不加载依赖私有服务器路径的环境。

## 输入和预算

Snapshot 必须完整嵌入 Scenario 并通过 hash/版本检查，SolverOptions 的 plan_id/snapshot_id 由后端分配且一致。requested_model_scope 至少包含 P0 七项，政策要求地形或通信时不能减少范围。只支持已经在 capabilities 声明的 objective 和物理 model_id，未知参数模型返回 INPUT_NOT_READY。

time_limit_s 是从函数入口到返回的墙钟总预算，包含本次预处理和独立检查。预处理、缓存命中、首个已验证候选、总运行时分别记录。A 应预留检查时间；Worker 可设置独立硬超时并清理子进程。多线程不可完全复现时记录版本、种子、线程数及边界，不承诺逐位相同。

progress_callback接受 `{"stage": str, "elapsed_s": number, "candidate_count": int}`，这是进程内通知，不是Plan，不做虚假百分比。当前Worker原子写入进度文件，Windows短暂读取竞争有界重试；取消由后端终止独立子进程并等待退出，再标canceled。

## 结果不变量

- FEASIBLE/OPTIMAL：非空真实 Plan，ID 原样回显，独立 validation=passed，has_validated_plan=true，必检项完整通过；最优性必须注明有限模型范围。
- INFEASIBLE：有指定模型的无解依据，plan=null。UNKNOWN：未证明无解，plan=null。
- 不支持范围或输入未就绪：UNKNOWN + unsupported_scope/input_not_ready + 结构化 diagnostics。
- 验证失败：ERROR + validation_failed，不能发布其候选 Plan；异常：ERROR + exception。Worker 补 request_id 并映射 failed Job，不泄露堆栈给 UI。
- 取消完成：内部 UNKNOWN/canceled；外部 Job canceled，solver_status=null，当前不保留可确认中间计划。

first_feasible_s 表示首个**独立检查通过**的候选时间，不是优化器第一次报告布尔可行。无该候选则 null，不能用 0 冒充。diagnostics 至少有 code/message，可附 field_path/object_id。

## 限时深入优化

`mode=improve` 在快速构造后使用 OR-Tools CP-SAT 对有限路线池重分箱件并联合安排机体/电池。可选只读 `initial_plan` 必须为同一快照、相同目标的真实 Solver 方案，并重新通过独立检查。HTTP 使用独立 `SolveRequest.initial_plan_id` 加载它，不向核心 SolverOptions 暗加字段；旧三参数调用保持兼容。

搜索采用10毫秒向上取整的资源占用时间网格、单线程和显式种子。共同目标先比较逐箱优先级加权期望延期，再比较所选时间/能耗/均衡目标；只有完整浮点物理重算通过且严格改善时才替换有效基线。有限池状态OPTIMAL仅说明该离散池模型；对外仍为FEASIBLE，不声称全路线空间全局最优。非满初始SOC、预算不足或整数范围过大时跳过该优化，保留快速方案。取消仍取消本次Job，旧Plan保持不变。

可选resource_limits要求ground_resource检查；准备/端口容量、初始补能与等待的语义见RFC-005和GROUND_RESOURCES。满初始SOC的深层模型支持Cumulative容量；非满初始SOC仍有真实有限日历构造与独立检查，深层阶段不暗重置SOC。

实现和同预算真实输入证据见 `solver/cp_pool.py`、`evidence/solver/deep-compact.json`、`deep-contest.json`。间隔模型参考 [OR-Tools调度文档](https://developers.google.com/optimization/scheduling/job_shop)。

启用连续通信时，先产生具有独立ID的私有运输松弛，再联合安排有限运输模式与悬停候选，最后重建中继物理/能源、资源并发与全阶段链路。松弛不保存为用户联合方案；旧metrics保持运输口径，联合目标使用joint_metrics。高级初始状态与80箱搜索提升仍在任务板。真实边界、默认参数和验收见COMMUNICATION.md及RFC-006。

## 重规划

后端先应用事件并保存新版本快照，再把新Snapshot、原Plan、完整Event和mode=replan的Options传入。核对Schema、Scenario、event.expected_state_version+1等于新版本、目标确实已退出、父Plan来自真实已验证来源。机体退出和运输电池退出均受支持，负载严格区分，详见RFC-010。旧Plan不修改，新Plan绑定新快照，不引用退出实体。运输局部修复同时识别两类资源直接影响并沿依赖传播；不适用或失败时在剩余预算内全量回退，通信走全量联合重算。整个场景必须尚未执行，中途修复须先补执行事实契约。

## 旧算法适配

只读analyze_single_site(snapshot,min_return_soc=None)由public_api导出，纯Python实现见nominal.py。它返回额定单点NominalReport，不是solve outcome或可确认Plan；完整范围、有限计数DP与独立检查见NOMINAL_ANALYSIS及RFC-009。调用不会重置实际实体状态或修改快照。

先读 `docs/LEGACY_BASELINE_AUDIT.md` 和 `references/modeling/README.md`。复制已核验物理函数至 solver adapter 并建立单测；不直接把 18 个提交文件包装成已独立可运行服务。它们有路径注入、导入建目录、旧输出依赖和有限模型假设。Q2/Q3 正式源码与旧问题目录不完全一致，必须跟随发布清单选择。

A-01/A-02已有非Mock输入、当前物理模型、真实调度和独立验证，运行证据位于evidence/solver，回归位于tests/solver。fixtures/mock保留开发结构示例，不能改标签冒充算法输出；当前能力与限制见IMPLEMENTATION_STATUS。

## 只读容量下界

solver.bounds.capacity_lower_bound(snapshot)计算完整运输架次容量必要下界，solver.analysis.analyze将其加入capacity_bound。无HTTP/数据库副作用，严格复用Snapshot输入校验。数值与独立见证见CAPACITY_BOUNDS/RFC-011。不是最少实体资源或完整调度最优证明。
