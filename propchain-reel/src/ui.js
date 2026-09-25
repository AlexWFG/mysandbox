// Typography + HUD layer. Everything is a pure function of t.
import { clamp, range, smooth, easeOutQuint, easeInCubic, easeOutExpo, easeInOutCubic, window01 } from './util.js';

const CHECK = '<svg viewBox="0 0 26 26"><path d="M7.5 13.5l3.6 3.6 7.4-8" fill="none" stroke="#FFBE06" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" pathLength="1"/></svg>';

const els = {};
const cards = [];
let root;

function h(tag, cls, html, parent) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (html != null) e.innerHTML = html;
  (parent || root).appendChild(e);
  return e;
}
function words(text, cls = '') {
  return text.split(/(\s+)/).filter(Boolean).map(w => /^\s+$/.test(w) ? w : `<span class="w ${cls}">${w}</span>`).join('');
}

// ----------------------------------------------------------------- cards
function card(o) {
  const c = h('div', 'card fx');
  if (o.style) Object.assign(c.style, o.style);
  const rec = { ...o, el: c, words: [], subWords: [] };
  if (o.eyebrow) {
    const eb = h('div', 'eyebrow', `<span class="bar"></span><span class="t"></span>`, c);
    rec.eb = eb; rec.ebBar = eb.querySelector('.bar'); rec.ebText = eb.querySelector('.t');
  }
  const hd = h('div', o.size || 'h1', null, c);
  o.lines.forEach((ln, li) => {
    const l = h('span', 'line', null, hd);
    const inner = h('span', null, ln.segs.map(([txt, cls]) => words(txt, cls)).join(''), l);
    const t0 = ln.t ?? (o.tin + 0.1 + li * 0.18);
    inner.querySelectorAll('.w').forEach((w, j) => rec.words.push({ el: w, t: t0 + j * (o.stagger ?? 0.065) }));
  });
  if (o.sub) {
    const s = h('div', 'sub', words(o.sub), c);
    const t0 = o.subT ?? (o.tin + 0.55);
    s.querySelectorAll('.w').forEach((w, j) => rec.subWords.push({ el: w, t: t0 + j * 0.028 }));
  }
  cards.push(rec);
  return rec;
}

function animCard(c, t) {
  const vis = t > c.tin - 0.05 && t < c.tout + 0.05;
  c.el.style.display = vis ? 'block' : 'none';
  if (!vis) return;
  const x = easeInCubic(range(t, c.tout - 0.42, c.tout));
  c.el.style.opacity = 1 - x;
  c.el.style.transform = `translateY(${-x * 26}px)`;
  c.el.style.filter = x > 0.001 ? `blur(${x * 9}px)` : 'none';
  if (c.eb) {
    const e = easeOutQuint(range(t, c.tin, c.tin + 0.6));
    c.ebBar.style.transform = `scaleX(${e})`;
    const n = Math.floor(clamp((t - c.tin - 0.08) / 0.5) * c.eyebrow.length);
    c.ebText.textContent = c.eyebrow.slice(0, n) + (n < c.eyebrow.length && n > 0 ? '_' : '');
  }
  for (const w of c.words) {
    const e = easeOutQuint(range(t, w.t, w.t + 0.85));
    w.el.style.opacity = e;
    w.el.style.transform = `translateY(${(1 - e) * 62}%)`;
    w.el.style.filter = e < 0.999 ? `blur(${(1 - e) * 12}px)` : 'none';
  }
  for (const w of c.subWords) {
    const e = easeOutQuint(range(t, w.t, w.t + 0.7));
    w.el.style.opacity = e;
    w.el.style.transform = `translateY(${(1 - e) * 14}px)`;
    w.el.style.filter = e < 0.999 ? `blur(${(1 - e) * 6}px)` : 'none';
  }
}

