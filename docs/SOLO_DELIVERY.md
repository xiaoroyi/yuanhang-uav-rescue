# 单人全栈版本交接

本报告仍在最终验收中，最终结果以evidence/verification/latest.json、实际CI提交和本文后续更新为准。两人分工：A算法兼负责人，B同一人负责前后端与集成。今晚跨模块实现仅在feat/solo-fullstack-v0，不改写main。

## 1. 版本与可运行成果

当前源码检查点877b220，包含真实运输、独立检查、限时深入优化、通信中继、冻结分区、单点诊断、容量下界、版本化后端与三页离线前端。最新提交请执行git rev-parse HEAD核对；最终文档/材料提交可能晚于源码验收提交，源码指纹用于关联实际测试。

动态事件支持整个场景尚未执行时的机体退出、运输电池退出、中继能源组件退出，以及已有救援点的紧急需求与实物库存插入。新版本真实计算，原Snapshot、Plan与Event保留。没有把回放写成遥测或实飞。

核心入口为solver/public_api.py、backend/app/main.py、frontend/src/App.tsx；独立检查solver/validation.py；共享验证shared/contracts.py。状态、完整任务与来源分别见IMPLEMENTATION_STATUS、08-TASK-BOARD和SOURCE_TRACEABILITY。

## 2. 本机环境

已实际检测Python3.11.15、Node24.16.0、npm11.13.0，使用项目.venv、frontend/node_modules和项目内Playwright Chromium。Python与前端锁文件均已保存。NumPy/Numba/OR-Tools、Rasterio/PyProj、React/TypeScript、MapLibre和ECharts均已实际运行，不要求CUDA或独立GPU。

首次安装执行setup.cmd；当前电脑已安装后双击start.cmd，访问http://127.0.0.1:8000/。有效生产产物不需要Node或联网。生产数据runtime/保留，测试、录像使用.local内独立目录。运维与备份见LOCAL_OPERATIONS，不把数据目录当缓存清理。

## 3. 可复制命令

在仓库根目录执行，Windows使用npm.cmd。新电脑先安装Python3.11/3.12和Node24，再setup.cmd。

```powershell
# 一体化本机服务
.venv\Scripts\python scripts/launch.py --open
# 分离开发服务，两个终端分别运行
.venv\Scripts\python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
npm.cmd --prefix frontend run dev
# 独立算法，原题将compact改为contest
.venv\Scripts\python -m solver --example compact --seconds 15 --output evidence/solver/run.json
# 完整业务、契约、构建及浏览器检查
.venv\Scripts\python scripts/verify.py --browser
# 单独生产构建或浏览器验收
npm.cmd --prefix frontend run build
npm.cmd --prefix frontend run test:e2e
```

E2E使用独立8011/5174，不覆盖演示库。CLI与完整测试可能占用CPU，正式演示时不要同时跑大规模回归。新电脑的安装依赖网络；本机已准备后的运行支持离线。

## 4. 三页与演示交互

页面均从左侧导航进入，不需要登录：场景与资源维护输入和地图资产；调度工作台求解、路线/箱件/甘特联动、策略比较与确认导出；事件复盘提供动态事件、资源试算与冻结任务分区。

最值得演示的流程：新建32箱演练→真实求解与同快照策略比较→确认并导出；选择已使用的电池或中继能源组件退出→新版本重算与历史对比；插入2箱紧急需求和等量实物→34箱完整服务，再以不可能硬截止展示不发布无效方案。现场步骤见DEMO_RUNBOOK，演示稿讲述见DEMO_SCRIPT。

## 5. P0/P1/P2状态

输入、真实算法闭环、独立Worker、版本/事务/历史、离线三页和常规故障重规划等P0核心已实现。已完成的P1能力包括静态限制区、DEM资产移交、有限准备位/充电端口、连续通信与中继、真实增配/压力情景、冻结任务分区、额定单点诊断、容量必要下界和部分新增事件。

