// Propchain — "The Missing Layer". 2-minute film compositor.
// Layers: stock footage (frame sequences) -> 3D scene -> press windows -> UI -> fx.
// window.__seek(t) renders any frame deterministically (async: waits for image decode).
import { clamp, range, smooth, lerp, easeOutExpo, easeInCubic, easeOutCubic, easeInOutCubic, window01, rng } from '../src/util.js';
import * as Mod from './modules.js';

export const DURATION = 132.4;
// Act II gained a 7.4s human beat (Bloomberg, Detroit, Forbes). Everything authored
// after the old 51.4s mark shifts by SHIFT; items flagged {abs:true} are in final time.
const SHIFT_AT = 51.4, SHIFT = 7.4;
const sh = x => (x >= SHIFT_AT - 1e-6 ? x + SHIFT : x);
const FPS = 30;
const $ = id => document.getElementById(id);

// =====================================================================================
// EDIT DECISION LIST
// =====================================================================================
// stock: [t0, t1, clip, {off (s into clip), speed, z:[z0,z1], pan:[x0,y0,x1,y1], grade, fi, fo, dim}]
const STOCK = [
  // ACT I — THE PROMISE
  [0.0, 5.6, 'skyline', { z: [1.12, 1.2], grade: 'cine', fo: 0 }],
  [5.6, 7.3, 'traders', { z: [1.05, 1.12], grade: 'cine', dim: 0.55 }],
  [7.3, 9.0, 'keynote', { z: [1.1, 1.18], grade: 'cine', dim: 0.5 }],
  [9.0, 10.6, 'lighttrails', { z: [1.0, 1.1], grade: 'cine', dim: 0.5 }],
  [10.6, 11.9, 'phone', { z: [1.05, 1.12], grade: 'cine', dim: 0.55 }],
  [11.9, 12.5, 'heatmap', { z: [1.2, 1.3], grade: 'cine', dim: 0.35 }],
  [12.5, 13.8, 'towers', { z: [1.05, 1.15], grade: 'cine', dim: 0.55 }],
  [13.8, 14.9, 'audience', { z: [1.1, 1.16], grade: 'cine', dim: 0.5 }],
  [14.9, 15.4, 'lighttrails', { off: 2, z: [1.3, 1.4], grade: 'cine', dim: 0.3 }],
  [15.4, 16.5, 'applause', { z: [1.05, 1.1], grade: 'cine', dim: 0.5 }],
  [16.5, 17.0, 'heatmap', { off: 2, z: [1.3, 1.4], grade: 'cine', dim: 0.3 }],
  [17.0, 18.1, 'traders', { off: 2.5, z: [1.15, 1.2], grade: 'cine', dim: 0.5 }],
  [18.1, 18.6, 'phone', { off: 2.5, z: [1.3, 1.45], grade: 'cine', dim: 0.3 }],
  [18.6, 26.6, 'exec', { speed: 0.85, z: [1.04, 1.14], grade: 'cine', dim: 0.42, fi: 0.3 }],
  [26.6, 30.2, 'applause', { off: 0.5, speed: 0.4, z: [1.12, 1.18], grade: 'mono', dim: 0.3, blur: 6 }],
  // ACT II — THE REALITY
  [34.3, 41.0, 'rain', { speed: 0.7, z: [1.05, 1.12], grade: 'night', fi: 1.2, dim: 0.7 }],
  [41.0, 47.5, 'headinhands', { speed: 0.8, z: [1.06, 1.12], grade: 'night', dim: 0.3, fi: 0.4 }],
  [47.5, 51.35, 'emptyoffice', { speed: 0.8, z: [1.04, 1.1], grade: 'night', dim: 0.55, fi: 0.4 }],
  [51.4, 54.2, 'rain', { abs: true, off: 4.5, speed: 0.6, z: [1.1, 1.16], grade: 'night', dim: 0.45 }],
  [54.2, 58.6, 'nightdesk', { abs: true, speed: 0.8, z: [1.04, 1.1], grade: 'night', dim: 0.42 }],
  [58.6, 61.4, 'emptyoffice', { abs: true, off: 3.2, speed: 0.6, z: [1.1, 1.14], grade: 'night', dim: 0.45 }],
  // ACT III — THE ROOT CAUSE
  [54.0, 57.5, 'aerial', { z: [1.04, 1.12], grade: 'cine', dim: 0.62, fi: 0.5 }],
  [57.5, 59.5, 'buried', { z: [1.05, 1.1], grade: 'cine', dim: 0.6 }],
  [59.5, 61.6, 'filestack', { z: [1.08, 1.16], grade: 'cine', dim: 0.6 }],
  [66.4, 68.6, 'sitevisit', { z: [1.05, 1.1], grade: 'cine', dim: 0.35 }],
  [68.6, 70.4, 'signing', { z: [1.08, 1.14], grade: 'cine', dim: 0.35 }],
  [70.4, 73.6, 'boardroom', { z: [1.04, 1.1], grade: 'cine', dim: 0.35 }],
  [73.6, 79.0, 'algos', { speed: 0.9, z: [1.05, 1.12], grade: 'cine', dim: 0.3 }],
  // ACT V — THE AUTONOMOUS MARKET
  [106.0, 110.6, 'allocator', { z: [1.04, 1.1], grade: 'cine', dim: 0.5, fi: 0.5 }],
  [117.0, 120.0, 'citynight', { z: [1.05, 1.1], grade: 'cine', dim: 0.4, fi: 0.4 }],
];

