"""Score + sound design for the 2-minute film, cut to the EDL in film.js.

python3 film/score.py -> film/out/score.wav (48 kHz stereo)

Arc: hype build (accelerating pulse, impacts on every headline) -> hard cut to
silence -> the crash (rain, sub drop, sparse piano) -> root cause (ostinato
tension, riser, silence, hit) -> the reveal (warm major lift, layer impacts) ->
the autonomous market (driving major pulse) -> logo sting.
"""
import numpy as np
from scipy import signal
from scipy.io import wavfile
import os

SR = 48000
DUR = 125.0
N = int(SR * DUR)
rng = np.random.default_rng(11)
L = np.zeros(N); R = np.zeros(N)
T = np.arange(N) / SR


def note(n): return 440.0 * 2 ** ((n - 69) / 12)
def tt(d): return np.arange(int(d * SR)) / SR
def noise(d): return rng.standard_normal(int(d * SR))


def filt(x, kind, f, order=2):
    wn = np.asarray(f, dtype=float) / (SR / 2)
    return signal.sosfilt(signal.butter(order, wn if wn.ndim else float(wn), btype=kind, output='sos'), x)


def place(x, t0, gain=1.0, pan=0.0):
    i0 = int(t0 * SR)
    if isinstance(x, tuple): xl, xr = x
    else:
        a = (pan + 1) * np.pi / 4; xl, xr = x * np.cos(a), x * np.sin(a)
    n = min(len(xl), N - i0)
    if n > 0: L[i0:i0 + n] += xl[:n] * gain; R[i0:i0 + n] += xr[:n] * gain


def env(n, a, r):
    e = np.ones(n); a, r = int(a * SR), int(r * SR)
    if a: e[:a] = np.linspace(0, 1, a)
    if r: e[-r:] *= np.linspace(1, 0, r)
    return e


# ------------------------------------------------------------------ instruments
def boom(d=3.0, f0=62, f1=30, drop=0.25, click=0.5):
    t = tt(d); f = f1 + (f0 - f1) * np.exp(-t / drop)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (d * 0.28)) * (1 - np.exp(-t * 400))
    c = filt(noise(d), 'bandpass', [80, 1200]) * np.exp(-t * 60) * click
    return np.tanh((body + c) * 1.6) * 0.9


def kick(g=0.5, d=0.45):
    t = tt(d); f = 45 + 95 * np.exp(-t * 35)
    return np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) * 2) * g


def hat(g=0.06, d=0.06):
    t = tt(d); return filt(noise(d), 'highpass', 8000) * np.exp(-t * 90) * g


def clap(g=0.2):
    d = 0.25; t = tt(d); x = filt(noise(d), 'bandpass', [900, 5000])
    e = sum(np.exp(-np.maximum(0, t - k * 0.011) * 60) * (t >= k * 0.011) for k in range(3)) + np.exp(-t * 18) * 0.5
    return x * e * g


def whoosh(d, f0=300, f1=8000, curve=2.0, rev=False):
    t = tt(d); x = noise(d); out = np.zeros_like(x); ch = 48; cl = len(x) // ch; zi = None
    for c in range(ch):
        u = c / (ch - 1); fc = f0 * (f1 / f0) ** (u ** curve)
        sos = signal.butter(2, [max(40, fc * .6) / (SR / 2), min(SR / 2 - 200, fc * 1.6) / (SR / 2)], btype='bandpass', output='sos')
        seg = x[c * cl:(c + 1) * cl if c < ch - 1 else len(x)]
        if zi is None: zi = signal.sosfilt_zi(sos) * 0
        y, zi = signal.sosfilt(sos, seg, zi=zi); out[c * cl:c * cl + len(y)] = y
    e = (t / d) ** 2.2 if not rev else (1 - t / d) ** 1.6
    return out * e


