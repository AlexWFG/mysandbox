import { chromium } from 'playwright';
const urls = process.argv.slice(2);
const b = await chromium.launch({ channel: 'chromium', proxy: process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY } : undefined });
const ctx = await b.newContext({ viewport:{width:1440,height:900}, deviceScaleFactor:2, userAgent:'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36' });
for (const [i,u] of urls.entries()) {
  const p = await ctx.newPage();
  try { const r = await p.goto(u,{waitUntil:'domcontentloaded',timeout:30000}); await p.waitForTimeout(3500);
    await p.screenshot({path:`research/s${i}.jpg`,quality:80,type:'jpeg'}); console.log(r.status(), u, (await p.title()).slice(0,90)); }
  catch(e){ console.log('ERR',u,e.message.slice(0,80)); }
  await p.close();
}
await b.close();
