// Scenes 0–4: title, the first decision, the components, one record's journey.
'use strict';

function T(p, x, y, cls, html, w) { const e = el('div', 'a ' + (cls || ''), p, html); pos(e, x, y, w); return e; }
function chip(p, x, y, w, ic, title, sub, cls = '') {
  const c = el('div', 'a chip ' + cls, p); pos(c, x, y, w);
  icon(ic, 34, c); const tx = el('div', '', c); el('div', 't', tx, title); if (sub) el('div', 's', tx, sub);
  return c;
}
function P(svg, d, cls = 'ln', extra = {}) { return sv('path', { d, class: cls, ...extra }, svg); }
// Move an element's centre along a path.
function follow(sc, e, svg, d, t0, dur, o = {}) {
  const path = sv('path', { d, fill: 'none', stroke: 'none' }, svg);
  const L = path.getTotalLength();
  const { w = 0, h = 0, e: ez = ease.io } = o;
  sc.on(t => {
    const k = ez(clamp((t - t0) / dur));
    const pt = path.getPointAtLength(k * L);
    e.style.left = (pt.x - w / 2).toFixed(1) + 'px'; e.style.top = (pt.y - h / 2).toFixed(1) + 'px';
  });
}
function rail(p, svg, x0, x1, y, label = 'LEDGER', sub = '') {
  const r = el('div', 'a rail', p); pos(r, x0, y - 26, x1 - x0, 52);
  el('span', 'mono y', r, label); if (sub) el('span', 'mono sm dim lc', r, sub);
  return r;
}

