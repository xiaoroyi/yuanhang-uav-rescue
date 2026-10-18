# V2 测试记录（持续更新）

本轮使用 Windows / Python 3.11.15 / Node 24.16.0，隔离临时 SQLite。V1 历史计数不当作 V2 结果。

## R00 / R01 首批

- `.venv\Scripts\python -m pytest tests/backend/test_operations.py -q`：3 passed，8.79s；覆盖不完整草稿、版本冲突、发布阻断、创建幂等、归档保留原输入、真实子进程求解后的阶段时间/能源/SOC合计。原始本机日志 `.local/v2-operations-pass.log`（忽略目录）。
- 首轮 2 passed / 1 failed：测试把浮点加法后的最后时刻按精确相等比较，差 1e-12s。改为绝对 1e-6s 容差；能源/SOC断言保留。失败日志未删除。
- `scripts/check_contracts.py`：10 旧领域 schemas、18 Mock fixtures、16 历史草案 HTTP 通过；不包含算法认证。
- `scripts/check_governance.py`：89 任务依赖无环、42 原件哈希、18 历史源码 AST、67 本地文档链接通过。
- `scripts/export_operations.py`、`scripts/export_openapi.py`、`node frontend/scripts/generate-types.mjs`：已执行，初批实际 API 54 路径。新增操作 Schema 位于子目录，避免改变旧领域生成器。

执行仿真、指令、在途修复、V2 浏览器和完整回归：尚未运行，不标记通过。实际后续运行结果追加至此。

## 首个纵向闭环（中间检查点）

- test_operations.py + test_execution_v2.py：最近9项核心测试通过，41.77s；覆盖真实 Worker、服务器时钟/持久化恢复、幂等事实、断流位置冻结、独立遥测会话、在途承诺和未来资源释放、逐设备上传/ACK/激活、超时未确定保留原排程、陈旧候选409、无库存与已装载退出阻断、空白CSV/XLSX往返、并发创建无孤立输入。测试后继续加入的断言不冒充已运行。
- `node scripts/v2_visual_review.mjs`：第二轮 passed=true，截图14张，源码当时完整闭环通过；见 browser-review.json。首轮因过度保守的共同资源边界导致默认案例调整未找到方案，已改为无有限地面模型时各资源独立释放并独立检查新旧互斥；原失败截图 failure.png 与日志保留。不是完整回归或当前全部能力完成。
- 正式Playwright `node frontend/scripts/run-e2e.mjs --grep "V2 new user"`：1 passed，13.0s；见 blank-browser-results.json。含成都合成区域空白任务、CSV逐步导入、不兼容电池阻断/修复、刷新恢复预检、实际计算与点位详情、双尺寸地图面积。先前失败分别是空态按钮重名、测试未等待异步路由、发布导致页签重置、点位点击冒泡被航线抢选，均记录并修复，不把失败轮改为通过。
- 原旧 workflow 测试入口显式改为 #/workspace，保留旧业务断言；新根地址由V2用例覆盖，未删除旧流程测试。

完整 Python/原题回归、完整浏览器、当前源码最终lint/build与视觉复验仍待后续执行。

## R13中继执行增量

新增test_relay_execution_v2.py：对已有小场景联合候选先执行当前独立validate，再重建中继阶段/能源/SOC、运行服务器模拟至服务中与最终组件释放、核对32箱事实与Plan数据库原JSON未改。专项1 passed 10.93s；与全部新增核心及操作契约组合11 passed 53.71s；lint与strict TS/build通过。首次专项末尾比较HTTP的UTC `Z` 与原候选`+00:00`文本而失败，实际阶段和账本断言已过；改为核对数据库原JSON不变，避免将等价日期序列化误判为数据改写。失败日志保留。此增量未声明浏览器/全量算法已经验证。
# R14 / RFC-019 W1增量检查点

当前W1与V2核心组合：17 passed，65.84s，命令为`.venv\Scripts\python -m pytest tests/backend/test_operations.py tests/backend/test_execution_v2.py tests/backend/test_weather_v2.py tests/backend/test_relay_execution_v2.py tests/solver/test_weather.py tests/test_operation_contracts.py -q`。含真实Worker自动必检范围、机型排除/窗口、独立负例、旧Plan不变/过期确认阻断、在飞承诺冻结与气象事件真实残余重算；不是完整旧算法回归。

正式Playwright两条V2流程2 passed，22.3s，见weather-browser-results.json；人工W1输入→预检→真实B型排程→地图信息显隐，以及非原题空白CSV导入闭环。第一轮发现通知遮住下一步，修改自动收起及点击穿透后重新运行；不依赖强制点击绕过缺陷。weather-plan-1440.png已实际查看，天气浮层仍可能遮住附近点位标签，列入R06后续避让检查。

lint、strict TS/build、12项前端单元通过；11领域Schema/18旧Mock/16旧草案HTTP契约通过，89任务/42原件哈希/18旧源码AST治理检查通过。WeatherRule解析曾因相对引用缺失回落Any，已改完整$id并开启生成器严格引用；新生成类型为具体WeatherRule。风致能耗/时长、预报与联合W1未伪称通过。

# R12 / RFC-020事件纠错与续传

`tests/backend/test_execution_v2.py`最终6 passed，70.11s；覆盖未处理事件统一阻断开始/继续/手动推进、误报纠正幂等与原记录/事实不变、事实游标续传无重复/超前拒绝，以及ACK未完成/完成超时、拒绝、TTL、客户端伪造actor/跨执行机体拒绝。补充测试首轮用了错误的app.state属性，第二轮错误地将0.9s ACK当1.2s完成超时并捕获了错误异常基类；修正测试与实际生命周期后重跑6项全过，未改短超时阈值掩盖问题。

正式浏览器1 passed，14.0s，resolution-browser-results.json，覆盖暂停已装载误报、禁用两类推进、核实依据纠错、恢复与再次暂停，核对交付事实未改变。event-manual-1440.png已查看；重叠机体标记、底部排程可用面积列入R06/R17继续改进。lint与strict TS/build通过。该增量尚未整体回归旧算法，不宣称所有R12特殊场景完成。

