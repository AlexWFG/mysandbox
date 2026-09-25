// Procedural texture atlases: the "before" (fragmented real-estate paperwork)
// and the "after" (structured, machine-readable data records).
import { rng } from './util.js';

export const ATLAS_COLS = 8, ATLAS_ROWS = 8;
const DW = 256, DH = 362;   // A-series portrait
const CW = 256, CH = 256;

const TITLES = [
  ['VALUATION REPORT', 'Mixed-use asset · Berlin-Mitte'], ['MIETVERTRAG', 'Gewerbeeinheit 3. OG'],
  ['RENT ROLL Q3', 'final_v7_REVISED.xlsx'], ['GRUNDBUCHAUSZUG', 'Amtsgericht Frankfurt'],
  ['TITLE DEED', 'Dubai Land Department'], ['SERVICE CHARGE', 'Budget 2026 · DRAFT'],
  ['LEASE AGREEMENT', 'Unit 1402 · Tower B'], ['TECHNICAL DD', 'Building survey'],
  ['EPC CERTIFICATE', 'Energy class C'], ['CAPEX PLAN', 'scan_0043.pdf'],
  ['INVOICE', 'Facility management'], ['LOAN AGREEMENT', 'Senior facility'],
  ['ESG REPORT', 'Scope 1-3 estimate'], ['NOTARIAL DEED', 'Urkundenrolle Nr.'],
  ['INSURANCE POLICY', 'Property all-risk'], ['SITE VISIT NOTES', 'handwritten'],
];

const MONO = '"Mono", monospace', SANS = '"Inter", sans-serif';

function paperColor(r) {
  const k = r();
  if (k < 0.45) return [246, 244, 238];
  if (k < 0.75) return [238, 232, 216];   // cream
  if (k < 0.9) return [228, 224, 214];    // grey scan
  return [232, 220, 190];                  // yellowed archive
}

function bars(ctx, r, x, y, w, lines, lh, color) {
  ctx.fillStyle = color;
  for (let i = 0; i < lines; i++) {
    const lw = i === lines - 1 ? w * (0.3 + r() * 0.4) : w * (0.82 + r() * 0.18);
    ctx.fillRect(x, y + i * lh, lw, Math.max(2, lh * 0.36));
  }
  return y + lines * lh;
}

