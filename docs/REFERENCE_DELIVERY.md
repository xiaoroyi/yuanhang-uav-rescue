# 援航V4完整参考包

用途：供师兄内部阅读、交流与本机演示，包含当前系统与打包时的完整运行数据。平台为Windows10/11 x64；无需预装Python或Node，不安装系统服务、不修改注册表、不连接真机或收费API。

## 启动

先完整解压，建议放到较短路径，例如`D:\Yuanhang`，双击根目录`start.cmd`，保持窗口开启。浏览器自动打开`http://127.0.0.1:8000/`；关闭窗口或Ctrl+C停止，重启保留本包内数据。如果8000被占用，在本目录终端运行`start.cmd --port 8001`，不会结束原程序。不要在压缩软件内直接运行，不需要先执行setup.cmd。

首页进入“救援任务”即可查看已有任务、真实方案、安排表和执行记录。新任务可从案例库选择山地、洪涝、通信协同或原题场景。标准引擎默认；EOH增强是本地评分包，内置包为规则初始化，未运行外部LLM进化。

## 随包内容

| 内容 | 位置与说明 |
|---|---|
| 前后端与求解器源码 | frontend/src、backend、solver、shared、contracts；当前工作树快照 |
| 已构建前端 | frontend/dist，包含地图上下文、字体、图表代码和教程视频；无需Node常驻 |
| Python与项目依赖 | portable-python；本机匹配CPython3.11与锁定项目依赖，采用相对路径隔离，与作者原Conda目录无关 |
| 原题输入与地形 | references/modeling/data，包含5张输入表与GeoTIFF/MAT地形；原论文和历史答案留在仓库，不进入演示包 |
| 运行数据 | runtime/yuanhang.sqlite3、地图/导入资产、本地策略和已完成Job工作件；任务、版本、快照、Plan、事件、执行事实、预约及操作记录保留 |
| 数据安全副本 | data-backup/下的一致性ZIP；通过SQLite backup接口生成，保留清单和hash |
| 对外文档 | docs/PROJECT_DEMO_GUIDE.md、6页《援航项目介绍与演示指南》及四张实际页面截图 |
| 包身份与文件清单 | BUNDLE_MANIFEST.json，含基线commit、服务/前端指纹、打包时间、各表数量、每文件SHA256 |
| 许可 | frontend/dist/THIRD_PARTY_NOTICES.txt、portable-python/LICENSE_PYTHON.txt、licenses与各Python包dist-info许可 |

按用户最后要求，对外包不包含内部分工、AGENTS、Codex提示词、任务板或独立实验对照记录。仓库的三份内部总文档/提示词仍更新维护，但不导出给师兄。Git历史、浏览器Cookie、密码/令牌、.env、SSH密钥、原作者Conda整环境、node_modules、GPU模型权重和临时测试库也不进入参考包。原电脑的浏览器头像/配色等个人偏好不携带，新浏览器使用默认深蓝界面。

## 演示顺序

1. 首页观察真实地形、点位、平台能力与创新入口。动画可关闭。
2. 进入已有任务，查看方案地图、调度安排、逐箱/架次、Excel导出、机体和电池时序。
3. 打开地形与航迹，查看真实巡航/升降剖面；通信方案查看中继驻点、服务窗口和空间覆盖分析。
4. 执行跟踪查看已保留的暂停或完成实例、运输看板和复盘。继续模拟会更新本包自己的数据。
5. 另建小演练，条件检查后真实计算，可对比策略或两种引擎。原输入变化生成新快照，原方案不覆盖。
6. 需要了解项目时读docs/PROJECT_DEMO_GUIDE.md或同目录图文Word，直接按演示步骤操作。

核心地形、路线、图表、字体、安排表、教程视频与重新计算可离线运行。在线卫星图和外部来源网页需要网络；它们不是离线包缺少计算数据。真机/SITL、多用户权限、LLM进化和在线天气服务没有因此变成已完成能力。

## 校验 备份与继续开发

首次启动前可运行：

```powershell
portable-python\python.exe scripts\check_reference_bundle.py --initial-data
```

日常使用后数据库会正常变化。此时不带`--initial-data`仅核对静态交付文件并检查数据库完整性。`backup.cmd`可生成新的完整一致性备份；恢复使用scripts/backup.py的`--restore`与尚不存在的新目录，不覆盖已有数据。

参考包没有.git。修改程序时先保留原ZIP和数据备份，在独立副本建立开发环境；不要再clone一份空数据仓库覆盖参考包，也不要编辑便携环境来替代正式依赖管理。前端源码变化后需要Node与锁定依赖重新构建；纯演示使用已构建版本即可。

便携Python以CPython相对模块路径和本地DLL目录运行，技术依据为[Windows模块路径](https://docs.python.org/3.11/using/windows.html#finding-modules)与[DLL目录接口](https://docs.python.org/3.11/library/os.html#os.add_dll_directory)。本轮实际验证包含移动到另一个路径后的启动、原记录读取、地图与视频、原题输入、Excel和新方案真实计算；准确结果以交付检查报告为准。未在另一台物理电脑上实测，不承诺不同硬件下搜索结果或耗时逐位相同。
