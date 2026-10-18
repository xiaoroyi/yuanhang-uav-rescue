## 最新继续点：R16静态评测检查点通过，继续R15（2026-10-18 20:26）

R16代码/模型/消费者/原始包已完成静态专项，准备提交此检查点：4后端44.19s、早先16组合105.95s、10浏览器组合全过约1.7m。首次区域camera v2修复、V2/legacy Portal UIContext隔离已测；MapLibre metadata不能代表瓦片，已改actual tile.loaded才ready，真实挂起12秒回退+50点故障2项23.8s通过。lint零警告/build通过。详细TEST_REPORT、EXPERIMENT_SMOKE/MANIFEST；动态/学习消融仍未完成，不把静态对照称贡献证明。

当前8000 PID62360/start1792325491757/launcher88473/source25c71f621ac16bb166b13a1b4216de20c6400e0a0e3f9fddec9fdebd0e531865；experiment-deployment.json已核对当前dist/source与原14Plan/10Snapshot不变。源8d4c926已推，R16本次提交/推送后继续，不停工。副工作树33e7fe4已合勿再合；8012仍旧服务不能当最新验证。

下一优先R15：当前执行残余仍全量quick，纯solver仅零时刻_try_local_repair；需要新增明确纯Python repair_remaining入口和原Plan/Snapshot原文引用，不能伪造旧Plan身份来调用零时刻replan。基于事实冻结后，未来资源退出可依赖局部修复，独立验证整个残余，失败用剩余预算全量回退；其他新需求/天气先明确全量，不篡改旧Event语义。补命名空间依赖图/受影响任务点击、实际修复方法与改派指标；之后同模型预算对照、R14/R22可做研究及最终全量/视觉。真实外部ODM/设备/SITL/多基地任务保留具体缺口，不用Mock。

## 最新进行中：R16真实评测与新用户镜头修复（2026-10-18 20:17）

主V2提交8d4c926已推送。当前未提交R16：RFC025、严格43操作模型/82HTTP路径、experiment.run/create后台协调器、真实quick/improve/三偏好批处理、1—3种子/预算、失败分母、冻结独立副本、后台派发/取消/重启、base64原始四文件证据；frontend ExperimentCenter已取代旧演练任务列表，带散点/表/环境/历史/日志/Plan地图与甘特。4项后端44.19s及之前16项组合105.95s通过；UI2项29.0s通过。没有动态/通信/学习消融冒充完成。

视觉发现Portal不继承V2，已用UIContext(v2/legacy)经React portal传递，v2-dialog共享变量及按钮/地图样式，旧路由默认legacy不污染。5项组合4过/1新用户失败：空白世界镜头被保留到设置基地/加入第一个点，需求点无法直接找到。已加camera记录version2/region_key，首次设置/移动基地或0→非零需求点重新fit，日常轮询/选择/resize保留；补空白保存基地后缩放断言。

当前冻结源码跑10项浏览器：session43518，.local/v2-experiments-map-regression.log，报告experiments-dialog-regression-results.json。涵盖新用户、全部4地图、W1、独立偏好、评测2项、在途档案。先读结果再改，不把此前失败轮称通过。frontend lint/build通过，最新build已生成。R16原始实际包在EXPERIMENT_SMOKE/strategy-benchmark.json。要查看最新弹窗/桌面与窄屏截图，修实质问题后提交R16完整消费者与证据。

8000现owned PID62360/start1792325491757，launcher88473，.local/v2-production-experiment-service.log，已加载R16后端。source25c71f621ac16bb166b13a1b4216de20c6400e0a0e3f9fddec9fdebd0e531865；workspace860bc839513f/runtime23afa25c2bda。experiment-deployment.json记录重启、备份108cf5...fd95及原14Plan/10Snapshot原JSON与6表行数不变。UI后续改镜头后需要再次核对frontend fingerprint，后台source未变。8012仍旧隔离服务不可作最新验收。

完成本检查点后继续R15：在途依赖传播链/变化有效性与真实局部修复（当前执行残余是全量quick，不能声称依赖局部修复）；纯solver已有零时刻_try_local_repair可复用但不能伪造旧Plan身份链。先保留安全承诺/独立检查，再实现明确新合同与真实对比。之后R14/R22研究、完整最终回归和全状态视觉；不在本检查点停止。

