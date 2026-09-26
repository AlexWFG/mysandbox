// 01 THE PROBLEM — the order book, why real estate breaks it, the two-sided ranked market.
import { T, h, s, svg, box, I, scene, rise, fade, draw, pulseDot, pr, eo, e3, eio, lerp, clamp, Y } from './core.js';

export default function ch1() {
  const W = T.W.bind(T), L = T.L.bind(T), E = T.E.bind(T);
  const t0 = W('01', 'that') - .35, t1 = E('03') + .9;
  const tB = L('02') - .2;               // real estate
  const tC = W('02', 'buyers') - .1;     // two-sided layout

  const sc = scene(t0, t1, update);
  const root = sc.el;

  // ---------------- headlines
  const hA = box(root, 140, 150, 'head', 'An order book matches <b>identical</b> things on one axis.');
  const hB = box(root, 140, 150, 'head', 'Real estate has none of that.');
  const hC = box(root, 140, 150, 'head', 'A two-sided, <b>ranked</b> matching market.');
  const subC = box(root, 142, 232, 'sub', 'Standing intents on both sides. Each side scores the other.');

  // ---------------- A: the ladder
  const lad = h('div.abs', { style: { left: '300px', top: '310px', width: '700px', height: '640px', transformOrigin: '0 0', scale: '1.2' } }, root);
  const rows = [];
  const prices = ['23.34', '23.33', '23.32', '23.31', '23.30', '23.29', '23.28', '23.27', '23.26', '23.25'];
  const sizes = [5, 7, 4, 6, 3, 4, 6, 8, 5, 7];
  prices.forEach((p, i) => {
    const ask = i < 5; const y = i * 58 + (ask ? 0 : 36);
    const r = box(lad, 0, y, '', '', { width: '700px', height: '44px' });
    box(r, 0, 8, 'mono', p, { fontSize: '22px', color: ask ? 'rgba(244,242,236,.75)' : 'rgba(244,242,236,.75)' });
    box(r, 110, 12, 'tag', ask ? 'ask' : 'bid', {});
    const toks = [];
    for (let k = 0; k < sizes[i]; k++) toks.push(box(r, 180 + k * 46, 4, '', '', { width: '36px', height: '36px', borderRadius: '6px', border: '1px solid rgba(244,242,236,.35)', background: ask ? 'rgba(244,242,236,.06)' : 'rgba(244,242,236,.12)' }));
    rows.push({ r, toks, ask });
  });
  const spread = box(lad, 0, 5 * 58 - 6, 'rule', '', { width: '640px', top: 5 * 58 + 10 + 'px', background: 'rgba(255,190,6,.5)' });
  const match = box(lad, 540, 5 * 58 - 10, 'chip y', 'MATCH · 23.30');
  const labsA = [
    box(root, 1240, 420, 'eyebrow', '<span class="y">01</span>&nbsp;&nbsp;One identical instrument', { fontSize: '22px' }),
    box(root, 1240, 500, 'eyebrow', '<span class="y">02</span>&nbsp;&nbsp;One axis: price', { fontSize: '22px' }),
    box(root, 1240, 580, 'eyebrow', '<span class="y">03</span>&nbsp;&nbsp;Price-time priority', { fontSize: '22px' }),
    box(root, 1240, 660, 'eyebrow', '<span class="y">04</span>&nbsp;&nbsp;No judgment needed', { fontSize: '22px' }),
  ];

  // ---------------- B: unique assets with value vectors
  const assets = [
    ['warehouse', 'Logistics', 'Hamburg', [.7, .5, .8, .6, .3]],
    ['building-2', 'Office', 'Frankfurt', [.45, .8, .9, .85, .5]],
    ['hotel', 'Hotel', 'Berlin', [.8, .35, .5, .7, .75]],
    ['store', 'Retail', 'Munich', [.55, .65, .4, .9, .4]],
    ['building', 'Residential', 'Leipzig', [.4, .9, .7, .45, .6]],
  ];
  const dims = ['Yield', 'Term', 'Credit', 'Loc.', 'Capex'];
  const cards = assets.map(([ic, cls, city, v], i) => {
    const pos = box(root, 140 + i * 336, 330, '', '', { width: '306px', height: '430px' });
    const c = box(pos, 0, 0, 'card solid', '', { width: '306px', height: '430px' });
    box(c, 30, 30, '', I(ic, 48, '#F4F2EC'));
    box(c, 30, 104, '', `<div style="font-size:30px;font-weight:400">${cls}</div><div class="tag" style="margin-top:8px;font-size:14px">${city}</div>`);
    const bars = v.map((x, k) => {
      const b = box(c, 32 + k * 52, 220, '', '', { width: '28px', height: '140px', background: 'rgba(244,242,236,.07)', borderRadius: '3px' });
      const f = box(b, 0, 0, '', '', { width: '28px', bottom: '0', top: 'auto', height: x * 140 + 'px', background: k === 0 ? Y : 'rgba(244,242,236,.55)', borderRadius: '3px', transformOrigin: '50% 100%' });
      box(c, 28 + k * 52, 374, 'tag', dims[k], { fontSize: '11px', letterSpacing: '.04em', width: '38px', textAlign: 'center' });
      return f;
    });
    // compact version for the two-sided layout
    const mini = box(root, 170, 330 + i * 118, 'card solid', `<div style="display:flex;gap:18px;align-items:center;padding:0 24px;height:96px">${I(ic, 32, '#F4F2EC')}<div style="width:190px"><div style="font-size:22px">${cls}</div><div class="tag" style="margin-top:5px">${city}</div></div>` +
      `<div style="display:flex;gap:6px;align-items:flex-end;height:44px">${v.map((x, k) => `<div style="width:12px;height:${x * 44}px;background:${k === 0 ? Y : 'rgba(244,242,236,.55)'};border-radius:2px"></div>`).join('')}</div></div>`, { width: '420px', height: '96px' });
    return { pos, c, bars, mini };
  });
  const vecLab = box(root, 140, 890, 'eyebrow', '<span class="y">Value is a vector</span>&nbsp;&nbsp;·&nbsp;&nbsp;yield · term · credit · location · capex');
  const uniqLab = box(root, 140, 950, 'eyebrow', 'No two are substitutes');

  // ---------------- C: two columns + mutual scoring
  const mandates = ['Core logistics', 'Value-add office', 'Yield-hungry', 'Capital preservation'];
  const mcards = mandates.map((m, i) => {
    const c = box(root, 1330, 330 + i * 148, 'card solid', `<div style="display:flex;gap:18px;align-items:center;padding:24px 26px">${I('target', 34, i === 0 ? Y : '#F4F2EC')}<div><div style="font-size:24px">${m}</div><div class="tag" style="margin-top:6px">buy mandate · standing</div></div></div>`, { width: '420px', height: '112px' });
    return c;
  });
  const colA = box(root, 170, 292, 'eyebrow', 'Assets · sellers rank bids');
  const colM = box(root, 1330, 300 - 8, 'eyebrow', 'Mandates · buyers rank assets');
  const sv = svg(root);
  const aY = i => 330 + i * 118 + 48, mY = i => 330 + i * 148 + 56;
  const links = [[0, 0], [0, 2], [1, 1], [2, 2], [3, 3], [4, 3], [1, 0], [3, 2], [2, 1]];
  const lk = links.map(([a, m], i) => {
    const x0 = 596, x1 = 1324, y0 = aY(a), y1 = mY(m);
    const p = s('path', { d: `M${x0},${y0} C${x0 + 300},${y0} ${x1 - 300},${y1} ${x1},${y1}`, fill: 'none', stroke: i === 0 ? Y : 'rgba(244,242,236,.28)', 'stroke-width': i === 0 ? 2 : 1.3, pathLength: 1 }, sv);
    return p;
  });
  const dots = [pulseDot(sv, 5), pulseDot(sv, 5)];
  const rankM = links.map(([a, m], i) => box(root, 1270, mY(m) - 14 + (i % 2 ? 16 : -16), 'mono', '', { fontSize: '14px', color: 'rgba(244,242,236,.6)' }));
  const rankA = links.map(([a, m], i) => box(root, 612 + (i % 3) * 34, aY(a) - 26, 'mono', '', { fontSize: '14px', color: 'rgba(244,242,236,.6)' }));
  const rankTxt = [['#1', '#2'], ['#3', '#1'], ['#1', '#2'], ['#2', '#1'], ['#1', '#3'], ['#2', '#1'], ['#2', '#3'], ['#3', '#2'], ['#2', '#3']];
  links.forEach((_, i) => { rankM[i].textContent = rankTxt[i][0]; rankA[i].textContent = ''; });

  function update(t) {
    // --- A
    const outA = tB + .1;
    rise(hA, t, t0 + .1, { out: outA - .3 });
    fade(lad, t, t0, .4, outA + .3, .6);
    rows.forEach((r, i) => {
      rise(r.r, t, t0 + .15 + i * .06, { dx: r.ask ? 20 : -20, dy: 0, d: .7 });
      r.toks.forEach((k, j) => {
        const on = pr(t, t0 + .5 + i * .05 + j * .03, .5);
        k.style.opacity = on;
        const hi = pr(t, W('01', 'identical'), .5) * (1 - pr(t, W('01', 'price'), .5));
        k.style.borderColor = `rgba(${hi > .01 ? '255,190,6' : '244,242,236'},${.35 + hi * .5})`;
      });
    });
    const mt = E('01') - 1.2;
    // best bid + best ask meet
    const m = pr(t, mt, .8, eio);
    rows[4].r.style.transform = `translate(0, ${m * 18}px)`; rows[5].r.style.transform = `translate(0, ${-m * 18}px)`;
    spread.style.opacity = pr(t, W('01', 'price'), .6) * (1 - m);
    fade(match, t, mt + .6, .4);
    labsA.forEach((l, i) => rise(l, t, [W('01', 'identical'), W('01', 'price'), mt, mt + .5][i], { dx: -24, dy: 0, out: outA - .2 }));

    // --- B -> C: cards
    rise(hB, t, tB + .3, { out: tC - .1 });
    cards.forEach((c, i) => {
      rise(c.pos, t, tB + .5 + i * .14, { dy: 40, d: 1.0, out: tC + i * .06, dout: .5 });
      rise(c.mini, t, tC + .35 + i * .08, { dx: -30, dy: 0 });
      c.bars.forEach((b, k) => { b.style.transform = `scaleY(${pr(t, W('02', 'vector') - .3 + k * .07 + i * .05, .7)})`; });
    });
    rise(vecLab, t, W('02', 'vector'), { dx: -20, dy: 0, out: tC });
    rise(uniqLab, t, W('02', 'alike') - .2, { dx: -20, dy: 0, out: tC });

    // --- C
    rise(hC, t, L('03') + .2); rise(subC, t, W('03', 'standing'));
    rise(colA, t, tC + .8); rise(colM, t, tC + .8);
    mcards.forEach((c, i) => rise(c, t, tC + .6 + i * .12, { dx: 30, dy: 0 }));
    lk.forEach((p, i) => draw(p, t, tC + 1.2 + i * .12, 1.1));
    rankM.forEach((r, i) => rise(r, t, tC + 2.0 + i * .1, { dy: 0, dx: 8 }));
    const st = W('03', 'score');
    dots[0].at(lk[0], pr(t, st - .6, 1.4, eio)); dots[1].at(lk[0], 1 - pr(t, st + .4, 1.4, eio));
  }
}
