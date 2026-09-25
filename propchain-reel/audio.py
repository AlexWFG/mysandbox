"""Sound design + score for the Propchain reel, synthesised to match the picture cue sheet.

python3 audio.py -> out/score.wav (48 kHz stereo, 30 s)
"""
import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 48000
DUR = 30.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
L = np.zeros(N)
Rr = np.zeros(N)
t_all = np.arange(N) / SR


def note(n):  # midi -> Hz
    return 440.0 * 2 ** ((n - 69) / 12)


def sos_filter(x, kind, f, order=2):
    wn = np.asarray(f, dtype=float) / (SR / 2)
    sos = signal.butter(order, wn if wn.ndim else float(wn), btype=kind, output='sos')
    return signal.sosfilt(sos, x)


def env_adsr(n, a, d, s, r, sus_len):
    a, d, r = int(a * SR), int(d * SR), int(r * SR)
    sl = max(0, n - a - d - r)
    e = np.concatenate([np.linspace(0, 1, max(a, 1)), np.linspace(1, s, max(d, 1)), np.full(sl, s), np.linspace(s, 0, max(r, 1))])
    return e[:n] if len(e) >= n else np.pad(e, (0, n - len(e)))


def place(x, t0, gain=1.0, pan=0.0):
    """Add mono (or stereo tuple) signal at time t0 with equal-power pan."""
    i0 = int(t0 * SR)
    if isinstance(x, tuple):
        xl, xr = x
    else:
        a = (pan + 1) * np.pi / 4
        xl, xr = x * np.cos(a), x * np.sin(a)
    n = min(len(xl), N - i0)
    if n <= 0:
        return
    L[i0:i0 + n] += xl[:n] * gain
    Rr[i0:i0 + n] += xr[:n] * gain


def tt(d):
    return np.arange(int(d * SR)) / SR


def noise(d):
    return rng.standard_normal(int(d * SR))


# ------------------------------------------------------------ building blocks
def sub_boom(d=3.0, f0=62, f1=32, drop=0.25):
    t = tt(d)
    f = f1 + (f0 - f1) * np.exp(-t / drop)
    ph = 2 * np.pi * np.cumsum(f) / SR
    e = np.exp(-t / (d * 0.28)) * (1 - np.exp(-t * 400))
    body = np.sin(ph) * e
    click = sos_filter(noise(d), 'bandpass', [80, 900]) * np.exp(-t * 60) * 0.5
    return np.tanh((body + click) * 1.6) * 0.9


def whoosh(d, f_start=300, f_end=6000, curve=2.0, rev=False):
    t = tt(d)
    x = noise(d)
    # time-varying bandpass via chunked filtering
    out = np.zeros_like(x)
    chunks = 64
    cl = len(x) // chunks
    zi = None
    for c in range(chunks):
        u = c / (chunks - 1)
        fc = f_start * (f_end / f_start) ** (u ** curve)
        sos = signal.butter(2, [max(40, fc * 0.6) / (SR / 2), min(SR / 2 - 100, fc * 1.6) / (SR / 2)], btype='bandpass', output='sos')
        seg = x[c * cl:(c + 1) * cl if c < chunks - 1 else len(x)]
        if zi is None:
            zi = signal.sosfilt_zi(sos) * 0
        y, zi = signal.sosfilt(sos, seg, zi=zi)
        out[c * cl:c * cl + len(y)] = y
    e = (t / d) ** 2.2 if not rev else (1 - t / d) ** 1.5
    e = e * (1 - np.exp(-(d - t) * 60)) if not rev else e
    return out * e


def pad(freqs, d, a=1.5, r=2.0, cutoff=1800, det=0.12, gain=0.12):
    t = tt(d)
    xl = np.zeros(len(t)); xr = np.zeros(len(t))
    for f in freqs:
        for k, dt in enumerate([-det, 0, det]):
            ph = rng.random() * 2 * np.pi
            ff = f * 2 ** (dt / 12)
            saw = 2 * ((t * ff + ph / (2 * np.pi)) % 1) - 1
            if k == 0: xl += saw
            elif k == 2: xr += saw
            else: xl += saw * 0.7; xr += saw * 0.7
    xl = sos_filter(xl, 'lowpass', cutoff, 2); xr = sos_filter(xr, 'lowpass', cutoff, 2)
    e = env_adsr(len(t), a, 0.5, 0.85, r, d)
    return (xl * e * gain / len(freqs), xr * e * gain / len(freqs))


