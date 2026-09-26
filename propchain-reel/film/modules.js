// Motion-graphic modules. Each factory returns { t0, t1, el, update(t) }.
// Everything is a pure function of time so any frame renders identically.
import { clamp, range, smooth, lerp, easeOutQuint, easeInCubic, easeOutExpo, easeInOutCubic, easeOutCubic, window01 } from '../src/util.js';

let ROOT;
export function setRoot(r) { ROOT = r; }
export function mk(tag, cls, html, parent) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (html != null) e.innerHTML = html;
  (parent || ROOT).appendChild(e);
  return e;
}
const words = (text, cls = '') => text.split(/(\s+)/).filter(Boolean).map(w => /^\s+$/.test(w) ? w : `<span class="w ${cls}">${w}</span>`).join('');
const CHECK = '<svg viewBox="0 0 30 30"><path d="M8.5 15.5l4.2 4.2 8.6-9.2" fill="none" stroke="#FFBE06" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" pathLength="1"/></svg>';

function vis(el, t, t0, t1, disp = 'block') { const on = t >= t0 - 0.02 && t <= t1 + 0.02; el.style.display = on ? disp : 'none'; return on; }
function exitFx(el, t, t1, dur = 0.45, dy = -24) {
  const x = easeInCubic(range(t, t1 - dur, t1));
  el.style.opacity = 1 - x;
  el.style.filter = x > 0.001 ? `blur(${x * 10}px)` : 'none';
  return x;
}
function wordIn(w, t, s, dur = 0.8, dy = 62, blur = 12) {
  const e = easeOutQuint(range(t, s, s + dur));
  w.style.opacity = e;
  w.style.transform = `translateY(${(1 - e) * dy}%)`;
  w.style.filter = e < 0.999 ? `blur(${(1 - e) * blur}px)` : 'none';
}
const typed = (str, t, t0, dur) => { const n = Math.floor(clamp((t - t0) / dur) * str.length); return str.slice(0, n) + (n > 0 && n < str.length ? '_' : ''); };

// ---------------------------------------------------------------- title card
export function title(o) {
  const el = mk('div', `card ${o.pos === 'c' ? 'pos-c' : o.pos === 'lc' ? 'pos-lc' : 'pos-ll'} shadow`);
  if (o.style) Object.assign(el.style, o.style);
  const W = [], S = [];
  let eb, ebBar, ebT;
  if (o.eyebrow) { eb = mk('div', 'eyebrow', `<span class="bar"></span><span class="t"></span>`, el); ebBar = eb.firstChild; ebT = eb.lastChild; if (o.pos === 'c') ebBar.style.display = 'none'; }
  const hd = mk('div', o.size || 'h-l', null, el);
  o.lines.forEach((ln, li) => {
    const l = mk('span', 'line', null, hd);
    const inner = mk('span', null, ln.segs.map(([tx, c]) => words(tx, c || '')).join(''), l);
    const s0 = ln.t ?? (o.t0 + 0.1 + li * 0.2);
    inner.querySelectorAll('.w').forEach((w, j) => W.push({ w, s: s0 + j * (o.stagger ?? 0.06) }));
  });
  if (o.sub) { const s = mk('div', 'sub', words(o.sub), el); if (o.pos === 'c') s.style.margin = '26px auto 0'; s.querySelectorAll('.w').forEach((w, j) => S.push({ w, s: (o.subT ?? o.t0 + 0.6) + j * 0.025 })); }
  return { el, update(t) {
    if (!vis(el, t, o.t0, o.t1)) return;
    exitFx(el, t, o.t1);
    if (o.pos === 'c') el.style.transform = `translate(-50%, -50%)`;
    if (eb) { ebBar.style.transform = `scaleX(${easeOutQuint(range(t, o.t0, o.t0 + 0.6))})`; ebT.textContent = typed(o.eyebrow, t, o.t0 + 0.05, 0.5); }
    W.forEach(({ w, s }) => wordIn(w, t, s));
    S.forEach(({ w, s }) => wordIn(w, t, s, 0.7, 30, 6));
  } };
}

