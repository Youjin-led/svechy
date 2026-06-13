const path = require("path");
const { pathToFileURL } = require("url");
const puppeteer = require("puppeteer");

async function checkPage(page, fileUrl, viewport, screenshotPath) {
  await page.setViewport({ ...viewport, deviceScaleFactor: 1 });
  await page.goto(fileUrl, { waitUntil: "networkidle0", timeout: 60000 });
  await page.screenshot({ path: screenshotPath, fullPage: false });

  return page.evaluate(() => ({
    title: document.title,
    h1: document.querySelector("h1")?.textContent.trim(),
    hasPrice:
      document.body.textContent.includes("70 000 ₽") &&
      document.body.textContent.includes("15 000 ₽/мес"),
    hasForm: Boolean(document.querySelector("#request-form")),
    hasLeadCta: Array.from(document.querySelectorAll("a")).some(
      (link) => link.getAttribute("href") === "#lead",
    ),
    faqCount: document.querySelectorAll("details").length,
    hasHorizontalOverflow:
      document.documentElement.scrollWidth >
      document.documentElement.clientWidth + 1,
  }));
}

(async () => {
  const fileUrl = pathToFileURL(
    path.resolve("ai-business-project/sales-site/index.html"),
  ).href;
  const browser = await puppeteer.launch({ headless: "new" });
  const page = await browser.newPage();
  const errors = [];

  page.on("console", (message) => {
    if (message.type() === "error") errors.push(message.text());
  });
  page.on("pageerror", (error) => errors.push(error.message));

  const desktop = await checkPage(
    page,
    fileUrl,
    { width: 1440, height: 900 },
    "ai-business-project/sales-site-desktop.png",
  );
  const mobile = await checkPage(
    page,
    fileUrl,
    { width: 390, height: 844 },
    "ai-business-project/sales-site-mobile.png",
  );

  await browser.close();

  const result = { desktop, mobile, errors };
  console.log(JSON.stringify(result, null, 2));

  if (
    errors.length ||
    !desktop.hasPrice ||
    !desktop.hasForm ||
    !mobile.hasPrice ||
    !mobile.hasForm ||
    desktop.hasHorizontalOverflow ||
    mobile.hasHorizontalOverflow
  ) {
    process.exit(1);
  }
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
