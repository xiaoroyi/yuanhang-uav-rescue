# 前端规范入口

本文件补齐完整实施提示词中约定的入口，不另建一份接口真值。B同一人负责前端、后端与集成，当前源码见frontend/src；当前能力和限制见[实现状态](IMPLEMENTATION_STATUS.md)。

- 三页职责、交互/异常态与离线验收见[UI验收](UI_ACCEPTANCE.md)，开发约束见[前端AGENTS](../frontend/AGENTS.md)。
- HTTP类型来自[实际OpenAPI](../contracts/http/openapi.generated.json)生成，领域类型来自相同Schema，禁止手写另一套Plan/Scenario。
- 场景页维护需求、逐箱库存与资源，地图点位可筛选站点表；编辑形成新版本。工作台地图、架次、箱件与甘特共享实体ID，前端只格式化后端物理指标。
- 时间、能耗和均衡偏好共用不可变Snapshot，读取完整Plan后比较；加载/错误/历史版本状态分别呈现，过期输入先重新求解。原始偏好验证见[实验记录](EXPERIMENT_RESULTS.md)。
- 动态事件先落版本与快照，再真实重规划；历史结果使用原Snapshot，不能混入当前输入。事件范围见[动态事件](EVENTS.md)，资源试算与冻结分区分别见[资源分析](RESOURCE_ANALYSIS.md)和[冻结分区](FROZEN_PARTITION.md)。
- 通信来源的直连/中继窗口、关联能源和服务时段只读已保存Plan，范围见[通信协同](COMMUNICATION.md)。不在浏览器推造信号强度、缺口位置、能耗或实飞状态。

实际测试用例位于frontend/tests，截图位于evidence/browser/verified。按[测试计划](09-TEST-PLAN.md)和README运行；颜色、响应式与真实交互需实际检查，构建通过不等于视觉或物理可行性通过。
