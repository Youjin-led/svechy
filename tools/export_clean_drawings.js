const fs = require("fs");
const path = require("path");
const puppeteer = require("puppeteer");

const ROOT = path.resolve(__dirname, "..");
const OUT = path.join(ROOT, "чертежи");

function size(svg) {
  return {
    w: Number(/width="([\d.]+)mm"/.exec(svg)?.[1] || 1200),
    h: Number(/height="([\d.]+)mm"/.exec(svg)?.[1] || 800),
  };
}

(async () => {
  const browser = await puppeteer.launch({ headless: "new" });
  const page = await browser.newPage();
  const svgs = fs.readdirSync(OUT).filter((f) => f.endsWith(".svg"));
  for (const file of svgs) {
    const svg = fs.readFileSync(path.join(OUT, file), "utf8");
    const { w, h } = size(svg);
    await page.setContent(`<!doctype html><meta charset="utf-8"><style>html,body{margin:0;background:white}svg{display:block}</style>${svg}`, { waitUntil: "load" });
    await page.pdf({
      path: path.join(OUT, file.replace(".svg", ".pdf")),
      width: `${w}mm`,
      height: `${h}mm`,
      printBackground: true,
      margin: { top: "0mm", right: "0mm", bottom: "0mm", left: "0mm" },
    });
    if (file === "01_fasad_kompozicii.svg") {
      await page.setViewport({ width: 1800, height: 1550, deviceScaleFactor: 1 });
      await page.screenshot({ path: path.join(OUT, "01_fasad_kompozicii.png"), fullPage: true });
    }
  }
  await browser.close();
  console.log(`exported ${svgs.length} svg sheets`);
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
