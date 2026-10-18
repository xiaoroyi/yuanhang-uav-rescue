# RFC-024：事实驱动的开始边界与资源可用性

状态：V2实施/验证中，待团队复核。保留旧Snapshot/Plan/执行事实，业务仿真范围。

承诺由持久`loaded`/`relay_started`事实的`(plan_id, sortie_id)`确定，不再从`prepare_start_s <= time_s`推断。ready/paused/completed状态下只读查询不产生新事实；只有开始/继续后的服务器时钟或显式advance能推进。采纳刚好在冻结时刻开始的未来程序，不意味着自动装载。遥测仅对已有开始事实的架次显示在机物资/能源。

TelemetrySample兼容新增可空`availability`（available/not_ready/unavailable）和`availability_reason`。phase继续表示当前模拟阶段；已开始架次保留空间/箱件状态，同时单独显示未来可用性。退出事件与输入状态不可显示成待命；available_after_s尚未到达时显示尚未就绪；误报更正按追加resolution投影，不删除或改写原事件。缺字段的旧档案不反推历史可用性。

Schema、Pydantic、实际OpenAPI和TypeScript同批同步。测试包含0秒未开始退出/误报/真实残余重算与采纳、暂停边界只读不装载、显式推进0秒后才写loaded；保留既有在飞/天气/中继回归。两项边界与既有执行/天气/中继/操作契约组合11 passed（98.14s）；完整细节和首轮可行性失败见TEST_REPORT。前端类型/构建通过。
