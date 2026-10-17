# RFC-002 单人实现分支的兼容接口与模型注册

状态：implementation-branch，待团队复核。用户2026-10-17明确授权跨模块实际开发，现有0.1对象保持原字段与旧样例。

新增HTTP资源列表、场景复制/示例、方案比较、导入预览、运行进度与方案确认元数据采用独立DTO，不暗改Scenario/Plan/SolveJob。物理model_id固定为contest_transport_v1和contest_two_stage_v1，参数清单见solver/physics.py。未知model_id拒绝计算。

数值模型继承归档flight_physics.py和routes.py中载荷相关等效航程、爬升能耗及两段充电公式，去除bootstrap、路径注入和写目录副作用。实体SOC/SOH保留，耗能与可用容量分离。未支持通信/真实飞控/全航程冲突时按capabilities拒绝强制检查或注明未评估。

对一般新区域，距离采用WGS84测地距离；题设DEM采用已有栅格与输入高程，明确题设净空范围。独立检查重新重建路线时间、载荷、能耗、充电和资源区间，不相信求解器自报passed。

导入预览和what-if独立快照、事件重试、确认幂等和只读导出均由HTTP层处理，solver保持纯Python。

增加只读 GET /plans/{plan_id}/playback：独立DTO返回prepare/flight/handover/return阶段、端点坐标与相对秒，is_execution_fact=false、position_semantics=schematic_linear_interpolation。前端仅作分段位置示意，不产生实际交付或遥测；核心Plan/Scenario保持原样。

Health增加service_id/workspace_id，用于本地启动器识别同一仓库服务；workspace_id为仓库路径摘要，不返回原路径。