function buildScenes1() {
  // ================================================================ 0 · TITLE
  {
    const sc = new Scene(0, 6.3, { fadeIn: 0, fadeOut: .7 });
    const logo = el('img', 'a', sc.el); logo.src = '../assets/logo-white.svg'; pos(logo, 160, 300); logo.style.height = '40px';
    appear(sc, logo, .2, { dy: 0, dx: -20 });
    appear(sc, T(sc.el, 160, 420, 'mono y', 'Technical architecture'), .6);
    appear(sc, T(sc.el, 152, 462, 'h1', 'Provable, not visible', 1100), .9, { dy: 34, blur: 14 });
    appear(sc, T(sc.el, 160, 588, 'h3 dim', 'How the attested market is built', 900), 1.7);
    const s = sc.svg();
    draw(sc, P(s, 'M160 690 H700', 'ln y'), 2.2, 1.4);
    // Merkle motif on the right: eight leaves roll up into one yellow root
    const lx = [1180, 1260, 1340, 1420, 1500, 1580, 1660, 1740], ly = 800;
    const lv2 = [1220, 1380, 1540, 1700], lv3 = [1300, 1620], root = [1460, 330];
    lx.forEach((x, i) => { const c = sv('rect', { x: x - 14, y: ly - 14, width: 28, height: 28, rx: 5, class: 'ln' }, s); appear(sc, c, 1.0 + i * .06, { dy: 10, blur: 0 }); });
    lx.forEach((x, i) => draw(sc, P(s, `M${x} ${ly - 14} C${x} ${ly - 70} ${lv2[i >> 1]} ${ly - 90} ${lv2[i >> 1]} 640`), 1.5 + i * .04, .8));
    lv2.forEach((x, i) => draw(sc, P(s, `M${x} 640 C${x} 580 ${lv3[i >> 1]} 560 ${lv3[i >> 1]} 500`), 2.2 + i * .05, .8));
    lv3.forEach(x => draw(sc, P(s, `M${x} 500 C${x} 430 ${root[0]} 420 ${root[0]} ${root[1] + 22}`, 'ln y'), 2.9, .9));
    [...lv2.map(x => [x, 640]), ...lv3.map(x => [x, 500])].forEach(([x, y], i) => appear(sc, sv('circle', { cx: x, cy: y, r: 7, fill: '#141416', class: 'ln' }, s), 2.0 + i * .1, { dy: 0, blur: 0 }));
    const rc = sv('circle', { cx: root[0], cy: root[1], r: 22, fill: '#FFBE06' }, s); rc.style.filter = 'drop-shadow(0 0 18px rgba(255,190,6,.7))';
    appear(sc, rc, 3.6, { dy: 0, blur: 0, scale: .2 }); rc.style.transformOrigin = `${root[0]}px ${root[1]}px`;
    appear(sc, T(sc.el, 1500, 312, 'mono sm y', 'root'), 3.9, { dy: 0, dx: -10 });
  }

  // ================================================================ 1 · THE FIRST DECISION
  chapter(6.2, 36.0, '01', 'The first decision');
  {
    const sc = new Scene(6.2, 36.3);
    // A: the one decision, as three tiles
    const tA = V('02'), outA = 12.3;
    appear(sc, T(sc.el, 0, 250, 'h2 center', 'The chain is a notary and a settlement rail.', 1920), tA + 1.4, { out: outA });
    const tiles = [['stamp', 'Notary', 'proves what happened', Wd('02', 'notary')], ['arrow-left-right', 'Settlement rail', 'moves value with title', Wd('02', 'settlement rail')], ['database', 'Database', 'holds the data', Wd('02', 'not a database')]];
    tiles.forEach(([ic, a, b, t], i) => {
      const c = el('div', 'a card tile', sc.el); pos(c, 330 + i * 440, 440, 380, 300);
      const ii = icon(ic, 72, c, i < 2 ? 'y' : 'dim'); ii.style.margin = '48px auto 26px'; ii.style.display = 'flex';
      el('div', 'h3 center' + (i < 2 ? '' : ' dim'), c, a); el('div', 'mono sm dim center', c, b).style.marginTop = '12px';
      appear(sc, c, t, { out: outA });
      if (i < 2) flag(sc, c, 'lit', t + .4);
    });
    const x = sc.svg();
    draw(sc, P(x, 'M1235 470 L1595 710', 'ln'), Wd('02', 'not a database') + .7, .5, { out: outA });
    draw(sc, P(x, 'M1595 470 L1235 710', 'ln'), Wd('02', 'not a database') + .9, .5, { out: outA });
    appear(sc, T(sc.el, 0, 790, 'mono dim center', 'Not a database', 1920), Wd('02', 'not a database') + 1.0, { out: outA });

    // B: on chain vs off chain
    const tB = 12.6;
    draw(sc, P(x, 'M960 190 V930'), tB, 1.2);
    appear(sc, T(sc.el, 150, 170, 'mono y', 'On chain'), tB + .1);
    appear(sc, T(sc.el, 150, 200, 'h3', 'Verify it later, without trusting us', 780), tB + .3);
    appear(sc, T(sc.el, 1030, 170, 'mono dim', 'Off chain'), V('04') - .2);
    appear(sc, T(sc.el, 1030, 200, 'h3', 'Anyone needs to read it', 780), V('04'));
    const on = [['hash', 'Commitments to records', 'salted hashes · a root per asset per period', 'commitments'],
      ['id-card', 'Identity registry', 'participants · agents · scopes · revocations', 'identities'],
      ['ticket-check', 'Permission grants', 'who may read what · every grant timestamped', 'grants'],
      ['signature', 'Attestation signatures', 'which source signed which commitment, at what level', 'signatures'],
      ['arrow-left-right', 'Escrow & settlement state', 'value moves atomically with title', 'settlement state'],
      ['scroll-text', 'Audit log root', "every action's hash · the log can't be rewritten", 'audit log root']];
    on.forEach(([ic, a, b, w], i) => { const c = chip(sc.el, 150, 290 + i * 104, 760, ic, a, b, 'on'); appear(sc, c, Wd('03', w), { dx: -30, dy: 0 }); });
    const off = [['file-spreadsheet', 'The records themselves', 'rent rolls, leases, ledgers · confidential, erasable', 'records'],
      ['briefcase', 'Mandates & credit boxes', 'strategy · visible only through the enclave', 'mandates'],
      ['cpu', 'The matching engine', 'compute · inputs and outputs committed, not the run', 'matching engine'],
      ['layers', 'Models & extraction', 'change weekly · only their outputs need lineage', 'models'],
      ['file-text', 'Documents', 'large, sensitive, subject to retention rules', 'documents'],
      ['key-round', 'Keys', 'never anywhere but a hardware security module', 'keys never']];
    off.forEach(([ic, a, b, w], i) => {
      const c = chip(sc.el, 1030, 290 + i * 104, 740, ic, a, b); appear(sc, c, Wd('04', w), { dx: 30, dy: 0 });
      if (i === 5) { flag(sc, c, 'on', Wd('04', 'hardware') + .2); const h = el('span', 'pill y', c, 'HSM only'); h.style.marginLeft = 'auto'; appear(sc, h, Wd('04', 'hardware') + .2, { dy: 0, dx: 10 }); }
    });
  }

  // ================================================================ 2 · THE COMPONENTS
  chapter(36.0, 54.6, '02', 'The components');
  {
    const sc = new Scene(36.0, 54.9);
    const s = sc.svg();
    const RY = 540;
    const r = rail(sc.el, s, 180, 1740, RY, 'Ledger', 'commitments · identities · grants · signatures · settlement state · audit root');
    appear(sc, r, V('06') + .1, { dy: 0, dx: -40 });
    appear(sc, T(sc.el, 0, 150, 'h3 center', 'Eight services around one ledger', 1920), V('06') + .3, { out: Wd('07', 'writes') - .3 });
    const svc = [
      ['01', 'fingerprint', 'Identity', 'participants · agents · scopes · revocation', 'Identity', 'Layer 02'],
      ['02', 'inbox', 'Ingestion', 'connectors · extraction · schema · lineage', 'ingestion', 'Layer 01'],
      ['03', 'vault', 'Record store', 'per-tenant vaults · field-level keys · grants', 'record store', 'Layer 01'],
      ['04', 'signature', 'Attestation', 'source signatures · quorum · level', 'attestation', 'Layer 02'],
      ['05', 'cpu', 'Matching', 'books · scoring · deferred acceptance · enclave', 'Matching', 'Layer 03'],
      ['06', 'arrow-left-right', 'Settlement', 'escrow · DvP of title and cash · tranches', 'settlement', 'Layer 02'],
      ['07', 'bot', 'Agent runtime', 'policy · permissions · spend limits · human gates', 'agent runtime', 'Layer 03'],
      ['08', 'plug', 'Integration', 'adapters · event bus · write-back', 'integration', 'All layers']];
    const tW = Wd('07', 'writes'), tG = Wd('07', 'reads grants'), tNone = Wd('07', 'None');
    svc.forEach(([n, ic, name, sub, w, layer], i) => {
      const top = i < 4, cx = 350 + (i % 4) * 406, y = top ? 250 : 680;
      const c = el('div', 'a card node', sc.el); pos(c, cx - 175, y, 350, 150);
      const hd = el('div', 'nodehd', c); el('span', 'mono y', hd, n); icon(ic, 34, hd);
      el('div', 'nodet', c, name); el('div', 'nodes', c, sub);
      const t0 = Wd('06', w); appear(sc, c, t0, { dy: top ? -24 : 24 });
      flag(sc, c, 'lit', t0, t0 + 1.1);
      if (i === 7) flag(sc, c, 'lit', t0 + 1.1, 1e9);
      const lt = T(sc.el, cx - 175, top ? y - 30 : y + 160, 'mono sm faint', layer, 350);
      appear(sc, lt, Vend('07') - 2.2 + i * .1, { dy: 0 });
      const y0 = top ? y + 150 : y, y1 = top ? RY - 26 : RY + 26;
      const a = P(s, `M${cx - 14} ${y0} V${y1}`), b = P(s, `M${cx + 14} ${y1} V${y0}`);
      draw(sc, a, t0 + .3, .6); draw(sc, b, t0 + .3, .6);
      pulse(sc, s, P(s, `M${cx - 14} ${y0} V${y1}`, '', { fill: 'none' }), tW + i * .12, 1.1, { repeat: 5, period: 1.6 });
      pulse(sc, s, P(s, `M${cx + 14} ${y1} V${y0}`, '', { fill: 'none' }), tG + i * .12, 1.1, { repeat: 4, period: 1.6, color: '#F4F2EC', len: .08, r: 4 });
    });
    const lg = T(sc.el, 0, 920, 'center', '', 1920);
    lg.innerHTML = '<span class="pill y">↓ writes commitments</span>&nbsp;&nbsp;&nbsp;<span class="pill">↑ reads grants</span>&nbsp;&nbsp;&nbsp;<span class="pill ns">no state stored on the ledger</span>';
    appear(sc, lg.children[0], tW, { dy: 10 }); appear(sc, lg.children[1], tG, { dy: 10 }); appear(sc, lg.children[2], tNone, { dy: 10 });
  }

  // ================================================================ 3 · STOCK: one record
  chapter(54.6, 101.6, '03', "One record's journey");
  {
    const sc = new Scene(54.6, 57.9, { fadeIn: .4, fadeOut: .6 });
    stock(sc, 'tower', 54.6, 57.9, { from: 0, zoom: [1.02, 1.1] });
    appear(sc, T(sc.el, 160, 800, 'h2', 'Follow one record.', 1200), 55.1);
  }

  // ================================================================ 4 · THE JOURNEY (camera over one world)
  {
    const sc = new Scene(57.5, 101.9, { fadeIn: .6 });
    const wd = el('div', 'world', sc.el);
    const s = sv('svg', { width: W, height: H, viewBox: `0 0 ${W} ${H}`, class: 'layer' }, wd);
    const t9 = V('09'), tAd = Wd('09', 'adapter'), tIn = Wd('09', 'Ingestion'), tLin = Wd('09', 'lineage');
    // source system
    const src = el('div', 'a card', wd); pos(src, 90, 290, 250, 230);
    const sh = el('div', 'nodehd', src); el('span', 'mono sm dim', sh, 'Source'); icon('server', 30, sh);
    el('div', 'nodet', src, 'Property system'); el('div', 'nodes', src, "the owner's system, unchanged");
    appear(sc, src, 57.7);
    // the rent roll document
    const doc = el('div', 'a docchip', wd); pos(doc, 0, 0, 150, 56); icon('file-spreadsheet', 26, doc, 'y'); el('span', '', doc, 'Rent roll');
    appear(sc, doc, 58.3, { dy: 0, blur: 4, out: tIn + .5, outDur: .3 });
    follow(sc, doc, s, 'M215 470 C300 470 330 405 455 405 S 560 400 700 400', tAd - 1.0, tIn - tAd + 1.3, { w: 150, h: 56 });
    // adapter gate
    const ad = el('div', 'a card', wd); pos(ad, 400, 350, 110, 110); ad.style.display = 'grid'; ad.style.placeItems = 'center';
    const adi = el('div', 'center', ad); icon('plug', 34, adi, 'y'); el('div', 'mono sm', adi, 'Adapter').style.marginTop = '6px';
    appear(sc, ad, tAd - 1.2, { dy: 0, scale: .8 }); flag(sc, ad, 'lit', tAd - .2, tAd + 1.5);
    draw(sc, P(s, 'M340 405 H400'), tAd - 1.0, .5); draw(sc, P(s, 'M510 405 H575'), tAd - .6, .5);
    // the record card (canonical schema)
    const card = el('div', 'a card', wd); pos(card, 580, 250, 400, 310);
    el('div', 'mono sm y', card, 'Ingestion · canonical schema').style.cssText = 'padding:18px 22px 6px';
    const fields = [['Tenant', '●●●●●●'], ['Rent', '●●●●●●'], ['NOI', '800,000']];
    const rows = fields.map(([k, v], i) => {
      const r = el('div', 'frow', card); el('span', 'fk', r, k); el('span', 'fv', r, v);
      appear(sc, r, tIn + .5 + i * .35, { dx: 20, dy: 0 });
      return r;
    });
    appear(sc, card, tIn, { dy: 0, scale: .92 });
    // lineage threads back to the source
    [0, 1, 2].forEach(i => { const p = P(s, `M600 ${355 + i * 70} C470 ${355 + i * 70} 420 ${540 + i * 16} 300 520`, 'ln dash'); draw(sc, p, tLin + i * .15, 1.0); });
    appear(sc, T(wd, 360, 560, 'mono sm dim', 'lineage → source', 300), tLin + .4, { dy: 10 });
    // vault + per-field keys
    const t10 = V('10');
    const vault = el('div', 'a vault', wd); pos(vault, 550, 200, 460, 400);
    el('div', 'mono sm', vault, 'Record store · vault · tenant A').style.cssText = 'position:absolute;left:18px;top:-11px;background:#111113;padding:0 10px;color:var(--y)';
    appear(sc, vault, t10 + .1, { dy: 0, scale: 1.05 });
    rows.forEach((r, i) => { const k = icon('key-round', 24, r, 'y'); k.style.marginLeft = '16px'; appear(sc, k, Wd('10', 'each field') + i * .3, { dy: 0, dx: 12 }); });
    flag(sc, card, 'hot', t10 + .3, V('11'));
    appear(sc, T(wd, 580, 612, 'mono sm dim', 'field-level keys · per-tenant vault', 420), Wd('10', 'own key'), { dy: 10 });
    // salted hashes
    const t11 = V('11');
    const hashes = ['9f3a·c21e·07b4', '4b70·18d2·e5a9', 'e61c·7a90·3fd1'];
    const hp = hashes.map((h, i) => {
      const y = 355 + i * 70;
      draw(sc, P(s, `M985 ${y} H1110`), t11 + .2 + i * .25, .5);
      const salt = el('div', 'a pill y', wd, '+ salt'); pos(salt, 1000, y - 17); salt.style.fontSize = '13px';
      appear(sc, salt, t11 + .5 + i * .25, { dy: 0, scale: .6 });
      const hb = el('div', 'a hashpill', wd); pos(hb, 1110, y - 22, 230, 44);
      const hs = el('span', '', hb); scramble(sc, hs, h, t11 + .8 + i * .3, 1.0);
      appear(sc, hb, t11 + .7 + i * .3, { dy: 0, blur: 0 });
      return hb;
    });
    // why salt: the guessing attack
    const tg = Wd('11', 'eight hundred'), tu = Wd('11', 'unsalted');
    const box = el('div', 'a card', wd); pos(box, 580, 670, 760, 150);
    const r1 = el('div', 'grow', box); r1.innerHTML = '<span class="mono lc">hash("NOI = 800,000")</span><span class="arrow">→</span><span class="mono lc">5e2b·91c0</span><span class="verdict dim">guess it, hash it → match: leaked</span>';
    const r2 = el('div', 'grow', box); r2.innerHTML = '<span class="mono lc">hash("NOI = 800,000" + salt)</span><span class="arrow">→</span><span class="mono lc y">e61c·7a90</span><span class="verdict y">salt unknown → unguessable</span>';
    appear(sc, r1, tg, { dx: -16, dy: 0 }); appear(sc, r2, tu + .3, { dx: -16, dy: 0 });
    flag(sc, r1, 'bad', tu - .2);
    appear(sc, box, tg - .3, { dy: 20, out: V('12') + .6 });
    // Merkle roll-up
    const t12 = V('12'), RX = 1600, RYt = 425;
    draw(sc, P(s, 'M1340 355 C1400 355 1400 390 1450 390'), t12 + .3, .6);
    draw(sc, P(s, 'M1340 425 C1400 425 1400 390 1450 390'), t12 + .3, .6);
    const n12 = sv('circle', { cx: 1460, cy: 390, r: 10, fill: '#141416', class: 'ln' }, s); appear(sc, n12, t12 + .8, { dy: 0, blur: 0 });
    draw(sc, P(s, 'M1470 390 C1520 390 1530 425 1566 425', 'ln y'), t12 + 1.0, .6);
    draw(sc, P(s, 'M1340 495 C1450 495 1500 425 1566 425', 'ln y'), t12 + 1.0, .6);
    const root = el('div', 'a root', wd); pos(root, RX - 34, RYt - 34, 68, 68);
    appear(sc, root, Wd('12', 'Merkle root'), { dy: 0, blur: 0, scale: .3 });
    appear(sc, T(wd, RX - 110, RYt + 50, 'mono sm y center', 'Merkle root', 220), Wd('12', 'Merkle root') + .2, { dy: 8 });
    appear(sc, T(wd, RX - 110, RYt + 76, 'mono sm dim center', 'per asset · per period', 220), Wd('12', 'per asset'), { dy: 8 });
    // attestation: independent sources sign, quorum ring fills, level
    const t13 = V('13');
    const ring = sv('circle', { cx: RX, cy: RYt, r: 56, class: 'ln y', 'stroke-width': 3, transform: `rotate(-90 ${RX} ${RYt})` }, s);
    ring.setAttribute('pathLength', 1);
    const tq = Wd('13', 'quorum');
    sc.on(t => { const k = clamp((t - (t13 + 1.6)) / (tq - t13 - 1.2)); const seg = Math.min(3, Math.floor(k * 3 + 1e-6)) / 3; const f = (t < t13 + 1.6) ? 0 : Math.max(seg, 0); ring.style.strokeDasharray = `${f} 1`; ring.style.opacity = f > 0 ? 1 : 0; });
    ['Source 1', 'Source 2', 'Source 3'].forEach((nm, i) => {
      const x = 1440 + i * 160, y = 160;
      const n = el('div', 'a srcnode', wd); pos(n, x - 36, y - 36, 72, 72); icon('signature', 32, n, 'y');
      appear(sc, n, t13 + .3 + i * .25, { dy: -16 });
      appear(sc, T(wd, x - 80, y + 44, 'mono sm dim center', nm, 160), t13 + .5 + i * .25, { dy: 0 });
      const d = `M${x} ${y + 64} C${x} ${y + 150} ${RX + (i - 1) * 30} ${RYt - 120} ${RX + (i - 1) * 20} ${RYt - 60}`;
      draw(sc, P(s, d), t13 + .6 + i * .25, .7);
      pulse(sc, s, P(s, d, '', { fill: 'none' }), t13 + 1.2 + i * .45, .9);
    });
    appear(sc, T(wd, 1330, 90, 'mono sm y', 'Independent sources of the fact', 520), t13 + .2, { dy: 0 });
    const lvl = el('div', 'a pill solid', wd, 'Level A2'); pos(lvl, RX + 76, RYt - 20);
    appear(sc, lvl, Wd('13', 'level'), { dx: -16, dy: 0 });
    appear(sc, T(wd, RX + 76, RYt + 26, 'mono sm y', 'Quorum ✓', 200), tq + .2, { dy: 0 });
    // the ledger: root, signatures and level go on chain; the rent roll never does
    const t14 = V('14'), LY = 900;
    const rl = rail(wd, s, 80, 1840, LY, 'Ledger', 'on chain');
    appear(sc, rl, t14 - .2, { dy: 30 });
    const tokens = [['root', Wd('14', 'the root')], ['signatures', Wd('14', 'signatures')], ['level', Wd('14', 'level')]];
    tokens.forEach(([nm, t], i) => {
      const tk = el('div', 'a pill y tok', wd); tk.innerHTML = `# ${nm}`; appear(sc, tk, t, { dy: 0, blur: 0 });
      follow(sc, tk, s, `M${RX} ${RYt + 40} C${RX} ${RYt + 250} ${1250 + i * 190} ${LY - 200} ${1250 + i * 190} ${LY}`, t, 1.2, { w: 150, h: 36, e: ease.out });
    });
    const off = T(wd, 580, 612, 'mono sm', '', 460); off.innerHTML = '<span class="y">✕</span> the rent roll · never on chain';
    appear(sc, off, Wd('14', 'rent roll itself'), { dy: 0 });
    sc.on(t => { vault.style.borderColor = t > Wd('14', 'rent roll itself') ? 'rgba(255,190,6,.7)' : ''; });
    camera(sc, wd, [
      [57.5, 380, 430, 1.5], [tAd + .2, 420, 430, 1.5], [tIn + .3, 700, 430, 1.35], [t10, 800, 420, 1.3],
      [t11 - .2, 800, 420, 1.3], [t11 + 1.2, 1000, 530, 1.1], [t12 - .2, 1000, 530, 1.1], [t12 + .8, 1320, 420, 1.2],
      [t13 - .2, 1320, 420, 1.2], [t13 + .6, 1420, 330, 1.12], [t14 - .6, 1420, 330, 1.12], [t14 + .8, 960, 540, .98], [101.9, 960, 540, .96]]);
  }
}
