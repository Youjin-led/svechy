const http = require('http');
const fs = require('fs');
const path = require('path');

const root = process.argv[2];
const port = Number(process.argv[3] || 5210);

const types = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.ico': 'image/x-icon',
  '.xml': 'application/xml; charset=utf-8',
  '.txt': 'text/plain; charset=utf-8',
  '.php': 'text/plain; charset=utf-8',
};

http.createServer((req, res) => {
  const url = new URL(req.url, `http://127.0.0.1:${port}`);
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
}).listen(port, '127.0.0.1', () => {
  console.log(`Serving ${root} at http://127.0.0.1:${port}/`);
});
