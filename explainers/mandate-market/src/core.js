// Core of the Mandate Market explainer: time helpers, DOM/SVG builders, reveal
// primitives, narration-cue lookup. Everything is a pure function of t.

export const Y = '#FFBE06', INK = '#F4F2EC', DIM = 'rgba(244,242,236,.62)', LINE = 'rgba(244,242,236,.16)';
export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const eo = x => 1 - Math.pow(1 - clamp(x), 5);                   // quint out
export const e3 = x => 1 - Math.pow(1 - clamp(x), 3);                   // cubic out
export const eio = x => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
export const pr = (t, a, d = .8, e = eo) => e((t - a) / d);
export const lerp = (a, b, p) => a + (b - a) * p;
/** 0->1 in at `a`, back to 0 at `b` */
export const win = (t, a, b, di = .7, dout = .5) => Math.min(pr(t, a, di), 1 - pr(t, b, dout, e3));

// ------------------------------------------------------------------ narration cues
export const T = {
  lines: {},
  init(tl) { this.duration = tl.duration; for (const l of tl.lines) this.lines[l.id] = l; },
  L(id) { return this.lines[id].t; },
  E(id) { return this.lines[id].end; },
  /** start time of the word in line `id` matching `key` (occurrence `n`) */
  W(id, key, n = 0) {
    const norm = s => s.toLowerCase().replace(/[^a-z0-9-']/g, '');
    const ws = this.lines[id].words; const k = norm(key);
    for (const w of ws) if (norm(w.w).startsWith(k) && n-- === 0) return w.t;
    throw new Error(`cue not found: ${id} "${key}"`);
  },
  WE(id, key, n = 0) {
    const norm = s => s.toLowerCase().replace(/[^a-z0-9-']/g, '');
    const ws = this.lines[id].words; const k = norm(key);
    for (const w of ws) if (norm(w.w).startsWith(k) && n-- === 0) return w.e;
    throw new Error(`cue not found: ${id} "${key}"`);
  },
};

// ------------------------------------------------------------------ builders
const SVGNS = 'http://www.w3.org/2000/svg';
/** h('div.card.big', {style:{left:'10px'}}, parent, 'html') */
export function h(spec, attrs = {}, parent = null, html = null) {
  const [tag, ...cls] = spec.split('.');
  const el = document.createElement(tag || 'div');
  if (cls.length) el.className = cls.join(' ');
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'style') Object.assign(el.style, v); else el.setAttribute(k, v);
  }
  if (html != null) el.innerHTML = html;
  if (parent) parent.appendChild(el);
  return el;
}
export function s(tag, attrs = {}, parent = null) {
  const el = document.createElementNS(SVGNS, tag);
  for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
  if (parent) parent.appendChild(el);
  return el;
}
export function svg(parent, w = 1920, h_ = 1080, style = {}) {
  const el = s('svg', { width: w, height: h_, viewBox: `0 0 ${w} ${h_}` }, parent);
  Object.assign(el.style, { position: 'absolute', left: 0, top: 0, overflow: 'visible', ...style });
  return el;
}
/** absolutely positioned div */
export function box(parent, x, y, cls = '', html = '', style = {}) {
  return h('div.abs' + (cls ? '.' + cls.split(' ').join('.') : ''), { style: { left: x + 'px', top: y + 'px', ...style } }, parent, html);
}

// ------------------------------------------------------------------ icons (lucide-static, inlined)
const ICONS = {};
export async function loadIcons(names) {
  await Promise.all(names.map(async n => {
    const r = await fetch(`node_modules/lucide-static/icons/${n}.svg`);
    if (!r.ok) throw new Error('icon ' + n);
    ICONS[n] = (await r.text()).replace(/<!--[\s\S]*?-->/g, '').replace(/stroke-width="[^"]*"/, 'stroke-width="1.5"');
  }));
}
export function I(n, size = 28, color = 'currentColor') {
  if (!ICONS[n]) throw new Error('icon not loaded ' + n);
  return ICONS[n].replace(/width="24"/, `width="${size}"`).replace(/height="24"/, `height="${size}"`).replace(/stroke="currentColor"/, `stroke="${color}"`).replace('<svg', '<svg class="ico"');
}

// ------------------------------------------------------------------ reveal primitives
/** slide + blur in at `at`; optional out at `out` */
export function rise(el, t, at, o = {}) {
  const { dy = 26, dx = 0, d = .9, blur = 8, out = null, dout = .45, scale = 0 } = o;
  const p = pr(t, at, d);
  let q = 1; if (out != null) q = 1 - pr(t, out, dout, e3);
  const a = Math.min(p, q);
  el.style.opacity = a;
  const sc = scale ? 1 - scale * (1 - p) : 1;
  el.style.transform = `translate(${(1 - p) * dx}px,${(1 - p) * dy}px)` + (sc !== 1 ? ` scale(${sc})` : '');
  el.style.filter = a < .999 ? `blur(${(1 - p) * blur + (1 - q) * 4}px)` : 'none';
  el.style.visibility = a <= 0.001 ? 'hidden' : 'visible';
  return p;
}
export function fade(el, t, at, d = .6, out = null, dout = .45) {
  const a = out == null ? pr(t, at, d) : win(t, at, out, d, dout);
  el.style.opacity = a; el.style.visibility = a <= .001 ? 'hidden' : 'visible';
  return a;
}
/** stroke draw-on for SVG elements created with pathLength=1 */
export function draw(el, t, at, d = 1.0, e = eio) {
  const p = pr(t, at, d, e);
  el.setAttribute('stroke-dasharray', '1 1');
  el.setAttribute('stroke-dashoffset', 1 - p);
  el.style.opacity = p > 0 ? 1 : 0;
  return p;
}
export const fmt = (v, dp = 2) => v.toFixed(dp);
export function setText(el, txt) { if (el.__t !== txt) { el.textContent = txt; el.__t = txt; } }

/** a travelling pulse along an SVG path, p in 0..1 */
export function pulseAt(path, dot, p, alpha = 1) {
  const L = path.getTotalLength(); const pt = path.getPointAtLength(clamp(p) * L);
  dot.setAttribute('cx', pt.x); dot.setAttribute('cy', pt.y);
  dot.style.opacity = p <= 0 || p >= 1 ? 0 : alpha;
}
export function pulseDot(parent, r = 7) {
  const g = s('g', {}, parent);
  s('circle', { r: r * 3, fill: Y, opacity: .18, class: 'halo' }, g);
  s('circle', { r, fill: Y }, g);
  return {
    g, at(path, p, a = 1) {
      const L = path.getTotalLength(); const pt = path.getPointAtLength(clamp(p) * L);
      g.setAttribute('transform', `translate(${pt.x},${pt.y})`);
      g.style.opacity = (p <= 0 || p >= 1) ? 0 : a * Math.min(1, p * 8, (1 - p) * 8);
    }
  };
}

// ------------------------------------------------------------------ scenes
export const scenes = [];
/** register a scene visible in [t0, t1] with fades; update(t) drives its content */
export function scene(t0, t1, update, o = {}) {
  const el = h('div.scene', {}, o.parent || document.getElementById('scenes'));
  const sc = { t0, t1, el, update, fi: o.fi ?? .6, fo: o.fo ?? .6, z: o.z ?? 0 };
  el.style.zIndex = sc.z;
  scenes.push(sc);
  return sc;
}
export function runScenes(t) {
  for (const sc of scenes) {
    const on = t >= sc.t0 - .01 && t <= sc.t1 + sc.fo + .01;
    sc.el.style.display = on ? 'block' : 'none';
    if (!on) continue;
    const a = Math.min(pr(t, sc.t0, sc.fi, e3), 1 - pr(t, sc.t1, sc.fo, e3));
    sc.el.style.opacity = a;
    const q = pr(t, sc.t1, sc.fo, e3);
    sc.el.style.filter = q > 0.001 ? `blur(${q * 6}px)` : 'none';
    sc.update(t, t - sc.t0);
  }
}