// ---------------------------------------------------------------- quote (typed, word by word)
export function quote(o) {
  const el = mk('div', 'quote shadow');
  el.style.top = (o.top ?? 300) + 'px';
  mk('div', 'mark', '“', el);
  const q = mk('div', 'qt', o.text.split(/(\s+)/).filter(Boolean).map(w => /^\s+$/.test(w) ? w : `<span class="w">${w}</span>`).join(''), el);
  if (o.size) q.style.fontSize = o.size + 'px';
  const at = mk('div', 'at', o.attrib, el);
  const W = [...q.querySelectorAll('.w')];
  const per = o.per ?? 0.11;
  const hi = new Set(o.hi || []);
  W.forEach((w, i) => { if (hi.has(i)) w.classList.add('yl'); });
  return { el, update(t) {
    if (!vis(el, t, o.t0, o.t1)) return;
    exitFx(el, t, o.t1, 0.6);
    el.style.transform = `translateY(${-8 * range(t, o.t0, o.t1)}px)`;
    W.forEach((w, i) => { const s = o.t0 + 0.3 + i * per; const e = easeOutCubic(range(t, s, s + 0.35)); w.style.opacity = 0.08 + 0.92 * e; w.style.filter = e < 1 ? `blur(${(1 - e) * 6}px)` : 'none'; });
    const ae = easeOutQuint(range(t, o.t0 + 0.3 + W.length * per, o.t0 + 0.9 + W.length * per));
    at.style.opacity = ae; at.style.transform = `translateY(${(1 - ae) * 16}px)`;
  } };
}

// ---------------------------------------------------------------- press window (real screenshot or verified fallback)
export function press(o, assets) {
  const wrap = mk('div', 'abs'); wrap.style.inset = '0';
  const win = mk('div', 'pwin', `<div class="chrome"><div class="dot"></div><div class="dot"></div><div class="dot"></div><div class="url">${o.url}</div></div>`, wrap);
  const has = o.img && assets.press.has(o.img);
  let shot;
  if (has) {
    shot = mk('div', 'shot', null, win);
    shot.style.backgroundImage = `url(press/${o.img})`;
    if (o.bgpos) shot.style.backgroundPosition = o.bgpos;
    if (o.bgsize) shot.style.backgroundSize = o.bgsize;
  } else {
    shot = mk('div', 'fallback', `<div class="ol">${o.outlet}</div><div class="hd">${o.headline}</div>${o.sub ? `<div class="sd">${o.sub}</div>` : ''}<div class="dt">${o.date}</div>`, win);
  }
  // highlight rects (in 1280x740 window space), swept one after another
  const rects = !o.hl ? [] : Array.isArray(o.hl[0]) ? o.hl : [o.hl];
  const tot = rects.reduce((a, r) => a + r[2], 0) || 1;
  const HL = rects.map(r => { const h = mk('div', 'hl' + (o.dark ? ' dark' : ''), null, shot); Object.assign(h.style, { left: r[0] + 'px', top: r[1] + 'px', width: r[2] + 'px', height: r[3] + 'px' }); return { h, w: r[2] }; });
  const cap = o.cap ? mk('div', 'pcap', o.cap, wrap) : null;
  const A = o.from, B = o.to;
  return { el: wrap, update(t) {
    if (!vis(wrap, t, o.t0, o.t1)) return;
    const u = range(t, o.t0, o.t1);
    const e = o.snap ? easeOutExpo(range(t, o.t0, o.t0 + 0.5)) : easeOutQuint(range(t, o.t0, o.t0 + 0.9));
    const k = (i) => lerp(A[i], B[i], e) + (B[i] - A[i]) * 0.0;
    // A,B: [x, y, scale, rotY, rotX]; plus slow drift over the whole shot
    const drift = u * (o.drift ?? 0.05);
    const x = k(0) + (o.dx ?? 0) * u, y = k(1) + (o.dy ?? 0) * u, s = k(2) * (1 + drift), ry = k(3), rx = k(4);
    win.style.transform = `translate(${x}px, ${y}px) perspective(2200px) rotateY(${ry}deg) rotateX(${rx}deg) scale(${s})`;
    const out = easeInCubic(range(t, o.t1 - (o.out ?? 0.25), o.t1));
    win.style.opacity = Math.min(1, range(t, o.t0, o.t0 + 0.15) * 1) * (1 - out);
    win.style.filter = out > 0 ? `blur(${out * 12}px)` : 'none';
    if (HL.length) {
      const h0 = o.hlT ?? o.t0 + 0.6, dur = o.hlDur ?? 0.3 + 0.5 * HL.length;
      const p = clamp((t - h0) / dur) * tot; let acc = 0;
      HL.forEach(({ h, w }) => { h.style.transform = `scaleX(${clamp((p - acc) / w)})`; acc += w; });
    }
    if (cap) { Object.assign(cap.style, { left: (o.capPos?.[0] ?? 132) + 'px', top: (o.capPos?.[1] ?? 960) + 'px' }); cap.style.opacity = window01(t, o.t0 + 0.2, o.t1, 0.3, 0.2); }
  } };
}

