# Provable, not visible · the architecture explainer

A narrated motion-graphics explainer made from `Propchain — Technical Architecture.pdf` (concept note, working draft, September 2026). It is film four of the explainer series (see `../BRIEF.md`).

| File | Spec |
|---|---|
| `architecture-1080p.mp4` | 1920×1080, 30 fps, H.264 two-pass, AAC 160k stereo |
| `architecture-preview.mp4` | 1280×720, 30 fps, two-pass ~0.8 Mbps, AAC 128k, under 29 MB |

**Runtime: 4:00.** That is the top of the brief's 1–4 minute range. The deck covers 15 dense slides, and the four things the film must land are the system diagram, one record's journey, the integration path and the custody model. Each needs its own time. To stay inside four minutes, the first narration draft (4:36) was cut by two lines and six lines were tightened.

## Who it is for, and what they should come away with

It is written for a smart non-engineer, such as an investor or partner. By the end they should understand these points:

1. The chain is a **notary and a settlement rail, not a database**. Only commitments, identities, grants, signatures, settlement state and the audit root go on chain. Records, mandates, the matching engine, models and documents stay off, and keys stay in HSMs.
2. **Eight services sit around one ledger.** They write commitments to it and read grants from it, and none of them stores state there.
3. **One rent roll's journey** runs: source system → adapter → ingestion (canonical schema and lineage) → per-field encryption in the tenant's vault → salted hash per field → Merkle root per asset per period → attestation (independent sources sign, quorum, level). Only the root, the signatures and the level reach the ledger. The rent roll never does.
4. **Consensus orders, attestation verifies.** Consensus runs on named, permissioned validators, anchored to a public chain.
5. **Disclosure** happens in two ways: a logged grant of value plus salt, checked against the on-chain root, or a range proof ("NOI ≥ X") with no disclosure at all.
6. **Every action traces to a person** (institution → principal → agent credential → action), and binding acts need the principal's signature. **Matching** runs deterministically in an attested enclave, with roots in and a root out.
7. **The deal end to end** runs List → Diligence → Match → Finance → Settle, and each step leaves a verifiable but unreadable mark on chain. Operate repeats monthly.
8. **Integration** never displaces anything: Shadow → Write back → Workflow. Each adapter is one untrusted source and cannot reach a quorum alone. A bank gets three connectors.
9. **Safety:** data and value are separated. One compromised key does nothing, two do only a little, and a third reverses. The film ends on the build sequence: commit, connect, match, settle.

## Beat list (final timings)

| Time | Chapter | Beat |
|---|---|---|
| 0:00 | Title | Logo, "Provable, not visible". A Merkle tree rolls up into one yellow root |
| 0:06 | 01 The first decision | Notary ✓ · Settlement rail ✓ · Database ✕ |
| 0:13 | | ON CHAIN column builds with six items, each timed to the narration |
| 0:24 | | OFF CHAIN column builds with six items. Keys lock to "HSM only" |
| 0:36 | 02 The components | The ledger rail draws, and eight services pop in as they are named |
| 0:47 | | Yellow pulses carry commitments down and white pulses carry grants up. "No state stored on the ledger". Layer tags follow the deck's mapping |
| 0:55 | 03 One record's journey | Stock: tower. "Follow one record." |
| 0:58 | | Camera follows the rent roll: property system → adapter → ingestion card, with lineage threads back to the source |
| 1:06 | | Vault · tenant A, with a key per field |
| 1:12 | | "+ salt" → hashes scramble in. The guessing attack: an unsalted `NOI = 800,000` leaks, a salted one is unguessable |
| 1:21 | | Hashes roll up into the Merkle root, per asset and per period |
| 1:27 | | Three independent sources sign, the quorum ring fills, level badge |
| 1:34 | | Pull out: root, signatures and level drop onto the ledger. "✕ the rent roll · never on chain" |
| 1:42 | 04 Two quorums | Split screen. Validators vote blocks into order, and sources sign a commitment. The deck's comparison rows |
| 1:54 | | Permissioned network: notaries, auditors, depositaries, banks. Periodic roots anchor to a public chain |
| 2:04 | 05 Disclosure | Grant token → buyer's agent. It recomputes the hash, which matches the on-chain root. Grant log row |
| 2:14 | | ZK range proof → credit box "NOI ≥ X ✓". NOI stays locked |
| 2:22 | 06 People, agents and the deal | Stock: signing. "Every action traces to a person." |
| 2:25 | | Institution → Principal → Agent credential → Action. The binding act needs two signatures (Proof of Agency) |
| 2:35 | | Attested enclave: three input roots in, stable-set root out. Attested build. "Neutrality: a property of the machine" |
| 2:43 | | List · Diligence · Match · Finance · Settle · Operate ↻ monthly, each with its on-chain mark. The regulator verifies, without seeing rent, mandate or price |
| 2:57 | 07 Integration | Stock: office team. "Zero change to their workflow." |
| 3:01 | | Their system of record stays unchanged. Shadow (attested copy) → Write back → Workflow |
| 3:11 | | Seven source classes → adapters → event bus → canonical schema → quorum. The compromised adapter fills 1/3 |
| 3:19 | | A loan today (Apply, Underwrite, Service) and three connectors: Pack in, Credit box out, Servicing feed |
| 3:29 | 08 Keeping value safe | Data vs value: different keys, networks and teams |
| 3:41 | | One key: nothing. Two: only a little. Three: reversed. "Agents hold no value keys. Ever." |
| 3:51 | 09 The build sequence | Commit first · Connect second · Match third · Settle last, with Now / Next / Later |
| 3:56 | End card | Propchain logo · "Provable, not visible." |

