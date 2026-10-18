# RFC-021：可重载执行档案与多源复盘

状态：V2分支已实施，只读模拟范围已通过专项与浏览器验收；协议仍待团队复核。全量回归记录另见evidence/redesign-v2/TEST_REPORT.md。

独立Execution归档不导入为可控制实例、不占用资源、不写交付账本。新增只读档案列表/导入/详情HTTP接口，资源中心“运行档案”为入口。来源限定业务simulation；真实/SITL日志需后续合同，不能通过修改文件mode提升权限。

执行包v2包含截取的ExecutionView、事件投影、调整与指令状态，以及初始/生效/事实/候选所引用的全部Plan和Snapshot、事件原输入和纠错记录。领域原文以有类型kind/id、UTF-8 payload_json及SHA256文档封装保留，避免默认字段补齐或时区重编码改变旧Snapshot.content_hash。整体checksum用于一致性与幂等去重，不称数字签名或来源认证。旧execution-simulation-v1格式保留只读下载兼容，缺文档时不伪称可重载。

导入严格检查文件体积、JSON/DTO、全包及文档哈希、重复ID、引用、Snapshot内容哈希、Plan结构/保障与事实游标/去重/箱件归属；地形/影像原件不凭空打包，档案保留asset_id/sha256与来源。若缺本地DEM，地图与已保存几何/事实仍能读，物理重验证不得标通过。档案不使历史输入成为当前输入，不覆写同ID领域记录。

多源排程按Execution.schedule_parts过滤各自Plan架次，键为plan_id:sortie_id，不能拼成伪造单个Plan。资源时间轴显示各段准备/运输/周转/充电与当前时标；原Plan对照另列。计划—模拟交付偏差以不可变delivered事实计算，新插单无初始基准时为null，不能显示0延误。档案回放游标仅客户端只读筛选历史事实/模型轨迹，绝不调用simulation/actions。

运行中复盘按事实游标刷新；导出与导入浏览器验收须核对原实例和数据库事实数量不增加，篡改、缺文档和跨Plan引用负例必须拒绝。

实现路径：GET `/executions/{id}/export?version=2`；不带version仍返回旧v1。POST `/execution-archives/import`、GET `/execution-archives`、GET `/execution-archives/{id}`；只追加execution.archive记录，绝不导入可控Execution/Plan/Snapshot行。20 MiB上限，按整体哈希去重。导入进行结构/引用/一致性检查，不重新认证物理、DEM或无线链路。导入档案返回的领域类型仅用于展示，原文字段仍在FrozenDocument中保留。

前端ExecutionTimeline从各自Plan筛选生效架次，不构造拼接Plan；支持机体/电池/中继组件切换、完整排程抽屉、时标与交付事实标记。ExecutionInsights显示初始预计对模拟交付阶梯与逐箱偏差。档案时间筛选只读取所保存事实，连续历史遥测未记录时不插造轨迹；完整地图路线是方案几何，最终时刻可显示截取的模拟遥测。