// ---------------------------------------------------------------- word slam
export function slam(o) {
  const el = mk('div', 'slam', o.word);
  if (o.size) el.style.fontSize = o.size + 'px';
  if (o.color) el.style.color = o.color;
  return { el, update(t) {
    if (!vis(el, t, o.t0, o.t1)) return;
    const u = range(t, o.t0, o.t1);
    const s = 1.35 - 0.35 * easeOutExpo(range(t, o.t0, o.t0 + 0.18)) - 0.06 * u;
    const off = 14 * Math.exp(-(t - o.t0) * 12);
    el.style.transform = `translateY(-50%) scale(${s})`;
    el.style.textShadow = `${off}px 0 rgba(255,60,40,.7), ${-off}px 0 rgba(40,160,255,.7)`;
    el.style.opacity = 1 - easeInCubic(range(t, o.t1 - 0.08, o.t1));
  } };
}

// ---------------------------------------------------------------- counter (keys: [[t, value]])
export function counter(o) {
  const el = mk('div', 'counter shadow');
  Object.assign(el.style, o.style || { left: '132px', bottom: '150px' });
  const num = mk('div', 'num', '', el);
  if (o.size) num.style.fontSize = o.size + 'px';
  const lab = mk('div', 'lab', '', el);
  return { el, update(t) {
    if (!vis(el, t, o.t0, o.t1)) return;
    exitFx(el, t, o.t1, 0.4);
    let v = o.keys[0][1];
    for (let i = 0; i < o.keys.length - 1; i++) {
      const [ta, va] = o.keys[i], [tb, vb, ease] = o.keys[i + 1];
      if (t >= ta) v = lerp(va, vb, (ease || easeOutExpo)(range(t, ta, tb)));
    }
    num.innerHTML = o.fmt(v, t);
    const L = typeof o.label === 'function' ? o.label(t) : o.label;
    lab.innerHTML = L;
    const e = easeOutQuint(range(t, o.t0, o.t0 + 0.6));
    el.style.transform = `translateY(${(1 - e) * 40}px)`;
    if (o.shake) { const k = o.shake(t); el.style.transform += ` translate(${(Math.sin(t * 91) * k).toFixed(1)}px, ${(Math.cos(t * 77) * k).toFixed(1)}px)`; }
  } };
}

// ---------------------------------------------------------------- asset-class penetration chart
export function assetChart(o) {
  const el = mk('div', 'abs chart');
  mk('div', 'eyebrow', `<span class="bar"></span>On-chain today · mid 2026`, el).style.marginBottom = '40px';
  mk('div', 'hdr', `<div>ASSET CLASS</div><div style="text-align:right">TOTAL MARKET</div><div>TOKENIZED ON-CHAIN</div><div style="text-align:right">PENETRATION</div>`, el);
  const rows = [['US Treasuries', '$29T', 15.0, '$15.0B', '0.05%'], ['Private credit', '$2T', 6.2, '$6.2B', '0.31%'], ['Gold', '$23T', 4.7, '$4.7B', '0.02%'], ['Public equities', '$130T', 2.2, '$2.2B', '0.002%'], ['Real estate', '$380T', 0.2, '$0.2B', '0.00005%']];
  const R = rows.map(([n, tm, v, vs, p], i) => {
    const r = mk('div', 'r' + (i === 4 ? ' re' : ''), `<div>${n}</div><div class="tm">${tm}</div><div class="barw"><div class="bar"></div><div class="bv">${vs}</div></div><div class="pen">${p}</div>`, el);
    return { r, bar: r.querySelector('.bar'), bv: r.querySelector('.bv'), v, s: o.t0 + 0.5 + i * (i === 4 ? 0.55 : 0.35) };
  });
  const src = mk('div', 'credit', 'Market sizes: SIFMA, PwC, World Gold Council, WFE, Savills · On-chain values: rwa.xyz, mid 2026', el);
  Object.assign(src.style, { position: 'relative', right: 'auto', bottom: 'auto', textAlign: 'left', marginTop: '26px' });
  return { el, update(t) {
    if (!vis(el, t, o.t0, o.t1)) return;
    exitFx(el, t, o.t1);
    R.forEach(({ r, bar, bv, v, s }, i) => {
      const e = easeOutQuint(range(t, s, s + 0.7));
      r.style.opacity = e; r.style.transform = `translateX(${(1 - e) * 40}px)`;
      const w = Math.max(4, v / 15 * 820) * easeOutExpo(range(t, s + 0.15, s + 1.1));
      bar.style.width = w + 'px'; bv.style.left = (w + 20) + 'px';
      if (i === 4) { const p = window01(t, s + 0.8, o.t1, 0.2, 0.3); r.style.background = `rgba(255,190,6,${0.08 * p})`; }
    });
  } };
}

