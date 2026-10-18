# API与展示迁移

| 部位 | 增量 | 兼容与约束 |
|---|---|---|
| MissionCreate.template | compact_joint / contest_joint | 旧blank/compact/contest和默认值不变；新建独立场景，显式启用原题通信与联合要求 |
| GET /plans/{id}/export | format=xlsx | 绑定原Snapshot生成6工作表；旧CSV/JSON/GeoJSON/relay_csv含义不变；数值保留秒/kWh与明确百分数单位；文本不执行公式 |
| TelemetrySample | nullable模型水平/垂直速度、估计电量、载荷、阶段结束 | 旧soc仍为阶段端点，估计另列；不回填或改写旧档案，不把倍速当物理速度；未知保持未知 |
| GET /plans/{id}/radio-coverage | 离地高度/可选中继/网格大小 | 新只读API，来自冻结输入/真实DEM/同Radio模型；不取代沿航迹的连续时间认证，预算不足点为unknown |
| POST /plans/{id}/confirm | 已有未结束实例时新请求409 | 修复P0静态预约入口覆盖V2执行的缺口；旧幂等回执可重读；执行调整走原采纳事务 |
| 静态托管 | /help、THIRD_PARTY_NOTICES.txt | 显式WebP/WebM/VTT MIME与视频字节范围；不再落到SPA首页；缺文件404 |
| 前端任务路由 | prepare / plans / schedule / terrain / communication / insights / execute / review | 仍为四阶段；规划下有5个核对视图。根地址为独立展示首页；旧九页兼容入口保留 |
| Solver / Plan / Snapshot | 无业务模型改写 | 保留原物理模型、求解/重规划/检查接口、实体ID、历史数据与原题回归依据 |

RFC030/031记录本轮授权与取舍。实际OpenAPI为83路径，操作Schema为51个严格模型；前端HTTP类型从OpenAPI生成。契约仍proposed，未代替A/B批准。