// ----------------------------------------------------------------- build
export function buildUI(r) {
  root = r;
  // legibility shade behind lower-left type
  els.shade = h('div', 'abs');
  Object.assign(els.shade.style, { inset: '0', background: 'radial-gradient(120% 90% at 0% 100%, rgba(5,5,5,.78) 0%, rgba(5,5,5,.45) 38%, rgba(5,5,5,0) 70%)' });

  // 1 — the asset
  card({ tin: 0.7, tout: 3.45, eyebrow: 'Real estate', lines: [{ segs: [['$', 'num'], ['0', 'num cnt'], [' trillion.', '']] }], sub: 'The largest asset class on earth.', subT: 1.5 });
  // 2 — the reality
  card({ tin: 4.35, tout: 7.75, eyebrow: 'The reality', size: 'h2',
    lines: [{ segs: [['Still run on PDFs,', '']] }, { segs: [['spreadsheets and paper.', '']] }],
    sub: 'Every deal re-verifies the asset from scratch. Three to six months, every time.', subT: 5.2 });
  // 3 — the thesis
  card({ tin: 8.05, tout: 10.85, size: 'h2',
    lines: [{ segs: [['Markets are going autonomous.', '']], t: 8.1 }, { segs: [['But AI can’t read real estate.', 'yl']], t: 9.15 }] });
  // 4-6 — the stack
  card({ tin: 11.25, tout: 13.5, eyebrow: 'Layer 01 · Structuring engine', lines: [{ segs: [['Structured.', '']] }],
    sub: 'Every source, one machine-readable schema, with full lineage.' });
  card({ tin: 13.75, tout: 16.0, eyebrow: 'Layer 02 · Validation engine', lines: [{ segs: [['Attested.', '']] }],
    sub: 'Origin, permission and state, provable by anyone, on chain.' });
  card({ tin: 16.25, tout: 18.5, eyebrow: 'Layer 03 · Know your agent', lines: [{ segs: [['Agent-ready.', '']] }],
    sub: 'Every AI agent identified, permissioned and audited.' });
  // 7 — the market
  card({ tin: 18.9, tout: 22.85, eyebrow: 'The autonomous capital market', size: 'h2', style: { bottom: '236px' },
    lines: [{ segs: [['Capital at the ', ''], ['speed of software.', 'yl']] }] });

  // proofs ticker
  els.proofs = h('div', 'abs', null);
  els.proofs.id = 'proofs';
  els.proofRows = ['Proof of ingestion', 'Proof of permission', 'Proof of state', 'Proof of agency'].map((name, i) => {
    const row = h('div', 'proof', `<div class="ck">${CHECK}</div><div><div class="pt">${name.toUpperCase()}</div><div class="ph"></div></div>`, els.proofs);
    const hashes = ['0x9f2c41e0…b7e41a', '0x31d7aa92…04c9fe', '0xe80b5c13…9a2d77', '0x5a6f0e8d…c13b20'];
    return { row, path: row.querySelector('path'), ph: row.querySelector('.ph'), hash: 'anchored · ' + hashes[i], t: 14.05 + i * 0.36 };
  });

  // agent tags
  els.tagSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  els.tagSvg.setAttribute('width', 1920); els.tagSvg.setAttribute('height', 1080);
  els.tagSvg.style.position = 'absolute'; els.tagSvg.style.inset = '0';
  root.appendChild(els.tagSvg);
  const tagText = [
    ['AGENT 0x3F·VALUATION', 'KYA', 'PERMISSIONED'],
    ['AGENT 0xA1·DILIGENCE', 'KYA', 'AUDIT TRAIL ON'],
    ['AGENT 0x7C·LENDER', 'KYA', 'MANDATE FIT'],
  ];
  els.tags = tagText.map(([a, b, c], i) => {
    const el = h('div', 'tag abs', `${a}<br><b>✓ ${b}</b> · ${c}`);
    el.innerHTML = `${a}<br><b>${b} VERIFIED</b> · ${c}`;
    const ln = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
    ln.setAttribute('fill', 'none'); ln.setAttribute('stroke', 'rgba(255,190,6,.75)'); ln.setAttribute('stroke-width', '1.2');
    const dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    dot.setAttribute('r', '5'); dot.setAttribute('fill', 'none'); dot.setAttribute('stroke', '#FFBE06'); dot.setAttribute('stroke-width', '1.5');
    els.tagSvg.append(ln, dot);
    return { el, ln, dot, t: 16.55 + i * 0.28, dx: [70, 90, -330][i], dy: [-110, 80, -90][i] };
  });

  // settlement rail
  els.rail = h('div', 'abs', `<div class="track"></div><div class="fill"></div>`);
  els.rail.id = 'rail';
  els.railFill = els.rail.querySelector('.fill');
  els.steps = ['List', 'Diligence', 'Match', 'Finance', 'Settle'].map((s, i) => {
    const st = h('div', 'step', `<div class="dot"></div><div class="lbl"><span class="idx">0${i + 1}</span>${s.toUpperCase()}</div>`, els.rail);
    st.style.left = `${i * 25}%`;
    if (i === 4) st.querySelector('.lbl').style.cssText += 'left:auto;right:-7px;';
    return { el: st, dot: st.querySelector('.dot'), lbl: st.querySelector('.lbl'), t: 19.2 + i * 0.7 };
  });

  // stats
  els.stats = h('div', 'abs');
  els.stats.id = 'stats';
  els.statList = [
    { v: 11000, fmt: n => n.toLocaleString('en') + '<i>+</i>', k: 'Units on platform' },
    { v: 90, fmt: n => '€' + n + '<i>B+</i>', k: 'Asset value under<br>data management' },
    { v: 4, fmt: n => n + '', k: 'Proofs live on<br>the validation engine' },
  ].map((s, i) => {
    const el = h('div', 'stat', `<div class="v"></div><div class="k">${s.k}</div>`, els.stats);
    return { ...s, el, vEl: el.querySelector('.v'), t: 23.0 + i * 0.2 };
  });
  els.statEb = h('div', 'eyebrow abs', `<span class="bar"></span><span class="t"></span>`);
  Object.assign(els.statEb.style, { left: '132px', bottom: '330px' });

  // brand bug + chapter marker
  els.bug = h('div', 'abs', `<img src="assets/logo-white.svg">`);
  els.bug.id = 'bug';
  els.chap = h('div', 'abs');
  els.chap.id = 'chap';

  // end card
  els.endShade = h('div', 'abs');
  Object.assign(els.endShade.style, { inset: '0', background: 'radial-gradient(60% 60% at 50% 50%, rgba(4,4,4,.72) 0%, rgba(4,4,4,.35) 60%, rgba(4,4,4,0) 100%)' });
  els.end = h('div', 'abs', `
    <div id="endlogo"><img class="word" src="assets/logo-white.svg"><div class="sweep"></div></div>
    <div id="endtag">${words('Structuring real estate for the autonomous era.')}</div>
    <div id="endtri">Machine-readable <b>·</b> Attested <b>·</b> Agent-ready</div>`);
  els.end.id = 'end';
  els.endLogo = els.end.querySelector('#endlogo');
  els.endWord = els.end.querySelector('.word');
  els.endSweep = els.end.querySelector('.sweep');
  Object.assign(els.endSweep.style, { position: 'absolute', top: '-30px', bottom: '-30px', width: '160px', background: 'linear-gradient(90deg, rgba(255,190,6,0), rgba(255,220,120,.55), rgba(255,190,6,0))', mixBlendMode: 'screen', filter: 'blur(6px)' });
  els.endTagWords = [...els.end.querySelectorAll('#endtag .w')];
  els.endTri = els.end.querySelector('#endtri');
}

