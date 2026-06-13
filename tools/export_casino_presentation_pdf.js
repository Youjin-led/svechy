const path = require("path");
const puppeteer = require("puppeteer");

const ROOT = path.resolve(__dirname, "..");
const DIR = path.join(ROOT, "presentation_casino_mirror");

(async () => {
  const browser = await puppeteer.launch({ headless: "new" });
  const page = await browser.newPage();
  await page.setViewport({ width: 1600, height: 900, deviceScaleFactor: 1 });
  await page.goto("file:///" + path.join(DIR, "index.html").replace(/\\/g, "/"), { waitUntil: "networkidle0" });
  await page.pdf({
    path: path.join(DIR, "casino_mirror_presentation.pdf"),
    width: "16in",
    height: "9in",
    printBackground: true,
    margin: { top: "0", right: "0", bottom: "0", left: "0" },
  });
  await page.screenshot({
    path: path.join(DIR, "preview_slide_01.png"),
    clip: { x: 0, y: 0, width: 1600, height: 900 },
  });
  await browser.close();
  console.log("presentation exported");
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
