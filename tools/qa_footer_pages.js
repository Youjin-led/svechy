const http = require('http');
const fs = require('fs');
const path = require('path');
const puppeteer = require('C:/Users/Ардор/OneDrive/Рабочий стол/JS/ДЗ-1/node_modules/puppeteer');

const root = process.argv[2];
const port = Number(process.argv[3] || 5199);

const types = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.ico': 'image/x-icon',
  '.xml': 'application/xml; charset=utf-8',
  '.txt': 'text/plain; charset=utf-8',
};

const server = http.createServer((req, res) => {
  const url = new URL(req.url, 'http://127.0.0.1');
  let file = decodeURIComponent(url.pathname);
  if (file === '/') file = '/index.html';
  file = file.replace(/^\/+/, '');
  const full = path.normalize(path.join(root, file));
  if (!full.startsWith(root)) {
    res.writeHead(403);
    res.end('Forbidden');
    return;
  }
  fs.readFile(full, (error, data) => {
    if (error) {
      res.writeHead(404);
      res.end(`Not found: ${full}`);
      return;
    }
    res.writeHead(200, { 'content-type': types[path.extname(full)] || 'application/octet-stream' });
    res.end(data);
  });
});

async function run() {
  await new Promise((resolve) => server.listen(port, '127.0.0.1', resolve));
  const browser = await puppeteer.launch({ headless: 'new' });
  const pages = ['/index.html', '/catalog.html', '/mktu.html', '/faq.html', '/place.html', '/privacy.html', '/trademarks/001.html'];
  for (const page of pages) {
    const tab = await browser.newPage();
    await tab.setViewport({ width: 1440, height: 1200, deviceScaleFactor: 1 });
    await tab.goto(`http://127.0.0.1:${port}${page}`, { waitUntil: 'networkidle0', timeout: 60000 });
    const data = await tab.evaluate(() => {
      const phone = document.querySelector('.site-footer .footer-brand a[href^="tel"]');
      const span = document.querySelector('.site-footer .footer-brand > span');
      const proof = document.querySelector('.ai-answer-section + .proof-strip');
      const ai = document.querySelector('.ai-answer-section');
      const proofRect = proof && proof.getBoundingClientRect();
      const aiRect = ai && ai.getBoundingClientRect();
      return {
        title: document.title,
        phone: phone && phone.textContent.trim(),
        phoneColor: phone && getComputedStyle(phone).color,
        spanColor: span && getComputedStyle(span).color,
        footerText: document.querySelector('.site-footer')?.innerText.slice(0, 120),
        proofGap: proofRect && aiRect ? Math.round(proofRect.top - aiRect.bottom) : null,
      };
    });
    console.log(page, JSON.stringify(data));
    await tab.close();
  }
  await browser.close();
  server.close();
}

run().catch((error) => {
  console.error(error);
  server.close();
  process.exit(1);
});
