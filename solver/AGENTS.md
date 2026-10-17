# A 算法模块

遵守根 AGENTS。维护算法、适配器、独立检查与实验，跨共享契约先 RFC。先读 docs/05、LEGACY_BASELINE_AUDIT与IMPLEMENTATION_STATUS。当前已有public_api，不重新搭空壳。

保持纯 Python JSON 边界，不 import backend，不在导入时写文件、下载数据或运行搜索。路径从配置/参数进入，禁止绑定个人绝对路径。先封装已核验物理模型，再做快速初解。独立验证不能只复用优化器的 passed 布尔结论。

物理在physics.py，题设数据适配器adapters/contest.py，独立重建检查validation.py，调度public_api.py。默认5点32箱，contest保留15点80箱；快速限时多起点启发式和全量重规划已实现，依赖图局部修复/中继尚待开发。真实耗时与证据存evidence/solver/。原题Q2/Q3不宣称全局最优，Q4必须继承同版Q3。单人跨模块授权见根AGENTS。
