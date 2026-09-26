// 03 THE MANDATE — M-0417 scores assets: filters, utilities, confidence, weights+floors, tie-break.
import { T, h, s, svg, box, I, scene, rise, fade, draw, pulseDot, pr, eo, e3, eio, lerp, clamp, setText, Y } from './core.js';

const uCap = x => x < 5.25 ? 0 : clamp((x - 5.25) / 1.75);
const GRID = 'rgba(244,242,236,.12)', AX = 'rgba(244,242,236,.35)';

/** a chart panel in its own SVG (designed at w x h); returns mappers */
function chart(parent, x, y, w, hh, o) {
  const wrap = box(parent, x, y, '', '', { width: w + 'px', height: hh + 'px', transformOrigin: '0 0' });
  const g = svg(wrap, w, hh);
  const pad = { l: 90, r: 30, t: 30, b: 80, ...(o.pad || {}) };
  const X = v => pad.l + (v - o.x0) / (o.x1 - o.x0) * (w - pad.l - pad.r);
  const Yv = v => hh - pad.b - v * (hh - pad.t - pad.b);
  const axes = s('g', {}, g);
  [0, .5, 1].forEach(v => {
    s('line', { x1: pad.l, x2: w - pad.r, y1: Yv(v), y2: Yv(v), stroke: v === 0 ? AX : GRID, 'stroke-width': 1 }, axes);
    const tx = s('text', { x: pad.l - 18, y: Yv(v) + 7, 'text-anchor': 'end', fill: 'rgba(244,242,236,.5)', 'font-family': 'JBM', 'font-size': o.fs || 20 }, axes); tx.textContent = v.toFixed(1);
  });
  (o.ticks || []).forEach(([v, lab]) => {
    s('line', { x1: X(v), x2: X(v), y1: Yv(0), y2: Yv(0) + 10, stroke: AX }, axes);
    const tx = s('text', { x: X(v), y: Yv(0) + 40, 'text-anchor': 'middle', fill: 'rgba(244,242,236,.55)', 'font-family': 'JBM', 'font-size': o.fs || 20 }, axes); tx.textContent = lab;
  });
  const cap = box(wrap, pad.l, -44, 'eyebrow', o.title || '', { fontSize: (o.fs || 20) * .85 + 'px' });
  return { wrap, g, X, Y: Yv, axes, cap, w, h: hh, pad };
}
const path = (g, d, o = {}) => s('path', { d, fill: 'none', stroke: o.c || Y, 'stroke-width': o.w || 4, 'stroke-linecap': 'round', 'stroke-linejoin': 'round', pathLength: 1, ...(o.dash ? { 'stroke-dasharray': o.dash } : {}) }, g);

