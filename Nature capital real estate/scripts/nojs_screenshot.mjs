#!/usr/bin/env node
// Full-page screenshot with JavaScript turned off, through the DevTools protocol.
// Chrome 154 headless writes no image with --blink-settings=scriptEnabled=false.
// Usage: node scripts/nojs_screenshot.mjs <url> <width> <out.png> <debug port>
// Uses Node's built-in fetch and WebSocket only (Node 22 or later).
import { spawn } from "node:child_process";
import { writeFileSync } from "node:fs";

const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const [url, widthArg, out, portArg] = process.argv.slice(2);
const width = Number(widthArg);
const port = Number(portArg);
if (!url || !out || !(width >= 500) || !(port > 1024)) {
  console.error("usage: node scripts/nojs_screenshot.mjs <url> <width >= 500> <out.png> <debug port>");
  process.exit(2);
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// A Chrome already on this port belongs to someone else; never drive it.
if (await fetch(`http://127.0.0.1:${port}/json/version`).then(() => true, () => false)) {
  console.error(`nojs_screenshot: port ${port} is already in use; pick another`);
  process.exit(1);
}

// Started and stopped here by its own PID, so other lanes' Chrome is never touched.
const chrome = spawn(CHROME, ["--headless=new", "--disable-gpu", "--hide-scrollbars",
  `--remote-debugging-port=${port}`, "about:blank"], { stdio: "ignore" });
chrome.on("error", fail);
process.on("exit", () => chrome.kill());
for (const signal of ["SIGINT", "SIGTERM"]) process.on(signal, () => process.exit(130));
const timer = setTimeout(() => fail(new Error("timed out after 40 s")), 40000);

function fail(err) {
  console.error(`nojs_screenshot: ${err.message}`);
  chrome.kill();
  process.exit(1);
}

async function debuggerUrl() {
  for (let i = 0; i < 40; i++) {
    try {
      const res = await fetch(`http://127.0.0.1:${port}/json/version`);
      return (await res.json()).webSocketDebuggerUrl;
    } catch {
      await sleep(250);
    }
  }
  throw new Error(`Chrome did not open port ${port}`);
}

async function main() {
  const ws = new WebSocket(await debuggerUrl());
  await new Promise((r) => ws.addEventListener("open", r, { once: true }));

  let id = 0;
  const waiting = new Map();
  const events = [];
  ws.addEventListener("message", ({ data }) => {
    const msg = JSON.parse(data);
    if (msg.id && waiting.has(msg.id)) waiting.get(msg.id)(msg);
    else events.push(msg);
  });
  const send = (method, params = {}, sessionId) => new Promise((resolve, reject) => {
    const n = ++id;
    waiting.set(n, (m) => (m.error ? reject(new Error(`${method}: ${m.error.message}`)) : resolve(m.result)));
    ws.send(JSON.stringify({ id: n, method, params, sessionId }));
  });

  const { targetId } = await send("Target.createTarget", { url: "about:blank" });
  const { sessionId } = await send("Target.attachToTarget", { targetId, flatten: true });
  const page = (method, params) => send(method, params, sessionId);
  const size = (height) => page("Emulation.setDeviceMetricsOverride",
    { width, height, deviceScaleFactor: 1, mobile: false });

  // Scripts must be off before the page loads. Runtime.evaluate never answers
  // while they are off, so measure with Page.getLayoutMetrics (or DOM.getBoxModel).
  await page("Page.enable");
  await page("Emulation.setScriptExecutionDisabled", { value: true });
  await size(900);
  // A dead server still loads Chrome's error page, so check the reply instead.
  const { errorText } = await page("Page.navigate", { url });
  if (errorText) throw new Error(`${url}: ${errorText}`);
  while (!events.some((e) => e.method === "Page.loadEventFired" && e.sessionId === sessionId)) await sleep(100);
  await sleep(1500); // web fonts and images

  const { cssContentSize } = await page("Page.getLayoutMetrics");
  const height = Math.ceil(cssContentSize.height);
  await size(height);
  const { data } = await page("Page.captureScreenshot", { format: "png", captureBeyondViewport: true });
  writeFileSync(out, Buffer.from(data, "base64"));
  console.log(`${out} ${width}x${height}`);
  ws.close();
}

main().then(() => {
  clearTimeout(timer);
  chrome.kill();
}, fail);
