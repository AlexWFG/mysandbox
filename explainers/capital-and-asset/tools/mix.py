"""Final mix: George narration (tempo 1.075, pitch preserved) + ElevenLabs music bed, with
synthesized, frame-accurate UI accents keyed to the narration timeline.

python3 tools/mix.py -> out/mix.wav (48 kHz stereo)
"""
import glob, json, os, subprocess
import numpy as np
from scipy import signal
from scipy.io import wavfile
import imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..'); AUD = os.path.join(ROOT, 'audio')
FF = imageio_ffmpeg.get_ffmpeg_exe()
TL = json.load(open(os.path.join(AUD, 'timeline.json')))
SR = 48000; DUR = TL['total']; N = int(SR * DUR)
rng = np.random.default_rng(3)


def load(path, af=None):
    cmd = [FF, '-v', 'error', '-i', path] + (['-af', af] if af else []) + ['-f', 'f32le', '-ac', '2', '-ar', str(SR), '-']
    raw = subprocess.run(cmd, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).astype(np.float64)


def tt(d): return np.arange(int(d * SR)) / SR
def filt(x, kind, f, order=2):
    wn = np.asarray(f, dtype=float) / (SR / 2)
    return signal.sosfilt(signal.butter(order, wn if wn.ndim else float(wn), btype=kind, output='sos'), x, axis=0)


class Bus:
    def __init__(self): self.x = np.zeros((N, 2))
    def add(self, sig, t0, gain=1.0, pan=0.0):
        if sig.ndim == 1:
            a = (pan + 1) * np.pi / 4; sig = np.stack([sig * np.cos(a), sig * np.sin(a)], 1)
        i0 = int(t0 * SR); n = min(len(sig), N - i0)
        if n > 0: self.x[i0:i0 + n] += sig[:n] * gain


music, vo, fx = Bus(), Bus(), Bus()
line = {l['id']: l for l in TL['lines']}
L = lambda i: line[i]['t']
def W(i, word, n=0):
    k = ''.join(c for c in word.lower() if c.isalnum()); c = 0
    for w, a, b in line[i]['words']:
        if ''.join(ch for ch in w.lower() if ch.isalnum()).startswith(k):
            if c == n: return a
            c += 1
    raise KeyError(word)

# ------------------------------------------------ narration
env = np.zeros(N)
for l in TL['lines']:
    s = load(os.path.join(AUD, l['file']), f"atempo={TL['tempo']}")
    s = filt(s, 'highpass', 70)
    vo.add(s, l['t'])
    i0 = int(l['t'] * SR); env[i0:i0 + len(s)] = 1
vo.x *= 0.7 / np.abs(vo.x).max()

# ------------------------------------------------ music bed
bed = load(sorted(glob.glob(os.path.join(AUD, 'music', 'bed_*.mp3')))[0])
bed = bed[:N]
k = min(len(bed), int(0.6 * SR)); bed[:k] *= np.linspace(0, 1, k)[:, None]
music.add(bed, 0.0)

# ------------------------------------------------ synthesized accents
def tick(g=.05, f=3200, d=.04):
    t = tt(d); return np.sin(2 * np.pi * f * t) * np.exp(-t * 180) * g
def pop(g=.08, f=880):  # soft rounded UI pop
    t = tt(.18); return (np.sin(2 * np.pi * f * t) + .3 * np.sin(2 * np.pi * 2 * f * t)) * np.exp(-t * 32) * (1 - np.exp(-t * 900)) * g
def swoosh(d=.7, f0=300, f1=6000, g=.06):
    x = rng.standard_normal(int(d * SR)); t = tt(d)
    return filt(x, 'bandpass', [f0, f1]) * np.sin(np.pi * t / d) ** 2 * g
def bell(f, d=1.6, g=.05):
    t = tt(d); return sum(a * np.sin(2 * np.pi * f * p * t) * np.exp(-t * kk / (d * .5)) for p, a, kk in [(1, 1, 1), (2.0, .35, 1.8), (3.01, .15, 2.6)]) * (1 - np.exp(-t * 800)) * g
def low(d=1.8, g=.18):
    t = tt(d); f = 42 + 30 * np.exp(-t / .12)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (d * .3)) * g
note = lambda n: 440 * 2 ** ((n - 69) / 12)

# chapter transitions
for i in ['v02', 'v06', 'v12', 'v17', 'v23', 'v30']:
    fx.add(swoosh(.9, 200, 5000, .05), L(i) - .7)
fx.add(low(2.2, .16), 0.1)                                   # open
# montage reveals
for w in ['brokers', 'valuers', 'lawyers', 'notaries', 'lenders']:
    fx.add(swoosh(.45, 800, 8000, .035), W('v02', w) - .25, pan=-.4)
