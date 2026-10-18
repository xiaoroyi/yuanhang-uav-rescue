# RFC-030 · V3体验与可解释执行增量

状态：按2026-10-19用户跨模块授权在feat/mission-experience-v3实施；未代替团队批准。

1. MissionCreate.template新增compact_joint/contest_joint：复制原小场景/原题，并在同一创建事务启用原题通信参数，policy.requires_communication=true；默认和旧三值含义不变，不复用历史Plan。新值是显式请求，不向旧请求补新字段，幂等哈希不变。
2. GET /plans/{id}/export的format新增xlsx：真实Plan绑定其不可变Snapshot，输出运输架次、逐箱交付、中继架次、通信保障、资源时序与来源说明。缺中继/未计算字段保持空/不适用，不填历史答案；字段/单位对照references/modeling/answers.xlsx。CSV/JSON/GeoJSON不改含义。
3. TelemetrySample新增可空缺省字段：`model_horizontal_speed_mps`（非负m/s）、`model_vertical_speed_mps`（升正降负m/s）、`phase_end_s`（相对秒）、`estimated_soc`（0—1）、`payload_kg`。由服务器当前生效阶段及真实模拟时间计算；旧soc仍为已计算端点，估计另列来源，不冒充实测。原题模型的等功率飞行/服务阶段按端点插值；没有装载能源实体或未具备模型时不估计。无源/断流不在前端外推，不把sim倍率当飞机速度。操作Schema/OpenAPI/TS已同步；不新增无消费者的站点字段。
4. 新前端页面路由属于展示层，不改变Plan或执行事实；三维飞行使用真实阶段起止海拔，原地表投影保留并说明。原题默认约束为50m净空、站点30m作业、20%返航储备，界面读取当前Snapshot参数而非固定覆盖。
5. 新只读`GET /plans/{id}/radio-coverage`：查询`altitude_agl_m`（1—300m，默认120）、可选该方案`relay_sortie_id`、`grid_size`（9—31，默认21）。`RadioCoverage`回显Plan/Snapshot/地形hash/高程参考/高度与所选中继服务期，点为gateway/relay/uncovered/unknown。复用同一个Radio双向预算与原始DEM模型；中继结果同时要求回传有效。仅离散空间采样，不修改原Plan、不宣称网格间连续覆盖、不取代实际航迹的时间窗认证。预算到期保留未知并允许重试。不存在中继返回404，无通信/地形不支持返回422。

兼容：旧字段/旧数据/草案批准状态保留；新增非破坏性能力，旧档案可空字段不补造。保护旧Plan/Snapshot原文。许可与参考选择见docs/experience-v3/RESEARCH.md。