## 最新继续点：地图专项通过并继续R15/R16（2026-10-18 19:50）

V2主分支05489b5已推GitHub；地图增量待本次提交。RFC023设备独立读回、RFC024事实边界均合入；地图6项浏览器55.8s、W1不遮点专项1项13.8s、lint零警告/12单元/build通过，截图实际查看。详情TEST_REPORT，不能重复初始化或在此停止。

8000已保护原数据并重启到当前后端。owned PID45064，start1792323612028，launcher37527，日志.local/v2-production-readback-service.log。workspace860bc839513f/runtime23afa25c2bda；原14Plan/10Snapshot原JSON与所有6表行数不变；readback-deployment.json记录备份SHA和身份，前端后续重建只需再次核对build fingerprint。8012仍是旧隔离服务，不当最新API。设备副工作树33e7fe4已合，勿重复合。

下一步R15依赖影响/真实反事实集成、R16独立评测中心（预算/seed/失败/日志），再R14/R22可做研究与R20当前源码全量/更多全状态截图。外部ODM/硬件/SITL/多基地任务仍保留，不能伪造。真实3名新用户试用缺真人，不算自动完成。

## 最新继续点：R12事实边界已验证，地图增量进行中

RFC-024事实驱动的承诺、暂停只读、退出/误报与未来就绪遥测已修复，11项组合通过98.14s；类型/构建通过。R06地图未提交增量：可空base用于空白任务真实选区、不伪造Scenario；宽航线点击区与候选选择；按任务保存镜头、resize/底图切换不强制fit；标签避让控件；命名空间选择修正。需继续实际浏览器密集50点/重叠航线/镜头/空白地图/离线与双尺寸验收，完善机体重叠选择。8000仍旧API，先验证新API后保护原数据重启。

## 最新继续点：R11读回已合入（2026-10-18）

模拟设备独立持久状态/后台命令调度/逐机启用读回已从隔离33e7fe4合入主V2，前端类型/查询界面/档案校验同步。后端组合15项及追加6项通过；浏览器真实在途插单与独立状态查询闭环1 passed（27.8s），lint/build通过。详情TEST_REPORT。隔离工作树保留且干净，不要再合5e5df65或33e7fe4。下一步R12：以事实判定已装载承诺、暂停读取不生成新事实、退出/误报与资源就绪遥测；然后R06地图密集点/重叠路线/镜头与空白选区。8000尚未重启加载这些新API，交付前需保护原14Plan/10Snapshot并统一重启校验。

# V2 连续实施交接（仍在开发，不是最终全量交付）

## 最新继续点（覆盖下方历史进程说明）

主V2已提交：cc7a20c复盘档案、7fde248进度容错、130cfa0新旧偏好隔离与完整回归证据；GitHub最新同步至cc7a20c，后两提交待推送。完整非浏览器6条通过（298 Python/8子测试/12单元/lint/build，源码不变）；完整浏览器42条是41通过/1旧动态设置失败，随后原失败用例与新跨路由偏好各1通过。不能写成同轮42全过。原旧输出94文件已归档并恢复，见legacy-regression-full/SOURCE_MAP.json；旧路径没有未提交更改。

8000仍为旧核心检查点PID4624，原10场景/10快照/14Plan/15Job/0Mission/0Execution最近核对未变，没有运行Job或Execution。最新只读基线.local/v2-before-r17-production.json；不要把当前dist+旧API视为已部署完成。

**正在另一个工作副本完成R11**：.local/worktrees/v2-device-readback，分支feat/v2-device-readback，基于cc7a20c；只稀疏检出源代码与必要14MB题设表格/DEM，沿用主项目.venv解释器。5e5df65进度容错已cherry-pick到主V2为7fde248，不重复合。该副本仍有未提交DeviceMissionState/SimulationDeviceStore、SimulationAdapter状态写入/读回、通用activate批准限制、后台command tick/逐设备启用回执、新5项读回测试；RFC-023。没有真实设备连接。

