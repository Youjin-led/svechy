const puppeteer = require('C:/Users/Ардор/OneDrive/Рабочий стол/JS/ДЗ-1/node_modules/puppeteer');

(async () => {
  const url = process.argv[2] || 'http://127.0.0.1:5178/';
  const output = process.argv[3] || 'site-preview.png';
  const browser = await puppeteer.launch({ headless: 'new', timeout: 90000 });
  const page = await browser.newPage();
  await page.setCacheEnabled(false);

  const logs = [];
  page.on('console', (message) => {
    const text = message.text();
    if (message.type() === 'error' || text.includes('shader') || text.includes('WebGL')) {
      logs.push({ type: message.type(), text });
    }
  });
  page.on('pageerror', (error) => logs.push({ type: 'pageerror', text: error.message }));

  await page.setDefaultTimeout(120000);
  await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 1 });
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 90000 });
  await page.waitForFunction('window.__SCENE_READY === true || Boolean(window.__SCENE_ERROR)', {
    timeout: 120000,
  });
  await new Promise((resolve) => setTimeout(resolve, 2500));
  await page.screenshot({ path: output, fullPage: false });

  const result = await page.evaluate(() => ({
    ready: window.__SCENE_READY,
    error: window.__SCENE_ERROR || '',
    canvas: Boolean(document.querySelector('canvas')),
  }));

  console.log(JSON.stringify({ result, logs, output }, null, 2));
  await browser.close();
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
