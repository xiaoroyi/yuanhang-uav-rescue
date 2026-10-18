/** Record a real offline production workflow in a separate, retained runtime. */
import fs from "node:fs/promises";
import path from "node:path";
import { createHash, randomUUID } from "node:crypto";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import { spawn, spawnSync } from "node:child_process";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
process.env.PLAYWRIGHT_BROWSERS_PATH = path.join(root, ".local/ms-playwright");
const require = createRequire(path.join(root, "frontend/package.json"));
const { chromium, expect } = require("@playwright/test");
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
    "import json; from shared.build_info import service_fingerprint,verification_fingerprint; from scripts.launch import current_frontend; from pathlib import Path; print(json.dumps(dict(service=service_fingerprint(Path.cwd()),source=verification_fingerprint(Path.cwd()),frontend_current=bool(current_frontend()))))",
  ],
  { cwd: root, encoding: "utf8", windowsHide: true },
);
if (identity.status !== 0) throw new Error(identity.stderr || identity.stdout);
const expected = JSON.parse(identity.stdout);
if (!expected.frontend_current)
  throw new Error(
    "Build the current frontend before recording: npm --prefix frontend run build",
  );
const verification = JSON.parse(
  await fs.readFile(
    path.join(root, "evidence/verification/latest.json"),
    "utf8",
  ),
);
const sourceVerified =
  verification.passed &&
  verification.verification_source_after_sha256 === expected.source;
if (process.argv.includes("--require-verified") && !sourceVerified)
  throw new Error(
    "Current source has not passed the full verification checkpoint.",
  );

const runId = randomUUID();
const runtime = path.join(root, ".local/video-runtime", runId);
const capture = path.join(root, ".local/video-capture", runId);
const output = path.join(root, "deliverables");
const evidence = path.join(root, "evidence/video");
await Promise.all([
  fs.mkdir(runtime, { recursive: true }),
  fs.mkdir(capture, { recursive: true }),
  fs.mkdir(output, { recursive: true }),
  fs.mkdir(evidence, { recursive: true }),
]);
const origin = "http://127.0.0.1:8021";
try {
  await fetch(origin, { signal: AbortSignal.timeout(500) });
  throw new Error(
    "Port 8021 is already occupied; no existing service was stopped.",
  );
} catch (error) {
  if (error.message.includes("already occupied")) throw error;
}
const env = {
  ...process.env,
  YUANHANG_RUNTIME: runtime,
  PYTHONIOENCODING: "utf-8",
  NO_PROXY: "127.0.0.1,localhost,::1",
  no_proxy: "127.0.0.1,localhost,::1",
};
delete env.NODE_TLS_REJECT_UNAUTHORIZED;
const service = spawn(
  python,
  [
    "-m",
    "uvicorn",
    "backend.app.main:app",
    "--host",
    "127.0.0.1",
    "--port",
    "8021",
    "--log-level",
    "warning",
    "--no-access-log",
  ],
  { cwd: root, env, windowsHide: true, stdio: ["ignore", "pipe", "pipe"] },
);
let serviceOutput = "";
for (const stream of [service.stdout, service.stderr])
  stream.on("data", (data) => {
    serviceOutput = (serviceOutput + data.toString()).slice(-12000);
  });
let browser, context, page;
const errors = [],
  external = [],
  chapters = [];
let started,
  health,
  scene,
  original,
  originalSnapshot,
  plan,
  finalSnapshot,
  events,
  analysis,
  video;