// ---------------------------------------------------------------- intermediary chain
export function chain(o) {
  const el = mk('div', 'abs chainwrap');
  mk('div', 'chain-ends', `<span>CAPITAL →</span><span>A DOZEN INTERMEDIARIES</span><span>→ ASSET</span>`, el);
  const pills = mk('div', 'pills', null, el);
  const names = ['Broker', 'Valuer', 'Legal · buy side', 'Legal · sell side', 'Technical DD', 'ESG DD', 'Notary', 'Bank / escrow', 'Registry', 'Fund admin', 'Transfer agent', 'Auditor'];
  const P = names.map((n, i) => ({ p: mk('div', 'pill', `<span class="d"></span>${n}`, pills), s: o.t0 + 0.4 + i * 0.22 }));
  const st = mk('div', 'cstats', null, el);
  const S = [['3–6', ' months', 'per transaction,<br>re-verified from scratch'], ['~30', '%', 'discount to NAV on<br>real estate fund stakes'], ['$220', 'B', 'trapped in funds past<br>their intended exit']].map(([a, b, k], i) =>
    ({ d: mk('div', 'cstat', `<div class="v">${a}<i>${b}</i></div><div class="k">${k}</div>`, st), s: o.t0 + 3.4 + i * 0.35 }));
  const src = mk('div', 'credit', 'Sources: Jefferies Global Secondary Market Review 2023–2025; Burgiss', el);
  Object.assign(src.style, { position: 'relative', right: 'auto', bottom: 'auto', textAlign: 'left', marginTop: '34px' });
  return { el, update(t) {
    if (!vis(el, t, o.t0, o.t1)) return;
    exitFx(el, t, o.t1);
    P.forEach(({ p, s }) => { const e = easeOutQuint(range(t, s, s + 0.5)); p.style.opacity = 0.15 + 0.85 * e; p.style.transform = `translateY(${(1 - e) * 20}px) scale(${1 + 0.06 * Math.exp(-Math.max(0, t - s) * 8) * (t > s ? 1 : 0)})`; p.classList.toggle('on', t > s + 0.1); });
    S.forEach(({ d, s }) => { const e = easeOutQuint(range(t, s, s + 0.7)); d.style.opacity = e; d.style.transform = `translateY(${(1 - e) * 30}px)`; });
    src.style.opacity = range(t, o.t0 + 4, o.t0 + 4.6) * 0.9;
  } };
}