## How it's made

- `film/`: a DOM/SVG compositor. `engine.js` holds the deterministic, time-driven helpers: appear with slide and blur-in, stroke draw-on, travelling yellow pulses, camera, hash scramble, stock frame sequences, grain, vignette and chapter markers. `scenes1–3.js` hold the scenes. Every beat is keyed to the narration: `Wd(line, word)` estimates when a word is spoken, in proportion to its character position within the generated line. The picture is timed to the voice, not the other way round.
- `audio/`: `narration.json` (George, `eleven_multilingual_v2`, series settings), `music.json` (one 4:00 composition plan with six sections matching the chapters), `timeline.json`, and the **committed ElevenLabs cache** (`vo/`, `music/`). All sound effects (ticks, whooshes, chimes, thumps) are synthesized in `tools/mix.py`, so no SFX credits were spent.
- `tools/`: `eleven.py` (cached ElevenLabs calls; a `pin` field keeps untouched lines on their cached takes when neighbours change), `layout.py` (places narration lines and writes `film/timeline.js`), `mix.py`, `pexels_search.py`, `fetch_stock.py` and `sheet.py`.
- `build.sh` runs everything end to end. Frames, stock downloads and the WAV are gitignored.

Rebuild with `npm i && ./build.sh`. Previews: `node render.mjs stills --page film/index.html 72 90 130`.

## Budgets

- **ElevenLabs.** Narration was 28 lines (3,471 characters) plus a re-take of 6 lines (978 characters) after trimming to four minutes. The account bills this voice at about 0.53 credits per character (from `/v1/history`). The first narration pass moved the shared counter by exactly 2,379 credits, and the whole narration comes to **about 2,900 credits**. The music bed was one call, and the shared counter moved 43 credits across it. Other sessions were spending on the same account in parallel, so per-film totals can only be estimated from these figures. The estimate is **well under the 15,000 budget**. Nothing needs regenerating: every take is cached in `audio/`.
- **Pexels: 3 API calls** out of 30, one search per slot. Clips were downloaded from the CDN.

### Stock credits (Pexels)

| Use | Clip | Photographer |
|---|---|---|
| "Follow one record" | https://www.pexels.com/video/glass-panel-windows-on-the-building-exterior-7317045/ | MART PRODUCTION |
| "Every action traces to a person" | https://www.pexels.com/video/man-writing-in-paper-8731199/ | Mikhail Nilov |
| "Zero change to their workflow" | https://www.pexels.com/video/people-working-together-7653214/ | Thirdman |

## Decisions and things the business should double-check

- **Illustrative values** (not from the deck; please check these read as illustrative):
  - The hash strings (`9f3a·c21e…`), block numbers (`#1041…`), the enclave build id (`7c1e·a94d`) and on-chain mark ids are decorative.
  - "Tenant A" and "Source 1/2/3" are generic labels.
  - **"Level A2"** on the attested record is borrowed from the deck's scope example ("level A2 or above"). The deck never says a rent roll attests at A2.
  - `NOI = 800,000` is the deck's own example.
- **Three sources in the quorum** is illustrative. The deck says "independent sources of the fact" and gives no number.
- **"Different keys / networks / teams"**: the per-row labels "data network / settlement network" and "data team / custody team" are my shorthand for the deck's "different keys, different networks and different teams".
- **Key-stance cards.** The small rule lists under "nothing / a little / reversed" group the deck's nine custody rules by which part of the stance they serve. That grouping is my interpretation. The stance itself is quoted from slide 14.
- **Omitted for time:**
  - the seven-threat table (slide 13);
  - the settlement-asset ladder (slide 15: tokenised deposits → regulated stablecoin → own issuance, "if ever"), which appears only as "Own settlement asset, if ever" in the build sequence;
  - erasure and residency rules for the record store;
  - the "decide" items on slide 16;
  - the layer mapping, which appears only as small layer tags on the component nodes.
- **Hedges kept:**
  - the end card says "working draft";
  - the deck's enclave caveat ("enclaves have had hardware flaws") is not narrated, but the film never claims the enclave is sufficient on its own;
  - the bank example is described generically, as in the deck ("individual banks differ").
- The **"Proof of Agency"** label and the "EU AI Act" point: only Proof of Agency is shown, as a caption. The film makes no regulatory claims.
