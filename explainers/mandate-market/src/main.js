// The Mandate Market — explainer film. window.__seek(t) renders any frame deterministically.
import { T, h, s, svg, box, I, loadIcons, scene, scenes, runScenes, rise, fade, draw, pulseDot, pr, e3, eo, clamp, Y } from './core.js';
import ch1 from './ch1.js';
import ch2 from './ch2.js';
import ch3 from './ch3.js';
import ch4 from './ch4.js';
import ch5 from './ch5.js';
import ch6 from './ch6.js';

const ICONS = ['warehouse', 'building-2', 'building', 'hotel', 'store', 'landmark', 'file-check', 'clock', 'gauge', 'target', 'funnel', 'scale',
  'shield-check', 'lock', 'user-check', 'badge-check', 'handshake', 'activity', 'refresh-cw', 'eye-off', 'eye', 'layers', 'file-text', 'banknote',
  'percent', 'trending-down', 'trending-up', 'circle-check', 'circle-x', 'x', 'check', 'arrow-right', 'history', 'timer', 'bot', 'scan-search',
  'sliders-horizontal', 'crosshair', 'git-merge', 'repeat', 'zap', 'radio', 'square-stack'];

let pending = [];
let chapters = [];
let grainFrames = [], gctx, gridCtx;

window.__ready = (async () => {
  const tl = await (await fetch('timeline.json')).json(); T.init(tl);
  const man = await (await fetch('stock/manifest.json')).json();
  await loadIcons(ICONS);
  await Promise.all(['300 20px Inter', '400 20px Inter', '500 20px Inter', '600 20px Inter', '500 20px JBM', '400 20px JBM'].map(f => document.fonts.load(f)));
  const logo = await (await fetch('assets/logo-white.svg')).text();

  bg(); grain();

  // ---------------------------------------------------------------- stock inserts
  const stock = (name, t0, t1, eyebrow, line, o = {}) => {
    const N = man[name].frames; const off = o.off || 0;
    const sc = scene(t0, t1, (t, lt) => {
      const f = clamp(Math.floor((lt + off) * 30) + 1, 1, N);
      const src = `stock/clips/${name}/f_${String(f).padStart(4, '0')}.jpg`;
      if (img.__src !== src) { img.src = src; img.__src = src; pending.push(img); }
      img.style.transform = `scale(${1.04 + lt * (o.push ?? .012)})`;
      if (cap) rise(cap, t, t0 + .35, { dx: -30, dy: 0 });
    }, { parent: document.getElementById('stock'), fi: o.fi ?? .5, fo: o.fo ?? .5 });
    const wrap = h('div.stockwrap', {}, sc.el);
    const img = h('img', {}, wrap); h('div.shade', {}, wrap);
    const cap = eyebrow ? box(sc.el, 140, 0, 'stockcap', `<div class="eyebrow y">${eyebrow}</div><div class="head" style="margin-top:18px">${line}</div>`, { top: 'auto' }) : null;
    return sc;
  };
  const W = T.W.bind(T), L = T.L.bind(T), E = T.E.bind(T);
  stock('trading', 4.9, W('01', 'that') - .15, 'Today · the order book', 'Identical shares, one price axis.');
  stock('warehouse', L('07') - 1.0, W('07', 'hard') - .1, 'Mandate M-0417', 'Logistics · Germany');
  stock('lenders', L('13') - 1.3, W('13', 'they') - .15, 'Object 03 · the debt layer', 'Lenders quote the pair.');
  stock('handshake', W('23', 'so') - .25, E('23') + .7, 'Stable', 'No reason to go around the platform.');
  stock('city', E('27') + 2.0, T.duration + 1, null, null, { push: .006, fi: 1.2 });

  // ---------------------------------------------------------------- title
  const title = scene(0, 4.6, (t) => {
    rise(tLogo, t, .15, { dy: 0, dx: -20 });
    rise(tEy, t, .45); rise(tH, t, .65, { dy: 34 }); rise(tSub, t, 1.1);
    ['a', 'm', 'c'].forEach((k, i) => rise(nodes[k], t, 1.3 + i * .3, { dy: 0, scale: .15 }));
    draw(lAM, t, 2.2, .9); draw(lMC, t, 2.5, .9); draw(lCA, t, 2.8, .9);
    pd.at(lAM, pr(t, 3.0, 1.2, e3)); pd2.at(lMC, pr(t, 3.4, 1.2, e3));
  }, { fi: .01, fo: .7 });
  const tLogo = box(title.el, 140, 130, '', logo, { width: '230px' });
  const tEy = box(title.el, 140, 390, 'eyebrow y', 'The market layer · concept note');
  const tH = box(title.el, 132, 430, 'big', 'The Mandate Market', { fontSize: '120px' });
  const tSub = box(title.el, 140, 590, 'sub', 'How capital, assets and credit find each other<br>on attested data — the matching engine, mechanically.', { fontSize: '30px' });
  const ts = svg(title.el);
  const P = { a: [1340, 360], m: [1640, 560], c: [1360, 760] };
  const lAM = s('path', { d: `M${P.a} L${P.m}`, stroke: 'rgba(244,242,236,.3)', 'stroke-width': 1.5, fill: 'none', pathLength: 1 }, ts);
  const lMC = s('path', { d: `M${P.m} L${P.c}`, stroke: 'rgba(244,242,236,.3)', 'stroke-width': 1.5, fill: 'none', pathLength: 1 }, ts);
  const lCA = s('path', { d: `M${P.c} L${P.a}`, stroke: 'rgba(244,242,236,.14)', 'stroke-width': 1.5, fill: 'none', 'stroke-dasharray': '4 6', pathLength: 1 }, ts);
  const pd = pulseDot(ts, 5), pd2 = pulseDot(ts, 5);
  const node = (k, icon, label) => box(title.el, P[k][0] - 50, P[k][1] - 50, 'card solid', `<div style="width:98px;height:98px;display:flex;align-items:center;justify-content:center;color:${k === 'm' ? Y : '#F4F2EC'}">${I(icon, 40)}</div><div class="tag" style="position:absolute;top:112px;left:50%;transform:translateX(-50%);white-space:nowrap">${label}</div>`);
  const nodes = { a: node('a', 'warehouse', 'Asset'), m: node('m', 'target', 'Buy mandate'), c: node('c', 'landmark', 'Credit box') };

  // ---------------------------------------------------------------- chapters
  const C = (n, name, t0) => chapters.push({ n, name, t0 });
  C('', '', 0);
  C('01', 'THE PROBLEM', 4.9);
  C('02', 'THE OBJECTS', L('04') - .7);
  C('03', 'THE MANDATE', L('07') - 1.0);
  C('04', 'THE DEBT', L('13') - 1.3);
  C('05', 'FROM SCORE TO BID', L('15') - .7);
  C('06', 'THE SELLER', L('19') - .7);
  C('07', 'CLEARING', L('20') - .7);
  C('08', 'A LIVING BOOK', L('24') - .8);
  C('09', 'THE CLAIM', L('26') - .9);
  C('', '', E('27') + 2.0);
  chrome(logo);

  ch1(); ch2(); ch3(); ch4(); ch5(); ch6();

  // ---------------------------------------------------------------- end card
  const t0 = E('27') + 2.0;
  const end = scene(t0, T.duration + 1, (t) => {
    rise(eLogo, t, t0 + .5, { dy: 20, d: 1.2 });
    rise(eT, t, t0 + 1.1); rise(eS, t, t0 + 1.4);
    eLine.style.width = 360 * pr(t, t0 + .8, 1.2) + 'px';
  }, { fi: 1.0 });
  const eLogo = box(end.el, 960 - 230, 430, '', logo, { width: '460px' });
  const eLine = box(end.el, 780, 560, 'rule', '', { background: Y, height: '2px' });
  const eT = box(end.el, 0, 600, 'eyebrow', 'The Mandate Market · the market layer', { width: '1920px', textAlign: 'center', color: '#F4F2EC' });
  const eS = box(end.el, 0, 640, 'eyebrow', 'Prop.com · Propchain · September 2026', { width: '1920px', textAlign: 'center', fontSize: '14px' });
})();

