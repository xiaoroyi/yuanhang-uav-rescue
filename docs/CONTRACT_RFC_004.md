# RFC-004 本地DEM资产注册与上下文

状态：implementation-branch，待团队复核。复用Scenario.terrain现有asset_id/sha256/CRS/vertical_datum字段，不改变旧核心对象。

新增独立HTTP资产列表/上传/绑定DTO。GeoTIFF上传在项目runtime/assets保存源文件hash和归一化只读栅格；最多16MiB、单波段、源/目标最多200万像元，必须有CRS和声明的米制垂直基准。非北向WGS84栅格通过Rasterio重投影，以max重采样，并单独max传播NoData掩码；不能把未知空洞填成已知高程。该处理仅认证准备后的栅格模型，不保证现实障碍完整性。

资产以归一化NPZ内容SHA256寻址，ID为DEM-加hash前20位。同ID内容不可原地替换；Scenario绑定完整hash和声明基准。API不接受本机路径或外部URL。Solver通过solver.assets.terrain_store(directory)只读上下文查找资产，默认项目runtime/assets；HTTP/Worker明确注入本实例资产目录，不读数据库，不向SolverOptions暗加路径字段。旧题设asset_id保持原加载与hash。

绑定资产创建新场景版本，可选择从DEM提取基地/服务点高程；旧快照及历史方案保留。点位或航段触及NoData/覆盖外即拒绝认证。地图只显示该场景绑定的DEM，不以原题地图冒充新区域。

元数据记录来源文件hash、CRS/变换、原始/准备栅格尺寸、垂直基准、NoData比例与处理方法。资产列表/原始下载/准备栅格由后端管理；源数据和运行库不提交Git。原题只读归档不修改。

参考：[Rasterio重投影](https://rasterio.readthedocs.io/en/stable/topics/reproject.html)、[warp API](https://rasterio.readthedocs.io/en/stable/api/rasterio.warp.html)。