正在运行第三轮冻结源码专项：会话日志.local/v2-protocol-worktree-third.log，exec会话须查询；命令涵盖device_readback + progress_resilience + execution_v2 + execution_archive。第一轮10过/1个墙钟ACK断言失败；第二轮12过/1个短TTL被后台调度成sent→indeterminate，已改为承认合法未确定，并补控制时钟的严格ACK/过期无副作用测试。未标第三轮通过。代码第三轮期间不要再修改。

后续先检查该副本测试结果，修实质问题；补只读档案对observed_state引用校验与schema往返。测试稳定后在副本提交R11（不含已经合回的5e5df65），主V2用cherry-pick --no-commit应用，再同步frontend生成类型、设备状态/启用回执界面与浏览器验证后整体提交。副本没有frontend包，不在里面跑前端build；生成OpenAPI已78路径。确认当前主工作树无他人更改。

还需补已发现R12边界：ready/time0未开始的架次不能仅因prepare_start<=0就被误认作已装载承诺；未来故障机体不能在遥测列表显示“待命”，需要按未撤销事件投影可用性；测试先覆盖这些真实状态。完成后备份/重启8000，按R06密集点位/重叠航线/镜头/空白区域和R16评测继续，不能就此停止。

当前项目 yuanhang-uav-rescue；分支 `feat/mission-workspace-v2`。最新已提交 `cf3d73d`，GitHub已同步至 `aafff5b`，后续R12纠错及R17需继续提交/推送；main、V1两分支不变。两个人：A算法与负责人，B一人前后端。不要重复初始化，不要在读到检查点后停止。

## 当前进程与数据保护

- 8000正式本机服务仍是核心检查点3f32c30（旧工作字节），owned backend PID4624、启动epoch毫秒1792316179571、launcher会话27826；runtime/，workspace860bc839513f、runtime23afa25c2bda。R13/W1/R12新纠错/R17服务端尚未重载。dist在开发中更新，完整验收后必须将服务端/前端统一重启核对，不能把新界面+旧API当交付。
- 上次迁移前备份 `.local/v2-before-migration/yuanhang-backup-20261018T090731Z-d0a7a73a.zip`，SHA256 `5a461890b2c0f854496269efa45583ae89cd817cd0bce2d20c045966abcec640`。原14 Plan/10 Snapshot原JSON哈希完全不变，见production-migration.json。再次重启前重新查询当前身份/Jobs/执行并备份，不能盲停其他进程，不清库。
- 8012是旧隔离视觉服务，owned PID57168、start1792314394773，runtime `.local/v2-runtime`；目前代码落后本轮，不作为当前API验收。
- Playwright仅运行8011/5174、`.local/e2e-runtime`。运行包/模拟事实不写8000。后台启动隐藏窗口；退出只停止核实归属的进程。

## 已实现的当前软件

- 新根首页/任务/资源/演练导航；任务准备4步→真实Job→方案/地图/安排→确认→模拟→变化/真实修复→复盘。旧App与旧hash入口仍保留。
- Mission草稿/版本/CSV-JSON-XLSX导入预览/模板/预检；空白非原题场景能从GUI完整录入与求解。旧Scenario、Snapshot、Plan、Event、确认预约事务保留。
- 持久化服务器时钟与不可变事实；暂停、倍速、断流/重连、刷新恢复；独立会话与序号。DeviceAdapter只有SimulationAdapter，202/ACK/完成/未确定分开；无真机/SITL。
- 承诺前缀保留已开始完整架次/在机箱件，未来资源按释放时间进入真实残余Worker与独立validate；有限地面模型保守共同边界。逐设备上传状态查询后采纳，一台ACK超时不激活新排程。
- RFC018：联合Plan中继阶段/能源组件/服务窗口、事实与模拟遥测；联合在途修复仍UNSUPPORTED_SCOPE。
- RFC019：人工W1气象来源/机型规则/有效窗口进入quick排程和独立验证/执行事件；无风致能源/预报。WeatherRule完整类型，生成器strict-refs。旧无weather数据不补字段。
- RFC020：未处理事件统一阻断start/resume/advance；误报纠正追加审计，不改原事件/事实，已采纳不能撤销。SSE游标续传、超前拒绝、线程池读取。UI处理状态与服务端一致。
- RFC021（当前未提交工作）：ExecutionTimeline按各Plan生效段展示机体/电池/中继组件与事实；复盘交付阶梯/逐箱偏差/来源；v2完整执行包有原文Plan/Snapshot/事件与纠错、指令、Job引用。只读导入execution.archive，不创建可控领域行；v1导出兼容。资源中心运行档案，事实时间筛选不写账；没有连续历史遥测就不造轨迹。

