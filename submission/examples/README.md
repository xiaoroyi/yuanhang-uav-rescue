# 去个人标识演示样例

scenario-demo.json可在“场景与资源 → 导入”作为Scenario JSON预览并导入，也可直接交给Solver CLI。它基于原题5点32箱子集，替换场景标识与地点显示名，并将第一箱由3kg/12L改为4kg/15L，明确标为user_input。需求、库存和实体引用仍符合当前契约，provenance.json记录变换与内容hash。

地理坐标与题设DEM保持，未声称地理匿名、原题数据授权或正式赛事匿名审查完成。此目录没有旧论文的作者/学校/队号，正式提交仍须按官方通知审核附件、文件属性、视频和源码包。

复现输入变化后的真实运输计算：

```powershell
.venv\Scripts\python -m solver --scenario submission/examples/scenario-demo.json --seconds 15 --output submission/examples/solve-result.json
```

输出包含完整Snapshot、Options、Outcome、真实Plan与独立验证，不能仅用截图代替它。结果生成和核对后在交接报告中记录；不要手写passed或复制原题方案填入该文件。
