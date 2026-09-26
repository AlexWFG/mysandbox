// Propchain launch reel — deterministic, frame-addressable WebGL film.
// window.__seek(t) renders the frame at t seconds; render.mjs captures it.
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { buildAtlases, ATLAS_COLS } from './textures.js';
import { rng, clamp, lerp, range, smooth, easeInOutCubic, easeOutCubic, easeOutExpo, easeInCubic, easeOutQuint, window01, hermite } from './util.js';
import { buildUI, updateUI } from './ui.js';

export const DURATION = 30;
const W = 1920, H = 1080;
const YELLOW = new THREE.Color('#FFBE06');

// ------------------------------------------------------------------ renderer
const canvas = document.getElementById('gl');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(1);
renderer.setSize(W, H, false);
renderer.setClearColor(0x070707, 1);

const camera = new THREE.PerspectiveCamera(38, W / H, 0.1, 600);
const scene = new THREE.Scene();

// ------------------------------------------------------------------ plate (photography + void backdrop)
const plateScene = new THREE.Scene();
const orthoCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
let plateLoaded; const plateReady = new Promise(r => (plateLoaded = r));
const plateTex = new THREE.TextureLoader().load(new URL('../assets/plate-city.jpg', import.meta.url).href, () => plateLoaded());
plateTex.colorSpace = THREE.SRGBColorSpace;
plateTex.minFilter = THREE.LinearMipmapLinearFilter;
const plateMat = new THREE.ShaderMaterial({
  depthTest: false, depthWrite: false,
  uniforms: {
    uTex: { value: plateTex }, uScale: { value: 1 }, uRot: { value: 0 }, uExp: { value: 0 },
    uBlur: { value: 0 }, uScanY: { value: -1 }, uScanAmt: { value: 0 }, uVoid: { value: 0 }, uTime: { value: 0 },
    uOff: { value: new THREE.Vector2() },
  },
  vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }`,
  fragmentShader: `
    uniform sampler2D uTex; uniform float uScale, uRot, uExp, uBlur, uScanY, uScanAmt, uVoid, uTime; uniform vec2 uOff;
    varying vec2 vUv;
    const float AR = 1.7778;
    vec2 xf(vec2 uv, float s){
      vec2 p = uv - 0.5; p.x *= AR;
      float c = cos(uRot), si = sin(uRot); p = mat2(c, -si, si, c) * p;
      p.x /= AR; p /= s; return p + 0.5 + uOff;
    }
    vec3 grade(vec3 c){
      float l = dot(c, vec3(0.2126, 0.7152, 0.0722));
      c = mix(vec3(l), c, 0.5);
      c *= vec3(0.93, 0.98, 1.06);
      return c;
    }
    void main(){
      vec3 col = vec3(0.0);
      if (uExp > 0.001) {
        float tot = 0.0;
        for (int k = 0; k < 14; k++) {
          float f = float(k) / 13.0;
          float w = 1.0 - f * 0.6;
          col += texture2D(uTex, xf(vUv, uScale * (1.0 + f * uBlur))).rgb * w; tot += w;
        }
        col = grade(col / tot);
        // "reading the building": luminance edges revealed below the scan line
        vec2 uv = xf(vUv, uScale); vec2 px = vec2(1.0 / 3510.0, 1.0 / 1976.0) * 1.6;
        float l00 = dot(texture2D(uTex, uv - px).rgb, vec3(.33)), l10 = dot(texture2D(uTex, uv + vec2(px.x, -px.y)).rgb, vec3(.33));
        float l01 = dot(texture2D(uTex, uv + vec2(-px.x, px.y)).rgb, vec3(.33)), l11 = dot(texture2D(uTex, uv + px).rgb, vec3(.33));
        float e = length(vec2(l10 + l11 - l00 - l01, l01 + l11 - l00 - l10));
        e = smoothstep(0.035, 0.16, e);
        float below = smoothstep(uScanY + 0.002, uScanY - 0.05, vUv.y) * smoothstep(uScanY - 0.55, uScanY - 0.05, vUv.y);
        float line = exp(-abs(vUv.y - uScanY) * 260.0);
        vec3 Y = vec3(1.0, 0.52, 0.004);
        // faint survey grid
        vec2 g = abs(fract(uv * vec2(64.0, 36.0)) - 0.5);
        float grid = (1.0 - smoothstep(0.0, 0.035, min(g.x, g.y))) * 0.12;
        col = col * uExp + uScanAmt * (Y * (e * 1.6 + grid) * below + Y * line * 3.0);
        col *= 1.0 - uScanAmt * below * 0.35;
      }
      // void backdrop for the 3D world
      vec2 q = vUv - vec2(0.5, 0.45); q.x *= 1.6;
      vec3 v = mix(vec3(0.020, 0.021, 0.024), vec3(0.004, 0.004, 0.005), smoothstep(0.0, 0.9, length(q)));
      col += v * uVoid;
      gl_FragColor = vec4(col, 1.0);
    }`,
});
plateScene.add(new THREE.Mesh(new THREE.PlaneGeometry(2, 2), plateMat));

// ------------------------------------------------------------------ records: 2304 objects, doc -> cell -> city tile
const NX = 16, NY = 12, NZ = 12, N = NX * NY * NZ, LS = 1.15;
const GROUND = -8.0;
const atl = buildAtlases();
const docTex = new THREE.CanvasTexture(atl.doc); docTex.colorSpace = THREE.SRGBColorSpace; docTex.anisotropy = 8;
const cellTex = new THREE.CanvasTexture(atl.cell); cellTex.colorSpace = THREE.SRGBColorSpace; cellTex.anisotropy = 8;
for (const t of [docTex, cellTex]) { t.minFilter = THREE.LinearMipmapLinearFilter; t.generateMipmaps = true; }

const recUniforms = {
  uDoc: { value: docTex }, uCell: { value: cellTex }, uTime: { value: 0 },
  uFocus: { value: 20 }, uFocusRange: { value: 18 }, uFogNear: { value: 60 }, uFogFar: { value: 140 },
  uMirror: { value: 0 }, uMirrorAlpha: { value: 0 }, uGround: { value: GROUND }, uDocLight: { value: 0.62 },
  uYellow: { value: new THREE.Vector3(1.0, 0.52, 0.004) },
};
const recVert = `
  attribute vec4 aA; attribute vec4 aB;
  uniform float uMirror, uGround, uTime;
  varying vec2 vUv; varying vec4 vA; varying vec4 vB; varying float vDepth, vShade, vWy;
  void main(){
    vUv = uv; vA = aA; vB = aB;
    vec3 p = position;
    float curl = (0.10 + 0.10 * sin(uTime * 1.3 + aB.x * 1.7 + instanceMatrix[3].x * 0.3)) * (1.0 - aA.x);
    p.z += (p.x * p.x - 0.08) * curl * 1.6 + p.y * p.y * 0.08 * (1.0 - aA.x);
    vec4 wp = modelMatrix * instanceMatrix * vec4(p, 1.0);
    vec3 n = normalize(mat3(modelMatrix * instanceMatrix) * normalize(vec3(-p.x * curl * 3.2, 0.0, 1.0)));
    if (uMirror > 0.5) { wp.y = 2.0 * uGround - wp.y; n.y = -n.y; }
    vWy = wp.y;
    vec4 mv = viewMatrix * wp; vDepth = -mv.z;
    vec3 L = normalize(vec3(-0.45, 0.75, 0.55));
    vec3 V = normalize(cameraPosition - wp.xyz);
    float ndl = abs(dot(n, L));
    vShade = 0.16 + 0.84 * ndl * ndl + 0.2 * pow(1.0 - abs(dot(n, V)), 3.0);
    gl_Position = projectionMatrix * mv;
  }`;
const recFrag = `
  uniform sampler2D uDoc, uCell; uniform float uTime, uFocus, uFocusRange, uFogNear, uFogFar, uMirror, uMirrorAlpha, uGround, uDocLight;
  uniform vec3 uYellow;
  varying vec2 vUv; varying vec4 vA; varying vec4 vB; varying float vDepth, vShade, vWy;
  float hash(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
  void main(){
    float morph = vA.x, seal = vA.y, glitch = vA.z, emis = vA.w;
    float idx = vB.x, alpha = vB.y, warm = vB.z, flash = vB.w;
    float blur = clamp(abs(vDepth - uFocus) / uFocusRange, 0.0, 1.0);
    vec2 uv = vUv;
    if (glitch > 0.01) {
      float row = floor(uv.y * 28.0);
      float r = hash(vec2(row, floor(uTime * 30.0) + idx));
      uv.x += (r - 0.5) * 0.35 * glitch * step(0.55, r);
      uv.y += (hash(vec2(idx, floor(uTime * 30.0))) - 0.5) * 0.04 * glitch;
    }
    float col = mod(idx, ${ATLAS_COLS}.0), row = floor(idx / ${ATLAS_COLS}.0);
    vec2 auv = vec2((col + clamp(uv.x, 0.002, 0.998)) / ${ATLAS_COLS}.0, 1.0 - (row + 1.0 - clamp(uv.y, 0.002, 0.998)) / ${ATLAS_COLS}.0);
    float bias = blur * 4.5;
    vec3 c = vec3(0.0); float a = 0.0;
    if (morph < 0.999) {
      vec4 d = texture2D(uDoc, auv, bias);
      vec3 dc = d.rgb * vShade * uDocLight * emis;
      if (glitch > 0.01) { dc = mix(dc, vec3(dc.r * 1.3, dc.g * 0.6, dc.b * 0.55) + 0.15 * step(0.8, hash(vec2(floor(uv.y * 60.0), uTime))), glitch * 0.8); }
      dc += uYellow * glitch * 0.9 * (0.4 + 0.6 * (1.0 - smoothstep(0.0, 0.06, min(min(vUv.x, 1.0 - vUv.x), min(vUv.y, 1.0 - vUv.y)))));
      c = dc; a = 1.0;
    }
    if (morph > 0.001) {
      vec4 q = texture2D(uCell, auv, bias);
      vec3 cc = q.rgb * emis * (0.75 + 0.25 * vShade);
      cc = mix(cc, cc * vec3(1.0, 0.75, 0.35) + uYellow * 0.35 * q.a, warm);
      float e = min(min(vUv.x, 1.0 - vUv.x), min(vUv.y, 1.0 - vUv.y));
      float border = 1.0 - smoothstep(0.0, 0.04, e);
      cc += uYellow * border * seal * (0.32 + 1.1 * seal * (1.0 - seal) * 4.0);
      cc += uYellow * 0.28 * seal * (1.0 - seal) * 4.0 * q.a;
      float ca = min(1.0, q.a * alpha);
      c = mix(c, cc, morph); a = mix(a, ca, morph);
    }
    // digitisation flash as a doc becomes a record
    c += vec3(1.0, 0.8, 0.45) * morph * (1.0 - morph) * 4.0 * 0.55;
    c += mix(vec3(1.0), uYellow, 0.7) * flash * 0.9;
    float edge = min(min(vUv.x, 1.0 - vUv.x), min(vUv.y, 1.0 - vUv.y));
    a *= smoothstep(0.0, 0.004 + blur * 0.16, edge);
    a *= mix(1.0, 0.55, blur * blur) * alpha;
    a *= 1.0 - smoothstep(uFogNear, uFogFar, vDepth);
    if (uMirror > 0.5) { a *= uMirrorAlpha * exp(-(uGround - vWy) * 0.10); c *= 0.8; }
    if (a < 0.003) discard;
    gl_FragColor = vec4(c, a);
  }`;
function makeRecMat(mirror) {
  const u = THREE.UniformsUtils.clone(recUniforms);
  u.uDoc.value = docTex; u.uCell.value = cellTex; u.uMirror.value = mirror ? 1 : 0;
  return new THREE.ShaderMaterial({ uniforms: u, vertexShader: recVert, fragmentShader: recFrag, transparent: true, depthWrite: false, side: THREE.DoubleSide });
}
const recGeo = new THREE.PlaneGeometry(1, 1, 8, 2);
const aA = new THREE.InstancedBufferAttribute(new Float32Array(N * 4), 4).setUsage(THREE.DynamicDrawUsage);
const aB = new THREE.InstancedBufferAttribute(new Float32Array(N * 4), 4).setUsage(THREE.DynamicDrawUsage);
recGeo.setAttribute('aA', aA); recGeo.setAttribute('aB', aB);
const recMat = makeRecMat(false), mirMat = makeRecMat(true);
const records = new THREE.InstancedMesh(recGeo, recMat, N);
const mirror = new THREE.InstancedMesh(recGeo, mirMat, N);
mirror.instanceMatrix = records.instanceMatrix;   // share transforms
for (const m of [records, mirror]) { m.frustumCulled = false; m.instanceMatrix.setUsage(THREE.DynamicDrawUsage); }
records.renderOrder = 10; mirror.renderOrder = 5;
scene.add(mirror, records);

// ---- per-record static data
const R = rng(20260925);
const rec = [];
const qTmp = new THREE.Quaternion(), qA = new THREE.Quaternion(), qB = new THREE.Quaternion();
const vTmp = new THREE.Vector3();
// city: towers built from the same records
const TOWERS = [
  [0, 0, 4, 4, 30], [-9.5, 4, 3, 3, 22], [8.5, -6, 4, 3, 20], [9.5, 7.5, 3, 3, 16], [-8.5, -8.5, 3, 4, 18],
  [-18, -1.5, 3, 3, 12], [18, 0.5, 3, 3, 13], [0, 13.5, 4, 3, 10], [-1, -16, 3, 3, 14],
];
const TS = 1.05;
const tiles = [];
for (const [cx, cz, w, d, h] of TOWERS) {
  const Wd = w * TS / 2, Dd = d * TS / 2;
  for (let r = 0; r < h; r++) {
    const y = GROUND + (r + 0.5) * TS, hy = r / 30;
    for (let c = 0; c < w; c++) {
      const x = cx - Wd + (c + 0.5) * TS;
      tiles.push({ p: [x, y, cz + Dd], q: [0, 0, 0], hy });
      tiles.push({ p: [x, y, cz - Dd], q: [0, Math.PI, 0], hy });
    }
    for (let c = 0; c < d; c++) {
      const z = cz - Dd + (c + 0.5) * TS;
      tiles.push({ p: [cx + Wd, y, z], q: [0, Math.PI / 2, 0], hy });
      tiles.push({ p: [cx - Wd, y, z], q: [0, -Math.PI / 2, 0], hy });
    }
  }
}
// parcels on the ground plane for the remainder
{
  const occupied = (x, z) => TOWERS.some(([cx, cz, w, d]) => Math.abs(x - cx) < w * TS / 2 + 1.2 && Math.abs(z - cz) < d * TS / 2 + 1.2);
  const cand = [];
  for (let gx = -26; gx <= 26; gx++) for (let gz = -26; gz <= 26; gz++) {
    const x = gx * TS, z = gz * TS, rr = Math.hypot(x, z);
    if (rr < 6 || rr > 28 || occupied(x, z)) continue;
    cand.push([x, z, rr]);
  }
  const rp = rng(9);
  cand.sort(() => rp() - 0.5);
  while (tiles.length < N && cand.length) {
    const [x, z] = cand.pop();
    tiles.push({ p: [x, GROUND + 0.02, z], q: [-Math.PI / 2, 0, 0], hy: 0, flat: true });
  }
}
const perm = [...Array(N).keys()]; { const rp = rng(4); for (let i = N - 1; i > 0; i--) { const j = (rp() * (i + 1)) | 0; [perm[i], perm[j]] = [perm[j], perm[i]]; } }

const LAT_CORNER = new THREE.Vector3(-(NX - 1) / 2 * LS, -(NY - 1) / 2 * LS, (NZ - 1) / 2 * LS);
for (let i = 0; i < N; i++) {
  const ix = i % NX, iy = ((i / NX) | 0) % NY, iz = (i / (NX * NY)) | 0;
  const lat = new THREE.Vector3((ix - (NX - 1) / 2) * LS, (iy - (NY - 1) / 2) * LS, (iz - (NZ - 1) / 2) * LS);
  // doc cloud: a deep field the camera flies through, with a clear tunnel on the flight path
  let x, y, z;
  for (;;) {
    x = (R() - 0.5) * 110; y = (R() - 0.5) * 56; z = -45 + R() * 175;
    const tunnel = z > 25 ? 4.5 : 0;
    if (Math.abs(x) > tunnel * 1.4 || Math.abs(y - 0.8) > tunnel) break;
  }
  const reserve = R() < 0.58;
  if (reserve) { const an = R() * 6.283, rad = 26 + R() * 30; x = Math.cos(an) * rad; z = Math.sin(an) * rad - 6; y = (R() - 0.5) * 34; }
  const docP = new THREE.Vector3(x, y, z);
  const vel = new THREE.Vector3((R() - 0.5) * 0.5, (R() - 0.5) * 0.35 + 0.08, (R() - 0.5) * 0.4);
  const q0 = new THREE.Quaternion().setFromEuler(new THREE.Euler(R() * 6.28, R() * 6.28, R() * 6.28));
  const axis = new THREE.Vector3(R() - 0.5, R() - 0.5, R() - 0.5).normalize();
  const w = 0.25 + R() * 0.8;
  const tile = tiles[perm[i]];
  const tq = new THREE.Quaternion().setFromEuler(new THREE.Euler(tile.q[0], tile.q[1], tile.q[2], 'YXZ'));
  const r = R();
  const cityEmis = r < 0.06 ? 1.6 : r < 0.3 ? 1.15 + R() * 0.45 : 0.45 + R() * 0.45;
  const warm = r < 0.06 ? 1 : 0;
  const dist = lat.distanceTo(LAT_CORNER);
  rec.push({
    lat, docP, vel, reserve, q0, axis, w, tile, tq, cityEmis, warm, dist,
    idx: (R() * 64) | 0, cellIdx: (R() * 64) | 0,
    dIn: R() * 0.35,
    dStruct: 0.55 * R() + 0.45 * clamp(docP.distanceTo(lat) / 90),
    dCity: tile.hy * 0.85 + R() * 0.35 + (tile.flat ? 0.2 : 0),
    arc: 3 + R() * 7, wob: R() * 6.28, spin: R() < 0.5 ? 1 : -1,
    pos: new THREE.Vector3(), quat: new THREE.Quaternion(), sx: 1, sy: 1.414,
    A: [0, 0, 0, 1], B: [0, 0, 0, 0], depth: 0,
  });
}

// ------------------------------------------------------------------ lineage threads (layer 02)
const threadGeo = new THREE.BufferGeometry();
{
  const pos = [], along = [], seed = [];
  const rs = rng(31);
  for (let ix = 0; ix < NX; ix++) for (let iy = 0; iy < NY; iy++) {
    const s = rs();
    if (s > 0.62) continue;
    const x = (ix - (NX - 1) / 2) * LS, y = (iy - (NY - 1) / 2) * LS;
    const z0 = -(NZ - 1) / 2 * LS - 0.6, z1 = (NZ - 1) / 2 * LS + 0.6;
    const cornerD = Math.hypot(x - LAT_CORNER.x, y - LAT_CORNER.y);
    pos.push(x + 0.5, y + 0.5, z0, x + 0.5, y + 0.5, z1);
    along.push(0, 1); seed.push(s, cornerD, s, cornerD);
  }
  threadGeo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  threadGeo.setAttribute('aAlong', new THREE.Float32BufferAttribute(along, 1));
  threadGeo.setAttribute('aSeed', new THREE.Float32BufferAttribute(seed, 2));
}
const threadMat = new THREE.ShaderMaterial({
  transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
  uniforms: { uTime: { value: 0 }, uAlpha: { value: 0 }, uWave: { value: -10 }, uYellow: recUniforms.uYellow },
  vertexShader: `attribute float aAlong; attribute vec2 aSeed; varying float vAlong; varying vec2 vSeed; void main(){ vAlong=aAlong; vSeed=aSeed; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.0);} `,
  fragmentShader: `uniform float uTime, uAlpha, uWave; uniform vec3 uYellow; varying float vAlong; varying vec2 vSeed;
    void main(){
      float lit = smoothstep(uWave - 1.5, uWave, 40.0 - vSeed.y) ;
      lit = smoothstep(0.0, 1.0, (uWave - vSeed.y * 0.045) * 3.0);
      float pulse = pow(max(0.0, 1.0 - abs(fract(vAlong * 1.0 - uTime * 0.9 + vSeed.x * 7.0) - 0.5) * 2.0), 18.0);
      vec3 c = uYellow * (0.07 + 0.3 * lit) + uYellow * pulse * 2.4 * lit;
      gl_FragColor = vec4(c * uAlpha, 1.0);
    }`,
});
const threads = new THREE.LineSegments(threadGeo, threadMat);
threads.renderOrder = 12; threads.frustumCulled = false;
scene.add(threads);

// ------------------------------------------------------------------ points: dust, agents, capital flows
function makePoints(n, additive = true) {
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(n * 3), 3).setUsage(THREE.DynamicDrawUsage));
  g.setAttribute('aSize', new THREE.BufferAttribute(new Float32Array(n), 1).setUsage(THREE.DynamicDrawUsage));
  g.setAttribute('aCol', new THREE.BufferAttribute(new Float32Array(n * 4), 4).setUsage(THREE.DynamicDrawUsage));
  const m = new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: additive ? THREE.AdditiveBlending : THREE.NormalBlending,
    uniforms: { uFocus: recUniforms.uFocus, uFocusRange: recUniforms.uFocusRange, uPx: { value: H / (2 * Math.tan(THREE.MathUtils.degToRad(19))) } },
    vertexShader: `attribute float aSize; attribute vec4 aCol; uniform float uFocus, uFocusRange, uPx; varying vec4 vCol; varying float vSoft;
      void main(){
        vec4 mv = modelViewMatrix * vec4(position, 1.0);
        float d = -mv.z; float blur = clamp(abs(d - uFocus) / uFocusRange, 0.0, 1.0);
        float s = aSize * uPx / max(d, 0.1);
        float grow = 1.0 + blur * 7.0;
        gl_PointSize = clamp(s * grow, 1.0, 360.0);
        vCol = aCol; vCol.a *= 1.0 / (grow * sqrt(grow)); vCol.a *= clamp(s * 1.5, 0.0, 1.0);
        vSoft = 0.15 + blur * 0.5;
        gl_Position = projectionMatrix * mv;
      }`,
    fragmentShader: `varying vec4 vCol; varying float vSoft;
      void main(){ float r = length(gl_PointCoord - 0.5) * 2.0; float a = 1.0 - smoothstep(1.0 - vSoft - 0.02, 1.0, r); a *= mix(1.0, 1.0 - r*r*0.6, 0.7); if (a <= 0.0) discard; gl_FragColor = vec4(vCol.rgb * vCol.a * a, vCol.a * a); }`,
  });
  const p = new THREE.Points(g, m); p.frustumCulled = false; p.renderOrder = 20;
  scene.add(p);
  return p;
}
const DUST_N = 1400, dust = makePoints(DUST_N);
const dustSeed = []; { const rd = rng(55); for (let i = 0; i < DUST_N; i++) dustSeed.push([(rd() - 0.5) * 120, (rd() - 0.5) * 60, -40 + rd() * 150, rd(), rd(), rd()]); }

const TRAIL = 26;
const COMET_MAX = 120;
const comets = makePoints(COMET_MAX * TRAIL);

// agents: random walks through lattice gaps
const AGENTS = [];
{
  const ra = rng(808);
  for (let a = 0; a < 16; a++) {
    let ix = (ra() * NX) | 0, iy = (ra() * NY) | 0, iz = (ra() * NZ) | 0;
    const nodes = [];
    const node = () => new THREE.Vector3((ix - (NX - 1) / 2) * LS + 0.575, (iy - (NY - 1) / 2) * LS + 0.575, (iz - (NZ - 1) / 2) * LS + 0.575);
    nodes.push(node());
    let lastAxis = -1;
    for (let s = 0; s < 40; s++) {
      let axis; do { axis = (ra() * 3) | 0; } while (axis === lastAxis);
      lastAxis = axis;
      const len = 1 + ((ra() * 4) | 0), dir = ra() < 0.5 ? -1 : 1;
      for (let k = 0; k < len; k++) {
        if (axis === 0) ix = clamp(ix + dir, 0, NX - 2); else if (axis === 1) iy = clamp(iy + dir, 0, NY - 2); else iz = clamp(iz + dir, 0, NZ - 2);
      }
      nodes.push(node());
    }
    const cum = [0]; for (let k = 1; k < nodes.length; k++) cum.push(cum[k - 1] + nodes[k].distanceTo(nodes[k - 1]));
    AGENTS.push({ nodes, cum, speed: 6 + ra() * 5, t0: 15.9 + ra() * 0.6, off: ra() * 3 });
  }
}
function agentPos(a, t, out) {
  const s = Math.max(0, (t - a.t0)) * a.speed + a.off;
  const { nodes, cum } = a; let k = 0;
  while (k < cum.length - 2 && cum[k + 1] < s) k++;
  const f = clamp((s - cum[k]) / Math.max(1e-4, cum[k + 1] - cum[k]));
  return out.copy(nodes[k]).lerp(nodes[k + 1], f);
}

// capital flows between tower tops (list -> diligence -> match -> finance -> settle)
const TOPS = TOWERS.map(([cx, cz, w, d, h]) => new THREE.Vector3(cx, GROUND + h * TS + 0.4, cz));
const FLOWS = [];
{
  const rf = rng(2027);
  const steps = [19.2, 19.9, 20.6, 21.3, 22.0];
  steps.forEach((st, si) => {
    for (let k = 0; k < 6; k++) {
      const a = (rf() * TOPS.length) | 0; let b; do { b = (rf() * TOPS.length) | 0; } while (b === a);
      FLOWS.push({ a, b, t0: st + rf() * 0.35, dur: 0.75 + rf() * 0.4, lift: 5 + rf() * 9, main: k < 2 });
    }
  });
  for (let k = 0; k < 40; k++) {
    const a = (rf() * TOPS.length) | 0; let b; do { b = (rf() * TOPS.length) | 0; } while (b === a);
    FLOWS.push({ a, b, t0: 22.4 + rf() * 7.0, dur: 0.9 + rf() * 0.6, lift: 4 + rf() * 10, main: false });
  }
}
function flowPos(f, s, out) {
  const A = TOPS[f.a], B = TOPS[f.b];
  const cx = (A.x + B.x) / 2, cz = (A.z + B.z) / 2, cy = Math.max(A.y, B.y) + f.lift;
  const u = 1 - s;
  out.set(u * u * A.x + 2 * u * s * cx + s * s * B.x, u * u * A.y + 2 * u * s * cy + s * s * B.y, u * u * A.z + 2 * u * s * cz + s * s * B.z);
  return out;
}
// arcs drawn as faint lines under the comets
const ARC_SEG = 40;
const arcGeo = new THREE.BufferGeometry();
arcGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(FLOWS.length * ARC_SEG * 2 * 3), 3));
arcGeo.setAttribute('aCol', new THREE.BufferAttribute(new Float32Array(FLOWS.length * ARC_SEG * 2 * 4), 4).setUsage(THREE.DynamicDrawUsage));
{
  const p = arcGeo.attributes.position.array; const v = new THREE.Vector3(), v2 = new THREE.Vector3(); let o = 0;
  FLOWS.forEach(f => { for (let k = 0; k < ARC_SEG; k++) { flowPos(f, k / ARC_SEG, v); flowPos(f, (k + 1) / ARC_SEG, v2); p.set([v.x, v.y, v.z, v2.x, v2.y, v2.z], o); o += 6; } });
}
const arcs = new THREE.LineSegments(arcGeo, new THREE.ShaderMaterial({
  transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
  vertexShader: `attribute vec4 aCol; varying vec4 vC; void main(){ vC = aCol; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.0);} `,
  fragmentShader: `varying vec4 vC; void main(){ gl_FragColor = vec4(vC.rgb * vC.a, 1.0); }`,
}));
arcs.frustumCulled = false; arcs.renderOrder = 15; scene.add(arcs);

// ------------------------------------------------------------------ scanner sheet (act 3)
const scanMat = new THREE.ShaderMaterial({
  transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
  uniforms: { uAlpha: { value: 0 }, uYellow: recUniforms.uYellow, uTime: { value: 0 } },
  vertexShader: `varying vec2 vUv; varying float vD; void main(){ vUv = uv; vec4 mv = modelViewMatrix*vec4(position,1.0); vD = -mv.z; gl_Position = projectionMatrix*mv; }`,
  fragmentShader: `uniform float uAlpha, uTime; uniform vec3 uYellow; varying vec2 vUv; varying float vD;
    void main(){
      float fall = exp(-abs(vUv.y - 0.5) * 3.0) * smoothstep(0.0, 0.2, vUv.x) * smoothstep(1.0, 0.6, vUv.x);
      float nearFade = smoothstep(2.0, 12.0, vD);
      float core = exp(-abs(vUv.y - 0.5) * 9.0);
      gl_FragColor = vec4((uYellow * 0.5 + vec3(0.1)) * (core * 0.6 + fall * 0.15) * uAlpha * nearFade, 1.0);
    }`,
});
const scanner = new THREE.Mesh(new THREE.PlaneGeometry(170, 70).rotateY(Math.PI / 2), scanMat);
scanner.renderOrder = 14; scanner.frustumCulled = false;
scene.add(scanner);

// ------------------------------------------------------------------ ground
const groundMat = new THREE.ShaderMaterial({
  transparent: true, depthWrite: false,
  uniforms: { uAlpha: { value: 0 }, uYellow: recUniforms.uYellow, uPulse: { value: 0 } },
  vertexShader: `varying vec3 vW; void main(){ vec4 w = modelMatrix*vec4(position,1.0); vW = w.xyz; gl_Position = projectionMatrix*viewMatrix*w; }`,
  fragmentShader: `uniform float uAlpha, uPulse; uniform vec3 uYellow; varying vec3 vW;
    float grid(vec2 p, float s, float w){ vec2 g = abs(fract(p / s - 0.5) - 0.5) * s; vec2 fw = fwidth(p); vec2 l = 1.0 - smoothstep(vec2(0.0), fw * w, g); return max(l.x, l.y); }
    void main(){
      float r = length(vW.xz);
      float fade = exp(-r * 0.028);
      float g1 = grid(vW.xz, 1.05, 1.0) * 0.10, g2 = grid(vW.xz, 10.5, 1.4) * 0.35;
      float ring = exp(-abs(r - uPulse) * 1.2) * step(0.01, uPulse);
      vec3 c = vec3(0.55, 0.57, 0.62) * (g1 + g2) * fade + uYellow * ring * 0.9 * fade;
      gl_FragColor = vec4(c, uAlpha * clamp(fade * 1.3, 0.0, 1.0) * (0.35 + g1 + g2 + ring));
    }`,
});
const ground = new THREE.Mesh(new THREE.PlaneGeometry(400, 400).rotateX(-Math.PI / 2), groundMat);
ground.position.y = GROUND - 0.01; ground.renderOrder = 1;
scene.add(ground);

// ------------------------------------------------------------------ post
const composer = new EffectComposer(renderer);
composer.setPixelRatio(1); composer.setSize(W, H);
composer.addPass(new RenderPass(plateScene, orthoCam));
const mainPass = new RenderPass(scene, camera); mainPass.clear = false; mainPass.clearDepth = true;
composer.addPass(mainPass);
const bloom = new UnrealBloomPass(new THREE.Vector2(W / 2, H / 2), 0.9, 0.55, 0.92);
composer.addPass(bloom);
const finalPass = new ShaderPass({
  uniforms: {
    tDiffuse: { value: null }, uTime: { value: 0 }, uExp: { value: 1 }, uFade: { value: 0 }, uFlash: { value: 0 },
    uCA: { value: 0.6 }, uGrain: { value: 0.045 }, uVig: { value: 0.85 }, uRes: { value: new THREE.Vector2(W, H) },
  },
  vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.0);} `,
  fragmentShader: `
    uniform sampler2D tDiffuse; uniform float uTime, uExp, uFade, uFlash, uCA, uGrain, uVig; uniform vec2 uRes; varying vec2 vUv;
    vec3 aces(vec3 x){ const float a=2.51,b=0.03,c=2.43,d=0.59,e=0.14; return clamp((x*(a*x+b))/(x*(c*x+d)+e),0.0,1.0); }
    float hash(vec3 p){ p = fract(p * 0.1031); p += dot(p, p.yzx + 33.33); return fract((p.x + p.y) * p.z); }
    void main(){
      vec2 d = vUv - 0.5; float r2 = dot(d, d);
      vec2 off = d * r2 * 0.012 * uCA;
      vec3 c = vec3(texture2D(tDiffuse, vUv + off).r, texture2D(tDiffuse, vUv).g, texture2D(tDiffuse, vUv - off).b);
      c *= uExp;
      c = aces(c * 1.1);
      // grade: cool shadows, warm highlights, gentle contrast
      float l = dot(c, vec3(0.2126, 0.7152, 0.0722));
      c = mix(c * vec3(0.94, 0.99, 1.06), c * vec3(1.04, 1.0, 0.94), smoothstep(0.1, 0.8, l));
      c = pow(c, vec3(1.0 / 2.2));
      c = mix(c, c * c * (3.0 - 2.0 * c), 0.25);
      float v = smoothstep(1.05, 0.25, length(d * vec2(1.0, 1.15)));
      c *= mix(1.0, v, uVig);
      c += uFlash;
      c *= uFade;
      float g = hash(vec3(vUv * uRes, floor(uTime * 30.0))) - 0.5;
      c += g * uGrain * (0.6 + 0.4 * (1.0 - l));
      gl_FragColor = vec4(c, 1.0);
    }`,
});
composer.addPass(finalPass);

