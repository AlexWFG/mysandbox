# Propchain explainer series — shared production brief

Four explainer films, each made by its own session, from these decks in the repo root:

| Slug | Deck | Branch |
|---|---|---|
| `mandate-market` | `Propchain — The Mandate Market.pdf` | `claude/explainer-mandate-market` |
| `capital-and-asset` | `Propchain — Between Capital and the Asset.pdf` | `claude/explainer-capital-and-asset` |
| `assurance` | `Propchain — Assurance Fraud, Bonds and Insurance.pdf` | `claude/explainer-assurance` |
| `architecture` | `Propchain — Technical Architecture.pdf` | `claude/explainer-architecture` |

Work only in `explainers/<slug>/` on your own branch. Never push to another session's branch.

## What these films are

The launch film (`propchain-reel/film/`, watch `propchain-reel/film/propchain-film-v2-preview.mp4`) was cinematic and emotional. These are **explainers**: less cinematic, more *beautifully flowing motion graphics*. The goal is that someone who will never read a 16-page deck watches the film and truly understands how the concept works — how things flow, act and behave.

- **Understanding first.** Turn every important concept in the deck into a visual mechanism: diagrams that build step by step, flows with things moving through them, before/after comparisons, worked examples with real numbers from the deck. If a slide says "X matches Y when Z", show X, Y and Z and animate the match.
- **You choose the length.** 1 to 4 minutes, whatever the content genuinely needs. Don't pad, don't rush. Pacing target: one idea at a time, each idea on screen long enough to read and absorb (roughly 5–10 s per beat).
- **Cut the deck, don't transcribe it.** Decks are text-heavy; decide what the viewer must understand and in what order. Restructure freely. Keep facts and numbers exactly as the deck states them.
- **Narrated.** Narration carries the explanation; on-screen text is short labels and key numbers, never paragraphs.
- **Some stock footage** (Pexels) to ground concepts in the real world — people, buildings, offices — used sparingly between diagram sequences. Most screen time is motion graphics.
- **Iconography.** Clean line icons (e.g. `npm i lucide-static` — SVGs, one consistent stroke weight), animated in, never clip-art.

## Visual system (keep it identical across the series)

- Background: deep charcoal `#0B0B0C` → `#141416` gradients (a light `#F7F6F2` paper variant is allowed for a section if it helps clarity, as in the decks).
- Brand yellow `#FFBE06` for the one thing that matters in each frame (active node, key number, the flow). Everything else ink `#F4F2EC` / dim `rgba(244,242,236,.62)` / lines `rgba(244,242,236,.16)`.
- Type: Inter 300/400/500/600 (headlines light 300, tight tracking) and JetBrains Mono 500 for eyebrows, labels, data. Fonts + logo are in `propchain-reel/assets/` (`logo-white.svg`, `logo-mark.svg`, `inter-*.woff2`, `jetbrains-mono-*.woff2`).
- Motion: eased (quint/cubic out), nothing linear, nothing bouncy. Elements draw on (strokes), slide 20–40 px with a short blur-in, flows use travelling yellow pulses along paths. Camera-like pushes on diagrams are welcome.
- 1920×1080, 30 fps. Subtle grain + vignette (lighter than the launch film). Chapter marker top-left (`01  THE PROBLEM` style), Propchain logo on open and end card.
- Open with a 3–5 s title (deck title + one-line promise) and end with the Propchain end card.

## Tooling you can reuse (all in `propchain-reel/`)

- `render.mjs` — deterministic headless-Chromium frame renderer. `node propchain-reel/render.mjs stills --page <path-to-your-index.html relative to propchain-reel> 3 12.5 …` for previews; `frames --page … --workers 3 --fps 30 --to <frames>` for the full render. Pages must expose `window.__ready` (promise) and `window.__seek(t)` (sync or async). Serve paths are relative to `propchain-reel/`, so it's simplest to put your film under `propchain-reel/../explainers/<slug>` and run a copy of `render.mjs` from your folder, or pass the right relative path. Adapt as needed.
- `film/modules.js`, `film/film.js`, `film/film.css` — the launch film's compositor (stock frame sequences, press windows, titles, counters, panels, chain/split diagrams, grain/letterbox fx). Copy and adapt; don't edit the originals.
- `film/tools/pexels_search.py`, `film/tools/fetch_stock.py` — Pexels search (one API call per slot, cached) and download + frame extraction.
- `film/tools/eleven.py` — ElevenLabs narration / music / SFX with on-disk caching. `film/mix.py` — mixer with voice ducking.
- `sheet.py` — contact sheets for reviewing stills.

Headless Chromium uses SwiftShader (no GPU): DOM/SVG/Canvas2D frames render in ~0.3–0.6 s; heavy WebGL is ~2 s/frame. Prefer DOM/SVG motion graphics; use WebGL only where it truly adds something.

## APIs and budgets (accounts are shared with other work — stay within these)

Both keys are injected by the environment's proxy; call the APIs with no key and they authenticate.

- **ElevenLabs** (`https://api.elevenlabs.io/v1/...`): budget **≤ 15,000 credits per film** for voice, music and SFX combined. Check `GET /v1/user/subscription` before and after. Cache every generation; never regenerate unchanged text.
  - Narrator for the whole series: **George** `JBFqnCBsd6RMkjVDRZzb`, model `eleven_multilingual_v2`, settings `{stability .5, similarity_boost .8, style .35, use_speaker_boost true, speed .95}` (same as the launch film). Do **not** use the "Russell" voice — it belongs to another project.
  - Music: `POST /v1/music` with a `composition_plan` (sections with durations). Never name real artists or composers in prompts (rejected as copyright). Explainers want calmer, flowing, modern, optimistic-intelligent beds — not trailer hits.
  - Narration should sit ~10 dB above music + SFX (see `film/mix.py` ducking).
- **Pexels** (`https://api.pexels.com/videos/search?...`): **≤ 30 API calls per film**. Downloads from the CDN (`videos.pexels.com`) don't count; use `curl -A Mozilla/5.0` (Python's default UA gets 403). Record photographer + URL in a manifest.

## Process

1. Read the whole deck (`pdftotext -layout`, and render pages to images with `pdftoppm -r 60` to see its diagrams). Install `poppler-utils` if missing.
2. Write `explainers/<slug>/STORYBOARD.md`: the viewer's learning goals, the narrative arc, and a beat sheet (time, narration line, visual, on-screen text). Commit and push it early.
3. Build, then review **stills at every beat** with contact sheets and fix what doesn't read clearly or look premium. Iterate until it's genuinely clear and beautiful.
4. Generate narration first and time the picture to it (not the other way round).
5. Render, mix, encode. Deliver in `explainers/<slug>/`:
   - `<slug>-preview.mp4` — under 29 MB (two-pass ~1.5 Mbps video, 160k AAC).
   - `<slug>-1080p.mp4` — under 95 MB (two-pass, light `hqdn3d` denoise if grain bloats it).
   - Don't commit frames, raw stock or other bulk (gitignore them). Do commit the ElevenLabs audio cache so credits are never spent twice.
6. Commit and push to your branch as you go (the container can restart at any time and anything unpushed is lost). Finish with `explainers/<slug>/README.md`: runtime, beat list, credits used, Pexels credits, and any claims the business should double-check.

Accuracy: every figure, name and mechanism must come from the deck. Where the deck is a "working draft" or hedges, keep the hedge. Mark anything you're unsure of in the README rather than inventing.
