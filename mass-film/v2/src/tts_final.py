"""The one-shot final narration: ONE ElevenLabs request for the whole script (with character
timestamps), saved raw, then cut into per-line files for the edit. Never re-requests if the raw
take exists. Usage: python3 tts_final.py <voice_id> [--dry-run]"""
import base64
import json
import os
import subprocess
import sys

import numpy as np
import requests
import soundfile as sf

import script

os.environ.setdefault('REQUESTS_CA_BUNDLE', '/root/.ccr/ca-bundle.crt')
V2 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(V2, 'out', 'vo_final')
MODEL = 'eleven_multilingual_v2'
SETTINGS = dict(stability=0.45, similarity_boost=0.8, style=0.25, use_speaker_boost=True)


def take_text():
    """Lines joined with spaces inside a section and a paragraph break between sections."""
    parts, spans, pos, prev = [], [], 0, None
    for (sec, _), txt in script.keyed():
        sep = '' if prev is None else (' ' if sec == prev else '\n\n')
        pos += len(sep)
        parts.append(sep + txt)
        spans.append((pos, pos + len(txt)))
        pos += len(txt)
        prev = sec
    return ''.join(parts), spans


def request(voice_id, text):
    raw = os.path.join(OUT, 'take_raw.json')
    if os.path.exists(raw):
        print('raw take exists, not re-requesting')
        return json.load(open(raw))
    sub = requests.get('https://api.elevenlabs.io/v1/user/subscription', timeout=30).json()
    left = sub['character_limit'] - sub['character_count']
    print(f'{len(text)} characters to synthesise; {left} left this period')
    if len(text) > left:
        raise SystemExit('not enough characters left')
    r = requests.post(f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps',
                      params=dict(output_format='mp3_44100_128'),
                      json=dict(text=text, model_id=MODEL, voice_settings=SETTINGS), timeout=600)
    if r.status_code != 200:
        raise SystemExit(f'ElevenLabs error {r.status_code}: {r.text[:300]}')
    d = r.json()
    d['request'] = dict(voice_id=voice_id, model_id=MODEL, voice_settings=SETTINGS, text=text)
    os.makedirs(OUT, exist_ok=True)
    json.dump(d, open(raw, 'w'))
    open(os.path.join(OUT, 'take.mp3'), 'wb').write(base64.b64decode(d['audio_base64']))
    return d


def cut(d, text, spans):
    al = d.get('alignment') or d['normalized_alignment']
    chars, t0s, t1s = al['characters'], al['character_start_times_seconds'], al['character_end_times_seconds']
    assert ''.join(chars) == text, 'alignment text differs from the request'
    wav = os.path.join(OUT, 'take.wav')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', os.path.join(OUT, 'take.mp3'), '-ar', '48000', '-ac', '1',
                    wav], check=True)
    x, fs = sf.read(wav)
    lines = []
    bounds = [(t0s[a], t1s[b - 1]) for a, b in spans]
    for k, ((a, b), (s0, s1)) in enumerate(zip(spans, bounds)):
        lo = max(0.0, s0 - 0.05)
        hi = s1 + 0.12
        if k > 0:
            lo = max(lo, (bounds[k - 1][1] + s0) / 2)
        if k + 1 < len(bounds):
            hi = min(hi, (s1 + bounds[k + 1][0]) / 2)
        seg = x[int(lo * fs):int(hi * fs)].copy()
        m = int(0.01 * fs)
        seg[:m] *= np.linspace(0, 1, m)
        seg[-m:] *= np.linspace(1, 0, m)
        name = f'{k:02d}.wav'
        sf.write(os.path.join(OUT, name), seg, fs, subtype='PCM_24')
        words, i = [], a
        for w in text[a:b].split(' '):
            j = i + len(w)
            words.append((w, round(t0s[i] - lo, 3), round(t1s[j - 1] - lo, 3)))
            i = j + 1
        lines.append(dict(file=name, dur=round(len(seg) / fs, 3), words=words))
    json.dump(lines, open(os.path.join(OUT, 'lines.json'), 'w'), indent=1)
    print(f'cut {len(lines)} lines; take length {len(x) / fs:.1f}s')


if __name__ == '__main__':
    text, spans = take_text()
    if '--dry-run' in sys.argv or len(sys.argv) < 2:
        print(text)
        print(f'\n{len(text)} characters, {len(spans)} lines')
        raise SystemExit
    d = request(sys.argv[1], text)
    cut(d, text, spans)