// ----------------------------------------------------------------- update
export function updateUI(t, ctx) {
  els.shade.style.opacity = 0.9 * window01(t, 0.3, 11.0, 0.8, 0.5) + 0.75 * window01(t, 11.0, 24.6, 0.5, 0.6);
  for (const c of cards) animCard(c, t);
  // count-up in card 1
  const cnt = cards[0].el.querySelector('.cnt');
  if (cnt) cnt.textContent = String(Math.round(380 * easeOutExpo(range(t, 0.9, 2.3))));

  // proofs
  const pv = window01(t, 13.9, 16.05, 0.3, 0.4);
  els.proofs.style.display = pv > 0 ? 'block' : 'none';
  els.proofs.style.opacity = pv;
  els.proofs.style.filter = pv < 0.999 ? `blur(${(1 - pv) * 8}px)` : 'none';
  for (const p of els.proofRows) {
    const e = easeOutQuint(range(t, p.t, p.t + 0.5));
    p.row.style.opacity = 0.25 + 0.75 * e;
    p.row.style.transform = `translateX(${(1 - e) * 30}px)`;
    const ck = clamp((t - p.t - 0.15) / 0.3);
    p.path.style.strokeDasharray = '1'; p.path.style.strokeDashoffset = String(1 - ck);
    p.row.querySelector('.ck').style.background = ck >= 1 ? 'rgba(255,190,6,.14)' : 'transparent';
    const n = Math.floor(clamp((t - p.t - 0.2) / 0.45) * p.hash.length);
    p.ph.textContent = p.hash.slice(0, n) || ' ';
  }

  // agent tags
  const P = ctx.projected.agents;
  els.tags.forEach((g, i) => {
    const v = window01(t, g.t, 18.45, 0.4, 0.35);
    const p = P[i];
    if (!p || v <= 0 || p.z > 1) { g.el.style.display = 'none'; g.ln.setAttribute('points', ''); g.dot.setAttribute('r', 0); return; }
    const x = (p.x * 0.5 + 0.5) * 1920, y = (1 - (p.y * 0.5 + 0.5)) * 1080;
    const e = easeOutQuint(range(t, g.t, g.t + 0.6));
    const tx = x + g.dx, ty = y + g.dy;
    g.el.style.display = 'block';
    g.el.style.left = `${tx}px`; g.el.style.top = `${ty - 24}px`;
    g.el.style.opacity = v; g.el.style.transform = `scale(${0.9 + 0.1 * e})`;
    const ex = g.dx < 0 ? tx + 300 : tx;
    const mx = x + (ex - x) * 0.35;
    g.ln.setAttribute('points', `${x},${y} ${mx},${ty + 24} ${x + (ex - x) * e},${ty + 24}`);
    g.ln.style.opacity = v;
    g.dot.setAttribute('cx', x); g.dot.setAttribute('cy', y); g.dot.setAttribute('r', 7 + 5 * (1 - e)); g.dot.style.opacity = v;
  });

  // rail
  const rv = window01(t, 18.95, 22.9, 0.4, 0.45);
  els.rail.style.display = rv > 0 ? 'block' : 'none';
  els.rail.style.opacity = rv;
  const fillP = clamp((t - 19.2) / (2.8)) ;
  els.railFill.style.width = `${easeInOutCubic(fillP) * 100}%`;
  for (const s of els.steps) {
    const on = smooth(range(t, s.t, s.t + 0.2));
    s.dot.style.background = on > 0.5 ? '#FFBE06' : '#0b0b0b';
    s.dot.style.borderColor = on > 0.5 ? '#FFBE06' : 'rgba(244,242,236,.35)';
    s.dot.style.boxShadow = on > 0.5 ? `0 0 ${10 + 30 * Math.exp(-(t - s.t) * 3)}px rgba(255,190,6,.9)` : 'none';
    s.dot.style.transform = `scale(${1 + 0.8 * Math.exp(-Math.max(0, t - s.t) * 6) * (t > s.t ? 1 : 0)})`;
    s.lbl.style.color = on > 0.5 ? '#F4F2EC' : 'rgba(244,242,236,.35)';
  }

  // stats
  const sv = window01(t, 22.95, 24.95, 0.3, 0.4);
  els.stats.style.display = sv > 0 ? 'flex' : 'none';
  els.stats.style.opacity = sv;
  els.stats.style.filter = t > 24.5 ? `blur(${range(t, 24.55, 24.95) * 9}px)` : 'none';
  for (const s of els.statList) {
    const e = easeOutQuint(range(t, s.t, s.t + 0.7));
    const n = Math.round(s.v * easeOutExpo(range(t, s.t, s.t + 1.1)));
    s.vEl.innerHTML = s.fmt(s.v >= 1000 ? Math.round(n / 10) * 10 : n);
    s.el.style.opacity = e; s.el.style.transform = `translateY(${(1 - e) * 30}px)`;
  }
  const seb = 'Live in production';
  els.statEb.style.display = sv > 0 ? 'block' : 'none';
  els.statEb.style.opacity = sv;
  els.statEb.querySelector('.bar').style.transform = `scaleX(${easeOutQuint(range(t, 22.95, 23.5))})`;
  els.statEb.querySelector('.t').textContent = seb.slice(0, Math.floor(clamp((t - 23.0) / 0.45) * seb.length)).toUpperCase();

  // bug + chapter
  const bv = window01(t, 11.2, 24.7, 0.5, 0.5);
  els.bug.style.opacity = bv * 0.92;
  const chapters = [[11.25, '01', 'STRUCTURED'], [13.75, '02', 'ATTESTED'], [16.25, '03', 'AGENT-READY'], [18.9, '', 'AUTONOMOUS MARKET']];
  let ch = null; for (const c of chapters) if (t >= c[0]) ch = c;
  if (ch && t < 24.7) {
    const txt = ch[2]; const n = Math.floor(clamp((t - ch[0]) / 0.4) * txt.length);
    els.chap.innerHTML = (ch[1] ? `<b>${ch[1]}</b> / 03 &nbsp;&nbsp;` : `<b>●</b> &nbsp;`) + txt.slice(0, n);
    els.chap.style.opacity = bv;
  } else els.chap.style.opacity = 0;

  // end card
  const endV = smooth(range(t, 24.8, 25.7));
  els.endShade.style.opacity = endV;
  els.end.style.display = t > 25.0 ? 'flex' : 'none';
  if (t > 25.0) {
    const lw = easeInOutCubic(range(t, 25.2, 26.25));
    const le = easeOutQuint(range(t, 25.1, 26.3));
    els.endLogo.style.clipPath = `inset(-40px ${(1 - lw) * 100}% -40px -40px)`;
    els.endLogo.style.transform = `scale(${1.06 - 0.06 * le})`;
    els.endLogo.style.filter = `blur(${(1 - le) * 10}px) drop-shadow(0 0 ${24 * (1 - range(t, 26.2, 27.5)) + 6}px rgba(255,190,6,.35))`;
    els.endLogo.style.opacity = le;
    els.endSweep.style.left = `${-200 + 1150 * easeInOutCubic(range(t, 26.1, 27.3))}px`;
    els.endSweep.style.opacity = window01(t, 26.1, 27.3, 0.2, 0.3);
    els.endTagWords.forEach((w, j) => {
      const s = 26.25 + j * 0.06, e = easeOutQuint(range(t, s, s + 0.8));
      w.style.opacity = e; w.style.transform = `translateY(${(1 - e) * 22}px)`; w.style.filter = e < 0.999 ? `blur(${(1 - e) * 8}px)` : 'none';
    });
    const te = easeOutQuint(range(t, 27.0, 27.8));
    els.endTri.style.opacity = te; els.endTri.style.letterSpacing = `${0.3 + (1 - te) * 0.25}em`;
  }
}
