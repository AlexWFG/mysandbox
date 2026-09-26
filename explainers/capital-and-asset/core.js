// Core helpers: easing, element factories, time-driven animation primitives, narration anchors,
// stock frame players and icons. Everything is a pure function of t so any frame renders identically.

export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const range = (t, a, b) => clamp((t - a) / (b - a));
export const eo5 = x => 1 - Math.pow(1 - x, 5);
export const eo3 = x => 1 - Math.pow(1 - x, 3);
export const ei3 = x => x * x * x;
export const eio3 = x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
export const lerp = (a, b, u) => a + (b - a) * u;

// ------------------------------------------------------------ narration anchors
export let TL, MAN;
const norm = s => s.toLowerCase().replace(/[^a-z0-9]/g, '');
export function setData(tl, man) { TL = tl; MAN = man; }
const line = id => { const l = TL.lines.find(l => l.id === id); if (!l) throw new Error('no line ' + id); return l; };
export const L = id => line(id).t;
export const E = id => line(id).t + line(id).dur;
export function W(id, word, n = 0) {
  const k = norm(word); let c = 0;
  for (const [w, a] of line(id).words) if (norm(w).startsWith(k) && c++ === n) return a;
  throw new Error(`word "${word}" #${n} not in ${id}`);
}
export function WE(id, word, n = 0) {
  const k = norm(word); let c = 0;
  for (const [w, , b] of line(id).words) if (norm(w).startsWith(k) && c++ === n) return b;
  throw new Error(`word "${word}" not in ${id}`);
}

// ------------------------------------------------------------ DOM
export function mk(tag, cls, parent, style, html) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (style) Object.assign(e.style, style);
  if (html != null) e.innerHTML = html;
  if (parent) parent.appendChild(e);
  return e;
}
const NS = 'http://www.w3.org/2000/svg';
export function sv(tag, attrs, parent) {
  const e = document.createElementNS(NS, tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]);
  if (parent) parent.appendChild(e);
  return e;
}
export function svgLayer(parent) { return sv('svg', { class: 'full', viewBox: '0 0 1920 1080' }, parent); }
export const px = v => v + 'px';

// ------------------------------------------------------------ animation primitives
// in/out envelope: returns {a, i, o} (alpha, eased in, eased out)
export function env(t, s, e = 1e9, din = .8, dout = .5) {
  const i = eo5(range(t, s, s + din)), o = ei3(range(t, e - dout, e));
  return { a: i * (1 - o), i, o };
}
// fade + slide + blur in, fade + blur out. Uses transform, so put it on wrappers.
export function show(el, t, s, e = 1e9, o = {}) {
  const { dy = 26, dx = 0, blur = 9, din = .8, dout = .5, min = 0, sc = 0 } = o;
  const v = env(t, s, e, din, dout);
  const a = min + (1 - min) * v.a;
  el.style.opacity = a;
  el.style.visibility = a < .002 ? 'hidden' : 'visible';
  el.style.transform = `translate(${dx * (1 - v.i)}px, ${dy * (1 - v.i) - 10 * v.o}px)` + (sc ? ` scale(${1 - sc * (1 - v.i)})` : '');
  const b = (1 - v.i) * blur + v.o * 6;
  el.style.filter = b > .05 ? `blur(${b}px)` : 'none';
  return v;
}
export function fade(el, a) { el.style.opacity = a; el.style.visibility = a < .002 ? 'hidden' : 'visible'; }
// stroke draw-on for elements carrying pathLength=1
export function draw(el, t, s, d = 1, ease = eo3) {
  const u = ease(range(t, s, s + d));
  el.style.strokeDasharray = '1 1';
  el.style.strokeDashoffset = 1 - u;
  return u;
}
export function drawU(el, u) { el.style.strokeDasharray = '1 1'; el.style.strokeDashoffset = 1 - u; }

// words
export function wordsHTML(text, hi = []) {
  return text.split(/(\s+)/).filter(Boolean).map(w => /^\s+$/.test(w) ? w : `<span class="w${hi.some(h => w.includes(h)) ? ' y' : ''}">${w}</span>`).join('');
}
export function wordsIn(el, t, s, stagger = .06, e = 1e9, o = {}) {
  el.querySelectorAll('.w').forEach((w, j) => show(w, t, s + j * stagger, e, { dy: 34, blur: 10, ...o }));
}

// pulse along a path (u in 0..1)
export function along(path, u) {
  const L = path.__len ?? (path.__len = path.getTotalLength());
  return path.getPointAtLength(clamp(u) * L);
}

// ------------------------------------------------------------ icons (lucide-static, 1.5 stroke)
export const ICONS = {};
export async function loadIcons(names) {
  await Promise.all(names.map(async n => {
    const r = await fetch(`node_modules/lucide-static/icons/${n}.svg`);
    ICONS[n] = (await r.text()).replace(/<!--.*?-->/s, '');
  }));
}
export function icon(name, size, parent, style = {}, sw = 1.5) {
  const d = mk('div', 'icon', parent, { width: px(size), height: px(size), ...style });
  d.innerHTML = ICONS[name];
  const s = d.querySelector('svg');
  s.removeAttribute('width'); s.removeAttribute('height'); s.removeAttribute('class');
  s.setAttribute('stroke-width', sw);
  s.querySelectorAll('path,line,circle,rect,polyline,polygon,ellipse').forEach(g => g.setAttribute('pathLength', 1));
  return d;
}
export function drawIcon(el, t, s, d = .9) {
  const u = eo3(range(t, s, s + d));
  el.querySelectorAll('[pathLength]').forEach((g, i) => drawU(g, clamp(u * 1.25 - i * .06)));
  return u;
}

// ------------------------------------------------------------ stock frame sequences
export const pending = [];
export function setClip(img, id, t, t0, speed = 1) {
  const m = MAN[id];
  const f = clamp(Math.floor(Math.max(0, t - t0) * 30 * speed), 0, m.frames - 1) + 1;
  const src = `stock/clips/${id}/f_${String(f).padStart(4, '0')}.jpg`;
  if (img.dataset.src !== src) {
    img.dataset.src = src; img.src = src;
    pending.push(img.decode().catch(() => {}));
  }
}
