"""Final mix: George narration + ElevenLabs music bed + synthesized, frame-accurate UI accents.

python3 tools/mix.py -> out/mix.wav (48 kHz stereo)
Narration sits ~10 dB above music + SFX; music is ducked under the voice.
"""
import glob, json, os, subprocess
import numpy as np
from scipy import signal
from scipy.io import wavfile
import imageio_ffmpeg

H = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
AUD = os.path.join(H, 'audio')
FF = imageio_ffmpeg.get_ffmpeg_exe()
TL = json.load(open(os.path.join(AUD, 'timeline.json')))
SR = 48000; DUR = TL['end']; N = int(SR * DUR)
rng = np.random.default_rng(3)


def load(path):
    raw = subprocess.run([FF, '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).astype(np.float64)


def tt(d): return np.arange(int(d * SR)) / SR
def filt(x, kind, f, order=2):
    wn = np.asarray(f, dtype=float) / (SR / 2)
    return signal.sosfilt(signal.butter(order, wn if wn.ndim else float(wn), btype=kind, output='sos'), x, axis=0)
def rms(x): return np.sqrt(np.mean(x ** 2) + 1e-12)
def db(x): return 10 ** (x / 20)


class Bus:
    def __init__(self): self.x = np.zeros((N, 2))
    def add(self, sig, t0, gain=1.0, pan=0.0):
        if sig.ndim == 1:
            a = (pan + 1) * np.pi / 4; sig = np.stack([sig * np.cos(a), sig * np.sin(a)], 1)
        i0 = int(t0 * SR); n = min(len(sig), N - i0)
        if n > 0: self.x[i0:i0 + n] += sig[:n] * gain


def W(i, word, lead=0.25):
    l = TL['lines'][i]; k = l['text'].index(word)
    return l['t'] + l['d'] * k / len(l['text']) - lead


music, vo, fx = Bus(), Bus(), Bus()

# ------------------------------------------------------------------ narration
env = np.zeros(N)
for i, l in TL['lines'].items():
    s = filt(load(os.path.join(AUD, l['file'])), 'highpass', 70)
    vo.add(s, l['t']); i0 = int(l['t'] * SR); env[i0:i0 + len(s)] = 1
vo.x *= 0.7 / np.abs(vo.x).max()
vo_rms = rms(vo.x[env > 0])

# ------------------------------------------------------------------ music bed, ducked
bed = load(sorted(glob.glob(os.path.join(AUD, 'music', 'bed_*.mp3')))[0])
music.add(bed[:N], 0.0)
music.x *= db(-7.5) * vo_rms / rms(music.x)          # bed sits ~9 dB under voice before ducking
k = int(0.35 * SR); duck = np.clip(np.convolve(env, np.ones(k) / k, mode='same') * 1.4, 0, 1)
music.x *= (1 - 0.3 * duck)[:, None]                 # a further ~6 dB under speech

# ------------------------------------------------------------------ synthesized accents
def tick(g=.05, f=3200, d=.04):
    t = tt(d); return np.sin(2 * np.pi * f * t) * np.exp(-t * 180) * g
def whoosh(d=.7, g=.06):
    x = rng.standard_normal(int(d * SR)); t = tt(d)
    y = filt(x, 'bandpass', [300, 6000]) * np.sin(np.pi * t / d) ** 2
    return y / (np.abs(y).max() + 1e-9) * g
def chime(f=880, d=1.6, g=.05):
    t = tt(d); return sum(a * np.sin(2 * np.pi * f * p * t) * np.exp(-t * kk) for p, a, kk in [(1, 1, 3), (2.0, .35, 5), (3.01, .15, 7)]) * (1 - np.exp(-t * 600)) * g
def thump(g=.12, d=.5):
    t = tt(d); f = 55 + 60 * np.exp(-t * 18); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) * g

# scene transitions
for t in [6.2, 12.4, 36.0, 54.6, 57.5, 101.6, 114.0, 123.9, 142.3, 145.4, 155.0, 163.4, 177.4, 181.4, 191.2, 199.0, 209.0, 221.1, 230.6, 235.6]:
    fx.add(whoosh(), t - .35, pan=0)
# chips / nodes / steps appearing
chips = [W('03', w) for w in ['commitments', 'identities', 'grants', 'signatures', 'settlement state', 'audit log root']]
chips += [W('04', w) for w in ['records', 'mandates', 'matching engine', 'models', 'documents', 'keys never']]
chips += [W('06', w) for w in ['Identity', 'ingestion', 'record store', 'attestation', 'Matching', 'settlement', 'agent runtime', 'integration']]
chips += [W('19', w) for w in ['institution', 'principal', 'agent credential', 'action.']]
chips += [W('21', w) for w in ['List', 'diligence', 'match,', 'finance', 'settle.', 'operate']]
chips += [W('24', w) for w in ['financing pack', 'credit policy', 'servicing feed']]
chips += [W('26', w) for w in ['Alone', 'second', 'third']] + [W('27', w) for w in ['Commit', 'Connect', 'Match', 'Settle']]
for i, t in enumerate(chips): fx.add(tick(.045, 2600 + (i % 5) * 180), t + .05, pan=(i % 3 - 1) * .3)
# hashes scrambling
for i in range(3):
    for j in range(8): fx.add(tick(.02, 5200 + j * 90, .02), TL['lines']['11']['t'] + .8 + i * .3 + j * .11, pan=.3)
# key moments: root, quorum, on chain, grant match, proof, enclave, neither replaced, logo
for t, f in [(W('12', 'Merkle root'), 880), (W('13', 'quorum') + .2, 1175), (TL['lines']['15']['t'] + 5.5, 988), (W('17', 'checks') + .9, 1318),
             (W('18', 'at least') + 1.6, 1175), (W('20', 'a root out') + .3, 988), (W('23', 'cannot reach'), 740)]:
    fx.add(chime(f), t, pan=.2)
for t in [W('14', 'the root') + 1.1, W('14', 'signatures') + 1.1, W('14', 'level') + 1.1]:
    fx.add(thump(.1), t)
fx.add(thump(.16, .9), 235.8); fx.add(chime(587, 3.0, .05), 235.8); fx.add(chime(880, 3.0, .03), 235.9)
fx.x *= db(-10) * vo_rms / (rms(fx.x[np.abs(fx.x).sum(1) > 1e-4]) + 1e-9)
fx.x *= (1 - 0.3 * duck)[:, None]

# ------------------------------------------------------------------ master
mix = music.x + fx.x + vo.x
T = np.arange(N) / SR
mix = filt(mix, 'highpass', 25)
mix *= np.clip(np.minimum(T / .05, (DUR - T) / 1.2), 0, 1)[:, None]
mix *= db(-16) / rms(mix)
mix = np.tanh(mix * 1.05) * .97
print('peak', np.abs(mix).max().round(3), 'rms dBFS', round(20 * np.log10(rms(mix)), 1),
      '| voice vs music+fx (speech regions) dB', round(20 * np.log10(rms(vo.x[env > 0]) / rms((music.x + fx.x)[env > 0])), 1))
os.makedirs(os.path.join(H, 'out'), exist_ok=True)
wavfile.write(os.path.join(H, 'out', 'mix.wav'), SR, (np.clip(mix, -1, 1) * 32767).astype(np.int16))
