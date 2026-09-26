// 06 THE SELLER — bids scored beyond price. 07 CLEARING — deferred acceptance, step by step.
import { T, h, s, svg, box, I, scene, rise, fade, draw, pulseDot, pr, eo, e3, eio, lerp, clamp, setText, Y } from './core.js';

export default function ch5() {
  const W = T.W.bind(T), L = T.L.bind(T), E = T.E.bind(T);

  // ================================================================ seller ranks bids
  {
    const t0 = L('19') - .5, t1 = E('19') + .8;
    const sc = scene(t0, t1, upd); const root = sc.el;
    const head = box(root, 140, 150, 'head', 'The seller scores bids on <b>more than price</b>.');
    const side = box(root, 140, 300, 'card solid', '', { width: '440px', height: '600px' });
    box(side, 34, 32, 'eyebrow y', "Seller's ranking");
    box(side, 34, 70, 'sub', 'A mandate too: filters, utilities, weights, floors. Rests with the asset, never shown to bidders.', { fontSize: '20px', width: '370px' });
    const dims = [['Price', 'price', 'bid P*, net of conditions'], ['Certainty of close', 'certainty', 'firm term sheet · equity evidenced'], ['Speed', 'speed', 'diligence already run on attested data'], ['Conditionality', 'conditions', 'subject-to clauses remaining']];
    const D = dims.map(([n, cue, d], i) => box(side, 34, 250 + i * 84, '', `<div style="font-size:23px">${n}</div><div class="mono" style="font-size:14px;margin-top:6px;color:rgba(244,242,236,.55)">${d}</div>`));
    const bids = [
      ['Bid A', 'Higher headline price', 'no debt attached · financing contingency', [.95, .3, .4, .35]],
      ['Bid B', 'Slightly lower price', 'firm term sheet attached · L1 · attested', [.85, .95, .85, .85]],
    ];
    const cards = bids.map(([n, a, b, v], i) => {
      const c = box(root, 680, 0, 'card solid', '', { width: '1100px', height: '250px' });
      const rk = box(c, 34, 30, 'mono', '', { fontSize: '44px', color: Y });
      box(c, 130, 34, '', `<div class="eyebrow">${n}</div><div style="font-size:30px;font-weight:300;margin-top:10px">${a}</div><div class="mono" style="font-size:15px;margin-top:10px;color:rgba(244,242,236,.6)">${b}</div>`, { width: '440px' });
      const bars = v.map((x, k) => {
        const lab = box(c, 620, 40 + k * 46, 'tag', ['Price', 'Certainty', 'Speed', 'Conditions'][k]);
        const tr = box(c, 760, 40 + k * 46, '', '', { width: '200px', height: '12px', borderRadius: '6px', background: 'rgba(244,242,236,.08)' });
        const f = box(tr, 0, 0, '', '', { height: '12px', borderRadius: '6px', width: x * 200 + 'px', background: k === 0 ? 'rgba(244,242,236,.6)' : Y, transformOrigin: '0 50%' });
        return { lab, tr, f };
      });
      const tot = box(c, 990, 88, 'mono', '', { fontSize: '40px' });
      return { c, rk, bars, v, tot };
    });
    const note = box(root, 680, 870, 'tag', 'The financing contingency is the single largest source of failed closes');
    function upd(t) {
      rise(head, t, t0 + .2); rise(side, t, t0 + .3, { dx: -30, dy: 0 });
      const cues = [W('19', 'price'), W('19', 'certainty'), W('19', 'speed'), W('19', 'conditions')];
      D.forEach((d, i) => { rise(d, t, cues[i] - .2, { dx: -16, dy: 0 }); d.style.color = t > cues[i] - .2 && t < (cues[i + 1] ?? W('19', 'firm')) ? Y : ''; });
      const sw = pr(t, W('19', 'beat') - .1, 1.1, eio);
      cards.forEach((c, i) => {
        rise(c.c, t, t0 + .6 + i * .15, { dx: 30, dy: 0 });
        const pos = i === 0 ? lerp(0, 1, sw) : lerp(1, 0, sw);
        c.c.style.top = 300 + pos * 280 + 'px';
        c.c.classList.toggle('hot', (i === 1 && sw > .5) || (i === 0 && sw <= .5 && t > cues[0]));
        let tot = 0, wsum = 0;
        c.bars.forEach((b, k) => { const p = pr(t, cues[k] + .1, .7); b.f.style.transform = `scaleX(${p})`; b.lab.style.opacity = b.tr.style.opacity = pr(t, cues[k] - .1, .4); tot += c.v[k] * (p > .02 ? 1 : 0); wsum += (p > .02 ? 1 : 0); });
        setText(c.tot, wsum ? (tot / wsum).toFixed(2) : ''); c.tot.style.color = (i === 1 && sw > .5) ? Y : '#F4F2EC';
        setText(c.rk, `#${Math.round(pos) + 1}`); c.rk.style.opacity = pr(t, cues[0], .5);
      });
      rise(note, t, W('19', 'debt') - .1, { dy: 10 });
    }
  }

  // ================================================================ clearing: deferred acceptance
  {
    const t0 = L('20') - .5, t1 = W('23', 'so') - .35;
    const sc = scene(t0, t1, upd); const root = sc.el;
    const head = box(root, 140, 150, 'head', 'Clearing is <b>deferred acceptance</b>, not price-time priority.');
    const steps = ['01 Mandates propose', '02 Assets hold, tentatively', '03 Released mandates move down', '04 Stop when nobody moves'];
    const S = steps.map((st, i) => box(root, 140 + i * 420, 262, 'eyebrow', st, { fontSize: '16px' }));
    const stepT = [W('20', 'proposes') - .3, W('21', 'holds') - .3, W('22', 'released') - .2, W('23', 'nobody') - .2];

    const MX = 300, AX = 1260, CW = 360, CH = 130, rowY = i => 380 + i * 190;
    const M = [['M-0417', ['A', 'B', 'C']], ['M-2', ['A', 'C', 'B']], ['M-3', ['B', 'A', 'C']]];
    const A_ = [['A', ['M-2', 'M-0417', 'M-3']], ['B', ['M-0417', 'M-3', 'M-2']], ['C', ['M-3', 'M-2', 'M-0417']]];
    const chipList = (list, own) => list.map(x => `<span class="mono" data-k="${x}" style="display:inline-block;padding:4px 10px;margin-right:6px;border:1px solid rgba(244,242,236,.2);border-radius:6px;font-size:14px">${x}</span>`).join('');
    const mC = M.map(([n, list], i) => box(root, MX, rowY(i), 'card solid', `<div style="padding:20px 24px"><div style="display:flex;gap:12px;align-items:center">${I('target', 26, i === 0 ? Y : '#F4F2EC')}<span style="font-size:26px">Mandate ${n}</span></div><div style="margin-top:16px"><span class="tag" style="margin-right:10px">book</span>${chipList(list)}</div></div>`, { width: CW + 'px', height: CH + 'px' }));
    const aC = A_.map(([n, list], i) => box(root, AX, rowY(i), 'card solid', `<div style="padding:20px 24px"><div style="display:flex;gap:12px;align-items:center">${I('warehouse', 26)}<span style="font-size:26px">Asset ${n}</span></div><div style="margin-top:16px"><span class="tag" style="margin-right:10px">seller</span>${chipList(list)}</div></div>`, { width: CW + 'px', height: CH + 'px' }));
    box(root, MX, 330, 'tag', 'Buy mandates · propose');
    box(root, AX, 330, 'tag', 'Assets · seller ranking decides');
    const colL = root.lastChild.previousSibling, colR = root.lastChild;
    const sv = svg(root);
    const mi = { 'M-0417': 0, 'M-2': 1, 'M-3': 2 }, ai = { A: 0, B: 1, C: 2 };
    const pathFor = (m, a, off) => { const y0 = rowY(m) + CH / 2 + off, y1 = rowY(a) + CH / 2 + off * 1.6; const x0 = MX + CW, x1 = AX; return `M${x0},${y0} C${x0 + 240},${y0} ${x1 - 240},${y1} ${x1},${y1}`; };
    // proposals: [mandate, asset, t propose, t hold (or null), t release (or null)]
    const tP1 = W('20', 'proposes'), tH = W('21', 'holds'), tR = W('21', 'releases');
    const tM = W('22', 'move'), tQ = W('22', 're-quoting');
    const P = [
      ['M-0417', 'A', tP1, null, tR, -10],
      ['M-2', 'A', tP1 + .25, tH, null, 10],
      ['M-3', 'B', tP1 + .5, tH + .3, tM + 1.6, 10],
      ['M-0417', 'B', tM - .1, tM + 1.5, null, -10],
      ['M-3', 'A', tM + 2.2, null, tM + 3.1, 20],
      ['M-3', 'C', tM + 3.4, tM + 4.1, null, 0],
    ].map(([m, a, tp, th, tr, off]) => {
      const d = pathFor(mi[m], ai[a], off);
      const base = s('path', { d, fill: 'none', stroke: 'rgba(244,242,236,.55)', 'stroke-width': 2, pathLength: 1 }, sv);
      const dot = pulseDot(sv, 6);
      return { m, a, tp, th, tr, base, dot };
    });
    const reqChip = box(root, 820, 0, 'chip yo', `${I('refresh-cw', 16, Y)} debt re-quoted for (B, M-0417)`, { fontSize: '14px' });
    const relTags = [];
    const lockIcons = [['M-2', 'A'], ['M-0417', 'B'], ['M-3', 'C']].map(([m, a]) => box(root, AX - 46, rowY(ai[a]) + CH / 2 - 16, '', I('lock', 30, Y)));
    const blocking = s('path', { d: pathFor(0, 0, -40), fill: 'none', stroke: 'rgba(244,242,236,.6)', 'stroke-width': 2, 'stroke-dasharray': '6 8' }, sv);
    const blockTag = box(root, 800, 330, 'chip', `${I('x', 16)} M-0417 would prefer A, but A's seller prefers M-2: no blocking pair`, { fontSize: '14px' });
    const stable = box(root, 140, 960, 'sub', 'A stable set: nobody can do better by going around the platform.', { fontSize: '24px' });
    const ill = box(root, 0, 0, 'illus', 'Illustrative books · after Gale and Shapley, adapted to standing books');

    // which asset each mandate is pointing at (for the chip highlight)
    const cursor = (m, t) => { let cur = null; for (const p of P) if (p.m === m && t >= p.tp) cur = p.a; return cur; };

    function upd(t) {
      rise(head, t, t0 + .2);
      S.forEach((st, i) => { rise(st, t, stepT[i] - .2, { dy: 8 }); st.style.color = (t > stepT[i] && (i === 3 || t < stepT[i + 1])) ? Y : ''; });
      mC.forEach((c, i) => rise(c, t, t0 + .4 + i * .12, { dx: -30, dy: 0 }));
      aC.forEach((c, i) => rise(c, t, t0 + .6 + i * .12, { dx: 30, dy: 0 }));
      fade(colL, t, t0 + .6, .5); fade(colR, t, t0 + .8, .5);
      fade(ill, t, t0 + 1.5, .6);
      // mandate book cursors
      M.forEach(([n], i) => { const cur = cursor(n, t); mC[i].querySelectorAll('[data-k]').forEach(ch => { const on = ch.dataset.k === cur; ch.style.borderColor = on ? Y : 'rgba(244,242,236,.2)'; ch.style.color = on ? Y : ''; }); });
      // asset holds
      A_.forEach(([n], i) => {
        let held = null; for (const p of P) if (p.a === n && p.th != null && t >= p.th && !(p.tr != null && t >= p.tr)) held = p.m;
        aC[i].querySelectorAll('[data-k]').forEach(ch => { const on = ch.dataset.k === held; ch.style.borderColor = on ? Y : 'rgba(244,242,236,.2)'; ch.style.color = on ? Y : ''; ch.style.background = on ? 'rgba(255,190,6,.1)' : ''; });
        aC[i].classList.toggle('hot', !!held && t > stepT[3]);
      });
      // proposals
      P.forEach(p => {
        const dp = pr(t, p.tp, .8, eio);
        const rel = p.tr != null ? pr(t, p.tr, .7, eio) : 0;
        const held = p.th != null && t >= p.th && rel === 0;
        // draw forward, retract back toward the mandate on release
        const vis = dp * (1 - rel);
        p.base.setAttribute('stroke-dasharray', '1 1'); p.base.setAttribute('stroke-dashoffset', 1 - vis);
        p.base.style.opacity = vis > 0 ? 1 : 0;
        const hk = p.th != null ? pr(t, p.th, .4) * (1 - rel) : 0;
        p.base.setAttribute('stroke', held ? Y : (rel > 0 ? 'rgba(244,242,236,.3)' : 'rgba(244,242,236,.55)'));
        p.base.setAttribute('stroke-width', 2 + hk * 2);
        p.dot.at(p.base, pr(t, p.tp, .8, eio) < 1 ? pr(t, p.tp, .8, eio) : 0);
      });
      const rq = P[3];
      reqChip.style.top = (rowY(0) + rowY(1)) / 2 + 36 + 'px';
      rise(reqChip, t, tQ - .2, { dy: 8, out: W('23', 'nobody') });
      lockIcons.forEach((l, i) => rise(l, t, W('23', 'stable') - .1 + i * .12, { scale: .3, dy: 0 }));
      const tb = W('23', 'prefer') - .6;
      const bp = pr(t, tb, .8, eio) * (1 - pr(t, W('23', 'hold') + .4, .5));
      blocking.style.opacity = bp;
      rise(blockTag, t, tb + .3, { dy: 8, out: W('23', 'hold') + .5 });
      rise(stable, t, W('23', 'hold') - .2, { dy: 10 });
    }
  }
}