## 实际验证范围

- core-checkpoint、relay-checkpoint、weather-checkpoint、resolution-checkpoint各自为历史增量，不冒充当前全量通过。
- 当前V2新增组合19 passed，92.33s；正式V2四流程4 passed，56.0s；之后配色/确定性截图档案闭环另跑1 passed，25.7s。前端12单元、lint/build曾通过，正在整体复核。R17两项专项2 passed，25.57s。
- 源数据：EXECUTION_SMOKE/inflight-repair-archive.json实际2 Plan/2 Snapshot/53事实/33交付；SCENARIO_MANIFEST记录原文与哈希。未将保存候选当新求解，未将导入当物理重认证。
- **当前整轮回归运行中**：`.venv/Scripts/python scripts/verify.py --output-dir evidence/redesign-v2/full-verification`，会话18942，日志 `.local/v2-full-verification.log`；包含全部pytest（历史约9分钟）+契约+治理+lint+12单元+build。运行期间不要修改测试/源码/生成契约，使source_unchanged证据有效。
- **当前完整浏览器运行中**：`node frontend/scripts/run-e2e.mjs`，会话36517，日志 `.local/v2-full-browser.log`，报告full-browser-results.json。旧浏览器输出143文件已先备份到 `.local/v2-before-full-browser.zip`/json，32.6MB。
- 完整浏览器结束后将本轮改动的旧路径输出复制到evidence/redesign-v2/legacy-regression-full/并记录映射，再从该ZIP恢复旧路径原字节。只处理明确由本次测试生成的输出，不重置用户修改，不删除原数据。R17自身图片/报告直接位于redesign-v2。
- 查看真实截图发现并修了：通知挡按钮、发布重置准备页签、点位点击冒泡、时间轴背景被全局按钮样式覆盖；最新复盘/排程/档案截图已实际查看。更多尺寸/异常不可据此自动算通过。

## 下一步（仍需继续实施）

1. 等当前两轮完整验证，修复真实失败并准确重跑；检查报告源码未变化。整理历史输出；R17更新测试/视觉/任务板证据、提交清晰检查点并推送独立分支。
2. 先补R11通用commands的模拟设备状态读回：目前生命周期按时钟变化，但通用upload/activate没有独立持久设备状态，不能将计时到达称实际读回成功。限制未批准候选的直接activate；保存uploaded/active状态与读回证据；ACK超时/完成未确定通过独立state.query核对，不盲重试。逐设备采纳当前保护排程，但这处接口质量仍需修正。之后备份并核对原Plan/Snapshot哈希，安全重启8000加载已验证新API+dist；再次核对runtime、源码指纹、原数据和启动能力。
3. **R06/R18/R20**：50点/长名/点线甘特联动、重叠航线宽点击区与候选选择、标签避让控件/气象、机体重叠、镜头保持、空白任务选区域、1024与离线/WebGL失败/反复切换。仍有真实可做工作，不用占位按钮。
4. **R12/R14/R15**：多次采纳与有限地面专项；条件有效性/影响依赖与真实增配对比；更多飞行/交接残差。当前仅保护完整已开始架次，非任意位置改航，不声称最小改动最优。
5. **R16/R22**：实际演练评测案例/预算/seed/失败/原始日志与消融；学习仅在真实搜索日志训练/测试隔离后开放。无数据不标AI成功。
6. **R21/R23/R24**：完善运行/许可/匿名材料；航片ODM、硬件/SITL、多基地等按缺数据/环境具体追踪，不能静默删任务或用Mock充能力。3名新用户试用缺真人，不能由自动脚本代替。

任务唯一状态为docs/task-board.json；大部分R仍in_progress。INDEX、FEATURE_TRACEABILITY、API_MIGRATION_MAP、TEST_REPORT、VISUAL_REVIEW、DEMO_GUIDE、KNOWN_LIMITATIONS同步维护。完整输入在docs/redesign-v2/，初次已读，不每个小任务反复全文读取。
