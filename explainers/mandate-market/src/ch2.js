// 02 THE OBJECTS — asset (attested vector with lineage), buy mandate, credit box, seller.
import { T, h, s, svg, box, I, scene, rise, fade, draw, pulseDot, pr, eo, e3, eio, lerp, clamp, Y } from './core.js';

export default function ch2() {
  const W = T.W.bind(T), L = T.L.bind(T), E = T.E.bind(T);
  const t0 = L('04') - .5, t1 = E('06') + .9;
  const sc = scene(t0, t1, update);
  const root = sc.el;

  const head = box(root, 140, 150, 'head', 'Three object types, <b>not three sides</b>.');

  // ---------------- cards
  const mk = (x, w, n, name, title) => {
    const c = box(root, x, 270, 'card solid', '', { width: w + 'px', height: '690px' });
    box(c, 36, 34, 'eyebrow y', `${n} · ${name}`);
    box(c, 36, 72, '', title, { fontSize: '34px', fontWeight: 300, letterSpacing: '-.01em' });
    return c;
  };
  const cA = mk(140, 760, '01', 'Asset', 'The instance object');
  const cM = mk(940, 400, '02', 'Buy mandate', 'A standing intent');
  const cC = mk(1380, 400, '03', 'Credit box', 'A conditional intent');

  // asset rows: dimension · attested from · refresh · confidence
  const rows = [
    ['NOI', 'Rent roll · Proof of State', '30 days', .95, 'income'],
    ['Cap rate', 'Derived: NOI over price', 'with NOI', .95, 'cap'],
    ['WALT', 'Lease register', 'lease event', .9, 'lease'],
    ['Tenant credit', 'Rating feeds, arrears', 'quarterly', .8, 'tenant'],
    ['Vacancy', 'Rent roll', '30 days', .92, 'credit'],
  ];
  const hdr = box(cA, 36, 150, '', '', { width: '690px' });
  [['Dimension', 0], ['Source', 180], ['Refresh', 474], ['Confidence', 610]].forEach(([n, x]) => box(hdr, x, 0, 'tag', n));
  const hdrCols = [...hdr.children];
  const R = rows.map(([d, src, ref, conf, cue], i) => {
    const r = box(cA, 36, 190 + i * 66, '', '', { width: '690px', height: '56px' });
    box(r, 0, -12, 'rule', '', { width: '690px' });
    box(r, 0, 12, '', d, { fontSize: '24px' });
    const a = box(r, 180, 16, 'mono', `<span style="display:inline-flex;gap:8px;align-items:center">${I('file-check', 18)}${src}</span>`, { fontSize: '15px', color: 'rgba(244,242,236,.7)' });
    const b = box(r, 474, 16, 'mono', `<span style="display:inline-flex;gap:8px;align-items:center">${I('clock', 18)}${ref}</span>`, { fontSize: '15px', color: 'rgba(244,242,236,.7)' });
    const track = box(r, 610, 22, '', '', { width: '80px', height: '8px', borderRadius: '4px', background: 'rgba(244,242,236,.1)' });
    const fill = box(track, 0, 0, '', '', { height: '8px', borderRadius: '4px', background: Y, width: conf * 80 + 'px', transformOrigin: '0 50%' });
    return { r, a, b, track, fill, cue };
  });
  const sellerRow = box(cA, 36, 548, '', `<div class="rule" style="width:690px;position:relative"></div><div style="display:flex;justify-content:space-between;margin-top:22px"><span class="tag">Seller instruction</span><span class="mono" style="font-size:16px;color:rgba(244,242,236,.7)">ask · reserve · timing · conditions</span></div>`, { width: '690px' });
  const sellerChip = box(cA, 36, 624, 'chip yo', `${I('user-check', 18, Y)} Seller: the fourth scorer · ranks the bids`);

  // mandate: scores many assets, names none
  const mTxt = box(cM, 36, 140, 'sub', 'Scores assets.<br>Never names one.', { fontSize: '24px' });
  const mRows = [['Logistics · Hamburg', .82], ['Logistics · Bremen', .71], ['Office · Frankfurt', 0], ['Logistics · Leipzig', .44]].map(([n, v], i) => {
    const r = box(cM, 36, 270 + i * 74, '', '', { width: '328px', height: '60px' });
    box(r, 0, 0, '', `<div style="display:flex;gap:10px;align-items:center">${I('warehouse', 20, 'rgba(244,242,236,.7)')}<span style="font-size:18px">${n}</span></div>`);
    const tr = box(r, 0, 36, '', '', { width: '260px', height: '6px', borderRadius: '3px', background: 'rgba(244,242,236,.1)' });
    const f = box(tr, 0, 0, '', '', { height: '6px', borderRadius: '3px', background: i === 0 ? Y : 'rgba(244,242,236,.6)', width: v * 260 + 'px', transformOrigin: '0 50%' });
    const n_ = box(r, 276, 26, 'mono', v ? v.toFixed(2) : 'out', { fontSize: '15px', color: v ? '#F4F2EC' : 'rgba(244,242,236,.4)' });
    return { r, f, n_ };
  });
  const mFoot = box(cM, 36, 600, 'tag', 'Rests in the book until filled, amended or withdrawn', { width: '330px', lineHeight: '1.6' });

  // credit box
  const cTxt = box(cC, 36, 140, 'sub', 'Scores the asset,<br>given the buyer.', { fontSize: '24px' });
  const cForm = box(cC, 36, 270, 'mono', 'quote( asset <span class="y">|</span> sponsor )', { fontSize: '22px' });
  const cFields = ['LTV cap', 'DSCR floor', 'Spread grid', 'Sponsor tier', 'Capacity'].map((f, i) => box(cC, 36 + (i % 2) * 168, 340 + Math.floor(i / 2) * 62, 'chip', f));
  const cFoot = box(cC, 36, 600, 'tag', 'Size shrinks as it fills: the closest thing to a resting limit order', { width: '330px', lineHeight: '1.6' });

  function update(t) {
    rise(head, t, t0 + .2);
    rise(cA, t, W('04', 'three') - .1, { dy: 40 });
    rise(cM, t, W('04', 'three') + .12, { dy: 40 });
    rise(cC, t, W('04', 'three') + .24, { dy: 40 });
    // focus
    const fM = W('05', 'buy') - .2, fC = W('06', 'credit') - .2, fS = W('06', 'seller') - .1;
    const focus = t < fM ? 0 : t < fC ? 1 : t < fS ? 2 : 0;
    [cA, cM, cC].forEach((c, i) => {
      const hot = i === focus && t > W('04', 'asset') - .2;
      c.classList.toggle('hot', hot);
      const dimmed = t > W('04', 'asset') - .2 && !hot;
      c.style.opacity = Math.min(parseFloat(c.style.opacity || 1), dimmed ? .5 : 1);
    });
    hdrCols.forEach((c, i) => fade(c, t, [W('04', 'income') - .3, W('04', 'source'), W('04', 'timestamp'), W('04', 'confidence')][i], .5));
    R.forEach((r, i) => {
      rise(r.r, t, W('04', r.cue) - .15, { dx: -20, dy: 0 });
      fade(r.a, t, W('04', 'source') + i * .06, .5);
      fade(r.b, t, W('04', 'timestamp') + i * .06, .5);
      fade(r.track, t, W('04', 'confidence') + i * .06, .5);
      r.fill.style.transform = `scaleX(${pr(t, W('04', 'confidence') + .1 + i * .08, .9)})`;
    });
    rise(sellerRow, t, W('04', 'confidence') + .8);
    rise(sellerChip, t, fS, { dx: -20, dy: 0 });
    // mandate
    rise(mTxt, t, fM + .2);
    mRows.forEach((r, i) => { rise(r.r, t, fM + .5 + i * .1, { dy: 12 }); r.f.style.transform = `scaleX(${pr(t, W('05', 'scores') + i * .15, .8)})`; fade(r.n_, t, W('05', 'scores') + .5 + i * .15, .4); });
    rise(mFoot, t, W('05', 'scores') + .8);
    // credit box
    rise(cTxt, t, fC + .2); rise(cForm, t, W('06', 'given') - .1);
    cFields.forEach((f, i) => rise(f, t, W('06', 'given') + .3 + i * .1, { dy: 10 }));
    rise(cFoot, t, W('06', 'buying') + .4);
  }
}
