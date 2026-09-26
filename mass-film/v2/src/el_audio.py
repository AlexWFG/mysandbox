"""ElevenLabs score and sound effects, derived from the final edit timeline.
  python3 el_audio.py plan     -> print the composition plan (no request)
  python3 el_audio.py score    -> ONE music request (sections timed to the edit), saved to out/el_audio
  python3 el_audio.py sfx      -> the foley list, one request each, skips files that exist"""
import json
import os
import sys

import requests

os.environ.setdefault('REQUESTS_CA_BUNDLE', '/root/.ccr/ca-bundle.crt')
os.environ.setdefault('MASS_VO', 'final')
import shots2 as S  # noqa: E402

V2 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(V2, 'out', 'el_audio')
API = 'https://api.elevenlabs.io/v1'
L = S.L

GLOBAL_POS = ['cinematic documentary score', 'instrumental', 'modern hybrid orchestral with subtle electronics',
              'emotional, visionary, premium brand film', 'clean mix, wide stereo', 'no vocals']
GLOBAL_NEG = ['vocals', 'singing', 'lyrics', 'choir words', 'rap', 'EDM drop', 'dubstep', 'comedy', 'lo-fi', 'jazz',
              'guitar solo', 'cheesy corporate ukulele', 'whistling']


def sections():
    """(name, start, positive styles, negative styles) keyed to the narration timeline."""
    p0 = L('peak', 0)
    t_turn = p0.end + 0.05                                  # the peak cuts to near silence here
    t_logo = L('reveal', 0).word('Mass') - 0.06
    return [
        ('Cold open', 0.0, ['dark ticking pulse', 'low drone', 'sparse muted piano', 'tension slowly rising',
                            'bureaucratic, mechanical rhythm'], ['melody', 'drums']),
        ('Aisha at night', L('aisha', 0).start - 0.05, ['intimate night atmosphere', 'soft felt piano motif in A minor',
                                                        'muted string ostinato', 'quiet determination', 'restless'],
         ['big drums', 'major key']),
        ('The licensing office', L('omar', 0).start - 0.2, ['same motif, more insistent', 'pulsing staccato strings',
                                                            'clockwork tension', 'frustration building'], ['big drums']),
        ('The ministry', L('ministry', 0).start - 0.2, ['dense layered pulses', 'many overlapping rhythms',
                                                        'rising pressure', 'dissonant but controlled'], ['release']),
        ('Peak', p0.start - 0.1, ['full crescendo of strings and low brass', 'accelerating', 'maximum tension',
                                  'ends abruptly in silence on the last beat'], ['resolution', 'fade out']),
        ('The turn', t_turn, ['begins in silence for two seconds', 'then a single warm piano note',
                              'hopeful swell in A major', 'airy pads', 'gentle rising strings'], ['drums', 'tension']),
        ('Logo breath', min(t_logo - 0.4, L('demo', 0).start - 0.3 - 3.05), ['very sparse', 'soft sustained low A major chord', 'leave space for a sound logo',
                                       'reverent pause'], ['drums', 'melody', 'hits']),
        ('The demo', L('demo', 0).start - 0.3, ['optimistic and driving', 'about 100 bpm', 'confident modern pulse',
                                                'piano arpeggios over warm strings', 'light electronic percussion',
                                                'momentum, progress, things working'], ['heavy drums', 'aggressive']),
        ('Trust', L('trust', 0).start - 0.2, ['solid and assured', 'broader strings', 'steady pulse', 'sovereign, dignified'],
         ['playful']),
        ('Across borders', L('network', 0).start - 0.1, ['expansive and epic', 'wide cinematic strings and horns',
                                                         'building layer by layer', 'global, uplifting'], ['sad']),
        ('Climax', L('close', 0).start - 0.1, ['full orchestral climax', 'powerful rising build', 'big and triumphant'],
         ['quiet']),
        ('Resolution', L('close', 1).word('Mass') - 0.05, ['resolved final chord in A major', 'long shimmering decay',
                                                          'calm confidence', 'fades to silence'], ['drums', 'new melody']),
    ]


def plan():
    secs = sections()
    out, total = [], 0
    for k, (name, t0, pos, neg) in enumerate(secs):
        t1 = secs[k + 1][1] if k + 1 < len(secs) else S.DUR
        ms = int(round((t1 - t0) * 1000))
        total += ms
        out.append(dict(section_name=name, positive_local_styles=pos, negative_local_styles=neg, duration_ms=ms, lines=[]))
    assert all(3000 <= s_['duration_ms'] <= 120000 for s_ in out), [s_['duration_ms'] for s_ in out]
    return dict(positive_global_styles=GLOBAL_POS, negative_global_styles=GLOBAL_NEG, sections=out), total