// 3D scene: [t0, t1, sceneT0, sceneT1, {fi, fo, exp}]
const THREE_SHOTS = [
  [61.5, 66.5, 4.3, 9.3, { fi: 0.3, fo: 0.2 }],        // the paper storm + machine scan
  [85.4, 89.5, 8.4, 9.95, { fi: 0.6, fo: 0.0, exp: 0.55 }], // behind the ingestion console
  [89.5, 92.2, 10.35, 12.9, { fi: 0.0, fo: 0.0 }],     // snap: structured
  [92.2, 97.6, 12.9, 16.0, { fi: 0.0, fo: 0.0 }],      // attested
  [97.6, 102.6, 16.0, 18.4, { fi: 0.0, fo: 0.0 }],     // agent-ready
  [102.6, 106.0, 18.4, 21.6, { fi: 0.0, fo: 0.5 }],    // the city rebuilds
  [110.6, 117.2, 21.6, 26.0, { fi: 0.5, fo: 0.3 }],    // autonomous market
];

const W = 1280;
const CENTER = [320, 150];
const shiftO = o => {
  if (o.abs) return o;
  const r = { ...o, t0: sh(o.t0), t1: sh(o.t1) };
  if (o.subT != null) r.subT = sh(o.subT);
  if (o.hlT != null) r.hlT = sh(o.hlT);
  if (o.lines) r.lines = o.lines.map(l => (l.t != null ? { ...l, t: sh(l.t) } : l));
  if (o.keys) r.keys = o.keys.map(k => [sh(k[0]), ...k.slice(1)]);
  return r;
};
function buildCues(assets) {
  const HLS = assets.hls;
  const M = Object.fromEntries(Object.entries(Mod).map(([k, f]) => [k, (k === 'mk' || k === 'setRoot') ? f : (o, ...a) => f(shiftO(o), ...a)]));
  const P = (o) => M.press(o, assets);
  const cues = [
    // ---------------- ACT I — THE PROMISE
    M.chapter({ t0: 0.8, t1: 30.0, num: 'I', title: 'The promise' }),
    M.quote({ t0: 0.8, t1: 5.5, top: 330, size: 66, per: 0.1, text: 'The next generation for markets, the next generation for securities, will be tokenization of securities.', attrib: '<b>Larry Fink</b> · Chairman & CEO, BlackRock · NYT DealBook, Dec 2022', hi: [12, 13, 14] }),
    P({ t0: 5.6, t1: 7.3, img: 'decrypt.jpg', url: 'decrypt.co/116145/blackrock-ceo-says-next-generation…', from: [620, 170, 0.8, -14, 2], to: [360, 150, 0.86, -8, 1], cap: 'Decrypt · <b>Dec 1, 2022</b>', capPos: [132, 972] }),
    P({ t0: 7.3, t1: 9.0, img: 'addx.jpg', url: 'addx.co/insights/bcg-addx-report-asset-tokenization…', from: [60, 190, 0.8, 14, 2], to: [260, 150, 0.86, 7, 1], hl: [0, 0, 0, 0], cap: 'BCG × ADDX report · <b>Sep 2022</b>', capPos: [132, 972] }),
    M.counter({ t0: 9.0, t1: 10.6, keys: [[9.0, 0], [10.2, 16.1]], fmt: v => `$${v.toFixed(1)}<i>T</i>`, label: 'Tokenized assets by 2030 · BCG, 2022', style: { left: '132px', bottom: '160px' } }),
    P({ t0: 10.6, t1: 11.9, img: 'pk_cnbc24.jpg', url: 'cnbc.com/2024/01/12/blackrocks-larry-fink-says-bitcoin-etfs-are-just-the-first-step…', from: [700, 140, 0.8, -16, 0], to: [420, 150, 0.86, -9, 0], hl: HLS.cnbc24, hlT: 10.95, hlDur: 0.6, cap: 'CNBC · Larry Fink · <b>Jan 12, 2024</b>', capPos: [132, 972], snap: true }),
    M.slam({ t0: 11.9, t1: 12.5, word: 'TOKENIZATION' }),
    P({ t0: 12.5, t1: 13.8, img: 'stanchart.jpg', url: 'sc.com/en/press-release/trade-finance-to-play-substantial-role…', from: [0, 180, 0.8, 16, 0], to: [240, 150, 0.84, 9, 0], cap: 'Standard Chartered · <b>Jun 27, 2024</b>', capPos: [132, 972], snap: true }),
    M.counter({ t0: 13.8, t1: 14.9, keys: [[13.8, 16.1], [14.5, 30.1]], fmt: v => `$${v.toFixed(1)}<i>T</i>`, label: 'Tokenized assets by 2034 · Standard Chartered, 2024', style: { left: '132px', bottom: '160px' } }),
    M.slam({ t0: 14.9, t1: 15.4, word: 'EVERY ASSET', color: '#FFBE06' }),
    P({ t0: 15.4, t1: 16.5, img: 'pk_deloitte.jpg', url: 'coindesk.com/markets/2025/04/24/global-tokenized-real-estate-market-could-explode-to-4t…', from: [640, 160, 0.8, -12, 0], to: [380, 150, 0.86, -6, 0], cap: 'CoinDesk · Deloitte forecast · <b>Apr 24, 2025</b>', capPos: [132, 972], snap: true }),
    M.slam({ t0: 16.5, t1: 17.0, word: 'TOKENIZED' }),
    P({ t0: 17.0, t1: 18.1, img: 'pk_dubai.jpg', url: 'dubailand.gov.ae/en/news-media/dld-launches-the-mena-s-first-tokenized-real-estate-project…', from: [40, 170, 0.8, 12, 0], to: [260, 150, 0.86, 6, 0], hl: HLS.dubai, hlT: 17.3, hlDur: 0.5, cap: 'Dubai Land Department · <b>May 25, 2025</b>', capPos: [132, 972], snap: true }),
    M.slam({ t0: 18.1, t1: 18.6, word: 'TRILLIONS', color: '#FFBE06' }),
    P({ t0: 18.6, t1: 22.6, img: 'blackrock_quote.jpg', url: 'blackrock.com/corporate/investor-relations/2025-larry-fink-annual-chairmans-letter', bgpos: '-120px -253px', bgsize: '2000px auto', from: [330, 200, 0.9, -6, 3], to: [300, 150, 0.98, -2, 0], drift: 0.14, hl: [74, 352, 670, 38], hlT: 19.7, cap: 'Larry Fink · <b>2025 Annual Chairman’s Letter</b>', capPos: [132, 972] }),
    M.quote({ t0: 22.6, t1: 26.6, top: 360, size: 72, per: 0.13, text: 'Markets wouldn’t need to close. Transactions that currently take days would clear in seconds.', attrib: '<b>Larry Fink</b> · 2025 Annual Chairman’s Letter' }),
    P({ t0: 26.6, t1: 30.2, img: 'pk_cnbc25.jpg', hl: HLS.cnbc25, hlT: 27.6, hlDur: 0.9, url: 'cnbc.com/2025/04/12/tokenization-stock-bond-real-estate-trading-market-coming-blackrock.html', outlet: 'CNBC', headline: 'Tokenization of the market, from stocks to bonds to real estate is coming, says BlackRock CEO Larry Fink, <span style="background:rgba(255,190,6,.55)">if we can solve one problem</span>', date: 'APR 12, 2025', from: [320, 190, 0.84, 0, 4], to: [320, 150, 0.9, 0, 0], drift: 0.1, out: 0.05, cap: 'CNBC · <b>Apr 12, 2025</b>', capPos: [132, 972] }),
    // ---------------- ACT II — THE REALITY
    M.chapter({ t0: 31.6, t1: 54.0, num: 'II', title: 'The reality' }),
    M.title({ t0: 31.8, t1: 34.3, pos: 'c', size: 'h-l', lines: [{ segs: [['Four years later.']] }] }),
    M.counter({ t0: 34.6, t1: 40.8, size: 280, keys: [[34.6, 16100], [36.0, 16100], [37.3, 27, easeInCubic]],
      fmt: v => v >= 1000 ? `$${(v / 1000).toFixed(1)}<i>T</i>` : `$${Math.round(v)}<i>B</i>`,
      label: t => t < 36.4 ? 'The forecast · tokenized by 2030' : 'What arrived · tradeable on-chain value, mid 2026 · <b style="color:#FFBE06;font-weight:500">under 0.2% of the forecast</b>',
      shake: t => t > 37.2 && t < 37.8 ? 6 * Math.exp(-(t - 37.2) * 8) : 0, style: { left: '132px', bottom: '170px' } }),
    M.assetChart({ t0: 41.0, t1: 47.4 }),
    M.title({ t0: 47.6, t1: 51.35, pos: 'll', size: 'h-l', lines: [{ segs: [['$1 on-chain for every', '']] }, { segs: [['$2 million', 'yl'], [' of real estate.', '']] }], sub: 'The largest asset class. The lowest penetration.' }),
    P({ abs: true, t0: 51.4, t1: 54.2, img: 'pk_bloomberg.jpg', dark: true, url: 'finance.yahoo.com/news/tokenization-become-wall-street-latest-favorite-crypto-buzzword…', from: [360, 200, 0.84, -6, 3], to: [300, 150, 0.92, -2, 0], drift: 0.12, hl: HLS.bloomberg, hlT: 52.0, hlDur: 1.1, cap: 'Bloomberg (via Yahoo Finance) · <b>Dec 27, 2024</b>', capPos: [132, 972] }),
    P({ abs: true, t0: 54.2, t1: 56.4, img: 'pk_detroit1.jpg', url: 'outliermedia.org/detroit-sues-realt-crypto-landlord-blight…', from: [300, 190, 0.84, 6, 3], to: [330, 150, 0.9, 2, 0], drift: 0.1, cap: 'Outlier Media, Detroit · <b>Jul 2, 2025</b>', capPos: [132, 972] }),
    P({ abs: true, t0: 56.4, t1: 58.6, img: 'pk_detroit2.jpg', url: 'outliermedia.org/realt-detroit-model-no-longer-works…', from: [340, 190, 0.84, -6, 3], to: [310, 150, 0.9, -2, 0], drift: 0.1, cap: 'Outlier Media, Detroit · <b>Mar 17, 2026</b>', capPos: [132, 972] }),
    P({ abs: true, t0: 58.6, t1: 59.9, img: 'pk_forbes.jpg', url: 'forbes.com/sites/digital-assets/2026/05/26/why-tokenized-real-estate-still-hasnt-taken-off/', from: [320, 170, 0.86, 0, 3], to: [320, 150, 0.9, 0, 0], cap: 'Forbes · <b>May 26, 2026</b>', capPos: [132, 972], snap: true }),
    P({ abs: true, t0: 59.9, t1: 61.4, img: 'pk_forbes2.jpg', url: 'forbes.com/sites/digital-assets/2026/05/26/why-tokenized-real-estate-still-hasnt-taken-off/', from: [320, 150, 0.9, 0, 0], to: [300, 140, 0.98, 0, 0], drift: 0.08, hl: HLS.forbes2, hlT: 60.0, hlDur: 1.0, cap: 'Forbes · <b>May 26, 2026</b>', capPos: [132, 972] }),
    // ---------------- ACT III — THE ROOT CAUSE
    M.chapter({ t0: 54.2, t1: 79.0, num: 'III', title: 'The root cause' }),
    M.title({ t0: 54.3, t1: 57.4, pos: 'll', size: 'h-xl', eyebrow: 'Real estate', lines: [{ segs: [['$380 trillion.', '']] }], sub: 'The largest asset class on earth.' }),
    M.title({ t0: 57.6, t1: 61.4, pos: 'll', size: 'h-l', lines: [{ segs: [['Still run on PDFs,', '']] }, { segs: [['spreadsheets and paper.', '']] }] }),
    M.title({ t0: 61.9, t1: 66.3, pos: 'll', size: 'h-m', lines: [{ segs: [['Every buyer re-verifies the asset.', '']] }, { segs: [['From scratch.', 'yl']], t: 63.2 }], sub: 'Scans in local languages. Excel as system of record. Registries that never talk to each other.', subT: 63.8 }),
    M.chain({ t0: 66.5, t1: 73.5 }),
    M.split({ t0: 73.7, t1: 78.9 }),
    M.title({ t0: 79.2, t1: 82.2, pos: 'c', size: 'h-l', lines: [{ segs: [['The token was never the problem.', '']], t: 79.3 }, { segs: [['The data was.', 'yl']], t: 80.6 }] }),
    // ---------------- ACT IV — THE LAYER
    M.endcard({ t0: 82.4, t1: 85.6, tag: 'The data layer beneath institutional real estate.', tri: false }),
    M.chapter({ t0: 85.6, t1: 106.0, num: 'IV', title: 'The missing layer' }),
    M.ingest({ t0: 85.6, t1: 89.5 }),
    M.title({ t0: 89.7, t1: 92.1, pos: 'll', size: 'h-l', eyebrow: 'Layer 01 · Structuring engine', lines: [{ segs: [['Structured.', '']] }], sub: 'Every source, one machine-readable schema, with full lineage.' }),
    M.title({ t0: 92.3, t1: 97.5, pos: 'll', size: 'h-l', eyebrow: 'Layer 02 · Validation engine', lines: [{ segs: [['Attested.', '']] }], sub: 'Origin, permission and state: provable by anyone, on chain.' }),
    M.proofs({ t0: 92.8, t1: 97.5 }),
    M.title({ t0: 97.7, t1: 102.5, pos: 'll', size: 'h-l', eyebrow: 'Layer 03 · Know your agent', lines: [{ segs: [['Agent-ready.', '']] }], sub: 'Every AI agent identified, permissioned and audited.' }),
    M.kya({ t0: 98.1, t1: 102.5 }),
    M.title({ t0: 102.9, t1: 105.9, pos: 'c', size: 'h-m', lines: [{ segs: [['Structure first.', '']] }, { segs: [['Trust follows from lineage.', 'yl']], t: 103.8 }] }),
    // ---------------- ACT V — THE AUTONOMOUS MARKET
    M.chapter({ t0: 106.1, t1: 119.8, num: 'V', title: 'The autonomous market' }),
    M.mandate({ t0: 106.3, t1: 110.5 }),
    M.deal({ t0: 110.7, t1: 116.9, gap: 0.95 }),
    M.title({ t0: 111.2, t1: 116.9, pos: 'll', size: 'h-m', style: { width: '900px' }, lines: [{ segs: [['From months of paper', '']] }, { segs: [['to minutes of software.', 'yl']], t: 112.0 }] }),
    M.stats({ t0: 117.1, t1: 119.8 }),
    M.endcard({ t0: 120.2, t1: 125.0 }),
  ];
  return cues;
}

