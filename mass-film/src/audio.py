"""Score and sound design for the Mass film, synthesised from scratch and locked to
timeline.py. 48 kHz stereo. Run: python3 audio.py out.wav"""
import math
import os
import sys

import numba as nb
import numpy as np
import soundfile as sf
from scipy import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import timeline as T  # noqa: E402

FS = 48000
N = int(T.DURATION * FS)


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


NOTE = {n: i for i, n in enumerate(['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'])}


def hz(name):
    """'A2' -> Hz, 'C#4' -> Hz."""
    p, o = name[:-1], int(name[-1])
    return midi(12 * (o + 1) + NOTE[p])


# ============================================================================ DSP core
@nb.njit(cache=True)
def _svf(x, fc, q, fs, mode):
    n = x.shape[0]
    y = np.empty(n)
    ic1 = 0.0
    ic2 = 0.0
    k = 1.0 / q
    for i in range(n):
        f = fc[i]
        if f > fs * 0.45:
            f = fs * 0.45
        if f < 8.0:
            f = 8.0
        g = math.tan(math.pi * f / fs)
        a1 = 1.0 / (1.0 + g * (g + k))
        a2 = g * a1
        a3 = g * a2
        v3 = x[i] - ic2
        v1 = a1 * ic1 + a2 * v3
        v2 = ic2 + a2 * ic1 + a3 * v3
        ic1 = 2.0 * v1 - ic1
        ic2 = 2.0 * v2 - ic2
        if mode == 0:
            y[i] = v2
        elif mode == 1:
            y[i] = v1 * k
        else:
            y[i] = x[i] - k * v1 - v2
    return y


def _arr(v, n):
    return np.full(n, float(v)) if np.isscalar(v) else np.asarray(v, np.float64)


def lp(x, fc, q=0.707):
    return _svf(np.asarray(x, np.float64), _arr(fc, len(x)), q, FS, 0)


def bp(x, fc, q=1.0):
    return _svf(np.asarray(x, np.float64), _arr(fc, len(x)), q, FS, 1)


def hp(x, fc, q=0.707):
    return _svf(np.asarray(x, np.float64), _arr(fc, len(x)), q, FS, 2)


@nb.njit(cache=True)
def _saw(freq, fs, ph):
    n = freq.shape[0]
    y = np.empty(n)
    for i in range(n):
        dt = freq[i] / fs
        v = 2.0 * ph - 1.0
        if ph < dt:
            t = ph / dt
            v -= t + t - t * t - 1.0
        elif ph > 1.0 - dt:
            t = (ph - 1.0) / dt
            v -= t * t + t + t + 1.0
        y[i] = v
        ph += dt
        if ph >= 1.0:
            ph -= 1.0
    return y


def saw(freq, n=None, phase=None, seed=0):
    f = _arr(freq, n) if n is not None else np.asarray(freq, np.float64)
    ph = np.random.default_rng(seed).uniform() if phase is None else phase
    return _saw(f, FS, ph)


def sine(freq, n=None, phase=0.0):
    f = _arr(freq, n) if n is not None else np.asarray(freq, np.float64)
    return np.sin(2 * np.pi * np.cumsum(f) / FS + phase)


def tri(freq, n=None):
    f = _arr(freq, n) if n is not None else np.asarray(freq, np.float64)
    ph = np.cumsum(f) / FS
    return 2 * np.abs(2 * (ph - np.floor(ph + 0.5))) - 1


def noise(n, seed=0):
    return np.random.default_rng(seed).standard_normal(n)


def pink(n, seed=0):
    w = noise(n, seed)
    b, a = [0.049922035, -0.095993537, 0.050612699, -0.004408786], [1, -2.494956002, 2.017265875, -0.522189400]
    return signal.lfilter(b, a, w) * 4.0


def tt(n):
    return np.arange(n) / FS


def ns(sec):
    return max(1, int(round(sec * FS)))


def expdec(n, tau):
    return np.exp(-tt(n) / tau)


def ad(n, a, tau):
    t = tt(n)
    e = np.exp(-np.clip(t - a, 0, None) / tau)
    if a > 0:
        e = e * np.clip(t / a, 0, 1)
    return e


def fade(x, fin=0.003, fout=0.01):
    x = x.copy()
    a, b = ns(fin), ns(fout)
    shp = (-1,) + (1,) * (x.ndim - 1)
    if a > 1:
        x[:a] *= np.linspace(0, 1, a).reshape(shp)
    if b > 1:
        x[-b:] *= np.linspace(1, 0, b).reshape(shp)
    return x


def mix(*sigs):
    """Sum mono signals of different lengths (zero-padded)."""
    n = max(len(x) for x in sigs)
    out = np.zeros(n)
    for x in sigs:
        out[:len(x)] += x
    return out


def sat(x, drive=1.0):
    return np.tanh(x * drive) / np.tanh(drive)


def pan2(x, pan):
    a = (pan + 1) * np.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)], -1)


def db(v):
    return 10 ** (v / 20)


# ============================================================================ mix buses
BUSES = ['sfx', 'music', 'sub', 'room', 'hall', 'space', 'delay']
GROUPS = {'I': {k: np.zeros((N, 2)) for k in BUSES}, 'II': {k: np.zeros((N, 2)) for k in BUSES}}
CUR = {'g': 'I'}


def place(t, sig, gain=1.0, pan=0.0, bus='sfx', room=0.0, hall=0.0, space=0.0, delay=0.0):
    if sig.ndim == 1:
        st = pan2(sig, pan)
    else:
        st = sig
    i0 = int(round(t * FS))
    if i0 >= N:
        return
    j0 = 0
    if i0 < 0:
        j0 = -i0
        i0 = 0
    m = min(N - i0, st.shape[0] - j0)
    if m <= 0:
        return
    seg = st[j0:j0 + m] * gain
    B = GROUPS[CUR['g']]
    B[bus][i0:i0 + m] += seg
    for name, amt in (('room', room), ('hall', hall), ('space', space), ('delay', delay)):
        if amt:
            B[name][i0:i0 + m] += seg * amt


