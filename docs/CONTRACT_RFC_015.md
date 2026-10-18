# RFC-015：只读空间分析和输入版本历史

状态：adopted_for_branch；正式契约审批仍待A/B，不填写approved_by。来源：用户2026-10-18要求前端深化、真实地图/高度分析、数据大屏和历史入口；明确允许在线卫星影像。此提案不改变Scenario、Snapshot、Plan或Solver输入输出，不改变数据库结构，不增加执行事实。

## 新增实际HTTP接口

| GET /api/v1 后的路径 | 返回 | 绑定及边界 |
|---|---|---|
| /map/surface?asset_id=…&sha256=… | TerrainSurface | 资产ID与64位hash必须同时显式提供；真实DEM最多73×73采样；经度升序、纬度降序、NoData为null；极值和已知比例按完整栅格统计 |
| /plans/{plan_id}/flight-profile?sortie_id=… | FlightProfile | 读取该Plan的原始Snapshot和同一资产上下文；复用现有leg/leg_values，重建巡航、载荷、爬升/下降、距离/时间及水平/爬升能耗；重建路线不符拒绝，不替历史结果编造高度 |
| /scenarios/{scenario_id}/versions | ScenarioVersionSummary[] | 保存版本按state_version降序；输入实体数量与内容hash；数据库未保存版本创建时间时created_at=null，不借用场景更新时间 |
| /scenarios/{scenario_id}/versions/{version} | Scenario | 返回当时完整输入；版本>=1，缺失404、非法422；没有恢复、覆盖或新建行为 |

所有新DTO由Pydantic实际OpenAPI生成前端类型，见backend/app/map_models.py、flight_profiles.py、version_views.py与contracts/http/openapi.generated.json。实际API路径从43增至47。客户端只增加读取入口，不手写重复消费者类型。

## 高度和能量语义

高程沿用资产声明的vertical_datum，未知统一海拔基准时不能标成AMSL。ground_elevation_m是地面高程，start/end_work_elevation_m是模型作业高程，cruise_elevation_m是水平巡航段模型高程；不等同实时遥测或逐秒飞行高度。

剖面全架次最多240个DEM采样点，未知保留null。它用于显示；完整地形极值仍来自已有闭像元净空方法，不能从稀疏显示曲线认证安全。返航、交接、充电不是纯飞行时长；水平和爬升能耗分解来自相同物理函数，不在前端复制公式。下降不产生能量抵扣，沿用当前模型。

三维视图为采样DEM网格，NoData单元不生成跨洞三角形。可选择视觉高程倍率，明确只改变显示、不参加求解。叠加线为地表投影，不冒充实飞高度轨迹。

## 底图与本机档案

在线卫星为用户显式选择后的外部底图，请求使用公开影像服务并保留归属；不批量缓存、不给出未核验拍摄日期，不参与净空/地形求解。默认离线、失败明确降级，现有强制离线检查保留。道路、水系、村镇与行政边界属于原题背景，不自动升级为空域或求解障碍。

本机档案仅浏览器姓名/团队/职责/头像与显示偏好，支持刷新和同源标签同步；不是HTTP账户、身份认证或多用户权限。没有增加密码/访问令牌存储。

## 验证

后端覆盖hash绑定、NoData、采样上限、两个独立资产目录、原Snapshot历史不变、重建物理与真实Plan一致、版本排序/缺失/只读及畸形参数。前端覆盖真实方案/高度切换、历史与输入版本下载、可比性、刷新恢复、教程/档案、深浅主题、移动导航、WebGL/离线降级。最终命令与计数以本轮EXPERIENCE_RELEASE及原始验收报告为准。
