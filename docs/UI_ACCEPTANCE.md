# 三页界面验收规格

B 同时维护 UI 与 API。本页定义目标，不表示已有页面。统一浅色、深蓝结构、青绿正常、橙色事件、红色冲突、灰色未知；状态必须同时有文字/形状。字号14–16px、8px间距作为初始 tokens，1440×900、1280×720 可操作，窄屏切页签。

| 页面 | 必需数据源 | 关键动作 | 错误/空态 |
|---|---|---|---|
| 场景与资源 | Scenario、validation、capabilities | 导入/预览/字段映射/编辑；地图与表格互定位；建快照 | 行/字段错误、重复 ID、无兼容资源、未具地形条件 |
| 调度工作台 | Snapshot、Job、Plan | 求解/取消；路线、任务表、机体和电池甘特同 ID 联动；同快照两目标比较；确认/导出 | queued/running/UNKNOWN/INFEASIBLE/failed/canceled、stale/null |
| 事件复盘与资源分析 | Event、旧新 Snapshot/Plan、能力清单 | 未起飞退出、显式重规划、变化清单、计划播放；P1 资源试算 | 不支持事件/在途状态拒绝、版本冲突、重复请求 |

MockProvider 与 HttpProvider 使用相同类型；Mock 常驻标签、禁确认，不显示已计算验证。时间、SOC、能耗只格式化后端字段，不从路线长度反推。null 显示“—/未评估”，地图播放只更新展示时钟。中继、地形、费用、AI、影像按钮按真实 capabilities 启用。

方案对比必须核对快照、共同保障集、模型范围与指标口径。事件后不同快照是“前后变化”，不能标为同条件优化优势。Gantt 使用 `drone_released_s` 与 `battery_released_s`；相同秒先释放后使用。
