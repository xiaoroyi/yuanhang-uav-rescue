/** Build a self-contained offline HTML/PDF walkthrough from recorded project evidence. */
import fs from "node:fs/promises";
import path from "node:path";
import { createHash } from "node:crypto";
import { createRequire } from "node:module";
import { fileURLToPath, pathToFileURL } from "node:url";
import { spawnSync } from "node:child_process";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const output = path.join(root, "deliverables");
const qa = path.join(root, "evidence/demo");
process.env.PLAYWRIGHT_BROWSERS_PATH = path.join(root, ".local/ms-playwright");
const require = createRequire(path.join(root, "frontend/package.json"));
const { chromium } = require("@playwright/test");
const sources = new Map();
const read = async (name) => {
  const buffer = await fs.readFile(path.join(root, name));
  sources.set(name, createHash("sha256").update(buffer).digest("hex"));
  return buffer;
};
const json = async (name) => JSON.parse((await read(name)).toString("utf8"));
const escape = (text) =>
  String(text)
    .replaceAll("；", "。")
    .replace(
      /[&<>"']/g,
      (c) =>
        ({
          "&": "&amp;",
          "<": "&lt;",
          ">": "&gt;",
          '"': "&quot;",
          "'": "&#39;",
        })[c],
    );
const n = (value, digits = 2) =>
  value == null
    ? "未评估"
    : Number(value).toLocaleString("zh-CN", { maximumFractionDigits: digits });
const minutes = (value) => n(value / 60, 1) + " 分钟";
const picture = async (name, alt) =>
  `<img src="data:image/png;base64,${(await read("evidence/browser/verified/" + name + ".png")).toString("base64")}" alt="${escape(alt)}">`;
const table = (headers, rows) =>
  `<table><thead><tr>${headers.map((h) => `<th>${escape(h)}</th>`).join("")}</tr></thead><tbody>${rows.map((row) => `<tr>${row.map((cell) => `<td>${escape(cell)}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
const bullets = (items) =>
  items.map((item) => `<p class="body-copy">${escape(item)}</p>`).join("");
const slides = [];
const titles = [];
function slide(title, body, source, className = "") {
  titles.push(title);
  slides.push(
    `<section class="slide ${className}" aria-label="${escape(title)}"><header><h2>${escape(title)}</h2></header><div class="content">${body}</div><footer><span>${escape(source)}</span><b>${String(slides.length + 1).padStart(2, "0")}</b></footer></section>`,
  );
}

const nominal = (await json("evidence/solver/nominal-contest.json")).report;
const compact = (await json("evidence/solver/nominal-compact.json")).snapshot
  .scenario;
const jointRun = await json("evidence/solver/joint-contest-recomputed.json");
const joint = jointRun.outcome.plan;
const partition = await json("evidence/solver/frozen-partition-contest.json");
const battery = await json("evidence/solver/battery-replan.json");
const urgent = await json("evidence/browser/urgent-demand.json");
const capacityCompact = (await json("evidence/solver/capacity-compact.json"))
  .report;
const capacityContest = (await json("evidence/solver/capacity-contest.json"))
  .report;
const verification = await json("evidence/verification/latest.json");
const checkOutput = (await read("evidence/verification/check-01.txt")).toString(
  "utf8",
);
const browserResult = await json("evidence/browser/e2e-results.json");
const pythonTests =
  [...checkOutput.matchAll(/(\d+) passed(?:,| in)/g)].at(-1)?.[1] || "见记录";
const subtests = checkOutput.match(/(\d+) subtests passed/)?.[1] || "0";
const python = path.join(
  root,
  process.platform === "win32"
    ? ".venv/Scripts/python.exe"
    : ".venv/bin/python",
);
const identity = spawnSync(
  python,
  [
    "-c",
    'import json; from pathlib import Path; from shared.build_info import verification_fingerprint; print(json.dumps({"verification_source":verification_fingerprint(Path.cwd())}))',
  ],
  { cwd: root, encoding: "utf8", windowsHide: true },
);
if (identity.status !== 0)
  throw new Error(identity.stderr || "Cannot read source identity.");
const sourceIdentity = JSON.parse(identity.stdout).verification_source;
const sameVerifiedSource =
  verification.passed &&
  verification.verification_source_after_sha256 === sourceIdentity;
if (process.argv.includes("--require-verified") && !sameVerifiedSource) {
  throw new Error(
    "Current source does not match a passed full verification. Run scripts/verify.py --browser first.",
  );
}
const dateFormatter = new Intl.DateTimeFormat("zh-CN", {
  timeZone: "Asia/Shanghai",
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
});
const date = dateFormatter.format(new Date());
const checkDate = dateFormatter.format(new Date(verification.at_utc));

slide(
  "援航",
  `<div class="cover-copy"><div class="cover-brand">援航</div><h1>无人机运输与<br>通信协同调度</h1><p>根据需求、地形与机队状态，生成可追溯的救援运输计划。</p><div class="cover-meta">本机离线演示版本　${escape(date)}</div></div>`,
  "规划辅助系统，输出仅在声明模型范围内有效",
  "cover",
);

slide(
  "场景与实体数据",
  `<div class="two-col"><div>${bullets(["需求数量与逐箱库存分开维护。每架机体、每块电池都有独立身份。", "默认采用题设的较小子集，便于演示故障、改派与历史恢复。", "JSON、CSV、XLSX可预览导入，保存后形成新版本。"])}</div><div>${table(
    ["默认演练", "实际数量"],
    [
      ["需求点", `${compact.sites.length} 处`],
      ["物资箱件", `${compact.cargo_items.length} 箱`],
      ["运输机", `${compact.drones.length} 架`],
      ["运输电池", `${compact.batteries.length} 块`],
      ["原题完整入口", "15 点、80 箱"],
    ],
  )}</div></div>`,
  "数据来源：题设适配器与 nominal-compact.json 的完整Snapshot",
);

slide(
  "真实调度工作台",
  `<div class="image-copy"><div>${bullets(["点击架次，地图、箱件明细与资源时间轴同步定位。", "时间与能耗策略分别真实计算。", "只有通过独立检查的方案，才能进入确认与规划资源预约。"])}</div>${await picture("workspace-1440", "真实调度工作台，运输路线与资源时间轴")}</div>`,
  "实际界面截图：workspace-1440.png；计划回放为示意，不写入交付事实",
);

slide(
  "电池与地面资源",
  `<div class="image-copy"><div>${bullets(["机体与电池分别占用资源。", "可限制准备工位和充电端口，等待与充电分开记录。", "初始低SOC先补满再调度，返航后按两阶段模型补能。"])}</div>${await picture("ground-timeline-expanded-1440", "有限准备工位和充电端口的真实资源时间轴")}</div>`,
  "实际演练：有限地面容量；起降坪容量尚未建模",
);

const oldBattery = new Map(
  battery.old_plan.sorties.flatMap((r) =>
    r.cargo_ids.map((cid) => [cid, r.battery_id]),
  ),
);
const batteryChanges = battery.plan.sorties.reduce(
  (count, r) =>
    count +
    r.cargo_ids.filter((cid) => oldBattery.get(cid) !== r.battery_id).length,
  0,
);
slide(
  "资源退出后的真实改派",
  `<div class="image-copy"><div><div class="big-number">${batteryChanges}<small>箱更换电池分配</small></div>${bullets([`退出 ${battery.event.payload.battery_id} 后，新计划绑定新版本，原方案与输入保留。`, "支持运输机、中继机、运输电池和中继能源组件退出。", "局部修复需要重新检查；不适用时在剩余预算内全量重算。"])}</div>${await picture("battery-fault-changes-1280", "运输电池退出后的真实改派统计和新时间轴")}</div>`,
  "来源：battery-replan.json；仅适用整个场景尚未执行的状态，不证明最小改动",
);

const sensitivity = nominal.sensitivity.filter((row) =>
  [0.2, 0.3].includes(row.min_return_soc),
);
slide(
  "紧急需求与实物库存一起插入",
  `<div class="image-copy"><div><div class="big-number">${new Set(urgent.plan.sorties.flatMap((r) => r.cargo_ids)).size}<small>箱重新完整排程</small></div>${bullets([`新增${urgent.event.payload.demand.required_quantity}箱需求，同时登记等量基地库存。`, "形成新版本与快照，全量重算，保留旧记录。", "零秒硬截止未发布新方案，旧版确认禁用。"])}</div>${await picture("urgent-demand-result-1440", "紧急新增物资后的真实全量重规划")}</div>`,
  "来源：urgent-demand.json；仅限未执行场景和已有点位，新增箱件不计为旧箱件改派",
);
slide(
  "单点额定运输诊断",
  `<p class="intro">额定满电、100%SOH的单点组批，比较组批方法与返航余量。</p>${table(["方法 / 参数", "架次", "运输能耗"], [["单箱直送", nominal.single_box_baseline.sortie_count, `${n(nominal.single_box_baseline.energy_kwh)} kWh`], ["确定性贪心组批", nominal.greedy_baseline.sortie_count, `${n(nominal.greedy_baseline.energy_kwh)} kWh`], ["计数DP，20%返航余量", nominal.metrics.sortie_count, `${n(nominal.metrics.energy_kwh)} kWh`], ...sensitivity.filter((row) => row.min_return_soc === 0.3).map((row) => ["计数DP，30%返航余量", row.metrics.sortie_count, `${n(row.metrics.energy_kwh)} kWh`])])}<p class="scope">每站最多512个计数状态，按架次、能耗、累计作业时长排序。<br>忽略实体数量、充电、时限与通信，须另行正式求解。</p>`,
  "同一80箱输入与额定模型，来源：nominal-contest.json；累计作业时间不等于机队完成时间",
);

slide(
  "地形与静态限制区",
  `<div class="image-copy"><div>${bullets(["本地GeoTIFF可注册、绑定并随完整资产包移交。", "限制区绕行后，距离、净空、飞行时间和能耗同步重算。", "覆盖外、NoData或缺少强制地形时，明确保留未评估状态。"])}</div>${await picture("zone-detour-1440", "静态限制区及当前输入下真实重算的绕行路线")}</div>`,
  "实际界面截图：zone-detour-1440.png；有限静态几何模型，不含气象与空管认证",
);

slide(
  "运输与通信联合保障",
  `<div class="image-copy"><div>${bullets(["直接链路与中继两跳链路共同保障运输活动。", "中继机、能源组件、服务窗口和地面容量一起排程。", "独立重建链路、能耗与资源占用，运输能耗与联合能耗分开统计。"])}</div>${await picture("joint-resource-windows-1440", "较小场景的运输、中继能源组件与通信服务窗口")}</div>`,
  "截图为较小演练；连续覆盖限于声明的投影DEM与无线模型，不是现场无线认证",
);

slide(
  "原题80箱联合实例",
  `<div class="two-col"><div><div class="big-number">80<small>箱完整保障</small></div>${bullets(["历史分组和高地驻点只作候选。", "当前物理、时刻、资源与连续覆盖全部重新计算。", "有限候选未证明全局最优。"])}</div><div>${table(
    ["本次记录", "结果"],
    [
      [
        "运输 / 中继架次",
        `${joint.sorties.length} / ${joint.relay_sorties.length}`,
      ],
      ["最后全部返航", minutes(joint.joint_metrics.joint_makespan_s)],
      ["运输能耗", `${n(joint.metrics.energy_kwh, 3)} kWh`],
      ["联合能耗", `${n(joint.joint_metrics.joint_energy_kwh, 3)} kWh`],
      ["模型内通信缺口", `${n(joint.communication_report.coverage_gap_s)} 秒`],
      ["预算 / 实际耗时", `60 / ${n(jointRun.outcome.runtime_s, 2)} 秒`],
    ],
  )}</div></div>`,
  "独立运行记录：joint-contest-recomputed.json；不是上一页较小演练的统计",
);

slide(
  "冻结任务分区",
  `<div class="image-copy"><div><div class="big-number">${partition.atoms.length}<small>个不可拆分连通单元</small></div>${bullets(["继承同一联合方案的任务、时刻和实际通信关系。", "完整枚举合法的2组或3组划分，比较专用资源与工作量。", "峰值见证、实体分配与库存缺口均可导出复核。"])}</div>${await picture("frozen-partition-1440", "联合方案冻结分区、专用资源与库存缺口")}</div>`,
  "同质满SOC/零时刻条件，最多10单元；冻结配置缺口不等于重新调度时的最少增配",
);

slide(
  "运输架次的容量必要下界",
  `<p class="intro">按可用库存与可用机型，分别计算质量、体积必要条件。</p>${table(
    ["输入", "最小质量", "最小体积", "质量下界", "体积下界", "合并下界"],
    [
      [
        "默认32箱",
        `${n(capacityCompact.mass_min_kg)} kg`,
        `${n(capacityCompact.volume_min_l)} L`,
        capacityCompact.mass_bound,
        capacityCompact.volume_bound,
        capacityCompact.sortie_lower_bound,
      ],
      [
        "原题80箱",
        `${n(capacityContest.mass_min_kg)} kg`,
        `${n(capacityContest.volume_min_l)} L`,
        capacityContest.mass_bound,
        capacityContest.volume_bound,
        capacityContest.sortie_lower_bound,
      ],
    ],
  )}<p class="scope">完整服务运输架次数的必要下界，不是最少机体或电池数量。<br>忽略路径、能耗、时限、整箱组合、充电与通信。<br>达到下界也不证明完整调度最优，精确比值与箱件见证可导出复核。</p>`,
  "来源：capacity-compact.json / capacity-contest.json；各自绑定输入hash，见RFC-011",
);

slide(
  "资源情景与压力对照",
  `<div class="image-copy"><div>${bullets(["增机、增电池与参数试算建立独立输入和真实计算任务。", "可查看资源占用、充电峰值与硬截止余量。", "运输倍率和三档压力是确定性情景，不输出成功概率或未经证明的稳健最优结论。"])}</div>${await picture("resource-analysis-1440", "真实计划的资源占用与独立试算入口")}</div>`,
  "界面示例来源：resource-analysis-1440.png；中继参数沿用情景原配置",
);

slide(
  "验证记录与模型边界",
  `<div class="two-col"><div><h3>${sameVerifiedSource ? "当前源码完整验收" : "最近完整验收检查点"}</h3><div class="test-count"><b>${escape(pythonTests)}</b><span>项Python测试<br>${escape(subtests)} 项子测试</span></div><div class="test-count"><b>${browserResult.stats.expected}</b><span>条浏览器流程<br>unexpected ${browserResult.stats.unexpected}</span></div><p class="small">检查日期：${escape(checkDate)}<br>完整记录：evidence/verification/latest.json</p></div><div>${bullets(["独立检查覆盖箱件、实体、载重、时限、能耗、充电及启用的空间与通信约束。", "执行中重规划、风雨、多机避碰与现场无线认证尚未支持。", "AI训练、自动建图与真机仿真需要额外数据或环境。", sameVerifiedSource ? "测试前后源码指纹一致，记录匹配当前源码。" : "当前源码待全套复验，已有专项证据。"])}</div></div>`,
  "完整验收与专项范围分别记录，不将UNKNOWN当无解，不把有限最优当现实全局最优",
);

slide(
  "本机演示操作",
  `<div class="operation"><div class="launch">双击 start.cmd<strong>http://127.0.0.1:8000/</strong><span>已准备依赖与构建的本机可离线运行，无需登录。</span></div><ol><li>新建演练，计算方案，点击架次和电池时间轴。</li><li>比较策略，检查后确认，导出计划与报告。</li><li>模拟资源退出，查看新版本和改派结果。</li><li>刷新恢复历史，查看通信和分区分析。</li></ol></div>`,
  "首次新电脑安装按README；数据保存在runtime，备份/恢复见LOCAL_OPERATIONS",
);

await fs.mkdir(output, { recursive: true });
await fs.mkdir(qa, { recursive: true });
const html = `<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>援航 · 系统演示</title><style>
*{box-sizing:border-box}html,body{margin:0;font-family:"Microsoft YaHei","Noto Sans SC",sans-serif;color:#183c38}body{background:#e8efec;overflow:hidden}.deck{width:1280px;height:720px;transform-origin:top left;position:absolute}.slide{width:1280px;height:720px;background:#fff;padding:52px 64px 28px;display:none;flex-direction:column;overflow:hidden}.slide.active{display:flex}header{flex-shrink:0}h2{font-size:46px;font-weight:650;line-height:1.25;margin:0 0 28px;letter-spacing:-1px}.content{flex:1;min-height:0}.two-col{display:grid;grid-template-columns:1fr 1.1fr;gap:68px;height:100%;align-items:center}.body-copy{text-wrap:balance;font-size:24px;line-height:1.75;margin:0 0 24px}.image-copy{height:100%;display:grid;grid-template-columns:318px minmax(0,1fr);gap:36px;align-items:center}.image-copy .body-copy{font-size:23px;line-height:1.7;margin-bottom:22px}img{max-width:100%;max-height:488px;width:100%;object-fit:contain;display:block}footer{display:flex;align-items:flex-end;gap:18px;justify-content:space-between;min-height:44px;padding-top:10px;color:#687d77;font-size:14px;line-height:1.5}footer b{font-size:17px;color:#0d8378;flex-shrink:0}table{border-collapse:collapse;width:100%;font-size:24px;line-height:1.5}th{text-align:left;color:#0d8378;font-size:21px;font-weight:600;border-bottom:2px solid #14897c;padding:16px 10px}td{padding:18px 10px;border-bottom:1px solid #dae7e1}td:first-child{font-weight:500}td:last-child{font-variant-numeric:tabular-nums}.intro{font-size:25px;line-height:1.6;margin:0 0 8px}.scope{font-size:21px;line-height:1.65;color:#637a72;margin:22px 0 0}.big-number{font-size:78px;font-weight:650;color:#078578;line-height:1.1;margin:0 0 30px}.big-number small{display:block;font-size:22px;font-weight:400;margin-top:14px;line-height:1.5;color:#486c61}.cover{background:#0b746a;color:white}.cover header{display:none}.cover .content{display:flex;align-items:center}.cover-brand{font-size:34px;font-weight:600;letter-spacing:6px;margin-bottom:40px}.cover h1{font-size:69px;line-height:1.3;font-weight:600;letter-spacing:1px;margin:0 0 26px}.cover p{font-size:25px;line-height:1.8;max-width:990px;color:#d8eeea;margin:0}.cover-meta{font-size:19px;letter-spacing:2px;margin-top:46px;color:#c0e1da}.cover footer{color:#b8dad3}.cover footer b{color:#c8e7e0}h3{font-size:26px;font-weight:600;margin:0 0 25px}.test-count{display:flex;gap:30px;align-items:center;margin-bottom:30px}.test-count>b{font-size:72px;line-height:1.1;color:#078578;font-weight:650}.test-count>span{font-size:23px;line-height:1.6}.small{font-size:17px;line-height:1.8;color:#6e837b}.operation{display:grid;grid-template-columns:1fr 1.1fr;gap:65px;height:100%;align-items:center}.launch{font-size:29px;line-height:1.6}.launch strong{display:block;color:#078578;font-size:32px;font-weight:600;margin:22px 0;overflow-wrap:anywhere}.launch span{display:block;font-size:23px;color:#647b73}.operation ol{margin:0;padding-left:30px;font-size:24px;line-height:1.8}.operation li{padding-left:8px;margin-bottom:23px}.toolbar{position:fixed;bottom:8px;left:50%;transform:translateX(-50%);height:32px;display:flex;gap:14px;align-items:center;font-size:13px;color:#385c52}.toolbar button{border:1px solid #c2d3cb;background:#fff;border-radius:6px;padding:6px 14px;color:inherit;cursor:pointer}.toolbar button:focus-visible{outline:3px solid #0d8378}.toolbar span{white-space:nowrap}
@page{size:1280px 720px;margin:0}@media print{html,body{background:white;overflow:visible}.deck{position:static!important;transform:none!important;width:1280px;height:auto;margin:0!important;top:0!important;left:0!important}.slide{display:flex!important;break-after:page;page-break-after:always}.slide:last-child{break-after:auto;page-break-after:auto}.toolbar{display:none!important}}
</style></head><body><main class="deck" aria-label="援航系统演示">${slides.join("")}</main><nav class="toolbar" aria-label="幻灯片导航"><button id="previous" aria-label="上一页">上一页</button><span id="counter" aria-live="polite"></span><button id="next" aria-label="下一页">下一页</button><button id="print">保存PDF</button></nav><script>
const pages=Array.from(document.querySelectorAll('.slide'));let current=0;function show(i){current=Math.max(0,Math.min(pages.length-1,i));pages.forEach((p,j)=>p.classList.toggle('active',j===current));document.getElementById('counter').textContent=(current+1)+' / '+pages.length;document.title='援航 · '+pages[current].getAttribute('aria-label')}function fit(){const scale=Math.min(innerWidth/1280,Math.max(100,innerHeight-48)/720);const deck=document.querySelector('.deck');deck.style.transform='scale('+scale+')';deck.style.left=((innerWidth-1280*scale)/2)+'px';deck.style.top=Math.max(0,(innerHeight-48-720*scale)/2)+'px'}document.getElementById('previous').onclick=()=>show(current-1);document.getElementById('next').onclick=()=>show(current+1);document.getElementById('print').onclick=()=>window.print();addEventListener('keydown',e=>{if(['ArrowRight','PageDown',' '].includes(e.key)){e.preventDefault();show(current+1)}if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();show(current-1)}if(e.key==='Home')show(0);if(e.key==='End')show(pages.length-1)});addEventListener('resize',fit);window.showDemoSlide=show;show(0);fit();
</script></body></html>`;
const htmlPath = path.join(output, "yuanhang-demo.html");
await fs.writeFile(htmlPath, html);
const browser = await chromium.launch({
  headless: true,
  env: {
    ...process.env,
    PLAYWRIGHT_BROWSERS_PATH: path.join(root, ".local/ms-playwright"),
  },
});
const errors = [],
  network = [];
const context = await browser.newContext({
  viewport: { width: 1280, height: 768 },
});
await context.route(/^https?:\/\//, (route) => {
  network.push(route.request().url());
  return route.abort();
});
const page = await context.newPage();
page.on("pageerror", (e) => errors.push(e.message));
await page.goto(pathToFileURL(htmlPath).href);
await page.evaluate(() => document.fonts.ready);
const layout = [];
for (let index = 0; index < slides.length; index++) {
  await page.evaluate((i) => window.showDemoSlide(i), index);
  const slideElement = page.locator(".slide.active");
  const issues = await slideElement.evaluate((node) => {
    const content = node.querySelector(".content"),
      footer = node.querySelector("footer");
    const result = [];
    if (content.scrollHeight > content.clientHeight + 2)
      result.push("content overflow");
    if (footer.scrollWidth > footer.clientWidth + 2)
      result.push("footer overflow");
    return result;
  });
  if (issues.length)
    throw new Error(`Slide ${index + 1}: ${issues.join(", ")}`);
  const name = `slide-${String(index + 1).padStart(2, "0")}.png`;
  await slideElement.screenshot({ path: path.join(qa, name) });
  layout.push({
    slide: index + 1,
    title: titles[index],
    image: `evidence/demo/${name}`,
    issues,
  });
}
await page.keyboard.press("Home");
await page.keyboard.press("ArrowRight");
if (
  (await page.locator(".slide.active").getAttribute("aria-label")) !== titles[1]
)
  throw new Error("Next-slide keyboard navigation failed.");
await page.keyboard.press("End");
if (
  (await page.locator(".slide.active").getAttribute("aria-label")) !==
  titles.at(-1)
)
  throw new Error("End navigation failed.");
await page.keyboard.press("Home");
if (
  (await page.locator(".slide.active").getAttribute("aria-label")) !== titles[0]
)
  throw new Error("Home navigation failed.");
await page.emulateMedia({ media: "print" });
await page.pdf({
  path: path.join(output, "yuanhang-demo.pdf"),
  printBackground: true,
  preferCSSPageSize: true,
});
await browser.close();
if (errors.length || network.length)
  throw new Error("Offline deck had page errors or network requests.");
const manifest = {
  generated_at_utc: new Date().toISOString(),
  slide_count: slides.length,
  source_files: Object.fromEntries(sources),
  verification_source_at_build: sourceIdentity,
  last_full_verification_source: verification.verification_source_after_sha256,
  full_verification_matches_current_source: sameVerifiedSource,
  page_errors: errors,
  network_requests: network,
  keyboard_navigation: "Home, ArrowRight and End checked",
  slides: layout,
  note: "HTML and PDF walkthrough from recorded evidence, not a PPTX or official contest submission template. Individual visual inspection remains required.",
};
await fs.writeFile(
  path.join(qa, "manifest.json"),
  JSON.stringify(manifest, null, 2) + "\n",
);
console.log(
  JSON.stringify({
    slides: slides.length,
    html: "deliverables/yuanhang-demo.html",
    pdf: "deliverables/yuanhang-demo.pdf",
    current_source_fully_verified: sameVerifiedSource,
  }),
);
