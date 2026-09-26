# The Mandate Market — explainer film

Narrated motion-graphics explainer made from `Propchain — The Mandate Market.pdf` (concept note, September 2026), following `explainers/BRIEF.md`.

- **`mandate-market-1080p.mp4`**: 1920×1080, 30 fps, H.264 two-pass + AAC 192k.
- **`mandate-market-preview.mp4`**: 1280×720, two-pass (~750 kbps so it fits under 29 MB; 1.5 Mbps would not at 4:00), AAC 160k — 27.7 MB. The 1080p file is 93.3 MB.
- **Runtime: 4:00** (240.0 s).

The film teaches the matching mechanics with one example that runs all the way through: **mandate M-0417** (logistics, Germany, €10–25M) scores a logistics asset in Munich, credit box **L1** quotes the pair, and the pair's bid comes out of the deck's worked example (NOI €800k, test price €13.0M).

## Beat list (as built)

| Time | Chapter | What the viewer sees and hears |
|---|---|---|
| 0:00 | Title | Propchain logo; *The Mandate Market*; the three object glyphs (asset, mandate, credit box) link up |
| 0:05 | 01 The problem | Stock: order-book screen → a clean order book (identical share tokens, one price axis, price-time priority, best bid meets best ask) |
| 0:14 | | Five unique buildings, each with its own value vector (yield, term, credit, location, capex): no two are substitutes |
| 0:19 | | Two-sided ranked matching market: assets and mandates in two columns, scoring lines with ranks in both directions |
| 0:29 | 02 The objects | Three cards. **Asset**: NOI, cap rate, WALT, tenant credit, vacancy, each with source, refresh and confidence, plus the seller instruction. **Buy mandate**: scores assets, never names one. **Credit box**: `quote(asset \| sponsor)`. The seller is flagged as the fourth scorer |
| 0:51 | 03 The mandate | Stock: logistics aerial. Then a sidebar shows M-0417's five parts, highlighted as each one comes up |
| 0:54 | | Hard filters as a live table: 7 assets are checked against class, country, lot size and cap rate. Four fail with the failing field logged, and the three survivors close up into the book |
| 1:06 | | Cap-rate utility: linear from 5.25% to 7.0%, then capped. A marker reads the value and its utility (6.15% → 0.51) |
| 1:15 | | Small multiples: lot-size plateau (€12M and €18M both score 1.0) and stepped tenant credit (IG 1.0, BB 0.6, B 0.2). Caption: why utilities, not distance |
| 1:24 | | Confidence decay c(t): a 6.2% cap rate attested last week overtakes a 6.4% cap rate attested five months ago |
| 1:33 | | Weights 45/25/20/10 fill into a score (0.68). A 7% yield with 20% vacancy trips the vacancy floor and scores 0 |
| 1:47 | | Tie-break: a near-tie reorders on longer WALT, with time priority struck through, giving M-0417's ranked book |
| 1:56 | 04 The debt | Stock: lenders. Asset (collateral) + mandate (sponsor) → **the pair (a, m)**. L1 fires 55% LTV · 185 bps, L2 60% · 210 bps, L3 is silent (sponsor below tier). A quote set is formed, with the attestation gate: NOI attested within 60 days |
| 2:14 | 05 From score to bid | Price ⇄ debt loop, then the worked-example ledger. The three proceeds tests are drawn as bars: €7.15M (LTV) / €9.47M (DSCR) / €10.67M (debt yield). LTV binds. Price splits into €7.15M debt and €5.85M equity (debt service €465k, cash to equity €335k, 5.7% year-one yield). A schematic r(P) curve is bisected against the 12% target to find P\*, then bid = min(P\*, ask). A more generous credit box shifts P\* right |
| 2:50 | 06 The seller | The seller's ranking (price, certainty, speed, conditionality). A higher unfinanced bid is overtaken by a slightly lower bid with a firm term sheet |
| 3:00 | 07 Clearing | Deferred acceptance on 3 mandates × 3 assets, with each side's rankings visible. Round 1: two mandates hit asset A, A holds M-2 and releases M-0417. Round 2: M-0417 moves to B and its debt is re-quoted; B trades up and releases M-3, which is rejected by A and held by C. The pairs lock, and a would-be blocking pair is tested and fails |
| 3:25 | | Stock: handshake. Caption: no reason to go around the platform |
| 3:28 | 08 A living book | Four events (asset state, mandate change, credit-box fill, rates and grids) pulse into the engine. An asset that stops attesting decays (c 1.00 → 0.38) and sinks to the bottom of three books at once, so decay replaces time priority |
| 3:42 | 09 The claim | Layers 03 / 02 / 01. The engine is known mathematics; the missing pieces are the attested vector (01) and a credit box that can trust it (02). List → Diligence → Match → Finance → Settle |
| 3:52 | | **Matching is a data outcome.** |
| 3:55 | End card | Propchain logo over the city at dusk |

The storyboard (learning goals, arc, planned beats and what was cut from the deck) is in `STORYBOARD.md`.

## Decisions made without a check-in

