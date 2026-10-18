# RFC-010 零时刻运输电池退出

状态：implementation-branch，用户授权实施，待A/B正式复核。是原事件协议的兼容扩展；保留原drone.unavailable JSON样例。长期两人职责不变。

新增event_type=battery.unavailable，payload精确为{battery_id:string}，只指Scenario.batteries中的运输电池。原drone.unavailable仍精确为{drone_id:string}，覆盖运输机和中继机。两种负载不能混用或同时给出；事件本身用Schema分支及实际生成类型表达，不以松散任意JSON替代。

事件仅适用于整个场景无已装载/预留/在途/交付等执行事实、effective_time_s=0的状态。退出将指定可用或正在初始补能的运输电池标成unavailable，不改变SOC、SOH、位置、可用时刻或其他实体。无此ID、重复的新退出事件或不支持的状态应拒绝；相同event_id和相同请求的幂等重试仍回原结果。

后端以自身接收时刻验证occurred_at，不能接受未来发生时间后又保存出received_at<occurred_at的记录；客户端received_at不参与幂等摘要，实际存储值由服务端填写。原事件的版本检查、不可变版本、预约清除、父Plan保留和快照链不变。

纯Python重规划验证事件类型、负载、Scenario/版本/目标退出状态及选项链。运输局部修复直接影响集同时包含不可用机体和不可用电池的原架次，按两类资源前序边传播；独立检查失败或非满SOC等不适用情况用剩余预算全量回退。联合通信仍全量联合重算。不能继续引用退出电池，也不能借事件重置执行事实。

前端事件类型可选机体或运输电池，目标选项只显示该类可用资源，事件时间线标明资源类型与真实ID。原始方案和比较仍保留，刷新可恢复。所有共享模型、实际OpenAPI、TS、fixtures、负例与浏览器流程一起更新。

本次不扩展中继能源组件退出、执行中故障、紧急插单、落点变更或未来封控；A-10仅部分完成，任务板保留其余范围。

事件顶层采用两个完整且event_type互斥的oneOf分支，避免条件校验在类型生成时丢失。生成后Event为Pydantic RootModel联合，model_dump仍输出原始JSON对象，不增加root包装。组合语义参考[JSON Schema官方说明](https://json-schema.org/understanding-json-schema/reference/combining)，根模型序列化参考[Pydantic官方文档](https://docs.pydantic.dev/latest/api/root_model/)；实际兼容性由旧fixture和HTTP负例验证。

迁移：数据库JSON形状和旧机体事件不变，无列迁移。Schema/Pydantic/OpenAPI/TS/消费者须同一分支一起发布；旧客户端未声明识别新电池事件，不能承诺单独升级服务端后旧客户端即可消费新类型。协议仍为未冻结草案，不伪造A/B签字。旧离线试验中缺字段的Event字典不属于完整协议，benchmark_replanning已补齐。
