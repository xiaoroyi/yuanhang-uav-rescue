# RFC-013 零时刻中继能源组件退出

状态：implementation-branch，用户已授权跨模块实施，待A/B复核；不伪造正式冻结。

Event联合新增relay_energy.unavailable，payload严格为{"component_id":"RE01"}，目标来自communication.relay_energy。运输battery_id、机体drone_id与中继component_id保持独立命名空间，不相互转换。旧三种事件JSON继续有效。

仅整个场景尚未执行、effective_time_s=0。目标须已配置且status为available或初始charging。纯状态转移只把其status改为unavailable，保留容量、SOC、SOH、位置和available_after_s；其他输入不改。事务、幂等、可信received_at、版本/快照/父Plan链与前两种退出事件相同。

启用连续通信的重规划始终全量重建运输和中继，独立检查不得继续引用退出组件。未找到可验证联合方案则不发布父Plan为当前结果。不可用组件不等于特定中继机退出，两类实体仍独立；未支持执行中换组件或实际返航状态。

前端在启用通信时提供“中继能源组件退出”，精确选择组件ID。事件时间线、中继甘特/任务表与联合指标反映新Plan。JSON/OpenAPI/Pydantic/TS同分支更新；Mock例使用独立通信Snapshot上下文，不修改旧开发样例。

验证包括精确字段与命名空间、未知/已退出目标、初始charging保留状态、不重置其他执行事实、幂等/回滚/预约、真实联合Worker重算与确认、旧快照保留、浏览器刷新恢复及1440/1280画面。A-10/C-08仍保留落点变更、未来封控及执行中状态范围。
