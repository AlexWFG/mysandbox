// Deterministic motion-graphics engine: everything on screen is a pure function of time t.
// window.__seek(t) renders any frame; window.__ready resolves once fonts, timeline and scenes exist.
const $ = (s, r = document) => r.querySelector(s);
const E = {
  o3: x => 1 - Math.pow(1 - x, 3),
  o5: x => 1 - Math.pow(1 - x, 5),
  io2: x => x < .5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2,
  io3: x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2,
  lin: x => x,
};
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const P = (t, t0, d = .8, e = E.o3) => e(clamp((t - t0) / d));
const lerp = (a, b, p) => a + (b - a) * p;
const Y = '#FFBE06', INK = '#F4F2EC', DIM = 'rgba(244,242,236,.62)', FAINT = 'rgba(244,242,236,.38)', LINE = 'rgba(244,242,236,.16)';

let TL = null, MAN = {};
const L = id => { const l = TL.lines[id]; if (!l) throw new Error('no line ' + id); return l; };
const T = id => L(id).t;
const END = id => L(id).t + L(id).dur;

// When is `word` spoken in line `id`? Phrases (split on punctuation) are mapped onto the
// speech segments measured from the waveform; inside a phrase the time is character-proportional.
function at(id, word, nth = 0, lead = .12) {
  const l = L(id); let i = -1;
  for (let k = 0; k <= nth; k++) { i = l.text.indexOf(word, i + 1); if (i < 0) throw new Error(`"${word}" not in ${id}`); }
  const re = /[,.:?!;]\s/g, bounds = [0]; let m;
  while ((m = re.exec(l.text))) bounds.push(m.index + m[0].length);
  bounds.push(l.text.length);
  const segs = l.segs || [];
  if (segs.length === bounds.length - 1) {
    let p = 0; while (p < segs.length - 1 && i >= bounds[p + 1]) p++;
    const f = (i - bounds[p]) / Math.max(1, bounds[p + 1] - bounds[p]);
    return l.t + lerp(segs[p][0], segs[p][1], f) - lead;
  }
  return l.t + l.dur * (i / l.text.length) - lead;
}

// ------------------------------------------------------------------ element helpers
function show(e, t, tin, tout = 1e9, o = {}) {
  const { dy = 24, dx = 0, blur = 8, d = .8, dout = .5, min = 0 } = o;
  const pi = P(t, tin, d, E.o5), po = P(t, tout, dout, E.io2);
  const v = Math.max(min, pi * (1 - po));
  if (v <= .002) { e.style.opacity = 0; e.style.visibility = 'hidden'; return 0; }
  e.style.visibility = 'visible'; e.style.opacity = v;
  if (e._base === undefined) e._base = e.style.transform || '';
  e.style.transform = `${e._base} translate(${dx * (1 - pi)}px,${(1 - pi) * dy - po * dy * .5}px)`;
  const b = ((1 - pi) + po) * blur;
  e.style.filter = b > .05 ? `blur(${b}px)` : 'none';
  return v;
}
function fade(e, v) { e.style.opacity = v; e.style.visibility = v > .002 ? 'visible' : 'hidden'; }
function draw(e, p) { e.style.strokeDasharray = '1 1'; e.style.strokeDashoffset = 1 - clamp(p); e.style.opacity = p > 0 ? 1 : 0; }
function drawAll(root, p) { root.querySelectorAll('[pathLength]').forEach(x => draw(x, p)); }
function num(e, v, fmt) { const s = fmt(v); if (e.textContent !== s) e.textContent = s; }
const eurk = v => '€' + Math.round(v).toLocaleString('en-GB') + 'k';

function icon(name, size = 32, color = 'currentColor', sw) {
  const w = sw ?? 2 * 24 / size;
  return `<span class="ic" style="width:${size}px;height:${size}px;color:${color}"><svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round">${ICONS[name]}</svg></span>`;
}
// icon inside an SVG, centred on (x, y), drawable (pathLength on every child)
function sicon(name, x, y, size = 40, color = INK, k = '') {
  const s = size / 24, inner = ICONS[name].replace(/<(path|circle|rect|line|polyline|polygon|ellipse)\b/g, '<$1 pathLength="1"');
  return `<g ${k ? `data-k="${k}"` : ''} transform="translate(${x - size / 2},${y - size / 2}) scale(${s})" fill="none" stroke="${color}" stroke-width="${2 / s}" stroke-linecap="round" stroke-linejoin="round">${inner}</g>`;
}

// travelling pulses along an SVG path
function flowDots(n = 7, r = 5, color = Y) {
  return Array.from({ length: n }, () => `<circle r="${r}" fill="${color}" opacity="0"/>`).join('');
}
function flow(g, path, t, t0, t1, o = {}) {
  const { rate = 3, dur = 1.2, fadeTail = true } = o;
  const cs = g.querySelectorAll('circle'), N = cs.length;
  if (!path._len) path._len = path.getTotalLength();
  cs.forEach(c => c.setAttribute('opacity', 0));
  if (t < t0) return;
  const kmax = Math.floor((Math.min(t, t1) - t0) * rate);
  for (let k = kmax; k > kmax - N && k >= 0; k--) {
    const ts = t0 + k / rate, p = (t - ts) / dur;
    if (p < 0 || p > 1) continue;
    const c = cs[k % N], pt = path.getPointAtLength(E.io2(p) * path._len);
    c.setAttribute('cx', pt.x); c.setAttribute('cy', pt.y);
    c.setAttribute('opacity', fadeTail ? Math.sin(Math.PI * p) ** .6 : 1);
  }
}
function place(e, x, y) { e.style.left = x + 'px'; e.style.top = y + 'px'; }