# crowd appears
for j in range(20): fx.add(tick(.02, 2600 + (j * 137) % 1800), W('v02', 'twenty') - .2 + ((j * 0.618) % 1) * 1.4, pan=((j * .37) % 1.6) - .8)
fx.add(swoosh(1.3, 150, 3000, .05), L('v04'))                # rail draws
for w, n in [('own', 72), ('tool', 74), ('onboard', 76)]: fx.add(pop(.07, note(n)), W('v05', w) - .1)
fx.add(swoosh(.9, 300, 4000, .05), W('v06', 'splits') - .1)  # split in three
for i, (v, w) in enumerate([('v07', 'tool'), ('v08', 'Prop.com'), ('v09', 'Propchain')]): fx.add(bell(note(76 + 2 * i), 1.4, .04), W(v, w) - .2)
fx.add(low(1.8, .12), W('v11', 'worth'))
fx.add(bell(note(69), 2.4, .05), W('v11', 'Independence') - .15); fx.add(bell(note(76), 2.4, .03), W('v11', 'Independence') - .1)
for c in range(8): fx.add(tick(.03, 2400 + c * 160), L('v12') + .5 + c * .42)
# verbs on the map
for v, words, n in [('v14', ['Investors', 'lenders', 'buyers', 'sellers', 'tenants'], 67), ('v15', ['notary', 'registry', 'valuer', 'auditor', 'depositary', 'lawyers'], 71),
                    ('v16', ['underwriting', 'reporting', 'asset', 'debt', 'payments'], 74)]:
    for j, w in enumerate(words): fx.add(pop(.05, note(n + (j % 3) * 2)), W(v, w) - .05, pan=-.5 + j * .2)
fx.add(swoosh(1.8, 200, 6000, .06), W('v16', 'Prop.com') + .1)
fx.add(swoosh(1.1, 200, 5000, .05), W('v17', 'replaced') - .1); fx.add(bell(note(74), 1.6, .04), W('v17', 'replaced') + .8)
for v in ['v19', 'v20', 'v21']: fx.add(pop(.06, note(69)), L(v) - .2)
for j, v in enumerate(['v24', 'v25', 'v26', 'v27', 'v28']):
    if j: fx.add(swoosh(.8, 500, 7000, .035), L(v) - .95)
    fx.add(bell(note(69 + [0, 2, 4, 7, 9][j]), 1.8, .05), L(v) - .15, pan=-.6 + j * .3)
fx.add(low(1.4, .08), W('v29', 'demo') - .1); fx.add(bell(note(81), 2.2, .05), W('v29', 'closing') - .3)
for w in ['prepares', 'presents', 'records']: fx.add(pop(.05, note(76)), W('v30', w) - .15)
fx.add(tick(.06, 1400, .08), W('v30', 'never') + .1)
for j, w in enumerate(['Services', 'records', 'rails', 'need']): fx.add(pop(.05, note(69 + j * 3)), W('v31', w) - .15)
for j in range(3): fx.add(tick(.035, 3000 + j * 200), W('v32', 'Every') + .1 + j * .3)
for j, w in enumerate(['Own', 'Tool', 'Onboard']): fx.add(low(1.2, .07), W('v33', w) - .1)
fx.add(bell(note(62), 3.5, .05), line['v33']['t'] + line['v33']['dur'] + .8); fx.add(bell(note(69), 3.5, .035), line['v33']['t'] + line['v33']['dur'] + .85)

# ------------------------------------------------ ducking + master
kk = int(0.25 * SR)
e = np.clip(np.convolve(env, np.ones(kk) / kk, mode='same') * 1.4, 0, 1)
music.x *= (1 - 0.55 * e)[:, None]
fx.x *= (1 - 0.35 * e)[:, None]
# level: music+fx bed ~10 dB under narration
def rms(x, m=None): x = x if m is None else x[m]; return np.sqrt(np.mean(x ** 2))
spk = env > 0
vo_r = rms(vo.x, spk); bed_r = rms(music.x + fx.x, spk)
g = vo_r / bed_r * 10 ** (-10.5 / 20)
mix = vo.x + (music.x + fx.x) * g
T = np.arange(N) / SR
mix *= np.clip(np.minimum(T / .05, (DUR - T) / 1.2), 0, 1)[:, None]
mix = filt(mix, 'highpass', 25)
mix *= 10 ** (-16 / 20) / rms(mix)
mix = np.tanh(mix * 1.05) * .97
print('bed gain', round(g, 3), 'peak', round(float(np.abs(mix).max()), 3), 'rms dBFS', round(20 * np.log10(rms(mix)), 1),
      'VO/bed dB during speech', round(20 * np.log10(rms(vo.x, spk) / rms((music.x + fx.x) * g, spk)), 1))
os.makedirs(os.path.join(ROOT, 'out'), exist_ok=True)
wavfile.write(os.path.join(ROOT, 'out', 'mix.wav'), SR, (np.clip(mix, -1, 1) * 32767).astype(np.int16))
