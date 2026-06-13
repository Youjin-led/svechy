const http = require('http');
const fs = require('fs');
const path = require('path');
const puppeteer = require('C:/Users/Ардор/OneDrive/Рабочий стол/JS/ДЗ-1/node_modules/puppeteer');

const root = process.argv[2];
const outDir = process.argv[3] || process.cwd();
const port = Number(process.argv[4] || 5207);

const types = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.ico': 'image/x-icon',
};

const server = http.createServer((req, res) => {
  const url = new URL(req.url, 'http://127.0.0.1');
  let file = decodeURIComponent(url.pathname);
  if (file === '/') file = '/index.html';
  const full = path.normalize(path.join(root, file.replace(/^\/+/, '')));
  if (!full.startsWith(root)) {
    res.writeHead(403);
    res.end('Forbidden');
    return;
  }
  fs.readFile(full, (error, data) => {
    if (error) {
      res.writeHead(404);
      res.end('Not found');
      return;
    }
    res.writeHead(200, { 'content-type': types[path.extname(full)] || 'application/octet-stream' });
    res.end(data);
  });
});

async function run() {
  fs.mkdirSync(outDir, { recursive: true });
  await new Promise((resolve) => server.listen(port, '127.0.0.1', resolve));
  const browser = await puppeteer.launch({ headless: 'new' });
  const shots = [
    { name: 'fake-hero-desktop.png', width: 1440, height: 920 },
    { name: 'fake-hero-mobile.png', width: 430, height: 920, isMobile: true },
  ];
  for (const shot of shots) {
    const page = await browser.newPage();
    await page.setViewport({ width: shot.width, height: shot.height, deviceScaleFactor: 1, isMobile: Boolean(shot.isMobile) });
    await page.goto(`http://127.0.0.1:${port}/index.html`, { waitUntil: 'networkidle0', timeout: 60000 });
    const metrics = await page.evaluate(() => {
      const visual = document.querySelector('.hero-logo-board-fake');
      const labels = [...document.querySelectorAll('.hero-logo-board-fake .fake-logo strong')].map((el) => el.textContent);
      const oldImages = [...document.querySelectorAll('.hero-logo-board img')].length;
      return {
        labels,
        oldImages,
        visual: visual ? visual.getBoundingClientRect().toJSON() : null,
      };
    });
    await page.screenshot({ path: path.join(outDir, shot.name), fullPage: false });
    console.log(shot.name, JSON.stringify(metrics));
    await page.close();
  }
  await browser.close();
  server.close();
}

run().catch((error) => {
  console.error(error);
  server.close();
  process.exit(1);
});
