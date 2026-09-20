const { chromium } = require("playwright");

const sleep = milliseconds => new Promise(resolve => setTimeout(resolve, milliseconds));
const apiHeaders = () => ({"Content-Type": "application/json", "X-Synthetic-Token": process.env.SYNTHETIC_API_TOKEN});

const emit = fields => console.log(JSON.stringify({
  "@timestamp": new Date().toISOString(),
  "message": "synthetic monitoring check completed",
  "service.name": "network-monitor-synthetic",
  "service.type": "synthetic",
  "event.dataset": "network_monitor.synthetic",
  ...fields
}));

async function loadConfig() {
  const response = await fetch(`${process.env.CONFIG_API_URL}/api/internal/synthetic/config`, {headers: apiHeaders()});
  if (!response.ok) throw new Error(`configuration API returned ${response.status}`);
  return response.json();
}

async function saveResult(result) {
  const response = await fetch(`${process.env.CONFIG_API_URL}/api/internal/synthetic/results`, {
    method: "POST", headers: apiHeaders(), body: JSON.stringify(result)
  });
  if (!response.ok) throw new Error(`result API returned ${response.status}`);
}

async function runCheck(config) {
  let browser;
  let statusCode = null;
  let responseTimeMs = 0;
  try {
    browser = await chromium.launch({headless: true});
    const page = await browser.newPage();
    const requestStarted = performance.now();
    const response = await page.goto(process.env.TEST_BASE_URL, {waitUntil: "commit", timeout: 30000});
    responseTimeMs = Math.round((performance.now() - requestStarted) * 100) / 100;
    statusCode = response && response.status();
    if (!response || !response.ok()) throw new Error(`web status ${statusCode}`);
    await page.locator("#login-form").waitFor({state: "visible", timeout: 15000});
    await page.locator('#login-form input[name="username"]').fill(config.username);
    await page.locator('#login-form input[name="password"]').fill(config.password);
    await page.locator("#login-form button").click();
    await page.locator("#application").waitFor({state: "visible", timeout: 15000});
    await saveResult({outcome: "success", status_code: statusCode, response_time_ms: responseTimeMs});
    emit({"event.outcome": "success", "monitor.status": "up", "http.response.status_code": statusCode, "event.duration_ms": responseTimeMs});
  } catch (error) {
    const result = {outcome: "failure", status_code: statusCode, response_time_ms: responseTimeMs, error_message: String(error.message).slice(0, 200)};
    try { await saveResult(result); } catch (saveError) { console.error(saveError); }
    emit({"event.outcome": "failure", "monitor.status": "down", "http.response.status_code": statusCode, "event.duration_ms": responseTimeMs, "error.type": error.constructor.name, "error.message": result.error_message});
  } finally {
    if (browser) await browser.close();
  }
}

(async () => {
  for (const name of ["TEST_BASE_URL", "CONFIG_API_URL", "SYNTHETIC_API_TOKEN"]) {
    if (!process.env[name]) throw new Error(`${name} is required`);
  }
  let nextRun = 0;
  let version = null;
  while (true) {
    try {
      const config = await loadConfig();
      if (!config.configured) {
        nextRun = 0;
        version = null;
      } else {
        if (config.version !== version) { version = config.version; nextRun = 0; }
        if (Date.now() >= nextRun) {
          await runCheck(config);
          nextRun = Date.now() + config.interval_seconds * 1000;
        }
      }
    } catch (error) {
      console.error(`synthetic scheduler: ${error.message}`);
    }
    await sleep(5000);
  }
})();
