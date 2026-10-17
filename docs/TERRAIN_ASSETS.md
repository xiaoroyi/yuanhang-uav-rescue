# 通用本地DEM资产

场景页“管理DEM资产”支持上传GeoTIFF、选择本地资产、查看CRS/高程基准/有效比例/内容hash，以及下载来源文件。导入仅注册栅格；“绑定DEM并保存新版本”才更新场景。默认可从DEM提取基地/服务点高程，也可保留已确认的输入高程。始终检查点位是否覆盖；实际航路含绕行的全部净空在求解与独立验证时检查。

支持单波段、带CRS、米制高程；文件最多16MiB，源与准备栅格最多200万像元。北向EPSG:4326保留原网格；其他水平CRS/旋转网格经Rasterio重投影，目标高程使用max，NoData掩码独立max传播，未知覆盖不通过插值抹除。像元模型仍不代表现实地物/障碍完整性。垂直基准需由输入者声明，系统不自动做大地水准面转换。

归一化资产为`runtime/assets/<SHA256>.npz`，含高程、经纬度轴、NoData与来源元数据。ID为DEM-加hash前20位；Scenario.terrain保存完整hash、EPSG:4326和匹配的垂直基准。原文件保存在`runtime/assets/sources/<source_SHA256>.tif`，原题MAT/TIF只读保留。资产内容不能原地替换，文件变化会使读取检查失败。地图展示同一绑定资产的离线晕渲，未知像元透明；旧Plan依旧显示其Snapshot绑定的旧DEM。

Solver保持只读JSON边界与独立Python调用，不读HTTP/数据库。纯Python使用自定义资产库时：

```python
from solver.assets import terrain_store
from solver.public_api import solve

with terrain_store("path/to/runtime/assets"):
    outcome = solve(snapshot, options)
```

后端每个请求注入本实例资产目录，独立Worker根据其runtime/jobs/JOB-id/input.json确定同一资产库；不把机器路径塞入核心SolverOptions或暴露给浏览器。默认库为项目runtime/assets。源/归一化hash、CRS、垂直基准、尺寸、有效比例和处理方法均可追溯。

当前资产准备在有界后台线程完成，HTTP保留响应；尚不是可取消/断点续传的长期建图队列。场景JSON包含资产引用，不内嵌二进制；给另一台电脑交接用户DEM时，应同时下载来源GeoTIFF并按相同垂直基准重新注册，核对归一化hash。原题资产随仓库只读参考文件提供。runtime属于本机运行数据，不提交Git。

验收包含：原题真实GeoTIFF上传→新版本绑定→新Snapshot→真实Worker→独立检查→确认→地图→来源下载；EPSG:3857重投影；NoData保留及航段拒绝；资产目录隔离；文件破坏hash拒绝；缺失CRS/非TIFF和路径型ID拒绝。代码与证据见tests/backend/test_terrain_assets.py、evidence/browser/verified/terrain-*.png。协议兼容说明见RFC-004。

实现参考 [Rasterio重投影](https://rasterio.readthedocs.io/en/stable/topics/reproject.html) 与 [warp API](https://rasterio.readthedocs.io/en/stable/api/rasterio.warp.html)。
