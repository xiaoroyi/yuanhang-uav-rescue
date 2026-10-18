# 开发样例

index.json 为样例清单。mock/ 全部是人工开发数据，没有真实求解的成功样例；plan 的时间只是占位，solver_status=UNKNOWN、has_validated_plan=false、validation=not_run。MOCK_UNSUPPORTED 物理模型禁止作为真实算法输入。

运行 scripts/check_contracts.py 校验结构与基本引用。真实算法完成后，另建 regression/，保存来源、配置、commit、快照hash与实际输出；不得只改 Mock 标签冒充实测。
