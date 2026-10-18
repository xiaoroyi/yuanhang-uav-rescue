# RFC-018：中继阶段与业务仿真

状态：V2分支实施中，待团队复核。扩展RFC-017的只读阶段与隔离执行；旧Plan/Snapshot不改写，纯Solver入口和物理不变。

StageAnalysis按已验证联合Plan重建中继准备、爬升、巡航、下降、建链、驻留服务、返航和周转。中继能源由原relay_model的巡航功率、爬升效率、悬停/无线功率重算，与Plan合计/返航SOC对齐。不凭前端插值造连续SOC。

ExecutionSchedulePart兼容增加relay_sortie_ids；事实可记录中继建链/服务/返航/能源释放。component_id始终独立于运输battery_id。只有所有声明的机体与能源释放事件完成，模拟才结束。遥测按已计算阶段位置推进，断流仍冻结最后观测。

本次仅推进已验证静态联合方案的业务仿真；执行中的联合窗口修复仍需下一步实现并核验，不能通过关闭通信绕过。HTTP/JSON Schema/TS同次生成，历史中继Plan必须经当前独立验证后才能进入模拟。