def make_ir(t60, length, seed, predelay=0.012, damp=0.45, width=1.0, er=6):
    n = ns(length)
    t = tt(n)
    rng = np.random.default_rng(seed)
    ir = np.zeros((n, 2))
    for ch in range(2):
        nz = rng.standard_normal(n)
        low = lp(nz, 400)
        high = hp(nz, 3500)
        mid = nz - low - high
        ir[:, ch] = (low * np.exp(-6.9 * t / (t60 * 1.15)) + mid * np.exp(-6.9 * t / t60) +
                     high * np.exp(-6.9 * t / (t60 * damp)))
        att = np.clip(t / 0.02, 0, 1)
        ir[:, ch] *= att
        for k in range(er):
            d = rng.uniform(0.004, 0.05)
            ir[ns(d), ch] += rng.uniform(0.2, 0.6) * rng.choice([-1, 1])
    mid = ir.mean(1, keepdims=True)
    side = (ir[:, :1] - ir[:, 1:]) / 2
    ir = np.concatenate([mid + side * width, mid - side * width], 1)
    pd = ns(predelay)
    ir = np.concatenate([np.zeros((pd, 2)), ir], 0)
    return ir / np.sqrt((ir ** 2).sum() / 2)


def convolve_bus(x, ir):
    mono = x.mean(1)
    out = np.zeros_like(x)
    for ch in range(2):
        out[:, ch] = signal.fftconvolve(mono, ir[:, ch])[:len(mono)]
    return out


def pingpong(x, time, fb=0.35, lp_fc=4500):
    out = np.zeros_like(x)
    d = ns(time)
    mono = x.mean(1)
    tap = mono.copy()
    g = 1.0
    for k in range(1, 7):
        g *= fb
        tap = lp(np.concatenate([np.zeros(d), tap[:-d]]), lp_fc)
        ch = k % 2
        out[:, ch] += tap * g / fb * 0.6
    return out


# ============================================================================ sound library
def s_tick(high=True, seed=0):
    n = ns(0.08)
    f = 2150 if high else 1780
    body = sine(f, n) * expdec(n, 0.010) + 0.5 * sine(f * 1.51, n) * expdec(n, 0.006)
    click = hp(noise(n, seed), 2500) * expdec(n, 0.0015)
    wood = bp(noise(n, seed + 1), 1100, 3) * expdec(n, 0.012)
    return fade(0.45 * body + 0.6 * click + 0.8 * wood, 0.0005, 0.01)


def s_typewriter(seed):
    rng = np.random.default_rng(seed)
    n = ns(0.28)
    tr = hp(noise(n, seed), 1800) * expdec(n, 0.0018)
    slap = bp(noise(n, seed + 3), 2400 * rng.uniform(0.9, 1.1), 1.8) * expdec(n, 0.018)
    metal = sum(sine(f * rng.uniform(0.97, 1.03), n) * expdec(n, d) * a
                for f, d, a in ((3120, 0.06, 0.12), (4470, 0.045, 0.09), (5810, 0.03, 0.07), (2290, 0.08, 0.05)))
    thump = sine(118 * rng.uniform(0.95, 1.05), n) * expdec(n, 0.03) + 0.4 * sine(236, n) * expdec(n, 0.015)
    x = 0.9 * tr + 0.7 * slap + metal + 0.55 * thump
    back = np.zeros(n)
    d = ns(rng.uniform(0.035, 0.05))
    m = n - d
    back[d:] = 0.35 * (hp(noise(m, seed + 7), 2200) * expdec(m, 0.004) + 0.3 * bp(noise(m, seed + 8), 1500, 2) * expdec(m, 0.01))
    return fade(x + back, 0.0003, 0.02)


def s_bell():
    n = ns(1.8)
    f0 = 2180
    x = sum(sine(f0 * r, n) * expdec(n, d) * a for r, d, a in ((1, 0.9, 1.0), (2.76, 0.45, 0.5), (5.40, 0.22, 0.3), (8.93, 0.1, 0.2)))
    x += hp(noise(n, 11), 3000) * expdec(n, 0.002) * 0.6
    # carriage ratchet + slide
    rat = np.zeros(n)
    for k in range(9):
        i = ns(0.09 + k * 0.024)
        m = ns(0.01)
        rat[i:i + m] += hp(noise(m, 20 + k), 2000) * expdec(m, 0.002) * 0.5
    slide = bp(noise(n, 30), 900, 0.8) * ad(n, 0.12, 0.08) * 0.25
    return fade(0.55 * x + rat + slide, 0.0005, 0.05)


def s_paper(seed=40):
    n = ns(0.45)
    rng = np.random.default_rng(seed)
    imp = np.zeros(n)
    for _ in range(90):
        i = int(rng.uniform(0, n * 0.8))
        imp[i] += rng.uniform(0.2, 1.0)
    crinkle = signal.fftconvolve(imp, expdec(ns(0.004), 0.0012))[:n]
    body = bp(noise(n, seed), 3200, 0.7) * crinkle * 3.0
    air = bp(noise(n, seed + 1), 1500, 0.6) * ad(n, 0.08, 0.15) * 0.25
    return fade(body + air, 0.002, 0.05)


def s_whoosh(dur, f0, f1, q=1.2, seed=0, shape=2.0):
    n = ns(dur)
    u = np.linspace(0, 1, n)
    fc = f0 * (f1 / f0) ** u
    x = bp(noise(n, seed), fc, q)
    env = np.sin(np.pi * u ** (1 / shape)) ** 2
    return fade(x * env, 0.002, 0.01)


def s_stamp():
    n = ns(1.6)
    t = tt(n)
    crack = hp(noise(n, 50), 900) * expdec(n, 0.004)
    f = 55 + 140 * np.exp(-t / 0.018)
    body = sine(f, n) * expdec(n, 0.16)
    slap = bp(noise(n, 51), 750, 1.1) * expdec(n, 0.05)
    boom = sat(sine(42 + 14 * np.exp(-t / 0.08), n) * expdec(n, 0.7) * 1.4, 1.5)
    rattle = sum(sine(fr, n) * expdec(n, 0.12) * 0.05 for fr in (1320, 1870, 2610))
    return fade(0.9 * crack + 1.0 * body + 0.8 * slap + 0.9 * boom + rattle, 0.0003, 0.1)


