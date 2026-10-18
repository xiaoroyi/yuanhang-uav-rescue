# RFC-019：人工气象情景、机型阈值与作业窗口

状态：V2分支已实施W1；机器协议仍为团队待复核草案，不替代A/B签字。旧输入不含weather时沿用无风题设模型。验证证据见 evidence/redesign-v2/TEST_REPORT.md。

目标为W1人工信息与可追溯机型阈值实际进入输入、排程和独立验证。暂不调用外部预报，不把固定地速的原模型随意乘风系数，也不把天气气温当电芯温度。W2风致时长/能量与W3概率模型继续独立登记为未具备。

兼容增加可选Scenario.weather完整冻结对象：manual_scenario来源、发布时间、相对有效窗口、适用高度/参考、风速/阵风/风向FROM/温度/降水中的已知变量，以及按type_id记录且有来源说明的作业限值。缺省字段不补写旧Snapshot。开启后所选机型所需变量缺失/越限不能静默通过。

weather_window范围进入能力、请求和Plan验证范围。求解仅安排在有效窗口内的飞行，独立检查从输入重算阈值与起降时刻；信息展示、阈值检查、能源模型三个能力分别登记。默认无气象仍明确为原题无风演练，不能宣称已检查天气。

前端准备机队/条件中提供人工情景与规则编辑、来源/新鲜度，变更新版本使旧Plan过期；在途变化需冻结事实并评估当前承诺，不能让新天气重置在飞状态。事件扩展先同步严格联合、生成类型、正反例和兼容回归，再开放界面。

实现边界：当前仅quick/transport排程支持W1；improve或联合通信与W1组合明确返回unsupported_scope，不静默忽略气象。缺失规则/变量的机型被排除，其它有依据且符合限值的机型仍可尝试排程；所有机型不可用时返回input_not_ready，不冒充不可行证明。有效窗口约束起飞至返回，独立验证再次检查。不推断电芯温度、不增加无依据的耗能系数。

映射：weather.schema.json → Scenario.weather/MissionDraft.weather → 冻结Snapshot → weather_window模型范围 → Plan与独立validate。ExecutionEventInput增加weather.changed分支，只接受weather+原因，不可混用object_id/demand/cargo；事件原输入冻结，在承诺不受违约影响时只重算剩余任务；越限涉及在飞承诺时requires_manual。地图天气开关仅控制可见性，不修改约束。人工来源、发布时间、AGL参考高度保留，不叫作实况或预报。

生成器开启--strict-refs；跨Schema的WeatherRule使用完整$id引用，防止本地引用在合并后丢失并退化为Any。无weather的旧样例仍通过契约检查。