def pad(freqs, d, a=1.5, r=2.0, cutoff=1800, det=0.12, gain=0.12):
    t = tt(d); xl = np.zeros(len(t)); xr = np.zeros(len(t))
    for f in freqs:
        for k, dt in enumerate([-det, 0, det]):
            ph = rng.random(); ff = f * 2 ** (dt / 12); saw = 2 * ((t * ff + ph) % 1) - 1
            if k == 0: xl += saw
            elif k == 2: xr += saw
            else: xl += saw * .7; xr += saw * .7
    e = env(len(t), a, r) * gain / len(freqs)
    return filt(xl, 'lowpass', cutoff) * e, filt(xr, 'lowpass', cutoff) * e


def piano(f, d=3.0, g=0.18):
    t = tt(d)
    x = sum(a * np.sin(2 * np.pi * f * h * t * (1 + 0.0004 * h * h)) * np.exp(-t * (1.2 + h * 0.9)) for h, a in [(1, 1), (2, .5), (3, .25), (4, .12), (5, .06)])
    return x * (1 - np.exp(-t * 900)) * g


def bell(f, d=2.5, g=0.1):
    t = tt(d)
    x = sum(a * np.sin(2 * np.pi * f * p * t) * np.exp(-t * k / (d * .5)) for p, a, k in [(1, 1, 1), (2.76, .45, 1.8), (5.4, .25, 2.6), (8.93, .12, 3.5)])
    return x * (1 - np.exp(-t * 800)) * g


def pluck(f, d=1.0, g=0.15, bright=4200):
    t = tt(d); x = sum(np.sin(2 * np.pi * f * h * t) / h ** 1.2 for h in range(1, 7))
    return filt(x, 'lowpass', bright) * np.exp(-t * 5) * (1 - np.exp(-t * 1500)) * g


def bass(f, d, g=0.2):
    t = tt(d); x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t)
    return np.tanh(x * 1.5) * env(len(t), 0.01, min(0.12, d / 2)) * g


def tick(g=0.05, f=4800, d=0.03):
    t = tt(d); return np.sin(2 * np.pi * f * t) * np.exp(-t * 260) * g + filt(noise(d), 'highpass', 6000) * np.exp(-t * 400) * g * .4


def typing(t0, t1, rate=16, g=0.03):
    t = t0
    while t < t1:
        place(tick(g * (0.6 + rng.random() * .6), 2500 + rng.random() * 2500, 0.02), t, pan=rng.random() * .6 - .3)
        t += (0.5 + rng.random()) / rate


def riser(d, n0, g=0.05, oct_=1.0):
    t = tt(d); f = note(n0) * 2 ** (t / d * oct_)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.5 * np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR)
    return x * (t / d) ** 2 * g


def paper(d, density=40, g=0.06):
    xl = np.zeros(int(d * SR)); xr = np.zeros(int(d * SR))
    for _ in range(int(d * density)):
        t0 = rng.random() * d; ln = 0.03 + rng.random() * 0.14
        s = filt(noise(ln), 'bandpass', [1500 * (0.7 + rng.random() * .6), 5000 * (0.7 + rng.random() * .5)])
        ts = tt(ln); s *= (0.5 + 0.5 * np.sin(2 * np.pi * (18 + rng.random() * 30) * ts) ** 2) * np.sin(np.pi * ts / ln) ** 1.5
        a = rng.random() * np.pi / 2; i0 = int(t0 * SR); n = min(len(s), len(xl) - i0); amp = .3 + rng.random()
        xl[i0:i0 + n] += s[:n] * np.cos(a) * amp; xr[i0:i0 + n] += s[:n] * np.sin(a) * amp
    return xl * g, xr * g


def reverb(xl, xr, dur=3.2, mix=0.28):
    n = int(dur * SR); tr = np.arange(n) / SR; ev = np.exp(-tr * 6.9 / dur)
    irl = filt(rng.standard_normal(n), 'bandpass', [200, 7000]) * ev; irr = filt(rng.standard_normal(n), 'bandpass', [200, 7000]) * ev
    irl /= np.sqrt(np.sum(irl ** 2)); irr /= np.sqrt(np.sum(irr ** 2))
    return xl * (1 - mix) + signal.fftconvolve(xl, irl)[:len(xl)] * mix * 1.4, xr * (1 - mix) + signal.fftconvolve(xr, irr)[:len(xr)] * mix * 1.4


