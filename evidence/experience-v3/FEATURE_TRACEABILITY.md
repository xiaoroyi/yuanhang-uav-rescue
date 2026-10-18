# 功能追踪

| 用户诉求 | 实际入口与实现 | 主要证据 |
|---|---|---|
| 1. 独立安排表、像答案表、可导出 | 方案规划→调度安排：运输、逐箱、中继、通信、资源；筛选/详情/CSV/六页Excel | schedule-1280、sortie-detail-1440；live-check.json；test_experience_v3.py |
| 2. 精致独立首页、图标、动态背景、优势 | 独立顶栏首页、原创山地协同SVG动态、真实案例规模、应用场景和3个可执行创新点 | release-home-1440；RESEARCH.md；Motion/Radix/Lucide锁文件 |
| 3. 图文帮助、录屏、跳转 | 5章图文、真实截图、约38秒实际操作录屏、9段中文字幕、术语检索、对应模块跳转 | release-help-1440；production-readonly.json（实际字幕已加载） |
| 4. 二三级菜单 | 任务4阶段图标/完成勾/箭头；准备4项已填写与检查状态；规划5种视图 | prepare-1440、plans-1280；browser-review.json |
| 5. 点位角色、3D/剖面、论文约束 | 调度中心/救援点标签与碰撞避让；原始DEM、真实阶段升降3D、剖面、逐段净空/载荷/能源 | release-terrain-1440、profile-1440；CONSTRAINT_TRACEABILITY.md |
| 6. 原题通信、中继安排与覆盖 | 小规模/原题联合模板；通信专页、两跳保障、能源时序；指定离地高度的真实空间采样 | coverage-1440；cases/contest_joint.json（80箱、23运输、3中继、模型缺口0秒） |
| 7. 偏好下拉无随机尾号 | 显示时间/能耗/折中、方案序号、输入版本；原始ID保留到来源详情 | schedule-1280、schedule-dark-1440 |
| 8. 文字通俗可读 | 返航时间与能耗取舍标题、中文调整状态、图标提示、SOC/DEM/净空/ACK等术语；浅/深主题 | help-1440、fleet-1440；Ctrl K导航实测 |
| 9. 资源按任务组织 | 任务卡→本任务地图/机队电池/需求库存/运行；另列外部只读档案；旧输入可接入任务 | resources-1440、resources-fleet-1280、release-missions-1440 |
| 10. 精致进度与流程反馈 | 实际阶段计算条、已用时与候选数；不伪造完成百分比；准备状态与阶段完成勾 | solve-progress-1440、checks-1440 |
| 11. 整体复核与同类参考 | Tabler/shadcn-admin/QGC/Fuselab等参考；补快速搜索、可发现的旧历史、生产媒体路由及执行确认保护 | RESEARCH.md；RFC031；production-smoke.json |
| 12. 无人机图标、运输状态、每机实况 | 运输进度账本、目的地/交接/空载返航、下一架次、逐机电量估计/端点、模型水平/垂直速度；断流冻结 | release-fleet-1440、execution-1280；2条数量守恒单测 |

整体复核额外修复：调整后总量必须包含已交付/在途承诺；普通确认不能覆盖已有实例预约；生产服务正确托管教程图片、视频Range与VTT，不回退成HTML。三项都记录了实际发现和修复范围，没有把静态界面或历史案例当成新能力。

上述截图相对`screenshots/`；状态唯一来源仍为`docs/task-board.json`。未完成的训练、真机、外部建图、多基地等原任务保留，不因本轮界面交付被标成完成。