- **Length.** The narration first came out at 4:17. To land on 4:00 I dropped two generated lines and played the voice at a light 1.05× tempo (word timestamps are scaled to match). The dropped lines are *"So a more generous credit box raises the bid, directly"*, whose idea stays on screen as a caption, and *"Visibility is set per object, up to double-blind…"*. The open / one-way / double-blind section of the deck is therefore not in the film. Both audio files remain in the cache.
- **Other cuts, for focus:** the capital-stack generalisation (slide 13), hold windows and hysteresis, proposer advantage, the Pareto-frontier flag, the full credit-box field table and the four open questions on slide 17.
- **Sync.** Narration was generated with ElevenLabs `with-timestamps`, so every build in the picture is cued to the exact spoken word (`timeline.json`).
- **Music.** The first request, a 240 s composed bed on the non-streaming endpoint, failed with a proxy **502** after about a minute. I regenerated a 150 s bed on the **streaming** endpoint and arranged it across the film: it restarts the groove at chapter 04 and uses its resolve section for the claim and end card. All SFX are synthesized in `tools/mix.py` (ticks, blips, soft whooshes, chimes), so no ElevenLabs SFX credits were spent.
- **Mix.** Voice sits about 11 dB above music plus SFX during speech, with smooth ducking.

## Credits used

**ElevenLabs.** The account is shared, and the counter moved concurrently with other sessions, so these are per-request estimates:

| Item | Credits |
|---|---|
| Narration: 27 lines, 3,323 characters (George, `eleven_multilingual_v2`, series settings), including the 2 lines later cut | ≈ 3,323 |
| Failed 240 s music request (502). The counter rose 6,603 around it while other sessions were also generating. From the 150 s price below, a 240 s track costs about 3,300 | ≈ 3,300, possibly up to 6,600 |
| 150 s music bed (streamed), measured on its own | 2,062 |
| SFX | 0 |
| **Total** | **≈ 8,700** (worst case ≈ 12,000). Under the 15,000 budget |

All generations are cached in `audio/` (committed), so re-running spends nothing.

**Pexels:** 5 API calls, one per slot (budget 30). Clips, all under the Pexels licence:

| Slot | Photographer | URL |
|---|---|---|
| trading (order book screen) | Tima Miroshnichenko | https://www.pexels.com/video/financial-market-7579577/ |
| warehouse (logistics aerial) | Altaf Shah | https://www.pexels.com/video/aerial-view-of-industrial-estate-with-warehouses-35376603/ |
| lenders (meeting) | Yan Krukau | https://www.pexels.com/video/colleagues-discussing-about-the-reports-7691631/ |
| handshake | Yan Krukau | https://www.pexels.com/video/business-people-doing-a-handshake-7692917/ |
| city (end card) | Borys Trusevych | https://www.pexels.com/video/20670675/ |

Icons: Lucide (`lucide-static`, ISC licence). Fonts and logo come from `propchain-reel/assets/`.

## Claims for the business to double-check

**Taken exactly from the deck:**
- M-0417's filters, curves, weights and floors.
- The tenant-credit tiers.
- The 6.2%-last-week vs 6.4%-five-months example.
- L1/L2/L3 quotes and the 60-day attestation gate.
- The whole worked example (€800k, €13.0M, 6.15%, 55% · 1.30× · 7.5%, k 6.5%, €7.15M / €9.47M / €10.67M, €5.85M, €465k, €335k, 5.7%, 12% levered IRR, ~€17.2M DSCR kink).
- The four re-run events.
- The layer mapping.
- "Matching is a data outcome".

The deck itself marks the quotes, curves, schema and worked example as **illustrative**, and the film labels them that way on screen.

**Invented by me for illustration, not from the deck** (all labelled "illustrative" or "schematic" on screen):
- Asset names and cities, including the Munich asset at €13.0M, and the other assets' lot sizes and cap rates in the filter table.
- The WALT, credit and vacancy utility values behind the 0.68 score. The score arithmetic itself is correct for those inputs.
- The shape of the decay curve (c = 0.97 at one week, 0.60 at five months). The deck gives no values.
- The WALT figures in the tie-break (7.1y vs 5.4y) and the book scores.
- The seller-score bars for bids A and B.
- The three-by-three preference lists in the deferred-acceptance demo.
- The r(P) curve. It is drawn as a **schematic** with no price axis values; the deck does not give P\*.
- The mandate names in the chapter 01 two-column diagram, and "M-2" / "M-3".

**Wording to check:**
- "Lenders don't quote the asset, or the buyer" and "the sponsor is below its tier" follow slide 08.
- "A firm term sheet can beat a higher bid with no debt behind it" paraphrases slide 11 ("can rank below it").
- "Freshness replaces time priority" paraphrases slide 14 ("Decay replaces time priority").

## Build

```bash
npm install                        # playwright + lucide-static
pip install numpy scipy pillow imageio-ffmpeg
python3 tools/eleven.py vo         # cached; writes audio/vo_lines.json with word timings
python3 tools/timeline.py          # lays lines on the film clock -> timeline.json
python3 tools/pexels_search.py     # cached searches (stock/search)
python3 tools/fetch_stock.py       # CDN downloads -> stock/clips (gitignored)
node render.mjs stills 12 95.5     # review stills -> out/stills
node render.mjs frames --workers 4 --fps 30 --to 7199
python3 tools/mix.py               # -> out/mix.wav
tools/encode.sh                    # -> mandate-market-1080p.mp4, mandate-market-preview.mp4
```

The picture is DOM/SVG motion graphics (`index.html`, `src/*.js`). `window.__seek(t)` renders any frame deterministically; open `index.html?t=95` or `?play` from a local server for a live preview.
