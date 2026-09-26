# Between Capital and the Asset — explainer film

Narrated motion-graphics explainer of the strategy note **`Propchain — Between Capital and the Asset.pdf`** (September 2026, working draft for internal discussion). Part of the four-film series described in `explainers/BRIEF.md`.

| File | What |
|---|---|
| `capital-and-asset-preview.mp4` | 1920×1080, 30 fps, two-pass H.264 ~0.72 Mbps + 160k AAC (< 29 MB) |
| `capital-and-asset-1080p.mp4` | 1920×1080, 30 fps, two-pass H.264 ~2.9 Mbps + 160k AAC (< 95 MB), light `hqdn3d` |
| `STORYBOARD.md` | Learning goals, arc and beat sheet (written before the build) |

**Runtime: 4:00** (240.2 s).

## What the viewer should come away with

1. About twenty parties sit between capital and the asset. Prop.com sells outcome services; Propchain builds the rails. For each party: own it, tool it or onboard it, and in which order.
2. **The rule**: every party splits into an **act** (stays independent → we tool it), a **process** (desk work, most of the hours and the fee → a Prop.com service) and **data** (→ Propchain attests it). Worked example: the valuer. Independence is the product.
3. **The map**: eight layers in the order a deal moves; every party gets one verb — **Onboard**, **Tool**, **Serve** — and the chips physically regroup into those three columns.
4. **Prop.com's order**: sell the outcome of a desk, not the AI (seats fold into one desk); five criteria → three tiers (now / next / later).
5. **Propchain's order**: lenders → valuers → notaries → assurance and peers → source and finality, each step unlocking the next. Dependency, not rank: a notary tool with nothing to settle is a demo; with a financed bid and a mark, it's a closing.
6. How it holds: tools are free or near-free and never produce the act; services make records, records make rails, rails create demand; Prop.com is only a participant on the rails, and every read is logged.

## Beat list (final timings)

| Time | Chapter | Beat |
|---|---|---|
| 0:00 | — | Title over a dimmed city aerial: *Between Capital and the Asset* |
| 0:05 | 01 The middle | Five stock strips (broker, valuer, lawyer, notary, lender) → capital and asset nodes with ~20 parties crowding the line |
| 0:13 | 01 | The crowd collapses into dots; the Prop.com lane (outcome services, cash flow now) appears above it |
| 0:21 | 01 | The Propchain rail draws beneath it; every party drops a connector onto it ("including Prop.com's competitors") |
| 0:27 | 01 | The question: own it? tool it? onboard it? And in which order? |
| 0:34 | 02 The rule | One party splits into three strata: act, process, data |
| 0:39 | 02 | Act: signature, deed, audit opinion → *stays independent · we tool it* |
| 0:49 | 02 | Process: data rooms, models, draft deeds; hours and fee bars → *becomes a Prop.com service* |
| 0:59 | 02 | Data: rent roll → NOI, comparables → mark with travelling pulses → *Propchain attests it* |
| 1:08 | 02 | The valuer: signed valuation / model, comparables, AVM / mark, inputs, lineage |
| 1:14 | 02 | The act linked to "the party that profits from the deal" loses worth → **Independence is the product.** |
| 1:23 | 03 The map | Eight layers draw left to right, parties under each |
| 1:30 | 03 | Legend: Onboard · Tool · Serve; participants turn grey (onboard), independents get locks (tool), process roles turn yellow (serve) |
| 1:57 | 03 | All chips regroup into three verb columns |
| 2:01 | 04 Prop.com · the order | Analysts at work → "We sell the outcome of a desk, not the AI" → nine seats with desk share; five fold into one Prop.com desk |
| 2:10 | 04 | Five criteria, then Tier 1 now / Tier 2 next / Tier 3 later, each with its reason |
| 2:37 | 05 Propchain · the sequence | Five stations on a rail with stock thumbnails; a pulse unlocks each next station; each shows what it unlocks |
| 3:15 | 05 | Dependency, not rank: *a demo* vs *a closing* |
| 3:25 | 06 How it holds | Tools for acts that stay theirs: prepares, presents, records; never produces the act; free or near-free |
| 3:33 | 06 | The four-step flywheel (services → records → rails → demand) |
| 3:43 | 06 | Prop.com as one participant among many; same identity and permissions; Proof of Permission read log |
| 3:52 | — | **Own the desk. Tool the act. Onboard the market.** → Propchain end card |

## Decisions made without sign-off

- **Length.** The narration came out at 243 s of speech for the script. To keep the film to the brief's 4-minute ceiling I dropped two generated lines (the criteria list, v18, and "land and expand", v22) and applied a pitch-preserving `atempo=1.075` to the narration in the mix. The voice settings sent to ElevenLabs are exactly the series settings (George, `eleven_multilingual_v2`, speed .95); the tempo change is a post-process only. If it sounds too quick, set `TEMPO = 1.0` in `tools/timeline.py` and re-run the pipeline: the runtime becomes about 4:18 and costs no credits.
- **Criteria and land-and-expand.** The five criteria (FTE density, desk share, licence barrier, data yield, margin) are on screen and not spoken. "Land and expand" is not in the film.
- **Map verbs.** Parties are coloured by the deck's slide 07 map (Onboard / Tool / Serve). Three of the slide 06 layer entries have no verb on the slide 07 map: *data providers*, *regulator* and *vendors*. They stay neutral and fade out when the chips regroup. *KYC · AML* and the *origination* roles (brokers, originators, placement, debt advisers) are shown as Serve, following slide 06 ("Serve, then automate", "Serve, tool") and slide 07's "Origination desk" and "Debt advisory". *Payment rails* is shown as "Payments" (Serve: slide 07 "Payment operations"), and *escrow bank* is shown as Tool.
- **Sequence.** I used the five steps of slide 12. The finer "Order" column of slide 11 (lawyers 6, registry "Later") is folded into step 05, as the deck does.
- **Seats.** The desk-share bars are the deck's qualitative ratings (very high = 4 … low = 1). The film labels them qualitative. The narration says "four or five analyst seats", as the deck does, and the animation folds the five highest-rated seats.
- **Not included.** Slide 16's open "Decide" items (internal discussion points).
- **Stock.** The "Assurance and peers" station uses a clip of a professional reviewing documents with a client, because I found no clip of auditors specifically. The valuer clip is a professional with a checklist and hard hat (Pexels calls her a realtor).
- **Music bed.** One 240 s ElevenLabs music cue, composed in six sections that match the chapter lengths. UI accents (pops, ticks, soft bells, swooshes) are synthesised in `tools/mix.py` rather than generated, to save credits. Narration sits about 10.5 dB above music and effects while speaking.