export default function ch3() {
  const W = T.W.bind(T), L = T.L.bind(T), E = T.E.bind(T);
  const tS = W('07', 'hard') - .2, tEnd = E('12') + .9;

  // ================================================================ sidebar: M-0417, five parts
  const side = scene(tS, tEnd, updSide);
  const sb = box(side.el, 140, 280, 'card solid', '', { width: '440px', height: '680px' });
  box(sb, 34, 32, 'eyebrow y', 'Mandate M-0417');
  box(sb, 34, 66, 'tag', 'illustrative · logistics · Germany');
  const parts = [['01', 'Hard filters', 'class · geography · lot · cap'], ['02', 'Utility curves', 'one per soft dimension, 0 to 1'], ['03', 'Weights and floors', 'cap 45 · WALT 25 · credit 20 · vac 10'], ['04', 'Tie-break order', 'longer WALT, then lower capex'], ['05', 'Return target', '12% levered IRR · 5-year hold']];
  const P = parts.map(([n, a, b], i) => {
    const r = box(sb, 34, 130 + i * 106, '', `<div style="display:flex;gap:18px"><span class="mono" style="font-size:16px;padding-top:6px">${n}</span><div><div style="font-size:26px">${a}</div><div class="mono" style="font-size:14px;margin-top:8px;color:rgba(244,242,236,.55)">${b}</div></div></div>`, { width: '380px' });
    box(sb, 34, 130 + i * 106 - 20, 'rule', '', { width: '372px' });
    return r;
  });
  const partAt = t => t < L('08') - .5 ? 0 : t < L('11') - .5 ? 1 : t < L('12') - .5 ? 2 : 3;
  function updSide(t) {
    rise(sb, t, tS + .1, { dx: -30, dy: 0 });
    const cur = partAt(t);
    P.forEach((p, i) => {
      rise(p, t, tS + .4 + i * .1, { dy: 10 });
      const on = i === cur;
      p.style.color = on ? '#FFBE06' : '#F4F2EC';
      p.style.opacity = Math.min(parseFloat(p.style.opacity), on ? 1 : .42);
    });
  }

  const RX = 660; // right-hand area origin

  // ================================================================ A: hard filters as a table
  {
    const t0 = tS, t1 = E('07') + .7;
    const sc = scene(t0, t1, upd); const root = sc.el;
    const head = box(root, 140, 150, 'head', 'Hard filters: <b>fail one and you are out</b>.');
    const cols = [['Asset', 0], ['Class', 300], ['Country', 470], ['Lot', 600], ['Cap rate', 760], ['', 930]];
    const flt = [['logistics', 'logistics'], ['Germany', 'germany'], ['€10–25M', 'ten'], ['≥ 5.25%', 'cap']];
    const hdr = cols.map(([n, x], i) => box(root, RX + x, 290, 'tag', n));
    const fl = flt.map(([f, cue], i) => box(root, RX + cols[i + 1][1], 322, 'chip', f, { fontSize: '14px', padding: '6px 12px' }));
    const assets = [
      ['Logistics · Hamburg', 'Logistics', 'DE', '€18M', '6.40%', -1],
      ['Office · Frankfurt', 'Office', 'DE', '€20M', '5.60%', 0],
      ['Logistics · Rotterdam', 'Logistics', 'NL', '€15M', '6.00%', 1],
      ['Logistics · Leipzig', 'Logistics', 'DE', '€42M', '5.90%', 2],
      ['Logistics · Munich', 'Logistics', 'DE', '€13.0M', '6.15%', -1],
      ['Logistics · Dortmund', 'Logistics', 'DE', '€12M', '4.90%', 3],
      ['Logistics · Bremen', 'Logistics', 'DE', '€21M', '5.80%', -1],
    ];
    const why = ['class = office', 'country = NL', 'lot = €42M', 'cap rate = 4.90%'];
    const rows = assets.map((a, i) => {
      const r = box(root, RX, 390 + i * 76, '', '', { width: '1140px', height: '64px' });
      box(r, 0, -8, 'rule', '', { width: '1140px' });
      box(r, 0, 14, '', `<span style="display:inline-flex;gap:12px;align-items:center">${I('warehouse', 22, 'rgba(244,242,236,.7)')}${a[0]}</span>`, { fontSize: '22px' });
      const cells = [1, 2, 3, 4].map(k => box(r, cols[k][1] + 34, 16, 'mono', a[k], { fontSize: '18px', color: 'rgba(244,242,236,.8)' }));
      const marks = [0, 1, 2, 3].map(k => box(r, cols[k + 1][1], 12, '', I(k === a[5] ? 'x' : 'check', 24, k === a[5] ? '#F4F2EC' : Y)));
      const st = box(r, cols[5][1], 14, 'mono', a[5] >= 0 ? `✕ ${why[a[5]]}` : 'in the book', { fontSize: '15px', color: a[5] >= 0 ? 'rgba(244,242,236,.6)' : '#FFBE06' });
      return { r, cells, marks, st, fail: a[5] };
    });
    const log = box(root, RX, 950, 'tag', 'Every rejection is logged with the failing field, so it is auditable');
    function upd(t) {
      rise(head, t, t0 + .2);
      hdr.forEach((hh, i) => fade(hh, t, t0 + .3, .5));
      const ft = flt.map(f => W('07', f[1]));
      fl.forEach((f, i) => { rise(f, t, ft[i] - .2, { dy: 8 }); f.classList.toggle('yo', t > ft[i]); });
      const outT = W('07', 'out') - .2;
      let surv = 0;
      rows.forEach((r, i) => {
        rise(r.r, t, t0 + .5 + i * .08, { dx: 30, dy: 0 });
        // a row stops being checked after its first failure
        r.marks.forEach((m, k) => {
          const shown = r.fail < 0 || k <= r.fail;
          const a = shown ? pr(t, ft[k] + .25 + i * .07, .4) : 0; m.style.opacity = a;
        });
        const failT = r.fail >= 0 ? ft[r.fail] + .35 + i * .07 : 1e9;
        const f = pr(t, failT, .4);
        const col = r.fail >= 0 ? 1 - .6 * f : 1;
        r.cells.forEach(c => c.style.opacity = col);
        r.st.style.opacity = r.fail >= 0 ? f : pr(t, W('07', 'fail') + .2, .5);
        // collapse: rejected rows vanish, survivors close up
        const c = pr(t, outT + .3, 1.0, eio);
        const yNow = lerp(390 + i * 76, 390 + surv * 76, r.fail < 0 ? c : 0);
        r.r.style.top = yNow + 'px';
        if (r.fail >= 0) { r.r.style.opacity = Math.min(parseFloat(r.r.style.opacity), 1 - c); r.r.style.left = RX - 60 * c + 'px'; }
        else surv++;
      });
      rise(log, t, W('07', 'fail'), { dy: 10 });
    }
  }

  // ================================================================ B+C: utility curves
  {
    const t0 = L('08') - .5, tC = L('09') - .3, t1 = E('09') + .7;
    const sc = scene(t0, t1, upd); const root = sc.el;
    const head = box(root, 140, 150, 'head', 'Every dimension maps to a <b>utility from 0 to 1</b>.');
    const cCap = chart(root, RX + 20, 330, 1080, 600, { x0: 4.5, x1: 8.0, ticks: [[4.5, '4.5%'], [5.25, '5.25%'], [6.15, '6.15%'], [7.0, '7.0%'], [8.0, '8.0%']], title: 'Cap rate · monotone, capped', fs: 22 });
    const g = cCap.g, X = cCap.X, Yv = cCap.Y;
    const floorL = s('line', { x1: X(5.25), x2: X(5.25), y1: Yv(0), y2: Yv(1.05), stroke: 'rgba(244,242,236,.35)', 'stroke-dasharray': '5 7', 'stroke-width': 1.5 }, g);
    const flTx = s('text', { x: X(5.25) - 14, y: Yv(.12), 'text-anchor': 'end', fill: 'rgba(244,242,236,.6)', 'font-family': 'JBM', 'font-size': 18 }, g); flTx.textContent = 'below: 0, asset drops';
    const curve = path(g, `M${X(4.5)},${Yv(0)} L${X(5.25)},${Yv(0)} L${X(7.0)},${Yv(1)} L${X(8.0)},${Yv(1)}`, { w: 5 });
    const capZone = s('rect', { x: X(7.0), y: Yv(1) - 60, width: X(8.0) - X(7.0), height: 60, fill: 'rgba(255,190,6,.08)' }, g);
    const capTx = s('text', { x: X(7.5), y: Yv(1) - 24, 'text-anchor': 'middle', fill: Y, 'font-family': 'JBM', 'font-size': 18 }, g); capTx.textContent = 'buyer stops paying for more';
    const guideV = s('line', { stroke: 'rgba(255,190,6,.5)', 'stroke-width': 1.5, 'stroke-dasharray': '4 5' }, g);
    const guideH = s('line', { stroke: 'rgba(255,190,6,.5)', 'stroke-width': 1.5, 'stroke-dasharray': '4 5' }, g);
    const dot = s('circle', { r: 11, fill: Y }, g); const halo = s('circle', { r: 26, fill: Y, opacity: .18 }, g);
    const read = box(cCap.wrap, 0, 0, 'chip yo', '', { fontSize: '18px' });

    const cLot = chart(root, RX + 560, 330, 1080, 600, { x0: 0, x1: 40, ticks: [[5, '€5M'], [10, '€10M'], [25, '€25M'], [35, '€35M']], title: 'Lot size · target-shaped (a plateau)', fs: 34, pad: { l: 110, b: 100 } });
    const lotC = path(cLot.g, `M${cLot.X(2)},${cLot.Y(0)} L${cLot.X(7)},${cLot.Y(0)} L${cLot.X(10)},${cLot.Y(1)} L${cLot.X(25)},${cLot.Y(1)} L${cLot.X(30)},${cLot.Y(0)} L${cLot.X(38)},${cLot.Y(0)}`, { w: 7 });
    const lotM = [12, 18].map(v => { const gg = s('g', {}, cLot.g); s('circle', { cx: cLot.X(v), cy: cLot.Y(1), r: 14, fill: Y }, gg); const tx = s('text', { x: cLot.X(v), y: cLot.Y(1) + 56, 'text-anchor': 'middle', fill: '#F4F2EC', 'font-family': 'JBM', 'font-size': 32 }, gg); tx.textContent = `€${v}M`; return gg; });
    const lotTx = box(cLot.wrap, 110, 610, 'mono', '€12M and €18M are equally fine', { fontSize: '34px', color: Y });

    const cCr = chart(root, RX + 20, 650, 1080, 600, { x0: 0, x1: 4, ticks: [[.75, 'B'], [1.75, 'BB'], [2.75, 'IG']], title: 'Tenant credit · stepped', fs: 34, pad: { l: 110, b: 100 } });
    const steps = [[.75, .2], [1.75, .6], [2.75, 1]].map(([x, v]) => {
      const gg = s('g', {}, cCr.g);
      const r = s('rect', { x: cCr.X(x) - 90, y: cCr.Y(v), width: 180, height: cCr.Y(0) - cCr.Y(v), fill: v === 1 ? Y : 'rgba(244,242,236,.5)', rx: 4 }, gg);
      const tx = s('text', { x: cCr.X(x), y: cCr.Y(v) - 18, 'text-anchor': 'middle', fill: '#F4F2EC', 'font-family': 'JBM', 'font-size': 34 }, gg); tx.textContent = v.toFixed(1);
      return gg;
    });
    const note = box(root, RX + 590, 700, '', `<div class="eyebrow y">Why utilities, not distance</div><div class="sub" style="margin-top:16px;font-size:24px;width:500px">Euros and percentage points don't compare. Utilities are normalised, directional and explainable.</div>`);

    function upd(t) {
      rise(head, t, t0 + .2, { out: tC + .2 });
      rise(cCap.cap, t, t0 + .4);
      fade(cCap.axes, t, t0 + .3, .6);
      draw(curve, t, W('08', 'utility') - .1, 1.6);
      fade(floorL, t, W('08', 'five') - .1, .5); fade(flTx, t, W('08', 'five'), .5);
      fade(capZone, t, W('08', 'caps') - .2, .5); fade(capTx, t, W('08', 'caps'), .5);
      // marker: sweeps 5.25 -> 6.15 (hold) -> 7.7
      const a = pr(t, W('08', 'climbs') - .1, 1.4, eio), b = pr(t, W('08', 'seven') - .1, 1.6, eio);
      const v = b > 0 ? lerp(6.15, 7.7, b) : lerp(4.8, 6.15, a);
      const u = uCap(v); const on = pr(t, W('08', 'climbs') - .2, .4);
      [dot, halo].forEach(c => { c.setAttribute('cx', X(v)); c.setAttribute('cy', Yv(u)); c.style.opacity = on * (c === halo ? .18 : 1); });
      guideV.setAttribute('x1', X(v)); guideV.setAttribute('x2', X(v)); guideV.setAttribute('y1', Yv(0)); guideV.setAttribute('y2', Yv(u));
      guideH.setAttribute('x1', cCap.pad.l); guideH.setAttribute('x2', X(v)); guideH.setAttribute('y1', Yv(u)); guideH.setAttribute('y2', Yv(u));
      guideV.style.opacity = guideH.style.opacity = on;
      setText(read, `cap ${v.toFixed(2)}% → u ${u.toFixed(2)}`);
      read.style.left = Math.min(X(v) + 24, 760) + 'px'; read.style.top = Yv(u) + 24 + 'px'; read.style.opacity = on;
      // C: shrink the cap chart, bring in the siblings
      const c = pr(t, tC, 1.1, eio);
      cCap.wrap.style.scale = lerp(1, .5, c);
      cCap.wrap.style.top = lerp(330, 300, c) + 'px';
      [cLot, cCr].forEach((ch, i) => { ch.wrap.style.scale = .5; rise(ch.wrap, t, [W('09', 'lot') - .1, W('09', 'tenant') - .1][i], { dy: 30 }); });
      draw(lotC, t, W('09', 'lot') + .3, 1.1);
      lotM.forEach((m, i) => fade(m, t, W('09', 'plateau') + .2 + i * .25, .4));
      fade(lotTx, t, W('09', 'plateau') + .7, .5);
      steps.forEach((st, i) => { const p = pr(t, [W('09', 'single-b'), W('09', 'double-b'), W('09', 'investment')][i] - .1, .7); st.style.opacity = p; st.style.transform = `translateY(${(1 - p) * 30}px)`; });
      rise(note, t, W('09', 'single-b') + 1.0, { dy: 12 });
    }
  }

  // ================================================================ D: confidence decay
  {
    const t0 = L('10') - .4, t1 = E('10') + .7;
    const sc = scene(t0, t1, upd); const root = sc.el;
    const head = box(root, 140, 150, 'head', 'Confidence multiplies in: <b>fresh data outranks stale</b>.');
    const ch = chart(root, RX + 20, 320, 1100, 330, { x0: 0, x1: 6, ticks: [[0, 'attested'], [1, '1 mo'], [3, '3 mo'], [5, '5 mo'], [6, '6 mo']], title: 'c(t) · confidence by attestation age · illustrative', fs: 18, pad: { b: 60, t: 20 } });
    const cf = m => .55 + .45 * Math.exp(-m / 2.2);      // illustrative decay toward a floor
    let d = ''; for (let m = 0; m <= 6.001; m += .1) d += (m ? 'L' : 'M') + ch.X(m) + ',' + ch.Y(cf(m)) + ' ';
    const cur = path(ch.g, d, { w: 4 });
    const mk = [[.25, 'last week'], [5, '5 months']].map(([m, lab]) => {
      const gg = s('g', {}, ch.g);
      s('line', { x1: ch.X(m), x2: ch.X(m), y1: ch.Y(0), y2: ch.Y(cf(m)), stroke: 'rgba(244,242,236,.4)', 'stroke-dasharray': '4 5' }, gg);
      s('circle', { cx: ch.X(m), cy: ch.Y(cf(m)), r: 9, fill: Y }, gg);
      const tx = s('text', { x: ch.X(m) + 16, y: ch.Y(cf(m)) - 16, fill: '#F4F2EC', 'font-family': 'JBM', 'font-size': 18 }, gg); tx.textContent = `${lab} · c ${cf(m).toFixed(2)}`;
      return gg;
    });
    const A = [['6.2% cap rate', 'attested last week', uCap(6.2), cf(.25)], ['6.4% cap rate', 'attested 5 months ago', uCap(6.4), cf(5)]];
    const rows = A.map(([n, age, u, c], i) => {
      const r = box(root, RX + 20, 0, '', '', { width: '1100px', height: '110px' });
      box(r, 0, 0, 'rule', '', { width: '1100px' });
      const rk = box(r, 0, 30, 'mono', '', { fontSize: '30px', color: Y });
      box(r, 70, 24, '', `<div style="font-size:28px">${n}</div><div class="mono" style="font-size:15px;margin-top:6px;color:rgba(244,242,236,.55)">${I('clock', 16)} ${age}</div>`);
      const tr = box(r, 480, 44, '', '', { width: '480px', height: '14px', borderRadius: '7px', background: 'rgba(244,242,236,.08)' });
      const fu = box(tr, 0, 0, '', '', { height: '14px', borderRadius: '7px', background: 'rgba(244,242,236,.35)', width: u * 480 + 'px', transformOrigin: '0 50%' });
      const fc = box(tr, 0, 0, '', '', { height: '14px', borderRadius: '7px', background: Y, width: u * c * 480 + 'px', transformOrigin: '0 50%' });
      const num = box(r, 990, 30, 'mono', '', { fontSize: '26px' });
      return { r, rk, fu, fc, num, u, c };
    });
    const leg = box(root, RX + 500, 690, 'tag', 'bar = utility × confidence');
    function upd(t) {
      rise(head, t, t0 + .2);
      fade(ch.axes, t, t0 + .3, .5); rise(ch.cap, t, t0 + .3);
      draw(cur, t, W('10', 'decays') - .2, 1.4);
      fade(mk[0], t, W('10', 'last'), .5); fade(mk[1], t, W('10', 'five') - .1, .5);
      rise(leg, t, W('10', 'so'));
      const sw = pr(t, W('10', 'outranks') + .1, 1.1, eio);      // swap order
      rows.forEach((r, i) => {
        rise(r.r, t, W('10', i ? 'outranks' : 'six') - .2, { dy: 16 });
        // before: 6.4% ranks above (raw); after: 6.2% above (scaled)
        const yBefore = i === 1 ? 0 : 1, yAfter = i === 0 ? 0 : 1;
        r.r.style.top = 730 + lerp(yBefore, yAfter, sw) * 120 + 'px';
        const k = pr(t, W('10', 'outranks') - .1, .9);
        r.fc.style.transform = `scaleX(${k})`;
        r.fu.style.transform = `scaleX(${pr(t, W('10', i ? 'outranks' : 'six'), .8)})`;
        setText(r.num, k < .5 ? `u ${r.u.toFixed(2)}` : `${(r.u * r.c).toFixed(2)}`);
        r.num.style.color = k < .5 ? 'rgba(244,242,236,.6)' : '#F4F2EC';
        setText(r.rk, sw > .5 ? `#${i + 1}` : `#${2 - i}`); r.rk.style.opacity = pr(t, W('10', 'outranks'), .5);
      });
    }
  }

  // ================================================================ E: weights and floors
  {
    const t0 = L('11') - .4, t1 = E('11') + .7;
    const sc = scene(t0, t1, upd); const root = sc.el;
    const head = box(root, 140, 150, 'head', 'Weights combine. <b>Floors come first.</b>');
    const form = box(root, RX + 20, 290, 'mono', 'S(a, m) = Σ w<sub>i</sub> · c<sub>i</sub>(t) · u<sub>i</sub>(a<sub>i</sub>)&nbsp;&nbsp;<span style="color:rgba(244,242,236,.5)">if every u<sub>i</sub> ≥ floor<sub>i</sub>, else 0</span>', { fontSize: '26px' });
    const WT = [['Cap rate', 45, 'cap'], ['WALT', 25, 'lease'], ['Credit', 20, 'credit'], ['Vac.', 10, 'vacancy']];
    const BW = 1000, BX = RX + 20;
    let acc = 0;
    const segs = WT.map(([n, w, cue]) => {
      const x = BX + acc / 100 * BW; acc += w;
      const sg = box(root, x, 380, '', `<div class="mono" style="font-size:17px;color:rgba(244,242,236,.8)">${n} <span class="y">${w}</span></div>`, { width: w / 100 * BW - 6 + 'px' });
      const bar = box(sg, 0, 36, '', '', { width: '100%', height: '10px', borderRadius: '5px', background: 'rgba(244,242,236,.25)' });
      return { sg, cue, w };
    });
    const mkRow = (y, name, sub, us) => {
      const r = box(root, BX, y, '', '', { width: '1120px', height: '140px' });
      box(r, 0, 0, '', `<div style="font-size:26px">${name}</div><div class="mono" style="font-size:15px;margin-top:6px;color:rgba(244,242,236,.55)">${sub}</div>`);
      let a2 = 0;
      const fills = us.map((u, k) => {
        const x = a2 / 100 * BW; a2 += WT[k][1];
        const tr = box(r, x, 76, '', '', { width: WT[k][1] / 100 * BW - 6 + 'px', height: '34px', borderRadius: '4px', background: 'rgba(244,242,236,.06)' });
        const f = box(tr, 0, 0, '', '', { height: '34px', borderRadius: '4px', background: u < 0 ? 'transparent' : Y, width: Math.max(0, u) * 100 + '%', transformOrigin: '0 50%' });
        return { tr, f };
      });
      const sc_ = box(r, BW + 30, 70, 'mono', '', { fontSize: '40px' });
      return { r, fills, sc_ };
    };
    const rA = mkRow(480, 'Logistics · Munich', 'cap 6.15% · vacancy within floor', [.51, .7, 1, .8]);
    const sA = .45 * .51 + .25 * .7 + .2 * 1 + .1 * .8;
    const rB = mkRow(680, 'A 7% yield hiding 20% vacancy', 'cap 7.0% · vacancy 20%', [1, .8, .6, 0]);
    const sB = .45 * 1 + .25 * .8 + .2 * .6;
    const stamp = box(root, BX + 560, 690, 'chip y', `${I('x', 18, '#111')} FLOOR · vacancy at most 5%`, { fontSize: '17px' });
    const floors = box(root, BX, 900, 'tag', 'Floors (M-0417): vacancy at most 5% · tenant credit at least BB. A strong dimension cannot mask a fatal one.');
    function upd(t) {
      rise(head, t, t0 + .2);
      rise(form, t, t0 + .5);
      segs.forEach(sg => rise(sg.sg, t, W('11', sg.cue) - .15, { dy: 12 }));
      const fA = W('11', 'vacancy') + .5;
      rise(rA.r, t, W('11', 'cap') - .2);
      rA.fills.forEach((f, k) => f.f.style.transform = `scaleX(${pr(t, W('11', segs[k].cue) + .1, .8)})`);
      setText(rA.sc_, (sA * pr(t, fA, .8)).toFixed(2)); rA.sc_.style.color = t > fA ? Y : '#F4F2EC';
      const tb = W('11', 'floors') - .1, tz = W('11', 'zeroes');
      rise(rB.r, t, tb, { dy: 16 });
      rB.fills.forEach((f, k) => f.f.style.transform = `scaleX(${pr(t, tb + .3 + k * .12, .7) * (1 - .85 * pr(t, tz, .6))})`);
      const vB = sB * pr(t, tb + .4, 1.0) * (1 - pr(t, tz, .5));
      setText(rB.sc_, vB.toFixed(2)); rB.sc_.style.color = t > tz ? Y : '#F4F2EC';
      rise(stamp, t, W('11', 'vacancy', 1) - .1, { dy: -10, scale: .1 });
      rise(floors, t, tz + .8, { dy: 10 });
    }
  }

  // ================================================================ F: tie-break -> ranked book
  {
    const t0 = L('12') - .4, t1 = E('12') + .9;
    const sc = scene(t0, t1, upd); const root = sc.el;
    const head = box(root, 140, 150, 'head', 'Near-ties go to the <b>tie-break order</b>, not the clock.');
    const bk = box(root, RX + 20, 290, 'eyebrow y', 'Book · M-0417 · ranked');
    const items = [
      ['Logistics · Hamburg', '0.68', 'WALT 5.4y'],
      ['Logistics · Munich', '0.68', 'WALT 7.1y'],
      ['Logistics · Bremen', '0.61', ''],
      ['Logistics · Kassel', '0.47', ''],
      ['Logistics · Hanover', '0.39', ''],
    ];
    const rows = items.map(([n, v, walt], i) => {
      const r = box(root, RX + 20, 0, '', '', { width: '820px', height: '84px' });
      box(r, 0, 0, 'rule', '', { width: '820px' });
      const rk = box(r, 0, 26, 'mono', `#${i + 1}`, { fontSize: '26px', color: 'rgba(244,242,236,.6)' });
      box(r, 80, 24, '', `<span style="display:inline-flex;gap:12px;align-items:center">${I('warehouse', 24, 'rgba(244,242,236,.75)')}${n}</span>`, { fontSize: '26px' });
      const w = box(r, 470, 30, 'mono', walt, { fontSize: '18px', color: Y });
      box(r, 700, 24, 'mono', v, { fontSize: '28px' });
      return { r, rk, w };
    });
    const tie = box(root, RX + 860, 380, 'chip yo', 'within tolerance');
    const rule1 = box(root, RX + 860, 470, '', `<div class="tag">Tie-break order</div><div class="mono" style="font-size:20px;margin-top:10px">1 · longer WALT<br>2 · lower capex</div>`);
    const clock = box(root, RX + 860, 610, 'chip', `${I('timer', 18)} <s>time priority</s>`, {});
    const foot = box(root, RX + 20, 800, 'sub', 'Every mandate holds its own ranked book. Price comes later.', { fontSize: '26px' });
    function upd(t) {
      rise(head, t, t0 + .2); rise(bk, t, t0 + .4);
      const sw = pr(t, W('12', 'longer') + .3, 1.1, eio);
      rows.forEach((r, i) => {
        rise(r.r, t, t0 + .4 + i * .1, { dx: 20, dy: 0 });
        let pos = i; if (i === 0) pos = lerp(0, 1, sw); if (i === 1) pos = lerp(1, 0, sw);
        r.r.style.top = 340 + pos * 86 + 'px';
        if (i < 2) { fade(r.w, t, W('12', 'longer') - .1, .4); setText(r.rk, `#${Math.round(pos) + 1}`); r.rk.style.color = i === 1 && sw > .5 ? Y : 'rgba(244,242,236,.6)'; }
      });
      rise(tie, t, W('12', 'near') + .2, { dx: -10, dy: 0 });
      rise(rule1, t, W('12', 'go'), { dy: 10 });
      rise(clock, t, W('12', 'never') - .1, { dy: 10 });
      rise(foot, t, W('12', 'each') - .1);
    }
  }
}
