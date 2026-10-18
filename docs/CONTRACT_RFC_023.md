# RFC-023：模拟设备持久状态、独立读回与受控启用

状态：后端隔离工作分支验证通过，合回V2时同步前端消费者并验证；合同仍待团队复核。只适用于business simulation，不开放硬件/收费/厂商接口。

问题：原通用Command按经过时间写“读回成功”，没有独立设备状态，也允许已归属执行但未获采纳的候选被直接mission.activate。新的完成判定必须由实际模拟状态证明，不能仅从请求回显或计时器推断。

新增DeviceMissionState与`simulation.device_state`持久存储：execution_id/device_id、revision、uploaded_plan_id/compiled SHA256、active_plan_id、最近上传/启用指令、更新/观测时间、明确simulation/无真实设备。CommandView兼容增加observed_state；DeviceApplication增加activation_command_id，以及真实expired/rejected上传状态。新增GET `/executions/{id}/devices/{device_id}/mission-state`按执行归属查询，不能跨执行控制。

上传先独立重验Plan、仅编译未来未装载架次。SimulationAdapter受理返回ACK；服务器调度器实际写入独立设备状态，之后read_mission_state核对上传Plan/SHA才标succeeded。未来程序的active_plan_id与当前已承诺架次来源是两个口径，不能据此声称任意在飞机体已替换航路。

通用mission.activate只能核对已被当前执行采纳的目标；其它候选返回409 ACTIVATION_APPROVAL_REQUIRED。新候选仍须走差异确认→逐设备上传→核对当前上传内容→获准启用→独立读回→更新未来生效排程。已开始承诺保留。每次启用保存独立Command与观测证据，不能绕过操作员确认。

SimulationEngine后台tick处理指令和待应用变更，不依赖前端GET驱动。暂停/关闭浏览器不清空命令或设备状态；服务重启后继续读取持久记录。TTL/失联/拒绝/ACK丢失/完成未确定分别处理，不自动重发有副作用的动作。

completion_timeout注入表示动作可能已在模拟设备发生、但完成回执丢失：原Command保留indeterminate，单独state.query读取持久状态核对；多次读取原指令不重复执行。它不是现实网络模型或真机容错证明。任何模拟部分应用失败保持暂停与资源保护，不宣称现实机队能原子切换。

Schema/Pydantic/实际OpenAPI/HTTP TypeScript同批同步；旧Command缺少observed_state不补伪造历史证据。既有只读执行档案仍保持校验与来源，新增观测只来自实际模拟状态。

后端实际验证：device_readback + progress_resilience + execution_v2 + execution_archive组合15 passed（110.73s）；追加档案内设备观测归属/方案引用校验后，device_readback + execution_archive为6 passed（54.41s）。受控时钟覆盖ACK≠完成、TTL发送前过期、断联不伪造ACK、完成回执丢失后独立查询；真实后台tick无HTTP轮询派发及重启恢复另有测试。旧执行档案仍可往返，篡改观测execution/device/Plan引用被拒绝。未验证真实硬件。
