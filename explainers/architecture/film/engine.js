// Deterministic motion-graphics engine. Everything is a pure function of t:
// scenes register animation closures, window.__seek(t) runs the visible ones.
'use strict';

const W = 1920, H = 1080;
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, p) => a + (b - a) * p;
const ease = {
  out: p => 1 - Math.pow(1 - p, 5),                       // quint out
  cub: p => 1 - Math.pow(1 - p, 3),
  io: p => (p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2),
};
const prog = (t, t0, dur, e = ease.out) => e(clamp((t - t0) / dur));

// ---------------------------------------------------------------- voice-over timing helpers
// V(id) -> start time of a narration line; Wd(id, word) -> estimated time the word is spoken
// (character-proportional within the line, nudged earlier so the picture leads the voice).
const V = id => window.VO[id][0];
const Vend = id => window.VO[id][0] + window.VO[id][1];
function Wd(id, word, lead = 0.25) {
  const [t0, d, text] = window.VO[id];
  const i = text.indexOf(word);
  if (i < 0) throw new Error(`word "${word}" not in line ${id}`);
  return t0 + d * (i / text.length) - lead;
}

// ---------------------------------------------------------------- DOM helpers
const SVGNS = 'http://www.w3.org/2000/svg';
function el(tag, cls, parent, html) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (html != null) e.innerHTML = html;
  if (parent) parent.appendChild(e);
  return e;
}
function sv(tag, attrs, parent) {
  const e = document.createElementNS(SVGNS, tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]);
  if (parent) parent.appendChild(e);
  return e;
}
function pos(e, x, y, w, h) {
  e.style.left = x + 'px'; e.style.top = y + 'px';
  if (w != null) e.style.width = w + 'px';
  if (h != null) e.style.height = h + 'px';
  return e;
}
const ICONS = {};
async function loadIcons(names) {
  await Promise.all(names.map(async n => {
    const r = await fetch(`../node_modules/lucide-static/icons/${n}.svg`);
    ICONS[n] = (await r.text()).replace(/<!--.*?-->/gs, '').replace(/class="[^"]*"/, 'class="ic"');
  }));
}
function icon(name, size = 32, parent, cls = '') {
  const w = el('span', 'icon ' + cls, parent, ICONS[name] || '');
  w.style.width = w.style.height = size + 'px';
  return w;
}

// ---------------------------------------------------------------- scenes
const SCENES = [];
let STAGE;
class Scene {
  constructor(t0, t1, { fadeIn = .5, fadeOut = .5, bg = null } = {}) {
    Object.assign(this, { t0, t1, fadeIn, fadeOut, anims: [] });
    this.el = el('div', 'scene', STAGE);
    if (bg) this.el.style.background = bg;
    SCENES.push(this);
  }
  on(fn) { this.anims.push(fn); return this; }
  svg(parent = this.el) { return sv('svg', { width: W, height: H, viewBox: `0 0 ${W} ${H}`, class: 'layer' }, parent); }
}

// Appear: slide + blur in at t0; optional out time.
function appear(sc, e, t0, o = {}) {
  const { dur = .8, dx = 0, dy = 26, blur = 10, out = null, outDur = .5, op = 1, scale = null } = o;
  e.style.opacity = 0;
  sc.on(t => {
    const p = prog(t, t0, dur);
    const q = out == null ? 1 : 1 - prog(t, out, outDur, ease.cub);
    const a = p * q;
    e.style.opacity = (a * op).toFixed(3);
    let tr = `translate(${(dx * (1 - p)).toFixed(1)}px,${(dy * (1 - p)).toFixed(1)}px)`;
    if (scale != null) tr += ` scale(${lerp(scale, 1, p).toFixed(3)})`;
    e.style.transform = tr;
    e.style.filter = p < .999 && blur ? `blur(${(blur * (1 - p)).toFixed(2)}px)` : 'none';
  });
  return e;
}
// Toggle a class between t0 and t1 (e.g. yellow highlight).
function flag(sc, e, cls, t0, t1 = 1e9) { sc.on(t => e.classList.toggle(cls, t >= t0 && t < t1)); return e; }
// Stroke draw-on for a path/line with pathLength=1.
function draw(sc, p, t0, dur = 1, o = {}) {
  p.setAttribute('pathLength', 1);
  p.style.strokeDasharray = '1 1';
  sc.on(t => {
    const k = prog(t, t0, dur, o.e || ease.cub);
    const q = o.out == null ? 1 : 1 - prog(t, o.out, o.outDur || .5, ease.cub);
    p.style.strokeDashoffset = (1 - k).toFixed(4);
    p.style.opacity = (k > 0 ? q : 0).toFixed(3);
  });
  return p;
}
// Travelling pulse: a bright streak + head dot moving along path. Runs from t0 over dur; repeats with period if given.
function pulse(sc, svg, path, t0, dur, o = {}) {
  const { color = 'var(--y)', r = 5, len = .12, repeat = 1, period = dur, until = 1e9, width = 3, reverse = false } = o;
  const d = path.getAttribute('d');
  const trail = sv('path', { d, class: 'trail', 'pathLength': 1, stroke: color, 'stroke-width': width, fill: 'none' }, svg);
  const head = sv('circle', { r, fill: color, class: 'head' }, svg);
  const L = path.getTotalLength();
  sc.on(t => {
    let k = -1;
    if (t < until) for (let i = 0; i < repeat; i++) {
      const s = t0 + i * period;
      if (t >= s && t < s + dur) { k = ease.io((t - s) / dur); break; }
    }
    if (k < 0) { trail.style.opacity = 0; head.style.opacity = 0; return; }
    if (reverse) k = 1 - k;
    const pt = path.getPointAtLength(k * L);
    head.setAttribute('cx', pt.x.toFixed(1)); head.setAttribute('cy', pt.y.toFixed(1));
    const a = Math.min(1, Math.min(k, 1 - k) * 8);
    head.style.opacity = a;
    trail.style.opacity = a * .9;
    const s0 = reverse ? k : Math.max(0, k - len);
    trail.style.strokeDasharray = `0 ${s0.toFixed(4)} ${len.toFixed(4)} 2`;
  });
}
// Deterministic hash-like scramble that resolves to `final`.
const HEX = '0123456789abcdef';
function scramble(sc, e, final, t0, dur = .9) {
  sc.on(t => {
    const p = clamp((t - t0) / dur);
    if (t < t0) { e.textContent = ''; return; }
    const n = Math.floor(p * final.length);
    let s = final.slice(0, n);
    const f = Math.floor(t * 30);
    for (let i = n; i < final.length; i++) s += final[i] === ' ' || final[i] === '…' ? final[i] : HEX[(i * 7 + f * 13 + i * f) % 16];
    e.textContent = s;
  });
}
// Camera over a world element: keys [[t, cx, cy, scale], ...]
function camera(sc, world, keys) {
  world.style.transformOrigin = '0 0';
  sc.on(t => {
    let [_, x, y, s] = keys[0];
    for (let i = 0; i < keys.length - 1; i++) {
      const [ta, xa, ya, sa] = keys[i], [tb, xb, yb, sb] = keys[i + 1];
      if (t >= tb) { x = xb; y = yb; s = sb; continue; }
      if (t > ta) { const p = ease.io((t - ta) / (tb - ta)); x = lerp(xa, xb, p); y = lerp(ya, yb, p); s = lerp(sa, sb, p); }
      break;
    }
    world.style.transform = `translate(${(W / 2 - x * s).toFixed(2)}px,${(H / 2 - y * s).toFixed(2)}px) scale(${s.toFixed(4)})`;
  });
}