def s_fluoro(dur, seed=60):
    n = ns(dur)
    t = tt(n)
    hum = sum(sine(100 * k, n) * a for k, a in ((1, 1.0), (2, 0.45), (3, 0.25), (4, 0.12), (6, 0.06)))
    pulse = np.sign(sine(100, n)) * 0.5
    buzz = bp(pulse + 0.2 * noise(n, seed), 2600, 1.5) * 0.25
    wob = 1 + 0.15 * np.sin(2 * np.pi * 0.7 * t) + 0.08 * lp(noise(n, seed + 1), 3)
    return (hum * 0.35 + buzz) * wob


def s_zap(seed):
    n = ns(0.09)
    pulse = np.sign(sine(100, n)) + 0.6 * noise(n, seed)
    return fade(bp(pulse, 3000, 0.8) * (0.4 + 0.6 * np.abs(noise(n, seed + 1)).clip(0, 2)) * expdec(n, 0.05), 0.001, 0.02)


def s_counter_tick(seed):
    n = ns(0.03)
    x = sine(4400, n) * expdec(n, 0.004) * 0.6 + hp(noise(n, seed), 3000) * expdec(n, 0.0015)
    return fade(x, 0.0003, 0.005)


def s_chime():
    out = np.zeros(ns(3.2))
    for k, (note, t0) in enumerate((('E5', 0.0), ('C5', 0.55))):
        n = ns(2.6)
        f = hz(note)
        x = (sine(f, n) * expdec(n, 0.9) + 0.35 * sine(f * 4.0, n) * expdec(n, 0.25) +
             0.12 * sine(f * 2.0, n) * expdec(n, 0.5))
        x *= np.clip(tt(n) / 0.006, 0, 1)
        i = ns(t0)
        out[i:i + n] += x
    out = bp(out, 1400, 0.5)
    return fade(out, 0.002, 0.2)


def s_crowd(dur, seed=80):
    n = ns(dur)
    rng = np.random.default_rng(seed)
    st = np.zeros((n, 2))
    for v in range(14):
        f = rng.uniform(250, 2200)
        x = bp(noise(n, seed + v), f, rng.uniform(2, 5))
        syl = lp(np.abs(noise(n, seed + 100 + v)), rng.uniform(3, 6))
        syl = np.clip(syl - np.percentile(syl, 40), 0, None)
        x = x * syl
        st += pan2(x / (np.std(x) + 1e-9), rng.uniform(-0.8, 0.8)) * rng.uniform(0.3, 1.0)
    room = lp(pink(n, seed + 500), 700) * 0.6
    st += pan2(room, 0)
    return st / np.max(np.abs(st)) * 0.9


def s_glitch(dur=0.28, seed=90):
    n = ns(dur)
    t = tt(n)
    f = 900 * (40 / 900) ** (t / dur)
    x = saw(f, seed=seed) * 0.8 + noise(n, seed) * 0.5
    hold = 7
    x = np.repeat(x[::hold], hold)[:n]
    x = np.round(x * 6) / 6
    gate = (np.sin(2 * np.pi * 22 * t) > -0.2).astype(float)
    x = x * gate * np.linspace(1, 0.6, n)
    beeps = np.zeros(n)
    for b0 in (0.02, 0.1):
        m = ns(0.04)
        i = ns(b0)
        beeps[i:i + m] += np.sign(sine(1250, m)) * 0.35
    st = np.stack([x * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 9 * t))), x * (0.5 - 0.5 * np.sign(np.sin(2 * np.pi * 9 * t)))], -1)
    st += beeps[:, None]
    return st * 0.8


def s_drone(dur):
    n = ns(dur)
    t = tt(n)
    u = t / dur
    x = np.zeros(n)
    for k, (note, det) in enumerate((('A1', 0), ('E2', 0), ('A2', 0), ('A1', 0.07), ('A2', -0.06))):
        f = hz(note) * 2 ** (det / 12) * 2 ** (0.9 * u ** 2 / 12)
        x += saw(f, n, seed=100 + k) * (0.6 if k < 3 else 0.35)
    # a creeping minor-second clash
    x += saw(hz('A#2') * 2 ** (0.9 * u ** 2 / 12), n, seed=111) * 0.45 * np.clip((u - 0.35) / 0.4, 0, 1)
    fc = 160 + 1300 * u ** 1.8
    x = lp(x, fc, 1.1)
    high = sine(hz('A5') * (1 + 0.004 * np.sin(2 * np.pi * 5.2 * t)), n) * np.clip((u - 0.45) / 0.4, 0, 1) * 0.08
    return (x * 0.5 + high) * (0.25 + 0.75 * u ** 1.4)


def s_heartbeat(seed=0):
    n = ns(0.5)
    t = tt(n)
    lub = sine(48 + 30 * np.exp(-t / 0.03), n) * expdec(n, 0.08)
    d = ns(0.14)
    dub = np.zeros(n)
    m = n - d
    tm = tt(m)
    dub[d:] = sine(55 + 25 * np.exp(-tm / 0.025), m) * expdec(m, 0.06) * 0.75
    x = sat((lub + dub) * 1.6, 1.3)
    return fade(lp(x, 220) + 0.15 * lp(noise(n, seed), 300) * (expdec(n, 0.05)), 0.002, 0.05)


def s_cymbal(dur, seed=120):
    n = ns(dur)
    x = hp(noise(n, seed), 4500) * expdec(n, dur / 3)
    metal = sum(sine(f, n) * 0.05 for f in (5230, 6120, 7390, 8810, 9420))
    x = x + metal * expdec(n, dur / 4)
    return x


def s_reverse_swell(dur, seed=130):
    c = s_cymbal(dur * 2.2, seed)[::-1][-ns(dur):]
    n = len(c)
    u = np.linspace(0, 1, n)
    tone = lp(saw(hz('A2') * (1 + 0.5 * u ** 3), n, seed=seed) + saw(hz('E3') * (1 + 0.5 * u ** 3), n, seed=seed + 1),
              200 + 3000 * u ** 3) * u ** 3 * 0.25
    return fade(c * 0.9 + tone, 0.01, 0.005)


