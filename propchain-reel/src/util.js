// Deterministic helpers shared by the scene and the timeline.
export function rng(seed) {
  let s = seed >>> 0 || 1;
  return () => { s |= 0; s = (s + 0x6D2B79F5) | 0; let t = Math.imul(s ^ (s >>> 15), 1 | s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}
export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const lerp = (a, b, t) => a + (b - a) * t;
export const range = (t, a, b) => clamp((t - a) / (b - a));
export const smooth = x => x * x * (3 - 2 * x);
export const easeInOutCubic = x => x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
export const easeOutCubic = x => 1 - Math.pow(1 - x, 3);
export const easeInCubic = x => x * x * x;
export const easeOutExpo = x => x >= 1 ? 1 : 1 - Math.pow(2, -10 * x);
export const easeInOutQuint = x => x < 0.5 ? 16 * x ** 5 : 1 - Math.pow(-2 * x + 2, 5) / 2;
export const easeOutQuint = x => 1 - Math.pow(1 - x, 5);
// 0 -> 1 -> 0 envelope with eased edges
export const window01 = (t, a, b, fi = 0.4, fo = 0.4) => smooth(range(t, a, a + fi)) * (1 - smooth(range(t, b - fo, b)));

// C1-continuous cubic Hermite through timed keys: [{t, v:[...]}]
export function hermite(keys, t) {
  if (t <= keys[0].t) return keys[0].v.slice();
  const n = keys.length;
  if (t >= keys[n - 1].t) return keys[n - 1].v.slice();
  let k = 0; while (keys[k + 1].t < t) k++;
  const a = keys[k], b = keys[k + 1], dt = b.t - a.t, s = (t - a.t) / dt;
  const tan = (i) => {
    const p = keys[i - 1], q = keys[i + 1], c = keys[i];
    if (c.hold) return c.v.map(() => 0);
    if (!p) return c.v.map(() => 0);
    if (!q) return c.v.map(() => 0);
    return c.v.map((_, j) => (q.v[j] - p.v[j]) / (q.t - p.t));
  };
  const ma = tan(k), mb = tan(k + 1);
  const s2 = s * s, s3 = s2 * s;
  const h00 = 2 * s3 - 3 * s2 + 1, h10 = s3 - 2 * s2 + s, h01 = -2 * s3 + 3 * s2, h11 = s3 - s2;
  return a.v.map((_, j) => h00 * a.v[j] + h10 * dt * ma[j] + h01 * b.v[j] + h11 * dt * mb[j]);
}
