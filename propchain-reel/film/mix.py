"""Final mix: ElevenLabs narration + music + SFX, plus synthesized frame-accurate accents.

python3 film/mix.py -> film/out/mix.wav (48 kHz stereo, 132.4 s)
Times are final-film seconds (after the Act II insert).
"""
import glob, json, os, subprocess
import numpy as np
from scipy import signal
from scipy.io import wavfile
import imageio_ffmpeg

SR = 48000; DUR = 132.4; N = int(SR * DUR)
HERE = os.path.dirname(__file__); AUD = os.path.join(HERE, 'audio')
FF = imageio_ffmpeg.get_ffmpeg_exe()
rng = np.random.default_rng(5)


def load(path):
    raw = subprocess.run([FF, '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).astype(np.float64)


def one(kind, prefix):
    return load(sorted(glob.glob(os.path.join(AUD, kind, prefix + '_*.mp3')))[0])


def tt(d): return np.arange(int(d * SR)) / SR
def filt(x, kind, f, order=2):
    wn = np.asarray(f, dtype=float) / (SR / 2)
    return signal.sosfilt(signal.butter(order, wn if wn.ndim else float(wn), btype=kind, output='sos'), x, axis=0)


class Bus:
    def __init__(self): self.x = np.zeros((N, 2))
    def add(self, sig, t0, gain=1.0, pan=0.0, fade_in=0.0, fade_out=0.0, dur=None, src_off=0.0):
        if sig.ndim == 1:
            a = (pan + 1) * np.pi / 4; sig = np.stack([sig * np.cos(a), sig * np.sin(a)], 1)
        s = sig[int(src_off * SR):]
        if dur is not None: s = s[:int(dur * SR)]
        s = s.copy()
        if fade_in: k = min(len(s), int(fade_in * SR)); s[:k] *= np.linspace(0, 1, k)[:, None]
        if fade_out: k = min(len(s), int(fade_out * SR)); s[len(s) - k:] *= np.linspace(1, 0, k)[:, None]
        i0 = int(t0 * SR); n = min(len(s), N - i0)
        if n > 0: self.x[i0:i0 + n] += s[:n] * gain


music, vo, fx = Bus(), Bus(), Bus()

# ------------------------------------------------------------------ music (three ElevenLabs cues)
A, B, C = one('music', 'A_hype'), one('music', 'B_reality'), one('music', 'C_reveal')
music.add(A, 0.0, 1.0, fade_in=0.4, dur=30.9, fade_out=0.75)            # cut to black: short natural decay, not a chop
music.add(B, 31.6, 1.0, fade_in=1.5, dur=86.15 - 31.6, fade_out=0.35)  # dies before "The token was never the problem."
music.add(C, 89.8, 1.0, fade_in=0.05, fade_out=1.2)

# ------------------------------------------------------------------ narration
tl = json.load(open(os.path.join(AUD, 'vo_timeline.json')))
times = {l['id']: l['t'] for l in json.load(open(os.path.join(AUD, 'narration.json')))['lines']}
vo_env = np.zeros(N)
for l in tl:
    s = load(os.path.join(AUD, l['file']))
    s = filt(s, 'highpass', 70)
    t0 = times[l['id']]
    vo.add(s, t0, 1.0)
    i0 = int(t0 * SR); vo_env[i0:i0 + len(s)] = 1
peak = np.abs(vo.x).max(); vo.x *= 0.72 / peak

# duck music under narration (smooth attack/release)
k = int(0.18 * SR)
env = np.convolve(vo_env, np.ones(k) / k, mode='same')
env = np.clip(env * 1.5, 0, 1)
music.x *= (1 - 0.84 * env)[:, None]

# ------------------------------------------------------------------ SFX (ElevenLabs) — realism layer
S = {n: one('sfx', n) for n in ['rain', 'clock', 'paperstorm', 'applause', 'tradefloor', 'shutters', 'keyboard', 'signing', 'glitch', 'citynight', 'boomtail', 'whoosh']}
fx.add(S['tradefloor'], 5.6, .22, fade_in=.1, dur=1.7, fade_out=.2)
fx.add(S['shutters'], 7.3, .2, dur=1.7, fade_out=.2)
fx.add(S['applause'], 15.4, .25, dur=1.2, fade_out=.3)
fx.add(S['tradefloor'], 17.0, .3, src_off=2.5, dur=1.1, fade_out=.2)
fx.add(S['applause'], 26.6, .18, src_off=1.0, dur=3.5, fade_in=.4, fade_out=.05)
fx.add(S['rain'], 34.3, .55, fade_in=1.5, dur=20.0)
fx.add(S['rain'], 54.3, .45, src_off=4.0, dur=7.1, fade_in=.2, fade_out=1.0)
fx.add(S['clock'], 41.0, .22, fade_in=1.0, dur=10.0, fade_out=1.0)
fx.add(S['clock'], 51.0, .18, dur=9.8, fade_out=1.5)
fx.add(S['paperstorm'], 68.9, .32, fade_in=.3, dur=5.0, fade_out=.4)
fx.add(S['glitch'], 70.9, .14, dur=2.4, fade_out=.3)
fx.add(S['signing'], 76.0, .5, dur=1.8, fade_out=.2)
fx.add(S['keyboard'], 93.2, .3, dur=3.6, fade_out=.4)
fx.add(S['keyboard'], 113.8, .28, dur=3.0, fade_out=.4)
fx.add(S['citynight'], 124.4, .35, fade_in=.5, dur=8.0, fade_out=1.2)
boom = S['boomtail']; wh = S['whoosh']
for t in [11.9, 14.9, 16.5, 18.1]:                                  # word slams
    fx.add(wh, t - 0.3, .2, dur=.45, fade_out=.1); fx.add(boom, t, .32)
fx.add(boom, 30.15, .42)                                            # cut to black: the tail carries the silence
fx.add(boom, 87.95, .5)                                             # "The data was."
fx.add(boom, 89.8, .4)                                              # reveal
fx.add(boom, 96.9, .45)                                              # snap: structured
fx.add(boom, 127.6, .4)                                             # logo

# ------------------------------------------------------------------ synthesized accents (frame-accurate)
def sboom(d=1.6, f0=90, f1=40, drop=.1):
    t = tt(d); f = f1 + (f0 - f1) * np.exp(-t / drop)
    return np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (d * .28)) * 1.6) * .8