def s_braam(notes, dur=3.2, seed=140, bright=2600.0, decay=1.0):
    n = ns(dur)
    t = tt(n)
    x = np.zeros(n)
    for k, nm in enumerate(notes):
        f = hz(nm)
        for d in (-9, -3, 3, 9):
            x += saw(f * 2 ** (d / 1200), n, seed=seed + k * 10 + d) * (1.0 if k < 2 else 0.7)
    fc = 180 + bright * np.exp(-t / (0.5 * decay))
    x = lp(x, fc, 1.6)
    x = sat(x * 0.25, 2.2)
    env = np.clip(t / 0.02, 0, 1) * np.exp(-t / (1.3 * decay))
    return x * env


def s_sub_drop(dur=2.2, f0=58, f1=30):
    n = ns(dur)
    t = tt(n)
    f = f1 + (f0 - f1) * np.exp(-t / 0.5)
    return sat(sine(f, n) * expdec(n, dur / 3) * 1.3, 1.4)


def s_impact(seed=150, size=1.0):
    n = ns(2.5)
    t = tt(n)
    kick = sine(40 + 110 * np.exp(-t / 0.03), n) * expdec(n, 0.35 * size)
    crack = hp(noise(n, seed), 1200) * expdec(n, 0.012)
    body = bp(noise(n, seed + 1), 180, 1.2) * expdec(n, 0.12) * 1.5
    return fade(sat(kick * 1.2, 1.3) + 0.5 * crack + body, 0.0005, 0.2)


def s_kick(seed=0, dec=0.28):
    n = ns(0.5)
    t = tt(n)
    x = sine(45 + 95 * np.exp(-t / 0.028), n) * expdec(n, dec)
    click = hp(noise(n, seed), 3000) * expdec(n, 0.002) * 0.25
    return fade(sat(x * 1.3, 1.2) + click, 0.0003, 0.05)


def s_hat(seed=0, dec=0.035):
    n = ns(0.15)
    return fade(hp(noise(n, seed), 7500) * expdec(n, dec), 0.0003, 0.02)


def s_snare(seed=0, dec=0.12):
    n = ns(0.4)
    t = tt(n)
    tone = sine(190 + 40 * np.exp(-t / 0.01), n) * expdec(n, 0.06)
    nz = bp(noise(n, seed), 3500, 0.7) * expdec(n, dec)
    return fade(0.6 * tone + nz, 0.0003, 0.05)


def s_tom(f=70, seed=0):
    n = ns(1.0)
    t = tt(n)
    x = sine(f * (1 + 0.6 * np.exp(-t / 0.04)), n) * expdec(n, 0.3)
    return fade(sat(x * 1.3, 1.3) + 0.2 * bp(noise(n, seed), 600, 1) * expdec(n, 0.03), 0.0005, 0.1)


def s_pluck(f, dur=1.6, bright=1.0, seed=0):
    n = ns(dur)
    t = tt(n)
    x = saw(f, n, seed=seed) * 0.6 + saw(f * 1.004, n, seed=seed + 1) * 0.4 + 0.4 * sine(f * 2, n)
    fc = 300 + 5200 * bright * np.exp(-t / 0.09)
    x = lp(x, fc, 1.2) * np.clip(t / 0.002, 0, 1) * expdec(n, 0.45)
    return fade(x, 0.0005, 0.05)


def s_bell_tone(f, dur=2.5, seed=0):
    n = ns(dur)
    x = sum(sine(f * r, n) * expdec(n, d) * a for r, d, a in ((1, 1.2, 1.0), (2.0, 0.6, 0.35), (3.01, 0.35, 0.2), (4.16, 0.2, 0.15)))
    x = x * np.clip(tt(n) / 0.003, 0, 1)
    return fade(x, 0.0005, 0.1)


def s_ui_confirm(f, seed=0):
    n = ns(0.6)
    t = tt(n)
    a = sine(f, n) * expdec(n, 0.12) + 0.3 * sine(f * 2, n) * expdec(n, 0.05)
    b = np.zeros(n)
    d = ns(0.07)
    m = n - d
    b[d:] = sine(f * 1.5, m) * expdec(m, 0.18) + 0.25 * sine(f * 3, m) * expdec(m, 0.06)
    click = hp(noise(n, seed), 3000) * expdec(n, 0.0015) * 0.3
    return fade((a * 0.8 + b) * np.clip(t / 0.002, 0, 1) + click, 0.0003, 0.05)


def s_key_click(seed):
    n = ns(0.05)
    rng = np.random.default_rng(seed)
    x = bp(noise(n, seed), 2800 * rng.uniform(0.8, 1.2), 2) * expdec(n, 0.006) + 0.4 * sine(900, n) * expdec(n, 0.004)
    return fade(x, 0.0003, 0.01)


def s_glass_in(seed=0):
    n = ns(0.5)
    w = s_whoosh(0.22, 1500, 7000, 1.0, seed)
    x = np.zeros(n)
    x[:len(w)] += w * 0.6
    tone = (sine(hz('E6'), n) + 0.6 * sine(hz('B6'), n)) * ad(n, 0.02, 0.15) * 0.25
    return fade(x + tone, 0.002, 0.05)


def s_lock():
    n = ns(2.2)
    t = tt(n)
    out = np.zeros(n)
    for k, t0 in enumerate((0.0, 0.07)):
        m = ns(0.05)
        i = ns(t0)
        out[i:i + m] += (hp(noise(m, 170 + k), 2500) * expdec(m, 0.004) + 0.3 * sine(3200, m) * expdec(m, 0.01)) * 0.5
    i = ns(0.19)
    m = n - i
    tm = tt(m)
    latch = hp(noise(m, 180), 1500) * expdec(m, 0.006) + sum(sine(f, m) * expdec(m, 0.09) * 0.12 for f in (2410, 3890, 5120))
    thunk = sine(70 + 120 * np.exp(-tm / 0.02), m) * expdec(m, 0.12)
    boom = sat(sine(38 + 10 * np.exp(-tm / 0.1), m) * expdec(m, 0.8) * 1.3, 1.4)
    out[i:] += latch * 0.9 + thunk * 0.9 + boom * 0.8
    return fade(out, 0.0003, 0.1)


