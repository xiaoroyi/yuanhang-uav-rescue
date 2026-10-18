# RFC-028：同一执行残余输入的修复方法对照

专项与消费者已验，待最终全量。新增suite=repair及repair_reference_id。只能使用服务器冻结的残余Snapshot与Reference，且具备生成当时的事件序列、原输入/纠错文档与事实游标；旧引用缺证据不在事后拼造，明确要求重新生成调整。生成时独立保存solver.repair.evidence，不改变纯Solver Reference含义。

分析复制相同残余物理输入、释放下界和承诺，仅更改储存身份字段；提供可比较输入SHA。两个方法同seed/预算/线程/目标，均先检查原来源，dependency尝试局部并允许剩余预算全量，full_recompute明确全量。calculation_method显示实际路径，repair_difference对同一旧未来统计保留/改机/换电池/移时/新增量；不隐藏失败，不预设局部更好，不把p95小样本当保证。

协调器仍串行真实Worker，后台取消/恢复规则沿用RFC025。原执行、事件、事实、源Plan/Snapshot及预约不变，不自动采纳评测结果。导出增加原Reference/分析Reference/生成时事件证据及全部原文依赖，保留每例原始输入/输出/进度/日志。严格模型、生成契约、TS/消费者与测试同批同步；旧strategy/search与旧档案缺字段兼容。
