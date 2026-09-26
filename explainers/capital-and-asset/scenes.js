import { clamp, range, eo5, eo3, ei3, eio3, lerp, L, E, W, WE, TL, mk, sv, svgLayer, px, env, show, fade, draw, drawU, wordsHTML, wordsIn, along, icon, drawIcon, setClip } from './core.js';

const Y = '#FFBE06', INK = '#F4F2EC', LINE = 'rgba(244,242,236,.16)', DIM = 'rgba(244,242,236,.62)';

// ------------------------------------------------------------ shared builders
function headline(root, text, x, y, o = {}) {
  const el = mk('div', o.cls || 'h2', root, { position: 'absolute', left: px(x), top: px(y), width: px(o.w || 1600), textAlign: o.align || 'left', ...(o.style || {}) }, wordsHTML(text, o.hi || []));
  return el;
}
function eyebrow(root, text, x, y, style = {}) {
  return mk('div', 'eyebrow', root, { position: 'absolute', left: px(x), top: px(y), ...style }, text);
}
function typed(el, text, t, s, d = .5) {
  const n = Math.floor(clamp((t - s) / d) * text.length);
  el.textContent = text.slice(0, n);
}
function chip(root, text, x, y, cls = '', ic = null) {
  const c = mk('div', 'chip ' + cls, root, { left: px(x), top: px(y) });
  if (ic) icon(ic, 20, c, {}, 1.75);
  mk('span', null, c, null, text);
  return c;
}

// ============================================================ 0 · TITLE
export function sTitle(root, S) {
  const t1 = L('v02') - 0.05;
  const bg = mk('div', 'abs', root, { inset: 0, overflow: 'hidden' });
  const img = mk('img', 'stockimg', bg, { left: 0, top: 0, width: '1920px', height: '1080px' });
  mk('div', 'abs', bg, { inset: 0, background: 'linear-gradient(90deg, rgba(11,11,12,.94) 0%, rgba(11,11,12,.78) 45%, rgba(11,11,12,.45) 100%)' });
  const logo = mk('img', 'abs', root, { left: '160px', top: '250px', width: '250px' }); logo.src = 'assets/logo-white.svg';
  const eb = eyebrow(root, '', 160, 350);
  const h = headline(root, 'Between Capital and the Asset', 160, 400, { cls: 'h1', w: 1100, hi: ['Asset'] });
  const sub = mk('div', 'body', root, { position: 'absolute', left: '160px', top: '660px', width: '900px', fontSize: '28px' }, 'Who sits in the middle, what must stay independent, what becomes a service, and in what order we go after each.');
  const foot = mk('div', 'label', root, { position: 'absolute', left: '160px', top: '930px' }, 'Prop.com · Propchain &nbsp;·&nbsp; Strategy note · September 2026 · working draft');
  return t => {
    setClip(img, 'city', t, 0, .8);
    const v = env(t, 0, t1, 1.2, .6);
    bg.style.opacity = v.a * .95; img.style.transform = `scale(${1.04 + .05 * range(t, 0, t1)})`;
    show(logo, t, .15, t1, { dy: 12 });
    typed(eb, 'Strategy note · the intermediary map', t, .5, .7); show(eb, t, .45, t1, { dy: 0 });
    wordsIn(h, t, .7, .09, t1);
    show(sub, t, 1.6, t1, { dy: 18 });
    show(foot, t, 2.1, t1, { dy: 0 });
  };
}

// ============================================================ 1a · MONTAGE of the middle
export function sMontage(root) {
  const t0 = L('v02') - 0.1, t1 = W('v02', 'Some') + 0.25;
  const names = [['broker', 'Broker', 'brokers'], ['valuer', 'Valuer', 'valuers'], ['signing', 'Lawyer', 'lawyers'], ['notary', 'Notary', 'notaries'], ['lender', 'Lender', 'lenders']];
  const w = 336, g = 16, x0 = (1920 - 5 * w - 4 * g) / 2;
  const items = names.map(([id, lab, word], i) => {
    const f = mk('div', 'clipframe', root, { left: px(x0 + i * (w + g)), top: '170px', width: px(w), height: '740px', borderRadius: '10px' });
    const img = mk('img', null, f);
    mk('div', 'shade', f);
    const l = mk('div', 'abs', f, { left: '24px', bottom: '26px' });
    mk('div', 'label', l, { color: Y, marginBottom: '6px' }, String(i + 1).padStart(2, '0'));
    mk('div', null, l, { font: '400 30px Inter', letterSpacing: '-.02em' }, lab);
    return { f, img, l, id, s: W('v02', word) - .15 };
  });
  return t => {
    items.forEach(({ f, img, l, id, s }, i) => {
      const u = eo5(range(t, s, s + .8));
      const o = ei3(range(t, t1 - .55 + i * .03, t1));
      f.style.clipPath = `inset(${(1 - u) * 100}% 0 0 0 round 10px)`;
      f.style.opacity = 1 - o; f.style.transform = `translateY(${-30 * o}px)`; f.style.filter = o > .01 ? `blur(${o * 8}px)` : 'none';
      img.style.transform = `scale(${1.15 - .15 * u})`;
      setClip(img, id, t, s);
      show(l, t, s + .35, 1e9, { dy: 14 });
    });
  };
}

// ============================================================ 1b · THE MIDDLE: crowd, two businesses, the question
const CROWD = ['Broker', 'Originator', 'Debt adviser', 'Valuer', 'Data provider', 'Technical DD', 'ESG DD', 'KYC · AML', 'Lawyers', 'Auditor',
  'Depositary', 'AIFM', 'Notary', 'Registry', 'Escrow bank', 'Fund admin', 'Transfer agent', 'Asset manager', 'Property manager', 'Vendors'];
