// 06 Who posts capital · 07 The insurer · 08 The plan · end card
function build3() {
  // ---------------------------------------------------------------- 06 · who posts (stock)
  const tU = at('n20', 'Usually');
  stock('meeting', T('n20') - .7, tU + .5, { bright: .55 });
  scene(T('n20') - .5, tU + .4, `
    <div data-k="h" class="abs h1" style="left:160px;top:780px">Who posts the <span class="y">capital</span>?</div>`,
    (t, k) => { show(k.h, t, T('n20') - .1, 1e9, { d: 1 }); });

  // ---------------------------------------------------------------- 06 · replaces what a sale already carries
  const CH = ['Holdback', 'Retention', 'W&I premium'];
  scene(tU - .1, T('n21') + .1, `
    <div data-k="h" class="abs h2" style="left:160px;top:140px">Net new capital is usually <span class="y">small</span></div>
    <div data-k="l" class="abs lbl" style="left:960px;top:400px;transform:translateX(-50%)">What an institutional sale already carries</div>
    ${CH.map((c, i) => `<div data-k="c${i}" class="abs" style="left:${560 + i * 400}px;top:540px"><div class="chip" style="font-size:22px;padding:18px 34px 16px;color:${INK};transform:translate(-50%,-50%);position:absolute">${c}</div></div>`).join('')}
    <div data-k="b" class="abs" style="left:960px;top:540px"><div class="chip y" style="font-size:30px;padding:22px 52px 20px;transform:translate(-50%,-50%);position:absolute">${icon('lock', 26, '#0B0B0C')} Bond</div></div>
    <div data-k="cap" class="abs sub" style="left:960px;top:640px;transform:translateX(-50%);white-space:nowrap">The bond replaces them, sized the same way</div>
    <div data-k="ft" class="foot">Where a deal carried none, the seller posts capital it would otherwise have conceded in price</div>`,
    (t, k) => {
      show(k.h, t, tU); show(k.l, t, tU + .3, 1e9, { dy: 0 });
      const tr = at('n20', 'replaces'), pm = P(t, tr + .2, 1.0, E.io3);
      CH.forEach((_, i) => {
        const v = show(k['c' + i], t, at('n20', i === 0 ? 'holdback' : 'W and I') + (i === 1 ? -.35 : 0), 1e9, { dy: 16 });
        k['c' + i].style.left = lerp(560 + i * 400, 960, pm) + 'px';
        k['c' + i].style.opacity = v * (1 - P(t, tr + .9, .4));
      });
      const pb = P(t, tr + 1.0, .7, E.o5); fade(k.b, pb); k.b.style.transform = `scale(${lerp(.6, 1, pb)})`;
      show(k.cap, t, tr + 1.3); show(k.ft, t, tr + 1.3, 1e9, { dy: 0 });
    });

  // ---------------------------------------------------------------- 06 · three ways to post
  const R = [{ x: 160, n: '1', h: 'Self-bond', c: 'Seller posts its own escrow. The yield stays with the seller; it costs liquidity.' },
    { x: 700, n: '2', h: 'Surety', c: 'A third party posts for a fee, priced by the seller’s record.' },
    { x: 1240, n: '3', h: 'Policy', c: 'No escrow. An insurer carries the risk against a premium and pays on the same trigger.' }];
  const cx = i => R[i].x + 260, DY = 540;
  scene(T('n21') - .4, T('n22') + .2, `
    <div data-k="h" class="abs h2" style="left:160px;top:140px">Three ways to post</div>
    ${R.map((r, i) => `<div data-k="k${i}" class="card ${i === 1 ? 'hi' : ''}" style="left:${r.x}px;top:280px;width:520px;height:640px">
      <div class="abs lbl y" style="left:32px;top:32px">${r.n}</div><div class="abs h2" style="left:30px;top:60px">${r.h}</div>
      <div class="abs body" style="left:32px;top:480px;width:450px;font-size:21px">${r.c}</div></div>`).join('')}
    <svg class="full">
      <path data-k="p0" d="M${cx(0) - 80} ${DY} H${cx(0) + 80}" stroke="${LINE}" stroke-width="1.5" fill="none"/><g data-k="f0">${flowDots(5, 6)}</g>
      <path data-k="p1a" d="M${cx(1)} ${DY - 30} L${cx(1) + 110} ${DY + 50}" stroke="${LINE}" stroke-width="1.5" fill="none"/><g data-k="f1a">${flowDots(5, 6)}</g>
      <path data-k="p1b" d="M${cx(1) - 110} ${DY + 50} L${cx(1)} ${DY - 30}" stroke="${LINE}" stroke-width="1.5" fill="none" stroke-dasharray="5 6"/><g data-k="f1b">${flowDots(4, 4, INK)}</g>
      <path data-k="p2" d="M${cx(2) + 80} ${DY} H${cx(2) - 80}" stroke="${Y}" stroke-width="2" fill="none" stroke-dasharray="5 6"/>
    </svg>
    ${[[0, -130, 0, 'user', 'Seller'], [0, 130, 0, 'landmark', 'Escrow'], [1, 0, -80, 'shield-check', 'Surety'], [1, -130, 80, 'user', 'Seller'], [1, 130, 80, 'landmark', 'Escrow'], [2, 130, 0, 'umbrella', 'Insurer'], [2, -130, 0, 'briefcase', 'Buyer']]
      .map(([c, dx, dy, ic, lb], j) => `<div data-k="n${j}" class="node" style="left:${cx(c) + dx}px;top:${DY + dy}px;width:84px;height:84px;margin:-42px 0 0 -42px">${icon(ic, 32)}</div>
      <div data-k="nl${j}" class="nodelbl lbl" style="left:${cx(c) + dx}px;top:${DY + dy + (dy < 0 ? -76 : 52)}px;font-size:12px">${lb}</div>`).join('')}
    <div data-k="fee" class="abs lbl" style="left:${cx(1) - 150}px;top:${DY - 44}px;transform:translateX(-50%);color:${INK}">Fee [x]%</div>
    <div data-k="pol" class="abs lbl y" style="left:${cx(2)}px;top:${DY - 40}px;transform:translateX(-50%)">Policy</div>
    <div data-k="ft" class="foot">Surety fee left as a placeholder; it is what the surety market will price</div>`,
    (t, k) => {
      show(k.h, t, T('n21') - .2);
      const ts = [at('n21', 'self-bond') - .3, at('n21', 'surety'), at('n21', 'policy')];
      ts.forEach((tt, i) => show(k['k' + i], t, tt, 1e9, { dy: 30 }));
      [[0, 0], [1, 0], [2, 1], [3, 1], [4, 1], [5, 2], [6, 2]].forEach(([j, c]) => { show(k['n' + j], t, ts[c] + .3, 1e9, { dy: 10 }); show(k['nl' + j], t, ts[c] + .4, 1e9, { dy: 0 }); });
      k.p0.style.opacity = P(t, ts[0] + .4, .4); flow(k.f0, k.p0, t, ts[0] + .5, 1e9, { rate: 2, dur: 1 });
      k.p1a.style.opacity = k.p1b.style.opacity = P(t, ts[1] + .4, .4);
      flow(k.f1a, k.p1a, t, ts[1] + .6, 1e9, { rate: 2, dur: 1 }); flow(k.f1b, k.p1b, t, ts[1] + .5, 1e9, { rate: 1.2, dur: 1 });
      show(k.fee, t, ts[1] + .7, 1e9, { dy: 0 });
      k.p2.style.opacity = P(t, ts[2] + .4, .4); show(k.pol, t, ts[2] + .6, 1e9, { dy: 0 });
      show(k.ft, t, ts[1] + .8, 1e9, { dy: 0 });
    });

  // ---------------------------------------------------------------- 06 · surety book
  const Q = [['Surety S1', .78], ['Surety S2', .52], ['Surety S3', .9], ['Surety S4', .64]];
  const CX0 = 1250, CX1 = 1720, CY0 = 380, CY1 = 780;
  scene(T('n22') - .4, END('n22') + .7, `
    <div data-k="h" class="abs h2" style="left:160px;top:140px">The market is the <span class="y">surety book</span></div>
    <div data-k="bk" class="card" style="left:160px;top:290px;width:920px;height:600px">
      <div class="abs lbl" style="left:36px;top:34px">Same bond · same attested record</div>
      <div class="abs h3" style="left:34px;top:66px">NOI at A3 · €1.3M · 12 months</div>
      ${Q.map((q, i) => `<div data-k="q${i}" class="abs" style="left:36px;top:${170 + i * 96}px;width:850px;height:76px;border-radius:10px">
        <div class="abs" style="left:18px;top:22px;color:${DIM}">${icon('shield-check', 30)}</div>
        <div class="abs h3" style="left:66px;top:20px;font-size:25px">${q[0]}</div>
        <div data-k="qb${i}" class="abs" style="left:290px;top:31px;height:14px;width:${q[1] * 400}px;border-radius:7px;background:rgba(244,242,236,.35);transform-origin:0 50%"></div>
        <div class="abs lbl" style="left:720px;top:28px">Fee [x]%</div></div>`).join('')}
    </div>
    <div data-k="tk" class="abs chip y" style="left:880px;top:${290 + 170 + 96 + 20}px">Seller takes it</div>
    <svg class="full"><g data-k="ch">
      <line x1="${CX0}" x2="${CX0}" y1="${CY0}" y2="${CY1}" stroke="${DIM}" stroke-width="1.5"/>
      <line x1="${CX0}" x2="${CX1}" y1="${CY1}" y2="${CY1}" stroke="${DIM}" stroke-width="1.5"/>
      <path data-k="cv" pathLength="1" d="M${CX0 + 20} ${CY0 + 30} C ${CX0 + 150} ${CY0 + 240}, ${CX0 + 280} ${CY1 - 90}, ${CX1 - 10} ${CY1 - 60}" fill="none" stroke="${Y}" stroke-width="4" stroke-linecap="round"/>
    </g></svg>
    <div data-k="cl" class="abs">
      <div class="abs lbl" style="left:${CX0 - 10}px;top:${CY0 - 40}px">Fee</div>
      <div class="abs lbl" style="left:${CX1}px;top:${CY1 + 20}px;transform:translateX(-100%);white-space:nowrap">Level + track record →</div>
      <div class="abs body" style="left:${CX0}px;top:${CY1 + 70}px;width:480px;font-size:20px">Fees fall with assurance level and history</div></div>`,
    (t, k) => {
      const t0 = T('n22') - .3;
      show(k.h, t, t0); show(k.bk, t, t0 + .2, 1e9, { dy: 30 });
      Q.forEach((_, i) => show(k['q' + i], t, at('n22', 'sureties') + i * .15, 1e9, { dy: 0, dx: -12 }));
      const tb = at('n22', 'same attested') + .3, hb = P(t, tb, .5);
      k.q1.style.background = `rgba(255,190,6,${.1 * hb})`; k.qb1.style.background = hb > .5 ? Y : 'rgba(244,242,236,.35)';
      show(k.tk, t, tb + .2, 1e9, { dy: 0, dx: -10 });
      const tf = at('n22', 'fees that fall');
      k.ch.style.opacity = P(t, tf - .6, .5); show(k.cl, t, tf - .4, 1e9, { dy: 0 });
      draw(k.cv, P(t, tf, 1.6, E.io2));
      const sh = P(t, tf + .3, 1.6, E.io2);
      Q.forEach((_, i) => { k['qb' + i].style.transform = `scaleX(${1 - .35 * sh})`; });
    });

  // ---------------------------------------------------------------- 06 · the test it has to pass
  const PX = 960, PY = 500, BL = 440;
  scene(T('n23') - .4, END('n23') + .9, `
    <div data-k="h" class="abs h2" style="left:160px;top:140px">The test it has to pass</div>
    <svg class="full">
      <path data-k="st" pathLength="1" d="M${PX} ${PY} L${PX - 50} ${PY + 330} H${PX + 50} Z" fill="none" stroke="${DIM}" stroke-width="2"/>
      <g data-k="beam"><line x1="${PX - BL}" x2="${PX + BL}" y1="${PY}" y2="${PY}" stroke="${INK}" stroke-width="3"/></g>
      <circle cx="${PX}" cy="${PY}" r="9" fill="${Y}"/>
    </svg>
    <div data-k="L" class="abs" style="left:0;top:0;width:420px"><div style="position:absolute;left:-210px;width:420px;text-align:center">
      <div class="lbl y">Certainty premium</div>
      <div style="margin-top:14px;display:flex;flex-wrap:wrap;gap:10px;justify-content:center">
        ${['Higher rank', 'Firm debt', 'Speed', 'Fewer retrades'].map(s => `<span class="chip yo">${s}</span>`).join('')}</div></div></div>
    <div data-k="Rr" class="abs" style="left:0;top:0;width:420px"><div style="position:absolute;left:-210px;width:420px;text-align:center">
      <div class="lbl" style="color:${INK}">Cost</div>
      <div style="margin-top:14px;display:flex;gap:10px;justify-content:center"><span class="chip">Liquidity or fee</span></div></div></div>
    <div data-k="m" class="abs" style="left:960px;top:860px;transform:translateX(-50%);text-align:center;white-space:nowrap">
      <div class="h3">Measured, <span class="y">not assumed</span></div>
      <div class="body" style="margin-top:8px;font-size:20px">If the market doesn’t pay for certainty, nobody bonds and the mechanism idles</div></div>
    <div data-k="ft" class="foot">Open risk · adverse selection: the surety fee has to reflect record, not just level</div>`,
    (t, k) => {
      const t0 = T('n23') - .3;
      show(k.h, t, t0); draw(k.st, P(t, t0 + .1, .8));
      const tw = at('n23', 'worth more'), a = -7 * P(t, tw, 1.4, E.io3) + 2 * (1 - P(t, t0 + .3, .8));
      k.beam.setAttribute('transform', `rotate(${a} ${PX} ${PY})`); k.beam.style.opacity = P(t, t0 + .3, .5);
      const r = a * Math.PI / 180;
      const lx = PX - BL * Math.cos(r), ly = PY - BL * Math.sin(r), rx = PX + BL * Math.cos(r), ry = PY + BL * Math.sin(r);
      place(k.L, lx, ly + 26); place(k.Rr, rx, ry + 26);
      show(k.L, t, at('n23', 'certainty'), 1e9, { dy: 14 }); show(k.Rr, t, at('n23', 'cost'), 1e9, { dy: 14 });
      show(k.m, t, at('n23', 'measured'), 1e9); show(k.ft, t, t0 + 1.2, 1e9, { dy: 0 });
    });

  // ---------------------------------------------------------------- 07 · three paths to being an insurer
  const IP = [{ l: 'A', h: 'Data partner', w: 'Evidence pack and levels supplied to W&I and title insurers', cap: 0, capl: 'None', lic: 'None', learn: 'Which fields move their premium' },
    { l: 'B', h: 'MGA', w: 'Delegated underwriting; a fronting carrier and reinsurers hold the risk', cap: .1, capl: 'Minimal', lic: 'Intermediary', learn: 'Loss ratios on our own pricing' },
    { l: 'C', h: 'Own carrier', w: 'Captive or licensed insurer on our balance sheet', cap: 1, capl: 'Solvency capital', lic: 'Full, per domicile', learn: 'Float; full margin; full risk' }];
  scene(T('n24b') - .5, END('n24b') + .9, `
    <div data-k="h" class="abs h2" style="left:160px;top:140px">Three ways to be an insurer, only one of them early</div>
    ${IP.map((p, i) => `<div data-k="c${i}" class="card" style="left:${160 + i * 540}px;top:280px;width:520px;height:520px">
      <div class="abs big ${i < 2 ? 'y' : ''}" style="left:30px;top:30px;font-size:64px">${p.l}</div>
      <div class="abs h2" style="left:100px;top:40px">${p.h}</div>
      <div class="abs body" style="left:32px;top:130px;width:450px;font-size:21px">${p.w}</div>
      <div class="abs lbl" style="left:32px;top:262px">Our capital · <span style="color:${INK}">${p.capl}</span></div>
      <div class="abs" style="left:32px;top:296px;width:450px;height:10px;border-radius:5px;background:rgba(244,242,236,.1)"><div data-k="cb${i}" style="height:10px;border-radius:5px;background:${i === 2 ? INK : Y};width:${Math.max(p.cap, .015) * 450}px;transform-origin:0 50%"></div></div>
      <div class="abs lbl" style="left:32px;top:344px">Licence · <span style="color:${INK}">${p.lic}</span></div>
      <div class="abs lbl" style="left:32px;top:400px">We learn</div>
      <div class="abs body" style="left:32px;top:428px;width:450px;font-size:20px;color:${INK}">${p.learn}</div></div>`).join('')}
    <svg class="full"><path data-k="rt" pathLength="1" d="M420 830 C 420 880, 440 890, 520 890 H 860 C 940 890, 960 880, 960 830" fill="none" stroke="${Y}" stroke-width="3"/>
      <path data-k="rta" d="M950 842 L960 828 L970 842" fill="none" stroke="${Y}" stroke-width="3"/></svg>
    <div data-k="rl" class="abs lbl y" style="left:690px;top:910px;transform:translateX(-50%);font-size:17px">The realistic route · A then B</div>
    <div data-k="lt" class="abs chip" style="left:1500px;top:830px;transform:translateX(-50%);color:${INK}">Later · if loss ratios earn it</div>
    <div data-k="ft" class="foot">Licence and capital regimes vary by domicile; specifics to be confirmed with counsel</div>`,
    (t, k) => {
      const t0 = T('n24b') - .3;
      show(k.h, t, t0); show(k.ft, t, t0 + 1, 1e9, { dy: 0 });
      const ts = [at('n24b', 'data partner'), at('n24b', 'M G A'), at('n24b', 'own carrier')];
      ts.forEach((tt, i) => { show(k['c' + i], t, tt - .2, 1e9, { dy: 30 }); k['cb' + i].style.transform = `scaleX(${P(t, tt + .4, 1.2, E.io3)})`; });
      const tr = at('n24b', 'realistic route');
      draw(k.rt, P(t, tr, 1.1, E.io2)); k.rta.style.opacity = P(t, tr + 1, .3); show(k.rl, t, tr + .5, 1e9, { dy: 0 });
      k.c0.classList.toggle('hi', t > tr); k.c1.classList.toggle('hi', t > tr + .6);
      if (t > tr) k.c2.style.opacity = parseFloat(k.c2.style.opacity) * (1 - .5 * P(t, tr, .6));
      show(k.lt, t, tr + .9, 1e9, { dy: 0 });
    });

  // ---------------------------------------------------------------- 07 · observation is the edge
  const tP = at('n25', 'The platform');
  stock('tower', T('n25') - .6, tP + .5, { bright: .5 });
  scene(T('n25') - .4, tP + .4, `<div data-k="h" class="abs h1" style="left:160px;top:780px">The edge is <span class="y">observation</span>, not volume</div>`,
    (t, k) => show(k.h, t, T('n25') - .1, 1e9, { d: 1 }));
  const ST = [['Underwrite', 'Attested fields, levels, model outputs'], ['Snapshot', 'State at close, frozen with lineage'], ['Observe', 'Realised NOI, cash, arrears, claims'],
    ['Curve', 'Loss frequency and severity'], ['Price', 'Premiums and surety fees']];
  const GX0 = 260, GX1 = 1660, GY = 880, GC = 640;
  const real = Array.from({ length: 29 }, (_, i) => { const x = GX0 + i * 50; const y = GC + 18 * Math.sin(i * 1.3) + 10 * Math.sin(i * .47 + 1) + i * 3.2; return `${i ? 'L' : 'M'}${x} ${y.toFixed(1)}`; }).join(' ');
  scene(tP - .3, END('n25') + .8, `
    ${ST.map((s, i) => `<div data-k="s${i}" class="abs" style="left:${160 + i * 330}px;top:160px;width:300px">
      <div data-k="sn${i}" class="lbl" style="font-size:18px">0${i + 1}</div><div class="h3" style="margin-top:10px">${s[0]}</div>
      <div class="body" style="margin-top:8px;font-size:19px">${s[1]}</div></div>`).join('')}
    <svg class="full">
      <path data-k="sl" d="M160 150 H1760" stroke="${LINE}" stroke-width="1.5" fill="none"/><g data-k="sd">${flowDots(3, 6)}</g>
      <line data-k="ax" x1="${GX0}" x2="${GX1}" y1="${GY}" y2="${GY}" stroke="${DIM}" stroke-width="1.5" pathLength="1"/>
      <line data-k="cl" x1="${GX0}" x2="${GX1}" y1="${GC}" y2="${GC}" stroke="${INK}" stroke-width="2" stroke-dasharray="8 8"/>
      <path data-k="rl" pathLength="1" d="${real}" fill="none" stroke="${Y}" stroke-width="3.5" stroke-linejoin="round"/>
    </svg>
    <div data-k="cll" class="abs lbl" style="left:${GX0}px;top:${GC - 44}px;color:${INK}">Claimed at close</div>
    <div data-k="rll" class="abs lbl y" style="left:${GX1 - 10}px;top:${GC + 120}px;transform:translateX(-100%)">Realised, for years</div>
    <div data-k="axl" class="abs lbl" style="left:${GX1}px;top:${GY + 18}px;transform:translateX(-100%)">Years after close →</div>
    <div data-k="lc" class="abs" style="left:960px;top:470px;transform:translateX(-50%);text-align:center;white-space:nowrap"><div class="h2">Claimed vs realised = <span class="y">a loss curve</span></div><div class="lbl" style="margin-top:12px">No incumbent has it</div></div>`,
    (t, k) => {
      const tc = at('n25', 'claimed'), tr = at('n25', 'realised'), tl = at('n25', 'loss curve');
      const lit = [tc - .6, tc, tr, tl, tl + .4];
      ST.forEach((_, i) => { show(k['s' + i], t, tP + i * .12, 1e9, { dy: 16 }); k['sn' + i].style.color = t > lit[i] ? Y : DIM; });
      k.sl.style.opacity = P(t, tP, .6); flow(k.sd, k.sl, t, tP + .3, 1e9, { rate: .8, dur: 3 });
      draw(k.ax, P(t, tc - .3, .8)); show(k.axl, t, tc, 1e9, { dy: 0 });
      k.cl.style.opacity = P(t, tc, .6); show(k.cll, t, tc + .1, 1e9, { dy: 0 });
      draw(k.rl, P(t, tr, 2.6, E.io2)); show(k.rll, t, tr + 1.4, 1e9, { dy: 0 });
      show(k.lc, t, tl - .2, 1e9, { dy: 18 });
    });

  // ---------------------------------------------------------------- 07 · short tails first
  const PR = [['Data warranty cover', 150, '12 months'], ['Surety bond', 150, '12 months'], ['Settlement cover', 40, 'Weeks'],
    ['Rent default cover', 330, '1 to 3 years'], ['W&I on share deals', 700, 'Up to 7 years'], ['Title cover', 960, 'Open-ended']];
  const py = i => (i < 3 ? 330 : 580) + (i % 3) * 66;
  scene(T('n26') - .4, END('n26') + 1.2, `
    <div data-k="h" class="abs h2" style="left:160px;top:140px">Short tails first, because they <span class="y">teach fastest</span></div>
    <div data-k="g0" class="abs lbl y" style="left:160px;top:282px">Parametric · the trigger is a number the platform measures</div>
    <div data-k="g1" class="abs lbl" style="left:160px;top:532px">Established market · enter as data partner and MGA, not a carrier</div>
    ${PR.map((p, i) => `<div data-k="p${i}" class="abs" style="left:160px;top:${py(i)}px;width:1600px;height:50px">
      <div class="abs h3" style="left:0;top:8px;font-size:25px;${i > 2 ? `color:${DIM}` : ''}">${p[0]}</div>
      <div data-k="pb${i}" class="abs" style="left:420px;top:18px;height:14px;width:${p[1]}px;border-radius:7px;background:${i < 3 ? Y : 'rgba(244,242,236,.3)'};transform-origin:0 50%;${i === 5 ? 'background:linear-gradient(90deg,rgba(244,242,236,.3),rgba(244,242,236,0))' : ''}"></div>
      <div data-k="pl${i}" class="abs lbl" style="left:${440 + p[1]}px;top:16px">${p[2]}</div></div>`).join('')}
    <div data-k="ov" class="abs" style="left:160px;top:850px;white-space:nowrap">
      <span class="lbl" style="margin-right:28px">Order of value</span>
      <span class="h3">1 · Loss curve</span><span class="h3" style="color:${DIM}">&nbsp;&nbsp;→&nbsp;&nbsp;</span>
      <span class="h3">2 · MGA margin</span><span class="h3" style="color:${DIM}">&nbsp;&nbsp;→&nbsp;&nbsp;</span>
      <span class="h3 y">3 · Float, last</span></div>
    <div data-k="ft" class="foot">Tail lengths indicative; product design subject to regulatory review per domicile</div>`,
    (t, k) => {
      const t0 = T('n26') - .3, tpa = at('n26', 'parametric');
      show(k.h, t, t0); show(k.ft, t, t0 + 1, 1e9, { dy: 0 });
      show(k.g0, t, tpa - .2, 1e9, { dy: 0 }); show(k.g1, t, t0 + 1.2, 1e9, { dy: 0 });
      PR.forEach((_, i) => {
        const ti = (i < 3 ? tpa : t0 + 1.3) + (i % 3) * .15;
        show(k['p' + i], t, ti, 1e9, { dy: 0, dx: -12 });
        k['pb' + i].style.transform = `scaleX(${P(t, ti + .2, 1, E.io3)})`;
      });
      show(k.ov, t, at('n26', 'Float') - .2, 1e9, { dy: 14 });
    });

  // ---------------------------------------------------------------- 08 · the plan
  const PL = [['Now', ['Assurance levels into the engine', 'Cash reconciliation via payment ops', 'Standard bond contract, self-bond only', 'Evidence pack to one W&I insurer']],
    ['Next', ['Surety book: standing terms on the platform', 'MGA with a fronting carrier', 'Data warranty and settlement cover', 'Named referee for adjudicated triggers']],
    ['Later', ['Own carrier if loss ratios earn it', 'Long-tail lines: W&I, title', 'Float as a balance-sheet business', 'Levels as an industry standard']]];
  const LN = [['Measure', ' first.'], ['Bond', ' what is measured.'], ['Insure', ' the rest.']];
  scene(T('n27a') - .5, TL.end + .3, `
    ${PL.map((c, i) => `<div data-k="c${i}" class="card" style="left:${160 + i * 540}px;top:280px;width:520px;height:420px">
      <div class="abs lbl y" style="left:32px;top:32px">${c[0]}</div>
      ${c[1].map((s, j) => `<div class="abs body" style="left:32px;top:${86 + j * 74}px;width:450px;font-size:21px;color:${INK}">${s}</div>`).join('')}</div>`).join('')}
    ${LN.map((l, i) => `<div data-k="l${i}" class="abs" style="left:160px;top:${300 + i * 150}px;font-weight:300;font-size:104px;letter-spacing:-.045em;white-space:nowrap"><span class="y">${l[0]}</span>${l[1]}</div>`).join('')}
    <div data-k="ft" class="foot">Working draft for internal discussion · sizes and terms illustrative</div>`,
    (t, k) => {
      const tb = T('n27b');
      PL.forEach((_, i) => show(k['c' + i], t, T('n27a') - .2 + i * .25, tb - .5, { dy: 30 }));
      ['Measure', 'Bond', 'Insure'].forEach((w, i) => show(k['l' + i], t, at('n27b', w) - .1, 1e9, { dy: 36, blur: 12, d: 1 }));
      show(k.ft, t, T('n27a'), 1e9, { dy: 0 });
    }, { fo: .7 });

  // ---------------------------------------------------------------- end card
  stock('skyline', TL.end - .6, TL.total + 1, { bright: .38, z0: 1.0, z1: 1.05 });
  scene(TL.end - .3, TL.total + 1, `
    <img data-k="logo" class="abs" src="../../propchain-reel/assets/logo-white.svg" style="left:960px;top:500px;height:66px;transform:translate(-50%,-50%)">
    <div data-k="l" class="abs lbl" style="left:960px;top:590px;transform:translateX(-50%)">Fraud, bonds and insurance · Concept note</div>`,
    (t, k) => { show(k.logo, t, TL.end, 1e9, { dy: 0, blur: 12, d: 1.2 }); show(k.l, t, TL.end + .6, 1e9, { dy: 0 });
      const f = P(t, TL.total - 1.2, 1.1, E.io2); $('#scenes').style.opacity = $('#stock').style.opacity = 1 - f; }, { fo: .01 });
}
