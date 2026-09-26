// Scenes 11–18: integration (stages, adapters, a bank), keeping value safe, build sequence, end card.
'use strict';

function buildScenes3() {
  // ================================================================ 11 · INTEGRATION
  chapter(177.5, 209.0, '07', 'Integration');
  {
    const sc = new Scene(177.4, 181.7, { fadeIn: .4, fadeOut: .5 });
    stock(sc, 'team', 177.4, 181.7, { from: .5, zoom: [1.03, 1.09] });
    appear(sc, T(sc.el, 160, 780, 'h2', 'Zero change to their workflow.', 1400), 177.9);
  }
  {
    const sc = new Scene(181.4, 191.4);
    const s = sc.svg();
    const tS = Wd('22', 'First, shadow'), tWb = Wd('22', 'write back'), tWf = Wd('22', 'work on the platform');
    const st = [['1 · Shadow', 'read only', tS], ['2 · Write back', 'their format, our lineage', tWb], ['3 · Workflow', 'they act on the platform', tWf]];
    st.forEach(([a, b, t], i) => {
      const p = el('div', 'a stage', sc.el); pos(p, 260 + i * 480, 170, 440, 84);
      el('div', 'mono y', p, a); el('div', 'mono sm dim lc', p, b).style.marginTop = '6px';
      appear(sc, p, t - .3, { dy: -12 }); flag(sc, p, 'lit', t, i < 2 ? st[i + 1][2] : 1e9);
    });
    // their system (never changes)
    const th = el('div', 'a card', sc.el); pos(th, 160, 320, 560, 470);
    const hh = el('div', 'nodehd', th); el('span', 'mono sm dim', hh, 'Their system of record'); icon('server', 32, hh);
    ['ERP', 'Property system', 'Loan book', 'Fund admin', 'PDFs & spreadsheets'].forEach(x => el('div', 'sysrow', th, x));
    const un = el('div', 'a pill', sc.el, 'unchanged'); pos(un, 190, 810);
    appear(sc, th, 181.6, { dx: -30, dy: 0 }); appear(sc, un, 182.3, { dy: 10 });
    // ours
    const ou = el('div', 'a card', sc.el); pos(ou, 1200, 320, 560, 470);
    const oh = el('div', 'nodehd', ou); el('span', 'mono sm y', oh, 'Propchain · system of proof'); icon('shield-check', 32, oh, 'y');
    const rowsO = ['ERP', 'Property system', 'Loan book', 'Fund admin', 'PDFs & spreadsheets'].map(x => { const r = el('div', 'sysrow att', ou, '✓ ' + x + ' · attested copy'); return r; });
    appear(sc, ou, tS, { dx: 30, dy: 0 });
    rowsO.forEach((r, i) => appear(sc, r, tS + .6 + i * .2, { dx: -14, dy: 0 }));
    const d1 = 'M720 440 H1200'; draw(sc, P(s, d1), tS + .2, .6); pulse(sc, s, P(s, d1, '', { fill: 'none' }), tS + .3, 1.0, { repeat: 3, period: 1.1, color: '#F4F2EC', len: .1 });
    appear(sc, T(sc.el, 760, 400, 'mono sm dim', 'adapters read', 300), tS + .4, { dy: 0 });
    const d2 = 'M1200 580 H720'; draw(sc, P(s, d2, 'ln y'), tWb, .6); pulse(sc, s, P(s, d2, '', { fill: 'none' }), tWb + .2, 1.0, { repeat: 3, period: 1.1 });
    const wb = T(sc.el, 740, 600, 'mono sm y lc', 'reporting pack · financing template<br>covenant certificate', 460); appear(sc, wb, tWb + .4, { dy: 0 });
    const d3 = 'M440 790 C440 900 1480 900 1480 790'; draw(sc, P(s, d3, 'ln dash'), tWf, .8);
    const us = el('div', 'a usr', sc.el); icon('users', 30, us, 'y'); appear(sc, us, tWf, { dy: 0, blur: 0 });
    follow(sc, us, s, d3, tWf, 1.6, { w: 56, h: 56 });
    const wf = T(sc.el, 1240, 810, 'mono sm y lc', 'mandates · credit boxes · closings', 520); appear(sc, wf, tWf + 1.2, { dy: 8 });
    appear(sc, T(sc.el, 0, 950, 'mono dim center', "…because it's faster", 1920), Wd('22', 'faster'), { dy: 8 });
  }
  // ---------------------------------------------------------------- adapters: one untrusted source each
  {
    const sc = new Scene(191.2, 199.2);
    const s = sc.svg(), t23 = V('23'), tc = Wd('23', 'compromised'), tq = Wd('23', 'cannot reach');
    appear(sc, T(sc.el, 0, 140, 'h3 center', 'One canonical schema, many adapters, an event bus between', 1920), t23 - .2, { dy: 12 });
    const src = ['ERP, accounting', 'Property management', 'Loan origination', 'Fund administration', 'Data rooms', 'Registries, notaries', 'Files and email'];
    const BX = 900, QX = 1600, QY = 560;
    const bus = el('div', 'a bus', sc.el); pos(bus, BX - 18, 240, 36, 640); appear(sc, bus, t23, { dy: 0 });
    appear(sc, T(sc.el, BX - 100, 895, 'mono sm dim center', 'Event bus', 200), t23 + .2, { dy: 0 });
    src.forEach((nm, i) => {
      const y = 260 + i * 88, bad = i === 1;
      const r = el('div', 'a srcrow', sc.el, nm); pos(r, 150, y, 400, 60); appear(sc, r, t23 + i * .08, { dx: -20, dy: 0 });
      const a = el('div', 'a adp', sc.el); pos(a, 620, y + 4, 52, 52); icon(bad ? 'triangle-alert' : 'plug', 26, a, bad ? 'y' : ''); appear(sc, a, t23 + .2 + i * .08, { dy: 0, scale: .6 });
      if (bad) { flag(sc, a, 'badadp', tc); flag(sc, r, 'lit', tc); }
      draw(sc, P(s, `M550 ${y + 30} H620`), t23 + .2, .4); draw(sc, P(s, `M672 ${y + 30} H${BX - 18}`), t23 + .3, .4);
      pulse(sc, s, P(s, `M672 ${y + 30} H${BX - 18}`, '', { fill: 'none' }), t23 + .5 + i * .13, .6, { color: '#F4F2EC', len: .2, r: 3, width: 2, repeat: 2, period: 1.5, until: tc });
    });
    const sch = el('div', 'a card center', sc.el); pos(sch, 1010, 500, 300, 120);
    el('div', 'mono sm y', sch, 'Canonical schema').style.paddingTop = '26px'; el('div', 'mono sm dim lc', sch, 'validated · one source each').style.marginTop = '10px';
    appear(sc, sch, t23 + .4, { dy: 0, scale: .9 });
    draw(sc, P(s, `M${BX + 18} 560 H1010`), t23 + .5, .4);
    // quorum ring: only one segment ever fills from the bad adapter
    const ring = sv('circle', { cx: QX, cy: QY, r: 80, class: 'ln', 'stroke-width': 3, transform: `rotate(-90 ${QX} ${QY})`, pathLength: 1 }, s);
    const ringY = sv('circle', { cx: QX, cy: QY, r: 80, class: 'ln y', 'stroke-width': 4, transform: `rotate(-90 ${QX} ${QY})`, pathLength: 1 }, s);
    appear(sc, ring, t23 + .6, { dy: 0, blur: 0 });
    sc.on(t => { const k = clamp((t - (tc + 1.6)) / .6); ringY.style.strokeDasharray = `${(k / 3).toFixed(3)} 1`; ringY.style.opacity = k > 0 ? 1 : 0; });
    appear(sc, T(sc.el, QX - 110, QY - 14, 'mono sm center', 'Quorum', 220), t23 + .7, { dy: 0 });
    draw(sc, P(s, `M1310 560 H${QX - 80}`), t23 + .6, .4);
    const badp = `M672 378 H${BX - 18}`;
    pulse(sc, s, P(s, `M646 378 C760 378 800 470 ${BX} 540 S 1300 560 ${QX - 82} 560`, '', { fill: 'none' }), tc + .3, 1.4);
    const l1 = T(sc.el, QX - 190, QY + 110, 'mono sm center lc', '<span class="y">1 / 3</span> · one source is never truth', 380); appear(sc, l1, tq - .2, { dy: 8 });
    const l2 = T(sc.el, 150, 900, 'h3', 'Can lie. <span class="y">Cannot reach a quorum alone.</span>', 1100);
    appear(sc, l2, Wd('23', 'can lie'), { dy: 12 });
  }
  // ---------------------------------------------------------------- a bank, worked
  {
    const sc = new Scene(199.0, 209.2);
    const s = sc.svg(), t24 = V('24');
    appear(sc, T(sc.el, 0, 140, 'h3 center', 'A loan today, and the three connectors that sit beside it', 1920), t24 - .2, { dy: 12 });
    const stg = [['Apply', 'financing pack arrives · data room, spreadsheets'], ['Underwrite', 'origination system · credit memo · committee'], ['Service', 'servicing system · payments · covenant tests']];
    stg.forEach(([a, b], i) => {
      const c = el('div', 'a card', sc.el); pos(c, 180 + i * 540, 250, 480, 150);
      el('div', 'nodet', c, a).style.paddingTop = '10px'; el('div', 'nodes', c, b);
      appear(sc, c, t24 + i * .15, { dy: -14 });
      if (i < 2) { const ch = T(sc.el, 668 + i * 540, 300, 'mono dim', '→', 40); appear(sc, ch, t24 + .3, { dy: 0 }); }
    });
    const con = [['1 · Pack in', "the bank's own template · every field attested with level and source", 'financing pack', 1],
      ['2 · Credit box out', "credit policy as a standing box · indicative terms fire, firm terms go to committee", 'credit policy', -1],
      ['3 · Servicing feed', 'covenant tests and reporting from platform state · the bank sees the asset monthly', 'servicing feed', 1]];
    con.forEach(([a, b, w, dir], i) => {
      const t = Wd('24', w), x = 180 + i * 540;
      const c = el('div', 'a card conn', sc.el); pos(c, x, 560, 480, 190);
      el('div', 'mono y', c, a).style.cssText = 'padding:22px 24px 0'; el('div', 'nodes', c, b).style.cssText = 'padding:12px 24px 0;font-size:16px';
      appear(sc, c, t - .2, { dy: 24 }); flag(sc, c, 'lit', t, t + 1.8);
      const d = dir > 0 ? `M${x + 240} 560 V400` : `M${x + 240} 400 V560`;
      draw(sc, P(s, `M${x + 240} 400 V560`, 'ln y'), t, .4);
      pulse(sc, s, P(s, d, '', { fill: 'none' }), t + .2, .7, { repeat: 4, period: 1.1, len: .3 });
    });
    const nb = T(sc.el, 0, 820, 'h3 center', 'Neither bank system is replaced.', 1920); appear(sc, nb, Wd('24', 'Neither'), { dy: 12 });
  }

  // ================================================================ 12 · KEEPING VALUE SAFE
  chapter(209.0, 230.6, '08', 'Keeping value safe');
  {
    const sc = new Scene(209.0, 221.3);
    const s = sc.svg(), t25 = V('25');
    const tb = Wd('25', 'data breach'), tk = Wd('25', 'key compromise'), tsep = Wd('25', 'different keys');
    appear(sc, T(sc.el, 0, 150, 'h2 center', 'Value and data are separate threats', 1920), t25, { dy: 12 });
    const col = (x, ic, lab, what, cost, t, hot) => {
      const c = el('div', 'a card' + (hot ? ' hot' : ''), sc.el); pos(c, x, 290, 600, 250);
      const h = el('div', 'nodehd', c); el('span', 'mono ' + (hot ? 'y' : 'dim'), h, lab); icon(ic, 40, h, hot ? 'y' : '');
      el('div', 'h3', c, what).style.cssText = 'padding:22px 20px 0';
      el('div', 'mono sm dim lc', c, cost).style.cssText = 'padding:14px 20px 0';
      appear(sc, c, t, { dy: 20 });
    };
    col(260, 'file-text', 'Data', 'A breach', '→ confidentiality and reputation', tb, false);
    col(1060, 'vault', 'Value', 'A key compromise', '→ money gone', tk, true);
    draw(sc, P(s, 'M960 280 V900', 'ln dash'), tsep - .3, .8);
    [['different keys', 'data keys', 'value keys'], ['networks', 'data network', 'settlement network'], ['teams', 'data team', 'custody team']].forEach(([w, a, b], i) => {
      const t = Wd('25', w), y = 600 + i * 90;
      const l = el('div', 'a sepr', sc.el, a); pos(l, 260, y, 600, 64); const r = el('div', 'a sepr y', sc.el, b); pos(r, 1060, y, 600, 64);
      appear(sc, l, t, { dx: 30, dy: 0 }); appear(sc, r, t, { dx: -30, dy: 0 });
    });
    appear(sc, T(sc.el, 0, 890, 'mono sm dim center', 'data: encrypted per field · access is a grant, never a role · no admin key', 1920), tsep + 2.0, { dy: 8 });
  }
  {
    const sc = new Scene(221.1, 230.8);
    const s = sc.svg(), t26 = V('26');
    appear(sc, T(sc.el, 0, 150, 'h2 center', 'Assume a key will be compromised', 1920), t26, { dy: 12 });
    const cols = [['Alone', 1, 'Nothing on its own', 'no single key moves value · threshold signing · keys in HSMs'],
      ['second', 2, 'Only a little', 'time-locks · velocity limits · allow-listed destinations only'],
      ['third', 3, 'Reversed', 'freeze and clawback · circuit breakers · monitoring that pages a human']];
    cols.forEach(([w, n, big, small], i) => {
      const t = Wd('26', w), x = 200 + i * 520;
      const c = el('div', 'a card', sc.el); pos(c, x, 300, 480, 330);
      const keys = el('div', 'keys', c);
      for (let k = 0; k < 3; k++) { const ki = icon('key-round', 44, keys, k < n ? 'y' : 'dim'); ki.style.opacity = k < n ? 1 : .22; }
      el('div', 'mono sm dim', c, n === 1 ? 'one compromised key' : n === 2 ? 'with a second' : 'with a third').style.cssText = 'padding:18px 26px 0';
      el('div', 'h3', c, big).style.cssText = 'padding:10px 26px 0' + (i === 2 ? ';color:var(--y)' : '');
      el('div', 'nodes', c, small).style.cssText = 'padding:18px 26px 0;font-size:16px';
      appear(sc, c, t - .1, { dy: 24 }); flag(sc, c, 'lit', t + .2, i < 2 ? Wd('26', cols[i + 1][0]) : 1e9);
    });
    appear(sc, T(sc.el, 0, 720, 'h3 center', 'Agents hold no value keys. Ever.', 1920), Wd('26', 'reversed') + .6, { dy: 10 });
    appear(sc, T(sc.el, 0, 800, 'mono sm dim center', 'value moves only to addresses bound to a Know Your Agent identity', 1920), Wd('26', 'reversed') + 1.2, { dy: 8 });
  }

  // ================================================================ 13 · BUILD SEQUENCE
  chapter(230.6, 235.7, '09', 'The build sequence');
  {
    const sc = new Scene(230.6, 235.9);
    const ph = ['Commit first.', 'Connect second.', 'Match third.', 'Settle last.'];
    const hd = T(sc.el, 0, 250, 'h2 center', ph.map(p => `<span>${p}</span>`).join(' '), 1920);
    ph.forEach((p, i) => { const t = Wd('27', p.replace('.', '')); appear(sc, hd.children[i], t - .1, { dy: 14 }); flag(sc, hd.children[i], 'lit', t, i < 3 ? Wd('27', ph[i + 1].replace('.', '')) : 1e9); });
    const cols = [['Now', ['Salted commitments, roots, grant log', 'Identity and agent credentials', 'Record store with field keys and HSM', 'Adapters for the internal portfolio']],
      ['Next', ['Permissioned network, named validators', 'Bank connectors: pack in, box out', 'Matching engine in an attested enclave', 'Escrow on tokenised deposits']],
      ['Later', ['Range proofs for double-blind filters', 'Atomic DvP with notary execution', 'Public anchoring, validator expansion', 'Own settlement asset, if ever']]];
    cols.forEach(([h, items], i) => {
      const c = el('div', 'a card', sc.el); pos(c, 200 + i * 520, 420, 480, 380);
      el('div', 'mono y', c, h).style.cssText = 'padding:24px 26px 8px';
      items.forEach(x => el('div', 'bitem', c, x));
      appear(sc, c, 231.0 + i * .25, { dy: 24 });
    });
  }

  // ================================================================ 14 · END CARD
  {
    const sc = new Scene(235.6, window.END, { fadeIn: .6, fadeOut: 1.0 });
    const lg = el('img', 'a', sc.el); lg.src = '../assets/logo-white.svg'; lg.style.height = '64px'; pos(lg, 960 - 236, 440);
    appear(sc, lg, 235.8, { dy: 0, scale: .94 });
    appear(sc, T(sc.el, 0, 560, 'h3 center dim', 'Provable, not visible.', 1920), 236.4, { dy: 12 });
    appear(sc, T(sc.el, 0, 640, 'mono sm faint center', 'Technical architecture · working draft · September 2026', 1920), 236.9, { dy: 8 });
  }
}
