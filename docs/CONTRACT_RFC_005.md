# RFC-005 准备工位与有限充电端口

状态：implementation-branch，待团队复核。本分支用户授权实施，旧数据继续回归。

Scenario可选resource_limits={prep_slots,charging_ports}，均为正整数。缺省沿用旧无限地面容量；两字段单位为可同时服务的实体数，不表示起降许可或飞行避碰。配置存在时强制ground_resource检查，相关model_scope/validation枚举兼容增加该值。

Plan.sorties可选charge_start_s，有限模型必须填写，满足return_s<=charge_start_s<=battery_released_s。电池占用包含返航后的等待，实际充电占用[charge_start_s,battery_released_s)，两段模型计算充电时长；机体释放仍与充电分离。准备工位占用[prepare_start_s,takeoff_s)。所有区间左闭右开。

Plan可选initial_charges数组，元素battery_id/start_s/end_s/from_soc/to_soc。有限模型对基地可用/充电中且SOC不足1的合格电池先安排补满，明确记录等待与充电窗口，随后才能使用；这是一项保守的计划策略，不是对已发生充电的遥测重建。不可用电池不调度。初始补能不算运输架次，飞行能耗指标不包含未知充电电网损耗。

Solver联合安排准备和返航充电；独立验证重算初始/返航充电时长、首次SOC、等待时序、实体占用和两类并发峰值。图表/报告区分排队等待与真正充电。未配置容量的旧Plan不补字段，旧Snapshot/hash不变。HTTP请求自动补必检范围；Pydantic/OpenAPI/TS同批生成。

限时CP-SAT可在满初始SOC时加入准备与充电Cumulative约束、包含等待的电池可选区间；非满初始SOC继续用可验证构造解，保留已有基线，不假装深层模型已覆盖。局部重规划需保留地面窗口并重新验算；不适用的状态全量回退。

此次不实现起降位、并行着陆、空域隔离、充电功率/温度曲线及已执行事实；这些约束不能由prep_slots替代。容量开关/编辑创建新Scenario版本，旧计划不可继续确认。