def bell(f, d=2.5, gain=0.2):
    t = tt(d)
    partials = [(1, 1.0, 1.0), (2.76, 0.45, 1.8), (5.4, 0.25, 2.6), (8.93, 0.12, 3.5)]
    x = sum(a * np.sin(2 * np.pi * f * p * t) * np.exp(-t * k / (d * 0.5)) for p, a, k in partials)
    x *= 1 - np.exp(-t * 800)
    return x * gain


def pluck(f, d=1.2, gain=0.25, bright=4000):
    t = tt(d)
    x = sum(np.sin(2 * np.pi * f * h * t) / h ** 1.2 for h in range(1, 7))
    x = sos_filter(x, 'lowpass', bright)
    return x * np.exp(-t * 4.5) * (1 - np.exp(-t * 1500)) * gain


def tick(gain=0.2, f=5200, d=0.03):
    t = tt(d)
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 260) * gain + sos_filter(noise(d), 'highpass', 6000) * np.exp(-t * 400) * gain * 0.4


def kick(gain=0.5):
    t = tt(0.45)
    f = 45 + 90 * np.exp(-t * 35)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    return np.tanh(x * 2) * gain


def hat(gain=0.07, d=0.06):
    t = tt(d)
    return sos_filter(noise(d), 'highpass', 8000) * np.exp(-t * 90) * gain


def paper_flutter(d, density=35, gain=0.12, lo=1800, hi=7000):
    """Many short rustles: papers flapping in air."""
    x_l = np.zeros(int(d * SR)); x_r = np.zeros(int(d * SR))
    n_ev = int(d * density)
    for _ in range(n_ev):
        t0 = rng.random() * d
        ln = 0.03 + rng.random() * 0.14
        seg = sos_filter(noise(ln), 'bandpass', [lo * (0.7 + rng.random() * 0.6), hi * (0.7 + rng.random() * 0.5)])
        tseg = tt(ln)
        # flap: several amplitude bumps
        fl = 18 + rng.random() * 30
        seg *= (0.5 + 0.5 * np.sin(2 * np.pi * fl * tseg) ** 2) * np.sin(np.pi * tseg / ln) ** 1.5
        a = rng.random() * np.pi / 2
        i0 = int(t0 * SR); n = min(len(seg), len(x_l) - i0)
        amp = 0.3 + rng.random()
        x_l[i0:i0 + n] += seg[:n] * np.cos(a) * amp; x_r[i0:i0 + n] += seg[:n] * np.sin(a) * amp
    return (x_l * gain, x_r * gain)


def glitch_burst(d=0.12, gain=0.12):
    t = tt(d)
    f = rng.choice([220, 330, 440, 660, 880, 1320])
    sq = np.sign(np.sin(2 * np.pi * f * t))
    crush = np.round(sq * 3) / 3
    gate = (np.floor(t * rng.integers(30, 90)) % 2)
    return crush * gate * np.exp(-t * 12) * gain


def reverb(xl, xr, dur=3.2, mix=0.28, pre=0.02, hp=200, lp=7000):
    n = int(dur * SR)
    tr = np.arange(n) / SR
    envr = np.exp(-tr * 6.9 / dur)
    irl = sos_filter(rng.standard_normal(n), 'bandpass', [hp, lp]) * envr
    irr = sos_filter(rng.standard_normal(n), 'bandpass', [hp, lp]) * envr
    p = int(pre * SR)
    irl = np.concatenate([np.zeros(p), irl]); irr = np.concatenate([np.zeros(p), irr])
    irl /= np.sqrt(np.sum(irl ** 2)); irr /= np.sqrt(np.sum(irr ** 2))
    wl = signal.fftconvolve(xl, irl)[:len(xl)]
    wr = signal.fftconvolve(xr, irr)[:len(xr)]
    return xl * (1 - mix) + wl * mix * 1.4, xr * (1 - mix) + wr * mix * 1.4


# ------------------------------------------------------------ cue sheet
D = 38  # D1 root

# Bed: sub drone + air through the whole film, shaped by act
bed_t = t_all
drone = (np.sin(2 * np.pi * note(D) * bed_t) * 0.5 + np.sin(2 * np.pi * note(D + 12) * bed_t + 0.3) * 0.18)
drone_env = np.interp(bed_t, [0, 1.5, 3.8, 4.2, 9.5, 10.9, 11.0, 11.6, 18.3, 18.6, 25.0, 25.3, 29.0, 30], [0, .55, .6, .8, .8, 1.0, 0.2, .7, .7, .9, .9, .5, .4, 0])
place((drone * drone_env * 0.16, drone * drone_env * 0.16), 0)
air = sos_filter(rng.standard_normal(N), 'bandpass', [120, 900])
air_env = np.interp(bed_t, [0, 1, 4, 11, 11.1, 30], [0, .9, .7, .8, .3, .3])
place((air * air_env * 0.02, np.roll(air, 1200) * air_env * 0.02), 0)