def s_ship_horn(dur=2.6):
    n = ns(dur)
    t = tt(n)
    env = np.clip(t / 0.3, 0, 1) ** 1.5 * np.clip((dur - t) / 0.9, 0, 1)
    wob = 1 + 0.003 * np.sin(2 * np.pi * 3.1 * t) + 0.002 * lp(noise(n, 190), 4)
    x = saw(hz('G2') * wob, n, seed=191) + 0.6 * saw(hz('D3') * wob * 1.002, n, seed=192)
    x = lp(x, 900, 1.4)
    x = bp(x, 400, 0.5) * 0.6 + lp(x, 250) * 0.8
    return sat(x * env * 0.8, 1.3)


def s_chirp(seed=0):
    n = ns(0.12)
    u = np.linspace(0, 1, n)
    f = 1400 * (3.2 ** u)
    x = sine(f, n) * np.sin(np.pi * u) ** 2 * 0.5 + hp(noise(n, seed), 4000) * expdec(n, 0.003) * 0.3
    return fade(x, 0.001, 0.01)


def s_space_boom():
    n = ns(4.5)
    t = tt(n)
    sub = sat(sine(34 + 20 * np.exp(-t / 0.15), n) * expdec(n, 1.3) * 1.3, 1.4)
    air = lp(noise(n, 200), 900 * np.exp(-t / 0.6) + 120) * expdec(n, 0.9) * 0.5
    body = sine(70 * (1 + 0.5 * np.exp(-t / 0.05)), n) * expdec(n, 0.4) * 0.6
    return fade(sub + air + body, 0.001, 0.3)


def s_sonar(f=hz('A4')):
    n = ns(3.0)
    t = tt(n)
    x = sine(f, n) * expdec(n, 0.7) + 0.3 * sine(f * 2.0, n) * expdec(n, 0.3) + 0.2 * sine(f * 0.5, n) * expdec(n, 1.0)
    return fade(x * np.clip(t / 0.004, 0, 1), 0.0005, 0.2)


def s_riser(dur, seed=210):
    n = ns(dur)
    u = np.linspace(0, 1, n)
    nz = hp(noise(n, seed), 400 + 6000 * u ** 2) * u ** 2.2
    tone = lp(saw(hz('G2') * 2 ** (u ** 2 * 12 / 12), n, seed=seed) + saw(hz('D3') * 2 ** (u ** 2), n, seed=seed + 1),
              300 + 5000 * u ** 2, 1.5) * u ** 2 * 0.4
    return nz * 0.6 + tone


def s_pad(notes, dur, seed=0, fc=1400, attack=0.6, release=0.8, detune=7):
    n = ns(dur)
    t = tt(n)
    x = np.zeros(n)
    for k, nm in enumerate(notes):
        f = hz(nm)
        for d in (-detune, 0, detune):
            x += saw(f * 2 ** (d / 1200), n, seed=seed + k * 7 + d)
    x = lp(x, fc, 0.8)
    env = np.clip(t / attack, 0, 1) * np.clip((dur - t) / release, 0, 1)
    return x * env / (len(notes) * 3) * 2.2


def s_bass_note(f, dur, seed=0, accent=1.0):
    n = ns(dur)
    t = tt(n)
    x = saw(f, n, seed=seed) + 0.5 * sine(f / 2, n)
    fc = 180 + 1400 * accent * np.exp(-t / 0.05)
    x = lp(x, fc, 1.3) * np.exp(-t / 0.11)
    return fade(sat(x * 0.9, 1.2), 0.001, 0.008)


# ============================================================================ the score
CHORDS = [  # (start, end, chord tones low->high, bass)
    (9.5, 13.5, ['A2', 'C3', 'E3', 'A3'], 'A1'),
    (13.5, 15.5, ['F2', 'A2', 'C3', 'F3'], 'F1'),
    (15.5, 17.5, ['G2', 'B2', 'D3', 'G3'], 'G1'),
    (17.5, 19.5, ['A2', 'E3', 'A3', 'C4'], 'A1'),
    (19.5, 21.5, ['F2', 'C3', 'F3', 'A3'], 'F1'),
    (21.5, 22.5, ['C3', 'E3', 'G3', 'C4'], 'C2'),
    (22.5, 23.5, ['G2', 'D3', 'G3', 'B3'], 'G1'),
    (23.5, 25.5, ['E2', 'B2', 'E3', 'G#3'], 'E1'),
]


def chord_at(t):
    for a, b, notes, bass in CHORDS:
        if a <= t < b:
            return notes, bass
    return CHORDS[-1][2], CHORDS[-1][3]


def node_pans():
    """Screen-space pan of each node at the moment it ignites (from the actual camera)."""
    try:
        import shots
        import globe as G
        out = {}
        for name, la, lo, ti, _ in T.NODES:
            u = (ti - T.S10[0]) / (T.S10[1] - T.S10[0])
            cam = shots.earth_cam(u)
            pr = cam.project(G.ll_to_vec(la, lo) * 1.002)
            out[name] = 0.0 if pr is None else float(np.clip((pr[0] / 1920 - 0.5) * 1.6, -0.9, 0.9))
        u = (T.HUB_IGNITE - T.S10[0]) / (T.S10[1] - T.S10[0])
        pr = shots.earth_cam(u).project(G.ll_to_vec(T.HUB[1], T.HUB[2]) * 1.002)
        out[T.HUB[0]] = 0.0 if pr is None else float(np.clip((pr[0] / 1920 - 0.5) * 1.6, -0.9, 0.9))
        return out
    except Exception as e:  # pragma: no cover
        print('pan fallback:', e)
        return {n[0]: float(np.clip((n[2] - 60) / 60, -0.9, 0.9)) for n in T.NODES} | {T.HUB[0]: 0.0}


