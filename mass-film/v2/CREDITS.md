# Credits: v2 launch film

## Stock footage (Pexels)
All motion footage is from [Pexels](https://www.pexels.com) under the
[Pexels License](https://www.pexels.com/license/): free for commercial use, no attribution required.
The creators are credited here anyway. Clips are fetched with `src/fetch_footage.py`, which
reads `footage/manifest.json`, and are not stored in the repository.

| Plate(s) | Clip | Creator |
|---|---|---|
| handshake | [close-up-video-of-people-shaking-hands-8069057](https://www.pexels.com/video/close-up-video-of-people-shaking-hands-8069057/) | RDNE Stock project |
| welder | [industrial-welding-at-night-with-sparks-32243438](https://www.pexels.com/video/industrial-welding-at-night-with-sparks-32243438/) | Usman AbdulrasheedGambo |
| cranes | [view-of-a-trade-port-at-sunset-13378859](https://www.pexels.com/video/view-of-a-trade-port-at-sunset-13378859/) | Engin Akyurt |
| pen_sign | [person-signing-a-document-7578633](https://www.pexels.com/video/person-signing-a-document-7578633/) | Tima Miroshnichenko |
| karachi_night | [dark-city-at-night-seen-from-above-11016391](https://www.pexels.com/video/dark-city-at-night-seen-from-above-11016391/) | Altaf Shah |
| aisha_night | [adult-woman-working-from-home-7983117](https://www.pexels.com/video/adult-woman-working-from-home-7983117/) | Ron Lach |
| forms | [woman-typing-a-document-on-computer-7983125](https://www.pexels.com/video/woman-typing-a-document-on-computer-7983125/) | Ron Lach |
| aisha_tired | [woman-taking-a-break-from-work-7983322](https://www.pexels.com/video/woman-taking-a-break-from-work-7983322/) | Ron Lach |
| passport_control | [changi-airport-immigration-area-overview-36679174](https://www.pexels.com/video/changi-airport-immigration-area-overview-36679174/) | LayG Traveller |
| abudhabi_morning | [clear-sky-over-skyscrapers-and-harbor-11336420](https://www.pexels.com/video/clear-sky-over-skyscrapers-and-harbor-11336420/) | Glenn Langhorst |
| omar_desk, omar_day | [woman-wearing-hijab-working-at-the-office-10341378](https://www.pexels.com/video/woman-wearing-hijab-working-at-the-office-10341378/) | Ron Lach |
| officers_papers | [muslim-women-standing-and-reading-papers-10347444](https://www.pexels.com/video/muslim-women-standing-and-reading-papers-10347444/) | Ron Lach |
| ministry_building | [city-at-night-11336050](https://www.pexels.com/video/city-at-night-11336050/) | Glenn Langhorst |
| ministry_room | [high-tech-control-room-with-multiple-cctv-monitors-38779095](https://www.pexels.com/video/high-tech-control-room-with-multiple-cctv-monitors-38779095/) | Kiwi and Camera |
| abudhabi_sunset | [sunlight-over-city-on-sea-shore-11258028](https://www.pexels.com/video/sunlight-over-city-on-sea-shore-11258028/) | Atif Dar |
| aisha_day | [a-woman-wearing-a-robe-using-a-laptop-on-a-table-8503286](https://www.pexels.com/video/a-woman-wearing-a-robe-using-a-laptop-on-a-table-8503286/) | Ivan S |
| aisha_coffee | [woman-drinking-coffee-at-home-8503285](https://www.pexels.com/video/woman-drinking-coffee-at-home-8503285/) | Ivan S |
| ministry_office | [high-tech-control-room-in-action-38779108](https://www.pexels.com/video/high-tech-control-room-in-action-38779108/) | Kiwi and Camera |
| flag | [the-flag-of-the-united-arab-emirates-flies-in-the-wind-15546303](https://www.pexels.com/video/the-flag-of-the-united-arab-emirates-flies-in-the-wind-15546303/) | Markus Winkler |
| card_tap | [person-paying-with-credit-card-8421360](https://www.pexels.com/video/person-paying-with-credit-card-8421360/) | Kampus Production |
| ship | [cargo-container-ships-in-port-3840442](https://www.pexels.com/video/cargo-container-ships-in-port-3840442/) | Tom Fisk |
| port_dusk | [aerial-view-of-busy-shipping-port-at-dusk-35907902](https://www.pexels.com/video/aerial-view-of-busy-shipping-port-at-dusk-35907902/) | willy one |

## Other sources
- Earth textures (network sequence): NASA Visible Earth / Earth Observatory, public domain (shared with v1).
- UAE outline (ministry dashboard): Natural Earth 1:50m, public domain.
- Fonts: Inter, JetBrains Mono and Courier Prime, all under the SIL Open Font License.
- Statistic in the trade-finance scene (41% of SME trade-finance requests rejected): Asian Development Bank
  trade finance survey, the figure cited in the Mass deck. Confirm the edition and wording before public release.
- Narration: ElevenLabs text-to-speech (Creator plan), voice "Russell" from the ElevenLabs voice library,
  model `eleven_multilingual_v2`, one take (`out/vo_final/`), plus one retake for pronunciation (`src/tts_fix.py`)
  and one request for the three layers and trade-finance lines, voiced with their neighbours as context
  (`src/tts_insert.py`). Scratch narration for the animatic: Piper TTS (`en_GB-alan-medium`).
- Score, version A: composed by Eleven Music (`music_v2_5`) from a composition plan timed to the edit
  (`src/el_audio.py`, `out/el_audio/score.mp3`). The layers and trade-finance section uses a bridge from a
  second Eleven Music generation in the same key and tempo (`out/el_audio/score_v2.mp3`), spliced into the
  original at the picture cuts (`el_audio.py bridge`). Recorded-style effects (stamps, pen, welding, port, city,
  typing, airport, office, control room, seal) from ElevenLabs sound effects (`out/el_audio/sfx_*.mp3`).
- Score, version B, UI sounds, the sonic logo and the closing hits: synthesised from scratch in `src/audio2.py`.
