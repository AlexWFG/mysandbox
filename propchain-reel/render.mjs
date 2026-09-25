// Frame-accurate renderer: serves the project, drives window.__seek(t) in
// headless Chromium and captures each frame.
//   node render.mjs stills 0.5 4.2 12        -> out/stills/t_XX.jpg
//   node render.mjs frames --workers 4       -> out/frames/f_00000.jpg ...
import { chromium } from 'playwright';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.dirname(new URL(import.meta.url).pathname);
const fpsArg = process.argv.indexOf('--fps');
const FPS = fpsArg > 0 ? parseInt(process.argv[fpsArg + 1]) : 30;
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.svg': 'image/svg+xml', '.jpg': 'image/jpeg', '.png': 'image/png', '.woff2': 'font/woff2', '.json': 'application/json' };

function serve() {
  return new Promise(res => {
    const srv = http.createServer((req, rsp) => {
      const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
      if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { rsp.writeHead(404); return rsp.end(); }
      rsp.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' });
      fs.createReadStream(p).pipe(rsp);
    }).listen(0, () => res(srv));
  });
}

async function openPage(port) {
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--disable-gpu-vsync'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') console.log('[page]', m.text()); });
  page.on('pageerror', e => console.log('[pageerror]', e.message));
  await page.goto(`http://localhost:${port}/index.html`);
  await page.waitForFunction(() => window.__ready !== undefined, null, { timeout: 60000 });
  await page.evaluate(() => window.__ready);
  return { browser, page };
}

async function shoot(page, t, file) {
  await page.evaluate(t => window.__seek(t), t);
  await page.screenshot({ path: file, type: 'jpeg', quality: 96, clip: { x: 0, y: 0, width: 1920, height: 1080 } });
}

const [mode, ...rest] = process.argv.slice(2);
const srv = await serve();
const port = srv.address().port;

if (mode === 'stills') {
  const dir = path.join(ROOT, 'out/stills'); fs.mkdirSync(dir, { recursive: true });
  const { browser, page } = await openPage(port);
  for (const a of rest) {
    const t = parseFloat(a); const t0 = Date.now();
    await shoot(page, t, path.join(dir, `t_${t.toFixed(2).padStart(5, '0')}.jpg`));
    console.log(`t=${t} ${Date.now() - t0}ms`);
  }
  await browser.close();
} else if (mode === 'frames') {
  const wi = rest.indexOf('--workers'); const workers = wi >= 0 ? parseInt(rest[wi + 1]) : 4;
  const fi = rest.indexOf('--from'); const from = fi >= 0 ? parseInt(rest[fi + 1]) : 0;
  const ti = rest.indexOf('--to'); const total = ti >= 0 ? parseInt(rest[ti + 1]) : 30 * FPS;
  const dir = path.join(ROOT, 'out/frames'); fs.mkdirSync(dir, { recursive: true });
  let next = from, done = 0; const t0 = Date.now();
  await Promise.all([...Array(workers)].map(async () => {
    const { browser, page } = await openPage(port);
    // warm-up so every worker starts from an identical state
    await page.evaluate(() => window.__seek(0));
    while (next < total) {
      const f = next++;
      const file = path.join(dir, `f_${String(f).padStart(5, '0')}.jpg`);
      if (fs.existsSync(file)) { done++; continue; }
      await shoot(page, f / FPS, file);
      done++;
      if (done % 30 === 0) { const el = (Date.now() - t0) / 1000; console.log(`${done}/${total - from} frames  ${(el / done).toFixed(2)}s/frame  eta ${((total - from - done) * el / done / 60).toFixed(1)}min`); }
    }
    await browser.close();
  }));
}
srv.close();
