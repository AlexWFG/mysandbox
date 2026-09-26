// Title · 01 The problem · 02 Six layers · 03 Corroboration (+ assurance levels)
function build1() {
  // ---------------------------------------------------------------- title
  scene(0, T('n01a') + .2, `
    <svg class="full"><g data-k="seal">
      <circle r="250" fill="none" stroke="${LINE}" stroke-width="1.5" pathLength="1" transform="rotate(-90)"/>
      <circle r="206" fill="none" stroke="${Y}" stroke-width="2" pathLength="1" transform="rotate(-90)"/>
      <path d="M-78 6 L-22 60 L84 -62" fill="none" stroke="${Y}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round" pathLength="1"/>
    </g></svg>
    <img data-k="logo" class="abs" src="../../propchain-reel/assets/logo-white.svg" style="left:160px;top:120px;height:38px">
    <div data-k="eb" class="abs eyebrow" style="left:160px;top:372px"><span class="bar"></span>Fraud, bonds and insurance</div>
    <div data-k="h" class="abs hxl" style="left:150px;top:430px">Making lies<br><span class="y">expensive</span></div>
    <div data-k="sub" class="abs sub" style="left:160px;top:740px;width:1000px">How fraud is stopped on attested data, who puts up capital, and what a native insurer would realistically be.</div>
    <div data-k="ft" class="abs lbl" style="left:160px;top:950px">Concept note · Working draft for internal discussion</div>`,
    (t, k) => {
      show(k.logo, t, .1, 1e9, { dy: 0, blur: 6 }); show(k.eb, t, .35); show(k.h, t, .6, 1e9, { dy: 40, blur: 14, d: 1.2 });
      show(k.sub, t, 1.3); show(k.ft, t, 1.8);
      const c = k.seal.querySelectorAll('[pathLength]');
      draw(c[0], P(t, .2, 1.8)); draw(c[1], P(t, .6, 1.6)); draw(c[2], P(t, 1.7, .8, E.o3));
      k.seal.setAttribute('transform', `translate(1450,540) rotate(${lerp(-10, 0, P(t, 0, 3.5))}) scale(${lerp(.92, 1, P(t, 0, 4))})`);
    }, { fi: .01, fo: .7 });

  // ---------------------------------------------------------------- 01 · lease stock + attestation overlay
  const leaseEnd = at('n01b', 'A rent roll') + .4;
  stock('lease', T('n01a') - .6, leaseEnd, { bright: .6, z0: 1.02, z1: 1.1 });
  scene(T('n01a') - .3, leaseEnd, `
    <svg class="full"><g data-k="br" fill="none" stroke="${Y}" stroke-width="3">
      <path pathLength="1" d="M640 330 v-60 h60"/><path pathLength="1" d="M1220 270 h60 v60"/>
      <path pathLength="1" d="M1280 750 v60 h-60"/><path pathLength="1" d="M700 810 h-60 v-60"/>
    </g><line data-k="scan" x1="640" x2="1280" stroke="${Y}" stroke-width="2" opacity=".0"/></svg>
    <div data-k="chip" class="abs chip y" style="left:640px;top:836px">${icon('check', 16, '#0B0B0C')} Attested · Proof of ingestion</div>
    <div data-k="meta" class="abs lbl" style="left:640px;top:890px">Source · lineage · timestamp</div>`,
    (t, k) => {
      const t0 = T('n01a');
      k.br.querySelectorAll('path').forEach((p, i) => draw(p, P(t, t0 + i * .08, .7)));
      const s = P(t, t0 + .3, 1.3, E.io2); k.scan.setAttribute('y1', lerp(280, 800, s)); k.scan.setAttribute('y2', lerp(280, 800, s));
      k.scan.setAttribute('opacity', s > 0 && s < 1 ? .8 : 0);
      show(k.chip, t, t0 + 1.2); show(k.meta, t, t0 + 1.45);
    }, { fo: .6 });

  // ---------------------------------------------------------------- 01 · the signed lie, and consensus
  const rows = [0, 1, 2, 3, 4, 5], ghost = [1, 4];
  scene(at('n01b', 'provenance') - .5, END('n02') + .7, `
    <div data-k="h" class="abs h1" style="left:160px;top:140px">Attestation proves <span class="y">provenance</span>,<br>not truth.</div>
    <div data-k="card" class="card" style="left:160px;top:390px;width:780px;height:540px">
      <div class="abs lbl" style="left:28px;top:28px">Rent roll · Asset A</div>
      <div data-k="seal" class="abs chip y" style="right:24px;top:20px">${icon('file-signature', 16, '#0B0B0C')} Signed · attested</div>
      ${rows.map(i => `<div data-k="r${i}" class="abs" style="left:24px;top:${88 + i * 72}px;width:730px;height:56px;border:1.5px dashed transparent;border-radius:10px">
        <div class="abs" style="left:16px;top:13px;color:${DIM}">${icon('user', 28)}</div>
        <div class="abs" data-k="b${i}" style="left:66px;top:22px;width:${200 + (i * 53) % 90}px;height:11px;border-radius:6px;background:rgba(244,242,236,.28)"></div>
        <div class="abs lbl" style="left:390px;top:19px">Unit 0${i + 1}</div>
        <div class="abs" style="left:560px;top:22px;width:${70 + (i * 37) % 50}px;height:11px;border-radius:6px;background:rgba(244,242,236,.28)"></div>
        <div data-k="g${i}" class="abs chip dash" style="right:10px;top:9px;border-color:${DIM};color:${INK}">Phantom</div>
      </div>`).join('')}
    </div>
    <div data-k="v1" class="abs" style="left:1080px;top:430px;width:660px">
      <div class="abs" style="left:0;top:0;width:76px;height:76px;border-radius:50%;background:${Y};display:flex;align-items:center;justify-content:center">${icon('check', 40, '#0B0B0C', 2.4)}</div>
      <div class="abs h2" style="left:110px;top:2px">Provenance</div>
      <div class="abs body" style="left:110px;top:62px;width:540px">Who signed it, where it came from, when. Proven.</div>
    </div>
    <div data-k="v2" class="abs" style="left:1080px;top:640px;width:660px">
      <div class="abs" style="left:0;top:0;width:76px;height:76px;border-radius:50%;border:1.5px dashed ${DIM};box-sizing:border-box;display:flex;align-items:center;justify-content:center;color:${DIM}">${icon('circle-help', 38)}</div>
      <div class="abs h2" style="left:110px;top:2px;color:${DIM}">Truth</div>
      <div class="abs body" style="left:110px;top:62px;width:540px">Whether the tenants exist. Not proven.</div>
    </div>
    <svg class="full">
      <g data-k="ring">
        <circle data-k="ringc" cx="1440" cy="620" r="170" fill="none" stroke="${LINE}" stroke-width="1.5"/>
        <path data-k="ringp" d="M1440 450 a170 170 0 1 1 -0.01 0" fill="none" stroke="none"/>
        ${Array.from({ length: 8 }, (_, i) => { const a = i / 8 * Math.PI * 2 - Math.PI / 2; return `<circle class="nd" cx="${1440 + 170 * Math.cos(a)}" cy="${620 + 170 * Math.sin(a)}" r="13" fill="#141416" stroke="${INK}" stroke-width="1.5"/>`; }).join('')}
        <g data-k="ringdots">${flowDots(8, 5, INK)}</g>
      </g>
      <path data-k="q" d="M946 ${390 + 88 + 72 + 28} C 1080 ${390 + 88 + 72 + 28}, 1140 620, 1262 620" fill="none" stroke="${Y}" stroke-width="2" stroke-dasharray="7 7"/>
      <g data-k="qdots">${flowDots(3, 6, Y)}</g>
    </svg>
    <div data-k="rl" class="abs lbl" style="left:1440px;top:606px;transform:translateX(-50%)">Consensus</div>
    <div data-k="rlbl" class="abs" style="left:1240px;top:830px;width:420px;text-align:center"><div class="lbl" style="color:${INK}">Orders what nodes can see</div></div>
    <div data-k="qchip" class="abs chip yo" style="left:1010px;top:604px;background:#0f0f10">Tenant exists?</div>
    <div data-k="ans" class="abs chip" style="left:1440px;top:885px;transform:translateX(-50%);color:${INK}">${icon('x', 16)} Cannot decide</div>`,
    (t, k) => {
      show(k.h, t, at('n01b', 'provenance') - .3, 1e9, { d: 1 });
      const tc = at('n01b', 'A rent roll');
      show(k.card, t, tc, 1e9, { dy: 30, d: 1 });
      show(k.seal, t, tc + .5, 1e9, { dy: 0, dx: 16 });
      const tg = at('n01b', 'phantom');
      ghost.forEach((i, j) => {
        const p = P(t, tg + j * .25, .6);
        k['r' + i].style.borderColor = `rgba(244,242,236,${.55 * p})`;
        k['b' + i].style.opacity = 1 - .7 * p;
        show(k['g' + i], t, tg + j * .25 + .15, 1e9, { dy: 0, dx: 12 });
      });
      rows.filter(i => !ghost.includes(i)).forEach(i => fade(k['g' + i], 0));
      const tn = T('n02') - .35;
      show(k.v1, t, at('n01b', 'perfectly signed'), tn, { dx: 20, dy: 0 });
      show(k.v2, t, at('n01b', 'perfectly false'), tn, { dx: 20, dy: 0 });
      // consensus ring
      const pr = P(t, tn + .15, .9);
      fade(k.ring, pr); k.ringc.style.strokeDasharray = '1068 1068'; k.ringc.style.strokeDashoffset = 1068 * (1 - pr);
      flow(k.ringdots, k.ringp, t, tn + .4, 1e9, { rate: 2.2, dur: 3, fadeTail: false });
      show(k.rl, t, tn + .4, 1e9, { dy: 0 }); show(k.rlbl, t, tn + .6);
      const tq = at('n02', 'whether');
      k.q.style.opacity = P(t, tq - .2, .5); flow(k.qdots, k.q, t, tq - .2, tq + 1.2, { rate: 2.5, dur: 1 });
      show(k.qchip, t, tq, 1e9, { dy: 0, blur: 4 });
      show(k.ans, t, END('n02') - .5);
    });

  // ---------------------------------------------------------------- 01 · where fraud happens
  const V = [['Fabricated source data', 'Phantom tenants, side letters, inflated rents'], ['Settlement diversion', 'Changed payment instructions by email'],
    ['Identity and authority', 'Fake counterparty, agent beyond permission'], ['Market manipulation', 'Fake mandates, spoofed boxes, collusive bids'],
    ['Collusive valuation', 'A mark that suits seller and lender'], ['Internal and adversarial', 'Tuned models, injected documents']];
  scene(T('n03') - .5, END('n03') + .9, `
    <div data-k="eb" class="abs eyebrow" style="left:160px;top:150px">Where fraud happens</div>
    <div data-k="h" class="abs h2" style="left:160px;top:190px">Six vectors, in order of how often they occur</div>
    ${V.map((v, i) => `<div data-k="v${i}" class="abs" style="left:160px;top:${320 + i * 96}px;width:1150px;height:96px">
      <div class="abs rule" style="left:0;right:0;top:0"></div>
      <div class="abs lbl" style="left:0;top:36px">0${i + 1}</div>
      <div data-k="vn${i}" class="abs h3" style="left:70px;top:28px">${v[0]}</div>
      <div class="abs body" style="left:560px;top:32px;font-size:21px">${v[1]}</div></div>`).join('')}
    <svg class="full"><path data-k="brk" pathLength="1" d="M1330 332 h22 v168 h-22" fill="none" stroke="${Y}" stroke-width="2.5"/>
      <path data-k="brl" pathLength="1" d="M1352 416 H1440" fill="none" stroke="${Y}" stroke-width="2.5"/>
      <circle data-k="cc" cx="1510" cy="416" r="68" fill="rgba(255,190,6,.1)" stroke="${Y}" stroke-width="2.5"/>
      ${sicon('banknote', 1510, 416, 56, Y, 'bn')}</svg>
    <div data-k="cash" class="abs" style="left:1440px;top:506px;width:380px">
      <div class="lbl y" style="font-size:18px">Cash</div>
      <div class="body" style="margin-top:8px">The mechanical truth the platform can see</div></div>
    <div data-k="ft" class="foot">Ordering is qualitative, from transaction practice, not measured</div>`,
    (t, k) => {
      const t0 = T('n03') - .3;
      show(k.eb, t, t0); show(k.h, t, t0 + .1);
      const tm = at('n03', 'misstated'), td = at('n03', 'diverted'), tc = at('n03', 'cash');
      V.forEach((_, i) => {
        const v = show(k['v' + i], t, t0 + .3 + i * .12, 1e9, { dy: 16 });
        if (i > 1) k['v' + i].style.opacity = v * (1 - .68 * P(t, tm, .7));
      });
      k.vn0.style.color = P(t, tm, .4) > .5 ? Y : INK; k.vn1.style.color = P(t, td, .4) > .5 ? Y : INK;
      draw(k.brk, P(t, tc - .6, .6)); draw(k.brl, P(t, tc - .2, .4));
      const pc = P(t, tc, .7, E.o5); k.cc.setAttribute('r', 68 * pc); k.cc.style.opacity = pc;
      drawAll(k.bn, P(t, tc + .2, .8)); show(k.cash, t, tc + .3); show(k.ft, t, t0 + 1, 1e9, { dy: 0 });
    });

  // ---------------------------------------------------------------- 02 · six layers
  const LY = [['Identity', 'Impersonation'], ['Provenance', 'Silent edits, undated data'], ['Corroboration', 'Single-source fabrication'],
    ['Economic · bonds', 'Cheap lies about verifiable facts'], ['Professional', 'Platform self-dealing'], ['Memory', 'Repeat offenders']];
  const KEYW = ['identity', 'provenance', 'corroboration', 'bonds', 'professional', 'memory'];
  const SX = 460, SW = 820, SH = 74, top = i => 890 - i * 90;
  // lies: (layer that stops it; 6 = gets through everything)
  const LIES = [0, 1, 2, 0, 3, 1, 2, 4, 5, 3, 1, 6, 4, 2, 5, 6];
  scene(T('n05') - .5, END('n06') + .9, `
    <div data-k="h" class="abs h2" style="left:160px;top:140px">Six layers, each stopping what the one below cannot</div>
    ${LY.map((l, i) => `<div data-k="s${i}" class="card" style="left:${SX}px;top:${top(i)}px;width:${SW}px;height:${SH}px;border-radius:12px">
      <div class="abs" style="left:26px;top:20px;font:500 22px Mono;color:${Y}">${i}</div>
      <div class="abs h3" style="left:70px;top:18px;font-size:28px">${l[0]}</div>
      <div class="abs lbl" style="right:24px;top:29px;font-size:13px">Stops · ${l[1]}</div></div>`).join('')}
    ${LY.map((l, i) => `<div data-k="c${i}" class="abs chip ${i === 3 || i === 4 ? 'y' : ''}" style="left:${SX + SW + 24}px;top:${top(i) + 18}px">${i === 3 || i === 4 ? 'New decision' : 'In the stack'}</div>`).join('')}
    <svg class="full">
      <path data-k="res" pathLength="1" d="M${SX} 400 v-26 h${SW} v26" fill="none" stroke="${Y}" stroke-width="2.5"/>
      ${LIES.map((_, i) => `<circle data-k="p${i}" r="8" fill="${INK}"/><circle data-k="f${i}" r="8" fill="none" stroke="${Y}" stroke-width="2"/>`).join('')}
    </svg>
    <div data-k="rl" class="abs lbl y" style="left:${SX + SW / 2}px;top:320px;transform:translateX(-50%);font-size:17px">Residual · what insurance prices</div>`,
    (t, k) => {
      show(k.h, t, T('n05') - .3);
      const A = KEYW.map(w => at('n05', w));
      LY.forEach((_, i) => {
        const v = show(k['s' + i], t, T('n05') + .2 + i * .14, 1e9, { dy: 30, d: .7 });
        const lit = P(t, A[i] - .1, .5); k['s' + i].style.opacity = v * (.3 + .7 * lit);
        k['s' + i].style.borderColor = t > A[i] - .1 && t < A[i] + .9 ? Y : '';
      });
      const tn = T('n06');
      LY.forEach((_, i) => show(k['c' + i], t, tn + .3 + i * .08, 1e9, { dy: 0, dx: -14 }));
      draw(k.res, P(t, at('n06', 'insurance') - .3, .7)); show(k.rl, t, at('n06', 'insurance'));
      LIES.forEach((s, i) => {
        const p = k['p' + i], f = k['f' + i], x = SX + 60 + ((i * 263) % (SW - 120));
        let ta, yEnd;
        if (s < 6) { ta = Math.max(A[s] + .45, A[0] + .4) + (i % 3) * .45; yEnd = top(s) + SH + 10; }
        else { ta = at('n06', 'insurance') + (i === 11 ? 0 : .35); yEnd = 386; }
        const t0 = ta - 1.3, pp = P(t, t0, 1.3, E.o3);
        if (t < t0) { p.setAttribute('opacity', 0); f.setAttribute('opacity', 0); return; }
        const y = lerp(1100, yEnd, pp);
        p.setAttribute('cx', x); p.setAttribute('cy', y); f.setAttribute('cx', x); f.setAttribute('cy', y);
        const hit = P(t, ta, .7, E.o3);
        p.setAttribute('fill', hit > 0 ? Y : INK);
        p.setAttribute('opacity', s < 6 ? 1 - P(t, ta + .5, .6) : 1);
        f.setAttribute('r', 8 + 22 * hit); f.setAttribute('opacity', hit > 0 && hit < 1 ? 1 - hit : 0);
      });
    });

  // ---------------------------------------------------------------- 03 · corroboration worked example
  const SRC = [['file-text', "Seller's rent roll", 'Overstate', 1020], ['book-open', 'Property manager ledger', 'Follows seller', 1020],
    ['landmark', 'Bank receipts, 12 months', 'None', 958], ['users', 'Tenant confirmations', 'Understate', 955]];
  const X = v => 820 + (v - 920) * 8, AY = 860;
  scene(T('n07') - .5, END('n10') + .8, `
    <div data-k="h" class="abs h2" style="left:160px;top:140px">A quorum of sources, with <span class="y">cash</span> as the tie-break</div>
    <div data-k="sub" class="abs lbl" style="left:160px;top:222px">Worked example · annual rent on one asset</div>
    ${SRC.map((s, i) => `<div data-k="c${i}" class="card" style="left:160px;top:${300 + i * 124}px;width:560px;height:104px">
      <div class="abs" style="left:26px;top:34px;color:${DIM}" data-k="ci${i}">${icon(s[0], 34)}</div>
      <div class="abs h3" style="left:84px;top:22px;font-size:26px">${s[1]}</div>
      <div class="abs lbl" style="left:84px;top:64px;font-size:13px">Incentive · ${s[2]}</div>
      <div data-k="cx${i}" class="abs chip ${i === 2 ? 'y' : 'dash'}" style="right:18px;top:18px;${i === 2 ? '' : `color:${INK}`}">${i === 2 ? 'Cash' : i === 0 ? 'Loses standing' : 'One source'}</div></div>`).join('')}
    <svg class="full">
      <rect data-k="band" x="${X(956 * .98)}" y="360" width="${X(956 * 1.02) - X(956 * .98)}" height="${AY - 360}" fill="rgba(255,190,6,.08)" stroke="${Y}" stroke-width="1.5" stroke-dasharray="6 6"/>
      <line data-k="axis" x1="820" x2="1780" y1="${AY}" y2="${AY}" stroke="${DIM}" stroke-width="1.5" pathLength="1"/>
      ${[920, 940, 960, 980, 1000, 1020, 1040].map(v => `<g data-k="tk${v}"><line x1="${X(v)}" x2="${X(v)}" y1="${AY}" y2="${AY + 10}" stroke="${DIM}" stroke-width="1.5"/>
        <text x="${X(v)}" y="${AY + 38}" fill="${FAINT}" font-family="Mono" font-size="15" text-anchor="middle">€${v.toLocaleString('en-GB')}k</text></g>`).join('')}
      <line data-k="m0" x1="${X(1020)}" x2="${X(1020)}" y1="${AY}" y2="400" stroke="${INK}" stroke-width="2.5"/>
      <circle data-k="d0" cx="${X(1020)}" cy="400" r="9" fill="${INK}"/>
      <circle data-k="d1" cx="${X(1020)}" cy="400" r="19" fill="none" stroke="${INK}" stroke-width="2"/>
      <line data-k="m2" x1="${X(958)}" x2="${X(958)}" y1="${AY}" y2="520" stroke="${INK}" stroke-width="2.5"/>
      <circle data-k="d2" cx="${X(958)}" cy="520" r="9" fill="${INK}"/>
      <line data-k="m3" x1="${X(955)}" x2="${X(955)}" y1="${AY}" y2="640" stroke="${INK}" stroke-width="2.5"/>
      <circle data-k="d3" cx="${X(955)}" cy="640" r="9" fill="${INK}"/>
      <line data-k="mq" x1="${X(956)}" x2="${X(956)}" y1="${AY}" y2="410" stroke="${Y}" stroke-width="4"/>
      <circle data-k="dq" cx="${X(956)}" cy="410" r="12" fill="${Y}"/>
    </svg>
    <div data-k="l0" class="abs" style="left:${X(1020) + 26}px;top:370px"><div class="big" style="font-size:44px">€1,020k</div><div data-k="l0s" class="lbl" style="margin-top:8px">Rent roll</div></div>
    <div data-k="l2" class="abs" style="left:${X(958) + 26}px;top:492px"><div class="big" style="font-size:40px">€958k</div><div class="lbl" style="margin-top:8px">Bank receipts</div></div>
    <div data-k="l3" class="abs" style="left:${X(955) - 26}px;top:612px;transform:translateX(-100%);text-align:right"><div class="big" style="font-size:40px">€955k</div><div class="lbl" style="margin-top:8px">Tenants</div></div>
    <div data-k="lq" class="abs" style="left:${X(956 * .98) - 24}px;top:372px;text-align:right;transform:translateX(-100%)"><div class="lbl y">Quorum</div><div class="big y" style="font-size:64px;margin-top:6px">€956k</div></div>
    <div data-k="a3" class="abs" style="left:${X(956 * .98) - 24}px;top:486px;transform:translateX(-100%)"><div class="chip y" style="font-size:20px;padding:9px 16px 8px">Level A3</div></div>
    <div data-k="bl" class="abs lbl y" style="left:${X(956)}px;top:326px;transform:translateX(-50%);font-size:13px">Tolerance 2%</div>
    <div data-k="ft" class="foot">Numbers are a worked illustration</div>`,
    (t, k) => {
      const t0 = T('n07') - .3;
      show(k.h, t, t0); show(k.sub, t, t0 + .3); show(k.ft, t, t0 + .8, 1e9, { dy: 0 });
      const tsrc = at('n07', 'four');
      SRC.forEach((_, i) => show(k['c' + i], t, tsrc - .4 + i * .16, 1e9, { dx: -24, dy: 0 }));
      draw(k.axis, P(t, tsrc, 1));
      [920, 940, 960, 980, 1000, 1020, 1040].forEach((v, i) => fade(k['tk' + v], P(t, tsrc + .2 + i * .06, .4)));
      // markers rise from the axis
      const rise = (m, d, yTop, ts) => { const p = P(t, ts, .8, E.o5); m.setAttribute('y2', lerp(AY, yTop, p)); m.style.opacity = p > 0 ? 1 : 0; d.setAttribute('cy', lerp(AY, yTop, p)); d.style.opacity = p > 0 ? 1 : 0; };
      const tr = at('n08', 'one million'), tl = at('n08', 'agrees'), t1 = at('n08', 'one source');
      rise(k.m0, k.d0, 400, tr); show(k.l0, t, tr + .2, 1e9, { dy: 0, dx: -10 });
      const pl = P(t, tl, .7, E.o5); k.d1.setAttribute('r', lerp(60, 19, pl)); k.d1.style.opacity = pl;
      k.l0s.textContent = t > tl + .3 ? 'Rent roll + ledger' : 'Rent roll';
      show(k.cx1, t, t1, 1e9, { dy: 0, dx: 10 }); fade(k.cx3, 0); show(k.cx0, t, at('n10', 'quorum'), 1e9, { dy: 0, dx: 10 });
      rise(k.m2, k.d2, 520, at('n09', 'Bank')); show(k.l2, t, at('n09', 'nine hundred'), 1e9, { dy: 0, dx: -10 });
      rise(k.m3, k.d3, 640, at('n09', 'Tenants')); show(k.l3, t, at('n09', 'nine fifty-five'), 1e9, { dy: 0, dx: 10 });
      // cash outranks documents
      const tcash = at('n10', 'Cash'), tq = at('n10', 'quorum'), ta3 = at('n10', 'A three');
      const hc = P(t, tcash, .5); k.c2.classList.toggle('hi', hc > .5); k.ci2.style.color = hc > .5 ? Y : DIM;
      show(k.cx2, t, tcash, 1e9, { dy: 0, dx: 10 });
      k.m2.setAttribute('stroke', hc > .5 ? Y : INK); k.d2.setAttribute('fill', hc > .5 ? Y : INK);
      const dimv = 1 - .55 * P(t, tq, .8);
      [k.c0, k.c1].forEach(c => { if (t > tq) c.style.opacity = Math.min(parseFloat(c.style.opacity || 1), dimv); });
      k.m0.style.opacity = t > tq ? dimv : k.m0.style.opacity; k.d0.style.opacity = t > tq ? dimv : k.d0.style.opacity;
      k.band.style.opacity = P(t, tq - .3, .6); show(k.bl, t, tq, 1e9, { dy: 0 });
      rise(k.mq, k.dq, 410, tq + .3); show(k.lq, t, tq + .5, 1e9, { dy: 0, dx: 12 });
      show(k.a3, t, ta3, 1e9, { dy: 10 });
    });

  // ---------------------------------------------------------------- 03 · assurance levels
  const LV = [['A0', 'Self-declared, no lineage', 'Nobody on the platform'], ['A1', 'Attested from one source system', 'Screening, early ranking'],
    ['A2', 'Two independent sources agree', 'Mandate scoring, full weight'], ['A3', 'Reconciled to cash on the payment rails', 'Credit boxes: indicative terms'],
    ['A4', 'A3 plus a bond or surety', 'Firm term sheets, held pairs'], ['A5', 'A4 plus a signed act or a policy', 'Settlement, LP reporting']];
  const ry = i => 850 - i * 92;
  scene(T('n11') - .5, END('n11') + .9, `
    <div data-k="h" class="abs h2" style="left:160px;top:140px">Confidence becomes a level a counterparty can require</div>
    <div data-k="hd" class="abs" style="left:160px;top:${ry(5) - 56}px;width:1060px"><span class="lbl" style="position:absolute;left:0">Level</span><span class="lbl" style="position:absolute;left:120px">What sits behind the value</span><span class="lbl" style="position:absolute;left:680px">Who accepts it</span></div>
    ${LV.map((l, i) => `<div data-k="lv${i}" class="abs" style="left:160px;top:${ry(i)}px;width:1060px;height:80px;border-radius:10px">
      <div class="abs rule" style="left:0;right:0;top:0"></div>
      <div data-k="lc${i}" class="abs big" style="left:0;top:18px;font-size:44px">${l[0]}</div>
      <div class="abs h3" style="left:120px;top:24px;font-size:25px">${l[1]}</div>
      <div class="abs lbl" style="left:680px;top:32px;font-size:13px">${l[2]}</div></div>`).join('')}
    <div data-k="pf" class="abs lbl y" style="left:1330px;top:${ry(5) - 56}px">Per field, not per asset</div>
    <svg class="full">
      <path data-k="an" pathLength="1" d="M1318 ${ry(3) + 40} H1236" fill="none" stroke="${Y}" stroke-width="2.5"/>
      <path data-k="ac" pathLength="1" d="M1318 ${ry(1) + 40} H1236" fill="none" stroke="${DIM}" stroke-width="2"/>
    </svg>
    <div data-k="fn" class="card hi" style="left:1330px;top:${ry(3) + 4}px;width:380px;height:72px"><div class="abs h3" style="left:22px;top:18px;font-size:26px">NOI</div><div class="abs lbl y" style="right:22px;top:28px">A3</div></div>
    <div data-k="fc" class="card" style="left:1330px;top:${ry(1) + 4}px;width:380px;height:72px"><div class="abs h3" style="left:22px;top:18px;font-size:26px">Capex</div><div class="abs lbl" style="right:22px;top:28px">A1</div></div>
    <div data-k="car" class="abs" style="left:1330px;top:${ry(4) + 16}px"><div class="chip y" style="font-size:16px">${icon('lock', 16, '#0B0B0C')} Capital at risk</div></div>
    <div data-k="ft" class="foot">Level names are placeholders; the ladder is the point</div>`,
    (t, k) => {
      const t0 = T('n11') - .3;
      show(k.h, t, t0); show(k.hd, t, t0 + .2, 1e9, { dy: 0 }); show(k.ft, t, t0 + .8, 1e9, { dy: 0 });
      const tz = at('n11', 'from A zero'), t5 = at('n11', 'A five');
      LV.forEach((_, i) => show(k['lv' + i], t, t0 + .2 + i * .1, 1e9, { dy: 18 }));
      LV.forEach((_, i) => { const tt = lerp(tz, t5, i / 5); k['lc' + i].style.color = t > tt && t < tt + .5 ? Y : INK; });
      const tf = at('n11', 'field by field');
      show(k.pf, t, tf - .3, 1e9, { dy: 0 });
      show(k.fn, t, tf, 1e9, { dx: 20, dy: 0 }); draw(k.an, P(t, tf + .3, .5));
      show(k.fc, t, tf + .35, 1e9, { dx: 20, dy: 0 }); draw(k.ac, P(t, tf + .65, .5));
      const t4 = at('n11', 'A four');
      const h4 = P(t, t4, .5);
      k.lv4.style.background = `rgba(255,190,6,${.1 * h4})`; k.lc4.style.color = h4 > .5 ? Y : k.lc4.style.color;
      show(k.car, t, at('n11', 'capital at risk'), 1e9, { dx: 16, dy: 0 });
    });
}
