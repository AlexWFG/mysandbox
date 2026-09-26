// 08 A LIVING BOOK — four events re-run the engine; decay replaces time priority. 09 THE CLAIM.
import { T, h, s, svg, box, I, scene, rise, fade, draw, pulseDot, pr, eo, e3, eio, lerp, clamp, setText, Y } from './core.js';

export default function ch6() {
  const W = T.W.bind(T), L = T.L.bind(T), E = T.E.bind(T);

  // ================================================================ a living book
  {
    const t0 = L('24') - .8, t1 = L('26') - 1.0;
    const sc = scene(t0, t1, upd); const root = sc.el;
    const head = box(root, 140, 150, 'head', 'Nothing in the book is still. <b>Four events re-run the engine.</b>');
    const ev = [['file-check', 'Asset state', 'new attestation: re-scores the asset in every book', 'attestations'],
      ['sliders-horizontal', 'Mandate change', 'weight, floor or target moves', 'amended'],
      ['landmark', 'Credit box fill', 'capacity drops; pairs fall to the next lender', 'filled'],
      ['percent', 'Rates and grids', 'every P* in the system shifts at once', 'rate']];
    const EV = ev.map(([ic, n, d, cue], i) => {
      const c = box(root, 140, 300 + i * 150, 'card solid', `<div style="display:flex;gap:18px;align-items:center;padding:22px 24px">${I(ic, 30)}<div><div style="font-size:24px">${n}</div><div class="mono" style="font-size:13px;margin-top:6px;color:rgba(244,242,236,.55)">${d}</div></div></div>`, { width: '470px', height: '118px' });
      return { c, cue };
    });
    const sv = svg(root);
    const ex = 800, ey = 600;
    const ring = s('circle', { cx: ex, cy: ey, r: 110, fill: 'rgba(255,190,6,.05)', stroke: Y, 'stroke-width': 2, 'stroke-dasharray': '14 10' }, sv);
    const core = box(root, ex - 90, ey - 40, '', `<div style="width:180px;text-align:center"><div class="eyebrow y">Engine</div><div class="mono" style="font-size:14px;margin-top:10px;color:rgba(244,242,236,.6)">re-runs affected pairs</div></div>`);
    const paths = EV.map((e, i) => s('path', { d: `M610,${359 + i * 150} C660,${359 + i * 150} 650,${ey} ${ex - 112},${ey}`, fill: 'none', stroke: 'rgba(244,242,236,.25)', 'stroke-width': 1.5, pathLength: 1 }, sv));
    const dots = EV.map(() => pulseDot(sv, 6));
    // three books; asset X sinks in all of them once it stops attesting
    const books = [['M-0417', 0], ['M-2', 1], ['M-3', 0]];
    const others = [['Hamburg', 'Bremen', 'Kassel', 'Hanover'], ['Frankfurt', 'Cologne', 'Essen', 'Mainz'], ['Munich', 'Leipzig', 'Dresden', 'Bonn']];
    const BK = books.map(([n, start], b) => {
      const x = 1040 + b * 260;
      box(root, x, 300, 'eyebrow', `Book · ${n}`, { fontSize: '14px' });
      const rows = others[b].map(o => box(root, x, 0, 'card solid', `<div class="mono" style="font-size:15px;padding:14px 16px;color:rgba(244,242,236,.7)">${o}</div>`, { width: '230px', height: '52px' }));
      const xr = box(root, x, 0, 'card hot', `<div class="mono" style="font-size:15px;padding:14px 16px;color:#FFBE06">Asset X · <span class="cv">c 1.00</span></div>`, { width: '230px', height: '52px' });
      return { x, rows, xr, start, hd: root.lastChild };
    });
    const heads = [...root.querySelectorAll('.eyebrow')].filter(e => e.textContent.startsWith('Book'));
    const rk = BK.map(bk => box(root, bk.x - 30, 0, 'mono', '', { fontSize: '14px' }));
    const decay = box(root, 1040, 700, '', `<div class="eyebrow y">Decay replaces time priority</div><div class="sub" style="font-size:22px;margin-top:12px;width:740px">In an order book the earliest order wins. Here the freshest attestation wins.</div>`);
    function upd(t) {
      rise(head, t, t0 + .2);
      const pulse = EV.map(e => W('24', e.cue) - .2);
      EV.forEach((e, i) => { rise(e.c, t, pulse[i] - .3, { dx: -30, dy: 0 }); draw(paths[i], t, pulse[i], .5); dots[i].at(paths[i], pr(t, pulse[i] + .2, .9, eio)); e.c.classList.toggle('hot', t > pulse[i] && t < pulse[i] + 1.2); });
      rise(core, t, t0 + .6, { scale: .2, dy: 0 }); fade(ring, t, t0 + .5, .6);
      const hit = Math.max(...pulse.map(p => Math.exp(-Math.max(0, t - p - 1.1) * 3) * (t > p + 1.1 ? 1 : 0)));
      ring.setAttribute('stroke-dashoffset', -t * 30); ring.setAttribute('r', 110 + hit * 10); ring.setAttribute('fill', `rgba(255,190,6,${.05 + hit * .12})`);
      const ts = W('24', 'stop', 1) - .1, sink = pr(t, W('24', 'sinks') - .6, 1.6, eio);
      const c = lerp(1, .38, pr(t, ts, 1.8, e3));
      heads.forEach((hh, i) => fade(hh, t, t0 + .8 + i * .1, .5));
      BK.forEach((bk, b) => {
        const pos = lerp(bk.start, 4, sink);
        let k = 0;
        bk.rows.forEach((r, i) => {
          const slot = i < bk.start ? i : i + 1;             // before
          const slotAfter = i;                                 // after X sinks to the bottom
          r.style.top = 340 + lerp(slot, slotAfter, sink) * 62 + 'px';
          rise(r, t, t0 + .9 + b * .1 + i * .05, { dy: 10 });
        });
        bk.xr.style.top = 340 + pos * 62 + 'px';
        rise(bk.xr, t, t0 + 1.1 + b * .1, { dy: 10 });
        setText(bk.xr.querySelector('.cv'), `c ${c.toFixed(2)}`);
        setText(rk[b], `#${Math.round(pos) + 1}`); rk[b].style.top = 340 + pos * 62 + 16 + 'px'; rk[b].style.color = Y; fade(rk[b], t, t0 + 1.4, .4);
      });
      rise(decay, t, W('24', 'stop', 1) + .8, { dy: 12 });
    }
  }

  // ================================================================ the claim
  {
    const t0 = L('26') - 1.0, t1 = E('27') + 1.9;
    const tBig = L('27') - .5;
    const sc = scene(t0, t1, upd, { fo: 1.0 }); const root = sc.el;
    const head = box(root, 140, 150, 'head', 'The engine is <b>known mathematics</b>. The data is not.');
    const layers = [
      ['03', 'The matching engine', 'books · scoring · pair quoting · deferred acceptance · hold windows', 'known'],
      ['02', 'Validation engine', 'c(t) for every field · gates the credit boxes · Proof of Permission and Agency', 'trust'],
      ['01', 'Ingestion and structuring', 'produces the asset vector: one schema, tiered categoricals, derived fields', 'vector'],
    ];
    const LY = layers.map(([n, a, b, cue], i) => {
      const c = box(root, 140, 300 + i * 150, 'card solid', `<div style="display:flex;align-items:center;gap:28px;padding:0 34px;height:124px"><span class="mono y" style="font-size:22px">${n}</span><div><div style="font-size:30px;font-weight:300">${a}</div><div class="mono" style="font-size:15px;margin-top:8px;color:rgba(244,242,236,.6)">${b}</div></div></div>`, { width: '1640px', height: '124px' });
      return { c, cue };
    });
    const known = box(root, 1500, 344, 'chip', 'known mathematics', { fontSize: '15px' });
    const missing = [box(root, 1380, 644, 'chip y', 'an attested vector', { fontSize: '15px' }), box(root, 1330, 494, 'chip y', 'a credit box that can trust it', { fontSize: '15px' })];
    const flow = ['List', 'Diligence', 'Match', 'Finance', 'Settle'];
    const F = flow.map((f, i) => box(root, 140 + i * 336, 790, '', `<div class="mono" style="font-size:15px;color:rgba(244,242,236,.5)">0${i + 1}</div><div style="font-size:26px;margin-top:6px">${f}</div>`));
    const fl = box(root, 140, 880, 'rule', '', { width: '1640px' });
    const fsv = svg(root);
    const fp = s('path', { d: 'M140,880 L1780,880', stroke: 'none', fill: 'none' }, fsv);
    const fd = pulseDot(fsv, 6);
    const big = box(root, 0, 470, 'big', 'Matching is a <span class="y">data outcome</span>.', { width: '1920px', textAlign: 'center', fontSize: '104px' });
    const all = [head, ...LY.map(l => l.c), known, ...missing, ...F, fl];
    function upd(t) {
      const out = tBig - .1;
      rise(head, t, t0 + .2, { out });
      LY.forEach((l, i) => rise(l.c, t, t0 + .4 + i * .15, { dy: 20, out }));
      const k = W('26', 'known'), wh = W('26', 'what');
      rise(known, t, k, { dx: 10, dy: 0, out });
      const lit = [t > k - .2 && t < wh, t > W('26', 'credit') - .2, t > W('26', 'attested') - .2];
      LY.forEach((l, i) => l.c.classList.toggle('hot', lit[i]));
      rise(missing[0], t, W('26', 'attested') - .1, { dx: 10, dy: 0, out }); rise(missing[1], t, W('26', 'credit') - .1, { dx: 10, dy: 0, out });
      F.forEach((f, i) => rise(f, t, t0 + 1.0 + i * .12, { dy: 10, out }));
      fade(fl, t, t0 + 1.0, .6, out, .4);
      const cyc = ((t - t0 - 1.4) / 3.2);
      fd.at(fp, cyc > 0 && t < out ? cyc % 1 : 0);
      F.forEach((f, i) => { const p = cyc % 1; const on = cyc > 0 && Math.abs(p - (i * 336 + 20) / 1640) < .06; f.style.color = on ? Y : ''; });
      rise(big, t, L('27') - .1, { dy: 30, d: 1.2 });
    }
  }
}