for (const s of STOCK) if (!s[3].abs) { s[0] = sh(s[0]); s[1] = sh(s[1]); }
for (const s of THREE_SHOTS) { s[0] = sh(s[0]); s[1] = sh(s[1]); }

// letterbox height keyframes (per bar): film look until the reveal
const BARS = [[0, 70], [82.2, 70], [84.2, 0], [125, 0]];
// fade-to-black keyframes
const BLACK = [[0, 1], [1.3, 0], [30.15, 0], [30.2, 1], [31.6, 1], [31.8, 0], [124.3, 0], [125, 1]];

// white flashes (t, strength)
const FLASH = [[11.9, 0.35], [14.9, 0.3], [16.5, 0.3], [18.1, 0.3], [37.25, 0.12], [80.6, 0.08], [89.8, 0.18], [82.4, 0.06]];
for (const K of [BARS, BLACK, FLASH]) for (const k of K) k[0] = sh(k[0]);

// film grade per shot
const GRADES = {
  cine: 'contrast(1.12) saturate(0.78) brightness(0.92)',
  mono: 'grayscale(0.9) contrast(1.2) brightness(0.8)',
  night: 'saturate(0.6) contrast(1.15) brightness(0.72) hue-rotate(-6deg)',
};

// =====================================================================================
// ENGINE
// =====================================================================================
let three = null, cues = [], manifest = {}, grainTiles = [];
const imgs = [];
const kf = (K, t) => { if (t <= K[0][0]) return K[0][1]; for (let i = 0; i < K.length - 1; i++) { const [a, va] = K[i], [b, vb] = K[i + 1]; if (t <= b) return lerp(va, vb, smooth(range(t, a, b))); } return K[K.length - 1][1]; };