// ------------------------------------------------------------------ camera choreography
const CAM = [
  { t: 3.4, v: [0, 0.6, 118, 0, 0.4, 0, 44] },
  { t: 4.25, v: [0.3, 0.8, 90, 0, 0.5, 0, 40] },
  { t: 5.6, v: [0.9, 1.2, 74, 0, 0.6, 0, 38] },
  { t: 8.0, v: [1.6, 1.6, 62, 0, 0.8, 0, 37] },
  { t: 9.8, v: [1.4, 1.9, 53, 0, 0.6, 0, 37] },
  { t: 11.0, v: [-5, 5, 39, 0, 0, 0, 38] },
  { t: 13.6, v: [-18, 10, 28, 0, -0.5, 0, 38] },
  { t: 16.0, v: [-27, 9, 15, 0.5, 0, 0, 38] },
  { t: 18.3, v: [-22, 6, 17, 1, 0, -1, 38] },
  { t: 21.4, v: [-35, 14, 37, 0, 6.5, 0, 38] },
  { t: 24.6, v: [-25, 22, 50, 0, 8, 0, 38] },
  { t: 30.0, v: [-8, 34, 66, 0, 8.5, 0, 36] },
];
const FOCUS = [
  { t: 3.4, v: [30, 30] }, { t: 5.6, v: [22, 22] }, { t: 8.0, v: [24, 22] }, { t: 11.0, v: [40, 30] },
  { t: 13.6, v: [32, 24] }, { t: 16.0, v: [30, 20] }, { t: 18.3, v: [27, 14] }, { t: 21.4, v: [58, 45] }, { t: 30, v: [70, 55] },
];

