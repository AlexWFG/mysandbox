// 04 The bond (worked example, both outcomes) · 05 What can be slashed
function build2() {
  // ---------------------------------------------------------------- 04 · the bond
  const X = v => 260 + (v - 700) * 10, AY = 470;           // NOI axis €700k..€840k
  const NS = [360, 880], NE = [960, 880], NB = [1560, 880]; // seller, escrow, buyer
  const M = 12;
  scene(T('n12') - .5, END('n17') + 1.6, `
    <div data-k="h" class="abs h1" style="left:160px;top:140px">A bond is a holdback with<br><span class="y">rules</span> instead of lawyers</div>
    <div data-k="st" class="abs" style="left:160px;top:430px;width:1600px;height:200px;transform-origin:0 0">
      <div data-k="s0" class="abs" style="left:0;top:0"><div class="lbl">Asset price</div><div class="big" style="font-size:120px;margin-top:14px" data-k="v0">€13.0M</div></div>
      <div data-k="s1" class="abs" style="left:560px;top:0"><div class="lbl">Attested NOI</div><div class="big" style="font-size:120px;margin-top:14px" data-k="v1">€800k</div></div>
      <div data-k="s2" class="abs" style="left:1120px;top:0"><div class="lbl">Cap rate</div><div class="big" style="font-size:120px;margin-top:14px" data-k="v2">6.15%</div></div>
    </div>
    <div data-k="ill" class="abs chip dash" style="left:1560px;top:150px">Illustrative</div>
    <svg class="full">
      <rect data-k="tz" x="${X(760)}" y="330" width="${X(840) - X(760)}" height="${AY - 330}" fill="rgba(255,190,6,.07)" stroke="${Y}" stroke-width="1.5" stroke-dasharray="6 6"/>
      <rect data-k="bz" x="${X(720)}" y="330" width="${X(760) - X(720)}" height="${AY - 330}" fill="rgba(244,242,236,.10)" stroke="${INK}" stroke-width="1.5"/>
      <line data-k="axis" x1="${X(700)}" x2="${X(840)}" y1="${AY}" y2="${AY}" stroke="${DIM}" stroke-width="1.5" pathLength="1"/>
      ${[700, 720, 740, 760, 780, 800, 820, 840].map(v => `<g data-k="tk${v}"><line x1="${X(v)}" x2="${X(v)}" y1="${AY}" y2="${AY + 10}" stroke="${DIM}" stroke-width="1.5"/><text x="${X(v)}" y="${AY + 36}" fill="${FAINT}" font-family="Mono" font-size="15" text-anchor="middle">€${v}k</text></g>`).join('')}
      <line data-k="ma" x1="${X(800)}" x2="${X(800)}" y1="${AY}" y2="330" stroke="${Y}" stroke-width="4"/>
      <g data-k="mr"><line data-k="mrl" x1="0" x2="0" y1="${AY}" y2="352" stroke="${INK}" stroke-width="3"/><path d="M-11 338 L11 338 L0 356 Z" fill="${INK}"/></g>
      <path data-k="miss" pathLength="1" d="M${X(800)} 520 V540 H${X(720)} V520" fill="none" stroke="${INK}" stroke-width="2"/>
      <!-- flows -->
      <path data-k="pSE" d="M${NS[0] + 66} ${NS[1] - 14} C 600 780, 760 780, ${NE[0] - 66} ${NE[1] - 14}" fill="none" stroke="${LINE}" stroke-width="1.5"/>
      <path data-k="pES" d="M${NE[0] - 66} ${NE[1] + 14} C 760 980, 600 980, ${NS[0] + 66} ${NS[1] + 14}" fill="none" stroke="${LINE}" stroke-width="1.5"/>
      <path data-k="pEB" d="M${NE[0] + 66} ${NE[1] - 14} C 1160 780, 1320 780, ${NB[0] - 66} ${NB[1] - 14}" fill="none" stroke="${LINE}" stroke-width="1.5"/>
      <g data-k="fSE">${flowDots(8, 6)}</g><g data-k="fES">${flowDots(8, 6)}</g><g data-k="fEB">${flowDots(8, 6)}</g>
      <circle data-k="gbg" cx="${NE[0]}" cy="${NE[1]}" r="76" fill="none" stroke="${LINE}" stroke-width="6"/>
      <circle data-k="gauge" cx="${NE[0]}" cy="${NE[1]}" r="76" fill="none" stroke="${Y}" stroke-width="6" pathLength="1" transform="rotate(-90 ${NE[0]} ${NE[1]})"/>
      <g data-k="mo">${Array.from({ length: M }, (_, i) => `<rect data-k="mo${i}" x="${560 + i * 68}" y="588" width="56" height="56" rx="8" fill="none" stroke="${LINE}" stroke-width="1.5"/>`).join('')}
        ${sicon('landmark', 500, 616, 36, DIM)}</g>
    </svg>
    <div data-k="la" class="abs" style="left:${X(800) + 18}px;top:324px"><div class="lbl y">Attested</div><div class="big" style="font-size:34px;margin-top:6px">€800k</div></div>
    <div data-k="tl" class="abs lbl y" style="left:${X(760) + 14}px;top:342px">Tolerance ±5% · €40k</div>
    <div data-k="w12" class="abs chip yo" style="left:${X(840) + 24}px;top:${AY - 20}px">${icon('clock', 15)} 12 months</div>
    <div data-k="ml" class="abs lbl" style="left:${X(760)}px;top:556px;transform:translateX(-50%);color:${INK}">10% miss = €80k of NOI</div>
    <div data-k="eq" class="abs" style="left:560px;top:606px;white-space:nowrap">
      <span data-k="e1" class="big" style="font-size:60px">€80k</span><span data-k="e2" class="big" style="font-size:60px;color:${DIM}"> ÷ 6.15%</span><span data-k="e3" class="big y" style="font-size:60px"> = €1.3M</span>
      <span data-k="e4" class="chip" style="margin-left:24px;vertical-align:14px">≈ 10% of price</span></div>
    <div data-k="mlb" class="abs lbl" style="left:560px;top:556px">Trigger · bank receipts vs attested NOI</div>
    <div data-k="rl" class="abs" style="left:0;top:270px;white-space:nowrap"><span class="lbl" style="color:${INK}">Realised </span><span data-k="rv" class="big" style="font-size:34px">€800k</span></div>
    <div data-k="oc1" class="abs" style="left:160px;top:590px"><div class="lbl y">Outcome 1</div><div class="h3" style="margin-top:6px">−5% · inside tolerance</div></div>
    <div data-k="oc2" class="abs" style="left:160px;top:590px"><div class="lbl y">Outcome 2</div><div class="h3" style="margin-top:6px">−10% · 5 pts beyond</div></div>
    <div data-k="bl" class="abs lbl" style="left:${(X(720) + X(760)) / 2}px;top:300px;transform:translateX(-50%);color:${INK}">Beyond tolerance</div>
    <div data-k="pr" class="abs" style="left:960px;top:596px;transform:translateX(-50%);text-align:center;white-space:nowrap">
      <div class="h2">Pro rata, <span class="y">never all or nothing</span></div>
      <div class="lbl" style="margin-top:14px">5 pts beyond tolerance, bond sized for 10 · half the bond</div></div>
    <div data-k="dsp" class="abs lbl" style="left:960px;top:716px;transform:translateX(-50%)">Disputes · automatic inside the band · expert determination outside it, 30 days, cost to the loser</div>
    <div data-k="nS" class="node" style="left:${NS[0]}px;top:${NS[1]}px">${icon('user', 44)}</div>
    <div data-k="nE" class="node" style="left:${NE[0]}px;top:${NE[1]}px;background:transparent;border-color:transparent">${icon('landmark', 46)}</div>
    <div data-k="nB" class="node" style="left:${NB[0]}px;top:${NB[1]}px">${icon('briefcase', 44)}</div>
    <div data-k="tS" class="nodelbl lbl" style="left:${NS[0]}px;top:${NS[1] + 76}px;color:${INK}">Seller</div>
    <div data-k="tE" class="nodelbl" style="left:${NE[0]}px;top:${NE[1] + 90}px"><div class="lbl" style="color:${INK}">Escrow <span data-k="ev" class="y">€0.0M</span></div><div class="lbl" style="margin-top:6px;font-size:12px">Yield-bearing · regulated bank</div></div>
    <div data-k="tB" class="nodelbl lbl" style="left:${NB[0]}px;top:${NB[1] + 76}px;color:${INK}">Buyer</div>
    <div data-k="cS1" class="abs chip y" style="left:${NS[0]}px;top:${NS[1] - 118}px;transform:translateX(-50%)">Released in full + yield</div>
    <div data-k="cS2" class="abs chip yo" style="left:${NS[0]}px;top:${NS[1] - 118}px;transform:translateX(-50%)">½ back · €650k</div>
    <div data-k="cB2" class="abs chip y" style="left:${NB[0]}px;top:${NB[1] - 118}px;transform:translateX(-50%)">½ bond to buyer · €650k</div>
    <div data-k="ft" class="foot">Sizes and terms are illustrative; the shape is the point</div>`,
    (t, k) => {
      const t0 = T('n12') - .3;
      const t13 = T('n13'), t14 = T('n14'), t15 = T('n15'), t16 = T('n16'), t17 = T('n17');
      show(k.h, t, t0, t13 - .4, { d: 1 }); show(k.ft, t, t0 + 1, 1e9, { dy: 0 });
      const ta = at('n12', 'thirteen'), tb = at('n12', 'eight hundred'), tc = at('n12', 'six point');
      show(k.s0, t, ta, 1e9, { dy: 30 }); show(k.s1, t, tb, 1e9, { dy: 30 }); show(k.s2, t, tc, 1e9, { dy: 30 });
      num(k.v0, 13 * P(t, ta, 1.1, E.o3), v => '€' + v.toFixed(1) + 'M');
      num(k.v1, 800 * P(t, tb, 1.1, E.o3), v => '€' + Math.round(v) + 'k');
      num(k.v2, 6.15 * P(t, tc, 1.1, E.o3), v => v.toFixed(2) + '%');
      show(k.ill, t, ta, 1e9, { dy: 0 });
      // stats shrink to a strip when the warranty starts
      const m = P(t, t13 - .5, 1.0, E.io3);
      k.st.style.transform = `translate(0px,${-285 * m}px) scale(${1 - .4 * m})`;
      // axis + tolerance
      draw(k.axis, P(t, t13 - .1, 1));
      [700, 720, 740, 760, 780, 800, 820, 840].forEach((v, i) => fade(k['tk' + v], P(t, t13 + i * .05, .4)));
      const pa = P(t, t13 + .2, .8, E.o5); k.ma.setAttribute('y2', lerp(AY, 330, pa)); k.ma.style.opacity = pa > 0 ? 1 : 0;
      show(k.la, t, t13 + .4, 1e9, { dy: 0, dx: -10 });
      const tt = at('n13', 'five percent');
      k.tz.style.opacity = P(t, tt, .6); show(k.tl, t, tt + .1, 1e9, { dy: 0 });
      show(k.w12, t, at('n13', 'twelve months'), 1e9, { dy: 0, dx: -10 });
      // sizing
      const tm = at('n14', 'ten percent'), te1 = at('n14', 'eighty'), te2 = at('n14', 'over the cap'), te3 = at('n14', 'One point');
      draw(k.miss, P(t, tm, .7) * (1 - P(t, t15 - .4, .3))); show(k.ml, t, tm + .3, t15 - .4, { dy: 0 });
      show(k.e1, t, te1, t15 - .4, { dy: 14 }); show(k.e2, t, te2, t15 - .4, { dy: 14 }); show(k.e3, t, te3, t15 - .4, { dy: 14 }); show(k.e4, t, te3 + .6, t15 - .4, { dy: 0 });
      k.eq.style.visibility = 'visible';
      // nodes
      show(k.nS, t, at('n13', 'seller'), 1e9, { dy: 16 }); show(k.tS, t, at('n13', 'seller') + .1, 1e9, { dy: 0 });
      show(k.nB, t, at('n14', "buyer"), 1e9, { dy: 16 }); show(k.tB, t, at('n14', 'buyer') + .1, 1e9, { dy: 0 });
      const th = at('n14', 'held in');
      show(k.nE, t, te3 - .2, 1e9, { dy: 16 }); show(k.tE, t, te3, 1e9, { dy: 0 });
      k.gbg.style.opacity = P(t, te3 - .2, .6);
      [k.pSE, k.pES, k.pEB].forEach(p => { p.style.opacity = P(t, te3 - .2, .6); });
      // escrow level over time
      const trel = at('n16', 'released'), tre2 = t17 - .5, th2 = at('n17', 'Half');
      let g;
      if (t < trel) g = P(t, te3, 1.8, E.io2);
      else if (t < tre2) g = 1 - P(t, trel, 1.5, E.io2);
      else if (t < th2) g = P(t, tre2, .7, E.io2);
      else g = 1 - P(t, th2, 1.6, E.io2);
      draw(k.gauge, g); k.gauge.style.opacity = g > .002 ? 1 : 0;
      k.ev.textContent = '€' + (1.3 * g).toFixed(1) + 'M';
      flow(k.fSE, k.pSE, t, te3, te3 + 1.2, { rate: 4, dur: 1 });
      flow(k.fES, k.pES, t, trel, trel + 1.1, { rate: 4, dur: 1 });
      if (t > th2 - .5) flow(k.fES, k.pES, t, th2, th2 + 1.1, { rate: 4, dur: 1 });
      flow(k.fEB, k.pEB, t, th2, th2 + 1.1, { rate: 4, dur: 1 });
      // twelve months of receipts
      show(k.mlb, t, t15 - .2, t16 - .2, { dy: 0 });
      k.mo.style.opacity = P(t, t15 - .3, .5) * (1 - P(t, t16 - .2, .4));
      for (let i = 0; i < M; i++) { const f = P(t, t15 + i * .17, .25); k['mo' + i].setAttribute('fill', `rgba(255,190,6,${.85 * f})`); k['mo' + i].setAttribute('stroke', f > .5 ? Y : LINE); }
      // realised marker
      const t760 = at('n16', 'seven sixty'), t720 = at('n17', 'seven twenty');
      const r = 800 - 40 * P(t, t760, 1.2, E.io3) - 40 * P(t, t720, 1.2, E.io3);
      const vr = P(t, t15 + .4, .6);
      k.mr.setAttribute('transform', `translate(${X(r)},0)`); k.mr.style.opacity = vr;
      k.rl.style.left = (X(r) - 70) + 'px'; fade(k.rl, vr); num(k.rv, r, v => '€' + Math.round(v) + 'k');
      show(k.oc1, t, at('n16', 'five percent'), t17 - .4, { dy: 0, dx: -12 });
      show(k.oc2, t, at('n17', 'five points'), 1e9, { dy: 0, dx: -12 });
      k.bz.style.opacity = P(t, at('n17', 'beyond'), .6); show(k.bl, t, at('n17', 'beyond') + .2, 1e9, { dy: 0 });
      show(k.cS1, t, trel + .8, tre2, { dy: 10 });
      show(k.cB2, t, th2 + .9, 1e9, { dy: 10 }); show(k.cS2, t, th2 + 1.1, 1e9, { dy: 10 });
      show(k.pr, t, at('n17', 'Pro rata'), 1e9, { dy: 16 });
      show(k.dsp, t, END('n17') + .1, 1e9, { dy: 0 });
      const nb = P(t, th2 + .6, .4); k.nB.classList.toggle('hi', nb > .5 && nb < 1 && t < th2 + 2.4 || (t > th2 + .6));
    });

  // ---------------------------------------------------------------- 05 · what can be slashed
  const COLS = [
    { x: 160, ic: 'check', h: 'Objective', s: 'Bondable', rows: ['Attested rent → bank receipts', 'Vacancy → lease register', 'In-place debt → loan register', 'Title → the registry', 'Closing funds → the closing set'], note: '' },
    { x: 700, ic: 'gavel', h: 'Adjudicated', s: 'Bondable with a referee', rows: ['Capex backlog → inspection', 'Building condition and defects', 'Environmental findings', 'Lease interpretation, side letters'], note: 'Referee named in advance, time-boxed, paid by the losing side' },
    { x: 1240, ic: 'x', h: 'Subjective', s: 'Never bond', rows: ['Valuation marks', 'Location and building class', 'Tenant credit opinion', 'Market outlook, ERV growth', 'ESG ratings'], note: 'Assured by a signature and a licence, not capital' }];
  scene(T('n18a') - .5, END('n18d') + 1.2, `
    <div data-k="h" class="abs h2" style="left:160px;top:140px">Slashing needs a <span class="y">later truth</span> a contract can read</div>
    <svg class="full"><g data-k="mech">
      <path data-k="tl" pathLength="1" d="M620 600 H1300" fill="none" stroke="${DIM}" stroke-width="2"/>
      <path d="M1290 592 L1302 600 L1290 608" fill="none" stroke="${DIM}" stroke-width="2" data-k="arr"/>
      <path data-k="la" d="M600 540 C 700 430, 820 400, 900 400" fill="none" stroke="${Y}" stroke-width="2" stroke-dasharray="6 7"/>
      <path data-k="lb" d="M1360 540 C 1260 430, 1100 400, 1020 400" fill="none" stroke="${Y}" stroke-width="2" stroke-dasharray="6 7"/>
      <g data-k="fa">${flowDots(3, 5)}</g><g data-k="fb">${flowDots(3, 5)}</g>
    </g></svg>
    <div data-k="n1" class="node" style="left:560px;top:600px">${icon('file-signature', 44)}</div>
    <div data-k="n2" class="node hi" style="left:1360px;top:600px">${icon('receipt', 44)}</div>
    <div data-k="n3" class="node" style="left:960px;top:400px;width:110px;height:110px;margin:-55px 0 0 -55px">${icon('file-check-2', 40)}</div>
    <div data-k="t1" class="nodelbl lbl" style="left:560px;top:680px;color:${INK}">The claim</div>
    <div data-k="t2" class="nodelbl lbl y" style="left:1360px;top:680px">Later mechanical truth</div>
    <div data-k="t3" class="nodelbl lbl" style="left:960px;top:300px;color:${INK}">Contract reads both</div>
    <div data-k="t4" class="nodelbl lbl" style="left:960px;top:620px">Time</div>
    ${COLS.map((c, j) => `<div data-k="col${j}" class="card ${j === 0 ? 'hi' : ''}" style="left:${c.x}px;top:290px;width:510px;height:640px;${j === 2 ? 'background:transparent;border-style:dashed' : ''}">
      <div class="abs lbl ${j < 2 ? 'y' : ''}" style="left:32px;top:32px">${c.s}</div>
      <div class="abs h2" style="left:30px;top:62px;${j === 2 ? `color:${DIM}` : ''}">${c.h}</div>
      ${c.rows.map((r, i) => `<div data-k="r${j}_${i}" class="abs" style="left:32px;top:${160 + i * 64}px;width:450px;height:40px">
        <div class="abs" style="left:0;top:4px;color:${j === 0 ? Y : j === 1 ? INK : DIM}">${icon(c.ic, 24)}</div>
        <div class="abs" style="left:42px;top:2px;font-size:22px;${j === 2 ? `color:${DIM}` : ''};white-space:nowrap">${r}</div>
        ${j === 2 ? `<div data-k="x${i}" class="abs" style="left:40px;top:17px;height:2px;width:${r.length * 11}px;background:${DIM};transform-origin:0 50%"></div>` : ''}</div>`).join('')}
      ${c.note ? `<div data-k="nt${j}" class="abs body" style="left:32px;top:500px;width:440px;font-size:20px">${c.note}</div>` : ''}</div>`).join('')}
    <div data-k="ft" class="foot">The lesson from staking: slashing works on facts the chain can see; slashing by governance vote has failed where tried</div>`,
    (t, k) => {
      const t0 = T('n18a') - .3, tb = T('n18b'), tc = T('n18c'), td = T('n18d');
      show(k.h, t, t0);
      const out = tb - .4;
      const pm = P(t, t0 + .3, .8);
      show(k.n1, t, t0 + .2, out); show(k.t1, t, t0 + .3, out, { dy: 0 });
      show(k.n2, t, at('n18a', 'later truth'), out); show(k.t2, t, at('n18a', 'later truth') + .1, out, { dy: 0 });
      draw(k.tl, pm); k.arr.style.opacity = pm; show(k.t4, t, t0 + .6, out, { dy: 0 });
      const tr = at('n18a', 'contract');
      show(k.n3, t, tr, out); show(k.t3, t, tr + .1, out, { dy: 0 });
      k.la.style.opacity = k.lb.style.opacity = P(t, tr, .5) * (1 - P(t, out, .4));
      k.mech.style.opacity = 1 - P(t, out, .4);
      flow(k.fa, k.la, t, tr + .2, out, { rate: 1.5, dur: 1 }); flow(k.fb, k.lb, t, tr + .2, out, { rate: 1.5, dur: 1 });
      // columns
      show(k.col0, t, tb - .1, 1e9, { dy: 30 }); show(k.col1, t, tc - .1, 1e9, { dy: 30 }); show(k.col2, t, td - .1, 1e9, { dy: 30 });
      const obj = [at('n18b', 'Rent'), at('n18b', 'Rent') + .5, at('n18b', 'Rent') + 1, at('n18b', 'Title'), at('n18b', 'Title') + .5];
      obj.forEach((tt, i) => show(k['r0_' + i], t, tt, 1e9, { dy: 0, dx: -12 }));
      COLS[1].rows.forEach((_, i) => show(k['r1_' + i], t, tc + .1 + i * .3, 1e9, { dy: 0, dx: -12 }));
      show(k.nt1, t, at('n18c', 'referee'), 1e9, { dy: 10 });
      COLS[2].rows.forEach((_, i) => { show(k['r2_' + i], t, td + i * .12, 1e9, { dy: 0, dx: -12 }); k['x' + i].style.transform = `scaleX(${P(t, at('n18d', 'never') + i * .08, .5)})`; });
      show(k.nt2, t, END('n18d') + .1, 1e9, { dy: 10 });
      show(k.ft, t, tb + .5, 1e9, { dy: 0 });
      // earlier columns step back as the next one arrives
      if (t > tc) k.col0.style.opacity = parseFloat(k.col0.style.opacity) * (1 - .35 * P(t, tc, .6));
    });
}