def tick(g=.05, f=4800, d=.03):
    t = tt(d); return np.sin(2 * np.pi * f * t) * np.exp(-t * 260) * g
def swoosh(d, f0=400, f1=9000):
    x = rng.standard_normal(int(d * SR)); t = tt(d)
    y = filt(x, 'bandpass', [f0, f1]) * (t / d) ** 2.2
    return y
def bell(f, d=2.0, g=.1):
    t = tt(d); return sum(a * np.sin(2 * np.pi * f * p * t) * np.exp(-t * k / (d * .5)) for p, a, k in [(1, 1, 1), (2.76, .45, 1.8), (5.4, .25, 2.6)]) * (1 - np.exp(-t * 800)) * g

for t in [5.6, 7.3, 10.6, 12.5, 15.4, 17.0, 18.6, 26.6, 51.4, 54.2, 56.4, 58.6, 59.9]:   # press window cuts: a light air whoosh only
    fx.add(wh, t - .3, .12, dur=.55, fade_out=.15)
for tc in [9.0, 13.8]:                                                               # counters climbing
    for k in range(18): fx.add(tick(.035, 4000 + k * 120), tc + .05 + (k / 18) ** 1.8 * 1.1)
fx.add(tick(.14, 1800, .05), 31.0)                                                   # the only sound in the silence
t = tt(3.0); dfl = np.tanh(np.sin(2 * np.pi * np.cumsum(90 * np.exp(-t * 1.2) + 25) / SR) * np.exp(-t * .9) * .8)
fx.add(dfl * .4, 37.25)                                                              # the crash
for k in range(22): fx.add(tick(.03, 5200 - k * 150), 36.0 + (k / 22) ** .7 * 1.25, pan=-.2)
for k in range(5): fx.add(tick(.04, 3200 + k * 150), 41.5 + k * .4, pan=.3)          # chart rows
for k in range(12): fx.add(tick(.045, 3000 + k * 90, .03), 74.3 + k * .22, pan=-.6 + k * .1)   # intermediaries light up
for k in range(0, 40, 2): fx.add(tick(.008, 6000, .015), 81.1 + k * .12, pan=-.5)    # algo prints (sparser)
fx.add(swoosh(2.0, 200, 9000) * .18, 84.2)                                          # riser into the silence
for k, n in enumerate([88, 91, 95, 98]): fx.add(bell(440 * 2 ** ((n - 69) / 12), 2.0, .06), 100.85 + k * .5, pan=.5)  # proofs
for k in range(12):                                                                   # agents
    dz = .2; zt = tt(dz); f = np.linspace(1800 + rng.random() * 1500, 5000 + rng.random() * 3000, len(zt))
    fx.add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * zt / dz) ** 2 * .015, 105.3 + k * .33, pan=rng.random() * 1.6 - .8)
for k in range(5): fx.add(tick(.05, 2400 + k * 300, .05), 118.7 + k * .95, pan=-.4 + k * .2)   # deal steps
for k in range(30): fx.add(tick(.025, 4600 + (k % 4) * 300), 124.5 + (k / 30) ** 1.8 * 1.3)   # stats

# ------------------------------------------------------------------ master
fx.x *= (1 - 0.72 * env)[:, None]
mix = music.x * 0.55 + fx.x * 0.57 + vo.x * 1.0
T = np.arange(N) / SR
# faint room tone so the black is never digital silence
room = filt(rng.standard_normal((N, 2)), 'bandpass', [60, 500]) * 0.0025
mix += room * np.clip(np.interp(T, [29.8, 30.4, 33.0, 35.0], [0, 1, 1, 0]), 0, 1)[:, None]
mix = filt(mix, 'highpass', 25)
fade = np.clip(np.minimum(T / .05, (DUR - T) / 1.0), 0, 1); mix *= fade[:, None]
rms = np.sqrt(np.mean(mix ** 2)); mix *= 10 ** (-16 / 20) / rms            # ~ -16 dBFS RMS
mix = np.tanh(mix * 1.05) * .97  # soft limiter: never exceeds .97
print('peak', np.abs(mix).max().round(3), 'rms dBFS', round(20 * np.log10(np.sqrt(np.mean(mix ** 2))), 1))
os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
wavfile.write(os.path.join(HERE, 'out', 'mix.wav'), SR, (np.clip(mix, -1, 1) * 32767).astype(np.int16))
