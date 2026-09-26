# The Mandate Market — explainer storyboard

Source: `Propchain — The Mandate Market.pdf` (concept note, September 2026, 17 slides).
Target runtime ≈ 3:50. Narrator George, series visual system (charcoal, brand yellow `#FFBE06`, Inter + JetBrains Mono).
Times below are planned; final times are set by the generated narration (see README for the as-built beat list).

## What the viewer must understand after watching

1. **Why not an order book.** A CLOB needs identical instruments ranked on one axis (price) with price-time priority. Real estate has unique assets, value as a vector, and two sides that rank each other differently → a *two-sided ranked matching market*.
2. **The three objects.** Asset = attested vector with lineage (source, timestamp, confidence). Buy mandate = a standing scoring function that never names an asset. Credit box = a lender's standing terms that score the asset *given the buyer*. The seller is a fourth scorer.
3. **How a mandate scores an asset** (mandate M-0417): hard filters → utility curves (capped, plateau, stepped) → confidence decay → floors → weights → tie-break → a ranked book.
4. **Debt quotes the pair**, not the asset or buyer. L1 fires 55% LTV / 185 bps, L2 60% / 210 bps, L3 silent (sponsor below tier). No attested NOI, no quote.
5. **Score → bid** (worked example): NOI €800k, test price €13.0M → proceeds €7.15M (LTV) / €9.47M (DSCR) / €10.67M (debt yield) → LTV binds → equity €5.85M → solve the max price P* against a 12% levered IRR → bid = min(P*, ask). A more generous credit box raises the bid.
6. **Sellers rank bids** on certainty, speed, conditions — a firm term sheet can beat a higher unfinanced bid.
7. **Clearing is deferred acceptance**: mandates propose, assets hold tentatively, released mandates move down, stop when nobody moves → a stable set, no blocking pair.
8. **It is continuous** (four re-run events; freshness replaces time priority) and **visibility is per object** (open / one-way / double-blind).
9. **The claim:** the maths is known; the missing piece is the attested asset vector and a credit box that can trust it. *Matching is a data outcome.*

## Arc

