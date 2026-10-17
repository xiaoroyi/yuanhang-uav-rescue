# 算法与后端 Python 接口草案

A 维护 `solver/public_api.py`，B 的 Worker 通过该入口调用。目前文件尚未实现，本页代码仅为签名契约。

```python
def solve(snapshot, options, progress_callback=None) -> dict: ...
def replan(snapshot, previous_plan, event, options, progress_callback=None) -> dict: ...
def validate(snapshot, plan) -> dict: ...
def capabilities() -> dict: ...
```

参数为只读 JSON-compatible Mapping，输出为 JSON-compatible dict；validate 返回 common/$defs/validation，其余分别按 solver-outcome/capabilities Schema。Solver 不访问数据库、HTTP、浏览器、不修改输入，不加载依赖私有服务器路径的环境。

## 输入和预算

Snapshot 必须完整嵌入 Scenario 并通过 hash/版本检查，SolverOptions 的 plan_id/snapshot_id 由后端分配且一致。requested_model_scope 至少包含 P0 七项，政策要求地形或通信时不能减少范围。只支持已经在 capabilities 声明的 objective 和物理 model_id，未知参数模型返回 INPUT_NOT_READY。

time_limit_s 是从函数入口到返回的墙钟总预算，包含本次预处理和独立检查。预处理、缓存命中、首个已验证候选、总运行时分别记录。A 应预留检查时间；Worker 可设置独立硬超时并清理子进程。多线程不可完全复现时记录版本、种子、线程数及边界，不承诺逐位相同。

progress_callback 接受 `{"stage": str, "elapsed_s": number, "candidate_count": int}`，这是进程内进度通知，不是 Plan，不做虚假百分比。业务实现时 A/B 在公共契约 PR 固定回调类型与可取消机制；G0 不声称回调、取消令牌已工作。

## 结果不变量

- FEASIBLE/OPTIMAL：非空真实 Plan，ID 原样回显，独立 validation=passed，has_validated_plan=true，必检项完整通过；最优性必须注明有限模型范围。
- INFEASIBLE：有指定模型的无解依据，plan=null。UNKNOWN：未证明无解，plan=null。
- 不支持范围或输入未就绪：UNKNOWN + unsupported_scope/input_not_ready + 结构化 diagnostics。
- 验证失败：ERROR + validation_failed，不能发布其候选 Plan；异常：ERROR + exception。Worker 补 request_id 并映射 failed Job，不泄露堆栈给 UI。
- 取消完成：内部 UNKNOWN/canceled；外部 Job canceled，solver_status=null，当前不保留可确认中间计划。

first_feasible_s 表示首个**独立检查通过**的候选时间，不是优化器第一次报告布尔可行。无该候选则 null，不能用 0 冒充。diagnostics 至少有 code/message，可附 field_path/object_id。

## 重规划

后端先应用事件并保存新版本快照，再把新 Snapshot、原 Plan、Event 和 mode=replan 的 Options 传入。两引用须完整、旧/新计划属于同一 Scenario，旧 Plan 不修改，新 Plan 绑定新快照，future sortie 不再引用故障实体。首版整个场景尚未执行，后续中途修复须先补执行事实契约。

## 旧算法适配

先读 `docs/LEGACY_BASELINE_AUDIT.md` 和 `references/modeling/README.md`。复制已核验物理函数至 solver adapter 并建立单测；不直接把 18 个提交文件包装成已独立可运行服务。它们有路径注入、导入建目录、旧输出依赖和有限模型假设。Q2/Q3 正式源码与旧问题目录不完全一致，必须跟随发布清单选择。

A-01 先交非 Mock 小场景输入和真实模型参数，A-02 真实计算并独立验证；到那时才增加 `fixtures/regression/` 和真实运行证据。不得把本轮人工画的 mock Plan 改标签当算法输出。