## Claims the business should double-check

- **"Some twenty parties"**: the deck's own phrase. The crowd shows 20 representative names drawn from slides 04–06.
- **"Tier two … we deliver the process under a named partner's act"**: from slide 10. The partner licence is still an open decision (slide 16).
- **"Every asset with attested NOI carries a debt quote"**: slide 12, step 01. This describes the target state, not something live today.
- **E-notarisation / notary sequencing**: the deck flags the scope as "to be confirmed". The film says nothing about e-notarisation.
- **Licence assumptions**: the deck assumes Germany and Luxembourg. The film does not name jurisdictions.
- **The deck is marked "working draft for internal discussion".** The film is built for internal use too.
- **"Structuring real estate for the autonomous era"** on the end card is reused from the launch film's end card. It is not in this deck.

## Credits and budgets

**ElevenLabs** (voice George `JBFqnCBsd6RMkjVDRZzb`, `eleven_multilingual_v2`, series settings):
- Narration: 33 lines, 3,335 characters, generated once with `/with-timestamps` for word-level sync. The account counter moved from 9,446 to 12,964 across the narration run (+3,518).
- Music: one `music_v1` cue (240 s), made through `/v1/music/stream`. The account's `character_count` did not change across the successful call (20,403 before and after), so music seems to be metered separately. The first attempt returned HTTP 502. Other sessions share the account and were generating at the same time, so the counter cannot attribute any cost to that failed attempt.
- No SFX generations.
- Total attributable to this film: about 3.5k characters plus one music cue, within the 15,000 budget. All generations are cached in `audio/` (committed); `tools/eleven.py` never regenerates unchanged requests.

**Pexels**: 7 API calls out of the 30 allowed (one search per slot, cached in `stock/search/`). Clips, all from pexels.com:

| Use | Photographer | URL |
|---|---|---|
| Broker (montage) | Kindel Media | https://www.pexels.com/video/men-shaking-hands-7577728/ |
| Valuer (montage, rule, sequence 02) | Pavel Danilyuk | https://www.pexels.com/video/a-realtor-doing-her-checklist-7816376/ |
| Notary (montage, sequence 03) | Mikhail Nilov | https://www.pexels.com/video/a-person-holding-a-pen-8731580/ |
| Lawyer (montage), independence beat | Kampus Production | https://www.pexels.com/video/a-person-signing-a-document-8439245/ |
| Lender (montage, sequence 01) | RDNE Stock project | https://www.pexels.com/video/a-person-giving-applying-for-a-loan-8293500/ |
| Assurance and peers (sequence 04) | Kampus Production | https://www.pexels.com/video/realtor-talking-to-his-client-using-digital-tablet-8814720/ |
| Analysts (the offer) | Artem Podrez | https://www.pexels.com/video/people-working-together-6780074/ |
| Property (sequence 05) | Cory Clean | https://www.pexels.com/video/modern-residential-neighborhood-aerial-view-31004744/ |
| City (title) | K | https://www.pexels.com/video/statue-on-roundabout-in-city-13764229/ |

Icons: lucide-static (ISC), 1.5 px stroke. Fonts and logo: `propchain-reel/assets/`.

## Rebuild

```bash
cd explainers/capital-and-asset
npm install                              # playwright 1.56.1 (uses /opt/pw-browsers), lucide-static
pip install numpy scipy pillow imageio-ffmpeg
python3 tools/eleven.py vo               # cached; writes audio/vo_lines.json
python3 tools/timeline.py                # line start times, tempo -> audio/timeline.json
python3 tools/fetch_stock.py             # CDN downloads only (no API calls) -> stock/clips
node render.mjs stills 12 60 118         # previews -> out/stills
node render.mjs frames --workers 4 --fps 30 --to 7206
python3 tools/mix.py                     # -> out/mix.wav
tools/encode.sh                          # -> the two MP4s
```

- `index.html`, `film.js`, `core.js`, `scenes.js`, `film.css`: the film. It is DOM + SVG only, and every frame is a pure function of `t` (`window.__seek`). `index.html?t=95` shows a still.
- Picture timing comes from the narration's word timestamps. Scenes anchor to words through `W('v15', 'notary')`, so re-voicing a line re-times the picture automatically.
- `render.mjs` is a copy of the launch-film renderer that launches Chromium with GPU compositing disabled. SwiftShader GPU raster produced stale-tile ghosting on this DOM-heavy page, and software compositing is also faster here (~0.04 s/frame).
