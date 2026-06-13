const fs = require('fs');
const http = require('http');
const path = require('path');
const puppeteer = require('puppeteer');

function arg(name, fallback) {
  const index = process.argv.indexOf(name);
  if (index === -1 || index + 1 >= process.argv.length) return fallback;
  return process.argv[index + 1];
}

function hasFlag(name) {
  return process.argv.includes(name);
}

function contentType(filePath) {
  if (filePath.endsWith('.html')) return 'text/html; charset=utf-8';
  if (filePath.endsWith('.js')) return 'text/javascript; charset=utf-8';
  if (filePath.endsWith('.css')) return 'text/css; charset=utf-8';
  if (filePath.endsWith('.json')) return 'application/json; charset=utf-8';
  if (filePath.endsWith('.png')) return 'image/png';
  if (filePath.endsWith('.jpg') || filePath.endsWith('.jpeg')) return 'image/jpeg';
  if (filePath.endsWith('.glb')) return 'model/gltf-binary';
  if (filePath.endsWith('.wasm')) return 'application/wasm';
  return 'application/octet-stream';
}

function startStaticServer(root, preferredPort) {
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
    response.writeHead(200, { 'Content-Type': contentType(filePath) });
    fs.createReadStream(filePath).pipe(response);
  });

  return new Promise((resolve) => {
    function listen(port) {
      server.once('error', () => listen(0));
      server.listen(port || 0, '127.0.0.1', () => resolve(server));
    }
    listen(preferredPort);
  });
}

function closeServer(server) {
  return new Promise((resolve) => {
    if (!server) {
      resolve();
      return;
    }
    server.close(() => {
      resolve();
    });
  });
}

async function canvasSample(page) {
  return page.evaluate(() => {
    const canvas = document.querySelector('canvas');
    if (!canvas) return { exists: false, nonBlackRatio: 0, width: 0, height: 0 };
    const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
    if (!gl) {
      const ctx = canvas.getContext('2d', { willReadFrequently: true });
      if (!ctx) return { exists: true, nonBlackRatio: 0, width: canvas.width, height: canvas.height, method: 'no-readable-context' };
      const width = Math.min(96, canvas.width);
      const height = Math.min(60, canvas.height);
      const x = Math.max(0, Math.floor((canvas.width - width) / 2));
      const y = Math.max(0, Math.floor((canvas.height - height) / 2));
      const data = ctx.getImageData(x, y, width, height).data;
      let nonBlack = 0;
      for (let i = 0; i < data.length; i += 4) {
        if (data[i] + data[i + 1] + data[i + 2] > 24) nonBlack += 1;
      }
      return {
        exists: true,
        nonBlackRatio: nonBlack / (width * height),
        width: canvas.width,
        height: canvas.height,
        method: '2d-getimagedata',
      };
    }
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
    return {
      exists: true,
      nonBlackRatio: nonBlack / (width * height),
      width: canvas.width,
      height: canvas.height,
      method: 'webgl-readpixels',
    };
  });
}

(async () => {
  const url = arg('--url', 'http://127.0.0.1:5178/');
  const outputDir = path.resolve(arg('--out', 'visual-qa'));
  const steps = Number(arg('--steps', '4'));
  const waitMs = Number(arg('--wait', '1400'));
  const width = Number(arg('--width', '1440'));
  const height = Number(arg('--height', '900'));
  const mobile = hasFlag('--mobile');
  let server = null;
  let targetUrl = url;

  if (!process.argv.includes('--url')) {
    const parsedUrl = new URL(url);
    server = await startStaticServer(path.resolve(__dirname, '..'), Number(parsedUrl.port));
    const port = server.address().port;
    targetUrl = `http://127.0.0.1:${port}/`;
  }

  fs.mkdirSync(outputDir, { recursive: true });

  const browser = await puppeteer.launch({ headless: 'new', timeout: 90000 });
  const page = await browser.newPage();
  await page.setCacheEnabled(false);
  await page.setViewport({
    width: mobile ? 390 : width,
    height: mobile ? 844 : height,
    deviceScaleFactor: mobile ? 2 : 1,
  });

  const logs = [];
  page.on('console', (message) => {
    const text = message.text();
    if (message.type() === 'error' || text.includes('shader') || text.includes('WebGL')) {
      logs.push({ type: message.type(), text });
    }
  });
  page.on('pageerror', (error) => logs.push({ type: 'pageerror', text: error.message }));

  await page.goto(`${targetUrl}${targetUrl.includes('?') ? '&' : '?'}visualQa=${Date.now()}`, {
    waitUntil: 'domcontentloaded',
    timeout: 90000,
  });
  await page.waitForFunction('window.__SCENE_READY === true || Boolean(window.__SCENE_DIAGNOSTICS__) || Boolean(window.__SCENE_ERROR)', {
    timeout: 120000,
  });
  await new Promise((resolve) => setTimeout(resolve, waitMs));

  const frames = [];
  for (let step = 0; step < steps; step += 1) {
    if (step > 0) {
      await page.mouse.wheel({ deltaY: 900 });
      await new Promise((resolve) => setTimeout(resolve, waitMs));
    }
    const file = path.join(outputDir, `frame-${String(step).padStart(2, '0')}.png`);
    await page.screenshot({ path: file, fullPage: false });
    const sample = await canvasSample(page);
    const bytes = fs.statSync(file).size;
    frames.push({ step, file, bytes, sample });
  }

  const state = await page.evaluate(() => ({
    ready: window.__SCENE_READY === true || Boolean(window.__SCENE_DIAGNOSTICS__),
    error: window.__SCENE_ERROR || '',
    hasCanvas: Boolean(document.querySelector('canvas')),
    diagnostics: window.__SCENE_DIAGNOSTICS__ || null,
    railStops: Array.isArray(window.__CARD_RAIL) ? window.__CARD_RAIL.length : null,
  }));

  await browser.close();
  await closeServer(server);

  const failedFrames = frames.filter((frame) => {
    if (!frame.sample.exists) return true;
    if (frame.sample.nonBlackRatio >= 0.015) return false;
    return frame.bytes < 25000;
  });
  const report = {
    status: state.ready && !state.error && logs.length === 0 && failedFrames.length === 0 ? 'PASS' : 'FAIL',
    url: targetUrl,
    state,
    logs,
    frames,
  };
  fs.writeFileSync(path.join(outputDir, 'report.json'), JSON.stringify(report, null, 2), 'utf8');
  console.log(JSON.stringify(report, null, 2));
  if (report.status !== 'PASS') process.exit(2);
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
