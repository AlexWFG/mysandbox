# MASS: 2-minute launch film (v2)

A story-driven launch film built on real stock footage, with a procedural UI and globe
and a synthesised score. The narration drives the whole edit: every cut, UI beat and sound
cue is keyed to a line or a word in `src/script.py`. Replacing the scratch voice with the final
ElevenLabs take re-times picture and sound automatically.

## Story
| Act | Beat | Narration |
|---|---|---|
| I | Cold open: deals, work, trade, then every form stamped *pending / returned / resubmit* | "Every deal. Every job. Every shipment…" |
| I | **Aisha**, founder, Karachi at 02:14: a week to build, months to make official, back to zero at the next border | "Karachi. Two a.m…" |
| I | **Nadia**, licensing officer, Abu Dhabi free zone: retypes one record into three systems that never connect | "In Abu Dhabi, Nadia…" |
| I | **The ministry**: a wall of screens that never agree | "At the ministry, the economy arrives in pieces…" |
| I | Peak: three people, one economy, held back. Then silence | "Three people. One economy…" |
| II | The turn: one living record, created in minutes, trusted everywhere | "What if a company only had to prove itself once?" |
| II | Reveal: the sonic logo lands on "Mass" | "This is Mass." |
| II | Three-way demo on one moving canvas: Aisha talks to her agent, Nadia decides, the ministry sees it live, and a rule change reaches everyone | "Aisha tells her agent what she's building…" |
| III | Trust: every action checked before it happens, on the nation's own infrastructure and keys | "Every action is checked…" |
| III | Network: another nation recognises the record | "Now imagine this across borders…" |
| III | Close: Formed · Licensed · Banked · Recognised, then the end card | "Mass. The operating system for sovereign economies." |

## Pipeline (`src/`)
| Step | Command |
|---|---|
| Search Pexels and build contact sheets | `python3 pexels_search.py` then `python3 pexels_preview.py` |
| Fetch the chosen clips and write the manifest | `python3 fetch_footage.py` (API key comes from the environment) |
| Scratch narration (offline) | `python3 scratch_vo.py` |
| Review sheets | `python3 render2.py --sheet 12.5,30,68,90 --sheet-out ../out/review/x.jpg` |
| Picture (lossless, parallel) | `python3 render2.py --video ../out/mass_v2_picture_lossless.mkv --workers 4` |
| Final narration (one ElevenLabs request, cut into lines) | `python3 tts_final.py <voice_id>` |
| ElevenLabs score and effects timed to the edit | `python3 el_audio.py score` / `python3 el_audio.py sfx` |
| Score, sound design and narration mix | `python3 audio2.py` (−15 LUFS, −1 dBTP); `MASS_SCORE=el` uses the ElevenLabs score |
| Delivery encodes | `finish2.py`: the video is encoded once, then each soundtrack is muxed onto it |
| Captions | `python3 captions.py` |

Set `MASS_VO=final` to build everything from the ElevenLabs take in `out/vo_final/`
(`lines.json` holds per-line durations and word timings).

Shared engine code (grading, type, Mass mark, globe) lives in `../src/` from v1.