def build():
    # ---------------------------------------------------------------- ACT I
    CUR['g'] = 'I'
    place(0.0, lp(pink(ns(8.05), 1), 900) * 0.02, bus='sfx')                    # room tone
    drone = s_drone(8.05 - 0.2)
    place(0.2, fade(drone, 0.5, 0.004), gain=0.34, bus='music', hall=0.25)
    k = 0
    tk = 0.0
    while tk < 8.0:
        g = 0.22 + 0.12 * (tk / 8.0)
        place(tk, s_tick(k % 2 == 0, k), gain=g, pan=-0.15, room=0.35)
        k += 1
        tk += T.BEAT
    for times, seed0, lane_pan in ((T.LINE1_T, 300, 0.0), (T.LINE2_T, 320, 0.05), (T.LINE3_T, 340, 0.0), (T.LINE4_T, 360, 0.05)):
        for j, tw in enumerate(times):
            place(tw - 0.004, s_typewriter(seed0 + j), gain=0.62, pan=lane_pan + 0.12 * ((j % 3) - 1), room=0.25)
    place(T.BELL, s_bell(), gain=0.45, pan=0.35, room=0.4)
    place(T.PAPER_RUSTLE, s_paper(), gain=0.5, pan=-0.1, room=0.2)
    place(T.STAMP - 0.13, s_whoosh(0.13, 400, 2500, 1.0, 55), gain=0.35, room=0.1)
    place(T.STAMP, s_stamp(), gain=1.0, room=0.45, hall=0.15)
    # waiting room
    place(T.S3[0], fade(s_fluoro(T.S3[1] - T.S3[0], 60), 0.02, 0.01), gain=0.16, pan=0.1, room=0.3)
    for tf in (4.93, 5.62, 5.70):
        place(tf, s_zap(int(tf * 100)), gain=0.3, pan=0.2, room=0.3)
    last, prev = -1.0, 0
    tc = T.COUNTER[0]
    while tc <= T.COUNTER[1]:
        u = (tc - T.COUNTER[0]) / (T.COUNTER[1] - T.COUNTER[0])
        v = 1 + int(round((T.COUNTER_MAX - 1) * u ** 2.2))
        if v != prev and tc - last >= 0.028:
            place(tc, s_counter_tick(int(tc * 1000)), gain=0.20 + 0.1 * u, pan=-0.55, room=0.15)
            last, prev = tc, v
        tc += 1 / 480
    # customs
    place(T.S4[0], fade(s_crowd(T.S4[1] - T.S4[0]), 0.08, 0.004), gain=0.2, room=0.3, hall=0.2)
    place(T.CHIME, s_chime(), gain=0.3, pan=0.25, hall=0.6)
    place(T.RESET, s_glitch(), gain=0.55, room=0.1)
    place(T.RESET, s_sub_drop(0.6, 70, 35), gain=0.5, bus='sub')
    # silence, heartbeats, the suck into the reveal (not gated)
    CUR['g'] = 'II'
    for hb in T.HEARTBEATS:
        place(hb, s_heartbeat(int(hb * 10)), gain=0.72, bus='sub', room=0.2)
    place(9.47 - 0.72, s_reverse_swell(0.72), gain=0.5, hall=0.2)

    # ---------------------------------------------------------------- ACT II
    t0 = T.REVEAL
    place(t0, s_braam(['A1', 'E2', 'A2', 'C3', 'E3'], 3.4), gain=0.72, bus='music', hall=0.45)
    place(t0, s_sub_drop(2.4, 62, 30), gain=0.85, bus='sub')
    place(t0, s_impact(151, 1.3), gain=0.6, hall=0.3)
    place(t0, s_cymbal(3.0, 152), gain=0.18, hall=0.4)
    shimmer = sum(s_bell_tone(hz(nm), 3.0, k) * a for k, (nm, a) in enumerate((('A6', 0.5), ('E7', 0.3), ('C7', 0.25))))
    place(t0 + 0.12, shimmer, gain=0.06, pan=0.2, hall=0.8, delay=0.3)
    for k, ts in enumerate(T.MARK_STROKES):
        place(ts, s_whoosh(0.16, 1800, 9000, 1.4, 160 + k), gain=0.22, pan=-0.3 + 0.3 * k, hall=0.2)
    place(t0 + 0.62, s_whoosh(0.7, 3000, 12000, 2.0, 165), gain=0.12, pan=0.3, hall=0.4)
    place(t0 + 0.64, s_bell_tone(hz('E6'), 2.0, 3), gain=0.05, pan=0.3, hall=0.6)
    # fly-through
    fl0, fl1 = T.FLYTHROUGH
    place(fl0 - 0.25, s_whoosh(fl1 - fl0 + 0.25, 200, 7000, 0.9, 170, 1.2), gain=0.55, hall=0.15)
    place(fl0 - 0.25, s_riser(fl1 - fl0 + 0.25, 171), gain=0.25, bus='music')
    place(fl1, s_impact(172, 0.8), gain=0.45, room=0.2)
    # driving section 11.5 -> 17.5
    for i in range(int((17.5 - 11.5) / T.BEAT)):
        tb = 11.5 + i * T.BEAT
        place(tb, s_kick(400 + i), gain=0.55, bus='sub')
        if tb >= 13.5:
            place(tb + T.BEAT / 2, s_hat(500 + i), gain=0.12, pan=0.25)
            place(tb + T.BEAT * 0.75, s_hat(600 + i, 0.02), gain=0.06, pan=-0.2)
        if tb >= 15.5 and i % 2 == 1:
            place(tb, s_snare(700 + i), gain=0.22, room=0.4)
    tq = 11.5
    k = 0
    pattern = [1.0, 0.45, 0.7, 0.45]
    octave = [0, 0, 12, 0, 0, 0, 12, 7]
    while tq < 17.5 - 1e-6:
        notes, bass = chord_at(tq)
        f = hz(bass) * 2 ** (octave[k % 8] / 12)
        place(tq, s_bass_note(f, 0.125, 800 + k, pattern[k % 4]), gain=0.19 + 0.05 * ((tq - 11.5) / 6), bus='music')
        k += 1
        tq += T.BEAT / 4
    for a, b, notes, bass in CHORDS:
        if a >= 11.5 and b <= 17.5:
            place(a, s_pad(notes, b - a + 0.8, int(a * 10), 1500), gain=0.09 + 0.03 * ((a - 11.5) / 6), bus='music', hall=0.4)
    # arpeggio shimmer 13.5 -> 17.5
    tq = 13.5
    k = 0
    while tq < 17.5 - 1e-6:
        notes, _ = chord_at(tq)
        nm = notes[[0, 1, 2, 3, 2, 1][k % 6]]
        f = hz(nm) * 4
        place(tq, s_pluck(f, 0.6, 0.6, 900 + k), gain=0.045, pan=0.35 * math.sin(k * 0.9), bus='music', delay=0.5)
        k += 1
        tq += T.BEAT / 4
    # agent UI
    place(T.S7_CUT, s_glass_in(220), gain=0.35, pan=0.35, hall=0.2)
    rng = np.random.default_rng(5)
    tkc = T.AGENT_TYPE[0]
    while tkc < T.AGENT_TYPE[1]:
        place(tkc, s_key_click(int(tkc * 1000)), gain=0.25, pan=0.3, room=0.2)
        tkc += rng.uniform(0.022, 0.045)
    for k, (tc_, nm) in enumerate(zip(T.CHECKS, ['E5', 'A5', 'C6', 'E6'])):
        place(tc_, s_ui_confirm(hz(nm), 230 + k), gain=0.32, pan=0.35, hall=0.35, delay=0.2)
    # layers + keys
    for k, (tl_, nm) in enumerate(zip(T.LAYERS, ['F5', 'A5', 'C6', 'F6', 'A6', 'C7'])):
        place(tl_ + 0.18, mix(s_bell_tone(hz(nm), 1.2, 240 + k) * 0.6, s_key_click(250 + k)), gain=0.18, pan=0.45, hall=0.35)
    place(T.KEY_LOCK - 0.19, s_lock(), gain=0.8, pan=0.3, room=0.3, hall=0.2)
    # trade
    place(T.SHIP_HORN - 0.05, s_ship_horn(2.8), gain=0.5, pan=-0.2, space=0.5, hall=0.3)
    for k, tg in enumerate(T.TAGS):
        place(tg, s_chirp(260 + k), gain=0.2, pan=0.1 + 0.25 * k, hall=0.2)
        place(tg + 0.3, s_ui_confirm(hz(['B5', 'D6', 'G6'][k]), 270 + k), gain=0.18, pan=0.1 + 0.25 * k, hall=0.3, delay=0.2)

    # ---------------------------------------------------------------- ACT III
    place(17.5 - 0.35, s_whoosh(0.35, 300, 5000, 0.8, 280, 1.3), gain=0.4, hall=0.2)
    place(17.5, s_space_boom(), gain=0.9, bus='sub', space=0.3)
    place(17.5, s_cymbal(4.0, 281), gain=0.14, space=0.6)
    for a, b, notes, bass in CHORDS:
        if a >= 17.5 and b <= 23.5:
            place(a, s_pad(notes + [notes[-1][:-1] + str(int(notes[-1][-1]) + 1)], b - a + 1.0, int(a * 10), 2400, 0.9, 1.0, 9),
                  gain=0.14, bus='music', space=0.5)
            place(a, s_pad([bass, bass[:-1] + str(int(bass[-1]) + 1)], b - a + 0.5, int(a * 10) + 3, 500, 0.3, 0.6, 4),
                  gain=0.10, bus='music')
    for i in range(int((21.5 - 17.5) / 1.0)):
        tb = 17.5 + i * 1.0
        place(tb, s_kick(420 + i, 0.4), gain=0.4, bus='sub')
        place(tb + 0.5, s_tom(62, 430 + i), gain=0.22, bus='sub', hall=0.3)
    pans = node_pans()
    place(T.HUB_IGNITE, s_sonar(hz('A4')), gain=0.28, pan=pans.get(T.HUB[0], 0.0), space=0.7, delay=0.4)
    place(T.HUB_IGNITE, s_sonar(hz('A2')), gain=0.2, pan=pans.get(T.HUB[0], 0.0), space=0.6)
    for k, (name, la, lo, ti, _) in enumerate(T.NODES):
        notes, _ = chord_at(ti)
        nm = notes[k % len(notes)]
        f = hz(nm) * (4 if k % 2 == 0 else 2)
        p = pans.get(name, 0.0)
        place(ti, s_pluck(f, 1.8, 0.9, 1000 + k), gain=0.13, pan=p, bus='music', space=0.45, delay=0.45)
        place(ti, s_bell_tone(f * 2, 1.4, 1100 + k), gain=0.035, pan=p, space=0.5)
        place(ti - T.ARC_TRAVEL, s_whoosh(T.ARC_TRAVEL, 800, 5000, 1.5, 1200 + k), gain=0.07, pan=p * 0.6, space=0.4)
    for k, (a_, b_, tm) in enumerate(T.MESH):
        notes, _ = chord_at(tm)
        place(tm + 0.5, s_pluck(hz(notes[(k + 2) % len(notes)]) * 4, 1.2, 0.6, 1300 + k), gain=0.06,
              pan=0.6 * math.sin(k * 1.3), bus='music', space=0.5, delay=0.5)
    # build 21.5 -> 23.5
    for i in range(4):
        tb = 21.5 + i * T.BEAT
        place(tb, s_kick(440 + i), gain=0.5, bus='sub')
    tr_ = 21.5
    k = 0
    while tr_ < 23.45:
        u = (tr_ - 21.5) / 2.0
        place(tr_, s_snare(460 + k, 0.08), gain=0.06 + 0.22 * u ** 1.5, room=0.3, pan=0.1 * math.sin(k))
        step = T.BEAT / 2 if u < 0.5 else (T.BEAT / 4 if u < 0.8 else T.BEAT / 8)
        tr_ += step
        k += 1
    place(T.RISER[0], fade(s_riser(T.RISER[1] - T.RISER[0] - 0.03), 0.3, 0.004), gain=0.42, bus='music', hall=0.2)
    for i in range(4):
        tb = 22.5 + i * T.BEAT
        place(tb, s_kick(470 + i), gain=0.45, bus='sub')

    # ---------------------------------------------------------------- montage
    stab = ['E2', 'B2', 'E3', 'G#3']
    for k, tm in enumerate(T.MONTAGE):
        place(tm, s_impact(500 + k, 1.0), gain=0.9, hall=0.25)
        place(tm, s_braam(stab, 0.6, 510 + k, 3000, 0.25), gain=0.45, bus='music', hall=0.3)
        place(tm, s_tom(55 + 6 * k, 520 + k), gain=0.4, bus='sub', hall=0.2)
        place(tm, s_whoosh(0.12, 5000, 1200, 1.0, 530 + k), gain=0.18, pan=0.4 * (-1) ** k)
    place(T.MONTAGE[0], s_cymbal(2.0, 540), gain=0.22, hall=0.4)
    place(T.FINAL_HIT - 0.55, s_reverse_swell(0.53, 541), gain=0.45, hall=0.2)

    # ---------------------------------------------------------------- final
    tf = T.FINAL_HIT
    place(tf, s_braam(['A1', 'E2', 'A2', 'C#3', 'E3', 'A3'], 4.5, 600, 3200, 1.8), gain=0.65, bus='music', space=0.6)
    place(tf, s_pad(['A2', 'E3', 'A3', 'C#4', 'E4', 'A4'], 4.5, 610, 3000, 0.02, 3.4, 8), gain=0.3, bus='music', space=0.7)
    place(tf, s_sub_drop(3.5, 55, 28), gain=0.9, bus='sub')
    place(tf, s_impact(620, 1.5), gain=0.7, space=0.4)
    place(tf, s_cymbal(4.0, 621), gain=0.2, space=0.7)
    for k, (nm, a) in enumerate((('A5', 0.5), ('E6', 0.35), ('C#7', 0.25), ('A6', 0.3))):
        place(tf + 0.05 + k * 0.11, s_bell_tone(hz(nm), 3.5, 630 + k), gain=0.09 * a / 0.5, pan=0.5 * math.sin(k * 2.1),
              space=0.8, delay=0.35)
    place(tf + 0.7, s_whoosh(0.7, 4000, 14000, 2.0, 640), gain=0.08, pan=0.2, space=0.5)
    place(tf + 0.72, s_bell_tone(hz('E7'), 2.0, 641), gain=0.04, pan=0.3, space=0.7)
    place(T.URL_IN, s_bell_tone(hz('A6'), 1.5, 650), gain=0.025, space=0.6)