Problem (order book doesn't fit) → the objects → one mandate scoring assets → the lender quoting the pair → turning score into a bid → the seller's side → clearing both books → a living, private market → the claim.
One hero example runs through the whole film: **mandate M-0417** (logistics, Germany, €10–25M) meeting a logistics asset, financed by credit box **L1**.

## Beat sheet

| # | ~Time | Chapter | Narration | Visual | On-screen text |
|---|---|---|---|---|---|
| 0 | 0:00 | Title | — (music) | Logo draws on, title lifts in over slow grid; three object glyphs (asset / mandate / credit box) orbit and link | THE MARKET LAYER · The Mandate Market · How capital, assets and credit find each other on attested data |
| 1 | 0:06 | 01 THE PROBLEM | "A stock exchange matches orders in an order book. That works because every share is identical, and price is the only question." | Stock: trading screens (2 s) → a clean CLOB ladder builds, identical tokens stack, one price axis, top bid meets top ask, yellow pulse = trade | ONE INSTRUMENT · ONE AXIS: PRICE · PRICE-TIME PRIORITY |
| 2 | 0:15 | | "Real estate breaks all of that. No two buildings are alike, value is a vector, and buyers and sellers rank each other, differently." | Tokens morph into unique building cards; each grows a radar/vector of five bars (yield, term, credit, location, capex); ladder dissolves | VALUE IS A VECTOR |
| 3 | 0:24 | | "So instead: a two-sided ranked matching market, where standing intents on both sides score each other." | Two columns (assets / mandates); scoring lines draw both ways with small rank numbers | TWO-SIDED RANKED MATCHING MARKET |
| 4 | 0:31 | 02 THE OBJECTS | "Three objects. The asset enters as an attested vector — income, cap rate, lease term, tenant credit — each value with its source, timestamp and confidence." | Stock: logistics warehouse (2 s) → Asset card: dimension rows fill in, each gets a lineage tag (source · attested · confidence) | 01 · ASSET — the instance object |
| 5 | 0:41 | | "The buy mandate never names an asset. It scores them." | Mandate card slides in: a funnel/scoring glyph, beams scanning across many asset cards | 02 · BUY MANDATE — a standing intent |
| 6 | 0:45 | | "The credit box scores the asset given who is buying it. And the seller ranks the bids." | Credit box card; link line from box to asset *through* mandate; seller badge on the asset | 03 · CREDIT BOX — conditional · SELLER = 4TH SCORER |
| 7 | 0:52 | 03 THE MANDATE | "Take mandate M-0417. Hard filters first: logistics, Germany, ten to twenty-five million euros, cap rate at least five point two five percent. Fail one, and the asset is out." | M-0417 spec panel; a stream of asset cards passes through four filter gates; failures drop out with the failing field logged in mono | M-0417 · LOGISTICS · GERMANY · €10–25M · CAP ≥ 5.25% |
| 8 | 1:03 | | "Every other dimension maps to a utility from zero to one. Cap rate climbs from five point two five to seven percent, then caps." | Big chart: x cap rate, y utility; curve draws; a marker slides along, reading value → utility | UTILITY 0 → 1 · LINEAR 5.25–7.0%, CAPPED |
| 9 | 1:11 | | "Lot size is a plateau. Tenant credit is stepped: investment grade one, BB point six, B point two." | Chart shrinks to 1/3, two siblings draw: plateau (€10–25M, €12M and €18M both = 1), steps IG/BB/B | PLATEAU · STEPPED 1.0 / 0.6 / 0.2 |
| 10 | 1:18 | | "Confidence decays with each attestation's age: a six point two percent cap rate attested last week outranks six point four from five months ago." | Two asset chips: 6.2% (1 wk) vs 6.4% (5 mo); decay curve c(t) drops; bars scale; order swaps | c(t) · FRESHEST ATTESTATION WINS |
| 11 | 1:27 | | "Weights combine it all — cap rate forty-five, lease term twenty-five, credit twenty, vacancy ten — but floors come first. Vacancy over five percent zeroes the score, whatever the yield." | Stacked weight bar 45/25/20/10 fills into a score; second asset with 7% yield but 20% vacancy trips the floor → score snaps to 0 | S(a,m) = Σ wᵢ · cᵢ(t) · uᵢ(aᵢ) · FLOOR → 0 |
| 12 | 1:37 | | "Near-ties go to longer lease term, then lower capex — never to who arrived first. Each mandate now holds a ranked book." | Near-tie pair reorders by WALT; list settles into a ranked book 1…6 | TIE-BREAK: LONGER WALT → LOWER CAPEX |
| 13 | 1:45 | 04 THE DEBT | "Lenders don't quote the asset or the buyer. They quote the pair." | Stock: office/lenders (2 s) → asset + mandate merge into the pair (a, m) | THE PAIR (a, m) · COLLATERAL × SPONSOR |
| 14 | 1:50 | | "Credit box L1 fires at fifty-five percent loan-to-value. L2 at sixty. L3 stays silent: sponsor below tier. And no attested NOI, no quote." | Three credit boxes to the right; L1, L2 light with quotes (55% · 185 bps, 60% · 210 bps), L3 greyed; an attestation gate closes on a stale NOI | ILLUSTRATIVE · NOI ATTESTED ≤ 60 DAYS |
| 15 | 2:01 | 05 SCORE → BID | "Price depends on debt, and debt on price. So test one: NOI of eight hundred thousand euros, price thirteen million." | Loop diagram price ⇄ debt, then the worked-example panel | NOI €800k · P €13.0M · CAP 6.15% |
| 16 | 2:08 | | "L1 lends the least of three tests: seven point one five million by loan-to-value, nine point four seven by debt cover, ten point six seven by debt yield. Loan-to-value binds." | Three horizontal bars grow (7.15 / 9.47 / 10.67); min wins in yellow | LTV 55% · DSCR 1.30× · DY 7.5% · k 6.5% |
| 17 | 2:19 | | "Equity: five point eight five million. The engine solves for the highest price that still meets the buyer's twelve percent return, and bids that — or the ask, if lower." | Price bar splits debt/equity; r(P) curve falls with P; 12% line; bisection ticks converge on P*; bid = min(P*, ask) | E €5.85M · 5.7% YR-1 CASH YIELD · 12% LEVERED IRR · BID = min(P*, ask) |
| 18 | 2:30 | | "A more generous credit box raises the bid directly." | Debt share grows, P* slides right | DEBT COMPETITION → EQUITY PRICE |
| 19 | 2:34 | 06 THE SELLER | "Sellers score bids beyond price: certainty, speed, conditions. A firm term sheet can beat a higher bid with no debt behind it." | Two bid cards; seller scorecard bars; the lower-headline bid with firm debt rises above | CERTAINTY · SPEED · CONDITIONALITY |
| 20 | 2:42 | 07 CLEARING | "Clearing is deferred acceptance. Each mandate proposes to the top asset in its book." | Bipartite board: 3 mandates left, 3 assets right; arrows fire to each mandate's #1 — two hit the same hot asset | DEFERRED ACCEPTANCE · 01 PROPOSE |
| 21 | 2:47 | | "Each asset tentatively holds the proposal its seller prefers, and releases the rest." | Asset holds one (dashed yellow), the other arrow bounces back | 02 HOLD, TENTATIVELY |
| 22 | 2:52 | | "Released mandates move down their books, re-quoting debt for the new pair." | Released mandate proposes to #2; debt tag re-quotes | 03 MOVE DOWN · RE-QUOTE |
| 23 | 2:57 | | "When nobody moves, the set is stable: no asset and mandate would both prefer each other to what they hold. No one gains by going around the platform." | Pairs lock solid; a would-be blocking pair line tries and fails; stock: handshake (2 s) | 04 STABLE · NO BLOCKING PAIR |
| 24 | 3:08 | 08 A LIVING BOOK | "And it never stops. New attestations, amended mandates, filled credit boxes and rate moves re-run the affected pairs. Stop attesting, and your asset sinks in every book." | Four event chips pulse into the engine; a stale asset slides down several ranked books at once | 4 EVENTS RE-RUN THE ENGINE · FRESHNESS > TIME PRIORITY |
| 25 | 3:19 | | "Visibility is per object — up to double-blind, where neither side sees the other until mutual scores clear a threshold." | Open / One-way / Double-blind tri-panel; in double-blind both books are dark until a pair lights | OPEN · ONE-WAY · DOUBLE-BLIND |
| 26 | 3:27 | 09 THE CLAIM | "The engine is known mathematics. What no one has had is an asset that arrives as an attested vector, and a credit box that can trust it." | Three layers stack (01 structuring, 02 validation, 03 matching); List → Diligence → Match → Finance → Settle pulse | LIST · DILIGENCE · MATCH · FINANCE · SETTLE |
| 27 | 3:37 | | "Matching is a data outcome." | Everything collapses to one line of type | Matching is a data outcome. |
| 28 | 3:41 | End card | — | Propchain logo, deck title, "Private and confidential · September 2026" | |

## Cut from the deck (deliberately)

Why-not-Euclidean-distance detail, the Pareto-frontier flag, the full credit-box field table, the capital-stack generalisation (slide 13), hold windows/hysteresis, proposer advantage and the four open questions of slide 17. They are real but secondary; the film keeps one clear path through the mechanism.

## Audio

Narration first (ElevenLabs `with-timestamps`, so visuals can cue on the exact words). Calm, flowing modern bed (pulsing soft synth arps, felt piano, light percussion from chapter 3), ducked ~10 dB under voice. Synthesised UI ticks for filters, bars and proposals; a few ElevenLabs SFX (soft whoosh, subtle chime).