function frameUrl(clip, n) { return `stock/clips/${clip}/f_${String(n + 1).padStart(4, '0')}.jpg`; }

async function drawStock(t) {
  const active = STOCK.filter(s => t >= s[0] - 0.001 && t < s[1] + (s[3].fo ?? 0));
  const jobs = [];
  imgs.forEach((im, k) => {
    const s = active[k];
    if (!s) { im.style.display = 'none'; return; }
    const [t0, t1, clip, o] = s;
    im.style.display = 'block';
    const m = manifest[clip];
    const u = range(t, t0, t1);
    const z = o.z ? lerp(o.z[0], o.z[1], easeInOutCubic(u) * 0.3 + u * 0.7) : 1.05;
    const pan = o.pan ? [lerp(o.pan[0], o.pan[2], u), lerp(o.pan[1], o.pan[3], u)] : [0, 0];
    const fi = o.fi ? smooth(range(t, t0, t0 + o.fi)) : 1;
    im.style.opacity = fi;
    im.style.zIndex = String(k);
    im.style.transform = `translate(${pan[0]}px, ${pan[1]}px) scale(${z})`;
    im.style.filter = `${GRADES[o.grade || 'cine']} brightness(${o.dim ?? 1})${o.blur ? ` blur(${o.blur}px)` : ''}`;
    if (!m) { im.removeAttribute('src'); im.alt = clip; return; }
    const n = Math.floor(((t - t0) * (o.speed ?? 1) + (o.off ?? 0)) * FPS);
    const f = Math.max(0, Math.min(m.frames - 1, n));
    const url = frameUrl(clip, f);
    if (im.dataset.src !== url) { im.dataset.src = url; im.src = url; jobs.push(im.decode().catch(() => {})); }
  });
  await Promise.all(jobs);
}

