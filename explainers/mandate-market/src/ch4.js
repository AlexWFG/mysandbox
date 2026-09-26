// 04 THE DEBT — lenders quote the pair. 05 FROM SCORE TO BID — the worked example.
import { T, h, s, svg, box, I, scene, rise, fade, draw, pulseDot, pr, eo, e3, eio, lerp, clamp, setText, Y } from './core.js';

export default function ch4() {
  const W = T.W.bind(T), L = T.L.bind(T), E = T.E.bind(T);

  // ================================================================ the pair and the credit boxes
  {
    const t0 = W('13', 'they') - .25, t1 = E('14') + .7;
    const sc = scene(t0, t1, upd); const root = sc.el;
    const head = box(root, 140, 150, 'head', 'Lenders don\'t quote the asset or the buyer. <b>They quote the pair.</b>');
    const card = (x, y, w, hh, ey, title, body, cls = 'card solid') => box(root, x, y, cls, `<div style="padding:28px 30px"><div class="eyebrow ${cls.includes('hot') ? 'y' : ''}">${ey}</div><div style="font-size:30px;font-weight:300;margin-top:12px">${title}</div><div class="mono" style="font-size:15px;line-height:1.6;margin-top:14px;color:rgba(244,242,236,.62)">${body}</div></div>`, { width: w + 'px', height: hh + 'px' });
    const cA = card(140, 300, 400, 250, 'Asset a', 'Collateral', 'attested NOI · WALT · tenant credit<br>vacancy · class · in-place debt');
    const cM = card(140, 600, 400, 250, 'Mandate m', 'Sponsor', 'entity · tier · track record<br>guarantees · equity committed<br>Know Your Agent identity');
    const cP = card(650, 420, 360, 310, 'The pair (a, m)', 'Collateral × sponsor', 'the object every credit box evaluates', 'card hot');
    const boxes = [['Credit box L1', 'fires', '55% LTV · 185 bps', 'fifty-five'], ['Credit box L2', 'fires', '60% LTV · 210 bps', 'sixty'], ['Credit box L3', 'silent', 'sponsor below tier', 'silent']];
    const B = boxes.map(([n, st, q, cue], i) => {
      const b = box(root, 1130, 300 + i * 190, 'card solid', `<div style="padding:24px 28px"><div style="display:flex;justify-content:space-between"><span class="eyebrow">${n}</span><span class="mono" style="font-size:15px;color:${i < 2 ? Y : 'rgba(244,242,236,.45)'}">${st}</span></div><div class="mono" style="font-size:${i < 2 ? 24 : 20}px;margin-top:22px;white-space:nowrap;color:${i < 2 ? '#F4F2EC' : 'rgba(244,242,236,.45)'}">${i < 2 ? '' : I('lock', 20, 'rgba(244,242,236,.45)').replace('class="ico"', 'class="ico" style="display:inline;vertical-align:-3px;margin-right:10px"')}${q}</div></div>`, { width: '330px', height: '150px' });
      return { b, cue };
    });
    const qs = box(root, 1510, 390, 'card solid', `<div style="padding:26px 26px"><div class="eyebrow y">Quote set for (a, m)</div><div class="sub" style="font-size:21px;margin-top:14px;line-height:1.45">Ranked on proceeds, spread, term, covenants. The best attaches to the pair.</div></div>`, { width: '280px', height: '270px' });
    const gate = box(root, 650, 800, 'chip yo', `${I('shield-check', 20, Y)} Gate: NOI attested within 60 days · no attestation, no quote`, { fontSize: '17px' });
    const ill = box(root, 0, 0, 'illus', 'Quotes shown are illustrative');
    const sv = svg(root);
    const pth = (d, c = 'rgba(244,242,236,.3)') => s('path', { d, fill: 'none', stroke: c, 'stroke-width': 1.6, pathLength: 1 }, sv);
    const pA = pth('M540,425 C600,425 600,520 650,540'), pM = pth('M540,725 C600,725 600,630 650,610');
    const pB = [0, 1, 2].map(i => pth(`M1010,575 C1070,575 1070,${375 + i * 190} 1130,${375 + i * 190}`, i < 2 ? 'rgba(255,190,6,.7)' : 'rgba(244,242,236,.2)'));
    const pQ = [0, 1].map(i => pth(`M1460,${375 + i * 190} C1485,${375 + i * 190} 1485,525 1510,525`, 'rgba(255,190,6,.7)'));
    const dots = [0, 1, 2, 3].map(() => pulseDot(sv, 5));
    function upd(t) {
      rise(head, t, t0 + .1);
      rise(cA, t, t0 + .2, { dx: -30, dy: 0 }); rise(cM, t, t0 + .35, { dx: -30, dy: 0 });
      const tp = W('13', 'pair') - .2;
      draw(pA, t, tp - .3, .7); draw(pM, t, tp - .3, .7);
      rise(cP, t, tp, { scale: .06, dy: 0 });
      B.forEach((b, i) => { rise(b.b, t, W('14', b.cue) - .5, { dx: 30, dy: 0 }); draw(pB[i], t, W('14', b.cue) - .7, .6); if (i < 2) dots[i].at(pB[i], pr(t, W('14', b.cue) - .6, 1.0, eio)); });
      pB[2].style.strokeDasharray = '0.02 0.02';
      rise(qs, t, W('14', 'tier') + .2, { dx: 30, dy: 0 });
      pQ.forEach((p, i) => { draw(p, t, W('14', 'tier') + i * .15, .5); dots[2 + i].at(p, pr(t, W('14', 'tier') + .4 + i * .15, .8, eio)); });
      rise(gate, t, W('14', 'attested') - .3, { dy: 14 });
      fade(ill, t, t0 + 2, .6);
    }
  }

  // ================================================================ from score to bid
  {
    const t0 = L('15') - .5, t1 = L('19') - .5;
    const tB = L('16') - .2, tC = L('17') - .2;
    const sc = scene(t0, t1, upd); const root = sc.el;
    const hA = box(root, 140, 150, 'head', 'Price depends on debt. <b>Debt depends on price.</b>');
    const hB = box(root, 140, 150, 'head', 'The lender offers <b>the least of three tests</b>.');
    const hC = box(root, 140, 150, 'head', 'Bid the <b>highest price</b> that still meets the return.');
    const ill = box(root, 0, 0, 'illus', 'Worked illustration from the deck · not a valuation');

    // worked-example ledger (left)
    const led = box(root, 140, 280, 'card solid', '', { width: '560px', height: '680px' });
    box(led, 32, 28, 'eyebrow y', 'Worked example');
    const rowsDef = [
      ['Attested NOI', '€800k', W('15', 'eight') - .1],
      ['Test price P', '€13.0M', W('15', 'thirteen') - .1],
      ['Implied cap rate', '6.15%', W('15', 'thirteen') + .5],
      ['L1: LTV · DSCR · debt yield', '55% · 1.30× · 7.5%', tB + .4],
      ['Debt constant k', '6.5%', tB + .8],
      ['Binding: LTV → D(P)', '€7.15M', W('16', 'binds')],
      ['Equity E(P) = P − D(P)', '€5.85M', W('17', 'five') - .1],
      ['Debt service · cash to equity', '€465k · €335k', W('17', 'equity') + .1],
      ['Year-one cash yield on equity', '5.7%', W('17', 'equity') + .5],
      ['Target (M-0417)', '12% levered IRR', W('17', 'twelve') - .1],
    ];
    const LR = rowsDef.map(([a, b, at], i) => {
      const r = box(led, 32, 84 + i * 58, '', `<div style="display:flex;justify-content:space-between;align-items:baseline;width:496px"><span style="font-size:19px;color:rgba(244,242,236,.75)">${a}</span><span class="mono" style="font-size:20px">${b}</span></div>`);
      box(led, 32, 84 + i * 58 + 42, 'rule', '', { width: '496px', position: 'absolute' });
      return { r, at, i };
    });
    const bidRow = box(led, 32, 84 + 10 * 58 + 6, '', `<div style="display:flex;justify-content:space-between;width:496px"><span class="mono y" style="font-size:22px">bid = min(P*, ask)</span><span class="mono" style="font-size:16px;color:rgba(244,242,236,.6)">financing attached</span></div>`);

    const RX = 780, RW = 1000;
    // A: the loop
    const loop = box(root, RX, 300, '', '', { width: RW + 'px', height: '560px' });
    const lsv = svg(loop, RW, 560);
    const nP = box(loop, 170, 210, 'card solid', `<div style="width:220px;height:130px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px">${I('banknote', 34)}<span class="eyebrow">Price P</span></div>`);
    const nD = box(loop, 610, 210, 'card solid', `<div style="width:220px;height:130px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px">${I('landmark', 34)}<span class="eyebrow">Debt D(P)</span></div>`);
    const a1 = s('path', { d: 'M280,205 C330,90 670,90 720,205', fill: 'none', stroke: Y, 'stroke-width': 2, pathLength: 1 }, lsv);
    const a2 = s('path', { d: 'M720,345 C670,460 330,460 280,345', fill: 'none', stroke: Y, 'stroke-width': 2, pathLength: 1 }, lsv);
    const t1a = box(loop, 400, 70, 'mono', 'proceeds cap at LTV · P', { fontSize: '16px', color: 'rgba(244,242,236,.7)' });
    const t2a = box(loop, 395, 460, 'mono', 'return falls as P rises', { fontSize: '16px', color: 'rgba(244,242,236,.7)' });
    const lp = pulseDot(lsv, 6);

    // B: three tests
    const tests = [['by loan-to-value', '55% × P', 7.15, 'seven'], ['by debt service cover', 'NOI ÷ (1.30 × k)', 9.47, 'nine'], ['by debt yield', 'NOI ÷ 7.5%', 10.67, 'ten']];
    const formula = box(root, RX, 300, 'mono', 'D(P) = min( LTV·P ,&nbsp; NOI ÷ (DSCR·k) ,&nbsp; NOI ÷ DY )', { fontSize: '25px' });
    const SC = 72; // px per €M
    const TB = tests.map(([n, f, v, cue], i) => {
      const r = box(root, RX, 400 + i * 130, '', '', { width: RW + 'px', height: '110px' });
      box(r, 0, 0, '', `<span style="font-size:22px">${n}</span><span class="mono" style="font-size:16px;margin-left:16px;color:rgba(244,242,236,.5)">${f}</span>`);
      const bar = box(r, 0, 42, '', '', { height: '40px', width: v * SC + 'px', borderRadius: '4px', background: 'rgba(244,242,236,.4)', transformOrigin: '0 50%' });
      const num = box(r, v * SC + 20, 46, 'mono', `€${v.toFixed(2)}M`, { fontSize: '26px' });
      return { r, bar, num, cue, v };
    });
    const bindTag = box(root, RX + 7.15 * SC + 190, 446, 'chip y', 'binding', { fontSize: '15px' });

    // C: debt / equity split + r(P) schematic
    const split = box(root, RX, 300, '', '', { width: RW + 'px', height: '150px' });
    box(split, 0, 0, 'eyebrow', 'Price €13.0M');
    const dBar = box(split, 0, 40, '', '<span class="mono" style="position:absolute;left:18px;top:14px;font-size:19px;color:#F4F2EC">debt €7.15M</span>', { height: '54px', width: 7.15 * SC + 'px', background: 'rgba(244,242,236,.22)', borderRadius: '4px 0 0 4px' });
    const eBar = box(split, 7.15 * SC + 3, 40, '', '<span class="mono" style="position:absolute;left:18px;top:14px;font-size:19px;color:#111">equity €5.85M</span>', { height: '54px', width: 5.85 * SC - 3 + 'px', background: Y, borderRadius: '0 4px 4px 0', transformOrigin: '0 50%' });
    const cw = 1000, chh = 420;
    const rc = box(root, RX, 490, '', '', { width: cw + 'px', height: chh + 'px' });
    const rsv = svg(rc, cw, chh);
    const X = p => 80 + p * (cw - 120), Yr = r => chh - 60 - r * (chh - 100);
    s('line', { x1: 80, x2: cw - 40, y1: Yr(0), y2: Yr(0), stroke: 'rgba(244,242,236,.35)' }, rsv);
    s('line', { x1: 80, x2: 80, y1: Yr(0), y2: Yr(1), stroke: 'rgba(244,242,236,.35)' }, rsv);
    const lab = (x, y, txt, o = {}) => { const e = s('text', { x, y, fill: o.c || 'rgba(244,242,236,.6)', 'font-family': 'JBM', 'font-size': o.fs || 18, 'text-anchor': o.a || 'start' }, rsv); e.textContent = txt; return e; };
    lab(cw - 40, Yr(0) + 36, 'price P →', { a: 'end' }); lab(96, Yr(1) + 6, 'levered return r(P)');
    const rf = p => .9 - .75 * p - .08 * Math.max(0, p - .72) * 3;   // schematic: falls with P, kinks where DSCR binds
    let d = ''; for (let p = 0; p <= 1.0001; p += .02) d += (p ? 'L' : 'M') + X(p) + ',' + Yr(rf(p)) + ' ';
    const curve = s('path', { d, fill: 'none', stroke: '#F4F2EC', 'stroke-width': 3, pathLength: 1 }, rsv);
    let d2 = ''; for (let p = 0; p <= 1.0001; p += .02) d2 += (p ? 'L' : 'M') + X(p) + ',' + Yr(rf(p - .14) ) + ' ';
    const curve2 = s('path', { d: d2, fill: 'none', stroke: Y, 'stroke-width': 3, 'stroke-dasharray': '8 8' }, rsv);
    const tgtR = .42; const pStar = (.9 - tgtR) / .75;  // before the kink
    const tgt = s('line', { x1: 80, x2: cw - 40, y1: Yr(tgtR), y2: Yr(tgtR), stroke: Y, 'stroke-width': 1.5, 'stroke-dasharray': '6 6' }, rsv);
    const tgtL = lab(96, Yr(tgtR) - 14, '12% levered IRR target', { c: Y });
    const kink = lab(X(.72) + 14, Yr(rf(.72)) + 34, 'DSCR binds above ~€17.2M', { fs: 15 });
    const kinkDot = s('circle', { cx: X(.72), cy: Yr(rf(.72)), r: 5, fill: 'rgba(244,242,236,.7)' }, rsv);
    const probes = [.2, .9, .45, .7, .58, .64].map(p => s('circle', { cx: X(p), cy: Yr(rf(p)), r: 7, fill: 'none', stroke: 'rgba(244,242,236,.8)', 'stroke-width': 2 }, rsv));
    const star = s('g', {}, rsv);
    s('line', { x1: X(pStar), x2: X(pStar), y1: Yr(0), y2: Yr(tgtR), stroke: Y, 'stroke-width': 2 }, star);
    s('circle', { cx: X(pStar), cy: Yr(tgtR), r: 10, fill: Y }, star);
    const sl = s('text', { x: X(pStar), y: Yr(0) + 36, fill: Y, 'font-family': 'JBM', 'font-size': 22, 'text-anchor': 'middle' }, star); sl.textContent = 'P*';
    const bis = lab(X(pStar) - 20, Yr(tgtR) + 40, 'bisection: a few steps per quote', { fs: 15, a: 'end' });
    const ask = s('g', {}, rsv);
    s('line', { x1: X(pStar + .17), x2: X(pStar + .17), y1: Yr(0), y2: Yr(.95), stroke: 'rgba(244,242,236,.5)', 'stroke-width': 1.5, 'stroke-dasharray': '3 5' }, ask);
    const al = s('text', { x: X(pStar + .17), y: Yr(.95) - 10, fill: 'rgba(244,242,236,.7)', 'font-family': 'JBM', 'font-size': 18, 'text-anchor': 'middle' }, ask); al.textContent = 'ask';
    const star2 = s('circle', { cx: X(pStar + .1), cy: Yr(tgtR), r: 10, fill: 'none', stroke: Y, 'stroke-width': 2.5 }, rsv);
    const schem = box(rc, 96, chh - 20, 'tag', 'schematic');
    const moral = box(root, RX, 930, 'chip yo', `${I('trending-up', 18, Y)} A more generous credit box raises P*: debt competition shows up as equity price`, { fontSize: '16px' });

    function upd(t) {
      rise(hA, t, t0 + .2, { out: tB - .2 }); rise(hB, t, tB + .1, { out: tC - .2 }); rise(hC, t, W('17', 'engine') - .2);
      fade(ill, t, t0 + 1, .6);
      rise(led, t, W('15', 'test') - .3, { dx: -30, dy: 0 });
      LR.forEach(r => rise(r.r, t, r.at, { dx: -16, dy: 0 }));
      [...led.querySelectorAll('.rule')].forEach((ru, i) => ru.style.opacity = pr(t, LR[i].at, .5) * .9);
      LR[5].r.style.color = t > W('16', 'binds') ? Y : '';
      rise(bidRow, t, W('17', 'ask') - .1, { dy: 8 });
      // A
      fade(loop, t, t0 + .2, .5, tB - .3, .4);
      rise(nP, t, W('15', 'price') - .1, { scale: .1, dy: 0 }); rise(nD, t, W('15', 'debt') - .1, { scale: .1, dy: 0 });
      draw(a1, t, W('15', 'depends'), .8); draw(a2, t, W('15', 'debt', 1), .8);
      fade(t1a, t, W('15', 'depends') + .4, .5); fade(t2a, t, W('15', 'debt', 1) + .4, .5);
      const cyc = (t - (W('15', 'price', 1))) / 1.4;
      if (cyc > 0) { const k = cyc % 2; if (k < 1) lp.at(a1, eio(k)); else lp.at(a2, eio(k - 1)); } else lp.at(a1, 0);
      // B
      rise(formula, t, tB + .3, { out: tC - .3 });
      TB.forEach((b, i) => {
        rise(b.r, t, W('16', b.cue) - .4, { dy: 12, out: tC - .3 });
        b.bar.style.transform = `scaleX(${pr(t, W('16', b.cue) - .2, 1.0)})`;
        b.num.style.opacity = pr(t, W('16', b.cue) + .4, .4);
        const bd = pr(t, W('16', 'binds') - .6, .5);
        b.bar.style.background = i === 0 ? `rgba(${bd > 0 ? '255,190,6' : '244,242,236'},${lerp(.4, 1, bd)})` : `rgba(244,242,236,${lerp(.4, .18, bd)})`;
      });
      rise(bindTag, t, W('16', 'binds') - .2, { dx: -10, dy: 0, out: tC - .3 });
      // C
      rise(split, t, tC + .1, { dy: 16 });
      eBar.style.scale = `${pr(t, W('17', 'five') - .1, .9)} 1`;
      rise(rc, t, W('17', 'engine') - .3, { dy: 16 });
      draw(curve, t, W('17', 'solves') - .2, 1.0);
      fade(tgt, t, W('17', 'twelve') - .2, .4); fade(tgtL, t, W('17', 'twelve'), .4);
      fade(kink, t, W('17', 'solves') + .6, .5); fade(kinkDot, t, W('17', 'solves') + .6, .5);
      const bs = W('17', 'return') - .1;
      probes.forEach((p, i) => fade(p, t, bs + i * .16, .15, bs + i * .16 + .4, .25));
      fade(star, t, bs + 1.0, .4); fade(bis, t, bs + 1.1, .4);
      fade(ask, t, W('17', 'ask') - .1, .4);
      const gen = W('17', 'lower') + .35;
      fade(curve2, t, gen, .6); fade(star2, t, gen + .3, .4);
      rise(moral, t, gen, { dy: 12 });
    }
  }
}
