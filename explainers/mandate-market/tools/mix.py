"""Final mix for the Mandate Market explainer -> out/mix.wav (48 kHz stereo).

Narration (ElevenLabs, light 1.05 atempo) on the timeline.json clock, one 150 s
ElevenLabs music bed arranged across the film, and synthesized UI accents cued
to the same narration words the picture uses. Music+SFX sit ~10 dB under voice.
"""
import glob, json, os, re, subprocess
import numpy as np
from scipy import signal
from scipy.io import wavfile
import imageio_ffmpeg

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
AUD = os.path.join(HERE, 'audio')
FF = imageio_ffmpeg.get_ffmpeg_exe()
TL = json.load(open(os.path.join(HERE, 'timeline.json')))
SR = 48000; DUR = TL['duration']; N = int(SR * DUR)
rng = np.random.default_rng(11)
LN = {l['id']: l for l in TL['lines']}


def W(i, key, n=0):
    norm = lambda s: re.sub(r"[^a-z0-9-']", '', s.lower())
    for w in LN[i]['words']:
        if norm(w['w']).startswith(norm(key)):
            if n == 0: return w['t']
            n -= 1
    raise KeyError((i, key))


def load(path, af=None):
    cmd = [FF, '-v', 'error', '-i', path] + (['-af', af] if af else []) + ['-f', 'f32le', '-ac', '2', '-ar', str(SR), '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, dtype=np.float32).reshape(-1, 2).astype(np.float64)


def filt(x, kind, f, order=2):
    wn = np.asarray(f, dtype=float) / (SR / 2)
    return signal.sosfilt(signal.butter(order, wn if wn.ndim else float(wn), btype=kind, output='sos'), x, axis=0)


def tt(d): return np.arange(int(d * SR)) / SR


class Bus:
    def __init__(self): self.x = np.zeros((N, 2))
    def add(self, sig, t0, gain=1.0, pan=0.0, fade_in=0.0, fade_out=0.0, dur=None, src_off=0.0):
        if sig.ndim == 1:
            a = (pan + 1) * np.pi / 4; sig = np.stack([sig * np.cos(a), sig * np.sin(a)], 1)
        s = sig[int(src_off * SR):]
        if dur is not None: s = s[:int(dur * SR)]
        s = s.copy()
        if fade_in: k = min(len(s), int(fade_in * SR)); s[:k] *= np.linspace(0, 1, k)[:, None] ** 1.5
        if fade_out: k = min(len(s), int(fade_out * SR)); s[len(s) - k:] *= np.linspace(1, 0, k)[:, None] ** 1.5
        i0 = int(t0 * SR); n = min(len(s), N - i0)
        if n > 0: self.x[i0:i0 + n] += s[:n] * gain


music, vo, fx = Bus(), Bus(), Bus()

# ------------------------------------------------------------------ narration
env = np.zeros(N)
for l in TL['lines']:
    s = filt(load(os.path.join(AUD, l['file']), f"atempo={TL['tempo']}"), 'highpass', 70)
    vo.add(s, l['t'] - .02)
    i0 = int(l['t'] * SR); env[i0:i0 + len(s)] = 1
vo.x *= 0.72 / np.abs(vo.x).max()

# ------------------------------------------------------------------ music: one 150 s bed, arranged
bed = load(glob.glob(os.path.join(AUD, 'music', 'bed150_*.mp3'))[0])
X1 = LN['13']['t'] - 1.3            # chapter 04 (the debt): restart the groove
X2 = LN['26']['t'] - 2.4            # chapter 09 (the claim): the resolve section
music.add(bed, 0.0, 1.0, fade_in=.3, dur=X1 + 1.5, fade_out=3.0)
music.add(bed, X1 - 1.5, 1.0, src_off=20.0, fade_in=3.0, dur=X2 - X1 + 3.0, fade_out=3.0)
music.add(bed, X2 - 1.5, 1.0, src_off=128.0, fade_in=3.0, fade_out=2.5)

k = int(0.25 * SR)
duck = np.clip(np.convolve(env, np.ones(k) / k, mode='same') * 1.4, 0, 1)
music.x *= (1 - 0.72 * duck)[:, None]

# ------------------------------------------------------------------ synthesized accents
def tick(g=.05, f=3200, d=.035):
    t = tt(d); return np.sin(2 * np.pi * f * t) * np.exp(-t * 180) * g
def blip(f=880, g=.06, d=.35):
    t = tt(d); return (np.sin(2 * np.pi * f * t) + .3 * np.sin(2 * np.pi * 2 * f * t)) * np.exp(-t * 14) * (1 - np.exp(-t * 900)) * g
def whoosh(d=.9, g=.05, f0=300, f1=5000):
    x = rng.standard_normal(int(d * SR)); t = tt(d)
    y = filt(x, 'bandpass', [f0, f1]) * np.sin(np.pi * t / d) ** 2
    return y * g
def thump(g=.25, d=1.4):
    t = tt(d); f = 42 + 40 * np.exp(-t / .08)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .35) * g
def chime(f=660, g=.05, d=2.2):
    t = tt(d); return sum(a * np.sin(2 * np.pi * f * p * t) * np.exp(-t * q) for p, a, q in [(1, 1, 2.2), (2.0, .35, 3.5), (3.01, .15, 5)]) * (1 - np.exp(-t * 500)) * g

