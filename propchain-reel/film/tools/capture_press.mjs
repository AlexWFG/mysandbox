// Capture clean article screenshots (headline area) for the press montage.
// node film/tools/capture_press.mjs            -> film/press/<id>.jpg
import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';

const OUT = path.join(path.dirname(new URL(import.meta.url).pathname), '..', 'press');
fs.mkdirSync(OUT, { recursive: true });
const TARGETS = {
  decrypt: 'https://decrypt.co/116145/blackrock-ceo-says-next-generationmarkets-is-tokenization',
  addx: 'https://addx.co/insights/bcg-addx-report-asset-tokenization-to-grow-50x-into-us-16-trillion-opportunity-by-2030/',
  ledger: 'https://www.ledgerinsights.com/bcg-addx-estimate-asset-tokenization-to-reach-16-trillion-by-2030/',
  securitize: 'https://investors.securitize.io/news/news-details/2024/BlackRock-Launches-Its-First-Tokenized-Fund-BUIDL-on-the-Ethereum-Network-03-20-2024/default.aspx',
  stanchart: 'https://www.sc.com/en/press-release/trade-finance-to-play-substantial-role-in-usd-30-1-trillion-tokenised-real-world-assets-market-by-2034/',
  coindesk: 'https://www.coindesk.com/business/2025/06/26/real-world-asset-tokenization-market-has-grown-almost-fivefold-in-3-years',
  blackrock: 'https://www.blackrock.com/corporate/investor-relations/2025-larry-fink-annual-chairmans-letter',
  kitco: 'https://www.kitco.com/news/article/2024-07-02/blockchain-not-bitcoin-tokenized-assets-hit-30-trillion-2034-standard',
};
const only = process.argv.slice(2);
const b = await chromium.launch({ channel: 'chromium', proxy: process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY } : undefined });
const ctx = await b.newContext({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 2, locale: 'en-US',
  userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36' });
for (const [id, url] of Object.entries(TARGETS)) {
  if (only.length && !only.includes(id)) continue;
  const p = await ctx.newPage();
  try {
    const r = await p.goto(url, { waitUntil: 'domcontentloaded', timeout: 40000 });
    await p.waitForTimeout(4000);
    // consent / modal buttons
    for (const label of ['Accept all', 'Accept All', 'Accept', 'I agree', 'Agree', 'Got it', 'OK', 'Allow all', 'Continue', 'Close']) {
      const btn = p.getByRole('button', { name: label, exact: true }).first();
      if (await btn.isVisible().catch(() => false)) { await btn.click({ timeout: 2000 }).catch(() => {}); await p.waitForTimeout(700); }
    }
    // remove leftover fixed/sticky overlays except the site header
    await p.evaluate(() => {
      for (const el of document.querySelectorAll('body *')) {
        const cs = getComputedStyle(el);
        if ((cs.position === 'fixed' || cs.position === 'sticky') && el.getBoundingClientRect().top > 120) el.remove();
        if (cs.position === 'fixed' && parseInt(cs.zIndex || '0') > 1000 && el.getBoundingClientRect().height > 300) el.remove();
      }
      document.querySelectorAll('iframe, ins, [id*="google_ads"], [class*="advert"], [class*="ad-slot"], [class*="AdSlot"], [data-ad], [id^="ad-"]').forEach(e => e.remove());
      document.documentElement.style.overflow = 'auto'; document.body.style.overflow = 'auto';
    });
    await p.waitForTimeout(500);
    await p.screenshot({ path: path.join(OUT, `${id}.jpg`), type: 'jpeg', quality: 88 });
    await p.screenshot({ path: path.join(OUT, `${id}_full.jpg`), type: 'jpeg', quality: 80, fullPage: true, clip: undefined }).catch(() => {});
    console.log(r.status(), id, (await p.title()).slice(0, 80));
  } catch (e) { console.log('ERR', id, e.message.slice(0, 90)); }
  await p.close();
}
await b.close();
