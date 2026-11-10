// servidor local com gzip e URLs limpas, como a Vercel serve
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path'; import zlib from 'node:zlib';
const raiz = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..'), porta = +process.argv[2] || 4230;
const tipos = {'.html':'text/html; charset=utf-8','.css':'text/css','.js':'text/javascript','.svg':'image/svg+xml','.webp':'image/webp','.png':'image/png','.jpg':'image/jpeg','.ico':'image/x-icon','.woff2':'font/woff2','.txt':'text/plain; charset=utf-8','.xml':'application/xml'};
http.createServer((req, res) => {
  let u = decodeURIComponent(req.url.split('?')[0]); if (u.endsWith('/')) u += 'index.html';
  let f = path.join(raiz, u); if (!path.extname(f) && fs.existsSync(f + '.html')) f += '.html';
  if (!f.startsWith(raiz) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404, {'content-type': tipos['.html']}); return res.end(fs.readFileSync(path.join(raiz, '404.html'))); }
  const ext = path.extname(f), corpo = fs.readFileSync(f), zip = /\.(html|css|js|svg|txt|xml)$/.test(ext) && /gzip/.test(req.headers['accept-encoding'] || '');
  res.writeHead(200, {'content-type': tipos[ext] || 'application/octet-stream', 'cache-control': ext === '.html' ? 'no-cache' : 'max-age=3600', ...(zip ? {'content-encoding': 'gzip'} : {}), 'connection': 'keep-alive'});
  res.end(zip ? zlib.gzipSync(corpo) : corpo);
}).listen(porta, () => console.log('rotoragro em http://localhost:' + porta));