function drawThree(t) {
  const s = THREE_SHOTS.find(s => t >= s[0] && t < s[1]);
  const c = $('gl');
  if (!s || !three) { c.style.opacity = 0; return; }
  const [t0, t1, a, b, o] = s;
  const t3 = lerp(a, b, range(t, t0, t1));
  const op = (o.fi ? smooth(range(t, t0, t0 + o.fi)) : 1) * (o.fo ? 1 - smooth(range(t, t1 - o.fo, t1)) : 1);
  c.style.opacity = op;
  three.seek(t3, { fade: 1, exp: o.exp ?? 1, grain: 0.03 });
}

function drawFx(t) {
  const bh = kf(BARS, t);
  document.querySelectorAll('#bars .bar').forEach(b => b.style.height = bh + 'px');
  $('black').style.opacity = kf(BLACK, t);
  let f = 0; for (const [ft, s] of FLASH) if (t >= ft) f = Math.max(f, s * Math.exp(-(t - ft) * 9));
  $('flash').style.opacity = f;
  const fr = Math.floor(t * FPS);
  $('grain').style.backgroundImage = `url(${grainTiles[fr % grainTiles.length]})`;
  $('grain').style.backgroundPosition = `${(fr * 73) % 512}px ${(fr * 151) % 512}px`;
}

