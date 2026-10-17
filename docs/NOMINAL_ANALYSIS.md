# 单点运输能力诊断

在“场景与资源”点击“单点运输诊断”。系统先为当前版本创建不可变Snapshot，再计算该快照的单站点往返能力。默认32箱得到6批；原题15点80箱在20%额定返航余量下得到18批、59.131296kWh。它对应原题Q1的额定运输模型，不能用这些批次直接确认执行。

## 模型与精确范围

每批只去一个需求点，去程带货、返程空载；使用机型声明的reference_energy_kwh、满SOC和100%SOH。保留当前地形、静态限制区、载荷相关航程、爬升能耗、准备/装载/交接时间。实体机体/电池库存、充电、并发、需求时限和通信由正式调度另行计算。

安全质量对每个站点与声明机型计算。若空载往返已超能源预算，capacity_kg=null、limit=empty_infeasible；满载可行则达到额定载重；否则对单调能耗二分到不超过1e-7kg的区间，取可行下界。体积上限独立保留，不以未知密度转换为质量。

同站、同物资类型、相同质量和体积的箱件可交换，压缩为计数类。完整枚举每个计数向量与声明机型，用动态规划依次最小化整数架次、总能耗、累计作业时长。能耗和时长的加总排序使用Decimal；物理本身仍为浮点模型。每站最多512个计数状态，超限、库存选择有歧义、路径未就绪或预算耗尽时明确limited/partial，不宣称完整模型最优。

只有完整有限模式中确实无可行组批时，单站status=infeasible；预算耗尽不是无解。整个报告partial时metrics=null，保留已完成站点的批次，不把局部结果冒充完整最少架次。

## 箱件与独立检查

available且位于基地的逐箱库存必须与每项正需求数量一致；本版本不选择多余库存。生成批次重新分配真实cargo_ids，NOM-*只是诊断批次标识。没有drone_id、battery_id或起飞时刻。

独立核查重新取箱件、两条航段和模型参数，检查唯一与完整覆盖、单站归属、质量、体积、能耗、额定SOC和作业时间，不信任优化器的passed标志；同样复核逐箱和贪心基线及敏感性组合。Mock、已有执行事实或关闭基地不能被重置后诊断。

单箱直送与确定性贪心是对照方法，不是全局最优。累计作业时长是各批“准备至返航”的和，不能叫机队完成时间。余量敏感性使用同一快照和模式库；切换参数不修改Scenario.policy。原题20%得到18批，30%得到20批，是当前输入真实重算结果。

## 接口与复现

GET /api/v1/snapshots/{snapshot_id}/single-site-analysis，min_return_soc为可选[0,1]诊断参数，缺省使用快照策略。NominalReport及消费者类型从实际OpenAPI生成，不改变Scenario/Plan契约。报告含原Snapshot内容hash、诊断参数和analysis_input_hash，运行耗时不是确定性身份的一部分。

```powershell
.venv\Scripts\python -m solver.nominal --example contest --output evidence/solver/nominal-contest.json
.venv\Scripts\python -m solver.nominal --example compact --output evidence/solver/nominal-compact.json
.venv\Scripts\python -m solver.nominal --scenario input.json --min-return-soc 0.3 --output diagnostic.json
.venv\Scripts\python -m pytest tests/solver/test_nominal.py tests/backend/test_nominal_api.py -q
```

CLI输出包含完整Snapshot和报告，拒绝输出覆盖输入场景。HTTP GET只读取已有Snapshot，不创建Plan、Job、确认或预约。前端Snapshot创建只发生于明确点击；切换余量不重复创建。

19项定向检查已通过，包含独立子集DP对照、改变箱重2批→3批、能力边界/不可达、破坏结果拒绝、超限/超时分类，以及场景改版后历史快照保持不变。浏览器已通过32/80箱、18→20批敏感性、导出与输入不变检查；全套回归计数以IMPLEMENTATION_STATUS和verification/latest.json为准。