// ------------------------------------------------------------------ UI
if (!window.__FILM) buildUI(document.getElementById('ui'));

// ------------------------------------------------------------------ per-frame update
const mat4 = new THREE.Matrix4();
const order = new Uint16Array(N);
const posArr = records.instanceMatrix.array;
const Aarr = aA.array, Barr = aB.array;
const heads = []; for (let a = 0; a < AGENTS.length; a++) heads.push(new THREE.Vector3());
const tmpV = new THREE.Vector3(), tmpV2 = new THREE.Vector3(), ident = new THREE.Quaternion();
const projected = { agents: [] };

function updateRecords(t) {
  const scanX = lerp(-46, 46, range(t, 8.15, 10.6));
  const scanOn = window01(t, 8.1, 10.7, 0.2, 0.3);
  const agentsOn = t > 15.8 && t < 19.4;
  if (agentsOn) AGENTS.forEach((a, k) => agentPos(a, t, heads[k]));
  const breath = window01(t, 11.4, 18.6, 0.8, 0.6);
  for (let i = 0; i < N; i++) {
    const r = rec[i];
    // --- document state
    const alphaIn = r.reserve ? smooth(range(t, 9.55 + r.dStruct * 0.7, 10.15 + r.dStruct * 0.7)) : smooth(range(t, 3.5 + r.dIn, 3.9 + r.dIn));
    const tq = t * r.w;
    qA.setFromAxisAngle(r.axis, tq).premultiply(r.q0);
    const dp = tmpV.copy(r.docP).addScaledVector(r.vel, t);
    dp.y += Math.sin(t * 0.6 + r.wob) * 0.35;
    // --- structuring: vortex into the lattice
    const ps = clamp((t - (9.7 + r.dStruct * 0.7)) / 1.5);
    const e = easeInOutCubic(ps);
    let px, py, pz;
    if (ps <= 0) { px = dp.x; py = dp.y; pz = dp.z; r.quat.copy(qA); }
    else {
      const r0 = Math.hypot(dp.x, dp.z), th0 = Math.atan2(dp.z, dp.x);
      const r1 = Math.hypot(r.lat.x, r.lat.z), th1 = Math.atan2(r.lat.z, r.lat.x);
      let dth = th1 - th0; while (dth > Math.PI) dth -= 2 * Math.PI; while (dth < -Math.PI) dth += 2 * Math.PI;
      dth += r.spin * Math.PI * 0.9;
      const th = th0 + dth * e, rr = lerp(r0, r1, e) * (1 - 0.25 * Math.sin(Math.PI * e));
      px = Math.cos(th) * rr; pz = Math.sin(th) * rr; py = lerp(dp.y, r.lat.y, easeOutCubic(ps));
      r.quat.copy(qA).slerp(ident, Math.pow(e, 0.8));
    }
    const DS = 2.1;
    const es = easeOutCubic(ps);
    let sy = lerp(1.414 * DS, 1.0, es), sx = lerp(DS, 1.0, es);
    const morph = clamp((t - (10.88 + r.dIn * 0.5)) / 0.2);
    // lattice life: subtle layer breathing
    if (ps >= 1) {
      const iz = (i / (NX * NY)) | 0;
      pz += Math.sin(t * 1.4 + iz * 0.7) * 0.06 * breath;
    }
    // --- attestation wave
    const seal = clamp((t - 13.65 - r.dist * 0.045) / 0.22) * (1 - clamp((t - 18.6) / 1.0));
    // --- agents pass: cells light
    let flash = 0;
    if (agentsOn && ps >= 1) {
      for (let a = 0; a < heads.length; a++) {
        const h = heads[a], dx = h.x - px, dy = h.y - py, dz = h.z - pz;
        const d2 = dx * dx + dy * dy + dz * dz;
        if (d2 < 4) flash += Math.exp(-d2 * 1.5) * 0.55;
      }
      flash *= window01(t, 16.0, 19.0, 0.3, 0.5);
    }
    // --- city: records fly to tower facades, bottom floors first
    const pc = clamp((t - (18.45 + r.dCity * 1.9)) / 1.35);
    let emis = 1.0, warm = 0, alpha = 1.0;
    if (pc > 0) {
      const ec = easeInOutCubic(pc);
      const T = r.tile.p;
      px = lerp(px, T[0], ec); pz = lerp(pz, T[2], ec);
      py = lerp(py, T[1], ec) + Math.sin(Math.PI * ec) * r.arc;
      r.quat.slerp(r.tq, ec);
      sx = lerp(sx, 0.97, ec); sy = lerp(sy, 0.97, ec);
      emis = lerp(1.0, r.cityEmis, ec); warm = r.warm * ec; alpha = lerp(1.0, 1.35, ec);
      const land = t - (18.45 + r.dCity * 1.9 + 1.35);
      if (land > 0) flash += Math.exp(-land * 5) * 0.35;
      // city life: slow window flicker
      if (pc >= 1) emis *= 0.85 + 0.15 * Math.sin(t * (0.6 + r.wob * 0.2) + r.wob * 3);
    }
    const glitch = ps < 0.5 ? scanOn * Math.exp(-((dp.x - scanX) ** 2) / 6) * (1 - ps * 2) : 0;
    if (pc <= 0) emis *= 1 - 0.35 * window01(t, 16.0, 18.7, 0.5, 0.4);
    r.pos.set(px, py, pz); r.sx = sx; r.sy = sy;
    r.A[0] = morph; r.A[1] = seal; r.A[2] = glitch; r.A[3] = lerp(1 - 0.68 * e, emis, morph);
    r.B[0] = morph > 0.5 ? r.cellIdx : r.idx; r.B[1] = alphaIn * alpha; r.B[2] = warm; r.B[3] = Math.min(flash, 2);
    // view depth for sorting
    r.depth = tmpV2.copy(r.pos).applyMatrix4(camera.matrixWorldInverse).z;
  }
  for (let i = 0; i < N; i++) order[i] = i;
  order.sort((a, b) => rec[a].depth - rec[b].depth);
  const sc = new THREE.Vector3();
  for (let k = 0; k < N; k++) {
    const r = rec[order[k]];
    sc.set(r.sx, r.sy, 1);
    mat4.compose(r.pos, r.quat, sc);
    mat4.toArray(posArr, k * 16);
    Aarr.set(r.A, k * 4); Barr.set(r.B, k * 4);
  }
  records.instanceMatrix.needsUpdate = true; aA.needsUpdate = true; aB.needsUpdate = true;
}