const pause = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const chapter = async (title, text, hold = 3500) => {
  chapters.push({
    start_s: Math.round((performance.now() - started) / 10) / 100,
    title,
    text,
  });
  console.log(title);
  await pause(hold);
};
const get = async (route) => {
  const response = await context.request.get(origin + "/api/v1" + route);
  if (!response.ok())
    throw new Error(
      `HTTP ${response.status()} ${route}: ${await response.text()}`,
    );
  return response.json();
};
const solve = async () => {
  await page.getByRole("button", { name: /^(生成真实方案|重新求解)$/ }).click();
  await expect(page.locator(".job-banner")).toBeVisible();
  await expect(page.locator(".job-banner")).toBeHidden({ timeout: 60000 });
  await expect(page.getByTestId("sortie-card").first()).toBeVisible();
};
try {
  for (let i = 0; i < 100; i++) {
    if (service.exitCode !== null) throw new Error(serviceOutput);
    try {
      const response = await fetch(origin + "/api/v1/health", {
        signal: AbortSignal.timeout(500),
      });
      if (response.ok) {
        health = await response.json();
        break;
      }
    } catch (error) {
      if (i === 10)
        console.log("Recording readiness:", error.cause?.code || error.message);
    }
    await pause(200);
  }
  if (!health || health.service_source_sha256 !== expected.service)
    throw new Error(
      "Recording service did not become ready with the current source: " +
        JSON.stringify({
          expected: expected.service,
          observed: health?.service_source_sha256,
          service_output: serviceOutput,
        }),
    );
  browser = await chromium.launch({
    args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"],
  });
  context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    recordVideo: { dir: capture, size: { width: 1440, height: 900 } },
    acceptDownloads: true,
  });
  await context.route("**/*", async (route) => {
    const url = new URL(route.request().url());
    if (
      ["http:", "https:"].includes(url.protocol) &&
      !["127.0.0.1", "localhost", "[::1]"].includes(url.hostname)
    ) {
      external.push(url.origin);
      await route.abort("internetdisconnected");
    } else await route.continue();
  });
  const created = await context.request.post(
    origin + "/api/v1/scenarios/examples",
    { data: { example: "compact" } },
  );
  if (created.status() !== 201) throw new Error(await created.text());
  scene = await created.json();
  scene.name = "离线操作录像 · 32箱动态调度";
  const renamed = await context.request.put(
    origin + `/api/v1/scenarios/${scene.scenario_id}`,
    { data: { expected_state_version: 1, scenario: scene } },
  );
  if (!renamed.ok()) throw new Error(await renamed.text());
  scene = await renamed.json();
  await context.addInitScript(
    (id) => localStorage.setItem("yuanhang-scenario", id),
    scene.scenario_id,
  );
  page = await context.newPage();
  video = page.video();
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(message.text());
  });
  started = performance.now();
  await page.goto(origin);
  await expect(
    page.getByRole("button", { name: "生成真实方案", exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "场景与资源", exact: true }).click();
  await chapter(
    "01 查看真实输入",
    "默认5个需求点、32箱物资，需求与逐箱库存、机体和电池分别维护。",
  );
  await page.getByRole("button", { name: "调度工作台", exact: true }).click();
  await chapter(
    "02 开始真实求解",
    "下面保留实际等待时间，后端独立Worker调用Python算法。",
    1000,
  );
  await solve();
  original = await get(
    "/plans/" + (await get(`/scenarios/${scene.scenario_id}/plans`))[0].plan_id,
  );
  originalSnapshot = await get("/snapshots/" + original.snapshot_id);
  await chapter(
    "03 地图与架次联动",
    "地图航线、任务卡与资源甘特来自同一真实Plan，点击架次定位相关资源。",
  );
  await page.getByTestId("sortie-card").nth(1).click();
  await expect(page.locator(".timeline-bar.is-selected").first()).toBeVisible();
  await pause(2500);
  await page
    .locator(".timeline-panel")
    .getByRole("button", { name: "电池", exact: true })
    .click();
  await page.getByTitle("展开时间轴", { exact: true }).click();
  await chapter(
    "04 电池与补能窗口",
    "电池占用、返航后补能和释放时间独立于机体，时间轴可展开查看。",
    5000,
  );
  await page.getByTitle("收起", { exact: true }).click();
  await page.getByRole("button", { name: "播放计划回放", exact: true }).click();
  await chapter(
    "05 计划示意回放",
    "播放按计算航线和时间运行，仅为计划示意，不写入真实飞行或交付事实。",
    6000,
  );
  await page.getByRole("button", { name: "暂停计划回放", exact: true }).click();
  await chapter(
    "06 同快照策略比较",
    "计算另一策略并保留原结果，公平比较绑定同一不可变快照。",
    1000,
  );
  await page
    .getByRole("button", { name: "真实计算此策略", exact: true })
    .click();
  await expect(page.locator(".job-banner")).toBeVisible();
  await expect(page.locator(".job-banner")).toBeHidden({ timeout: 60000 });
  await expect(page.locator(".strategy-metrics")).toHaveCount(2);
  const summaries = await get(`/scenarios/${scene.scenario_id}/plans`);
  if (summaries[0].snapshot_id !== original.snapshot_id)
    throw new Error("Compared strategies are not bound to the same snapshot.");
  await pause(4000);
  await page.getByRole("button", { name: "检查报告", exact: true }).click();
  await expect(page.getByRole("dialog")).toContainText("声明范围内检查通过");
  await chapter(
    "07 独立检查与确认",
    "重新检查物理、资源、需求和时限；确认只作规划审核，不下发飞控。",
    4000,
  );
  await page
    .getByRole("dialog")
    .getByRole("button", { name: "关闭弹窗" })
    .click();
  const confirmationResponse = page.waitForResponse(
    (response) =>
      /\/plans\/[^/]+\/confirm$/.test(response.url()) &&
      response.request().method() === "POST",
  );
  await page.getByRole("button", { name: "确认方案", exact: true }).click();
  const confirmation = await (await confirmationResponse).json();
  await expect(
    page.locator(".toast").filter({ hasText: "方案已确认" }),
  ).toBeVisible();
  const baseline = await get("/plans/" + confirmation.plan_id);
  const failed = baseline.sorties[0].battery_id;
  await page.getByRole("button", { name: "事件复盘", exact: true }).click();
  await page.getByLabel("故障事件类型").selectOption("battery");
  await page.getByLabel("故障运输电池").selectOption(failed);
  await chapter(
    "08 运输电池退出",
    `将尚未执行场景中的运输电池${failed}设为不可用，生成新版本并真实重规划。`,
    4000,
  );
  await page
    .getByRole("button", { name: "记录故障并重规划", exact: true })
    .click();
  await expect(page.locator(".job-banner")).toBeVisible();
  await expect(page.locator(".job-banner")).toBeHidden({ timeout: 60000 });
  await expect(page.locator(".comparison-cards")).toContainText("电池改派箱件");
  plan = await get(
    "/plans/" + (await get(`/scenarios/${scene.scenario_id}/plans`))[0].plan_id,
  );
  if (
    plan.parent_plan_id !== baseline.plan_id ||
    plan.validation.status !== "passed" ||
    plan.sorties.some((s) => s.battery_id === failed)
  )
    throw new Error(
      "Battery replan did not pass the real identity/resource checks.",
    );
  if (
    JSON.stringify(await get("/plans/" + original.plan_id)) !==
    JSON.stringify(original)
  )
    throw new Error("Original plan was modified.");
  finalSnapshot = await get("/snapshots/" + plan.snapshot_id);
  events = await get(`/scenarios/${scene.scenario_id}/events`);
  await chapter(
    "09 新旧方案对照",
    "原方案保留，新方案绑定新版本，列出时间变化、路线变化及机体/电池改派。",
    4500,
  );
  await page.locator(".comparison-cards").scrollIntoViewIfNeeded();
  await pause(3000);
  await page
    .getByRole("button", { name: "资源分析与试算", exact: true })
    .click();
  await expect(page.getByTestId("capacity-sortie-lower-bound")).toBeVisible();
  await page
    .getByRole("region", { name: "运输架次容量下界" })
    .locator("summary")
    .click();
  await page
    .getByRole("region", { name: "运输架次容量下界" })
    .scrollIntoViewIfNeeded();
  analysis = await get(`/plans/${plan.plan_id}/analysis`);
  await chapter(
    "10 查看资源依据",
    "资源占用和截止余量绑定原Snapshot；容量下界不是最少机队数量或完整调度最优值。",
    5500,
  );
  const downloadResponse = page.waitForEvent("download");
  await page.getByRole("button", { name: "导出分析JSON", exact: true }).click();
  const download = await downloadResponse;
  const analysisFile = path.join(output, "walkthrough-analysis.json");
  await download.saveAs(analysisFile);
  const exported = JSON.parse(await fs.readFile(analysisFile, "utf8"));
  if (
    exported.analysis.plan_id !== plan.plan_id ||
    exported.analysis.capacity_bound.snapshot_content_hash !==
      finalSnapshot.content_hash
  )
    throw new Error("Downloaded analysis was not bound to the final plan.");
  await chapter(
    "11 导出与可追溯记录",
    "导出的JSON保留完整分析、快照hash、数值比值与逐箱见证，原始方案和事件均可恢复。",
    3500,
  );
  await page.getByRole("button", { name: "调度工作台", exact: true }).click();
  await expect(page.getByTestId("sortie-card").first()).toBeVisible();
  await chapter(
    "12 本机离线闭环完成",
    "输入 → 算法 → 检查 → 确认 → 事件 → 重规划 → 分析导出。本次浏览器阻止所有外部HTTP(S)请求。",
    6000,
  );
  await page.screenshot({ path: path.join(output, "walkthrough-poster.png") });
  const end_s = Math.round((performance.now() - started) / 10) / 100;
  if (errors.length || external.length)
    throw new Error(JSON.stringify({ errors, external }));
  const finalIdentity = spawnSync(
    python,
    [
      "-c",
      "from shared.build_info import verification_fingerprint; from pathlib import Path; print(verification_fingerprint(Path.cwd()))",
    ],
    { cwd: root, encoding: "utf8", windowsHide: true },
  );
  if (
    finalIdentity.status !== 0 ||
    finalIdentity.stdout.trim() !== expected.source
  )
    throw new Error(
      "Source changed during recording; keep the source fixed and record again.",
    );
  await context.close();
  context = null;
  await video.saveAs(path.join(output, "yuanhang-walkthrough.webm"));
  const videoHash = createHash("sha256")
    .update(await fs.readFile(path.join(output, "yuanhang-walkthrough.webm")))
    .digest("hex");
  const stamp = (seconds) => {
    const ms = Math.round(seconds * 1000);
    return `${String(Math.floor(ms / 3600000)).padStart(2, "0")}:${String(Math.floor(ms / 60000) % 60).padStart(2, "0")}:${String(Math.floor(ms / 1000) % 60).padStart(2, "0")}.${String(ms % 1000).padStart(3, "0")}`;
  };
  const vtt =
    "WEBVTT\n\n" +
    chapters
      .map(
        (item, i) =>
          `${i + 1}\n${stamp(item.start_s)} --> ${stamp(chapters[i + 1]?.start_s ?? end_s)}\n${item.title}\n${item.text}\n`,
      )
      .join("\n");
  await fs.writeFile(path.join(output, "yuanhang-walkthrough.zh.vtt"), vtt);
  const safe = (value) => JSON.stringify(value).replaceAll("<", "\\u003c");
  const html = `<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>援航 · 真实离线操作录像</title><style>body{margin:0;background:#f2f7f5;color:#173f38;font:16px/1.65 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1200px;margin:36px auto;padding:0 20px}h1{font-size:28px;margin-bottom:8px}p{color:#55776d}video::cue{font:22px/1.4 "Microsoft YaHei",sans-serif;background:#173f38e6}video{width:100%;background:#fff;border-radius:12px;box-shadow:0 8px 30px #173f3815}nav{display:flex;gap:8px;flex-wrap:wrap;margin:20px 0}button{font:inherit;font-size:14px;padding:7px 12px;border:1px solid #d0e2db;background:white;color:#176e5d;border-radius:8px;cursor:pointer}small{color:#647f76}</style><main><h1>援航 · 真实离线操作录像</h1><p>自动操作真实生产构建，保留计算等待时间。无旁白，附中文字幕与章节。模型内规划辅助，不是实飞记录。</p><video controls poster="walkthrough-poster.png" src="yuanhang-walkthrough.webm"></video><nav></nav><small>本次录制使用独立数据库；不会改变演示数据。生成时源码${expected.source.slice(0, 12)}，完整证据见evidence/video/recording.json。</small></main><script>const v=document.querySelector('video'),c=${safe(chapters)},t=document.createElement('track');t.kind='subtitles';t.label='中文操作说明';t.srclang='zh';t.default=true;t.src=URL.createObjectURL(new Blob([${safe(vtt)}],{type:'text/vtt'}));v.append(t);for(const x of c){const b=document.createElement('button');b.textContent=x.title;b.onclick=()=>{v.currentTime=x.start_s;v.play().catch(e=>{if(e.name!=='AbortError')document.querySelector('small').textContent='请点击播放器播放按钮，或使用支持WebM的浏览器。'})};document.querySelector('nav').append(b)}</script></html>`;
  await fs.writeFile(path.join(output, "walkthrough.html"), html);
  await fs.writeFile(
    path.join(evidence, "recording.json"),
    JSON.stringify(
      {
        recorded_at_utc: new Date().toISOString(),
        origin,
        runtime_relative: path.relative(root, runtime).replaceAll("\\", "/"),
        viewport: { width: 1440, height: 900 },
        captured_elapsed_s: end_s,
        source_sha256: expected.source,
        full_verification_matches_source: sourceVerified,
        service_health: health,
        scenario_id: scene.scenario_id,
        original_plan: original,
        original_snapshot: originalSnapshot,
        baseline_plan: baseline,
        final_plan: plan,
        final_snapshot: finalSnapshot,
        events,
        analysis,
        external_requests: external,
        page_errors: errors,
        chapters,
        video_sha256: videoHash,
        note: "Real browser recording of current production build in a dedicated retained runtime. No voice or simulated telemetry. Caption times are measured against page creation and may differ by a fraction of a second. Final video visual inspection is recorded separately.",
      },
      null,
      2,
    ) + "\n",
  );
  console.log(
    JSON.stringify({
      video: "deliverables/yuanhang-walkthrough.webm",
      player: "deliverables/walkthrough.html",
      elapsed_s: end_s,
      source_fully_verified: sourceVerified,
    }),
  );
} finally {
  if (context) await context.close().catch(() => {});
  if (browser) await browser.close().catch(() => {});
  if (service.exitCode === null) {
    service.kill();
    await Promise.race([
      new Promise((resolve) => service.once("exit", resolve)),
      pause(5000),
    ]);
  }
}
