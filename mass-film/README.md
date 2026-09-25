# MASS — "One Economy" · 30 s cinematic film

A 30-second brand film for **Mass (Managed Administrative & Sovereign Services)**:
real-world photography graded like a feature, a crisp digital layer in the mass.inc
palette, a night-side Earth for the network payoff, and a synthesised score with sound
design locked to every cut.

- **Film:** `out/MASS_OneEconomy_30s_1080p.mp4` (1920×1080, 24 fps, H.264 + AAC 48 kHz stereo)
- **Share copy:** `out/MASS_OneEconomy_30s_1080p_share.mp4` (same film at 7.2 Mbps, under 30 MB for messaging and uploads)
- **Score stem:** `out/mass_score.wav` (24-bit, −15.6 LUFS)
- **Storyboard and rationale:** [`STORYBOARD.md`](STORYBOARD.md)
- **Credits and licences:** [`CREDITS.md`](CREDITS.md)

## The story in 30 seconds
| Time | Beat | Line on screen |
|---|---|---|
| 0–9.5 s | The paper world: typewriter keys, a note stamped PENDING, empty waiting rooms, a customs hall, a day counter that resets at the border | *Every economy runs on companies. Yet every company still lives on paper. Months to start one. Every border, back to zero.* |
| 8–9.5 s | Silence | *Until now.* |
| 9.5–11.5 s | The Mass mark forms against Dubai at sunset | **MASS**, Managed Administrative & Sovereign Services |
| 11.5–13.5 s | 02:14 in Karachi: Aisha forms her Abu Dhabi company through the Mass Agent (formed, licensed, bank account, screened) | *A company, born in minutes.* |
| 13.5–15.5 s | Abu Dhabi: six stacked layers (registry, licences and rules, banking, zones, corridors, markets) locked by government-held keys | *Every rule runs as code. Governments hold the keys.* |
| 15.5–17.5 s | A container ship in the Suez Canal, its cargo carrying a live record | *Trade flows on one live record.* |
| 17.5–23.5 s | The frame opens to 16:9 on Earth at night: Abu Dhabi ignites, then corridors reach the 13 target corridor countries from the deck | *Every nation, a sovereign node. Connected into one economy.* |
| 23.5–25.5 s | Four hits | **Formed. Licensed. Banked. Recognised.** |
| 25.5–30 s | Lockup over the mass.inc dust band | *The operating system for sovereign economies.* · mass.inc |

## How it's made
Everything is procedural and reproducible. Every shot is Python code, with no
editing or compositing app involved.

```
src/timeline.py   single source of truth for every cue (shared by picture and sound)
src/engine.py     linear-light compositor: filmic shoulder, bloom, halation, grain, CA,
                  grading, frosted glass, kerned typography (HarfBuzz + Skia), Mass mark
src/globe.py      ray-traced night Earth: Black Marble lights, atmosphere, sunrise limb
src/shots.py      the twelve shots
src/audio.py      score and sound design (numba DSP: SVF filters, PolyBLEP oscillators,
                  convolution reverbs, sidechain, glue compression, true-peak limiter)
src/render.py     parallel renderer → lossless segments → final encode
```

The Mass mark is rebuilt as vector paths fitted to the mass.inc header logo (pixel-mask
fit, sub-pixel error), and the palette is sampled from the site.

### Rebuild
```bash
apt-get install -y ffmpeg fonts-inter fonts-jetbrains-mono libegl1
pip install numpy scipy opencv-python-headless skia-python uharfbuzz numba soundfile pyloudnorm
cd src
python3 audio.py ../out/mass_score.wav
python3 render.py --video ../out/mass_picture_lossless.mkv --workers 4
python3 finish.py      # two-pass H.264 + AAC delivery file and a contact sheet
```
Stills for review: `python3 render.py --stills 3.7,11.0,20.5,28.0`.
