const path = require("path");
const { pathToFileURL } = require("url");
const puppeteer = require("puppeteer");

async function inspect(page) {
  return page.evaluate(() => ({
    title: document.title,
    h1: document.querySelector("h1")?.textContent.trim(),
    sources: document.querySelectorAll(".source-item").length,
    insights: document.querySelectorAll(".insight-item").length,
    knowledge: document.querySelectorAll(".knowledge-item").length,
    hasRunButton: Boolean(document.querySelector("#run-analysis")),
    hasAssistant: Boolean(document.querySelector("#ask-assistant")),
    hasHorizontalOverflow:
      document.documentElement.scrollWidth >
      document.documentElement.clientWidth + 1,
  }));
}

async function smokeViewport(page, fileUrl, viewport, screenshotPath) {
  await page.setViewport({ ...viewport, deviceScaleFactor: 1 });
  await page.goto(fileUrl, { waitUntil: "networkidle0", timeout: 60000 });
  await page.evaluate(() => localStorage.clear());
  await page.reload({ waitUntil: "networkidle0", timeout: 60000 });

  await page.click("#run-analysis");
  await new Promise((resolve) => setTimeout(resolve, 1100));
  await page.type("input[name='name']", "Новый источник");
  await page.type("input[name='url']", "https://example.ru/new");
  await page.select("select[name='topic']", "assortment");
  await page.click("#source-form button[type='submit']");
  await page.click("#ask-assistant");
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({ path: screenshotPath, fullPage: false });

  return inspect(page);
}

(async () => {
  const fileUrl = pathToFileURL(
    path.resolve("ai-business-project/client-monitoring-app/index.html"),
  ).href;
  const browser = await puppeteer.launch({ headless: "new" });
  const page = await browser.newPage();
  const errors = [];

  page.on("console", (message) => {
    if (message.type() === "error") errors.push(message.text());
  });
  page.on("pageerror", (error) => errors.push(error.message));

  const desktop = await smokeViewport(
    page,
    fileUrl,
    { width: 1440, height: 900 },
    "ai-business-project/client-monitoring-app-desktop.png",
  );
  const mobile = await smokeViewport(
    page,
    fileUrl,
    { width: 390, height: 844 },
    "ai-business-project/client-monitoring-app-mobile.png",
  );

  await browser.close();

  const result = { desktop, mobile, errors };
  console.log(JSON.stringify(result, null, 2));

  if (
    errors.length ||
    desktop.sources < 4 ||
    desktop.insights < 4 ||
    desktop.knowledge < 3 ||
    mobile.sources < 4 ||
    mobile.insights < 4 ||
    desktop.hasHorizontalOverflow ||
    mobile.hasHorizontalOverflow
  ) {
    process.exit(1);
  }
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
