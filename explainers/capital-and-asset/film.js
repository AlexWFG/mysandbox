import { setData, loadIcons, L, E, W, TL, mk, range, ei3, eo5, clamp, pending, show } from './core.js';
import * as S from './scenes.js';

const stage = document.getElementById('stage');
const ICONS = ['banknote', 'building-2', 'pen-line', 'stamp', 'scale', 'folder-open', 'calculator', 'file-pen-line', 'wrench', 'briefcase', 'badge-check', 'coins', 'lock', 'user-round', 'lock-open', 'database', 'shield-check', 'handshake', 'arrow-right', 'landmark', 'circle-check'];

async function init() {
  const [tl, man] = await Promise.all([fetch('audio/timeline.json').then(r => r.json()), fetch('stock/manifest.json').then(r => r.json())]);
  setData(tl, man);
  await loadIcons(ICONS);
  await document.fonts.load('300 40px Inter'); await document.fonts.load('400 40px Inter'); await document.fonts.load('500 40px Inter'); await document.fonts.load('500 20px Mono');
  await document.fonts.ready;

  const scenes = [
    [S.sTitle, 0, L('v02')],
    [S.sMontage, L('v02') - .15, W('v02', 'Some') + .3],
    [S.sMiddle, W('v02', 'Some') - .2, L('v06')],
    [S.sRule, L('v06') - .35, L('v11')],
    [S.sIndep, L('v11') - .3, L('v12')],
    [S.sMap, L('v12') - .35, L('v17')],
    [S.sOffer, L('v17') - .35, L('v19')],
    [S.sTiers, L('v19') - .35, L('v23')],
    [S.sSeq, L('v23') - .35, L('v29')],
    [S.sDemo, L('v29') - .35, L('v30')],
    [S.sTools, L('v30') - .35, L('v31')],
    [S.sLoop, L('v31') - .35, L('v32')],
    [S.sNeutral, L('v32') - .35, L('v33')],
    [S.sFinale, L('v33') - .35, tl.total + 1],
  ].map(([fn, t0, t1]) => { const root = mk('div', 'scene', stage); return { root, t0, t1, up: fn(root) }; });

  // chapter marker
  const CH = [['01', 'The middle', L('v02') - .1, L('v06') - .3], ['02', 'The rule', L('v06') - .1, L('v12') - .3], ['03', 'The map', L('v12') - .1, L('v17') - .3],
    ['04', 'Prop.com · the order', L('v17') - .1, L('v23') - .3], ['05', 'Propchain · the sequence', L('v23') - .1, L('v30') - .3], ['06', 'How it holds', L('v30') - .1, L('v33') - .3]];
  const chap = mk('div', null, stage, null); chap.id = 'chapter';
  const cn = mk('span', 'n', chap), ct = mk('span', null, chap), cb = mk('div', 'bar', chap);
  // fx
  const vig = mk('div', 'layer', stage); vig.id = 'vignette';
  const grain = mk('div', 'layer', stage); grain.id = 'grain';
  const c = document.createElement('canvas'); c.width = c.height = 256; const g = c.getContext('2d'); const id = g.createImageData(256, 256);
  let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  for (let i = 0; i < id.data.length; i += 4) { const v = rnd() * 255; id.data[i] = id.data[i + 1] = id.data[i + 2] = v; id.data[i + 3] = 255; }
  g.putImageData(id, 0, 0); grain.style.backgroundImage = `url(${c.toDataURL()})`;

  window.__seek = async t => {
    for (const s of scenes) {
      const on = t >= s.t0 && t <= s.t1;
      s.root.style.display = on ? 'block' : 'none';
      if (on) s.up(t);
    }
    const ch = CH.find(c => t >= c[2] && t <= c[3]);
    if (ch) {
      const [n, name, a, b] = ch; const k = clamp((t - a - .2) / .6);
      cn.textContent = n; ct.textContent = name.toUpperCase().slice(0, Math.floor(k * name.length));
      const o = ei3(range(t, b - .4, b)); chap.style.opacity = eo5(range(t, a, a + .5)) * (1 - o);
      cb.style.transform = `scaleX(${eo5(range(t, a + .1, a + 1.2))})`;
    } else chap.style.opacity = 0;
    const f = Math.floor(t * 30);
    grain.style.backgroundPosition = `${(f * 97) % 256}px ${(f * 61) % 256}px`;
    const ps = pending.splice(0); await Promise.all(ps);
  };
  const q = new URLSearchParams(location.search);
  if (q.has('t')) await window.__seek(parseFloat(q.get('t')));
}
window.__ready = init();