function updatePoints(t) {
  // dust motes: atmosphere everywhere
  const dp = dust.geometry.attributes.position.array, ds = dust.geometry.attributes.aSize.array, dc = dust.geometry.attributes.aCol.array;
  const dustAmt = 0.35 + 0.65 * smooth(range(t, 3.6, 4.4));
  for (let i = 0; i < DUST_N; i++) {
    const s = dustSeed[i];
    dp[i * 3] = s[0] + Math.sin(t * 0.13 + s[3] * 20) * 2 + t * 0.15;
    dp[i * 3 + 1] = s[1] + Math.sin(t * 0.21 + s[4] * 20) * 1.5 + t * 0.05;
    dp[i * 3 + 2] = s[2] + Math.cos(t * 0.17 + s[5] * 20) * 2;
    ds[i] = 0.035 + s[3] * 0.06;
    const warm = s[4] < 0.25;
    dc.set([warm ? 1.0 : 0.85, warm ? 0.7 : 0.87, warm ? 0.25 : 0.9, (0.25 + 0.5 * s[5]) * dustAmt], i * 4);
  }
  dust.geometry.attributes.position.needsUpdate = true; dust.geometry.attributes.aSize.needsUpdate = true; dust.geometry.attributes.aCol.needsUpdate = true;

  // comets: agents (layer 03) + capital flows (city)
  const cp = comets.geometry.attributes.position.array, cs = comets.geometry.attributes.aSize.array, cc = comets.geometry.attributes.aCol.array;
  cc.fill(0);
  let slot = 0;
  const Y = [1.0, 0.52, 0.004];
  const agentVis = window01(t, 15.95, 19.2, 0.35, 0.6);
  projected.agents.length = 0;
  if (agentVis > 0) {
    AGENTS.forEach((a, k) => {
      if (slot >= COMET_MAX) return;
      const base = slot * TRAIL;
      for (let j = 0; j < TRAIL; j++) {
        agentPos(a, t - j * 0.012, tmpV);
        cp.set([tmpV.x, tmpV.y, tmpV.z], (base + j) * 3);
        const f = 1 - j / TRAIL;
        cs[base + j] = j === 0 ? 0.55 : 0.2 * f + 0.03;
        const hot = j === 0 ? 3.5 : 1.6 * f * f;
        cc.set([Y[0] * hot + (j === 0 ? 1 : 0), Y[1] * hot + (j === 0 ? 0.8 : 0), Y[2] * hot + (j === 0 ? 0.5 : 0), agentVis * (j === 0 ? 1 : f)], (base + j) * 4);
      }
      if (k < 3) { agentPos(a, t, tmpV); projected.agents.push(tmpV.clone().project(camera)); }
      slot++;
    });
  }
  // capital flows
  const ac = arcGeo.attributes.aCol.array; ac.fill(0);
  FLOWS.forEach((f, fi) => {
    const s = (t - f.t0) / f.dur;
    const arcA = clamp(s * 3) * (1 - clamp((s - 1) * 1.5)) * (f.main ? 0.5 : 0.22) * window01(t, 18.8, 29.9, 0.3, 0.8);
    for (let k = 0; k < ARC_SEG * 2; k++) {
      const u = (k >> 1) / ARC_SEG;
      const lit = u < s ? 1 : 0.0;
      ac.set([Y[0], Y[1], Y[2], arcA * lit], (fi * ARC_SEG * 2 + k) * 4);
    }
    if (s < 0 || s > 1.25 || slot >= COMET_MAX) return;
    const base = slot * TRAIL;
    for (let j = 0; j < TRAIL; j++) {
      const sj = clamp(s - j * 0.012);
      flowPos(f, easeInOutCubic(clamp(sj)), tmpV);
      cp.set([tmpV.x, tmpV.y, tmpV.z], (base + j) * 3);
      const fdec = 1 - j / TRAIL, alive = s <= 1 ? 1 : 1 - (s - 1) * 4;
      cs[base + j] = j === 0 ? (f.main ? 0.55 : 0.4) : 0.22 * fdec + 0.04;
      const hot = (j === 0 ? 4 : 2 * fdec * fdec) * (f.main ? 1.3 : 0.9);
      cc.set([Y[0] * hot + (j === 0 ? 1.2 : 0), Y[1] * hot + (j === 0 ? 1 : 0), Y[2] * hot + (j === 0 ? 0.7 : 0), Math.max(0, alive) * (j === 0 ? 1 : fdec)], (base + j) * 4);
    }
    slot++;
  });
  for (const k of ['position', 'aSize', 'aCol']) comets.geometry.attributes[k].needsUpdate = true;
  arcGeo.attributes.aCol.needsUpdate = true;
}

