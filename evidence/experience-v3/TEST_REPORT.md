# V3实际检查记录

按用户要求做针对性功能检查、真实计算和视觉检查，没有重复整套长回归。以下是分批执行的范围，不代表一次运行了全项目所有测试。

| 检查 | 实际结果 |
|---|---|
| test_experience_v3.py + test_execution_boundaries_v2.py + test_relay_execution_v2.py | 7 passed；联合模板隔离、Excel/空间采样、执行零秒/暂停边界和中继阶段 |
| test_execution_confirmation_v3.py | 2 passed；ready/paused实例拦截新确认，预约/事实/方案不变，旧回执可读 |
| test_ui_media_v3.py | 1 passed；生产媒体MIME、206字节范围、VTT、声明文本与缺文件404 |
| test_execution_archive.py / test_operation_contracts.py | 前一批2项通过；旧档案与DTO扩展兼容检查。未在最后再次重跑 |
| execution-progress.test.mjs | 2 passed；原32箱＋新增1箱＝33，保留已交付/在途；不重复计入迟到遥测里的已交付箱件 |
| 前端严格typecheck / lint / 正式Vite构建 | 通过，3128模块，离线构建21文件；源码/运行身份见release-identity.json |
| check_contracts.py / check_governance.py | 通过。契约脚本仅做结构/引用/状态/Hash，不把18个Mock当算法验证 |
| 实际Worker与原题 | 3个真实案例重新计算；当前独立校验全部passed，输入/方案/复算保存在cases/ |
| Excel与空间采样实际API | 六表行数与源Plan核对，文本无公式；读前读后Plan/Snapshot相同。225点示例135直连/56中继/34不通；独立空间结果不当连续覆盖认证 |
| 浏览器真实闭环 | 新建→检查→计算→安排表/导出→地形→确认→开始模拟→交付→新增需求→修复/差异/采纳→复盘；passed、无页面异常 |
| 布局/主题/帮助 | 1440×900、1280×720、1024×768；主地图502/383/431px，页面无水平溢出；表格首行可见；浅/深色、全屏、快捷搜索、视频和字幕已实际查看 |
| 正式8000服务 | 离线首页、现有3任务安排/执行只读、帮助图片、37.68秒视频与9段字幕均通过；启动器识别正在运行的正确版本 |
| 数据保护 | 备份核验通过；13场景/26快照/29方案/30Job/3任务/3暂停实例保留；原29方案与26快照原文Hash一致 |

发现并修复：新测试最初使用错误旧URL；复核脚本误把已打开菜单关闭；V3摘要漏算被剩余快照排除的在途箱件；旧确认入口未保护执行预约；生产媒体未托管且Windows缺MIME映射。前两项为测试定位问题，后三项为产品问题，均有后续实际验证。初次生产静态失败报告保留在production-static-initial-failure.json；最后结果看production-smoke.json、production-readonly.json。

有一条环境弃用提示：Starlette建议未来迁移httpx2；不影响本轮通过结果。没有把未运行的全量CI、真机/SITL、训练/消融等写成已通过。
