"""Final mix -> out/mix.wav: narration (from timeline.json) over the ElevenLabs music bed, ducked,
plus a light layer of ElevenLabs SFX and synthesized ticks on picture cues.

Levels: during speech the music+SFX bus sits ~12 dB below the voice (brief asks for ~10 dB).
"""
import glob, json, os, re, subprocess
import numpy as np
from scipy import signal
from scipy.io import wavfile

HERE = os.path.dirname(os.path.abspath(__file__)); AUD = os.path.join(HERE, 'audio')
TL = json.load(open(os.path.join(HERE, 'timeline.json')))
SR = 48000; DUR = TL['total']; N = int(SR * DUR)


def load(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)
def one(kind, pre): return load(sorted(glob.glob(os.path.join(AUD, kind, pre + '_*.mp3')))[0])
def rms(x): return np.sqrt(np.mean(x ** 2) + 1e-12)
def db(x): return 20 * np.log10(x)


def at(lid, word, nth=0, lead=.12):   # port of engine.js at()
    l = TL['lines'][lid]; i = -1
    for _ in range(nth + 1): i = l['text'].index(word, i + 1)
    b = [0] + [m.end() for m in re.finditer(r'[,.:?!;]\s', l['text'])] + [len(l['text'])]
    s = l.get('segs', [])
    if len(s) == len(b) - 1:
        p = 0
        while p < len(s) - 1 and i >= b[p + 1]: p += 1
        f = (i - b[p]) / max(1, b[p + 1] - b[p]); return l['t'] + s[p][0] + (s[p][1] - s[p][0]) * f - lead
    return l['t'] + l['dur'] * i / len(l['text']) - lead
T = lambda k: TL['lines'][k]['t']


class Bus:
    def __init__(s): s.x = np.zeros((N, 2))
    def add(s, sig, t0, g=1.0, pan=0.0, fi=0.0, fo=0.0, dur=None, off=0.0):
        if sig.ndim == 1: a = (pan + 1) * np.pi / 4; sig = np.stack([sig * np.cos(a), sig * np.sin(a)], 1)
        x = sig[int(off * SR):].copy()
        if dur: x = x[:int(dur * SR)]
        if fi: k = min(len(x), int(fi * SR)); x[:k] *= np.linspace(0, 1, k)[:, None]
        if fo: k = min(len(x), int(fo * SR)); x[len(x) - k:] *= np.linspace(1, 0, k)[:, None]
        i0 = int(t0 * SR); n = min(len(x), N - i0)
        if n > 0: s.x[i0:i0 + n] += x[:n] * g


vo, mus, fx = Bus(), Bus(), Bus()
# ------------------------------------------------ narration
env = np.zeros(N)
hp = signal.butter(2, 70 / (SR / 2), 'highpass', output='sos')
for lid, l in TL['lines'].items():
    s = signal.sosfilt(hp, load(os.path.join(AUD, l['file'])), axis=0)
    t0 = l['t'] - l['clip_in']; vo.add(s, t0)
    i0 = int(l['t'] * SR); env[i0:i0 + int(l['dur'] * SR)] = 1
speech = env > 0
vo.x *= 10 ** (-18 / 20) / rms(vo.x[speech])                      # speech at -18 dBFS RMS
# ------------------------------------------------ music bed, ducked
bed = one('music', 'bed'); mus.add(bed, 0.0, fi=.2, fo=2.5)
k = int(.35 * SR); duck = np.convolve(env, np.ones(k) / k, 'same')  # smooth attack/release
m_speech = rms(mus.x[speech])
g_duck = 10 ** ((-18 - 13 - db(m_speech)) / 20)                    # music 13 dB under voice while speaking
g_open = g_duck * 10 ** (5.5 / 20)                                  # opens up 5.5 dB between lines
mus.x *= (g_open + (g_duck - g_open) * duck)[:, None]
# ------------------------------------------------ SFX
S = {n: one('sfx', n) for n in ['whoosh', 'stamp', 'coins', 'tick', 'paper']}
def tick(g=.06, f=3200, d=.035):
    t = np.arange(int(d * SR)) / SR; return np.sin(2 * np.pi * f * t) * np.exp(-t * 180) * g
for c in TL['chapters'][1:]: fx.add(S['whoosh'], c['t'] - .35, .35, fo=.3)
fx.add(S['whoosh'], TL['end'] - .5, .3, fo=.3)
fx.add(S['paper'], T('n01a') - .5, .35, fo=.3)
fx.add(S['stamp'], T('n01a') + 1.15, .5)
fx.add(S['stamp'], at('n01b', 'A rent roll') + .45, .4)
fx.add(S['stamp'], at('n10', 'A three'), .45)
fx.add(S['stamp'], at('n11', 'capital at risk'), .35)
for w in ['misstated', 'diverted']: fx.add(tick(.07, 2600), at('n03', w))
for i, w in enumerate(['identity', 'provenance', 'corroboration', 'bonds', 'professional', 'memory']): fx.add(tick(.05, 2400 + i * 180), at('n05', w))
for tt in [at('n08', 'one million'), at('n08', 'agrees'), at('n09', 'Bank'), at('n09', 'Tenants')]: fx.add(tick(.05, 2900), tt + .1)
fx.add(S['tick'], at('n10', 'quorum') + .3, .35)
for i in range(12): fx.add(tick(.04, 3000 + i * 60), T('n15') + i * .17)
fx.add(S['coins'], at('n14', 'One point'), .3, fo=.3)
fx.add(S['coins'], at('n16', 'released'), .3, fo=.3)
fx.add(S['coins'], at('n17', 'Half'), .3, fo=.3)
for w in ['self-bond', 'surety', 'policy']: fx.add(S['tick'], at('n21', w), .25)
for w in ['data partner', 'M G A', 'own carrier']: fx.add(S['tick'], at('n24b', w), .25)
for w in ['Measure', 'Bond', 'Insure']: fx.add(tick(.05, 2200), at('n27b', w))
fx.x *= (1 - .45 * duck)[:, None]
# ------------------------------------------------ master
mix = vo.x + mus.x + fx.x
mix = signal.sosfilt(signal.butter(2, 25 / (SR / 2), 'highpass', output='sos'), mix, axis=0)
Tm = np.arange(N) / SR; mix *= np.clip(np.minimum(Tm / .05, (DUR - Tm) / 1.2), 0, 1)[:, None]
bg = mus.x + fx.x
print('voice vs music+sfx during speech: %.1f dB' % (db(rms(vo.x[speech])) - db(rms(bg[speech]))))
mix = np.tanh(mix * 1.1) * .95
print('peak %.3f  rms %.1f dBFS' % (np.abs(mix).max(), db(rms(mix))))
os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
wavfile.write(os.path.join(HERE, 'out', 'mix.wav'), SR, (np.clip(mix, -1, 1) * 32767).astype(np.int16))
