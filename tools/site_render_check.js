const fs = require('fs');
const http = require('http');
const path = require('path');
const puppeteer = require('puppeteer');

function arg(name, fallback) {
  const index = process.argv.indexOf(name);
  if (index === -1 || index + 1 >= process.argv.length) return fallback;
  return process.argv[index + 1];
}

function contentType(filePath) {
  if (filePath.endsWith('.html')) return 'text/html; charset=utf-8';
  if (filePath.endsWith('.css')) return 'text/css; charset=utf-8';
  if (filePath.endsWith('.js')) return 'text/javascript; charset=utf-8';
  if (filePath.endsWith('.json')) return 'application/json; charset=utf-8';
  if (filePath.endsWith('.glb')) return 'model/gltf-binary';
  if (filePath.endsWith('.png')) return 'image/png';
  return 'application/octet-stream';
}

function startServer(root) {
  const server = http.createServer((request, response) => {
    const urlPath = decodeURIComponent(new URL(request.url, 'http://127.0.0.1').pathname);
    if (urlPath === '/favicon.ico') {
      response.writeHead(204);
      response.end();
      return;
    }

    const relativePath = urlPath === '/' ? 'index.html' : urlPath.slice(1);
    const filePath = path.resolve(root, relativePath);
    if (!filePath.startsWith(root) || !fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
      response.writeHead(404);
      response.end('Not found');
      return;
    }

    response.writeHead(200, {
      'Content-Type': contentType(filePath),
      'Cache-Control': 'no-store',
    });
    fs.createReadStream(filePath).pipe(response);
  });

  return new Promise((resolve) => {
    server.listen(0, '127.0.0.1', () => resolve(server));
  });
}

async function canvasSample(page) {
  return page.evaluate(() => {
    const canvas = document.querySelector('canvas');
    if (!canvas) return { exists: false, nonBlackRatio: 0, width: 0, height: 0 };
    const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
    if (!gl) return { exists: true, nonBlackRatio: 0, width: canvas.width, height: canvas.height };
    const width = Math.min(96, canvas.width);
    const height = Math.min(60, canvas.height);
    const x = Math.max(0, Math.floor((canvas.width - width) / 2));
    const y = Math.max(0, Math.floor((canvas.height - height) / 2));
    const data = new Uint8Array(width * height * 4);
    gl.readPixels(x, y, width, height, gl.RGBA, gl.UNSIGNED_BYTE, data);
    let nonBlack = 0;
    for (let i = 0; i < data.length; i += 4) {
      if (data[i] + data[i + 1] + data[i + 2] > 24) nonBlack += 1;
    }
    return { exists: true, nonBlackRatio: nonBlack / (width * height), width: canvas.width, height: canvas.height };
  });
}

(async () => {
  const root = path.resolve(arg('--root', '.'));
  const output = path.resolve(arg('--out', 'site-render-check.png'));
  const server = await startServer(root);
  const port = server.address().port;
  const logs = [];

  const browser = await puppeteer.launch({
    headless: 'new',
    timeout: 0,
    protocolTimeout: 180000,
    args: ['--disable-dev-shm-usage'],
  });
  const page = await browser.newPage();
  await page.setCacheEnabled(false);
  await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 1 });
  page.on('console', (message) => {
    if (message.type() === 'error') logs.push({ type: message.type(), text: message.text() });
  });
  page.on('pageerror', (error) => logs.push({ type: 'pageerror', text: error.message }));

  const url = `http://127.0.0.1:${port}/`;
  await Promise.race([
    page.goto(url, { waitUntil: 'domcontentloaded', timeout: 0 }).catch((error) => {
      logs.push({ type: 'navigation', text: error.message });
    }),
    new Promise((resolve) => setTimeout(resolve, 15000)),
  ]);
  await page.waitForFunction('window.__SCENE_READY === true || Boolean(window.__SCENE_ERROR)', { timeout: 90000 });
  await new Promise((resolve) => setTimeout(resolve, 2400));
  await page.screenshot({ path: output, fullPage: false });
  const sample = await canvasSample(page);
  const state = await page.evaluate(() => ({
    ready: window.__SCENE_READY === true,
    error: window.__SCENE_ERROR || '',
    railStops: Array.isArray(window.__CARD_RAIL) ? window.__CARD_RAIL.length : 0,
  }));

  await browser.close();
  server.close();

  const report = {
    status: state.ready && !state.error && logs.length === 0 && sample.nonBlackRatio > 0.015 ? 'PASS' : 'FAIL',
    output,
    state,
    sample,
    logs,
  };
  console.log(JSON.stringify(report, null, 2));
  if (report.status !== 'PASS') process.exit(2);
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