// ---------------------------------------------------------------- public vs private
export function split(o) {
  const el = mk('div', 'abs split');
  const pub = mk('div', 'side pub', `<div class="eyebrow" style="margin:0"><span class="bar"></span>Public markets</div><div class="big">~70<i>%</i></div><div class="desc">of US equity volume is executed by algorithms, not humans. Standard identifiers. Continuous, machine-readable disclosure.</div><div class="ticker"></div>`, el);
  const prv = mk('div', 'side prv', `<div class="eyebrow" style="margin:0;color:#8a6a00"><span class="bar" style="background:#8a6a00"></span>Private markets</div><div class="big">0<i>%</i></div><div class="desc">of private market volume is automated. No standard identifiers. Diligence by PDF, data room and site visit.</div><div class="ticker"></div>`, el);
  const tick = [pub.querySelector('.ticker'), prv.querySelector('.ticker')];
  const bigs = [pub.querySelector('.big'), prv.querySelector('.big')];
  const note = mk('div', 'credit', 'Academic and industry estimates put algorithmic share at 60–75% of US equity volume', el);
  Object.assign(note.style, { position: 'absolute', right: 'auto', left: 0, bottom: '-60px', textAlign: 'left' });
  const syms = ['AAPL', 'MSFT', 'NVDA', 'AMZN', 'JPM', 'BLK', 'GOOGL', 'META', 'TSLA', 'V'];
  return { el, update(t) {
    if (!vis(el, t, o.t0, o.t1, 'grid')) return;
    exitFx(el, t, o.t1);
    [pub, prv].forEach((s, i) => { const e = easeOutQuint(range(t, o.t0 + i * 0.5, o.t0 + 0.8 + i * 0.5)); s.style.opacity = e; s.style.transform = `translateY(${(1 - e) * 50}px)`; });
    bigs[0].innerHTML = `~${Math.round(70 * easeOutExpo(range(t, o.t0 + 0.2, o.t0 + 1.6)))}<i>%</i>`;
    // live algorithmic prints vs. an idle, manual log
    const k = Math.floor((t - o.t0) * 18);
    let a = '';
    for (let j = 0; j < 5; j++) { const n = k - j; if (n < 0) break; const s = syms[(n * 7) % syms.length]; const px = (100 + ((n * 37) % 400) + ((n * 13) % 100) / 100).toFixed(2); const q = 100 * (1 + (n * 11) % 40); a += `${String(9 + Math.floor(n / 3600)).padStart(2, '0')}:31:${String((n * 7) % 60).padStart(2, '0')}.${String((n * 137) % 1000).padStart(3, '0')}  ALGO  ${s.padEnd(5)} ${q} @ ${px}<br>`; }
    tick[0].innerHTML = a;
    const d = t - o.t0;
    tick[1].innerHTML = `Day 1 · data room requested<br>${d > 1.5 ? 'Day 19 · rent roll v7 received (xlsx)<br>' : ''}${d > 2.6 ? 'Day 46 · site visit scheduled<br>' : ''}${d > 3.6 ? 'Day 88 · valuation report pending…<br>' : ''}`;
    note.style.opacity = range(t, o.t0 + 1.5, o.t0 + 2) * 0.9;
  } };
}

// ---------------------------------------------------------------- ingestion console (layer 01)
export function ingest(o) {
  const el = mk('div', 'panel ingest');
  const src = mk('div', 'src', `<div class="ptitle" style="margin-bottom:14px">Sources · Berlin-Mitte mixed-use</div>`, el);
  const rows = [['PDF', 'Grundbuchauszug_Mitte_scan.pdf'], ['XLSX', 'rent_roll_FINAL(3).xlsx'], ['ERP', 'Property system export · 146 units'], ['REG', 'Land register · title & encumbrances'], ['EML', 'RE: RE: FW: service charge 2026'], ['IMG', 'EPC_certificate_photo.jpg']].map(([ic, nm], i) => {
    const r = mk('div', 'srow', `<div class="ic">${ic}</div><div class="nm">${nm}</div><div class="st">QUEUED</div>`, src);
    return { r, st: r.querySelector('.st'), s: o.t0 + 0.5 + i * 0.4 };
  });
  const sc = mk('div', 'schema', null, el);
  const lines = [['asset_id', '"DE-BER-0042"'], ['type', '"mixed_use"'], ['units', '146'], ['gla_sqm', '12480'], ['occupancy', '0.962'], ['noi_eur', '1284000'], ['valuation_eur', '41200000'], ['epc', '"B"'], ['title', '"verified"'], ['lineage', '6 sources · hashed']];
  mk('div', 'ptitle', 'Propchain schema · machine-readable', sc).style.marginBottom = '16px';
  const body = mk('div', null, null, sc);
  const prog = mk('div', 'prog', null, el);
  return { el, update(t) {
    if (!vis(el, t, o.t0, o.t1, 'grid')) return;
    exitFx(el, t, o.t1);
    const e = easeOutQuint(range(t, o.t0, o.t0 + 0.8));
    el.style.transform = `translateY(${(1 - e) * 60}px)`; el.style.opacity = Math.min(e, 1 - easeInCubic(range(t, o.t1 - 0.45, o.t1)));
    rows.forEach(({ r, st, s }) => {
      const p = t - s;
      st.textContent = p < 0 ? 'QUEUED' : p < 0.55 ? 'PARSING ' + '▮'.repeat(1 + Math.floor(p * 8) % 4) : 'STRUCTURED ✓';
      st.classList.toggle('ok', p >= 0.55);
      r.style.opacity = p < 0 ? 0.45 : 1;
    });
    const n = clamp((t - o.t0 - 0.9) / 2.6) * lines.length;
    let h = '{<br>';
    lines.forEach(([k, v], i) => { if (i < n) h += `&nbsp;&nbsp;<span class="k">"${k}"</span>: <span class="${v.startsWith('"') ? 's' : 'v'}">${v}</span>${i < lines.length - 1 ? ',' : ''}<br>`; });
    body.innerHTML = h + (n >= lines.length ? '}' : '');
    prog.style.width = `${clamp((t - o.t0 - 0.4) / 3.2) * 100}%`;
  } };
}