function drawDoc(ctx, i) {
  const r = rng(1000 + i * 17);
  const type = i % 6;
  const [pr, pg, pb] = paperColor(r);
  ctx.fillStyle = `rgb(${pr},${pg},${pb})`;
  ctx.fillRect(0, 0, DW, DH);
  const [title, subt] = TITLES[(i * 5 + (i >> 3)) % TITLES.length];
  const ink = 'rgba(28,28,30,0.85)', soft = 'rgba(40,40,44,0.28)';
  const m = 20;
  ctx.save();
  if (type === 3) { ctx.translate(DW / 2, DH / 2); ctx.rotate((r() - 0.5) * 0.06); ctx.translate(-DW / 2, -DH / 2); }

  if (type === 0 || type === 3 || type === 5) {
    // Report / registry extract / deed
    ctx.fillStyle = ink; ctx.font = `600 15px ${SANS}`; ctx.fillText(title, m, 40);
    ctx.fillStyle = 'rgba(40,40,44,.55)'; ctx.font = `400 10px ${SANS}`; ctx.fillText(subt, m, 56);
    ctx.fillStyle = soft; ctx.fillRect(m, 66, DW - 2 * m, 1);
    let y = 84;
    if (type === 0 && r() < 0.7) {
      // photo box
      const g = ctx.createLinearGradient(0, y, 0, y + 90);
      g.addColorStop(0, '#9aa0a6'); g.addColorStop(1, '#4b4f55');
      ctx.fillStyle = g; ctx.fillRect(m, y, DW - 2 * m, 90);
      ctx.fillStyle = 'rgba(20,20,22,.55)';
      for (let k = 0; k < 6; k++) { const bw = 14 + r() * 26, bh = 30 + r() * 60; ctx.fillRect(m + 8 + k * 36, y + 90 - bh, bw, bh); }
      y += 104;
    }
    y = bars(ctx, r, m, y, DW - 2 * m, 5 + (r() * 5 | 0), 11, soft) + 10;
    if (type === 3) {
      // table rows
      ctx.strokeStyle = 'rgba(30,30,34,.35)'; ctx.lineWidth = 1;
      for (let k = 0; k < 6; k++) { ctx.strokeRect(m, y + k * 16, DW - 2 * m, 16); }
      ctx.beginPath(); ctx.moveTo(m + 60, y); ctx.lineTo(m + 60, y + 96); ctx.stroke();
      ctx.fillStyle = soft; for (let k = 0; k < 6; k++) ctx.fillRect(m + 68, y + k * 16 + 6, 60 + r() * 80, 4);
      y += 108;
    }
    y = bars(ctx, r, m, y, DW - 2 * m, 4 + (r() * 4 | 0), 11, soft);
    // stamp
    if (r() < 0.8) {
      const sx = DW - 70 - r() * 40, sy = DH - 70 - r() * 30;
      ctx.save(); ctx.translate(sx, sy); ctx.rotate(-0.3 + r() * 0.3);
      const blue = r() < 0.5;
      ctx.strokeStyle = blue ? 'rgba(40,70,160,.55)' : 'rgba(170,40,40,.5)'; ctx.lineWidth = 3;
      ctx.beginPath(); ctx.arc(0, 0, 30, 0, Math.PI * 2); ctx.stroke();
      ctx.beginPath(); ctx.arc(0, 0, 22, 0, Math.PI * 2); ctx.lineWidth = 1.5; ctx.stroke();
      ctx.fillStyle = ctx.strokeStyle; ctx.font = `600 8px ${SANS}`; ctx.textAlign = 'center';
      ctx.fillText(blue ? 'BEGLAUBIGT' : 'RECEIVED', 0, 3); ctx.restore();
    }
    // signature
    ctx.strokeStyle = 'rgba(20,30,90,.6)'; ctx.lineWidth = 1.6; ctx.beginPath();
    let sx = m + 4, sy = DH - 40; ctx.moveTo(sx, sy);
    for (let k = 0; k < 9; k++) { sx += 8 + r() * 6; ctx.quadraticCurveTo(sx - 4, sy - 16 * r(), sx, sy + (r() - 0.5) * 10); }
    ctx.stroke();
  } else if (type === 1 || type === 4) {
    // Spreadsheet
    const green = type === 1;
    ctx.fillStyle = green ? '#1f6e43' : '#2b2f36'; ctx.fillRect(0, 0, DW, 26);
    ctx.fillStyle = '#fff'; ctx.font = `500 11px ${MONO}`; ctx.fillText(subt.length > 22 ? 'rent_roll_FINAL(3).xlsx' : subt, 10, 17);
    const cw = [34, 70, 56, 56], rh = 15;
    ctx.font = `400 8.5px ${MONO}`;
    for (let row = 0; row < 21; row++) {
      const y = 34 + row * rh;
      if (row === 0) { ctx.fillStyle = 'rgba(0,0,0,.08)'; ctx.fillRect(6, y, DW - 12, rh); }
      let x = 6;
      for (let c = 0; c < cw.length; c++) {
        ctx.strokeStyle = 'rgba(0,0,0,.14)'; ctx.strokeRect(x, y, cw[c], rh);
        ctx.fillStyle = r() < 0.06 ? 'rgba(200,40,40,.9)' : 'rgba(25,25,28,.8)';
        const txt = row === 0 ? ['#', 'TENANT', 'SQM', 'EUR/M'][c]
          : c === 0 ? String(row) : c === 1 ? ['Muller GmbH', 'n/a', 'VACANT', 'Al Noor LLC', '???', 'Kaya & Co', 'see email'][(r() * 7) | 0]
          : (r() < 0.1 ? '#REF!' : (r() * (c === 2 ? 900 : 9999)).toFixed(c === 3 ? 2 : 0));
        ctx.fillText(txt, x + 3, y + 11);
        x += cw[c];
      }
    }
    if (r() < 0.6) { ctx.fillStyle = 'rgba(255,230,0,.35)'; ctx.fillRect(6, 34 + ((r() * 18 + 1) | 0) * rh, DW - 12, rh); }
  } else {
    // Email print-out
    ctx.fillStyle = ink; ctx.font = `500 10px ${MONO}`;
    const rows = ['From:  asset.mgmt@', 'To:    valuation-team', 'Cc:    legal; fund-admin', 'Subj:  RE: RE: FW: ' + title.toLowerCase()];
    rows.forEach((t, k) => ctx.fillText(t, m, 36 + k * 16));
    ctx.fillStyle = soft; ctx.fillRect(m, 106, DW - 2 * m, 1);
    let y = bars(ctx, r, m, 122, DW - 2 * m, 4, 11, soft) + 12;
    y = bars(ctx, r, m, y, DW - 2 * m, 6, 11, soft) + 16;
    ctx.fillStyle = 'rgba(40,40,44,.08)'; ctx.fillRect(m, y, DW - 2 * m, 40);
    ctx.fillStyle = 'rgba(30,30,34,.7)'; ctx.font = `400 9px ${MONO}`;
    ctx.fillText('[attachment] scan_' + (1000 + (r() * 8999 | 0)) + '.pdf  4.2MB', m + 8, y + 24);
    bars(ctx, r, m, y + 56, DW - 2 * m, 5, 11, soft);
  }
  ctx.restore();
  // paper fibre / scan noise + fold
  const img = ctx.getImageData(0, 0, DW, DH), d = img.data;
  const nAmt = type === 3 ? 22 : 9;
  for (let p = 0; p < d.length; p += 4) { const n = (r() - 0.5) * nAmt; d[p] += n; d[p + 1] += n; d[p + 2] += n; }
  ctx.putImageData(img, 0, 0);
  if (r() < 0.5) { const g = ctx.createLinearGradient(0, DH * 0.48, 0, DH * 0.52); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(0.5, 'rgba(0,0,0,.12)'); g.addColorStop(1, 'rgba(255,255,255,0)'); ctx.fillStyle = g; ctx.fillRect(0, DH * 0.48, DW, DH * 0.04); }
}

