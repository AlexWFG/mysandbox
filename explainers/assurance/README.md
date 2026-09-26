# Making lies expensive — assurance explainer

Narrated motion-graphics explainer of **`Propchain — Assurance Fraud, Bonds and Insurance.pdf`**
(concept note, working draft, September 2026). Part of the four-film series in `explainers/BRIEF.md`.

| File | What |
|---|---|
| `assurance-1080p.mp4` | 1920×1080, 30 fps, two-pass H.264 ~2.7 Mbps (light `hqdn3d`), AAC 192k, loudness −16 LUFS |
| `assurance-preview.mp4` | 1280×720, two-pass ~0.76 Mbps, AAC 160k — see "Decisions" for why 720p |
| `STORYBOARD.md` | learning goals, arc and the planned beat sheet |

**Runtime: 3:58.9** (238.9 s).

## Beat list (as rendered)

Times are measured from the narration (`timeline.json`); picture is timed to the voice.

| Time | Chapter | What the viewer sees |
|---|---|---|
| 0:00 | Title | Logo, *Making lies expensive*, a seal draws on |
| 0:04 | 01 The problem | Stock: a lease being scanned and stamped "attested" → a signed rent roll whose tenants turn into dashed "phantoms": **provenance ✓, truth ?** → a consensus ring orders transactions but "cannot decide" whether a tenant exists → six fraud vectors; the first two (misstated income, diverted closing funds) light up and bracket to **cash** |
| 0:29 | 02 Six layers | The six-layer stack builds as each is named; "lies" rise and are caught at the layer that stops them; two get through into the **residual that insurance prices**; layers 3 and 4 tagged "new decision" |
| 0:45 | 03 Corroboration | Worked example: rent roll €1,020k, ledger €1,020k (follows seller → one source), bank receipts €958k, tenants €955k; cash outranks documents; 2 % band → **quorum €956k → level A3**; rent roll "loses standing" → the A0–A5 ladder, per field (NOI A3, capex A1); A4 needs **capital at risk** |
| 1:26 | 04 The bond | €13.0M · €800k NOI · 6.15 % cap rate; ±5 % warranty for 12 months (€40k); a 10 % miss = €80k ÷ 6.15 % = **€1.3M** (≈10 % of price) flows into a yield-bearing escrow; 12 months of bank receipts fill; **€760k → released in full + yield**; **€720k → 5 pts beyond, half the bond to the buyer** (pro rata, never all or nothing); dispute rule |
| 2:14 | 05 What can be slashed | Claim → later mechanical truth, read by a contract; three columns: objective (bondable) / adjudicated (bondable with a named referee) / subjective (never — struck through); staking lesson as footnote |
| 2:33 | 06 Who posts capital | Stock: meeting → holdback, retention, W&I premium merge into one bond ("net new capital usually small") → self-bond / surety / policy with flows → the surety book (quotes on the same record, fee [x] %, fees fall with level and record) → a balance: certainty premium vs cost, "measured, not assumed"; adverse-selection risk as footnote |
| 3:09 | 07 The insurer | Paths A data partner / B MGA / C own carrier with capital meters; route A → B; stock: tower → underwrite → snapshot → observe → curve → price, claimed-at-close vs realised line = the loss curve → products by tail length, parametric short tails first; order of value: loss curve → MGA margin → float, last |
| 3:42 | 08 The plan | Now / Next / Later → **Measure first. Bond what is measured. Insure the rest.** |
| 3:54 | End card | Propchain logo over the city at dusk |

## Hedges kept from the deck

Shown as on-screen footnotes (and spoken where noted): ordering of fraud vectors is qualitative;
numbers are a worked illustration (spoken at the end: "a working draft, and the numbers are illustrative");
level names are placeholders; sizes and terms are illustrative; the surety fee stays **[x] %** (a placeholder the
surety market will price); licence and capital regimes vary by domicile, to be confirmed with counsel; tail lengths
indicative, product design subject to regulatory review; adverse selection named as an open risk;
"measured, not assumed".

## Claims the business should double-check

- **€650k** (half the bond, both to the buyer and back to the seller in outcome 2) is my arithmetic on the deck's
  "half the bond" of €1.3M; the deck doesn't print the figure.