// ---------------------------------------------------------------- proofs (layer 02)
export function proofs(o) {
  const el = mk('div', 'panel proofs');
  mk('div', 'ptitle', 'Validation engine · on chain', el).style.marginBottom = '12px';
  const P = [['Proof of ingestion', '0x9f2c41e0…b7e41a'], ['Proof of permission', '0x31d7aa92…04c9fe'], ['Proof of state', '0xe80b5c13…9a2d77'], ['Proof of agency', '0x5a6f0e8d…c13b20']].map(([n, h], i) => {
    const r = mk('div', 'proof', `<div class="ck">${CHECK}</div><div><div class="pt">${n.toUpperCase()}</div><div class="ph">&nbsp;</div></div>`, el);
    return { r, path: r.querySelector('path'), ph: r.querySelector('.ph'), ck: r.querySelector('.ck'), hash: 'anchored · ' + h, s: o.t0 + 0.5 + i * 0.5 };
  });
  return { el, update(t) {
    if (!vis(el, t, o.t0, o.t1)) return;
    exitFx(el, t, o.t1);
    const e = easeOutQuint(range(t, o.t0, o.t0 + 0.7)); el.style.transform = `translateX(${(1 - e) * 60}px)`;
    P.forEach(p => {
      const a = easeOutQuint(range(t, p.s, p.s + 0.5)); p.r.style.opacity = 0.25 + 0.75 * a;
      const c = clamp((t - p.s - 0.15) / 0.3); p.path.style.strokeDasharray = '1'; p.path.style.strokeDashoffset = String(1 - c);
      p.ck.style.background = c >= 1 ? 'rgba(255,190,6,.16)' : 'transparent';
      p.ph.textContent = typed(p.hash, t, p.s + 0.2, 0.5) || ' ';
    });
  } };
}

// ---------------------------------------------------------------- Know Your Agent card (layer 03)
export function kya(o) {
  const el = mk('div', 'panel kya');
  mk('div', 'hdr', `<div class="avatar"><svg width="34" height="34" viewBox="0 0 34 34"><rect x="5" y="7" width="24" height="20" rx="6" fill="none" stroke="#FFBE06" stroke-width="2"/><circle cx="13" cy="17" r="2.4" fill="#FFBE06"/><circle cx="21" cy="17" r="2.4" fill="#FFBE06"/><path d="M17 3v4" stroke="#FFBE06" stroke-width="2"/></svg></div><div class="ptitle">Know your agent</div><div class="badge">VERIFIED</div>`, el);
  const F = [['AGENT ID', 'agt_0x3f…a91c'], ['ROLE', 'Valuation · diligence'], ['PRINCIPAL', 'Manager A · LEI verified'], ['PERMISSIONS', 'read asset.* · write valuation'], ['MANDATE', 'Core+ residential · DE/NL'], ['DATA SCOPE', 'attested records only'], ['AUDIT TRAIL', '1,284 actions · anchored']].map(([k, v], i) => {
    const f = mk('div', 'f', `<div class="k">${k}</div><div class="v"></div>`, el);
    return { f, v: f.querySelector('.v'), val: v, s: o.t0 + 0.6 + i * 0.22 };
  });
  const badge = el.querySelector('.badge');
  return { el, update(t) {
    if (!vis(el, t, o.t0, o.t1)) return;
    exitFx(el, t, o.t1);
    const e = easeOutQuint(range(t, o.t0, o.t0 + 0.7)); el.style.transform = `translateX(${(1 - e) * 60}px)`;
    F.forEach(f => { f.f.style.opacity = range(t, f.s, f.s + 0.2); f.v.textContent = typed(f.val, t, f.s, 0.35); });
    const b = range(t, o.t0 + 2.4, o.t0 + 2.6); badge.style.opacity = b; badge.style.transform = `scale(${1 + 0.3 * (1 - b)})`;
  } };
}