function seek(t, o = {}) {
  // camera
  const c = hermite(CAM, t);
  camera.position.set(c[0], c[1], c[2]);
  // handheld micro-drift for realism
  camera.position.x += Math.sin(t * 0.9) * 0.08 + Math.sin(t * 2.3) * 0.03;
  camera.position.y += Math.sin(t * 1.1 + 1) * 0.06 + Math.sin(t * 2.9) * 0.02;
  camera.lookAt(c[3], c[4], c[5]);
  const roll = t < 11 ? Math.sin(t * 0.4) * 0.03 : Math.sin(t * 0.3) * 0.012;
  camera.rotateZ(roll);
  camera.fov = c[6]; camera.updateProjectionMatrix(); camera.updateMatrixWorld();
  const fc = hermite(FOCUS, t);
  for (const m of [recMat, mirMat]) {
    m.uniforms.uTime.value = t; m.uniforms.uFocus.value = fc[0]; m.uniforms.uFocusRange.value = fc[1];
    m.uniforms.uFogNear.value = t < 11 ? 55 : 80; m.uniforms.uFogFar.value = t < 11 ? 125 : 190;
  }
  recUniforms.uFocus.value = fc[0]; recUniforms.uFocusRange.value = fc[1];
  mirMat.uniforms.uMirrorAlpha.value = 0.45 * smooth(range(t, 18.6, 21));

  // plate: opening shot
  const pu = plateMat.uniforms;
  pu.uTime.value = t;
  pu.uExp.value = smooth(range(t, 0.0, 1.6)) * (1 - smooth(range(t, 3.55, 4.05))) * 0.88;
  pu.uScale.value = lerp(1.04, 1.13, easeOutCubic(range(t, 0, 3.4))) * (1 + 0.9 * easeInCubic(range(t, 3.3, 4.05)));
  pu.uBlur.value = 0.35 * easeInCubic(range(t, 3.25, 4.05));
  pu.uRot.value = THREE.MathUtils.degToRad(lerp(-1.2, 1.8, range(t, 0, 4)));
  pu.uOff.value.set(0, lerp(0.012, -0.01, range(t, 0, 4)));
  pu.uScanY.value = lerp(-0.05, 1.12, easeInOutCubic(range(t, 1.7, 3.5)));
  pu.uScanAmt.value = window01(t, 1.7, 3.8, 0.3, 0.3);
  pu.uVoid.value = smooth(range(t, 3.6, 4.4));

  // scene elements
  scanner.position.set(lerp(-46, 46, range(t, 8.15, 10.6)), 0, 20);
  scanMat.uniforms.uAlpha.value = 0.22 * window01(t, 8.1, 10.7, 0.25, 0.35);
  scanMat.uniforms.uTime.value = t;
  threadMat.uniforms.uTime.value = t;
  threadMat.uniforms.uAlpha.value = window01(t, 11.4, 18.9, 1.0, 0.6);
  threadMat.uniforms.uWave.value = t - 13.65;
  groundMat.uniforms.uAlpha.value = smooth(range(t, 10.8, 12.5));
  groundMat.uniforms.uPulse.value = t > 11.0 && t < 14 ? (t - 11.0) * 22 : (t > 18.4 && t < 21.4 ? (t - 18.4) * 16 : 0);

  updateRecords(t);
  updatePoints(t);

  // post
  const fu = finalPass.uniforms;
  fu.uTime.value = t;
  fu.uFade.value = smooth(range(t, 0.0, 0.9)) * (1 - smooth(range(t, 29.2, 30.0)));
  fu.uFlash.value = 0.22 * Math.exp(-Math.abs(t - 3.95) * 14) + 0.10 * Math.exp(-Math.max(0, t - 11.0) * 7) * (t >= 11.0 ? 1 : 0);
  fu.uExp.value = t < 24.6 ? 1 : lerp(1, 0.32, smooth(range(t, 24.6, 25.8)));
  fu.uCA.value = 0.5 + 1.6 * window01(t, 3.3, 5.0, 0.5, 0.9) + 1.0 * window01(t, 10.4, 11.6, 0.6, 0.6);
  bloom.strength = 0.8 + 0.4 * window01(t, 10.6, 12.0, 0.4, 0.8) + 0.15 * window01(t, 18.6, 30, 2, 1);

  if (o.fade != null) fu.uFade.value = o.fade;
  if (o.exp != null) fu.uExp.value = o.exp;
  if (o.grain != null) fu.uGrain.value = o.grain;
  composer.render();
  if (!window.__FILM) updateUI(t, { projected });
}

// ------------------------------------------------------------------ boot
async function boot() {
  await document.fonts.ready;
  await Promise.all(['300 20px Inter', '400 20px Inter', '500 20px Inter', '600 20px Inter', '400 20px Mono', '500 20px Mono'].map(f => document.fonts.load(f)));
  // atlases were drawn at import time; redraw now that fonts are guaranteed
  const a2 = buildAtlases();
  docTex.image = a2.doc; cellTex.image = a2.cell; docTex.needsUpdate = true; cellTex.needsUpdate = true;
  await plateReady;
  if (window.__FILM) return;
  await new Promise(r => setTimeout(r, 200));
  seek(0);
}
const readyP = boot();
export { seek, readyP, camera, projected };
window.__duration = DURATION;
if (!window.__FILM) { window.__seek = seek; window.__ready = readyP; }
// live preview: ?t=12.5 renders a still, ?play plays in real time
const qs = new URLSearchParams(location.search);
if (!window.__FILM) readyP.then(() => {
  if (qs.has('t')) seek(parseFloat(qs.get('t')));
  if (qs.has('play')) { const t0 = performance.now(); const loop = () => { seek(((performance.now() - t0) / 1000) % DURATION); requestAnimationFrame(loop); }; loop(); }
});
