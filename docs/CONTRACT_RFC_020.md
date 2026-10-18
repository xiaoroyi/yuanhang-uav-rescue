# RFC-020：执行事件纠错与游标续传

状态：V2实施中，协议待团队复核。既有事件、事实和Plan不覆盖。

事件新增只读投影withdrawn、resolved_at与resolution_reason；新POST `/executions/{id}/events/{event_id}/resolve` 仅接受暂停/待开始的本机simulation误报核实，需expected_revision、幂等键、withdraw_misreport动作和至少10字符依据。已采纳事件不能撤销，正在应用或未确定的设备变更不能绕过。原execution.event/input保持不变，另增execution.event.resolution审计记录。真实风险不能以“继续旧方案”确认消除；真实设备权限仍未开放。

执行视图兼容增加applied_event_ids，界面与服务器据此区分待处理/已采纳/误报。开始、继续、手动推进统一检查待处理事件，不能绕过冻结事实去交付未来任务。修复只重放未撤销事件，但候选指纹包含纠错投影，纠错使旧候选过期。

SSE支持非负cursor与Last-Event-ID，超前游标明确409并要求重新读取快照。连接先核实执行存在，再返回流；同步数据库读取使用线程池避免阻塞异步事件循环。重连只发送cursor之后的不可变事实，遥测会话/序号与事实游标分开，不重复写交付。数据包明确connected，失联样本保留stale。

这不实现任意在飞故障改航，不声称完成真机部分应用恢复。完整任务包与只读重载将在独立RFC补齐。