async function seek(t) {
  await drawStock(t);
  drawThree(t);
  for (const c of cues) c.update(t);
  drawFx(t);
}

function makeGrain() {
  const r = rng(99);
  for (let k = 0; k < 8; k++) {
    const c = document.createElement('canvas'); c.width = c.height = 512;
    const g = c.getContext('2d'), d = g.createImageData(512, 512);
    for (let i = 0; i < d.data.length; i += 4) { const v = 128 + (r() + r() + r() - 1.5) * 90; d.data[i] = d.data[i + 1] = d.data[i + 2] = v; d.data[i + 3] = 255; }
    g.putImageData(d, 0, 0); grainTiles.push(c.toDataURL('image/png'));
  }
}

async function boot() {
  await document.fonts.ready;
  await Promise.all(['300 20px Inter', '400 20px Inter', '500 20px Inter', '600 20px Inter', '400 20px Mono', '500 20px Mono'].map(f => document.fonts.load(f)));
  manifest = await fetch('stock/manifest.json').then(r => r.json()).catch(() => ({}));
  const pressFiles = ['decrypt.jpg', 'addx.jpg', 'stanchart.jpg', 'blackrock_quote.jpg', ...['cnbc24', 'cnbc25', 'dubai', 'deloitte', 'bloomberg', 'detroit1', 'detroit2', 'forbes', 'forbes2'].map(n => `pk_${n}.jpg`)];
  const hls = await fetch('press/pk_highlights.json').then(r => r.json()).catch(() => ({}));
  const press = new Set();
  await Promise.all(pressFiles.map(f => fetch('press/' + f, { method: 'HEAD' }).then(r => r.ok && press.add(f)).catch(() => {})));
  await Promise.all([...press].map(f => new Promise(res => { const i = new Image(); i.onload = i.onerror = res; i.src = 'press/' + f; })));
  for (let k = 0; k < 3; k++) { const im = document.createElement('img'); im.decoding = 'sync'; $('stock').appendChild(im); imgs.push(im); }
  makeGrain();
  Mod.setRoot($('ui'));
  cues = buildCues({ press, hls });
  // press windows sit on their own layer beneath the type
  cues.forEach(c => { if (c.el.querySelector?.('.pwin')) $('press').appendChild(c.el); });
  three = await import('../src/main.js');
  await three.readyP;
  await seek(0);
}

window.__duration = DURATION;
window.__seek = seek;
window.__ready = boot();
const qs = new URLSearchParams(location.search);
window.__ready.then(() => {
  if (qs.has('t')) seek(parseFloat(qs.get('t')));
  if (qs.has('play')) { const t0 = performance.now() - (parseFloat(qs.get('play')) || 0) * 1000; const loop = async () => { await seek(((performance.now() - t0) / 1000) % DURATION); requestAnimationFrame(loop); }; loop(); }
});
