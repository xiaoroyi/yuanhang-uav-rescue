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

## R17 / RFC-021多源复盘与可重载档案

V2新增测试全组合19 passed，92.33s（日志.local/v2-archive-regression.log）；另两项档案/在途专项2 passed，25.57s。真实Worker形成残余方案，完成33箱/53事实后导出两份Plan/两份Snapshot，导入只读档案，核对原领域行数与事实数量完全不增；篡改整体/文档、缺快照、重复事实、交付汇总不符、真实source伪造等拒绝。首次多源导出发现command_view调用参数错误，修正后再次通过，不将单Plan无指令往返当作全部通过。

正式4条V2 Playwright通过56.0s，archive-browser-final-results.json；视觉微调后档案流程又通过25.7s，archive-browser-visual-results.json。含真实在途插单→修复→逐设备应用→完成→复盘→GUI导入→时间筛选→核对不重写事实。浏览器报告和截图均为实际生成；最新运行包保存EXECUTION_SMOKE/inflight-repair-archive.json，SCENARIO_MANIFEST.json记录2快照/2Plan/53事实的来源与哈希。物理重验证不因导入被伪称通过。

完整旧算法/接口/前端检查正在通过scripts/verify.py运行，输出独立full-verification/，避免覆盖V1历史证据。当前段落不预先声明整轮通过。

## 完整非浏览器回归检查点

full-verification/latest.json：passed=true、source_unchanged=true，前后验证源码指纹均`2c58b9d8c6b55e851138a03b2872e2e5fbbdaed808ea814c6ebb6439bf913086`。全部Python 298 passed、8 subtests，830.85s；契约、治理、lint、12单元、strict TS/build共6条命令退出码全0。原题与原接口回归包含在此轮，不再以V1计数代替。完整浏览器仍在运行，已发现旧兼容入口动态设置隔离问题，不能将本段解释为全部浏览器通过。

## 完整浏览器与回归修复

full-browser-results.json：完整42条，41 passed、1 failed，21.8m。唯一失败是旧兼容入口动态背景，V2父组件首次挂载覆盖了旧页面data-motion；将主题/动态设置限定到对应路由后，原失败用例1 passed（32.6s，含文件初始化），新加跨新旧路由偏好隔离用例1 passed（7.1s），见legacy-motion-fix-results.json及preference-isolation-results.json。不能将分开的复测写成同一轮42 passed。

同轮服务器日志真实捕获Windows进度文件暂态PermissionError。RFC-022在隔离副本和主V2分支分别通过3项HTTP故障注入；保留最后有效样本、不重置Job状态、恢复读取通过。完整298 Python/8子测试是在此修复前的已保存检查点；新增3项和此后改动分别记录，不能直接加总伪造新一轮全量计数。

全浏览器写入旧目录的94个实际输出已另存legacy-regression-full/，SOURCE_MAP.json保存映射和新旧哈希，原V1字节恢复；旧策略专项后续2个输出另存legacy-motion-fix/。未重置源码、删除业务数据或覆盖V1验证报告。

## R11 / RFC-023 模拟程序独立读回

后端隔离分支组合15 passed（110.73s）；补充档案内观测归属与方案引用校验后6 passed（54.41s），合回V2的后端内容相同。覆盖HTTP受理/ACK/实际完成、完成回执丢失后独立查询、后台无轮询派发、TTL和断联、重启恢复、未批准候选禁止通用activate、档案篡改拒绝。前端lint与strict TS/build通过。正式浏览器在途插单→逐设备读回启用→独立查询→完成→复盘→只读档案1 passed（27.8s），device-readback-browser-results.json。运行时补齐显式simulation_fault=none，热更新发生在查询步骤之前；未声称本轮整体源码冻结。实际查看device-state-readback-1440.png，未来程序与当前架次来源分开。无真实设备连接。

## R12 / RFC-024 开始边界与遥测可用性

新增两项边界先复现失败（19.25s），修正事实驱动承诺/暂停只读/误报可用性投影后，与执行/天气/中继/操作契约组合11 passed（98.14s）。首轮组合9 passed/1 failed：原急需场景退出关键机体后确实未找到满足硬截止的可验证方案，系统返回UNKNOWN；测试改为专用无硬截止输入以检验可行修复，生产输入/原题回归保持原样。专用测试验证ready 0秒无已装载承诺→退出/误报→真实残余Worker→逐机采纳→刷新不写账→显式advance(0)才写loaded；暂停读取同样不写新边界。新增可空availability/reason，前端区分当前飞行阶段与未来任务可用性。lint/strict TS/build通过，浏览器与后续地图联动继续验证。

## R06 / R18 / R20 地图工作台增量