// ---------------------------------------------------------------- stock clips (frame sequences)
function stock(sc, id, t0, t1, o = {}) {
  const { from = 0, zoom = [1.04, 1.1], dim = .45 } = o;
  const wrap = el('div', 'stock', sc.el);
  const img = el('img', '', wrap);
  el('div', 'stock-shade', wrap).style.opacity = dim;
  const n = window.STOCK[id].frames;
  sc.on(async t => {
    const f = clamp(Math.floor((t - t0 + from) * 30) + 1, 1, n);
    const src = `../stock/clips/${id}/f_${String(f).padStart(4, '0')}.jpg`;
    const p = clamp((t - t0) / (t1 - t0));
    img.style.transform = `scale(${lerp(zoom[0], zoom[1], p).toFixed(4)})`;
    if (!img.src.endsWith(src)) { img.src = src; }
  });
  sc.imgs = (sc.imgs || []).concat(img);
  return wrap;
}

// ---------------------------------------------------------------- global overlays
const CHAPTERS = [];
function chapter(t0, t1, num, label) { CHAPTERS.push({ t0, t1, num, label }); }

let chapEl, grainEl, grainCtx, noiseTiles = [];
function buildOverlays() {
  chapEl = el('div', 'chapter', document.getElementById('film'));
  grainEl = el('canvas', 'grain', document.getElementById('film'));
  grainEl.width = 960; grainEl.height = 540;
  grainCtx = grainEl.getContext('2d');
  let seed = 7;
  const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  for (let k = 0; k < 8; k++) {
    const img = grainCtx.createImageData(960, 540);
    for (let i = 0; i < img.data.length; i += 4) { const v = rnd() * 255; img.data[i] = img.data[i + 1] = img.data[i + 2] = v; img.data[i + 3] = 255; }
    noiseTiles.push(img);
  }
  el('div', 'vignette', document.getElementById('film'));
}
function overlays(t) {
  grainCtx.putImageData(noiseTiles[Math.floor(t * 30) % 8], 0, 0);
  const c = CHAPTERS.find(c => t >= c.t0 && t < c.t1);
  if (!c) { chapEl.style.opacity = 0; return; }
  const key = c.num + c.label;
  if (chapEl.dataset.k !== key) { chapEl.dataset.k = key; chapEl.innerHTML = `<b>${c.num}</b><span>${c.label}</span>`; }
  const p = prog(t, c.t0, .9), q = 1 - prog(t, c.t1 - .5, .5, ease.cub);
  chapEl.style.opacity = (p * q).toFixed(3);
  chapEl.style.transform = `translateX(${(-20 * (1 - p)).toFixed(1)}px)`;
}

async function seek(t) {
  const waits = [];
  for (const sc of SCENES) {
    const vis = t >= sc.t0 - 1e-6 && t < sc.t1;
    if (!vis) { if (sc.el.style.display !== 'none') sc.el.style.display = 'none'; continue; }
    sc.el.style.display = 'block';
    const a = Math.min(sc.fadeIn ? prog(t, sc.t0, sc.fadeIn, ease.cub) : 1, sc.fadeOut ? 1 - prog(t, sc.t1 - sc.fadeOut, sc.fadeOut, ease.cub) : 1);
    sc.el.style.opacity = a.toFixed(3);
    for (const f of sc.anims) f(t);
    if (sc.imgs) for (const im of sc.imgs) waits.push(im.decode().catch(() => {}));
  }
  overlays(t);
  await Promise.all(waits);
}
