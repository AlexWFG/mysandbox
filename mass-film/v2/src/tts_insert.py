"""Voice new script lines in one request (neighbouring lines as context) and splice them into the
final take's lines.json in script order. Existing lines keep their files and timings."""
import base64
import json
import os
import subprocess

import numpy as np
import requests
import soundfile as sf

import script
import tts_final as TF

os.environ.setdefault('REQUESTS_CA_BUNDLE', '/root/.ccr/ca-bundle.crt')
OUT = TF.OUT
VOICE = 'NYC9WEgkq1u4jiqBseQ9'


def insert(new_idx, old_lines_path, raw_name):
    keyed = script.keyed()
    texts = [keyed[i][1] for i in new_idx]
    secs = [keyed[i][0][0] for i in new_idx]
    parts, spans, pos = [], [], 0
    for k, (sec, txt) in enumerate(zip(secs, texts)):
        sep = '' if k == 0 else (' ' if sec == secs[k - 1] else '\n\n')
        pos += len(sep)
        parts.append(sep + txt)
        spans.append((pos, pos + len(txt)))
        pos += len(txt)
    text = ''.join(parts)
    raw = os.path.join(OUT, raw_name)
    if not os.path.exists(raw):
        prev_t = ' '.join(keyed[i][1] for i in range(max(0, new_idx[0] - 3), new_idx[0]))
        next_t = keyed[new_idx[-1] + 1][1] if new_idx[-1] + 1 < len(keyed) else None
        body = dict(text=text, model_id=TF.MODEL, voice_settings=TF.SETTINGS, previous_text=prev_t)
        if next_t:
            body['next_text'] = next_t
        r = requests.post(f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps',
                          params=dict(output_format='mp3_44100_192'), json=body, timeout=300)
        if r.status_code != 200:
            raise SystemExit(f'error {r.status_code}: {r.text[:300]}')
        json.dump(r.json(), open(raw, 'w'))
        print(f'requested {len(text)} characters')
    d = json.load(open(raw))
    mp3 = raw.replace('.json', '.mp3')
    open(mp3, 'wb').write(base64.b64decode(d['audio_base64']))
    wav = raw.replace('.json', '.wav')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', mp3, '-ar', '48000', '-ac', '1', wav], check=True)
    x, fs = sf.read(wav)
    al = d['alignment']
    chars, t0s, t1s = al['characters'], al['character_start_times_seconds'], al['character_end_times_seconds']
    assert ''.join(chars) == text, 'alignment text differs'
    old = json.load(open(old_lines_path))
    # loudness reference: the take's own lines around the insertion point
    def speech_rms(v):
        e = np.abs(v)
        return np.sqrt(np.mean(v[e > e.max() * 0.05] ** 2))
    refs = [sf.read(os.path.join(OUT, old[i]['file']))[0] for i in (new_idx[0] - 1, min(len(old) - 1, new_idx[0] + 1))]
    ref = np.mean([speech_rms(r_.mean(1) if r_.ndim > 1 else r_) for r_ in refs])
    bounds = [(t0s[a], t1s[b - 1]) for a, b in spans]
    new_lines = []
    for k, ((a, b), (s0, s1)) in enumerate(zip(spans, bounds)):
        lo = max(0.0, s0 - 0.05)
        hi, tail = s1 + 0.12, s1 + 0.35
        if k > 0:
            lo = max(lo, (bounds[k - 1][1] + s0) / 2)
        if k + 1 < len(bounds):
            mid = (s1 + bounds[k + 1][0]) / 2
            hi, tail = min(hi, mid), min(tail, mid)
        hi, tail = min(hi, len(x) / fs), min(tail, len(x) / fs)
        seg = x[int(lo * fs):int(tail * fs)].copy()
        seg *= ref / speech_rms(seg)
        m1, m2 = int(0.01 * fs), int(0.08 * fs)
        seg[:m1] *= np.linspace(0, 1, m1)
        seg[-m2:] *= np.linspace(1, 0, m2)
        name = f'ins_{new_idx[k]:02d}.wav'
        sf.write(os.path.join(OUT, name), seg, fs, subtype='PCM_24')
        words, i = [], a
        for w in text[a:b].split(' '):
            j = i + len(w)
            words.append((w, round(t0s[i] - lo, 3), round(t1s[j - 1] - lo, 3)))
            i = j + 1
        new_lines.append(dict(file=name, dur=round(hi - lo, 3), words=words, inserted=True))
        print(f'line {new_idx[k]}: {hi - lo:.2f}s  "{text[a:b]}"')
    return new_lines


if __name__ == '__main__':
    before = os.path.join(OUT, 'lines_before_layers.json')   # the take's lines before this insert
    old = json.load(open(before))
    new = insert([22, 23, 24], before, 'insert_layers_trade.json')
    lines = old[:22] + new + old[23:]          # old[22] was "And it all runs on the nation's own infrastructure..."
    assert len(lines) == len(script.keyed()), (len(lines), len(script.keyed()))
    json.dump(lines, open(os.path.join(OUT, 'lines.json'), 'w'), indent=1)
    print('lines.json:', len(lines), 'lines')