L = lambda i: LN[i]['t']; E = lambda i: LN[i]['end']
fx.add(thump(.22), 0.1)
fx.add(chime(523, .05), 0.4, pan=-.2)
# chapter turns: a soft air whoosh
for t in [4.9, L('04') - .7, L('07') - 1.0, W('07', 'hard') - .2, L('13') - 1.3, W('13', 'they') - .25, L('15') - .7, L('19') - .7, L('20') - .7, W('23', 'so') - .3, L('24') - .8, L('26') - .9]:
    fx.add(whoosh(1.0, .06), t - .5, pan=0)
# order book: tokens stacking, then the match
for i in range(10): fx.add(tick(.03, 2600 + i * 90), W('01', 'that') + .2 + i * .06, pan=-.3 + i * .06)
fx.add(blip(988, .07), E('01') - .6)
# asset rows + lineage
for cue in ['income', 'cap', 'lease', 'tenant']: fx.add(tick(.045, 3000), W('04', cue) - .1, pan=-.4)
for cue in ['source', 'timestamp', 'confidence']: fx.add(blip(1175, .035, .25), W('04', cue))
fx.add(blip(784, .05), W('06', 'seller') - .05, pan=-.3)
# filters: one tick per check, a low blip per rejection
ft = [W('07', 'logistics'), W('07', 'germany'), W('07', 'ten'), W('07', 'cap')]
for k, f in enumerate(ft):
    for i in range(7): fx.add(tick(.03, 3400 + k * 150), f + .25 + i * .07, pan=.2)
for k in range(4): fx.add(blip(330, .05, .3), ft[k] + .35 + [1, 2, 3, 5][k] * .07, pan=.1)
# utilities, decay swap, floor, tie-break
fx.add(whoosh(1.4, .035, 800, 7000), W('08', 'utility') - .1)
fx.add(blip(659, .05), W('08', 'caps'))
fx.add(blip(880, .05), W('10', 'outranks') + .6)
for cue in ['cap', 'lease', 'credit', 'vacancy']: fx.add(tick(.045, 2800), W('11', cue) - .1)
fx.add(thump(.16, 1.0), W('11', 'zeroes'))
fx.add(blip(880, .05), W('12', 'longer') + .9)
# debt: pair, boxes fire, gate
fx.add(chime(587, .045), W('13', 'pair') - .1)
fx.add(blip(988, .05), W('14', 'fifty-five') - .1, pan=.3); fx.add(blip(988, .05), W('14', 'sixty') - .1, pan=.3)
fx.add(blip(262, .05), W('14', 'silent'), pan=.3)
fx.add(tick(.06, 2000, .05), W('14', 'attested') - .2)
# bid: three bars, bind, P*
for cue in ['seven', 'nine', 'ten']: fx.add(whoosh(.8, .025, 1500, 8000), W('16', cue) - .25, pan=.2)
fx.add(blip(784, .06), W('16', 'binds'))
bs = W('17', 'return') - .1
for i in range(6): fx.add(tick(.04, 3600 - i * 200), bs + i * .16)
fx.add(chime(698, .05), bs + 1.0)
# seller reorder
fx.add(blip(880, .05), W('19', 'beat'))
# clearing: proposals, holds, releases, lock
tP = W('20', 'proposes'); tH = W('21', 'holds'); tR = W('21', 'releases'); tM = W('22', 'move')
for i in range(3): fx.add(blip(660 + i * 60, .04, .3), tP + i * .25, pan=-.3 + i * .3)
fx.add(blip(880, .05), tH); fx.add(blip(330, .04), tR)
for dt, f in [(-.1, 700), (1.5, 880), (1.6, 330), (2.2, 700), (3.1, 330), (3.4, 700), (4.1, 880)]: fx.add(blip(f, .04, .3), tM + dt)
fx.add(chime(523, .06, 3.0), W('23', 'stable') - .1); fx.add(chime(784, .03, 3.0), W('23', 'stable') + .05)
# living book: four event pulses, sinking asset
for cue in ['attestations', 'amended', 'filled', 'rate']: fx.add(blip(740, .04, .3), W('24', cue) + .9)
fx.add(whoosh(1.6, .035, 200, 2000), W('24', 'sinks') - .6)
# claim
fx.add(thump(.2), L('27') - .1)
fx.add(chime(523, .05, 3.0), E('27') + 2.3); fx.add(chime(784, .03, 3.0), E('27') + 2.45)

# ------------------------------------------------------------------ master
fx.x *= (1 - 0.35 * duck)[:, None]
mix = music.x * 0.40 + fx.x * 0.9 + vo.x * 1.0
T = np.arange(N) / SR
mix = filt(mix, 'highpass', 25)
fade = np.clip(np.minimum(T / .05, (DUR - T) / 1.2), 0, 1); mix *= fade[:, None]
rms = np.sqrt(np.mean(mix ** 2)); mix *= 10 ** (-17 / 20) / rms
mix = np.tanh(mix * 1.05) * .97
def db(x): return round(20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12), 1)
m = env > 0
print('peak', np.abs(mix).max().round(3), 'rms', db(mix), '| voice-only segs: vo', db(vo.x[m]), 'music+fx', db(music.x[m] * .40 + fx.x[m] * .9))
os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
wavfile.write(os.path.join(HERE, 'out', 'mix.wav'), SR, (np.clip(mix, -1, 1) * 32767).astype(np.int16))