D = 38  # D1
Dm = [D + 12, D + 15, D + 19, D + 24]          # D minor
Bb = [D + 8, D + 12, D + 15, D + 20]           # Bb major
F = [D + 3, D + 10, D + 15, D + 19]            # F major
C = [D + 10, D + 14, D + 17, D + 22]           # C major
Gm = [D + 5, D + 12, D + 17, D + 20]

# ================================================================== bed
drone = np.sin(2 * np.pi * note(D) * T) * .5 + np.sin(2 * np.pi * note(D + 12) * T + .3) * .15
de = np.interp(T, [0, 2, 30.1, 30.15, 31.5, 34, 54, 79, 80.5, 82, 106, 120, 125], [0, .5, .9, 0, 0, .7, .8, 1, .2, .6, .7, .6, 0])
place((drone * de * .13, drone * de * .13), 0)
air = filt(rng.standard_normal(N), 'bandpass', [150, 900])
ae = np.interp(T, [0, 1, 30.1, 30.15, 31.5, 32.5, 125], [0, .8, .8, 0, 0, .7, .5])
place((air * ae * .018, np.roll(air, 1500) * ae * .018), 0)

# ================================================================== ACT I — the promise (0–30.2)
place(pad([note(n) for n in Dm], 5.8, a=2.5, r=1.0, cutoff=900, gain=.18), 0.0)
for k, n in enumerate([D + 36, D + 39, D + 43, D + 41]):
    place(piano(note(n), 3.0, .09), 0.9 + k * 1.1, pan=-.2 + k * .15)
typing(1.1, 3.4, rate=14, g=.02)
place(whoosh(0.8, 300, 9000, 2.2) * .35, 4.85)
# pulse accelerates: quarter kicks from 5.6, 8th hats from 9.0, 16ths from 13.8
for b in np.arange(5.6, 30.1, 0.5):
    place(kick(.36 if (b - 5.6) % 1.0 < .01 else .24), b)
    if b >= 9.0: place(clap(.07), b + .25, pan=.1)
for b in np.arange(9.0, 30.1, 0.25 if True else .5):
    if b < 13.8 and (b * 4) % 2 == 1: continue
    place(hat(.045 if (b * 4) % 2 else .06), b, pan=.3 if (b * 4) % 2 else -.3)
for b in np.arange(13.8, 30.1, 0.125):
    place(hat(.022), b, pan=.5)
