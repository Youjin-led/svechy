const path = require('path');
const fs = require('fs');
const http = require('http');

function contentType(filePath) {
  if (filePath.endsWith('.js')) return 'text/javascript; charset=utf-8';
  if (filePath.endsWith('.html')) return 'text/html; charset=utf-8';
  if (filePath.endsWith('.css')) return 'text/css; charset=utf-8';
  if (filePath.endsWith('.json')) return 'application/json; charset=utf-8';
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

    response.writeHead(200, { 'Content-Type': contentType(filePath) });
    fs.createReadStream(filePath).pipe(response);
  });

  return new Promise((resolve) => {
    server.listen(0, '127.0.0.1', () => resolve(server));
  });
}

async function main() {
  let puppeteer;
  try {
    puppeteer = require('puppeteer');
  } catch (error) {
    console.error('Puppeteer is not installed. Run: npm install');
    process.exit(1);
  }

  const htmlPath = process.argv[2];
  const prompt = process.argv[3] || '';
  const root = path.dirname(path.resolve(htmlPath));
  const errors = [];
  const server = await startServer(root);
  const port = server.address().port;
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();

  page.on('console', (message) => {
    if (message.type() === 'error') errors.push(`console: ${message.text()}`);
  });
  page.on('pageerror', (error) => errors.push(`pageerror: ${error.message}`));

  try {
    await page.goto(`http://127.0.0.1:${port}/index.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForSelector('canvas', { timeout: 5000 });
    await page.waitForFunction(() => window.__SCENE_DIAGNOSTICS__, { timeout: 10000 });
  } catch (error) {
    errors.push(error.stack || error.message);
  }

  const diagnostics = await page.evaluate(() => window.__SCENE_DIAGNOSTICS__ || null);
  if (!diagnostics) errors.push('3D diagnostics object is missing.');
  if (!diagnostics?.hasRendererCanvas) errors.push('Renderer canvas was not created.');
  if (!diagnostics?.hasBlenderAssets) errors.push('Blender asset metadata is missing from scene specs.');
  if (!diagnostics?.hasExternalArtist) errors.push('External 3D artist metadata is missing from scene specs.');
  if (!diagnostics?.objectCount || diagnostics.objectCount < 3) errors.push('3D scene is empty or nearly empty.');
  if (/\u043a\u0440\u0430\u0441\u043d|\bred\b/i.test(prompt) && diagnostics?.carColor !== 0xff0000) {
    errors.push(`Car is not red. Expected 0xff0000, got ${diagnostics?.carColor}.`);
  }

  await browser.close();
  server.close();
  process.stdout.write(JSON.stringify({ status: errors.length ? 'FAIL' : 'PASS', errors }));
  if (errors.length) process.exit(2);
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exit(1);
});
