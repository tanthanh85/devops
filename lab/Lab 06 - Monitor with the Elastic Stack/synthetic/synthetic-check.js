const { chromium } = require("playwright");

const emit = fields => console.log(JSON.stringify({
  "@timestamp": new Date().toISOString(),
  "message": "synthetic monitoring check completed",
  "service.name": "network-monitor-synthetic",
  "service.type": "synthetic",
  "event.dataset": "network_monitor.synthetic",
  ...fields
}));

(async () => {
  const started = performance.now();
  let browser;
  try {
    for (const name of ["TEST_BASE_URL", "E2E_USERNAME", "E2E_PASSWORD"]) {
      if (!process.env[name]) throw new Error(`${name} is required`);
    }
    browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    const response = await page.goto(process.env.TEST_BASE_URL, { waitUntil: "networkidle", timeout: 30000 });
    if (!response || !response.ok()) throw new Error(`web status ${response && response.status()}`);
    await page.locator('#login-form input[name="username"]').fill(process.env.E2E_USERNAME);
    await page.locator('#login-form input[name="password"]').fill(process.env.E2E_PASSWORD);
    await page.locator("#login-form button").click();
    await page.locator("#application").waitFor({ state: "visible", timeout: 15000 });
    if (await page.locator("#router-select option").count() < 1) throw new Error("router inventory is empty");
    await page.locator("#collect").click();
    await page.waitForFunction(() => document.querySelector("#time-value")?.textContent !== "--", null, { timeout: 30000 });
    const cpuText = await page.locator("#cpu-value").textContent();
    const memoryText = await page.locator("#memory-value").textContent();
    const cpu = Number.parseFloat(cpuText);
    const memory = Number.parseFloat(memoryText);
    if (!Number.isFinite(cpu) || !Number.isFinite(memory)) throw new Error("CPU and memory values were not displayed");
    emit({
      "event.outcome": "success",
      "monitor.status": "up",
      "http.response.status_code": response.status(),
      "event.duration_ms": Math.round((performance.now() - started) * 100) / 100,
      "network.router.cpu.pct": cpu,
      "network.router.memory.pct": memory
    });
  } catch (error) {
    emit({
      "event.outcome": "failure",
      "monitor.status": "down",
      "event.duration_ms": Math.round((performance.now() - started) * 100) / 100,
      "error.type": error.constructor.name,
      "error.message": String(error.message).slice(0, 200)
    });
    process.exitCode = 1;
  } finally {
    if (browser) await browser.close();
  }
})();
