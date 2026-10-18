# 视觉与交互复核

采用浅色操作面、深色侧栏、统一Radix/Lucide组件语义和克制强调色，参考Tabler/shadcn-admin的信息层级。首页是独立展示页；工作台以实际地图、任务与表格为主体。没有复制外部界面截图充当本系统。

| 页面 | 看过的实际截图 | 处理结果 |
|---|---|---|
| 首页 | release-home-1440 / home-1280 | 大标题与主操作突出；协同动态有来源/示意标记，系统减少动态效果生效 |
| 准备与检查 | prepare-1440 / checks-1440 | 四阶段与子步骤分明，已填写与检查通过不同；下一步给出名称 |
| 安排表 | schedule-1280 / schedule-dark-1440 | 压缩重复工具与摘要，首屏直接出现运输行；横向滚动限于表格 |
| 地图 | plans-1440 / plans-1280 / plans-1024 | 默认收起大甘特，主图高度502/383/431；角色标签与5/50点既有碰撞机制保留 |
| 地形 | release-terrain-1440 / profile-1440 | 地面投影与真实阶段航迹分色；竖线显示升降；标签越界/冲突时隐藏而非堆叠 |
| 通信 | communication-1440 / coverage-1440 | 连接链、来源窗口、中继排程与离地高度采样分开；颜色区分直连/中继/不通/未知 |
| 执行 | execution-1280 / release-fleet-1440 | 大地图与运输看板切换；数量/电量/速度/下一任务各自成列，低频动作收入更多菜单 |
| 变化与复盘 | repair-1440 / review-1440 | 保留承诺、重排/换机/换电池/新增量可核对；当前界面调整状态已中文化 |
| 资源 | resources-1440 / resources-fleet-1280 / resource-dark-1440 | 先选任务，再管理资源；不会把不同任务的同名机体并为一架 |
| 数据分析/大屏 | release-insights-1440 / data-screen-1440 | 普通分析优先图表，三维另有专页；只读全屏可切综合与详细 |
| 帮助 | release-help-1440 / help-1280 | 实际截图、分章步骤、对应入口、可播放录屏与可加载中文字幕 |

对应机器记录为browser-review.json、visual-finish.json、bundle-smoke.json和production-smoke.json。截图名称均相对`screenshots/`。不是仅检查空页面或仅以build通过下结论。
