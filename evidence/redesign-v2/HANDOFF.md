# V2 连续实施交接（仍在开发，不是最终全量交付）

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
