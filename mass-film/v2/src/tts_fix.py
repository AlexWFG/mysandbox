"""Retake single narration lines (pronunciation fixes) without disturbing the rest of the edit.
A respelled text goes to ElevenLabs with the neighbouring lines as context; several candidates are
scored acoustically; the winner replaces the line and the pause after it absorbs any length change."""
import base64
import json
import os
import subprocess
import sys

import numpy as np
import requests
import soundfile as sf
from scipy import signal
from scipy.linalg import solve_toeplitz

import script
import tts_final as TF

os.environ.setdefault('REQUESTS_CA_BUNDLE', '/root/.ccr/ca-bundle.crt')
OUT = TF.OUT
FIX = os.path.join(OUT, 'fixes')
VOICE = 'NYC9WEgkq1u4jiqBseQ9'


def formant_track(x, fs, a, b):
    """(F1, F2) per 12 ms frame between a and b seconds (voiced, loud frames only)."""
    n, h, out = int(0.025 * fs), int(0.012 * fs), []
    for i in range(int(a * fs), int(b * fs) - n, h):
        seg = x[i:i + n]
        if 20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-9) < -30:
            continue
        seg = signal.lfilter([1, -0.97], 1, seg) * np.hamming(len(seg))
        r = np.correlate(seg, seg, 'full')[len(seg) - 1:len(seg) + 18]
        a_ = solve_toeplitz(r[:18], -r[1:19])
        roots = [z for z in np.roots(np.concatenate([[1], a_])) if np.imag(z) > 0]
        fr = sorted((np.angle(z) * fs / (2 * np.pi), -fs / np.pi * np.log(abs(z))) for z in roots)
        f = [q for q, bw in fr if 200 < q < 3500 and bw < 400][:2]
        if len(f) == 2:
            out.append(f)
    return np.array(out)


def diphthong_score(track):
    """/aI/: F1 starts high (open) and falls, F2 rises. Returns (max F1, F1 fall, F2 rise)."""
    if len(track) < 4:
        return (0, 0, 0)
    k = max(2, len(track) // 3)
    return (float(track[:, 0].max()), float(track[:k, 0].mean() - track[-k:, 0].mean()),
            float(track[-k:, 1].mean() - track[:k, 1].mean()))


def retake(idx, spoken, word_map, n=3):
    keyed = script.keyed()
    text = keyed[idx][1]
    prev_t = ' '.join(t for _, t in keyed[max(0, idx - 3):idx])
    next_t = keyed[idx + 1][1] if idx + 1 < len(keyed) else None
    os.makedirs(FIX, exist_ok=True)
    cands = []
    for c in range(n):
        path = os.path.join(FIX, f'line{idx:02d}_cand{c}.json')
        if not os.path.exists(path):
            body = dict(text=spoken, model_id=TF.MODEL, voice_settings=TF.SETTINGS, previous_text=prev_t)
            if next_t:
                body['next_text'] = next_t
            r = requests.post(f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps',
                              params=dict(output_format='mp3_44100_192'), json=body, timeout=300)
            if r.status_code != 200:
                raise SystemExit(f'error {r.status_code}: {r.text[:300]}')
            json.dump(r.json(), open(path, 'w'))
        d = json.load(open(path))
        mp3 = path.replace('.json', '.mp3')
        open(mp3, 'wb').write(base64.b64decode(d['audio_base64']))
        wav16 = path.replace('.json', '_16k.wav')
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', mp3, '-ar', '16000', '-ac', '1', wav16], check=True)
        x, fs = sf.read(wav16)
        al = d['alignment']
        chars, t0s, t1s = al['characters'], al['character_start_times_seconds'], al['character_end_times_seconds']
        got = ''.join(chars)
        target = [w for w in word_map][0]
        i = got.index(target)
        score = diphthong_score(formant_track(x, fs, t0s[i], t1s[i + len(target) - 1] + 0.03))
        speech = t1s[len(got.rstrip()) - 1] - t0s[0]
        cands.append(dict(c=c, path=path, mp3=mp3, score=score, speech=speech, al=al))
        print(f'cand {c}: F1max {score[0]:.0f} Hz, F1 fall {score[1]:.0f} Hz, F2 rise {score[2]:.0f} Hz, speech {speech:.2f}s')
    return text, cands


def install(idx, text, cand, word_map):
    """Cut the chosen candidate like the main take and swap it in, keeping later lines where they were."""
    lines = json.load(open(os.path.join(OUT, 'lines.json')))
    old = lines[idx]
    al = cand['al']
    chars, t0s, t1s = al['characters'], al['character_start_times_seconds'], al['character_end_times_seconds']
    got = ''.join(chars)
    wav = cand['mp3'].replace('.mp3', '.wav')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', cand['mp3'], '-ar', '48000', '-ac', '1', wav], check=True)
    x, fs = sf.read(wav)
    end = len(got.rstrip())
    lo = max(0.0, t0s[0] - 0.05)
    hi = min(len(x) / fs, t1s[end - 1] + 0.35)
    seg = x[int(lo * fs):int(hi * fs)].copy()
    # loudness-match to the line it replaces
    ref, _ = sf.read(os.path.join(OUT, old['file']))
    ref = ref.mean(1) if ref.ndim > 1 else ref
    def speech_rms(v):
        e = np.abs(v)
        return np.sqrt(np.mean(v[e > e.max() * 0.05] ** 2))
    seg *= speech_rms(ref) / speech_rms(seg)
    m1, m2 = int(0.01 * fs), int(0.08 * fs)
    seg[:m1] *= np.linspace(0, 1, m1)
    seg[-m2:] *= np.linspace(1, 0, m2)
    name = f'{idx:02d}_fix.wav'
    sf.write(os.path.join(OUT, name), seg, fs, subtype='PCM_24')
    words, i = [], 0
    for w_spoken, w_text in zip(got[:end].split(' '), text.split(' ')):
        j = i + len(w_spoken)
        words.append((w_text, round(t0s[i] - lo, 3), round(t1s[j - 1] - lo, 3)))
        i = j + 1
    new_dur = round(t1s[end - 1] + 0.12 - lo, 3)
    lines[idx] = dict(file=name, dur=new_dur, words=words, pause_adj=round(old['dur'] + old.get('pause_adj', 0) - new_dur, 3),
                      replaced=dict(file=old['file'], dur=old['dur']))
    json.dump(lines, open(os.path.join(OUT, 'lines.json'), 'w'), indent=1)
    print(f'line {idx}: {old["dur"]:.2f}s -> {new_dur:.2f}s (pause adjusted {lines[idx]["pause_adj"]:+.2f}s), words {words}')


if __name__ == '__main__':
    idx = 19                                   # "The ministry sees it happen, live."
    spoken = 'The ministry sees it happen, lyve.'
    text, cands = retake(idx, spoken, {'lyve': 'live'})
    if len(sys.argv) > 1 and sys.argv[1] == 'install':
        pick = int(sys.argv[2])
        install(idx, text, cands[pick], {'lyve': 'live'})
