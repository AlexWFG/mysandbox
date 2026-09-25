# Propchain — launch reel (30s)

`out/propchain-reel.mp4`: 1920×1080, 30 fps (rendered at 60 fps and blended for a 180° shutter), H.264 + AAC stereo score.

## Story

One continuous transformation. The same 2,304 objects move through every act:

| Time | Act | Picture | Line |
|---|---|---|---|
| 0–4s | The asset | Hero photography, low angle, push-in. A survey scan reads the towers | **$380 trillion.** The largest asset class on earth. |
| 4–8s | The reality | The building bursts into its paperwork: valuation reports, rent rolls, Grundbuch extracts, leases, emails | **Still run on PDFs, spreadsheets and paper.** |
| 8–11s | The thesis | A machine scanner sweeps the paper and every document garbles. The storm starts to swirl | **Markets are going autonomous. But AI can't read real estate.** |
| 11–13.5s | Layer 01 | Impact: the vortex snaps into a lattice and paper becomes machine-readable records | **Structured.** |
| 13.5–16s | Layer 02 | A proof wave seals every record and lineage threads light up. Proof of Ingestion, Permission, State and Agency | **Attested.** |
| 16–18.5s | Layer 03 | Identified agents race through the data with KYA tags | **Agent-ready.** |
| 18.5–25s | The market | The records fly out and rebuild the city floor by floor, now machine-readable. Capital arcs between towers: List → Diligence → Match → Finance → Settle. Live proof points | **Capital at the speed of software.** 11,000+ units · €90B+ · 4 proofs live |
| 25–30s | End card | Propchain wordmark | **Structuring real estate for the autonomous era.** Machine-readable · Attested · Agent-ready |

## Build

```bash
npm install
pip install numpy scipy pillow imageio-ffmpeg
./build.sh            # score -> frames -> out/propchain-reel.mp4
```

- `src/main.js`: the film. Three.js scene, camera choreography and grading. `window.__seek(t)` renders any frame deterministically.
- `src/textures.js`: procedural document and data-record atlases.
- `src/ui.js`: typography and HUD, all driven by time.
- `audio.py`: synthesised sound design and score, cut to the picture cue sheet.
- `render.mjs`: headless-Chromium frame capture (`node render.mjs stills 4.2 12.5` for previews).

For a live preview, serve the folder and open `index.html?play`, or `index.html?t=14.2` for a still.

Photography and logo come from the Propchain infrastructure deck (September 2026).