def duck_env():
    """Sidechain envelope for the music bus from the kicks and impacts."""
    env = np.ones(N)
    hits = [11.5 + i * T.BEAT for i in range(12)] + [17.5 + i for i in range(4)] + \
           [21.5 + i * T.BEAT for i in range(8)] + list(T.MONTAGE) + [T.STAMP, T.REVEAL, T.FINAL_HIT]
    for h in hits:
        i = int(h * FS)
        m = min(N - i, ns(0.35))
        e = 1 - 0.45 * np.exp(-tt(m) / 0.12)
        env[i:i + m] = np.minimum(env[i:i + m], e)
    return lp(env, 40)


@nb.njit(cache=True)
def _limiter(x, ceiling, look, rel):
    n = x.shape[0]
    pk = np.empty(n)
    for i in range(n):
        pk[i] = max(abs(x[i, 0]), abs(x[i, 1]))
    # running max over the lookahead window
    need = np.empty(n)
    for i in range(n):
        m = 0.0
        for j in range(i, min(n, i + look)):
            if pk[j] > m:
                m = pk[j]
        need[i] = min(1.0, ceiling / m) if m > 0 else 1.0
    g = np.empty(n)
    cur = 1.0
    for i in range(n):
        if need[i] < cur:
            cur = need[i]
        else:
            cur = cur + (need[i] - cur) * rel
        g[i] = cur
    y = np.empty_like(x)
    for i in range(n):
        y[i, 0] = x[i, 0] * g[i]
        y[i, 1] = x[i, 1] * g[i]
    return y


