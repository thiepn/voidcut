import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const HOST = '127.0.0.1';
const PORT = 4173;
const OFFLINE_SENTINEL = path.join(ROOT, '.f23-origin-offline');

const CONTENT_TYPES = new Map([
  ['.html', 'text/html; charset=utf-8'],
  ['.js', 'text/javascript; charset=utf-8'],
  ['.mjs', 'text/javascript; charset=utf-8'],
  ['.css', 'text/css; charset=utf-8'],
  ['.json', 'application/json; charset=utf-8'],
  ['.webmanifest', 'application/manifest+json; charset=utf-8'],
  ['.svg', 'image/svg+xml'],
  ['.png', 'image/png'],
  ['.ico', 'image/x-icon'],
]);

async function exists(file) {
  try { await fs.access(file); return true; } catch { return false; }
}

function safePath(urlPath) {
  let decoded;
  try { decoded = decodeURIComponent(urlPath); } catch { return null; }
  const pathname = decoded === '/' ? '/index.html' : decoded;
  const candidate = path.resolve(ROOT, `.${pathname}`);
  return candidate === ROOT || candidate.startsWith(`${ROOT}${path.sep}`) ? candidate : null;
}

const server = http.createServer(async (req, res) => {
  if (await exists(OFFLINE_SENTINEL)) {
    req.socket.destroy();
    return;
  }

  const url = new URL(req.url || '/', `http://${HOST}:${PORT}`);
  const file = safePath(url.pathname);
  if (!file) {
    res.writeHead(403, { 'Cache-Control': 'no-store' });
    res.end('Forbidden');
    return;
  }

  try {
    const stat = await fs.stat(file);
    if (!stat.isFile()) throw new Error('not-file');
    const body = await fs.readFile(file);
    res.writeHead(200, {
      'Content-Type': CONTENT_TYPES.get(path.extname(file).toLowerCase()) || 'application/octet-stream',
      'Content-Length': body.length,
      'Cache-Control': 'no-store',
    });
    if (req.method === 'HEAD') res.end();
    else res.end(body);
  } catch {
    res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8', 'Cache-Control': 'no-store' });
    res.end('Not found');
  }
});

server.listen(PORT, HOST, () => {
  console.log(`VOIDCUT PWA test server listening on http://${HOST}:${PORT}`);
});

for (const signal of ['SIGINT', 'SIGTERM']) {
  process.on(signal, () => server.close(() => process.exit(0)));
}