DIRECTIONS = {'Peak': 'stops abruptly, dead silence after the last hit', 'The turn': 'silence for two seconds, then one warm piano note',
              'Logo breath': 'almost silent, one sustained low chord', 'Resolution': 'long decay to silence'}


def plan_chunks():
    """Composition plan for music_v2 / v2.5: chunks with section names, inline directions and styles."""
    cp, total = plan()
    chunks = []
    for k, s_ in enumerate(cp['sections']):
        name = s_['section_name']
        text = f'[Instrumental: {name}]' + (f"\n{{{DIRECTIONS[name]}}}" if name in DIRECTIONS else '')
        pos = (GLOBAL_POS + s_['positive_local_styles']) if k == 0 else (s_['positive_local_styles'] + ['instrumental',
                                                                                                   'great production quality'])
        chunks.append(dict(text=text, duration_ms=s_['duration_ms'], positive_styles=pos,
                           negative_styles=GLOBAL_NEG + s_['negative_local_styles']))
    return dict(chunks=chunks), total


def credits():
    s = requests.get(f'{API}/user/subscription', timeout=30).json()
    return s['character_count']


def score(model='music_v2_5'):
    dest = os.path.join(OUT, 'score.mp3')
    if os.path.exists(dest):
        print('score exists, not re-requesting')
        return
    cp, total = plan_chunks() if model in ('music_v2', 'music_v2_5') else plan()
    c0 = credits()
    r = requests.post(f'{API}/music', params=dict(output_format='mp3_44100_192'),
                      json=dict(composition_plan=cp, model_id=model), timeout=900)
    if r.status_code != 200:
        raise SystemExit(f'music error {r.status_code}: {r.text[:400]}')
    open(dest, 'wb').write(r.content)
    meta = dict(model=model, plan=cp, total_ms=total, headers={k: v for k, v in r.headers.items() if 'song' in k.lower()
                                                                or 'request' in k.lower()}, credits=credits() - c0)
    json.dump(meta, open(os.path.join(OUT, 'score.json'), 'w'), indent=1)
    print(f"score: {len(r.content) / 1e6:.1f} MB, {total / 1000:.1f}s planned, {meta['credits']} credits")


SFX = {  # name: (prompt, duration s, loop)
    'stamp_1': ('Heavy rubber stamp slammed hard onto paper on a wooden desk, close-up, crisp thud', 1.2, False),
    'stamp_2': ('Official rubber ink stamp pressed firmly on a document on a desk, single hit, dry room', 1.0, False),
    'stamp_3': ('Rubber stamp hitting a stack of paper forms, office, single decisive stamp', 1.0, False),
    'pen': ('Fountain pen signing a signature on thick paper, close-up scratching, quiet room', 2.5, False),
    'welding': ('Industrial arc welding with crackling sparks in a factory, close', 3.0, False),
    'port': ('Container port at dusk, distant ship horn, cranes and metal clanks, wind, far away', 6.0, False),
    'city_night': ('Big city at night seen from a high window, very distant traffic hum, calm, quiet wind', 12.0, True),
    'typing': ('Fast typing on a laptop keyboard at night in a quiet room', 6.0, True),
    'airport': ('Airport immigration hall ambience, crowd murmur, footsteps, a soft PA chime', 8.0, True),
    'office': ('Modern open office ambience, air conditioning hum, soft distant chatter, keyboards', 10.0, True),
    'control_room': ('Operations control room ambience, electronic hum, computer fans, soft beeps', 10.0, True),
    'seal': ('Satisfying official approval stamp on paper followed by a soft bright chime', 1.5, False),
}


def sfx():
    c0 = credits()
    for name, (prompt, dur, loop) in SFX.items():
        dest = os.path.join(OUT, f'sfx_{name}.mp3')
        if os.path.exists(dest):
            continue
        r = requests.post(f'{API}/sound-generation', params=dict(output_format='mp3_44100_192'),
                          json=dict(text=prompt, duration_seconds=dur, loop=loop, prompt_influence=0.5), timeout=300)
        if r.status_code != 200:
            print(f'{name}: error {r.status_code}: {r.text[:200]}')
            continue
        open(dest, 'wb').write(r.content)
        print(f'{name}: {len(r.content) / 1e3:.0f} kB', flush=True)
    print(f'sfx credits: {credits() - c0}')


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'plan'
    if cmd == 'plan':
        cp, total = plan()
        for s_ in cp['sections']:
            print(f"{s_['duration_ms'] / 1000:6.2f}s  {s_['section_name']}")
        print(f'total {total / 1000:.2f}s (film {S.DUR:.2f}s)')
    elif cmd == 'score':
        score()
    elif cmd == 'sfx':
        sfx()