def glue(x, thr_db=-16, ratio=2.0, att=0.01, rel=0.15):
    lvl = np.sqrt(lp((x ** 2).mean(1), 1 / (2 * np.pi * rel)).clip(1e-12, None))
    over = 20 * np.log10(lvl) - thr_db
    gr = np.where(over > 0, -over * (1 - 1 / ratio), 0.0)
    return x * db(lp(gr, 1 / (2 * np.pi * att)))[:, None]


def render_group(Bg, irs, duck):
    ir_room, ir_hall, ir_space = irs
    room = convolve_bus(Bg['room'], ir_room)
    hall = convolve_bus(Bg['hall'], ir_hall)
    space = convolve_bus(Bg['space'], ir_space)
    dly = pingpong(Bg['delay'], T.BEAT * 0.75, 0.38)
    music = Bg['music'] * duck[:, None]
    sub = Bg['sub'].copy()
    for ch in range(2):
        sub[:, ch] = hp(sub[:, ch], 26)
        music[:, ch] = hp(music[:, ch], 30)
    return Bg['sfx'] + music * 0.9 + sub + room * 0.28 + hall * 0.24 + space * 0.22 + dly * 0.25


def act1_gate():
    g = np.ones(N)
    i = int(T.S5[0] * FS)
    m = ns(0.008)
    g[i:i + m] = np.linspace(1, 0, m)
    g[i + m:] = 0
    return g


def master(out_path, target=-15.0):
    build()
    irs = (make_ir(0.6, 1.2, 1, 0.006, 0.4, 0.8), make_ir(2.4, 4.0, 2, 0.018, 0.45, 1.0), make_ir(5.5, 8.0, 3, 0.04, 0.35, 1.2))
    duck = duck_env()
    mix = render_group(GROUPS['I'], irs, duck) * act1_gate()[:, None] + render_group(GROUPS['II'], irs, duck)
    for ch in range(2):
        mix[:, ch] = hp(mix[:, ch], 22)
    mix = glue(mix, -14, 1.5)
    import pyloudnorm as pyln
    meter = pyln.Meter(FS)
    g = db(target - meter.integrated_loudness(mix))
    rel = 1 - math.exp(-1 / (0.08 * FS))
    for _ in range(3):
        out = _limiter(mix * g, db(-1.5), ns(0.004), rel)
        g *= db(target - meter.integrated_loudness(out))
    out = _limiter(mix * g, db(-1.5), ns(0.004), rel)
    up = signal.resample_poly(out, 4, 1, axis=0)
    tp = np.max(np.abs(up))
    if tp > db(-1.0):
        out = out * db(-1.0) / tp
    m = ns(0.35)
    out[-m:] *= np.linspace(1, 0, m)[:, None]
    sf.write(out_path, out.astype(np.float32), FS, subtype='PCM_24')
    print(f'integrated loudness: {meter.integrated_loudness(out):.1f} LUFS, '
          f'true peak ~ {20 * np.log10(np.max(np.abs(signal.resample_poly(out, 4, 1, axis=0)))):.1f} dBTP')
    return out


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                             'out', 'mass_score.wav')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    master(out)
    print('wrote', out)