const FIELDS = [
  ['asset.id', () => 'DE-BER-' + String(40 + (Math.random() * 900 | 0)).padStart(4, '0')],
  ['noi.annual', r => '€' + (0.4 + r() * 3).toFixed(2) + 'M'],
  ['valuation', r => '€' + (12 + r() * 180).toFixed(1) + 'M'],
  ['occupancy', r => (84 + r() * 16).toFixed(1) + '%'],
  ['lease.wault', r => (2 + r() * 9).toFixed(1) + ' yrs'],
  ['epc.rating', r => 'ABCD'[(r() * 4) | 0]],
  ['units', r => String(20 + (r() * 400 | 0))],
  ['arrears', r => (r() * 2.4).toFixed(2) + '%'],
  ['yield.gross', r => (3.8 + r() * 3).toFixed(2) + '%'],
  ['ltv', r => (32 + r() * 30).toFixed(1) + '%'],
  ['gfa.sqm', r => (1200 + r() * 40000 | 0).toLocaleString('en')],
  ['title.state', () => 'VERIFIED'],
];

function hex(r, n) { let s = ''; for (let i = 0; i < n; i++) s += '0123456789abcdef'[(r() * 16) | 0]; return s; }

function drawCell(ctx, i) {
  const r = rng(5000 + i * 31);
  // Dark glass panel; alpha encodes glass translucency
  ctx.clearRect(0, 0, CW, CH);
  const g = ctx.createLinearGradient(0, 0, CW, CH);
  g.addColorStop(0, 'rgba(46,48,54,0.80)'); g.addColorStop(1, 'rgba(18,19,22,0.70)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, CW, CH);
  ctx.strokeStyle = 'rgba(255,255,255,0.30)'; ctx.lineWidth = 2; ctx.strokeRect(1, 1, CW - 2, CH - 2);
  // corner ticks
  ctx.fillStyle = 'rgba(255,190,6,0.95)';
  ctx.fillRect(0, 0, 18, 3); ctx.fillRect(0, 0, 3, 18);
  ctx.fillRect(CW - 18, CH - 3, 18, 3); ctx.fillRect(CW - 3, CH - 18, 3, 18);
  const f = FIELDS[i % FIELDS.length];
  ctx.fillStyle = 'rgba(255,255,255,0.5)'; ctx.font = `400 17px ${MONO}`; ctx.fillText(f[0], 20, 44);
  ctx.fillStyle = 'rgba(255,255,255,0.96)'; ctx.font = `300 46px ${SANS}`;
  ctx.fillText(f[1](r), 18, 100);
  // sparkline or bar
  ctx.strokeStyle = 'rgba(255,190,6,0.9)'; ctx.lineWidth = 2.5; ctx.beginPath();
  let v = 0.5;
  for (let k = 0; k <= 20; k++) { v = Math.min(0.95, Math.max(0.05, v + (r() - 0.45) * 0.22)); const x = 20 + k * 10.8, y = 180 - v * 50; k ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }
  ctx.stroke();
  ctx.fillStyle = 'rgba(255,255,255,0.14)'; ctx.fillRect(20, 196, CW - 40, 1);
  ctx.fillStyle = 'rgba(255,255,255,0.42)'; ctx.font = `400 14px ${MONO}`;
  ctx.fillText('0x' + hex(r, 6) + '…' + hex(r, 4), 20, 226);
  ctx.fillStyle = 'rgba(255,190,6,0.85)'; ctx.fillText('SRC:' + ['ERP', 'PDF', 'XLS', 'API', 'REG'][(r() * 5) | 0], CW - 86, 226);
}

export function buildAtlases() {
  const doc = document.createElement('canvas');
  doc.width = DW * ATLAS_COLS; doc.height = DH * ATLAS_ROWS;
  const dctx = doc.getContext('2d');
  const cell = document.createElement('canvas');
  cell.width = CW * ATLAS_COLS; cell.height = CH * ATLAS_ROWS;
  const cctx = cell.getContext('2d');
  const tmpD = document.createElement('canvas'); tmpD.width = DW; tmpD.height = DH;
  const tmpC = document.createElement('canvas'); tmpC.width = CW; tmpC.height = CH;
  const td = tmpD.getContext('2d', { willReadFrequently: true }), tc = tmpC.getContext('2d');
  // seed Math.random-based field so the atlas is deterministic
  const r0 = rng(77); const mr = Math.random; Math.random = r0;
  for (let i = 0; i < ATLAS_COLS * ATLAS_ROWS; i++) {
    const cx = i % ATLAS_COLS, cy = (i / ATLAS_COLS) | 0;
    drawDoc(td, i); dctx.drawImage(tmpD, cx * DW, cy * DH);
    drawCell(tc, i); cctx.drawImage(tmpC, cx * CW, cy * CH);
  }
  Math.random = mr;
  return { doc, cell };
}