仍部分实现：一般大规模联合搜索、完整实验设计、多情景风险优化、部分保障与可证明最小增配、异质状态分区、在途/落点/未来封控事件。未实现的P2保留在任务板：学习辅助搜索、实测能耗校准、ODM影像建图、SITL/真机、多基地与权限等。缺少真实数据/外部环境的研究不以占位按钮或模拟精度冒充完成。

## 6. 接口与待复核RFC

Solver纯Python JSON边界，不依赖FastAPI/SQLite。Schema生成Pydantic，实际OpenAPI生成HTTP TypeScript；禁止队友再手写第二套DTO。当前实际API43路径。Schema仍0.1.0-draft、proposed、approved_by为空，用户授权本分支实施，正式团队冻结未代签。

RFC-003至013记录限制区、DEM、地面资源、通信、分区、本机运维、单点诊断及新增事件/诊断。旧Scenario/Plan字段口径与退出事件保持；新增可选字段省略时仍可读取旧例。Event为严格联合，不混用drone_id、battery_id和component_id；新增需求必须同时有实际库存。正式合并前A/B共同核对所有RFC与Schema差异。

## 7. 测试与证据

最终完整验收仍在运行。已实际完成的新专项及失败历史分别记录于capacity-rfc011.json、demand-rfc012.json、relay-energy-rfc013.json和github-ci.json；路径均在evidence/verification。不得把专项累计数或旧检查点称为最终全套。

最新原始Python/契约/治理/lint/unit/build/E2E命令输出由scripts/verify.py保存check-01至07.txt，latest.json同时保存源码前后指纹。Windows与Linux的环境/用例范围分别说明；远端CI需要对应实际head_sha，不能继承旧提交的success。

## 8. 截图、去标识样例与原始输出

实际界面位于evidence/browser/verified，覆盖1440×900、1280×720和390宽屏。普通、联合及低SOC打印PDF需按最终生成文件逐页检查，不能只验证文本存在。

去个人标识且改变一箱输入的样例在submission/examples，含Scenario与来源记录；完整原始求解结果将保存在同目录solve-result.json并核对。它不是官方匿名合规证明。原研究材料含实名信息，仅供只读追溯，不直接作为匿名提交附件。

evidence/solver保存真实32/80箱、深入优化、联合通信、分区、额定诊断和事件前后完整JSON，不把历史论文的时间/能耗直接展示为新优化结果。演示稿与真实录像位于deliverables，来源hash和视觉检查记录分别在evidence/demo与evidence/video。

## 9. 模型与产品边界

运输与联合调度输出模型内FEASIBLE，有限候选池OPTIMAL不等于完整问题全局最优。UNKNOWN表示当前输入/预算未找到方案，不能改称严格无解。额定单点DP与冻结分区只在各自有界模型中完整求解；容量下界是运输架次必要条件，不能转成最少机体/电池数量。

DEM/限制区/无线覆盖均有声明的几何、尺度与输入边界；没有风雨、全程多机避碰、实地无线认证、遥测、真实飞控或起降坪约束。未知费率不输出人民币。压力情景不是成功概率或稳健最优证明。

## 10. 两人接手与合并

A重点复核物理/数值、必要下界、联合模式候选、独立检查、紧急需求全服务和所有算法证据；B同一人重点复核HTTP/生成类型、版本/幂等/预约、Worker恢复、三页交互、资产、启动/备份与导出。两人共同评审Schema/RFC、原始数据复用与赛事要求。

先评审本功能分支或待审PR，通过后由负责人合并。没有自动改写main。接手时各自clone；同步已接受的基线后分别创建feat/solver-next和feat/system-next，不共用同一工作目录或直接同时修改今晚分支。

每次工作先git status，干净基线用git pull --ff-only同步；按文件git add、commit、push到各自分支，再开PR。Git add记录暂存，commit保存本地版本，push同步远端，pull取回并快进已有提交。不要把pull当成上传，也不要用force push解决冲突。
