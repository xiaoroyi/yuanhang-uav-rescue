# B 系统线后端模块

RFC-010的Event由Schema生成RootModel联合，model_dump仍是原始JSON对象，不在HTTP增加root层；严格区分机体与运输电池负载。服务器先去重，再用自身received_at校验新事件；初次应用检查版本、执行事实与可退出状态。只修改指定资源status，保留能源/位置，并清除当前规划预约。Snapshot单点诊断见RFC-009，不持久化为Plan或Job。

B 与 frontend owner 是同一人，C-* 为历史任务编号。遵守根 AGENTS，先读 docs/03、04、05。

维护 FastAPI、数据校验、SQLite、不可变快照、独立 Worker、幂等事件、确认事务和导出；不重写算法物理公式。只通过 solver/public_api 调用 A。长求解不能阻塞 HTTP；真实 Worker 停止后才能 canceled。

当前已有backend/app/main.py应用、SQLAlchemy SQLite存储、独立子进程JobManager、JSON/CSV/XLSX导入。生成类型在app/generated/domain.py，来自根contracts Schema；不手改。实际OpenAPI快照由scripts/export_openapi.py输出，前端类型随后生成。外部输入不能自称verified_dataset。版本/快照/事件/确认/取消/重启已有测试，后续修改跑tests/backend，进度见docs/IMPLEMENTATION_STATUS.md。

terrain_assets.py注册本地GeoTIFF，只写本实例runtime/assets，源文件和归一化栅格内容寻址，不覆盖旧资产。请求与Worker使用同一terrain_store上下文；独立检查/确认/回放也必须能读到该库。JSON场景仅引用hash，二进制移交方式见TERRAIN_ASSETS。reports.py只输出已验证Plan绑定的Snapshot，不使用当前可变场景替代历史输入。

Event现包含四个严格分支（含demand.added和relay_energy.unavailable），纯apply_event_to_scenario统一状态转移；不要在API重新手写另一套追加/退出逻辑，保留旧负载与幂等。

RFC-014的WhatIfRequest.ground_addition仅给已配置有限resource_limits的源场景增加准备工位/充电端口。严格整数与总量32/64在入库前检查；新来源标签what_if_v2_ground_capacity，缺省/null保持旧v1且不补null参数。实际OpenAPI/TS同步生成，历史来源与原Plan/Snapshot不可变；不要把无限容量当0或把增配等同最少购买证明。
