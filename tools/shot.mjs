// Headless screenshot harness: the cheap half of the article's QA loop.
// Usage: node tools/shot.mjs [outfile] [width] [height]
import { chromium } from "playwright";
import { mkdir } from "node:fs/promises";
import path from "node:path";

const out = process.argv[2] ?? "build/web.png";
const width = Number(process.argv[3] ?? 1280);
const height = Number(process.argv[4] ?? 800);
const url = process.env.SHOT_URL ?? "http://127.0.0.1:9100/";

await mkdir(path.dirname(out), { recursive: true });

const browser = await chromium.launch({
  args: ["--use-gl=angle", "--use-angle=metal", "--enable-gpu"],
});
const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 2 });

const errors = [];
page.on("console", (m) => {
  if (m.type() === "error") errors.push(m.text());
});
page.on("pageerror", (e) => errors.push(String(e)));

await page.goto(url, { waitUntil: "networkidle", timeout: 30000 });
await page.waitForFunction(
  () => /\d/.test(document.getElementById("stat")?.textContent ?? ""),
  null,
  { timeout: 20000 },
);
await page.waitForTimeout(1200);
await page.screenshot({ path: out });

const stat = await page.textContent("#stat");
await browser.close();

console.log(`shot -> ${out}`);
console.log(`stat -> ${stat}`);
if (errors.length) {
  console.error(`console errors (${errors.length}):`);
  for (const e of errors) console.error(`  ${e}`);
  process.exitCode = 1;
} else {
  console.log("console -> clean");
}
