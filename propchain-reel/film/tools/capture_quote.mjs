// Capture a specific quoted passage on a page, scrolled to center: node capture_quote.mjs id url "text snippet"
import { chromium } from 'playwright';
const [id, url, snippet] = process.argv.slice(2);
const b = await chromium.launch({ channel: 'chromium', proxy: process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY } : undefined });
const ctx = await b.newContext({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 2,
  userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36' });
const p = await ctx.newPage();
await p.goto(url, { waitUntil: 'domcontentloaded', timeout: 40000 });
await p.waitForTimeout(4000);
for (const sel of ['text=Accept', 'button:has-text("Accept")', 'a:has-text("Accept")', '#onetrust-accept-btn-handler']) {
  const el = p.locator(sel).first(); if (await el.isVisible().catch(() => false)) { await el.click().catch(() => {}); await p.waitForTimeout(1200); break; }
}
await p.evaluate(() => { for (const el of document.querySelectorAll('body *')) { const cs = getComputedStyle(el); if (cs.position === 'fixed' && el.getBoundingClientRect().top > 100) el.remove(); } });
await p.screenshot({ path: `film/press/${id}.jpg`, type: 'jpeg', quality: 88 });
if (snippet) {
  const loc = p.getByText(snippet, { exact: false }).first();
  await loc.scrollIntoViewIfNeeded(); await loc.evaluate(e => e.scrollIntoView({ block: 'center' }));
  await p.waitForTimeout(800);
  await p.evaluate(() => { for (const el of document.querySelectorAll('body *')) { const cs = getComputedStyle(el); if (cs.position === 'fixed' || cs.position === 'sticky') el.style.visibility = 'hidden'; } });
  const box = await loc.boundingBox(); console.log('quote box', JSON.stringify(box));
  await p.screenshot({ path: `film/press/${id}_quote.jpg`, type: 'jpeg', quality: 90 });
}
console.log('ok', id, await p.title());
await b.close();