// ---------------------------------------------------------------- LP mandate (act V)
export function mandate(o) {
  const el = mk('div', 'panel mandate');
  mk('div', 'eyebrow', `<span class="bar"></span>Allocator · new mandate`, el);
  const F = [['INVESTOR', 'European pension fund'], ['ALLOCATION', '€250,000,000'], ['STRATEGY', 'Core+ residential'], ['MARKETS', 'Germany · Netherlands'], ['TARGET', '4.5% net yield · LTV ≤ 50%'], ['DATA', 'Attested assets only']].map(([k, v], i) => {
    const f = mk('div', 'f', `<div class="k">${k}</div><div class="v"></div>`, el);
    return { f, v: f.querySelector('.v'), val: v, s: o.t0 + 0.5 + i * 0.3 };
  });
  const dep = mk('div', 'deploy', '', el);
  return { el, update(t) {
    if (!vis(el, t, o.t0, o.t1)) return;
    exitFx(el, t, o.t1);
    const e = easeOutQuint(range(t, o.t0, o.t0 + 0.7)); el.style.transform = `translateY(${(1 - e) * 50}px)`;
    F.forEach(f => { f.f.style.opacity = range(t, f.s, f.s + 0.2); f.v.textContent = typed(f.val, t, f.s, 0.4); });
    dep.textContent = typed('→ DEPLOYING AGENT agt_0x7c · PERMISSIONED', t, o.t0 + 2.6, 0.9);
  } };
}

// ---------------------------------------------------------------- agentic deal flow (act V)
export function deal(o) {
  const el = mk('div', 'panel deal');
  const top = mk('div', 'top', `<div><div class="ptitle">Autonomous transaction · DE-BER-0042</div><div class="clock">00:00:00</div></div><div class="vs">TODAY<br><s>3–6 MONTHS</s></div>`, el);
  const clock = top.querySelector('.clock');
  const S = [['List', 'Manager A lists the asset. Its verified data room already exists; state attested to the minute.'], ['Diligence', 'AI agents run diligence on attested data; smart contracts check permissions and mandate fit.'], ['Match', 'Managers B, C and D receive the offer automatically: it fits their mandates.'], ['Finance', "Lenders' agents price the collateral in real time; debt offers arrive alongside bids."], ['Settle', 'The winning bid clears. Title and token transfer atomically, financing attached.']].map(([n, d], i) => {
    const r = mk('div', 'step', `<div class="n">0${i + 1}</div><div><div class="t">${n}</div><div class="d">${d}</div></div><div class="ts"></div>`, el);
    return { r, ts: r.querySelector('.ts'), s: o.t0 + 0.6 + i * (o.gap ?? 1.0) };
  });
  const fmt = s => { s = Math.floor(s); return `${String(Math.floor(s / 3600)).padStart(2, '0')}:${String(Math.floor(s / 60) % 60).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`; };
  // film seconds -> "deal" seconds: the whole transaction completes in ~4 minutes
  const dealT = t => Math.max(0, t - o.t0 - 0.6) * (250 / ((o.gap ?? 1.0) * 4 + 0.4));
  return { el, update(t) {
    if (!vis(el, t, o.t0, o.t1)) return;
    exitFx(el, t, o.t1);
    const e = easeOutQuint(range(t, o.t0, o.t0 + 0.7)); el.style.transform = `translateX(${(1 - e) * 70}px)`;
    const last = S[S.length - 1].s;
    clock.textContent = fmt(dealT(Math.min(t, last + 0.4)));
    clock.style.color = t > last + 0.4 ? '#FFBE06' : '';
    S.forEach(st => {
      const a = easeOutQuint(range(t, st.s, st.s + 0.5));
      st.r.style.opacity = 0.18 + 0.82 * a; st.r.classList.toggle('on', t > st.s);
      st.ts.textContent = t > st.s ? '+' + fmt(dealT(st.s)).slice(3) : '';
    });
  } };
}

