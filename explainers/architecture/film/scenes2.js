// Scenes 5–10: two quorums, the network, disclosure, delegation, the enclave, the deal end to end.
'use strict';

function buildScenes2() {
  // ================================================================ 5 · TWO QUORUMS
  chapter(101.6, 123.9, '04', 'Two quorums');
  {
    const sc = new Scene(101.6, 114.2);
    const s = sc.svg(), t15 = V('15');
    const tC = Wd('15', 'Consensus orders'), tA = Wd('15', 'Attestation verifies');
    const hd = T(sc.el, 0, 150, 'h2 center', '<span class="c1">Consensus orders.</span> <span class="c2">Attestation verifies.</span>', 1920);
    appear(sc, hd.children[0], tC - .2, { dy: 16 }); appear(sc, hd.children[1], tA - .2, { dy: 16 });
    draw(sc, P(s, 'M960 280 V960'), t15 + .2, 1.0);
    const side = (x0, t0, label, q, rows) => {
      appear(sc, T(sc.el, x0, 290, 'mono y', label), t0);
      appear(sc, T(sc.el, x0, 326, 'h3', q, 760), t0 + .3);
      rows.forEach(([k, v], i) => { const r = T(sc.el, x0, 780 + i * 54, 'qrow', `<span class="mono sm dim">${k}</span><span>${v}</span>`, 760); appear(sc, r, t0 + 1.2 + i * .45, { dy: 12 }); });
    };
    side(160, tC, 'Consensus quorum', 'In what order did things happen, finally?', [['Who votes', 'Validator nodes'], ['Writes', 'Blocks'], ['Fails by', 'Fork, halt']]);
    side(1040, tA, 'Attestation quorum', 'Is this fact true enough to act on?', [['Who votes', 'Independent sources of the fact'], ['Writes', 'Signatures over a commitment, and a level'], ['Fails by', 'False fact with lineage']]);
    // consensus: validators vote, blocks append in order
    const vx = [230, 410, 590, 770];
    vx.forEach((x, i) => { const n = el('div', 'a srcnode', sc.el); pos(n, x - 32, 440, 64, 64); icon('server', 28, n); appear(sc, n, tC + .3 + i * .15, { dy: -12 }); });
    for (let b = 0; b < 6; b++) {
      const x = 160 + b * 118, tb = tC + 1.2 + b * .75;
      const bl = el('div', 'a block', sc.el, `#${1041 + b}`); pos(bl, x, 600, 100, 66); appear(sc, bl, tb, { dx: 30, dy: 0, blur: 4 });
      if (b) draw(sc, P(s, `M${x - 18} 633 H${x}`), tb, .3);
      flag(sc, bl, 'lit', tb, tb + .75);
      vx.forEach((vv, i) => pulse(sc, s, P(s, `M${vv} 508 C${vv} 560 ${x + 50} 560 ${x + 50} 598`, '', { fill: 'none' }), tb - .55, .55, { r: 3, len: .2, width: 2 }));
    }
    // attestation: sources sign one commitment, ring fills, level
    const RX = 1400, RY = 620;
    const root = el('div', 'a root', sc.el, 'ROOT'); pos(root, RX - 34, RY - 34, 68, 68); appear(sc, root, tA + .2, { dy: 0, scale: .3, blur: 0 });
    const ring = sv('circle', { cx: RX, cy: RY, r: 54, class: 'ln y', 'stroke-width': 3, transform: `rotate(-90 ${RX} ${RY})`, pathLength: 1 }, s);
    [1180, 1400, 1620].forEach((x, i) => {
      const n = el('div', 'a srcnode', sc.el); pos(n, x - 32, 440, 64, 64); icon('signature', 28, n, 'y'); appear(sc, n, tA + .4 + i * .2, { dy: -12 });
      const d = `M${x} 508 C${x} 560 ${RX + (i - 1) * 30} 540 ${RX + (i - 1) * 24} ${RY - 58}`;
      draw(sc, P(s, d), tA + .6 + i * .2, .6);
      pulse(sc, s, P(s, d, '', { fill: 'none' }), tA + 1.2 + i * .6, .8);
    });
    sc.on(t => { const k = Math.min(3, Math.max(0, Math.floor((t - (tA + 2.0)) / .6) + 1)); ring.style.strokeDasharray = `${k / 3} 1`; ring.style.opacity = k ? 1 : 0; });
    const lv = el('div', 'a pill solid', sc.el, 'Level'); pos(lv, RX + 80, RY - 20); appear(sc, lv, tA + 3.8, { dx: -14, dy: 0 });
  }
  // ---------------------------------------------------------------- the network
  {
    const sc = new Scene(114.0, 124.2);
    const s = sc.svg(), t16 = V('16'), C = [960, 470], R = 190;
    appear(sc, T(sc.el, 0, 150, 'h2 center', 'A permissioned network of named validators', 1920), t16, { dy: 16 });
    const names = [['stamp', 'Notaries', 'notaries'], ['search-check', 'Auditors', 'auditors'], ['vault', 'Depositaries', 'auditors'], ['landmark', 'Banks', 'banks']];
    const ang = [-150, -30, 30, 150].map(a => a * Math.PI / 180);
    const P4 = ang.map(a => [C[0] + Math.cos(a) * R * 2.3, C[1] + Math.sin(a) * R]);
    for (let i = 0; i < 4; i++) for (let j = i + 1; j < 4; j++) draw(sc, P(s, `M${P4[i][0]} ${P4[i][1]} L${P4[j][0]} ${P4[j][1]}`), t16 + 1.8 + (i + j) * .1, .8);
    names.forEach(([ic, nm, w], i) => {
      const [x, y] = P4[i]; const c = el('div', 'a card vnode', sc.el); pos(c, x - 120, y - 44, 240, 88);
      icon(ic, 32, c, 'y'); el('span', 'nodet', c, nm);
      appear(sc, c, Wd('16', w) + (i === 2 ? .5 : 0), { dy: 0, scale: .85 });
    });
    const hub = el('div', 'a pill y', sc.el, 'Validators · consensus'); pos(hub, C[0] - 130, C[1] - 18); hub.style.background = '#131312'; appear(sc, hub, t16 + 2.2, { dy: 0 });
    // public anchor
    const tP = Wd('16', 'public chain');
    const pc = el('div', 'a pubchain', sc.el); pos(pc, 160, 820, 1600, 70);
    el('span', 'mono dim', pc, 'Public chain');
    for (let k = 0; k < 12; k++) { const b = el('span', 'pblk', pc); }
    appear(sc, pc, tP - .4, { dy: 30 });
    sc.on(t => { pc.style.backgroundPosition = `${-(t * 30) % 118}px 0`; });
    const ad = `M${C[0]} ${C[1] + 30} V812`;
    draw(sc, P(s, ad, 'ln dash'), tP, .6);
    pulse(sc, s, P(s, ad, '', { fill: 'none' }), tP + .3, 1.0, { repeat: 4, period: 1.6 });
    const anc = T(sc.el, C[0] + 30, 720, 'mono sm y', 'periodic roots anchored', 400); appear(sc, anc, tP + .4, { dy: 0 });
    const l = T(sc.el, 160, 930, 'mono sm dim', 'Accountability · validators a risk committee can name', 760); appear(sc, l, tP + 1.4, { dy: 10 });
    const r = T(sc.el, 1000, 930, 'mono sm dim', 'Immutability · no consortium member controls the anchor', 760); r.style.textAlign = 'right'; appear(sc, r, tP + 1.9, { dy: 10 });
  }

  // ================================================================ 6 · DISCLOSURE
  chapter(123.9, 142.3, '05', 'Disclosure');
  {
    const sc = new Scene(123.9, 142.6);
    const s = sc.svg(), t17 = V('17'), t18 = V('18');
    appear(sc, T(sc.el, 0, 140, 'h2 center', 'Prove a field without publishing it', 1920), t17, { dy: 16 });
    // seller vault
    const v = el('div', 'a card', sc.el); pos(v, 160, 290, 470, 330);
    el('div', 'mono sm y', v, 'Vault · seller').style.cssText = 'padding:20px 22px 4px';
    const f = [['Tenant', '●●●●●●'], ['Rent', '●●●●●●'], ['NOI', '●●●●●●']].map(([k, val]) => {
      const r = el('div', 'frow', v); el('span', 'fk', r, k); el('span', 'fv', r, val); icon('lock', 24, r, 'dim'); return r; });
    appear(sc, v, t17 - .2, { dx: -30, dy: 0 });
    // ledger with the root
    const rl = rail(sc.el, s, 160, 1760, 900, 'Ledger', ''); appear(sc, rl, t17, { dy: 20 });
    const root = el('div', 'a root', sc.el, 'ROOT'); pos(root, 925, 865, 70, 70); appear(sc, root, t17 + .3, { dy: 0, scale: .3, blur: 0 });
    draw(sc, P(s, 'M395 620 C395 760 700 900 925 900', 'ln dash'), t17 + .4, 1.0);
    // buyer's agent
    const tg = Wd('17', 'grant:'), tc = Wd('17', 'checks'), tl = Wd('17', 'logged');
    const ag = el('div', 'a card', sc.el); pos(ag, 1240, 260, 520, 240);
    const ah = el('div', 'nodehd', ag); el('span', 'mono sm y', ah, "Buyer's agent"); icon('bot', 32, ah, 'y');
    const ar = el('div', 'frow', ag); el('span', 'fk', ar, 'Rent'); el('span', 'fv mono lc', ar, 'value + salt');
    const hv = el('div', 'mono sm lc dim', ag); hv.style.cssText = 'padding:14px 22px 0';
    appear(sc, ag, t17 + .2, { dx: 30, dy: 0 });
    appear(sc, ar, tg + 1.4, { dy: 0, dx: -12 });
    sc.on(t => { hv.innerHTML = t > tc - .3 ? 'hash(value + salt) = <span class="y">4b70·18d2·e5a9</span>' : ''; });
    flag(sc, f[1], 'lit', tg, 1e9);
    const tk = el('div', 'a pill y tok2', sc.el, 'GRANT · rent · value + salt'); appear(sc, tk, tg, { dy: 0, blur: 0, out: tg + 1.5, outDur: .3 });
    follow(sc, tk, s, 'M500 420 C800 300 1000 330 1370 380', tg, 1.4, { w: 300, h: 36 });
    const chk = 'M1500 500 C1500 700 1200 880 995 900';
    draw(sc, P(s, chk, 'ln y'), tc, .9);
    pulse(sc, s, P(s, chk, '', { fill: 'none' }), tc, 1.0, { repeat: 2, period: 1.3 });
    const ok = el('div', 'a pill y', sc.el, '✓ matches the root on chain'); pos(ok, 1080, 760); appear(sc, ok, tc + .9, { dy: 10 });
    // the grant log
    const lg = el('div', 'a logrow', sc.el); pos(lg, 160, 670, 900, 56);
    lg.innerHTML = '<span class="mono sm y">Grant log</span><span>who <b>buyer\'s agent</b></span><span>what <b>rent</b></span><span>when <b>timestamped</b></span><span>under <b>seller\'s permission</b></span>';
    appear(sc, lg, tl, { dy: 16, out: t18 - .2 });
    // range proof: NOI >= X, no disclosure
    const tr = Wd('18', 'range proof'), tx = Wd('18', 'at least');
    sc.on(t => { ok.style.display = t > t18 - .2 ? 'none' : ''; });
    const cb = el('div', 'a card', sc.el); pos(cb, 1240, 540, 520, 180);
    const ch = el('div', 'nodehd', cb); el('span', 'mono sm y', ch, 'Credit box'); icon('briefcase', 30, ch, 'y');
    el('div', 'h3', cb, 'needs NOI ≥ X').style.cssText = 'padding:14px 22px 0';
    const res = el('div', 'mono sm lc', cb); res.style.cssText = 'padding:12px 22px 0';
    appear(sc, cb, t18, { dx: 30, dy: 0 });
    sc.on(t => { res.innerHTML = t > tx + 1.6 ? '<span class="y">✓ NOI ≥ X · true</span>&nbsp;&nbsp;<span class="dim">NOI itself: never disclosed</span>' : ''; });
    flag(sc, f[2], 'lit', tr - .2, 1e9);
    const zk = el('div', 'a pill solid', sc.el, 'ZK range proof'); appear(sc, zk, tr, { dy: 0, blur: 0, out: tx + 1.5, outDur: .3 });
    follow(sc, zk, s, 'M500 560 C800 640 1000 660 1140 630', tr, 1.8, { w: 190, h: 36 });
    const nd = T(sc.el, 160, 640, 'mono sm', '<span class="y">●</span> NOI stays locked · the proof answers the question, not the value', 900); appear(sc, nd, tx + .4, { dy: 10 });
  }

  // ================================================================ 7 · THE DEAL: stock, delegation
  chapter(142.3, 177.5, '06', 'People, agents and the deal');
  {
    const sc = new Scene(142.3, 145.8, { fadeIn: .4, fadeOut: .5 });
    stock(sc, 'sign', 142.3, 145.8, { from: .5, zoom: [1.03, 1.09] });
    appear(sc, T(sc.el, 160, 800, 'h2', 'Every action traces to a person.', 1400), 142.7);
  }
  {
    const sc = new Scene(145.4, 155.3);
    const s = sc.svg(), t19 = V('19');
    appear(sc, T(sc.el, 0, 150, 'h3 center dim', 'A chain of scopes, from institution to action', 1920), 145.6, { dy: 12 });
    const nodes = [['building-2', 'Institution', 'verified legal entity · root of every credential', 'institution'],
      ['user', 'Principal', 'a named person with authority to act and delegate', 'principal'],
      ['id-card', 'Agent credential', 'scope · limits · expiry · revocable · signed by the principal', 'agent credential'],
      ['pen-line', 'Action', 'signed by the agent key · checked against scope · logged', 'action.']];
    nodes.forEach(([ic, a, b, w], i) => {
      const x = 130 + i * 430, t = Wd('19', w);
      const c = el('div', 'a card', sc.el); pos(c, x, 290, 370, 230);
      const hd = el('div', 'nodehd', c); el('span', 'mono sm y', hd, '0' + (i + 1)); icon(ic, 38, hd, i === 2 ? 'y' : '');
      el('div', 'nodet', c, a); el('div', 'nodes', c, b);
      appear(sc, c, t, { dx: -24, dy: 0 }); flag(sc, c, 'lit', t, t + 1.0);
      if (i) { const d = `M${x - 58} 405 H${x}`; draw(sc, P(s, d, 'ln y'), t - .2, .4); pulse(sc, s, P(s, d, '', { fill: 'none' }), t - .2, .5, { len: .5 }); }
    });
    // the binding act: two signatures
    const tp = Wd('19', 'Agents prepare'), tb = Wd('19', "principal's signature");
    const act = el('div', 'a card', sc.el); pos(act, 560, 610, 800, 220);
    el('div', 'mono sm y', act, 'Anything that binds').style.cssText = 'padding:22px 26px 4px';
    el('div', 'h3', act, 'Firm quote · bid · execution').style.cssText = 'padding:4px 26px 14px';
    const sigs = el('div', 'sigs', act);
    const s1 = el('span', 'pill', sigs, '✓ agent key · prepares'), s2 = el('span', 'pill solid', sigs, '✓ principal · commits');
    appear(sc, act, tp - .3, { dy: 20 }); appear(sc, s1, tp + .4, { dy: 0, dx: -10 }); appear(sc, s2, tb, { dy: 0, dx: -10, scale: .8 });
    const pa = T(sc.el, 0, 890, 'mono sm dim center', 'The whole chain is on the audit log · Proof of Agency', 1920); appear(sc, pa, tb + .8, { dy: 8 });
  }

  // ================================================================ 8 · THE ENCLAVE
  {
    const sc = new Scene(155.0, 163.7);
    const s = sc.svg(), t20 = V('20');
    appear(sc, T(sc.el, 0, 150, 'h2 center', 'Matching, inside an attested enclave', 1920), t20, { dy: 16 });
    const bx = el('div', 'a enclave', sc.el); pos(bx, 700, 330, 520, 330);
    el('div', 'mono sm y', bx, 'Trusted execution environment').style.cssText = 'position:absolute;left:24px;top:-11px;background:#111113;padding:0 10px';
    const inner = el('div', 'center', bx); inner.style.paddingTop = '58px'; icon('cpu', 64, inner, 'y').style.margin = '0 auto';
    el('div', 'h3', inner, 'Matching').style.marginTop = '14px';
    el('div', 'mono sm dim lc', inner, 'books · scoring · pair quotes · deferred acceptance').style.marginTop = '10px';
    appear(sc, bx, t20 + .2, { dy: 0, scale: .9 });
    const tin = Wd('20', 'roots in'), tout = Wd('20', 'a root out'), tdet = Wd('20', 'deterministically');
    ['Mandates root', 'Assets root', 'Credit boxes root'].forEach((nm, i) => {
      const y = 390 + i * 100; const p = el('div', 'a pill y tok3', sc.el, '# ' + nm); pos(p, 250, y - 18, 290, 36);
      appear(sc, p, tin - .4 + i * .15, { dx: -20, dy: 0 });
      const d = `M540 ${y} C620 ${y} 620 ${495} 700 495`; draw(sc, P(s, d), tin - .2 + i * .15, .6);
      pulse(sc, s, P(s, d, '', { fill: 'none' }), tin + i * .2, .8, { repeat: 3, period: 2.4 });
    });
    const o = el('div', 'a pill solid tok3', sc.el, '# Stable set root'); pos(o, 1380, 477, 290, 36);
    appear(sc, o, tout + .3, { dx: -20, dy: 0 });
    const d2 = 'M1220 495 H1380'; draw(sc, P(s, d2, 'ln y'), tout, .5); pulse(sc, s, P(s, d2, '', { fill: 'none' }), tout, .6, { repeat: 3, period: 2.2, len: .4 });
    const b1 = el('div', 'a pill', sc.el, 'Same books · same rules · same result'); pos(b1, 740, 700); appear(sc, b1, tdet + .6, { dy: 10 });
    const b2 = el('div', 'a pill y', sc.el, 'Build 7c1e·a94d · attested'); pos(b2, 810, 262); appear(sc, b2, Wd('20', 'attested') + .3, { dy: -10 });
    const b3 = T(sc.el, 0, 800, 'h3 center', 'Neutrality: a property of the machine, not a promise', 1920); appear(sc, b3, Wd('20', 'Neutrality'), { dy: 12 });
    appear(sc, T(sc.el, 0, 880, 'mono sm dim center', 'roots in and out go on chain · any run can be replayed by an auditor', 1920), Wd('20', 'Neutrality') + .8, { dy: 8 });
  }

  // ================================================================ 9 · THE DEAL, END TO END
  {
    const sc = new Scene(163.4, 177.9);
    const s = sc.svg(), t21 = V('21'), RY = 560;
    appear(sc, T(sc.el, 0, 150, 'h2 center', 'One deal, end to end', 1920), t21 - .1, { dy: 16, out: Wd('21', 'regulator') - .6 });
    const rl = rail(sc.el, s, 120, 1800, RY, 'Ledger', ''); appear(sc, rl, t21, { dy: 0, dx: -30 });
    const steps = [['List', 'ingestion · attestation', 'asset root · signatures · level', 'List'],
      ['Diligence', 'record store · agents', 'grants and reads logged · DD root', 'diligence'],
      ['Match', 'matching enclave', 'input roots · output root · enclave attestation', 'match,'],
      ['Finance', 'matching · identity', "term sheet commitment · lender's agent", 'finance'],
      ['Settle', 'settlement · identity', 'escrow lock · DvP of title and cash · tranches', 'settle.'],
      ['Operate', 'ingestion · attestation', 'period roots · level updates · bond release or forfeit', 'operate']];
    steps.forEach(([nm, comp, oc, w], i) => {
      const x = 270 + i * 276, t = Wd('21', w);
      const c = el('div', 'a stepn', sc.el); pos(c, x - 110, 330, 220, 120);
      el('div', 'nodet center', c, nm); el('div', 'mono sm dim center lc', c, comp).style.marginTop = '6px';
      appear(sc, c, t, { dy: -16 }); flag(sc, c, 'lit', t, t + 1.4);
      const d = `M${x} 450 V${RY - 26}`; draw(sc, P(s, d), t + .1, .3);
      pulse(sc, s, P(s, `M${x} 450 V${RY + 60}`, '', { fill: 'none' }), t + .2, .6, { len: .4, repeat: i === 5 ? 3 : 1, period: 1.2 });
      const tok = el('div', 'a mark', sc.el); pos(tok, x - 125, RY + 60, 250, 120);
      tok.innerHTML = `<div class="mono sm y"># ${['a91f', '3c07', 'd5e2', '70b8', 'e4c9', '1f6a'][i]}…</div><div class="mono sm dim lc">${oc}</div>`;
      appear(sc, tok, t + .6, { dy: -12 });
      if (i === 5) { const lp = el('div', 'a pill y', sc.el, '↻ monthly'); pos(lp, x - 62, 270); appear(sc, lp, t + .4, { dy: 8 }); }
    });
    const tR = Wd('21', 'regulator'), tS = Wd('21', 'without seeing');
    const rg = el('div', 'a card regc', sc.el); pos(rg, 460, 800, 1000, 120);
    const rh = el('div', 'nodehd', rg); el('span', 'mono sm y', rh, 'Regulator · auditor · counterparty'); icon('eye', 30, rh, 'y');
    const rr = el('div', 'reglist', rg);
    rr.innerHTML = '<span>✓ every step happened</span><span>✓ in order</span><span>✓ under permission</span><span class="hid">rent ✕</span><span class="hid">mandate ✕</span><span class="hid">price ✕</span>';
    appear(sc, rg, tR - .2, { dy: 20 });
    [...rr.children].forEach((c, i) => appear(sc, c, (i < 3 ? tR + .3 + i * .3 : tS + (i - 3) * .35), { dy: 0, blur: 0 }));
  }
}
