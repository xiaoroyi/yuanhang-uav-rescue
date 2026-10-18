# RFC-014 地面容量增配试算

状态：proposed，按本轮分支授权实施，正式A/B复核待完成。核心Scenario/Plan及Schema版本不变，只扩展已有HTTP情景请求和来源DTO；实际实现及测试以IMPLEMENTATION_STATUS为准。

## 输入与语义

现有`POST /api/v1/scenarios/{scenario_id}/what-if`新增可选`ground_addition`。缺省或null沿用原变换；非null要求源场景已经配置有限`resource_limits`，不能把原本无限容量解释成零个资源。

```json
{
  "expected_state_version": 2,
  "name": "增加地面保障",
  "ground_addition": { "prep_slots": 1, "charging_ports": 2 }
}
```

两个数均为严格非负整数，不接受布尔、分数或数字字符串。增量prep_slots上限31、charging_ports上限63；与原数量相加后仍须分别不超过32和64。省略的增量为0。该功能只能增加有限资源数量；改变或取消容量限制仍走场景设置和正常版本保存。

所有变换发生在深拷贝的新Scenario；源版本、Snapshot、Plan、硬截止、必须保障数量、资源身份和通信参数保持。地面工位/端口按既有模型由运输与中继共享。新场景继续通过真实Snapshot→Worker→Solver→独立检查，前端不估算排队减少量，不保证启发式结果的每项指标单调改善，不声称最少增配。

## 来源与兼容

`ScenarioOrigin.transformation_version`扩展为`what_if_v1 | what_if_v2_ground_capacity`。携带非null ground_addition的新请求使用第二个标签；缺省/null保持v1，来源parameters不新增无意义null字段。旧持久化v1记录、旧请求和原16份Mock例继续有效。

该新标签需要同步升级消费者，不能假定旧的严格枚举客户端会识别v2。后端DTO、实际OpenAPI及生成TS同批更新；不手写第二套前端请求类型。事务、源版本和source_plan_id校验沿用原接口，参数错误在新场景入库之前返回422，不留下半成品情景。

## 页面与验收

资源分析试算区显示基线工位/端口和增量输入。源场景未设置上限时禁用，并提示先在场景设置启用；默认提交不传新参数，旧情景流程仍可用。来源与历史记录展示真实变更说明，刷新可恢复。

验收包括：有限资源真实重算与独立检查；无限源、越界、非整数和混合未知字段拒绝且无入库副作用；原版本/Snapshot/Plan不变；历史v1兼容；生成类型无漂移；实际浏览器增配、比较、导出、刷新与桌面/窄屏检查。