// ------------------------------------------------------------------ background: faint dot grid, slow drift
function bg() {
  const c = document.getElementById('grid'); gridCtx = c.getContext('2d');
}
function drawBg(t) {
  const g = gridCtx; g.clearRect(0, 0, 1920, 1080);
  const sp = 48, ox = (t * 3) % sp, oy = (t * 1.5) % sp;
  g.fillStyle = 'rgba(244,242,236,.07)';
  for (let x = -sp; x < 1920 + sp; x += sp) for (let y = -sp; y < 1080 + sp; y += sp) {
    const dx = (x + ox - 960) / 960, dy = (y + oy - 540) / 540; const a = Math.max(0, 1 - (dx * dx + dy * dy) * .7);
    if (a <= 0) continue; g.globalAlpha = a; g.fillRect(x + ox, y + oy, 1.6, 1.6);
  }
  g.globalAlpha = 1;
}
function grain() {
  const c = document.getElementById('grain'); gctx = c.getContext('2d');
  let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  for (let k = 0; k < 8; k++) {
    const im = gctx.createImageData(960, 540);
    for (let i = 0; i < im.data.length; i += 4) { const v = rnd() * 255; im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 255; }
    grainFrames.push(im);
  }
}

let chEl, chN, chName;
function chrome(logo) {
  const root = document.getElementById('chrome');
  chEl = h('div.chapter', {}, root); chN = h('span.n', {}, chEl); chName = h('span', {}, chEl);
}
function drawChrome(t) {
  let cur = chapters[0], next = null;
  for (let i = 0; i < chapters.length; i++) if (t >= chapters[i].t0) { cur = chapters[i]; next = chapters[i + 1]; }
  const a = Math.min(pr(t, cur.t0 + .2, .8), next ? 1 - pr(t, next.t0 - .4, .4, e3) : 1);
  chEl.style.opacity = cur.n ? a : 0;
  chEl.style.transform = `translateY(${(1 - pr(t, cur.t0 + .2, .8)) * 10}px)`;
  if (chN.textContent !== cur.n) { chN.textContent = cur.n; chName.textContent = cur.name; }
}

window.__seek = async (t) => {
  await window.__ready;
  pending = [];
  drawBg(t);
  runScenes(t);
  drawChrome(t);
  gctx.putImageData(grainFrames[Math.floor(t * 30) % 8], 0, 0);
  await Promise.all(pending.map(img => img.decode().catch(() => { })));
};

// live preview: index.html?t=12.5 or ?play
const q = new URLSearchParams(location.search);
if (q.has('t')) window.__seek(parseFloat(q.get('t')));
if (q.has('play')) { const s0 = performance.now(); const loop = () => { window.__seek((performance.now() - s0) / 1000); requestAnimationFrame(loop); }; loop(); }