# ACT 1 — the asset
place(sub_boom(4.0, 70, 30, 0.3), 0.68, 0.55)
place(pad([note(D + 12), note(D + 19), note(D + 24), note(D + 26)], 3.6, a=1.4, r=0.8, cutoff=900, gain=0.16), 0.3)
for k in range(24):  # counter ticks, decelerating
    u = k / 23
    place(tick(0.05 * (1 - u * 0.5), 4200 + 600 * (k % 3)), 0.9 + 1.4 * (1 - (1 - u) ** 2.2), pan=0.2)
scan = whoosh(1.9, 900, 9000, 1.2) * 0.08
place(scan, 1.7, pan=-0.2)
place(sos_filter(np.sin(2 * np.pi * np.cumsum(np.linspace(2200, 5200, int(1.8 * SR))) / SR), 'bandpass', [1500, 7000]) * np.sin(np.linspace(0, np.pi, int(1.8 * SR))) * 0.025, 1.7, pan=0.3)

# Transition into paper storm
place(whoosh(0.95, 250, 9000, 2.2), 3.05, 0.45)
place(sub_boom(2.5, 90, 38, 0.12), 3.97, 0.5)
place(paper_flutter(0.9, density=160, gain=0.12, hi=6000), 3.9)

# ACT 2 — the reality: paper storm
pf = paper_flutter(6.2, density=45, gain=0.055, hi=5200)
env = np.interp(tt(6.2), [0, 0.5, 5.2, 6.2], [1.0, 0.7, 0.8, 0.0])
place((pf[0] * env, pf[1] * env), 4.3)
place(pad([note(D + 12), note(D + 13), note(D + 19)], 5.8, a=2.0, r=1.2, cutoff=700, det=0.18, gain=0.14), 4.0)

# ACT 3 — thesis: scanner hum + glitches
d = 2.6
ts = tt(d)
hum = sos_filter(2 * ((ts * 110) % 1) - 1, 'bandpass', [200, 2400]) * 0.05 + np.sin(2 * np.pi * 3520 * ts) * 0.008
pan_curve = np.linspace(-0.9, 0.9, len(ts))
hum *= np.sin(np.pi * ts / d) ** 0.7
a = (pan_curve + 1) * np.pi / 4
place((hum * np.cos(a), hum * np.sin(a)), 8.1)
for k in range(18):
    place(glitch_burst(0.06 + rng.random() * 0.1, 0.05), 8.3 + k * 0.13 + rng.random() * 0.05, pan=-0.8 + k / 10)
# vortex riser
place(whoosh(1.35, 150, 12000, 1.6) * 1.1, 9.62, 0.5)
rt = tt(1.35)
rise = np.sin(2 * np.pi * np.cumsum(note(D + 24) * 2 ** (rt / 1.35 * 1.0)) / SR) * (rt / 1.35) ** 2 * 0.06
place((rise, rise), 9.62)

# ACT 4 — IMPACT: structured
place(sub_boom(4.5, 110, 30, 0.18), 10.97, 0.9)
snap = sos_filter(noise(0.4), 'bandpass', [1200, 9000]) * np.exp(-tt(0.4) * 22) * 0.35
place(snap, 10.97)
place(bell(note(D + 36), 3.0, 0.08), 10.99, pan=-0.3)
place(bell(note(D + 43), 3.0, 0.06), 10.99, pan=0.3)

# Pulse bed 11–18.5 (120 BPM); chords move with each layer
for b in range(15):
    tb = 11.0 + b * 0.5
    place(kick(0.32 if b % 2 == 0 else 0.2), tb)
for b in range(40):
    tb = 13.6 + b * 0.125
    if tb < 18.4:
        place(hat(0.035 if b % 2 else 0.05), tb, pan=0.3 if b % 2 else -0.3)
