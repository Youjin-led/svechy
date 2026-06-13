const fs = require('fs');
const http = require('http');
const path = require('path');

const root = __dirname;
const port = Number(process.env.PORT || 5177);
const dataFile = path.join(root, 'data', 'cms.json');

function contentType(filePath) {
  if (filePath.endsWith('.html')) return 'text/html; charset=utf-8';
  if (filePath.endsWith('.js')) return 'text/javascript; charset=utf-8';
  if (filePath.endsWith('.css')) return 'text/css; charset=utf-8';
  if (filePath.endsWith('.json')) return 'application/json; charset=utf-8';
  if (filePath.endsWith('.glb')) return 'model/gltf-binary';
  if (filePath.endsWith('.wasm')) return 'application/wasm';
  return 'application/octet-stream';
}

function sendJson(response, status, payload) {
  response.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8' });
  response.end(JSON.stringify(payload));
}

function readJsonBody(request) {
  return new Promise((resolve, reject) => {
    let body = '';
    request.on('data', (chunk) => {
      body += chunk;
      if (body.length > 1_000_000) {
        request.destroy();
        reject(new Error('Payload too large'));
      }
    });
    request.on('end', () => {
      try {
        resolve(body ? JSON.parse(body) : {});
      } catch (error) {
        reject(error);
      }
    });
  });
}

function readCms() {
  return JSON.parse(fs.readFileSync(dataFile, 'utf8'));
}

function writeCms(data) {
  fs.mkdirSync(path.dirname(dataFile), { recursive: true });
  fs.writeFileSync(dataFile, JSON.stringify(data, null, 2), 'utf8');
}

function createId(prefix) {
  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`;
}

function removeById(items, id) {
  const next = items.filter((item) => item.id !== id);
  return { next, removed: next.length !== items.length };
}

async function handleApi(request, response, url) {
  try {
    const cms = readCms();
    if (request.method === 'GET' && url.pathname === '/api/cms') {
      sendJson(response, 200, cms);
      return true;
    }

    if (request.method === 'POST' && url.pathname === '/api/blog') {
      const body = await readJsonBody(request);
      cms.blog.unshift({
        id: createId('blog'),
        tag: String(body.tag || 'Разбор'),
        title: String(body.title || 'Новая статья'),
        text: String(body.text || ''),
        url: String(body.url || 'blog.html')
      });
      writeCms(cms);
      sendJson(response, 200, cms);
      return true;
    }

    if (request.method === 'POST' && url.pathname === '/api/reviews') {
      const body = await readJsonBody(request);
      cms.reviews.unshift({
        id: createId('review'),
        name: String(body.name || 'Гость'),
        meta: String(body.meta || 'Отзыв с сайта'),
        title: String(body.title || 'Отзыв'),
        text: String(body.text || ''),
        rating: Math.max(1, Math.min(5, Number(body.rating || 5))),
        approved: body.approved !== false
      });
      writeCms(cms);
      sendJson(response, 200, cms);
      return true;
    }

    if (request.method === 'POST' && url.pathname === '/api/categories') {
      const body = await readJsonBody(request);
      const section = body.section === 'maker' ? 'maker' : 'wholesale';
      cms.sections[section].categories.push({
        name: String(body.name || 'Новый раздел'),
        label: String(body.label || cms.sections[section].tag),
        description: String(body.description || ''),
        color: String(body.color || 'red')
      });
      writeCms(cms);
      sendJson(response, 200, cms);
      return true;
    }

    if (request.method === 'POST' && url.pathname === '/api/products') {
      const body = await readJsonBody(request);
      cms.products.unshift({
        id: createId('product'),
        section: body.section === 'maker' ? 'maker' : 'wholesale',
        category: String(body.category || ''),
        title: String(body.title || 'Новый товар'),
        description: String(body.description || ''),
        price: Math.max(0, Number(body.price || 0)),
        color: String(body.color || 'red'),
        image: String(body.image || '')
      });
      writeCms(cms);
      sendJson(response, 200, cms);
      return true;
    }

    const deleteMatch = url.pathname.match(/^\/api\/(blog|reviews|products)\/([^/]+)$/);
    if (request.method === 'DELETE' && deleteMatch) {
      const [, collection, id] = deleteMatch;
      const result = removeById(cms[collection], decodeURIComponent(id));
      cms[collection] = result.next;
      writeCms(cms);
      sendJson(response, result.removed ? 200 : 404, cms);
      return true;
    }

    const categoryDeleteMatch = url.pathname.match(/^\/api\/categories\/(wholesale|maker)\/(.+)$/);
    if (request.method === 'DELETE' && categoryDeleteMatch) {
      const [, section, rawName] = categoryDeleteMatch;
      const name = decodeURIComponent(rawName);
      cms.sections[section].categories = cms.sections[section].categories.filter((item) => item.name !== name);
      cms.products = cms.products.filter((item) => !(item.section === section && item.category === name));
      writeCms(cms);
      sendJson(response, 200, cms);
      return true;
    }
  } catch (error) {
    sendJson(response, 400, { error: error.message });
    return true;
  }
  return false;
}

const server = http.createServer(async (request, response) => {
  const requestUrl = new URL(request.url, 'http://127.0.0.1');
  if (requestUrl.pathname.startsWith('/api/') && await handleApi(request, response, requestUrl)) return;

  const urlPath = decodeURIComponent(requestUrl.pathname);
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

server.listen(port, '127.0.0.1', () => {
  console.log(`Active Theory scene: http://127.0.0.1:${port}/`);
});