# bassline (8ths) D–D–F–C pattern
for b in np.arange(5.6, 30.1, 0.5):
    bar = int((b - 5.6) // 2) % 4
    root = [D + 12, D + 12, D + 15, D + 10][bar]
    place(bass(note(root), .45, .16), b)
# chord pads every 2 bars
for k, t0 in enumerate(np.arange(5.6, 30, 4.0)):
    place(pad([note(n) for n in [Dm, Bb, F, C][k % 4]], 4.2, a=.2, r=.8, cutoff=1200 + k * 200, gain=.1), t0)
# impacts on every headline cut
for tc in [5.6, 7.3, 10.6, 12.5, 15.4, 17.0, 18.6, 26.6]:
    place(whoosh(.45, 400, 9000, 1.8) * .22, tc - .45)
    place(boom(1.6, 90, 40, .1, .7) * .45, tc)
for tc in [9.0, 13.8]:
    place(whoosh(.5, 300, 7000, 1.5) * .2, tc - .5); place(boom(1.2, 100, 45, .08) * .35, tc)
    for k in range(18): place(tick(.03, 4000 + k * 120), tc + 0.05 + (k / 18) ** 1.8 * 1.1)
# slams
for ts in [11.9, 14.9, 16.5, 18.1]:
    place(whoosh(.35, 800, 12000, 1.5, rev=False) * .3, ts - .35)
    place(boom(2.2, 70, 30, .2, 1.0) * .8, ts)
    place(filt(noise(.5), 'bandpass', [2000, 9000]) * np.exp(-tt(.5) * 14) * .25, ts)
# Fink letter: lift + softer groove
place(pad([note(n) for n in [D + 15, D + 19, D + 22, D + 27]], 8.0, a=1.0, r=1.0, cutoff=2400, gain=.14), 18.6)
for k, n in enumerate([D + 51, D + 55, D + 58, D + 62]): place(bell(note(n), 2.0, .05), 19.7 + k * .18, pan=.4)
typing(22.9, 25.0, rate=12, g=.018)
# tension ramp to the cut
place(riser(3.6, D + 24, .07, 1.0), 26.6)
place(whoosh(3.55, 200, 14000, 1.3) * .5, 26.6)
place(pad([note(n) for n in [D + 12, D + 13, D + 19]], 3.6, a=.3, r=.05, cutoff=3000, det=.25, gain=.13), 26.6)

# ================================================================== ACT II — the reality (30.2–54)
place(tick(.12, 1800, .05), 31.0)                        # the only sound in the silence
place(piano(note(D + 26), 4.0, .1), 31.8, pan=-.1)
place(piano(note(D + 21), 4.0, .08), 32.9, pan=.1)
rain = filt(rng.standard_normal(int(20 * SR)), 'bandpass', [500, 4500]) * .022
rain *= np.interp(tt(20), [0, 1.5, 18, 20], [0, 1, .8, 0]); place((rain, np.roll(rain, 900)), 34.2)
for k in range(60):                                          # droplets
    place(filt(noise(.02), 'bandpass', [2500, 6000]) * np.exp(-tt(.02) * 200) * .05 * rng.random(), 34.3 + rng.random() * 19, pan=rng.random() * 2 - 1)
place(pad([note(n) for n in [D + 12, D + 15, D + 19]], 19.0, a=3.0, r=3.0, cutoff=600, gain=.14), 34.5)
# the crash: deflating sub + reverse swell
place(whoosh(1.2, 6000, 200, .8) * .25, 36.1)
t = tt(3.0); dfl = np.sin(2 * np.pi * np.cumsum(90 * np.exp(-t * 1.2) + 25) / SR) * np.exp(-t * .9) * .5
place(np.tanh(dfl * 1.5), 37.25)
for k in range(22):                                          # counter ticks falling
    place(tick(.03, 5200 - k * 150), 36.0 + (k / 22) ** .7 * 1.25, pan=-.2)
for k, (tn, n) in enumerate([(41.3, D + 29), (42.6, D + 27), (44.0, D + 24), (45.5, D + 22), (47.6, D + 21), (49.2, D + 19)]):
    place(piano(note(n), 4.0, .09), tn, pan=-.3 + k * .1)
for k in range(8): place(tick(.025, 3500 + k * 120), 41.5 + k * .38, pan=.3)  # chart rows
for k in range(26): place(tick(.02, 1400, .04), 41.0 + k * 1.0, pan=.6)      # slow clock
place(boom(3.0, 55, 28, .4, .2) * .35, 47.6)
place(whoosh(.8, 300, 5000, 2) * .15, 50.6); place(boom(1.8, 70, 35, .15) * .3, 51.4)

# ================================================================== ACT III — the root cause (54–82)
place(boom(3.5, 60, 28, .3, .3) * .45, 54.0)
place(pad([note(n) for n in Dm], 8, a=2.0, r=2.0, cutoff=1100, gain=.13), 54.0)
# ostinato returns, 16ths, rising filter
arp = [D + 26, D + 29, D + 33, D + 36, D + 33, D + 29]
for k, tb in enumerate(np.arange(57.5, 79.0, 0.125)):
    u = (tb - 57.5) / 21.5
    place(pluck(note(arp[k % 6] + (3 if 66.5 <= tb < 73.5 and (k // 16) % 2 else 0)), .35, .045 + .04 * u, 1500 + 4000 * u), tb, pan=np.sin(k * .7) * .4)
for b in np.arange(61.5, 79.0, 0.5):
    place(kick(.2 + .12 * ((b - 61.5) / 17.5)), b)
    place(bass(note(D + 12 if int((b - 61.5) // 2) % 2 == 0 else D + 10), .45, .12), b)
for b in np.arange(66.5, 79.0, .25): place(hat(.03), b, pan=-.3)
place(paper(5.0, 45, .05), 61.5)
for k in range(14): place(tick(.04, rng.choice([700, 1400, 2800])) * (rng.random() > .3), 63.0 + k * .16 + rng.random() * .05, pan=-.6 + k * .09)
for k in range(12): place(tick(.04, 3000 + k * 90, .03), 66.9 + k * .22, pan=-.6 + k * .1)   # pills lighting
place(boom(1.5, 80, 40, .1) * .3, 69.9)                                                       # stats
for k in range(40): place(tick(.012, 6000, .015), 73.7 + k * .12, pan=-.5)                   # algo prints
place(riser(2.2, D + 24, .07, 1.0), 76.8); place(whoosh(2.2, 200, 12000, 1.4) * .4, 76.8)
# silence -> "The token was never the problem." -> HIT "The data was."
place(piano(note(D + 26), 3.0, .12), 79.3)
place(boom(4.5, 110, 28, .2, 1.0) * 1.0, 80.6)
place(filt(noise(.4), 'bandpass', [1200, 9000]) * np.exp(-tt(.4) * 20) * .3, 80.6)

# ================================================================== ACT IV — the layer (82–106)
place(pad([note(n) for n in [D + 3, D + 10, D + 15, D + 19, D + 22]], 4.0, a=.05, r=2.0, cutoff=2800, gain=.2), 82.4)
for k, n in enumerate([D + 51, D + 58, D + 62, D + 65]): place(bell(note(n), 3.0, .05), 82.45 + k * .05, pan=-.3 + k * .2)
place(boom(4, 70, 30, .3) * .6, 82.4)
typing(86.0, 89.0, rate=18, g=.02)
place(riser(1.2, D + 31, .05, 1.0), 88.3); place(whoosh(1.2, 150, 12000, 1.6) * .5, 88.3)
place(boom(4.5, 110, 30, .18, 1.0) * .9, 89.5)                                     # SNAP
for b in np.arange(89.5, 106, 0.5):
    place(kick(.3 if (b - 89.5) % 1 < .01 else .2), b)
    bar = int((b - 89.5) // 2) % 4
    place(bass(note([D + 3, D + 8, D + 12, D + 10][bar] + 12), .45, .14), b)
for b in np.arange(92.2, 106, .25): place(hat(.035 if (b * 4) % 2 else .05), b, pan=.3 if (b * 4) % 2 else -.3)
for k, t0 in enumerate(np.arange(89.5, 106, 4.0)):
    place(pad([note(n) for n in [F, Bb, Dm, C][k % 4]], 4.2, a=.2, r=.8, cutoff=1600 + k * 250, gain=.11), t0)
for tl in [92.2, 97.6]: place(boom(2, 90, 40, .12, .6) * .45, tl); place(whoosh(.5, 400, 9000) * .2, tl - .5)
place(whoosh(1.6, 3000, 11000, .8) * .05, 92.3)
for k, n in enumerate([D + 50, D + 53, D + 57, D + 60]): place(bell(note(n), 2.0, .07), 93.45 + k * .5, pan=.5)
for k in range(14):
    dz = .18 + rng.random() * .2; zt = tt(dz); f = np.linspace(1800 + rng.random() * 1500, 5000 + rng.random() * 3000, len(zt))
    place(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * zt / dz) ** 2 * .018, 97.8 + k * .3 + rng.random() * .1, pan=rng.random() * 1.8 - .9)
typing(98.7, 100.4, rate=16, g=.018)
place(whoosh(1.2, 120, 7000, 1.5) * .6, 101.4); place(boom(4, 80, 34, .3) * .55, 102.6)
place(pad([note(n) for n in [D + 3, D + 10, D + 15, D + 19, D + 22]], 3.6, a=.8, r=1.0, cutoff=2600, gain=.16), 102.6)
for k in range(50): place(tick(.018, 3000 + k * 50), 102.8 + (k / 50) ** 1.2 * 3.0, pan=rng.random() * 1.4 - .7)

# ================================================================== ACT V — the autonomous market (106–125)
for b in np.arange(106.0, 120.0, 0.5):
    place(kick(.34 if (b - 106) % 1 < .01 else .22), b)
    if (b - 106) % 1 > .4: place(clap(.07), b, pan=.1)
    bar = int((b - 106) // 2) % 4
    place(bass(note([D + 3, D + 10, D + 12, D + 8][bar] + 12), .45, .15), b)
for b in np.arange(106.0, 120.0, .125): place(hat(.02 if (b * 8) % 2 else .035), b, pan=.4 if (b * 8) % 2 else -.4)
for k, t0 in enumerate(np.arange(106, 120, 4.0)):
    place(pad([note(n) for n in [F, C, Dm, Bb][k % 4]], 4.2, a=.2, r=.8, cutoff=2400, gain=.12), t0)
arpM = [D + 39, D + 43, D + 46, D + 51, D + 46, D + 43]
for k, tb in enumerate(np.arange(110.6, 120.0, 0.125)): place(pluck(note(arpM[k % 6]), .3, .035, 5000), tb, pan=np.sin(k * .6) * .5)
typing(106.8, 109.2, rate=16, g=.02)
for k, n in enumerate([D + 45, D + 48, D + 50, D + 52, D + 57]):
    place(pluck(note(n), 1.4, .13), 111.3 + k * .95, pan=-.5 + k * .25); place(boom(1, 120, 60, .05, .3) * .15, 111.3 + k * .95)
for k in range(40): place(tick(.025, 4600 + (k % 4) * 300), 117.1 + (k / 40) ** 1.8 * 1.4, pan=-.5 + (k % 3) * .5)
place(whoosh(1.0, 200, 10000, 1.8) * .5, 119.2)
place(boom(5.0, 70, 29, .35) * .9, 120.2)
place(pad([note(n) for n in [D + 3, D + 10, D + 15, D + 22, D + 26]], 4.8, a=.05, r=3.0, cutoff=3000, gain=.22), 120.2)
for k, n in enumerate([D + 51, D + 58, D + 62, D + 65]): place(bell(note(n), 3.5, .05), 120.25 + k * .05, pan=-.3 + k * .2)

# ================================================================== master
L, R = reverb(L, R, 3.4, .26)
L = filt(L, 'highpass', 25); R = filt(R, 'highpass', 25)
# hard silence at the cut (30.15–31.0) except the reverb-free tick
cut = np.ones(N); i0, i1 = int(30.15 * SR), int(30.98 * SR); cut[i0:i1] = 0; cut[i0 - 240:i0] = np.linspace(1, 0, 240)
L *= cut; R *= cut
place(tick(.12, 1800, .05), 31.0)
fade = np.clip(np.minimum(T / .05, (DUR - T) / 1.2), 0, 1); L *= fade; R *= fade
g = .95 / max(np.abs(L).max(), np.abs(R).max())
L = np.tanh(L * g * 1.3) / np.tanh(1.3); R = np.tanh(R * g * 1.3) / np.tanh(1.3)
out = np.stack([L, R], 1) * .9
os.makedirs(os.path.join(os.path.dirname(__file__), 'out'), exist_ok=True)
wavfile.write(os.path.join(os.path.dirname(__file__), 'out', 'score.wav'), SR, (out * 32767).astype(np.int16))
print('peak', np.abs(out).max(), 'rms dBFS', 20 * np.log10(np.sqrt(np.mean(out ** 2))))