export function sMiddle(root) {
  const t0 = W('v02', 'Some') - 0.15, t1 = L('v06') - 0.1;
  const tDots = W('v03', 'Two'), tProp = W('v03', 'Prop.com'), tRail = L('v04'), tQ = L('v05');
  const svg = svgLayer(root);
  const main = sv('path', { d: 'M 250 540 L 1670 540', stroke: LINE, 'stroke-width': 2, fill: 'none', pathLength: 1 }, svg);
  const mainP = sv('path', { d: 'M 250 540 L 1670 540', fill: 'none' }, svg);
  // end nodes
  const node = (x, lab, ic) => {
    const g = mk('div', 'abs', root, { left: px(x - 62), top: '478px', width: '124px', height: '124px' });
    const c = mk('div', 'abs', g, { inset: 0, borderRadius: '50%', border: '1.5px solid ' + INK, background: '#0E0E10' });
    const i = icon(ic, 48, g, { position: 'absolute', left: '38px', top: '38px' });
    const l = mk('div', 'label', g, { position: 'absolute', top: '146px', left: '-40px', width: '204px', textAlign: 'center', color: INK }, lab);
    return { g, i };
  };
  const cap = node(190, 'Capital', 'banknote'), ast = node(1730, 'Asset', 'building-2');
  const title = eyebrow(root, '', 0, 190, { width: '1920px', textAlign: 'center' });
  // crowd
  const rnd = k => { const x = Math.sin(k * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
  const cols = 5, rows = 4;
  const P = CROWD.map((name, i) => {
    const c = i % cols, r = Math.floor(i / cols);
    const x = 470 + c * 245 + (rnd(i) - .5) * 70 + (r % 2) * 50, y = 305 + r * 155 + (rnd(i + 40) - .5) * 50;
    const el = mk('div', 'chip', root, { left: px(x), top: px(y), height: '42px', fontSize: '16px', padding: '0 16px' }, name);
    const dx = 400 + i * (1120 / 19), dy = 540 + (rnd(i + 80) - .5) * 70;
    const dot = sv('circle', { cx: dx, cy: dy, r: 7, fill: INK }, svg);
    return { el, x, y, dx, dy, dot, s: W('v02', 'twenty') - .2 + rnd(i + 7) * 1.4 };
  });
  // Prop.com lane
  const lane = mk('div', 'panel', root, { left: '400px', top: '250px', width: '1120px', height: '130px', borderColor: 'rgba(255,190,6,.45)' });
  mk('div', 'eyebrow', lane, { position: 'absolute', left: '34px', top: '28px' }, 'Prop.com · outcome services');
  mk('div', null, lane, { position: 'absolute', left: '34px', top: '62px', font: '300 34px Inter', letterSpacing: '-.02em' }, 'Desk work, delivered faster and cheaper');
  const cash = chip(lane, 'Cash flow now', 850, 44, '', 'banknote');
  const laneLinks = [2, 5, 9, 12, 15, 17].map(i => sv('path', { d: `M ${P[i].dx} ${P[i].dy - 10} L ${P[i].dx} 382`, stroke: 'rgba(255,190,6,.5)', 'stroke-width': 1.2, 'stroke-dasharray': '4 6', fill: 'none' }, svg));
  // Propchain rail
  const railG = sv('g', {}, svg);
  const r1 = sv('path', { d: 'M 250 742 L 1670 742', stroke: INK, 'stroke-width': 2, fill: 'none', pathLength: 1 }, railG);
  const r2 = sv('path', { d: 'M 250 756 L 1670 756', stroke: INK, 'stroke-width': 2, fill: 'none', pathLength: 1 }, railG);
  const ties = []; for (let x = 262; x < 1670; x += 28) ties.push(sv('path', { d: `M ${x} 736 L ${x} 762`, stroke: 'rgba(244,242,236,.3)', 'stroke-width': 1.5 }, railG));
  const drops = P.map(p => sv('path', { d: `M ${p.dx} ${p.dy + 9} L ${p.dx} 740`, stroke: 'rgba(244,242,236,.45)', 'stroke-width': 1, fill: 'none', pathLength: 1 }, svg));
  const railTx = mk('div', 'abs', root, { left: '400px', top: '790px' });
  mk('div', 'eyebrow', railTx, { color: INK }, 'Propchain · rails');
  mk('div', null, railTx, { font: '300 34px Inter', letterSpacing: '-.02em', marginTop: '12px' }, 'The standard everyone runs on');
  const comp = chip(root, "Including Prop.com's competitors", 1100, 820, 'outl');
  // the question
  const focus = 3; // the valuer
  const ring = sv('circle', { cx: P[focus].dx, cy: P[focus].dy, r: 22, fill: 'none', stroke: Y, 'stroke-width': 2 }, svg);
  const verbs = [['Own it?', 'own'], ['Tool it?', 'tool'], ['Onboard it?', 'onboard']].map(([tx, w], i) => {
    const c = chip(root, tx, 0, 0, i === 0 ? 'yl' : 'outl');
    c.style.left = px(P[focus].dx + 70); c.style.top = px(300 + i * 58);
    return { c, s: W('v05', w) - .1 };
  });
  const vLink = sv('path', { d: `M ${P[focus].dx + 12} ${P[focus].dy - 18} C ${P[focus].dx + 30} 420, ${P[focus].dx + 40} 400, ${P[focus].dx + 66} 380`, stroke: Y, 'stroke-width': 1.5, fill: 'none', pathLength: 1 }, svg);
  const order = mk('div', 'abs', root, { left: '1060px', top: '300px' });
  mk('div', 'eyebrow', order, { color: INK, marginBottom: '18px' }, 'And in which order?');
  const slots = [1, 2, 3, 4, 5].map(n => mk('div', 'abs', order, { left: px((n - 1) * 78), top: '44px', width: '58px', height: '58px', borderRadius: '50%', border: '1.5px dashed rgba(244,242,236,.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', font: '500 20px Mono', color: DIM }, '?'));
  const pulse = sv('circle', { r: 6, fill: Y }, svg);
  const glow = sv('circle', { r: 16, fill: 'rgba(255,190,6,.18)' }, svg);

  return t => {
    const out = ei3(range(t, t1 - .5, t1));
    root.style.opacity = 1 - out; root.style.filter = out > .01 ? `blur(${out * 6}px)` : 'none';
    show(cap.g, t, t0 + .1, 1e9, { dy: 0, sc: .2 }); show(ast.g, t, t0 + .3, 1e9, { dy: 0, sc: .2 });
    drawIcon(cap.i, t, t0 + .2); drawIcon(ast.i, t, t0 + .4);
    draw(main, t, t0 + .2, 1.2);
    typed(title, 'Some twenty parties between capital and the asset', t, t0 + .4, .9); show(title, t, t0 + .35, tDots + .2, { dy: 0 });
    const k = eio3(range(t, tDots, tDots + 1.3));
    P.forEach((p, i) => {
      const a = eo5(range(t, p.s, p.s + .7));
      const kk = eio3(range(t, tDots + i * .02, tDots + 1.1 + i * .02));
      p.el.style.opacity = a * (1 - kk);
      p.el.style.transform = `translate(${(p.dx - p.x - 50) * kk}px, ${(p.dy - p.y - 20) * kk + (1 - a) * 20}px) scale(${1 - .8 * kk})`;
      p.el.style.filter = a < .99 ? `blur(${(1 - a) * 8}px)` : 'none';
      p.dot.setAttribute('r', 7 * kk);
      const hi = i === focus ? range(t, tQ, tQ + .4) : 0;
      p.dot.setAttribute('fill', hi > 0 ? Y : INK);
      p.dot.style.opacity = t > tQ ? (i === focus ? 1 : lerp(1, .45, range(t, tQ, tQ + .6))) : 1;
    });
    // pulse trying to cross the crowd
    const pu = range(t, W('v02', 'between') - .2, W('v02', 'between') + 2.6);
    const pa = pu > 0 && pu < 1 ? 1 : 0; const pt = along(mainP, eio3(pu));
    pulse.setAttribute('cx', pt.x); pulse.setAttribute('cy', pt.y); glow.setAttribute('cx', pt.x); glow.setAttribute('cy', pt.y);
    pulse.style.opacity = pa; glow.style.opacity = pa;
    // Prop.com lane
    const qd = 1 - .88 * range(t, tQ, tQ + .6);
    show(lane, t, tProp - .1, 1e9, { dy: -20, min: 0 }); lane.style.opacity *= qd;
    show(cash, t, W('v03', 'faster'), 1e9, { dy: 10 });
    laneLinks.forEach((l, i) => { fade(l, env(t, tProp + .3 + i * .08).a * .9 * qd); });
    // rail
    draw(r1, t, tRail - .1, 1.4); draw(r2, t, tRail, 1.4);
    ties.forEach((ti, i) => fade(ti, range(t, tRail + i * .02, tRail + .3 + i * .02) * qd));
    r1.style.opacity = r2.style.opacity = qd;
    drops.forEach((d, i) => { draw(d, t, W('v04', 'standard') + i * .05, .5); d.style.opacity = qd; });
    show(railTx, t, tRail + .2, 1e9, { dy: 16 }); railTx.style.opacity *= qd;
    show(comp, t, W('v04', 'competitors') - .2, 1e9, { dy: 12 }); comp.style.opacity *= qd;
    // question
    const ru = eo5(range(t, tQ + .1, tQ + .8));
    ring.setAttribute('r', 10 + 16 * ru); ring.style.opacity = ru;
    draw(vLink, t, W('v05', 'own') - .3, .5);
    verbs.forEach(({ c, s }) => show(c, t, s, 1e9, { dx: -20, dy: 0 }));
    show(order, t, W('v05', 'which') - .3, 1e9, { dy: 16 });
    slots.forEach((s, i) => show(s, t, W('v05', 'which') + i * .1, 1e9, { dy: 10 }));
  };
}

// ============================================================ 2 · THE RULE
const ROWS = [
  { k: 'act', eb: 'The act', title: 'Carries the liability', ex: [['pen-line', 'Signature'], ['stamp', 'Deed'], ['scale', 'Audit opinion']], vlab: 'Stays independent', vtx: 'We tool it', vic: 'wrench', vcls: 'outl', val: 'Signed valuation' },
  { k: 'process', eb: 'The process', title: 'Prepares the act', ex: [['folder-open', 'Data rooms'], ['calculator', 'Models'], ['file-pen-line', 'Draft deeds']], vlab: 'Becomes a', vtx: 'Prop.com service', vic: 'briefcase', vcls: 'yl', val: 'Model · comparables · AVM' },
  { k: 'data', eb: 'The data', title: 'Consumed and emitted', ex: [], vlab: 'Attested', vtx: 'Propchain attests it', vic: 'badge-check', vcls: 'outl', val: 'Mark · inputs · lineage' },
];
export function sRule(root) {
  const t0 = L('v06') - 0.3, t1 = L('v11') - 0.05;
  const tSplit = W('v06', 'splits') - .1, tV = L('v10');
  const X = 160, Wd = 1600, H = 196, Ys = [292, 516, 740];
  const h1 = headline(root, 'Every party in the middle splits in three', 160, 128, { w: 1400 });
  const h2 = headline(root, 'Take the valuer', 160, 128, { w: 1100, hi: ['valuer'] });
  const vf = mk('div', 'clipframe', root, { left: '1380px', top: '96px', width: '380px', height: '176px', borderRadius: '12px' });
  const vimg = mk('img', null, vf); mk('div', 'shade', vf);
  mk('div', 'label', vf, { position: 'absolute', left: '18px', bottom: '14px', color: INK }, 'Valuer');
  const rows = ROWS.map((r, ri) => {
    const el = mk('div', 'panel', root, { left: px(X), top: px(Ys[ri]), width: px(Wd), height: px(H) });
    mk('div', 'eyebrow', el, { position: 'absolute', left: '40px', top: '44px' }, r.eb);
    mk('div', 'h3', el, { position: 'absolute', left: '40px', top: '80px', fontSize: '38px' }, r.title);
    const ex = r.ex.map(([ic, lab], i) => {
      const g = mk('div', 'abs', el, { left: px(560 + i * 175), top: '42px', width: '150px', textAlign: 'center' });
      const ii = icon(ic, 56, g, { margin: '0 auto' });
      mk('div', 'label', g, { marginTop: '18px', color: INK, fontSize: '14px' }, lab);
      return { g, ii };
    });
    const vb = mk('div', 'abs', el, { left: '1250px', top: '52px', width: '320px' });
    mk('div', 'label', vb, { marginBottom: '14px' }, r.vlab);
    const vc = chip(vb, r.vtx, 0, 0, r.vcls, r.vic); vc.style.position = 'relative'; vc.style.display = 'inline-flex';
    const val = mk('div', null, el, { position: 'absolute', left: '560px', top: '74px', font: '300 40px Inter', letterSpacing: '-.02em', whiteSpace: 'nowrap' }, r.val);
    return { el, ex, vb, val };
  });
  const one = mk('div', 'abs', rows[1].el, { inset: '-1px', borderRadius: '18px', background: '#131315', border: '1px solid rgba(244,242,236,.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '22px', font: '300 40px Inter', letterSpacing: '-.02em' });
  icon('user-round', 40, one); mk('span', null, one, null, 'One party in the middle');
  // act extra: independence
  const indep = mk('div', 'label', rows[0].el, { position: 'absolute', left: '40px', top: '138px', color: Y }, 'Value = independence');
  // process extra: hours & fee bars
  const bars = ['Hours', 'Fee'].map((lab, i) => {
    const g = mk('div', 'abs', rows[1].el, { left: '1080px', top: px(52 + i * 52), width: '130px' });
    mk('div', 'label', g, { fontSize: '12px', marginBottom: '8px' }, lab);
    const tr = mk('div', null, g, { height: '6px', background: 'rgba(244,242,236,.12)', borderRadius: '3px', overflow: 'hidden' });
    const f = mk('div', null, tr, { height: '100%', width: '0%', background: Y });
    return f;
  });
  const most = mk('div', 'label', rows[1].el, { position: 'absolute', left: '1080px', top: '152px', color: Y, fontSize: '12px' }, 'Most of both');
  // data flows
  const dsvg = sv('svg', { width: 640, height: 196, style: 'position:absolute;left:520px;top:0;overflow:visible' }, rows[2].el);
  const flows = [['Rent roll', 'NOI', 62, 'rent'], ['Comparables', 'Mark', 134, 'comparables']].map(([a, b, y, w]) => {
    const la = mk('div', 'chip', rows[2].el, { left: '540px', top: px(y - 20), height: '40px', fontSize: '14px' }, a);
    const lb = mk('div', 'chip yl', rows[2].el, { left: '1010px', top: px(y - 20), height: '40px', fontSize: '14px' }, b);
    const p = sv('path', { d: `M 205 ${y} L 480 ${y}`, stroke: 'rgba(244,242,236,.5)', 'stroke-width': 1.5, fill: 'none', pathLength: 1 }, dsvg);
    const ah = sv('path', { d: `M 472 ${y - 6} L 480 ${y} L 472 ${y + 6}`, stroke: 'rgba(244,242,236,.5)', 'stroke-width': 1.5, fill: 'none' }, dsvg);
    const pp = sv('path', { d: `M 205 ${y} L 480 ${y}`, fill: 'none' }, dsvg);
    const dot = sv('circle', { r: 5, fill: Y }, dsvg);
    return { la, lb, p, ah, pp, dot, s: W('v09', w) - .1 };
  });
  const act = [L('v07') - .2, L('v08') - .2, L('v09') - .2];
  const actV = [W('v10', 'signature') - .2, W('v10', 'model') - .2, W('v10', 'mark') - .2];

  return t => {
    const out = ei3(range(t, t1 - .5, t1));
    root.style.opacity = 1 - out; root.style.filter = out > .01 ? `blur(${out * 6}px)` : 'none';
    show(h1, t, t0 + .2, tV - .1, { dy: 20 }); wordsIn(h1, t, t0 + .25, .05);
    show(h2, t, tV, 1e9, { dy: 20 }); wordsIn(h2, t, tV + .05, .07);
    show(vf, t, tV + .1, 1e9, { dy: 0, dx: 30 }); setClip(vimg, 'valuer', t, tV);
    // split: rows start stacked in the middle
    const k = eio3(range(t, tSplit, tSplit + 1.1));
    one.style.opacity = 1 - range(t, tSplit, tSplit + .5);
    rows.forEach((r, i) => {
      const a0 = eo5(range(t, t0 + .5, t0 + 1.2));
      const y = lerp(Ys[1], Ys[i], k);
      r.el.style.top = px(y);
      // active state
      let active = -1;
      for (let j = 0; j < 3; j++) if (t >= act[j]) active = j;
      if (t >= actV[0]) { active = -1; for (let j = 0; j < 3; j++) if (t >= actV[j]) active = j; }
      const isA = active === i, anyA = active >= 0;
      r.el.style.opacity = (i === 1 ? a0 : a0 * k) * (anyA && !isA ? .42 : 1);
      r.el.style.borderColor = isA ? 'rgba(255,190,6,.55)' : LINE;
      r.el.style.background = isA ? 'rgba(255,190,6,.045)' : 'rgba(244,242,236,.035)';
      // examples
      const vOut = range(t, actV[0] - .3, actV[0] + .1);
      r.ex.forEach((e, j) => {
        const s = i === 0 ? W('v07', ['signature', 'deed', 'audit'][j]) - .15 : W('v08', ['data', 'models', 'draft'][j]) - .15;
        show(e.g, t, s, actV[0], { dy: 14 }); drawIcon(e.ii, t, s);
      });
      show(r.val, t, actV[i], 1e9, { dy: 18 });
      const vs = [W('v07', 'tool'), W('v08', 'Prop.com'), W('v09', 'Propchain')][i] - .2;
      show(r.vb, t, vs, 1e9, { dx: 24, dy: 0 });
    });
    show(indep, t, W('v07', 'independence') - .2, actV[0], { dy: 8 });
    const bu = eo3(range(t, W('v08', 'most') - .1, W('v08', 'most') + 1.1));
    bars[0].style.width = (bu * 78) + '%'; bars[1].style.width = (bu * 70) + '%';
    bars.forEach(b => b.parentNode.parentNode.style.opacity = env(t, W('v08', 'desk') - .2, actV[0], .6).a);
    show(most, t, W('v08', 'fee') - .1, actV[0], { dy: 6 });
    flows.forEach(f => {
      const e = actV[0];
      show(f.la, t, f.s, e, { dx: -14, dy: 0 });
      const u = draw(f.p, t, f.s + .25, .7); f.p.style.opacity = f.ah.style.opacity = env(t, f.s, e).a; f.ah.style.opacity *= u > .95 ? 1 : 0;
      show(f.lb, t, f.s + .8, e, { dx: 14, dy: 0 });
      const pu = range(t, f.s + .3, f.s + 1.1); const pt = along(f.pp, eo3(pu));
      f.dot.setAttribute('cx', pt.x); f.dot.setAttribute('cy', pt.y); f.dot.style.opacity = pu > 0 && pu < 1 ? 1 : 0;
    });
  };
}

// ============================================================ 2b · INDEPENDENCE IS THE PRODUCT
export function sIndep(root) {
  const t0 = L('v11') - 0.25, t1 = L('v12') - 0.1;
  const tI = W('v11', 'Independence') - .15;
  const bg = mk('div', 'abs', root, { inset: 0, overflow: 'hidden' });
  const img = mk('img', 'stockimg', bg, { width: '1920px', height: '1080px' });
  mk('div', 'abs', bg, { inset: 0, background: 'rgba(11,11,12,.72)' });
  const svg = svgLayer(root);
  const g = mk('div', 'abs', root, { inset: 0 });
  const seal = mk('div', 'abs', g, { left: '560px', top: '330px', width: '240px', height: '240px', borderRadius: '50%', border: '1.5px solid ' + INK, background: 'rgba(11,11,12,.6)' });
  const si = icon('stamp', 84, seal, { position: 'absolute', left: '78px', top: '62px' });
  mk('div', 'label', seal, { position: 'absolute', top: '166px', width: '240px', textAlign: 'center', color: INK }, 'The act');
  const kinds = mk('div', 'label', g, { position: 'absolute', left: '430px', top: '600px', width: '500px', textAlign: 'center' }, 'An opinion · a deed · a mark');
  const party = chip(g, 'The party that profits from the deal', 1130, 428, 'outl', 'coins');
  const link = sv('path', { d: 'M 802 450 L 1126 450', stroke: Y, 'stroke-width': 2, fill: 'none', pathLength: 1, 'stroke-dasharray': '1 1' }, svg);
  const meter = mk('div', 'abs', g, { left: '480px', top: '680px', width: '400px' });
  mk('div', 'label', meter, { marginBottom: '12px' }, 'Worth to a buyer, lender, regulator');
  const tr = mk('div', null, meter, { height: '8px', background: 'rgba(244,242,236,.12)', borderRadius: '4px' });
  const fill = mk('div', null, tr, { height: '100%', width: '100%', background: INK, borderRadius: '4px' });
  const whatever = mk('div', 'label', g, { position: 'absolute', left: '480px', top: '740px', color: Y }, 'Whatever its quality');
  const big = headline(root, 'Independence is the product.', 0, 470, { cls: 'h1', w: 1920, align: 'center', hi: ['Independence'] });
  return t => {
    const out = ei3(range(t, t1 - .5, t1));
    root.style.opacity = 1 - out;
    const v = env(t, t0, 1e9, .6); bg.style.opacity = v.a; setClip(img, 'signing', t, t0, .7);
    img.style.transform = `scale(${1.06 - .04 * range(t, t0, t1)})`;
    const gOut = range(t, tI - .4, tI);
    g.style.opacity = 1 - gOut; svg.style.opacity = 1 - gOut;
    show(seal, t, t0 + .1, 1e9, { dy: 0, sc: .1 }); drawIcon(si, t, t0 + .2);
    show(kinds, t, t0 + .5, 1e9, { dy: 8 });
    show(party, t, W('v11', 'party') - .1, 1e9, { dx: 30, dy: 0 });
    draw(link, t, W('v11', 'profits') - .2, .6);
    show(meter, t, t0 + .4, 1e9, { dy: 10 });
    const drop = eio3(range(t, W('v11', 'worth') - .1, W('v11', 'worth') + .9));
    fill.style.width = (100 - 64 * drop) + '%'; fill.style.background = drop > .5 ? DIM : INK;
    seal.style.borderColor = drop > .5 ? 'rgba(244,242,236,.35)' : INK;
    show(whatever, t, W('v11', 'whatever') - .1, 1e9, { dy: 8 });
    show(big, t, tI, 1e9, { dy: 0, blur: 0 }); wordsIn(big, t, tI, .12);
  };
}

// ============================================================ 3 · THE MAP: eight layers, one verb each
const LAYERS = [
  ['Participants', [['LPs', 'o'], ['GPs, managers', 'o'], ['Lenders', 'o', 'lenders'], ['Buyers', 'o', 'buyers'], ['Sellers', 'o', 'sellers'], ['Tenants', 'o', 'tenants']]],
  ['Origination', [['Brokers', 's'], ['Originators', 's'], ['Placement', 's'], ['Debt advisers', 's', 'debt']]],
  ['Pricing', [['Underwriting', 's', 'underwriting'], ['Valuers', 't', 'valuer'], ['Data providers', 'n']]],
  ['Verification', [['Technical DD', 's'], ['ESG DD', 's'], ['Legal DD', 's'], ['KYC · AML', 's']]],
  ['Guardrails', [['Lawyers', 't', 'lawyers'], ['Auditor', 't', 'auditor'], ['Depositary', 't', 'depositary'], ['AIFM', 't'], ['Regulator', 'n']]],
  ['Settlement', [['Notary', 't', 'notary'], ['Registry', 't', 'registry'], ['Escrow bank', 't'], ['Payments', 's', 'payments']]],
  ['Administration', [['Fund admin', 's', 'administration'], ['Transfer agent', 's'], ['Reporting', 's', 'reporting'], ['Servicing', 's']]],
  ['Performance', [['Asset managers', 's', 'asset'], ['Property mgrs', 's'], ['Facility mgrs', 's'], ['Vendors', 'n']]],
];
export function sMap(root) {
  const t0 = L('v12') - 0.3, t1 = L('v17') - 0.05;
  const tLeg = L('v13') - .1, tRe = W('v16', 'Prop.com', 0) + .1;
  const x0 = 100, cw = 205, gap = 10;
  const svg = svgLayer(root);
  const h = headline(root, 'Eight layers, in the order a deal moves', 100, 118, { cls: 'h3', w: 1300 });
  const h2 = headline(root, 'Every party gets one verb', 100, 118, { cls: 'h3', w: 1300, hi: ['one', 'verb'] });
  const dir = mk('div', 'label', root, { position: 'absolute', right: '110px', top: '136px', color: INK }, 'Capital &nbsp;→&nbsp; Asset');
  const chain = sv('path', { d: `M ${x0 + cw / 2} 344 L ${x0 + 7 * (cw + gap) + cw / 2} 344`, stroke: 'rgba(244,242,236,.3)', 'stroke-width': 1.5, fill: 'none', pathLength: 1 }, svg);
  const chainP = sv('path', { d: `M ${x0 + cw / 2} 344 L ${x0 + 7 * (cw + gap) + cw / 2} 344`, fill: 'none' }, svg);
  const pulse = sv('circle', { r: 6, fill: Y }, svg);
  const colStart = i => L('v12') + .5 + i * .42;
  const heads = LAYERS.map(([name], i) => {
    const x = x0 + i * (cw + gap);
    const g = mk('div', 'abs', root, { left: px(x), top: '252px', width: px(cw) });
    mk('div', 'label', g, { color: Y, fontSize: '14px' }, String(i + 1).padStart(2, '0'));
    mk('div', null, g, { font: '500 23px Inter', marginTop: '6px', letterSpacing: '-.01em' }, name);
    const n = sv('circle', { cx: x + cw / 2, cy: 344, r: 5, fill: '#0E0E10', stroke: INK, 'stroke-width': 1.5 }, svg);
    return { g, n };
  });
  // chips
  const C = [];
  LAYERS.forEach(([, parties], i) => parties.forEach(([name, v, word], j) => {
    const x = x0 + i * (cw + gap), y = 380 + j * 64;
    const el = mk('div', 'chip', root, { left: px(x), top: px(y), width: px(cw), height: '50px', fontSize: '15px', padding: '0 14px', letterSpacing: '.03em', gap: '9px' });
    const ic = icon(v === 't' ? 'lock' : v === 'o' ? 'user-round' : 'briefcase', 17, el, { flex: 'none' }, 2);
    mk('span', null, el, { overflow: 'hidden', textOverflow: 'ellipsis' }, name);
    C.push({ el, ic, v, x, y, i, j, word, name });
  }));
  // when each chip gets its verb
  const vid = { o: 'v14', t: 'v15', s: 'v16' };
  let serveK = 0;
  C.forEach(c => {
    if (c.v === 'n') { c.tv = 1e9; return; }
    if (c.word) { try { c.tv = W(vid[c.v], c.word) - .05; } catch (e) { c.tv = null; } }
    if (c.tv == null) {
      if (c.v === 'o') c.tv = W('v14', 'Investors') + (c.name === 'LPs' ? 0 : .25);
      else if (c.v === 't') c.tv = W('v15', 'each') + (c.name === 'AIFM' ? 0 : .2);
      else c.tv = W('v16', 'payments') + .45 + (serveK++) * .09;
    }
  });
  // regroup targets
  const G = { o: [], t: [], s: [] };
  C.forEach(c => { if (c.v !== 'n') G[c.v].push(c); });
  const gx = { o: 100, t: 420, s: 990 }, gw = 230, gc = { o: 1, t: 2, s: 3 };
  for (const k of 'ots') G[k].forEach((c, n) => { c.tx = gx[k] + (n % gc[k]) * (gw + 16); c.ty = 400 + Math.floor(n / gc[k]) * 62; });
  const gh = [['o', 'Onboard', 'Participants: the market'], ['t', 'Tool', 'Stays independent'], ['s', 'Serve', 'Prop.com outcome services']].map(([k, a, b]) => {
    const g = mk('div', 'abs', root, { left: px(gx[k]), top: '262px' });
    mk('div', null, g, { font: '300 44px Inter', letterSpacing: '-.03em', color: k === 's' ? Y : INK }, a);
    mk('div', 'label', g, { marginTop: '6px' }, b);
    return g;
  });
  // legend
  const leg = mk('div', 'abs', root, { left: '100px', top: '900px', display: 'flex', gap: '26px' });
  const lg = [['Onboard', 'grey', 'user-round', 'v14', 'onboards'], ['Tool', 'outl', 'lock', 'v15', 'tool'], ['Serve', 'yl', 'briefcase', 'v16', 'serves']].map(([tx, cls, ic, id, w]) => {
    const c = chip(leg, tx, 0, 0, cls, ic); c.style.position = 'relative'; return { c, s: W(id, w) - .1 };
  });
  return t => {
    const out = ei3(range(t, t1 - .5, t1));
    root.style.opacity = 1 - out; root.style.filter = out > .01 ? `blur(${out * 6}px)` : 'none';
    const reK = eio3(range(t, tRe, tRe + 1.8));
    show(h, t, t0 + .2, tLeg + .3, { dy: 16 }); wordsIn(h, t, t0 + .25, .05);
    show(h2, t, tLeg + .3, 1e9, { dy: 16 }); wordsIn(h2, t, tLeg + .35, .07);
    show(dir, t, t0 + .6, tRe, { dy: 0 });
    draw(chain, t, colStart(0), 3.2, x => x); chain.style.opacity = 1 - reK;
    const pu = range(t, colStart(0), colStart(0) + 3.4); const pt = along(chainP, pu);
    pulse.setAttribute('cx', pt.x); pulse.setAttribute('cy', pt.y); pulse.style.opacity = (pu > 0 && pu < 1 ? 1 : 0);
    heads.forEach((hd, i) => { show(hd.g, t, colStart(i), tRe + .3, { dy: 14 }); fade(hd.n, env(t, colStart(i), tRe + .3, .4).a); });
    C.forEach(c => {
      const s = colStart(c.i) + .15 + c.j * .07;
      const v = env(t, s, 1e9, .6);
      const on = t >= c.tv; const u = eo3(range(t, c.tv, c.tv + .35));
      const isN = c.v === 'n';
      const fadeN = isN ? 1 - range(t, tRe, tRe + .6) : 1;
      const dimOthers = t > tLeg + .4 && !on ? .55 : 1;
      c.el.style.opacity = v.a * fadeN * (on ? 1 : dimOthers);
      const x = c.tx != null ? lerp(c.x, c.tx, reK) : c.x, y = c.ty != null ? lerp(c.y, c.ty, reK) : c.y;
      c.el.style.left = px(x); c.el.style.top = px(y);
      c.el.style.width = px(lerp(205, c.tx != null ? gw : 205, reK));
      c.el.style.transform = `translateY(${(1 - v.i) * 16}px) scale(${1 + .08 * Math.sin(Math.PI * u)})`;
      c.el.className = 'chip ' + (on ? { o: 'grey', t: 'outl', s: 'yl' }[c.v] : '');
      c.ic.style.opacity = on ? u : 0; c.ic.style.width = on ? '17px' : '0px';
    });
    gh.forEach((g, i) => show(g, t, tRe + .6 + i * .15, 1e9, { dy: 14 }));
    lg.forEach(({ c, s }, i) => { show(c, t, tLeg + i * .15, tRe + .4, { dy: 10 }); c.style.boxShadow = t > s && t < s + 1.8 ? '0 0 0 3px rgba(255,190,6,.35)' : 'none'; });
  };
}

// ============================================================ 4a · THE OFFER: seats fold into a desk
const SEATS = [['Acquisitions analyst', 4], ['Fund controller', 4], ['Reporting, IR', 4], ['Asset manager', 3], ['Debt, treasury', 3], ['ESG officer', 3], ['Technical, project', 2], ['In-house legal', 2], ['Property management', 1]];
export function sOffer(root) {
  const t0 = L('v17') - 0.3, t1 = L('v19') - 0.05;
  const tG = W('v17', 'four') - .35, tF = W('v17', 'replaced') - .1;
  const bg = mk('div', 'abs', root, { inset: 0, overflow: 'hidden' });
  const img = mk('img', 'stockimg', bg, { width: '1920px', height: '1080px' });
  mk('div', 'abs', bg, { inset: 0, background: 'linear-gradient(0deg, rgba(11,11,12,.92) 0%, rgba(11,11,12,.55) 55%, rgba(11,11,12,.35) 100%)' });
  const cap = mk('div', 'abs', root, { left: '160px', top: '690px', width: '1500px' });
  mk('div', 'eyebrow', cap, { marginBottom: '22px' }, 'Prop.com · the offer');
  const hl = headline(cap, 'We sell the outcome of a desk, not the AI.', 0, 50, { cls: 'h2', w: 1500, hi: ['outcome'] });
  hl.style.position = 'relative'; hl.style.top = '0';
  const gr = mk('div', 'abs', root, { inset: 0 });
  const eb = eyebrow(gr, 'Seats in a mid-size manager', 160, 200);
  const dsl = mk('div', 'label', gr, { position: 'absolute', left: '160px', top: '236px', fontSize: '13px' }, 'Bar: desk share of the role · qualitative');
  const cw = 330, ch = 118, gx = 22, gy = 24;
  const seats = SEATS.map(([name, lvl], i) => {
    const x = 160 + (i % 3) * (cw + gx), y = 300 + Math.floor(i / 3) * (ch + gy);
    const el = mk('div', 'panel', gr, { left: px(x), top: px(y), width: px(cw), height: px(ch) });
    icon('user-round', 30, el, { position: 'absolute', left: '26px', top: '26px' });
    mk('div', null, el, { position: 'absolute', left: '72px', top: '28px', font: '400 21px Inter', whiteSpace: 'nowrap' }, name);
    const bars = [0, 1, 2, 3].map(k => mk('div', 'abs', el, { left: px(72 + k * 44), top: '76px', width: '38px', height: '6px', borderRadius: '3px', background: k < lvl ? INK : 'rgba(244,242,236,.14)' }));
    return { el, x, y, lvl, bars };
  });
  const desk = mk('div', 'abs', gr, { left: '1330px', top: '380px', width: '430px', height: '250px', borderRadius: '18px', background: Y, color: '#0B0B0C' });
  icon('briefcase', 44, desk, { position: 'absolute', left: '36px', top: '36px' }, 1.6);
  mk('div', 'label', desk, { position: 'absolute', left: '36px', top: '112px', color: 'rgba(11,11,12,.7)' }, 'Prop.com');
  mk('div', null, desk, { position: 'absolute', left: '36px', top: '140px', font: '400 36px/1.1 Inter', letterSpacing: '-.02em' }, 'One outsourced desk');
  const res = mk('div', 'label', gr, { position: 'absolute', left: '1330px', top: '660px', color: INK, lineHeight: '1.8' }, 'Same work · faster<br>Lower fixed cost');
  return t => {
    const out = ei3(range(t, t1 - .5, t1));
    root.style.opacity = 1 - out;
    const bgv = env(t, t0, tG + .5, .6, .7); bg.style.opacity = bgv.a; setClip(img, 'analyst', t, t0, .8);
    img.style.transform = `scale(${1.03 + .04 * range(t, t0, tG)})`;
    show(cap, t, t0 + .2, tG + .3, { dy: 0, blur: 0 }); wordsIn(hl, t, t0 + .3, .07);
    gr.style.opacity = range(t, tG, tG + .4);
    show(eb, t, tG, 1e9, { dy: 0 }); show(dsl, t, tG + .3, 1e9, { dy: 0 });
    const fk = eio3(range(t, tF, tF + 1.2));
    seats.forEach((s, i) => {
      const v = env(t, tG + .1 + i * .07, 1e9, .6);
      const moving = i < 5;
      const mk_ = moving ? eio3(range(t, tF + i * .08, tF + 1.0 + i * .08)) : 0;
      const dx = (1545 - (s.x + cw / 2)) * mk_, dy = (505 - (s.y + ch / 2)) * mk_;
      s.el.style.opacity = v.a * (moving ? 1 - range(t, tF + .6 + i * .08, tF + 1.1 + i * .08) : 1 - .55 * fk);
      s.el.style.transform = `translate(${dx}px, ${dy + (1 - v.i) * 14}px) scale(${1 - .5 * mk_})`;
      s.el.style.borderColor = moving && t > tG + 1.2 ? 'rgba(255,190,6,.6)' : LINE;
    });
    const dv = eo5(range(t, tF + .7, tF + 1.4));
    desk.style.opacity = dv; desk.style.transform = `scale(${.85 + .15 * dv})`;
    show(res, t, tF + 1.4, 1e9, { dy: 10 });
  };
}

// ============================================================ 4b · THREE TIERS
const TIERS = [
  { eb: 'Tier 1 · Now', title: 'The analyst desks', items: [['Underwriting', 'underwriting'], ['Reporting, controlling', 'reporting'], ['Asset management desk', 'asset'], ['Debt advisory', 'debt']], id: 'v19', foot: [['lock-open', 'No licence in the way', 'Pure'], ['database', 'Output: asset vector, NOI', 'Pure']] },
  { eb: 'Tier 2 · Next', title: 'The licensed desk', items: [['Fund admin and TA', 'fund'], ['DD report assembly', 'D-D'], ['Legal process ops', 'legal'], ['Payment operations', 'payments']], id: 'v20', foot: [['shield-check', 'A regulated act in the way', 'regulated'], ['handshake', "Under a named partner's act", 'named']] },
  { eb: 'Tier 3 · Later', title: 'The field, by integration', items: [['Property and facility management', 'property'], ['Origination', 'origination']], id: 'v21', foot: [['database', 'The records, not the headcount', 'records'], ['arrow-right', 'Origination: displaced by the market', 'headcount']] },
];
export function sTiers(root) {
  const t0 = L('v19') - 0.3, t1 = L('v23') - 0.05;
  const h = headline(root, 'Three tiers: desk, licensed desk, field', 160, 118, { cls: 'h3', w: 1400 });
  const crit = mk('div', 'abs', root, { left: '160px', top: '196px', display: 'flex', gap: '12px', alignItems: 'center' });
  const cl = mk('div', 'label', crit, { color: Y, marginRight: '10px' }, 'Scored on');
  const cr = ['FTE density', 'Desk share', 'Licence barrier', 'Data yield', 'Margin'].map(c => { const e = chip(crit, c, 0, 0); e.style.position = 'relative'; e.style.height = '36px'; e.style.fontSize = '13px'; return e; });
  const cols = TIERS.map((T, i) => {
    const el = mk('div', 'panel', root, { left: px(160 + i * 545), top: '278px', width: '510px', height: '660px' });
    mk('div', 'eyebrow', el, { position: 'absolute', left: '36px', top: '38px' }, T.eb);
    mk('div', 'h3', el, { position: 'absolute', left: '36px', top: '74px', fontSize: '36px' }, T.title);
    const its = T.items.map(([name, w], j) => {
      const r = mk('div', 'abs', el, { left: '36px', top: px(160 + j * 62), width: '438px', height: '48px', borderRadius: '10px', background: 'rgba(244,242,236,.06)', display: 'flex', alignItems: 'center', padding: '0 18px', boxSizing: 'border-box', font: '400 21px Inter' }, name);
      return { r, s: W(T.id, w) - .15 };
    });
    const ft = T.foot.map(([ic, tx, w], j) => {
      const r = mk('div', 'abs', el, { left: '36px', top: px(480 + j * 64), display: 'flex', alignItems: 'center', gap: '16px', width: '440px' });
      const ii = icon(ic, 30, r, { flex: 'none' }, 1.5);
      mk('div', null, r, { font: '400 20px/1.25 Inter', color: j === 0 ? INK : DIM }, tx);
      return { r, ii, s: W(T.id, w) - .15 + j * .25 };
    });
    const line_ = mk('div', 'abs', el, { left: '36px', top: '450px', width: '438px', height: '1px', background: LINE });
    return { el, its, ft, s: L(T.id) - .2, line_ };
  });
  return t => {
    const out = ei3(range(t, t1 - .5, t1));
    root.style.opacity = 1 - out; root.style.filter = out > .01 ? `blur(${out * 6}px)` : 'none';
    show(h, t, t0 + .1, 1e9, { dy: 14 }); wordsIn(h, t, t0 + .15, .05);
    show(cl, t, t0 + .3, 1e9, { dy: 0 });
    cr.forEach((c, i) => show(c, t, t0 + .45 + i * .12, 1e9, { dy: 10 }));
    let active = 0; cols.forEach((c, i) => { if (t >= c.s) active = i; });
    cols.forEach((c, i) => {
      const v = show(c.el, t, i === 0 ? t0 + .3 : c.s - .3, 1e9, { dy: 24 });
      c.el.style.opacity = v.a * (i === 0 || t >= c.s - .3 ? 1 : .0) * (i === active ? 1 : (t >= c.s ? .5 : 1));
      if (i > 0 && t < c.s - .3) c.el.style.opacity = env(t, t0 + .5 + i * .15, 1e9).a * .28;
      c.el.style.borderColor = i === active && t >= c.s ? 'rgba(255,190,6,.55)' : LINE;
      c.its.forEach(it => show(it.r, t, it.s, 1e9, { dx: -16, dy: 0 }));
      c.ft.forEach(f => { show(f.r, t, f.s, 1e9, { dy: 10 }); drawIcon(f.ii, t, f.s); });
      fade(c.line_, range(t, c.s, c.s + .6));
    });
  };
}

// ============================================================ 5a · PROPCHAIN SEQUENCE
const STEPS = [
  ['Lenders', 'lender', 'v24', 'Credit boxes rest on the platform', 'Attested NOI carries a debt quote', 'Debt quote'],
  ['Valuers', 'valuer', 'v25', 'Marks on attested inputs', 'LTV tests on marks lenders trust', 'Attested mark'],
  ['Notaries', 'notary', 'v26', 'Financed, marked pairs settle', 'Without re-verification', 'Closing'],
  ['Assurance and peers', 'lender2', 'v27', 'Auditors, depositaries read the same records', 'Managers follow their lenders', 'Audit-ready state'],
  ['Source and finality', 'property', 'v28', 'Property managers feed in data', 'Lawyers: DD as fields · registry last', 'Fresh NOI'],
];
export function sSeq(root) {
  const t0 = L('v23') - 0.3, t1 = L('v29') - 0.05;
  const h = headline(root, 'Each party makes the next one worth adding', 160, 118, { cls: 'h3', w: 1500 });
  const sub = eyebrow(root, 'Propchain · sequenced by what each party unlocks', 160, 190);
  const svg = svgLayer(root);
  const xs = [260, 610, 960, 1310, 1660], ry = 560;
  const rail = sv('path', { d: `M 140 ${ry} L 1780 ${ry}`, stroke: 'rgba(244,242,236,.22)', 'stroke-width': 2, fill: 'none', pathLength: 1 }, svg);
  const segs = xs.slice(1).map((x, i) => sv('path', { d: `M ${xs[i] + 36} ${ry} L ${x - 36} ${ry}`, stroke: Y, 'stroke-width': 3, fill: 'none', pathLength: 1 }, svg));
  const segP = xs.slice(1).map((x, i) => sv('path', { d: `M ${xs[i] + 36} ${ry} L ${x - 36} ${ry}`, fill: 'none' }, svg));
  const pul = sv('circle', { r: 7, fill: Y }, svg); const pulG = sv('circle', { r: 18, fill: 'rgba(255,190,6,.2)' }, svg);
  const st = STEPS.map(([name, clip, id, a, b, out], i) => {
    const x = xs[i];
    const c = sv('circle', { cx: x, cy: ry, r: 34, fill: '#0E0E10', stroke: 'rgba(244,242,236,.35)', 'stroke-width': 1.5 }, svg);
    const n = mk('div', 'abs', root, { left: px(x - 34), top: px(ry - 34), width: '68px', height: '68px', display: 'flex', alignItems: 'center', justifyContent: 'center', font: '500 20px Mono' }, String(i + 1).padStart(2, '0'));
    const f = mk('div', 'clipframe', root, { left: px(x - 150), top: '300px', width: '300px', height: '176px', borderRadius: '12px' });
    const img = mk('img', null, f);
    const card = mk('div', 'abs', root, { left: px(x - 160), top: '630px', width: '320px', textAlign: 'center' });
    const eb = mk('div', 'eyebrow', card, { fontSize: '15px', marginBottom: '14px', whiteSpace: 'normal' }, name);
    mk('div', null, card, { font: '400 21px/1.3 Inter', marginBottom: '10px' }, a);
    mk('div', null, card, { font: '400 18px/1.35 Inter', color: DIM }, b);
    const o = chip(root, out, 0, 850, 'yl'); o.style.left = px(x); o.style.transform = 'translateX(-50%)';
    const oi = mk('div', 'label', root, { position: 'absolute', left: px(x - 100), top: '820px', width: '200px', textAlign: 'center', fontSize: '12px' }, 'Unlocks');
    return { c, n, f, img, card, eb, o, oi, s: L(id) - .15 };
  });
  return t => {
    const out = ei3(range(t, t1 - .5, t1));
    root.style.opacity = 1 - out; root.style.filter = out > .01 ? `blur(${out * 6}px)` : 'none';
    show(h, t, t0 + .1, 1e9, { dy: 14 }); wordsIn(h, t, t0 + .15, .05);
    show(sub, t, t0 + .7, 1e9, { dy: 0 });
    draw(rail, t, t0 + .4, 1.6);
    let pa = 0;
    st.forEach((s, i) => {
      const on = t >= s.s, u = eo5(range(t, s.s, s.s + .6));
      fade(s.c, env(t, t0 + .6 + i * .15).a); fade(s.n, env(t, t0 + .6 + i * .15).a);
      s.c.setAttribute('fill', on ? Y : '#0E0E10'); s.c.setAttribute('stroke', on ? Y : 'rgba(244,242,236,.35)');
      s.c.setAttribute('r', 34 + 6 * Math.sin(Math.PI * u));
      s.n.style.color = on ? '#0B0B0C' : DIM;
      show(s.f, t, s.s + .1, 1e9, { dy: 20 }); setClip(s.img, STEPS[i][1], t, s.s);
      s.f.style.opacity *= (st[i + 1] && t > st[i + 1].s ? .5 : 1);
      show(s.card, t, s.s + .15, 1e9, { dy: 16 });
      if (i > 0) {
        const u2 = draw(segs[i - 1], t, s.s - .9, .8, x => x);
        const pu = range(t, s.s - .9, s.s - .1);
        if (pu > 0 && pu < 1) { const p = along(segP[i - 1], pu); pul.setAttribute('cx', p.x); pul.setAttribute('cy', p.y); pulG.setAttribute('cx', p.x); pulG.setAttribute('cy', p.y); pa = 1; }
      }
      show(s.o, t, s.s + .9, 1e9, { dy: 10 }); s.o.style.transform = 'translateX(-50%)' + s.o.style.transform.replace(/translate\(0px, /, ' translate(0px, ');
      show(s.oi, t, s.s + .9, 1e9, { dy: 0 });
      s.eb.style.color = on ? Y : DIM;
    });
    pul.style.opacity = pulG.style.opacity = pa;
  };
}

// ============================================================ 5b · DEPENDENCY, NOT RANK
export function sDemo(root) {
  const t0 = L('v29') - 0.3, t1 = L('v30') - 0.05;
  const h = headline(root, 'Dependency, not rank.', 160, 118, { cls: 'h2', w: 1500, hi: ['Dependency,'] });
  const P = [0, 1].map(i => {
    const el = mk('div', 'panel', root, { left: px(160 + i * 820), top: '290px', width: '780px', height: '620px' });
    mk('div', 'eyebrow', el, { position: 'absolute', left: '40px', top: '38px', color: i ? Y : INK }, i ? 'After lenders and valuers' : 'A notary tool, alone');
    const n = mk('div', 'abs', el, { left: '60px', top: '200px', width: '150px', height: '150px', borderRadius: '50%', border: '1.5px solid ' + INK });
    icon('stamp', 60, n, { position: 'absolute', left: '44px', top: '42px' });
    mk('div', 'label', el, { position: 'absolute', left: '60px', top: '370px', width: '150px', textAlign: 'center', color: INK }, 'Notary');
    const set = mk('div', 'abs', el, { left: '300px', top: '130px', width: '420px', height: '300px', borderRadius: '14px', border: '1.5px dashed rgba(244,242,236,.4)' });
    mk('div', 'label', set, { position: 'absolute', left: '24px', top: '20px' }, 'Closing set');
    const res = mk('div', 'abs', el, { left: '40px', top: '480px', font: '300 72px Inter', letterSpacing: '-.04em', color: i ? Y : 'rgba(244,242,236,.45)' }, i ? 'A closing' : 'A demo');
    return { el, set, res };
  });
  const empty = mk('div', 'label', P[0].set, { position: 'absolute', left: 0, width: '420px', top: '140px', textAlign: 'center' }, 'Nothing to settle');
  const bid = chip(P[1].set, 'Financed bid', 24, 80, 'outl', 'landmark');
  const mark = chip(P[1].set, 'Mark', 24, 146, 'outl', 'badge-check');
  const chk = mk('div', 'abs', P[1].set, { left: '24px', top: '216px', display: 'flex', alignItems: 'center', gap: '12px' });
  const ci = icon('circle-check', 34, chk, { color: Y }, 1.6); mk('div', 'label', chk, { color: Y }, 'Executes');
  return t => {
    const out = ei3(range(t, t1 - .5, t1));
    root.style.opacity = 1 - out;
    show(h, t, t0 + .1, 1e9, { dy: 14 }); wordsIn(h, t, t0 + .15, .08);
    show(P[0].el, t, W('v29', 'notary') - .3, 1e9, { dy: 20 });
    show(empty, t, W('v29', 'nothing') - .1, 1e9, { dy: 6 });
    show(P[0].res, t, W('v29', 'demo') - .1, 1e9, { dy: 16 });
    show(P[1].el, t, W('v29', 'With') - .3, 1e9, { dy: 20 });
    show(bid, t, W('v29', 'financed') - .1, 1e9, { dx: -40, dy: 0 });
    show(mark, t, W('v29', 'mark') - .1, 1e9, { dx: -40, dy: 0 });
    const cs = W('v29', 'closing') - .3;
    show(chk, t, cs, 1e9, { dy: 8 }); drawIcon(ci, t, cs);
    P[1].set.style.borderColor = t > cs ? Y : 'rgba(244,242,236,.4)'; P[1].set.style.borderStyle = t > cs ? 'solid' : 'dashed';
    show(P[1].res, t, cs, 1e9, { dy: 16 });
  };
}

// ============================================================ 6a · TOOLS FOR ACTS THAT STAY THEIRS
export function sTools(root) {
  const t0 = L('v30') - 0.3, t1 = L('v31') - 0.05;
  const h = headline(root, 'Tools for acts that stay theirs', 160, 118, { cls: 'h3', w: 1500 });
  const svg = svgLayer(root);
  const tool = mk('div', 'panel', root, { left: '160px', top: '260px', width: '720px', height: '460px' });
  mk('div', 'eyebrow', tool, { position: 'absolute', left: '40px', top: '40px' }, 'Our tool');
  const free = chip(tool, 'Free or near-free', 420, 28, 'yl');
  const steps = ['Prepares', 'Presents', 'Records'].map((s, i) => {
    const r = mk('div', 'abs', tool, { left: '40px', top: px(130 + i * 96), display: 'flex', alignItems: 'center', gap: '22px' });
    const ii = icon('circle-check', 40, r, { color: Y }, 1.5);
    mk('div', null, r, { font: '300 46px Inter', letterSpacing: '-.03em' }, s);
    return { r, ii, s: W('v30', s.toLowerCase()) - .15 };
  });
  const ex = mk('div', 'abs', root, { left: '160px', top: '760px', lineHeight: '2.1' }, ['Notary · machine-readable closing set', 'Valuer · attested input feed, signature stays theirs', 'Auditor · continuous evidence pack'].map(s => `<div class="label" style="color:${INK}">${s}</div>`).join(''));
  const act = mk('div', 'abs', root, { left: '1250px', top: '310px', width: '340px', height: '340px', borderRadius: '50%', border: '1.5px solid ' + INK });
  const ai = icon('stamp', 100, act, { position: 'absolute', left: '120px', top: '96px' });
  mk('div', 'label', act, { position: 'absolute', top: '220px', width: '340px', textAlign: 'center', color: INK }, 'The act · theirs');
  const arrow = sv('path', { d: 'M 900 480 L 1230 480', stroke: 'rgba(244,242,236,.5)', 'stroke-width': 2, 'stroke-dasharray': '8 8', fill: 'none' }, svg);
  const x1 = sv('path', { d: 'M 1045 455 L 1095 505 M 1095 455 L 1045 505', stroke: Y, 'stroke-width': 3, fill: 'none', pathLength: 1 }, svg);
  const never = mk('div', 'label', root, { position: 'absolute', left: '900px', top: '530px', width: '340px', textAlign: 'center', color: Y }, 'Never produces the act');
  return t => {
    const out = ei3(range(t, t1 - .5, t1));
    root.style.opacity = 1 - out; root.style.filter = out > .01 ? `blur(${out * 6}px)` : 'none';
    show(h, t, t0 + .1, 1e9, { dy: 14 }); wordsIn(h, t, t0 + .15, .05);
    show(tool, t, t0 + .3, 1e9, { dy: 20 });
    show(free, t, W('v30', 'free') - .1, 1e9, { dy: 8 });
    show(act, t, t0 + .5, 1e9, { dy: 0, sc: .08 }); drawIcon(ai, t, t0 + .6);
    show(ex, t, t0 + 1.0, 1e9, { dy: 12 });
    const ns = W('v30', 'never') - .2;
    fade(arrow, range(t, ns, ns + .4)); draw(x1, t, ns + .3, .5); show(never, t, ns + .4, 1e9, { dy: 8 });
    steps.forEach(s => { show(s.r, t, s.s, 1e9, { dx: -16, dy: 0 }); drawIcon(s.ii, t, s.s); });
  };
}

// ============================================================ 6b · THE FLYWHEEL
const LOOP = [
  ['1 · Prop.com services', 'Underwriting, reporting, asset management', 'Services'],
  ['2 · Attested records', 'Vectors, NOI, marks, cash events, with lineage', 'records'],
  ['3 · Rails worth joining', 'Lenders, valuers, notaries, auditors connect', 'rails'],
  ['4 · Demand for services', 'Their process half, delivered: more desks', 'need'],
];
export function sLoop(root) {
  const t0 = L('v31') - 0.3, t1 = L('v32') - 0.05;
  const h = headline(root, 'Services make records; records make rails', 160, 118, { cls: 'h3', w: 1500 });
  const svg = svgLayer(root);
  const cx = [560, 1360, 1360, 560], cy = [410, 410, 790, 790];
  const d = 'M 560 410 L 1360 410 Q 1500 410 1500 550 L 1500 650 Q 1500 790 1360 790 L 560 790 Q 420 790 420 650 L 420 550 Q 420 410 560 410 Z';
  const path = sv('path', { d, stroke: 'rgba(244,242,236,.22)', 'stroke-width': 2, fill: 'none', pathLength: 1 }, svg);
  const pp = sv('path', { d, fill: 'none' }, svg);
  const lit = sv('path', { d, stroke: Y, 'stroke-width': 2.5, fill: 'none', pathLength: 1 }, svg);
  const pulses = [0, 1, 2].map(() => sv('circle', { r: 6, fill: Y }, svg));
  const nodes = LOOP.map(([a, b, w], i) => {
    const el = mk('div', 'panel', root, { left: px(cx[i] - 230), top: px(cy[i] - 70), width: '460px', height: '140px', background: '#111113' });
    mk('div', 'eyebrow', el, { position: 'absolute', left: '30px', top: '30px', color: INK }, a);
    mk('div', null, el, { position: 'absolute', left: '30px', top: '66px', width: '400px', font: '400 21px/1.3 Inter', color: DIM }, b);
    let s; try { s = W('v31', w) - .15; } catch (e) { s = L('v31') + i; }
    return { el, s };
  });
  nodes[1].s = W('v31', 'records', 0) - .1; // "Services make records"
  nodes[2].s = W('v31', 'rails', 0) - .1;
  const mid = mk('div', 'label', root, { position: 'absolute', left: '560px', top: '585px', width: '800px', textAlign: 'center', lineHeight: '1.9' }, 'Models improve on anonymised platform data<br>Client data is never sold or shared');
  return t => {
    const out = ei3(range(t, t1 - .5, t1));
    root.style.opacity = 1 - out; root.style.filter = out > .01 ? `blur(${out * 6}px)` : 'none';
    show(h, t, t0 + .1, 1e9, { dy: 14 }); wordsIn(h, t, t0 + .15, .05);
    draw(path, t, t0 + .3, 1.5);
    const ls = nodes[0].s, le = nodes[3].s + .8;
    drawU(lit, clamp((t - ls) / (le - ls)) * 1);
    let active = -1; nodes.forEach((n, i) => { if (t >= n.s) active = i; });
    nodes.forEach((n, i) => {
      show(n.el, t, t0 + .4 + i * .12, 1e9, { dy: 16 });
      n.el.style.borderColor = i === active ? Y : LINE;
      n.el.querySelector('.eyebrow').style.color = t >= n.s ? Y : INK;
    });
    pulses.forEach((p, k) => {
      const u = ((t - ls) / 3.2 + k / 3) % 1; const on = t > le;
      const pt = along(pp, u < 0 ? u + 1 : u); p.setAttribute('cx', pt.x); p.setAttribute('cy', pt.y); p.style.opacity = on ? range(t, le, le + .5) : 0;
    });
    show(mid, t, t0 + 1.2, 1e9, { dy: 8 });
  };
}

// ============================================================ 6c · NEUTRALITY
export function sNeutral(root) {
  const t0 = L('v32') - 0.3, t1 = L('v33') - 0.1;
  const h = headline(root, 'Prove the exchange never reads the book', 160, 118, { cls: 'h3', w: 1500 });
  const svg = svgLayer(root);
  const rail = sv('path', { d: 'M 160 520 L 1760 520', stroke: 'rgba(244,242,236,.3)', 'stroke-width': 2, fill: 'none', pathLength: 1 }, svg);
  const names = ['Manager', 'Lender', 'Prop.com', 'Manager', 'Valuer', 'Manager'];
  const nodes = names.map((n, i) => {
    const x = 300 + i * 264;
    const g = mk('div', 'abs', root, { left: px(x - 60), top: '300px', width: '120px', textAlign: 'center' });
    const c = mk('div', null, g, { width: '96px', height: '96px', borderRadius: '50%', border: '1.5px solid ' + INK, margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#0E0E10' });
    icon(n === 'Lender' ? 'landmark' : n === 'Valuer' ? 'badge-check' : 'briefcase', 36, c);
    mk('div', 'label', g, { marginTop: '14px', color: INK }, n);
    const drop = sv('path', { d: `M ${x} 420 L ${x} 516`, stroke: 'rgba(244,242,236,.4)', 'stroke-width': 1.2, fill: 'none', pathLength: 1 }, svg);
    return { g, c, drop, pc: n === 'Prop.com' };
  });
  const tags = [['Same KYA identity', 'same', 0], ['Same permissions', 'same', 1], ['No privileged read', 'privileged', 0]].map(([tx, w, n], i) => {
    const c = chip(root, tx, 0, 580, 'outl'); c.style.left = px(560 + i * 0); return { c, s: W('v32', w, n) - .15 };
  });
  const tagRow = mk('div', 'abs', root, { left: '0', top: '580px', width: '1920px', display: 'flex', justifyContent: 'center', gap: '18px' });
  tags.forEach(tg => { tg.c.style.position = 'relative'; tg.c.style.left = tg.c.style.top = '0'; tagRow.appendChild(tg.c); });
  const log = mk('div', 'panel', root, { left: '560px', top: '690px', width: '800px', height: '230px', background: '#0F0F11' });
  mk('div', 'eyebrow', log, { position: 'absolute', left: '32px', top: '28px' }, 'Proof of Permission · read log');
  const rows = ['read · mandate · prop.com', 'read · credit box · manager', 'read · asset · lender'].map((r, i) => {
    const e = mk('div', 'abs', log, { left: '32px', top: px(80 + i * 44), width: '736px', display: 'flex', justifyContent: 'space-between', font: '500 17px Mono', color: INK, letterSpacing: '.06em' });
    mk('span', null, e, null, r); mk('span', null, e, { color: Y }, 'logged ✓');
    return e;
  });
  return t => {
    const out = ei3(range(t, t1 - .5, t1));
    root.style.opacity = 1 - out; root.style.filter = out > .01 ? `blur(${out * 6}px)` : 'none';
    show(h, t, t0 + .1, 1e9, { dy: 14 }); wordsIn(h, t, t0 + .15, .05);
    draw(rail, t, t0 + .3, 1.2);
    const tp = W('v32', 'participant') - .1;
    nodes.forEach((n, i) => {
      show(n.g, t, n.pc ? t0 + .3 : tp + .1 + i * .08, 1e9, { dy: 16 });
      draw(n.drop, t, n.pc ? t0 + .6 : tp + .3 + i * .08, .4);
      if (n.pc) { const k = range(t, tp + .8, tp + 1.4); n.c.style.borderColor = k < 1 ? Y : INK; n.c.style.boxShadow = `0 0 0 ${6 * (1 - k)}px rgba(255,190,6,${.25 * (1 - k)})`; }
    });
    tags.forEach(tg => show(tg.c, t, tg.s, 1e9, { dy: 10 }));
    const ls = W('v32', 'Every') - .2;
    show(log, t, ls, 1e9, { dy: 16 });
    rows.forEach((r, i) => show(r, t, ls + .3 + i * .3, 1e9, { dx: -12, dy: 0 }));
  };
}

// ============================================================ 7 · FINALE + END CARD
export function sFinale(root) {
  const t0 = L('v33') - 0.3, t1 = TL.total;
  const tEnd = E('v33') + .5;
  const lines = [['Own', 'the desk.', 'Own'], ['Tool', 'the act.', 'Tool'], ['Onboard', 'the market.', 'Onboard']].map(([a, b, w], i) => {
    const el = mk('div', 'h1', root, { position: 'absolute', left: '160px', top: px(290 + i * 150), fontSize: '118px' }, `<span class="y">${a}</span> ${b}`);
    return { el, s: W('v33', w) - .12 };
  });
  const sub = mk('div', 'label', root, { position: 'absolute', left: '166px', top: '790px', color: INK }, 'Now · Next · Later — the plan on one page');
  const end = mk('div', 'abs', root, { inset: 0, background: '#0B0B0C' });
  const logo = mk('img', 'abs', end, { left: '760px', top: '490px', width: '400px' }); logo.src = 'assets/logo-white.svg';
  const tag = mk('div', 'label', end, { position: 'absolute', top: '600px', width: '1920px', textAlign: 'center', color: DIM }, 'Structuring real estate for the autonomous era');
  const fin = mk('div', 'abs', root, { inset: 0, background: '#0B0B0C' });
  return t => {
    lines.forEach(l => show(l.el, t, l.s, tEnd, { dy: 40, blur: 12 }));
    show(sub, t, W('v33', 'Onboard') + .4, tEnd, { dy: 0 });
    fade(end, range(t, tEnd - .2, tEnd + .5));
    show(logo, t, tEnd + .3, 1e9, { dy: 10, blur: 6, din: 1.2 });
    show(tag, t, tEnd + .9, 1e9, { dy: 8 });
    fade(fin, range(t, t1 - .9, t1 - .05));
  };
}
