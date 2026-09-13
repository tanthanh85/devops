const { test, expect } = require("@playwright/test");

test("authenticated user can collect and chart router metrics", async ({ page }) => {
  const baseURL = process.env.TEST_BASE_URL;
  const username = process.env.E2E_USERNAME;
  const password = process.env.E2E_PASSWORD;

  if (!baseURL || !username || !password) {
    throw new Error("TEST_BASE_URL, E2E_USERNAME, and E2E_PASSWORD are required");
  }

  await page.goto(baseURL, { waitUntil: "networkidle" });
  await expect(page.locator("#instance span")).toContainText(/network-monitor-web-.+ · \d+\.\d+\.\d+\.\d+/);
  await page.locator('#login-form input[name="username"]').fill(username);
  await page.locator('#login-form input[name="password"]').fill(password);
  await page.locator("#login-form button").click();

  await expect(page.locator("#application")).toBeVisible();
  await expect.poll(
    async () => page.locator("#router-select option").count(),
    { timeout: 15_000 }
  ).toBeGreaterThan(0);

  await page.locator("#collect").click();
  await expect(page.locator("#values")).toContainText(/CPU \d+(\.\d+)?% · Memory \d+(\.\d+)?%/, { timeout: 30_000 });
  await page.waitForTimeout(500);
  await page.locator("#collect").click();
  await expect(page.locator("#values")).toContainText(/CPU \d+(\.\d+)?% · Memory \d+(\.\d+)?%/, { timeout: 30_000 });

  const renderedPixels = await page.locator("#chart").evaluate((canvas) => {
    const context = canvas.getContext("2d");
    const pixels = context.getImageData(0, 0, canvas.width, canvas.height).data;
    let nonTransparent = 0;
    for (let index = 3; index < pixels.length; index += 4) {
      if (pixels[index] !== 0) nonTransparent += 1;
    }
    return nonTransparent;
  });
  expect(renderedPixels).toBeGreaterThan(0);
  await page.screenshot({ path: "test-results/monitoring-page.png", fullPage: true });
});
