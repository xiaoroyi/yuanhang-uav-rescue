/** Decode the real recorded video and exercise its offline caption/chapter player. */
import fs from "node:fs/promises";
import path from "node:path";
import { createHash } from "node:crypto";
import { createRequire } from "node:module";
import { fileURLToPath, pathToFileURL } from "node:url";
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
process.env.PLAYWRIGHT_BROWSERS_PATH = path.join(root, ".local/ms-playwright");
const require = createRequire(path.join(root, "frontend/package.json"));
const { chromium, expect } = require("@playwright/test");
const report = JSON.parse(
  await fs.readFile(path.join(root, "evidence/video/recording.json"), "utf8"),
);
const bytes = await fs.readFile(
  path.join(root, "deliverables/yuanhang-walkthrough.webm"),
);
if (createHash("sha256").update(bytes).digest("hex") !== report.video_sha256)
  throw new Error("Video hash differs from recording evidence.");
const output = path.join(root, "evidence/video/frames");
await fs.mkdir(output, { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 1000 } });
const errors = [],
  external = [],
  frames = [];
page.on("pageerror", (error) => errors.push(error.message));
page.on("request", (request) => {
  if (/^https?:/.test(request.url()))
    external.push(new URL(request.url()).origin);
});
try {
  await page.goto(
    pathToFileURL(path.join(root, "deliverables/walkthrough.html")).href,
  );
  const video = page.locator("video");
  await expect
    .poll(() => video.evaluate((v) => v.readyState), { timeout: 15000 })
    .toBeGreaterThanOrEqual(2);
  await expect
    .poll(() => video.evaluate((v) => v.textTracks[0]?.cues?.length || 0))
    .toBe(report.chapters.length);
  const media = await video.evaluate((v) => ({
    width: v.videoWidth,
    height: v.videoHeight,
    duration_s: v.duration,
    caption_mode: v.textTracks[0].mode,
    caption_count: v.textTracks[0].cues.length,
  }));
  if (
    media.width !== 1440 ||
    media.height !== 900 ||
    Math.abs(media.duration_s - report.captured_elapsed_s) > 3
  )
    throw new Error(
      "Decoded media dimensions or duration differ from capture.",
    );
  for (const i of [0, 3, 6, 8, 9, 11]) {
    const chapter = report.chapters[i];
    await page
      .getByRole("button", { name: chapter.title, exact: true })
      .click();
    await expect
      .poll(() => video.evaluate((v) => v.currentTime))
      .toBeGreaterThanOrEqual(chapter.start_s);
    await video.evaluate(async (v, t) => {
      v.pause();
      const seeked = new Promise((resolve, reject) => {
        v.addEventListener("seeked", resolve, { once: true });
        setTimeout(() => reject(new Error("Video seek timed out")), 5000);
      });
      v.currentTime = Math.min(t, v.duration - 0.1);
      await seeked;
    }, chapter.start_s + 1.2);
    await video.evaluate(async (v) => {
      await v.play();
      await new Promise((resolve) => v.requestVideoFrameCallback(resolve));
      v.pause();
      v.controls = false;
    });
    await page.waitForTimeout(150);
    const file = `chapter-${String(i + 1).padStart(2, "0")}.png`;
    await video.screenshot({ path: path.join(output, file) });
    frames.push({
      chapter: i + 1,
      title: chapter.title,
      requested_time_s: chapter.start_s + 1.2,
      image: "evidence/video/frames/" + file,
    });
  }
  if (errors.length || external.length)
    throw new Error(JSON.stringify({ errors, external }));
  await fs.writeFile(
    path.join(root, "evidence/video/playback-qa.json"),
    JSON.stringify(
      {
        at_utc: new Date().toISOString(),
        video_sha256: report.video_sha256,
        bytes: bytes.length,
        decoded_media: media,
        chapter_buttons: report.chapters.length,
        checked_chapter_seek: frames,
        page_errors: errors,
        external_requests: external,
        note: "Actual browser decoding and subtitle/chapter checks. Individual visual inspection of these captured video frames is recorded separately.",
      },
      null,
      2,
    ) + "\n",
  );
  console.log(
    JSON.stringify({
      decoded_media: media,
      frames: frames.length,
      external_requests: external.length,
      page_errors: errors.length,
    }),
  );
} finally {
  await browser.close();
}