// ---------------------------------------------------------------- stats
export function stats(o) {
  const el = mk('div', 'abs stats');
  const L = [{ v: 11000, f: n => Math.round(n / 10) * 10 === 11000 ? '11,000<i>+</i>' : (Math.round(n / 10) * 10).toLocaleString('en') + '<i>+</i>', k: 'Units on platform' }, { v: 90, f: n => '€' + Math.round(n) + '<i>B+</i>', k: 'Asset value under<br>data management' }, { v: 3000, f: n => (Math.round(n / 10) * 10).toLocaleString('en') + '<i>+</i>', k: 'Assets under<br>data management' }, { v: 4, f: n => Math.round(n) + '', k: 'Proofs live on<br>the validation engine' }]
    .map((s, i) => { const d = mk('div', 'stat', `<div class="v"></div><div class="k">${s.k}</div>`, el); return { ...s, d, v_: d.querySelector('.v'), s: o.t0 + i * 0.22 }; });
  return { el, update(t) {
    if (!vis(el, t, o.t0, o.t1, 'flex')) return;
    exitFx(el, t, o.t1);
    L.forEach(s => { const e = easeOutQuint(range(t, s.s, s.s + 0.7)); s.d.style.opacity = e; s.d.style.transform = `translateY(${(1 - e) * 30}px)`; s.v_.innerHTML = s.f(s.v * easeOutExpo(range(t, s.s, s.s + 1.3))); });
  } };
}

// ---------------------------------------------------------------- chapter marker
export function chapter(o) {
  const el = mk('div', 'abs chapter');
  return { el, update(t) {
    if (!vis(el, t, o.t0, o.t1)) return;
    el.innerHTML = `<b>${o.num}</b>${typed(o.title.toUpperCase(), t, o.t0 + 0.1, 0.6)}`;
    el.style.opacity = window01(t, o.t0, o.t1, 0.3, 0.4);
  } };
}

// ---------------------------------------------------------------- logo reveal / end card
export function endcard(o) {
  const el = mk('div', 'abs end');
  const logo = mk('img', 'logo', null, el); logo.src = '../assets/logo-white.svg';
  const tag = mk('div', 'tag', words(o.tag || 'Structuring real estate for the autonomous era.'), el);
  const tri = o.tri !== false ? mk('div', 'tri', 'Machine-readable <b>·</b> Attested <b>·</b> Agent-ready', el) : null;
  const url = o.url ? mk('div', 'url', o.url, el) : null;
  const TW = [...tag.querySelectorAll('.w')];
  return { el, update(t) {
    if (!vis(el, t, o.t0, o.t1, 'flex')) return;
    exitFx(el, t, o.t1, 0.6);
    const lw = easeInOutCubic(range(t, o.t0 + 0.1, o.t0 + 1.1)), le = easeOutQuint(range(t, o.t0, o.t0 + 1.2));
    logo.style.clipPath = `inset(-40px ${(1 - lw) * 100}% -40px -40px)`;
    logo.style.transform = `scale(${1.06 - 0.06 * le})`;
    logo.style.filter = `blur(${(1 - le) * 10}px) drop-shadow(0 0 ${6 + 26 * (1 - range(t, o.t0 + 1, o.t0 + 2.4))}px rgba(255,190,6,.4))`;
    TW.forEach((w, j) => wordIn(w, t, o.t0 + 1.1 + j * 0.06, 0.8, 40, 8));
    if (tri) { const e = easeOutQuint(range(t, o.t0 + 1.9, o.t0 + 2.7)); tri.style.opacity = e; tri.style.letterSpacing = `${0.3 + (1 - e) * 0.25}em`; }
    if (url) url.style.opacity = easeOutQuint(range(t, o.t0 + 2.4, o.t0 + 3.2));
  } };
}