正式浏览器组合6 passed（55.8s）：空白草稿地图选坐标且不造基地/高程；50长名/同坐标点可分别选择；1440/1280/1024镜头、刷新、缩放、标签不遮点、控件不被详情挡住；在线影像请求失败自动降级；真实求解重叠航线选择正确架次/箱件；WebGL失败仍可录入；在途插单/逐机读回/复盘/档案闭环；W1真实求解与地图显隐。weather浮层再移至保留上沿后专项1 passed（13.8s），增加不遮任何点位的DOM几何断言。lint零警告、strict TS/build、12前端单元通过。map-workspace-browser-results.json与weather-map-clearance-results.json分别记录，不能相加冒充一次完整回归。

首轮3 passed/2 failed：测试误写卫星按钮可访问名称（实际含空格），以及异步快照到达时测试分两次取marker矩形遇到节点替换。次轮4 passed/1 failed：断言了界面不存在的“箱件”固定词。修正为实际同帧几何、所选sortie_id及真实cargo_id，第三轮5 passed；追加标签不遮点/控件几何与W1后6 passed。失败JSON保留。视觉检查发现窄屏详情遮控件和聚合基地缺详情，修复为流内面板、1024时收起对象列表、基地独立详情；实际截图已查看，不用强制点击绕过。

## R16 / RFC-025 真实评测与Portal样式

后端初轮3 passed（33.00s）；与设备读回/事实边界/任务输入/契约组合16 passed（105.95s）；追加真实Job排队取消及注入2次503后继续真实Worker的恢复测试，最终4 passed（44.19s）。原输入/Plan/执行行不变、同分析快照的三偏好、失败不置零/保留分母、导出原始四文件SHA/base64、重启恢复、派发结果未知不盲重试均覆盖。仅静态策略/quick-improve对照，不冒充动态/学习消融。

正式UI两流程初轮2 passed（30.8s），表格与截图滚动修正后2 passed（29.0s）。Portal共享UIContext后10项组合全部通过，见experiments-dialog-regression-results.json（评测2项、新用户CSV闭环、偏好独立、在途档案、4项地图、W1）。中间5项4过/1失败暴露真实新用户镜头问题：空白视角被错误保留到基地/首个需求点；修复camera version2/region_key，首次建立区域才fit，轮询/选择/resize仍保留。下一轮9过/1失败则为断网注入误写实际影像域名，修正正则覆盖真实arcgisonline子域并断言确有请求被阻断，10项全过，原失败JSON保留。

检查MapLibre当前安装源代码发现content也会在影像元信息就绪时发出，不能等于已有瓦片。改为实际tile.state=loaded才标ready，挂起请求超过12秒自动离线回退。强制失败+真正挂起两项2 passed（23.8s），imagery-deadline-browser-results.json。lint零警告/strict TS/build通过。现有12项前端单元在地图检查点已过；没有把专项数量相加成当前全量。

实际包EXPERIMENT_SMOKE/strategy-benchmark.json来自浏览器下载，含3个真实求解结果、2份输入原文、3份Plan原文和12个原始Worker文件，来源与字节哈希见同目录MANIFEST.json；不使用固定数据冒充新求解。

## R15 / RFC-026：真实在途电池退出与残余局部修复

新增纯Python repair_remaining、冻结原文Reference、资源释放依赖修复及同一残余快照全量基线。零时刻replan/Event兼容；局部失败在剩余预算全量回退。实际方法由Worker诊断而非请求偏好决定。候选轮询改读最新change，生成后即显示真实候选地图/甘特/逐箱差异，采纳前可以点箱件核对架次。

- backend boundaries/readback + battery/demand Event：31 passed，96.87s。
- 新dependency 3条 + execution/archive：10 passed，112.59s；含真正首架次在飞、备用电池退出、未来换电池延迟、原承诺位置/SOC/箱件不变、最终2箱交付；并发队列失败有明确失败/幂等回执，可真实重试。
- 加强Reference/事实游标/原文校验后：4 passed，45.91s（新3条+archive），不是当前完整回归。
- Playwright三流程3 passed，约1分钟：实际GUI电池退出→局部修复→逐箱/候选架次→采纳→原在飞来源保持→完成；在途新增需求明确全量/新箱件无旧基准；空白CSV输入。dependency-browser-results.json保留原报告，DEPENDENCY_SMOKE有完整原始包和SHA清单。
- lint零警告、strict TypeScript/build通过。三张新截图实际查看，1440/1280差异表和地图可读；候选甘特与采纳位于弹窗滚动区，未用强制点击绕过。

各批为独立专项，不相加冒充全量。当前R15依赖影响图与规划页条件有效性提示继续实施。原文日志位于dependency-validation；当时源码未提交，最终当前源码全量仍待执行。
