const fs = require("fs");
const path = require("path");
const puppeteer = require("puppeteer");

const ROOT = path.resolve(__dirname, "..");
const DIR = path.join(ROOT, "чертежи_для_конструктора");

function getSize(svg) {
  return {
    w: Number(/width="([\d.]+)mm"/.exec(svg)?.[1] || 1600),
    h: Number(/height="([\d.]+)mm"/.exec(svg)?.[1] || 1100),
  };
}

(async () => {
  const browser = await puppeteer.launch({ headless: "new" });
  const page = await browser.newPage();
  const svgs = fs.readdirSync(DIR).filter((f) => f.endsWith(".svg"));
  for (const file of svgs) {
    const svg = fs.readFileSync(path.join(DIR, file), "utf8");
    const { w, h } = getSize(svg);
    await page.setContent(`<!doctype html><meta charset="utf-8"><style>html,body{margin:0;background:white}svg{display:block}</style>${svg}`, { waitUntil: "load" });
    await page.pdf({
      path: path.join(DIR, file.replace(".svg", ".pdf")),
      width: `${w}mm`,
      height: `${h}mm`,
      printBackground: true,
      margin: { top: "0mm", right: "0mm", bottom: "0mm", left: "0mm" },
    });
    await page.setViewport({ width: 1600, height: 1100, deviceScaleFactor: 1 });
    await page.screenshot({ path: path.join(DIR, file.replace(".svg", ".png")), fullPage: true });
  }
  await browser.close();
  console.log(`exported ${svgs.length} constructor sheets`);
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