place(pad([note(D + 12), note(D + 17), note(D + 21), note(D + 24)], 2.8, a=0.4, r=0.6, cutoff=1400, gain=0.13), 11.0)    # Dm
place(pad([note(D + 8), note(D + 15), note(D + 20), note(D + 24)], 2.6, a=0.3, r=0.6, cutoff=1800, gain=0.13), 13.6)     # Bbmaj7
place(pad([note(D + 5), note(D + 12), note(D + 17), note(D + 22)], 2.6, a=0.3, r=0.5, cutoff=2200, gain=0.13), 16.1)     # Gm7
# layer marks
for tl, n in [(11.25, D + 38), (13.75, D + 41), (16.25, D + 45)]:
    place(pluck(note(n), 1.4, 0.10), tl, pan=-0.4)
# attestation: wave shimmer + four proof chimes
place(whoosh(1.6, 3000, 11000, 0.8) * 0.05, 13.6, pan=0.2)
for k, n in enumerate([D + 50, D + 53, D + 57, D + 60]):
    place(bell(note(n), 2.0, 0.07), 14.2 + k * 0.36, pan=0.5)
# agents: zips panned with motion
for k in range(12):
    dz = 0.18 + rng.random() * 0.2
    zt = tt(dz)
    f = np.linspace(1800 + rng.random() * 1500, 5000 + rng.random() * 3000, len(zt))
    z = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * zt / dz) ** 2 * 0.018
    place(z, 16.1 + k * 0.19 + rng.random() * 0.08, pan=-0.9 + rng.random() * 1.8)

# ACT 5 — city rises
place(whoosh(1.1, 120, 7000, 1.5) * 0.8, 17.45, 0.5)
place(sub_boom(4.0, 80, 34, 0.3), 18.55, 0.55)
place(pad([note(D + 3), note(D + 10), note(D + 15), note(D + 19), note(D + 22)], 6.8, a=1.2, r=1.5, cutoff=2600, gain=0.16), 18.5)   # Bbmaj9 lift
# tiles landing: soft ticks rising in pitch as floors complete
for k in range(60):
    tk = 18.9 + (k / 60) ** 1.2 * 3.0
    place(tick(0.022, 3000 + k * 45), tk, pan=-0.7 + rng.random() * 1.4)
# settlement steps: ascending plucks
for k, n in enumerate([D + 45, D + 48, D + 50, D + 52, D + 57]):
    place(pluck(note(n), 1.5, 0.14), 19.2 + k * 0.7, pan=-0.6 + k * 0.3)
    place(kick(0.18), 19.2 + k * 0.7)
for b in range(36):
    tb = 19.2 + b * 0.125
    if tb < 24.4:
        place(hat(0.03 if b % 2 else 0.045), tb, pan=0.25 if b % 2 else -0.25)
# stats counters
for k in range(30):
    place(tick(0.03, 4800 + (k % 4) * 300), 23.0 + (k / 30) ** 1.8 * 1.3, pan=-0.5 + (k % 3) * 0.5)

# ACT 6 — logo
place(whoosh(0.9, 200, 10000, 1.8) * 0.6, 24.35, 0.5)
place(sub_boom(5.0, 70, 29, 0.35), 25.22, 0.8)
place(pad([note(D + 3), note(D + 10), note(D + 15), note(D + 22), note(D + 26)], 4.8, a=0.05, r=2.6, cutoff=3000, gain=0.2), 25.22)
for k, n in enumerate([D + 51, D + 58, D + 62, D + 65]):
    place(bell(note(n), 3.5, 0.05), 25.25 + k * 0.05, pan=-0.3 + k * 0.2)
place(whoosh(1.2, 6000, 12000, 0.5) * 0.04, 26.1, pan=0.4)   # light sweep

# ------------------------------------------------------------ master
L, Rr = reverb(L, Rr, 3.6, 0.3)
# gentle glue: highpass rumble, soft clip, fade
L = sos_filter(L, 'highpass', 24); Rr = sos_filter(Rr, 'highpass', 24)
fade = np.clip(np.minimum(t_all / 0.05, (DUR - t_all) / 0.8), 0, 1)
L *= fade; Rr *= fade
peak = max(np.abs(L).max(), np.abs(Rr).max())
g = 0.95 / peak
L = np.tanh(L * g * 1.25) / np.tanh(1.25); Rr = np.tanh(Rr * g * 1.25) / np.tanh(1.25)
out = np.stack([L, Rr], axis=1) * 0.89
wavfile.write('out/score.wav', SR, (out * 32767).astype(np.int16))
rms = np.sqrt(np.mean(out ** 2))
print('peak', np.abs(out).max(), 'rms dBFS', 20 * np.log10(rms))