- Outcome-2 subline "5 pts beyond tolerance, bond sized for 10 · half the bond" is my explanation of *why* it is half
  (bond sized at a 10 % miss, forfeit pro rata to the shortfall beyond tolerance). Please confirm that is the intended rule.
- The warranty band is drawn as ±5 % around €800k (deck: "NOI within 5%").
- Narration line "Usually, it isn't new money" paraphrases the deck's "net new capital is usually small".
- Four surety rows (S1–S4) with fee bars, the fee-vs-level curve, the claimed-vs-realised line and the product
  tail-length bars are **schematic** — the deck gives no numbers for them. Sureties are labelled "Fee [x]%".
- The consensus diagram (ring of nodes that "cannot decide") and the "lies caught by layers" particles are
  visual metaphors for deck statements, not models of any system.
- "Released in full + yield" uses the deck's release rule (yield to the poster).

## Decisions made autonomously

- **Length vs content.** First narration was 4:24; I cut three lines (the "make lies expensive" restatement, the spoken
  staking lesson — kept as footnote — and a separate intro to the insurer paths), re-recorded six lines tighter,
  trimmed each clip's silence and tightened pauses to land at 3:59, inside the 1–4 min brief.
- **Preview at 720p.** The brief's "<29 MB, ~1.5 Mbps" can't both hold for a 3:59 film (1.5 Mbps ≈ 45 MB), so the
  preview is 1280×720 at ~0.76 Mbps to stay under 29 MB. The 1080p file is the quality master.
- The deck's analogues slide (escrow, W&I, surety, staking, oracles) and the float economics slide are compressed to a
  footnote and the "order of value" strip; the plan slide's "Decide:" items are not shown.
- Dispute rules (automatic inside the band; 30-day expert determination, cost to the loser) are on screen only.

## Credits and budgets

- **ElevenLabs** (≤ 15,000 budget): narration 4,060 characters (33 lines + 6 tighter re-records; George
  `JBFqnCBsd6RMkjVDRZzb`, `eleven_multilingual_v2`, series settings); music one 240 s bed via `/v1/music` with a
  six-section composition plan ≈ 3,300 credits (measured from the account's usage stats around the call);
  5 short SFX (whoosh, stamp, coins, tick, paper). **Total ≈ 7,700 credits.** The account is shared with the other
  three films running in parallel, so the account-wide counter can't isolate this film exactly; per-call log in
  `audio/spend.json`. All audio is cached in `audio/` so nothing is ever regenerated.
- **Pexels** (≤ 30 calls): **5 search calls** (`stock/api_calls.json`); downloads via CDN.
  - "Close-up video of a document" — RDNE Stock project — https://www.pexels.com/video/close-up-video-of-a-document-7841590/
  - "Colleagues having discussions" — Mikhail Nilov — https://www.pexels.com/video/colleagues-having-discussions-8847991/
  - "Blue sky" — Adnan Muhammad — https://www.pexels.com/video/blue-sky-20336481/
  - "View of the city at dusk" — Ricky Esquivel — https://www.pexels.com/video/view-of-the-city-at-dusk-1826904/
- Icons: Lucide (ISC), inlined in `icons.js`. Fonts and logo from `propchain-reel/assets/`.

## Build

```bash
cd explainers/assurance
npm install                                   # playwright + lucide-static
python3 tools/eleven.py vo                    # narration (cached)  -> audio/vo_durations.json
python3 tools/trim.py && python3 tools/timeline.py   # speech bounds + phrase segments -> timeline.json
python3 tools/eleven.py music && python3 tools/eleven.py sfx   # cached
python3 tools/pexels.py search && python3 tools/pexels.py fetch  # stock (search cached; frames not committed)
node render.mjs stills 12 55.5 …              # review stills -> out/stills ; tools/sheet.py makes contact sheets
node render.mjs frames --workers 3 --fps 30 --to 7168
python3 mix.py && ./encode.sh
```

- `engine.js` — deterministic engine: `__seek(t)`, eased show/draw/flow helpers, stock frame sequences, chapter HUD,
  grain. `at(line, word)` times a visual cue to the spoken word by mapping phrases onto speech segments measured from
  the waveform.
- `scenes1.js` (title → corroboration), `scenes2.js` (bond, slashing), `scenes3.js` (capital, insurer, plan, end).
- Live preview: serve the repo root and open `explainers/assurance/index.html?play` or `?t=120`.
