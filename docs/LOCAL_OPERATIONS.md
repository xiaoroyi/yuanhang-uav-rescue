# 本机安装、版本检查与数据备份

## 日常启动

双击start.cmd，或在仓库根目录执行`.venv\Scripts\python scripts/launch.py --open`。默认只监听127.0.0.1:8000，使用runtime/数据，关闭服务窗口或Ctrl+C停止。无需登录、Node进程或外部地图服务。

启动器会核对当前项目、数据目录和后端进程启动时的源码身份。代码更新后若旧服务仍在运行，会说明需要关闭旧窗口并重启，不会自动终止未知进程。不同数据目录或其他程序占用端口时，使用`--port 8001`启动另一实例。

前端构建在frontend/dist/assets/build-info.json记录源码hash和产物大小/hash。启动时核对全部已记录产物，防止过期或不完整构建。构建有效时不调用Node/npm；需要更新且已有项目依赖时，离线执行npm run build，不隐式安装依赖。缺少依赖时先运行setup.cmd。

`/api/v1/health`增加service_source_sha256与runtime_id，用来区分代码和数据目录，不返回目录原路径。前后端源码身份规则在shared/build_info.py与frontend/scripts/build-info.mjs，并有跨语言一致性回归。验证脚本另记录测试前后源码身份，测试过程中改动代码不能被记作同一版本完整通过。

## 首次安装与检查

新电脑安装Python3.11/3.12与Node24后运行setup.cmd。入口优先使用已有项目环境，否则依次检测py3.11、py3.12及PATH中的兼容Python。依赖只装入.venv和frontend/node_modules，版本取锁文件。

```powershell
.\setup.cmd --check
# 只检查Python/Node/npm，不创建环境或安装依赖
.\setup.cmd
# 需要浏览器回归时才额外安装项目内Chromium
.\setup.cmd --with-browser
```

.env.example只说明可选的shell/IDE环境变量，程序不会自动读取根目录.env。默认配置无需环境变量即可使用。需要其他数据目录时，在启动命令所在终端设置YUANHANG_RUNTIME；前端开发代理可设置YUANHANG_API_URL。不要把凭据写入仓库。

## 备份正在运行的系统

双击backup.cmd，或在仓库根目录执行：

```powershell
.venv\Scripts\python scripts/backup.py
```

备份写入runtime/backups/yuanhang-backup-时间-随机ID.zip，不覆盖既有备份。SQLite使用backup API取得一致性快照，包含已提交的WAL内容；不能用资源管理器直接复制正在运行的.sqlite3文件来代替。自定义地形资产一并加入，清单记录各文件字节数/hash、数据表行数、源码身份和Git信息。

归档不包括源码、依赖、日志、凭据或备份自身；原题只读DEM等来源仍由同一仓库提供。上限为4096个条目、512MiB展开大小。备份只保存数据，不能代替Git代码版本；未完成任务不会变成可继续执行的原进程。

```powershell
.venv\Scripts\python scripts/backup.py --verify "runtime/backups/实际文件名.zip"
```

验证会检查路径、重复条目、清单、大小、CRC与SHA-256，不直接extractall解压。备份文件属于本机运行数据，已被Git忽略；需要交接数据时单独移交该ZIP。

## 恢复到独立的新目录

恢复不会覆盖已有目录，包括已有空目录。选择一个尚不存在的路径：

```powershell
.venv\Scripts\python scripts/backup.py --restore "runtime/backups/实际文件名.zip" --into .local/restored-data
$env:YUANHANG_RUNTIME = (Resolve-Path .local/restored-data).Path
.venv\Scripts\python scripts/launch.py --port 8001 --open
```

这样可在8001核对恢复结果，同时保留8000的原始数据。恢复逐文件核对hash，再检查SQLite完整性，成功后才将暂存目录改为目标目录。错误不会改写原运行目录；若核验后的恢复过程失败，错误信息会指出保留的暂存目录。

恢复后检查场景、快照、历史方案、事件和自定义DEM。重启时中断的任务按现有异常恢复规则标记，不会伪装成已完成结果。停止恢复实例后，可在同一终端执行`$env:YUANHANG_RUNTIME = $null`回到默认数据配置。

## 已执行的检查

tests/engineering覆盖有效构建不调用Node/npm、源码/产物变化、资源路径限制、旧服务与其他数据目录拒绝复用、离线重建、相对数据路径、运行中WAL内容备份、原方案/快照HTTP恢复、资产字节、重复备份不递归、已有目录不覆盖、损坏/穿越/重复/清单外归档拒绝。

evidence/engineering/startup-smoke.json记录实际8000服务的启动身份与重复启动复用；backup-smoke.json记录当前演示库2个场景/3份方案恢复至新目录，原始JSON记录和HTTP输出都一致。evidence/browser/production-offline.json记录生产构建在仅允许本机HTTP(S)请求时的求解、确认、故障重规划和导出，外网请求与控制台错误均为空。
