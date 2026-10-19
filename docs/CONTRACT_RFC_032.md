# RFC-032 · 可选离线启发式与演练资产入口

状态：本轮用户授权的兼容实施提案；不代替A/B正式批准。`approved_by=[]`。

新增SolverOptions/SolveRequest可选`engine_type: standard|eoh`与`heuristic_policy_id`。省略仍使用标准评分；新页面显式指定。新Plan可选`engine`保存实际包版本、SHA256、真实来源和评分/回退次数。旧Plan/Snapshot JSON与hash均不重写，不因读取补写数据库。

EoH仅替换已通过物理/机队分配的候选排序，保持硬约束、独立检查、最终目标与CP选择。`ranking_evaluations=0`表示本次搜索没有调用该评分（如直接沿用历史模式/深入基线），不伪称取得改善。初始化策略为人工规则`rule_initialization`，不是LLM实验；`eoh_offline`只能来自离线产物，导入者的实验声明与本机数值检查分开。

在线只运行受限标量表达式：有限数字、四则运算、五个特征与白名单数学函数；无属性访问、循环、导入、任意Python执行或网络。表达式运行异常退回标准评分并计数；不存在的包在提交前拒绝。

新增`MissionCreate.case_id`，仅创建新的演练输入，不复制Plan或实际交付。来源记录在任务创建操作日志。`GET /case-library`返回内置案例和公开资料来源，`/case-library/{id}/preview`只读；`/asset-overview`动态聚合任务/计划/快照/事件/执行计数。公共背景与演练合成需求明确分开。无在线气象抓取或真机连接。

前后端类型从Schema/实际OpenAPI生成；引擎对比使用同一Snapshot、同一偏好/规则。重规划/深入/资源试算继承原方案引擎，不将引擎变化错误归因为资源变化。