// ------------------------------------------------------------------ scenes, stock, hud
const SCENES = [], STOCK = [];
function scene(a, b, html, update, o = {}) {
  const root = document.createElement('div');
  root.className = 'scene'; root.innerHTML = html;
  $('#scenes').appendChild(root);
  const k = {}; root.querySelectorAll('[data-k]').forEach(e => { k[e.dataset.k] = e; });
  SCENES.push({ a, b, root, k, update, fi: o.fi ?? .5, fo: o.fo ?? .5 });
  return k;
}
function stock(clip, a, b, o = {}) {
  const img = document.createElement('img'); $('#stock').appendChild(img);
  STOCK.push({ clip, a, b, img, from: o.from || 0, op: o.op ?? 1, z0: o.z0 ?? 1.0, z1: o.z1 ?? 1.07, bright: o.bright ?? .62, shade: o.shade ?? 1 });
}
async function renderStock(t) {
  const waits = []; let sh = 0;
  for (const s of STOCK) {
    const v = P(t, s.a, .6, E.io2) * (1 - P(t, s.b - .6, .6, E.io2));
    if (v <= 0) { s.img.style.opacity = 0; continue; }
    const n = MAN[s.clip]?.frames || 1;
    const f = clamp(Math.floor((t - s.a + s.from) * 30) + 1, 1, n);
    const src = `stock/clips/${s.clip}/f_${String(f).padStart(4, '0')}.jpg`;
    if (s.src !== src) { s.src = src; s.img.src = src; waits.push(s.img.decode().catch(() => {})); }
    s.img.style.opacity = v * s.op;
    s.img.style.filter = `brightness(${s.bright}) saturate(.85)`;
    s.img.style.transform = `scale(${lerp(s.z0, s.z1, clamp((t - s.a) / (s.b - s.a)))})`;
    sh = Math.max(sh, v * s.shade);
  }
  $('#stock .shade').style.opacity = sh;
  await Promise.all(waits);
}

let CHAPS = [];
function buildHud() {
  const hud = $('#hud');
  CHAPS = TL.chapters.map((c, i) => {
    const e = document.createElement('div'); e.className = 'chap';
    e.innerHTML = `<b>${String(c.n).padStart(2, '0')}</b>${c.name}`;
    hud.appendChild(e);
    const next = TL.chapters[i + 1];
    return { e, a: c.t, b: next ? next.t - .1 : TL.end - .4 };
  });
  const m = document.createElement('img'); m.className = 'mark'; m.src = '../../propchain-reel/assets/logo-white.svg'; m.id = 'hudmark';
  hud.appendChild(m);
}
function renderHud(t) {
  for (const c of CHAPS) show(c.e, t, c.a, c.b, { dy: 0, dx: -24, blur: 6, d: .9, dout: .4 });
  const m = $('#hudmark'); fade(m, .55 * P(t, CHAPS[0].a, 1) * (1 - P(t, TL.end - .6, .5)));
}

const GRAIN = [];
function buildGrain() {
  for (let i = 0; i < 6; i++) {
    const c = document.createElement('canvas'); c.width = c.height = 256;
    const g = c.getContext('2d'), d = g.createImageData(256, 256);
    let s = 1234 + i * 977;
    for (let p = 0; p < d.data.length; p += 4) { s = (s * 16807) % 2147483647; const v = 128 + ((s / 2147483647) - .5) * 190; d.data[p] = d.data[p + 1] = d.data[p + 2] = v; d.data[p + 3] = 255; }
    g.putImageData(d, 0, 0); GRAIN.push(c.toDataURL('image/png'));
  }
}
function renderGrain(t) {
  const f = Math.round(t * 30), g = $('#grain');
  g.style.backgroundImage = `url(${GRAIN[f % GRAIN.length]})`;
  g.style.backgroundPosition = `${(f * 73) % 256}px ${(f * 151) % 256}px`;
}

window.__seek = async t => {
  for (const s of SCENES) {
    const v = P(t, s.a, s.fi, E.io2) * (1 - P(t, s.b - s.fo, s.fo, E.io2));
    if (v <= 0) { if (s.root.style.display !== 'none') s.root.style.display = 'none'; continue; }
    s.root.style.display = 'block'; s.root.style.opacity = v;
    s.update(t, s.k, s.root);
  }
  renderHud(t); renderGrain(t);
  await renderStock(t);
};

window.__ready = (async () => {
  TL = await (await fetch('timeline.json')).json();
  try { MAN = await (await fetch('stock/manifest.json')).json(); } catch (e) { MAN = {}; }
  const sh = document.createElement('div'); sh.className = 'shade'; $('#stock').appendChild(sh);
  buildGrain(); buildHud(); buildScenes();
  await document.fonts.load('300 40px Inter'); await document.fonts.load('400 40px Inter');
  await document.fonts.load('500 40px Inter'); await document.fonts.load('500 20px Mono');
  await document.fonts.ready;
  window.__total = TL.total;
})();

// live preview: index.html?t=12.3 (still) or ?play
(async () => {
  const q = new URLSearchParams(location.search); if (!q.has('t') && !q.has('play')) return;
  await window.__ready;
  if (q.has('t')) return window.__seek(parseFloat(q.get('t')));
  const t0 = performance.now() - parseFloat(q.get('play') || 0) * 1000;
  const loop = async () => { await window.__seek((performance.now() - t0) / 1000); requestAnimationFrame(loop); }; loop();
})();

function buildScenes() {
  build1();
  if (typeof build2 === 'function') build2();
  if (typeof build3 === 'function') build3();
}
