# A 算法模块

遵守根 AGENTS。维护算法、适配器、独立检查与实验，跨共享契约先 RFC。先读 docs/05、LEGACY_BASELINE_AUDIT与IMPLEMENTATION_STATUS。当前已有public_api，不重新搭空壳。

保持纯 Python JSON 边界，不 import backend，不在导入时写文件、下载数据或运行搜索。路径从配置/参数进入，禁止绑定个人绝对路径。先封装已核验物理模型，再做快速初解。独立验证不能只复用优化器的 passed 布尔结论。adapters/joint_patterns.py仅提取历史分组与驻点候选；其私有pattern_only记录没有可行性，必须经当前物理、联合排程和独立检查后才能发布。

物理在physics.py，题设数据适配器adapters/contest.py，独立重建检查validation.py，调度public_api.py。默认5点32箱，contest保留15点80箱；限时多起点、局部修复/全量回退已有真实测试。radio.py/relay.py/joint.py提供有限投影模型的连续通信与中继联合调度，小场景已验收，80箱历史模式候选已重新计算通过，一般搜索仍待提升；不要将私有运输松弛发布为联合可行方案。analysis.py/metrics.py只读分析绑定快照，口径见docs/RESOURCE_ANALYSIS.md与COMMUNICATION.md。真实耗时与证据存evidence/solver/。原题Q2/Q3不宣称全局最优，Q4必须继承同版Q3。单人跨模块授权见根AGENTS。

cp_pool.py为可选限时深入优化，继承已验算基线、只接受共同目标严格改善；不宣称全路线空间最优。routing.py为静态限制区可见图，规则见SPATIAL_ROUTING与RFC-003。assets.py提供只读terrain_store上下文与内容hash校验，通用DEM见TERRAIN_ASSETS与RFC-004；自定义资产目录需显式上下文，不绕过NoData/CRS/基准检查。

partition.py为冻结同版联合任务的有限完整枚举与独立分配核查，最多10个连通单元，仅同质满SOC/零时刻资源；不改原Plan或通信来源，不把配置缺口称重新调度时最少资源。接口与复现见FROZEN_PARTITION和RFC-007。

nominal.py由public_api导出analyze_single_site，额定单点能力、完整计数DP与基线/敏感性，只生成诊断批次，不是实体Plan。边界与独立重建见NOMINAL_ANALYSIS/RFC-009。replan必须接收完整Event并核对应用后版本/目标退出状态；局部直接影响集包含不可用机体和运输电池，沿两类资源依赖传播，非满SOC和通信等情况全量回退，见RFC-010。

bounds.py为只读运输架次容量下界，numerics.py固定原容量容差；validation用fsum重建容量，Fraction下界需保守包含容差与舍入保护。不得把架次数转为最少机体/电池数量。见CAPACITY_BOUNDS/RFC-011。

新增需求事件直接全量重算，不能仅修旧任务；中继能源组件退出由联合重算与独立检查覆盖。完整Event链见RFC-012/013。
