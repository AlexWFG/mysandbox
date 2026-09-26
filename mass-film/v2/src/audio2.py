"""Score, sound design and narration mix for the 2-minute film. Every cue is read from the
same narration timeline as the picture (shots2), so a new voice take re-times the sound too.
Run: python3 audio2.py [out.wav]   (MASS_VO=final for the ElevenLabs take)."""
import json
import math
import os
import sys

import numpy as np
import soundfile as sf
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), 'src'))
import audio as A  # noqa: E402  (v1 DSP core + sound library)
from audio import (FS, hz, lp, bp, hp, saw, sine, tri, noise, pink, tt, ns, expdec, ad, fade, sat, pan2, db,  # noqa: E402
                   make_ir, convolve_bus, pingpong, s_tick, s_stamp, s_whoosh, s_fluoro, s_zap, s_counter_tick,
                   s_chime, s_crowd, s_glitch, s_cymbal, s_reverse_swell, s_sub_drop, s_kick, s_hat, s_snare, s_tom,
                   s_pluck, s_bell_tone, s_ui_confirm, s_key_click, s_glass_in, s_lock, s_ship_horn, s_chirp,
                   s_sonar, s_riser, s_pad, s_bass_note, s_heartbeat, s_paper)
import shots2 as S  # noqa: E402

L = S.L
V2 = os.path.dirname(HERE)
DUR = S.DUR
N = int(DUR * FS) + FS
BEAT = 0.6            # 100 bpm
BUSES = ['sfx', 'music', 'sub', 'room', 'hall', 'space', 'delay', 'vo']
BED_DB = -12.0        # the whole bed relative to the narration
B = {k: np.zeros((N, 2)) for k in BUSES}


def place(t, sig, gain=1.0, pan=0.0, bus='sfx', room=0.0, hall=0.0, space=0.0, delay=0.0):
    st = pan2(sig, pan) if sig.ndim == 1 else sig
    i0 = int(round(t * FS))
    j0 = 0
    if i0 < 0:
        j0, i0 = -i0, 0
    m = min(N - i0, st.shape[0] - j0)
    if m <= 0:
        return
    seg = st[j0:j0 + m] * gain
    B[bus][i0:i0 + m] += seg
    for name, amt in (('room', room), ('hall', hall), ('space', space), ('delay', delay)):
        if amt:
            B[name][i0:i0 + m] += seg * amt


# ============================================================================ new sounds
def s_click(f=2400, seed=0):
    n = ns(0.03)
    x = sine(f, n) * expdec(n, 0.004) + 0.4 * hp(noise(n, seed), 3000) * expdec(n, 0.0015)
    return fade(x, 0.0002, 0.005)


def s_bloom(notes, dur=5.0, seed=0, peak=5200.0, open_t=1.1):
    """A chord that opens from dark to bright and hangs (the sonic logo body)."""
    n = ns(dur)
    t = tt(n)
    out = np.zeros((n, 2))
    for k, nm in enumerate(notes):
        f = hz(nm)
        for d, pn in ((-6, -0.6), (0, 0.0), (6, 0.6)):
            v = saw(f * 2 ** (d / 1200), n, seed=seed + k * 11 + d) * 0.6 + tri(f * 2 ** (d / 1200), n) * 0.5
            out += pan2(v, pn * (0.4 + 0.1 * k)) * (1.0 if k < 3 else 0.7)
    u = np.clip(t / open_t, 0, 1)
    fc = 260 + peak * (1 - (1 - u) ** 3) * np.exp(-np.clip(t - open_t, 0, None) / 2.2)
    for ch in range(2):
        out[:, ch] = lp(out[:, ch], fc, 0.9)
    env = np.clip(t / 0.015, 0, 1) * (0.55 + 0.45 * np.exp(-t / 0.35)) * np.clip((dur - t) / (dur * 0.7), 0, 1) ** 1.5
    return out * env[:, None] / (len(notes) * 2.2)


def s_boom(dur=3.0, f0=62, f1=30, seed=0):
    n = ns(dur)
    t = tt(n)
    f = f1 + (f0 - f1) * np.exp(-t / 0.35)
    body = sine(f, n) * expdec(n, dur / 3.2)
    thump = sine(90 * np.exp(-t / 0.05) + 45, n) * expdec(n, 0.12) * 0.7
    air = lp(noise(n, seed), 700 * np.exp(-t / 0.4) + 90) * expdec(n, 0.6) * 0.35
    return fade(body * 1.1 + thump + air, 0.0008, 0.3)


def s_sting(t0, big=False):
    """Sonic logo: three precise clicks as the mark assembles, then a warm boom and a blooming chord."""
    place(t0 - 0.85, fade(s_reverse_swell(0.85, 700 + big), 0.2, 0.003), gain=0.42, hall=0.2)
    place(t0 - 0.6, fade(s_riser(0.6, 701 + big), 0.2, 0.003), gain=0.18, bus='music')
    for k, dt in enumerate((0.0, 0.08, 0.16)):
        place(t0 + dt, s_click(2200 + 400 * k, 710 + k), gain=0.35, pan=-0.35 + 0.35 * k, hall=0.25, delay=0.15)
    place(t0 + 0.16, s_boom(3.6 if big else 3.0, 64, 30, 720), gain=1.0, bus='sub')
    place(t0 + 0.16, s_bloom(['A1', 'E2', 'A2', 'C#3', 'E3', 'B3'], 6.5 if big else 4.6, 730, 5600 if big else 4800),
          gain=1.15 if big else 1.0, bus='music', hall=0.35, space=0.3)
    place(t0 + 0.16, hp(noise(ns(0.02), 740), 2500) * expdec(ns(0.02), 0.004), gain=0.5, hall=0.4)
    place(t0 + 0.16, s_cymbal(3.5 if big else 2.6, 741), gain=0.09, hall=0.5, space=0.3)
    for k, (nm, a) in enumerate((('A5', 0.5), ('E6', 0.4), ('C#7', 0.25), ('B6', 0.25))):
        place(t0 + 0.3 + k * 0.07, s_bell_tone(hz(nm), 3.2 if big else 2.4, 750 + k), gain=0.06 * a / 0.5,
              pan=0.5 * math.sin(k * 2.1), space=0.8, delay=0.4)
    place(t0 + 0.42, s_whoosh(0.9, 2600, 11000, 1.8, 760), gain=0.10, pan=0.25, hall=0.4)


def s_metal(seed=0, dur=1.2):
    n = ns(dur)
    x = np.zeros(n)
    for k, (f, d) in enumerate(((523, 0.5), (1371, 0.35), (2211, 0.25), (3127, 0.18), (4390, 0.12))):
        x += sine(f * (1 + 0.002 * k), n) * expdec(n, d) * (0.5 / (k + 1) ** 0.5)
    return fade(x * np.clip(tt(n) / 0.001, 0, 1), 0.0002, 0.2)


def s_hit(k, stab, seed=0):
    """One of the four closing hits: sucked in, landed with weight, pitched up the chord each time."""
    size = 1.0 + 0.18 * k
    n = ns(2.4)
    t = tt(n)
    sub = sine(42 + 70 * np.exp(-t / 0.04), n) * expdec(n, 0.45 * size)
    body = sine(105 * (1 + 0.6 * np.exp(-t / 0.02)), n) * expdec(n, 0.14) * 0.8
    snap = hp(noise(n, seed), 1800) * expdec(n, 0.009) * 0.35
    thud = bp(noise(n, seed + 1), 240, 1.1) * expdec(n, 0.08) * 0.6
    x = sat(sub * 1.15 + body + snap + thud, 1.2)
    x = lp(x, 260) + 0.55 * (x - lp(x, 260))          # keep the weight, leave room for the word
    place_t = None  # noqa: F841
    # brass-like stab through the chord, short and clean
    m = ns(1.6)
    tm = tt(m)
    st = np.zeros(m)
    for j, nm in enumerate(stab):
        for d in (-7, 0, 7):
            st += saw(hz(nm) * 2 ** (d / 1200), m, seed=seed + 20 + j * 5 + d)
    fc = 250 + (2600 + 500 * k) * np.exp(-tm / 0.22)
    st = lp(st, fc, 1.2) * np.clip(tm / 0.006, 0, 1) * np.exp(-tm / (0.55 + 0.1 * k)) / (len(stab) * 3) * 1.8
    return fade(x, 0.0003, 0.2), fade(st, 0.001, 0.2)


def s_arc(dur, seed=0):
    """Welding arc: mains buzz with a crackling spray."""
    n = ns(dur)
    t = tt(n)
    buzz = sum(sine(100 * h, n) * (0.5 / h) for h in (1, 2, 3, 5, 7)) * (0.6 + 0.4 * lp(noise(n, seed), 30))
    rng = np.random.default_rng(seed)
    cr = np.zeros(n)
    for _ in range(int(dur * 160)):
        i = rng.integers(0, n - 200)
        cr[i:i + 200] += hp(noise(200, int(rng.integers(0, 9999))), 2500) * expdec(200, 0.0008) * rng.uniform(0.3, 1.0)
    env = np.clip(t / 0.03, 0, 1) * np.clip((dur - t) / 0.2, 0, 1)
    return (lp(buzz, 1800) * 0.25 + cr * 0.9) * env


def s_pen(dur, seed=0):
    n = ns(dur)
    t = tt(n)
    strokes = np.clip(np.sin(2 * np.pi * 5.3 * t + 2 * np.sin(2 * np.pi * 1.7 * t)), 0, 1) ** 2
    return bp(noise(n, seed), 3200, 0.9) * strokes * np.clip(t / 0.05, 0, 1) * np.clip((dur - t) / 0.1, 0, 1) * 0.6


def s_pop(up=True, seed=0):
    n = ns(0.12)
    t = tt(n)
    f = (620 if up else 880) * (1 + (0.5 if up else -0.3) * np.exp(-t / 0.02))
    return fade(sine(f, n) * expdec(n, 0.035) * 0.6 + hp(noise(n, seed), 4000) * expdec(n, 0.002) * 0.2, 0.0005, 0.01)


def s_msg_in(seed=0):
    n = ns(0.9)
    x = s_bell_tone(hz('E6'), 0.9, seed)[:n] * 0.5
    m = ns(0.75)
    x[ns(0.09):ns(0.09) + m] += s_bell_tone(hz('A6'), 0.75, seed + 1)[:m] * 0.4
    return x


def s_scan(dur=1.0, seed=0):
    n = ns(dur)
    u = np.linspace(0, 1, n)
    sweep = bp(noise(n, seed), 900 + 3200 * u, 4.0) * np.sin(np.pi * u) ** 0.5 * 0.5
    hum = sine(1760 + 200 * u, n) * 0.05 * np.sin(np.pi * u)
    return sweep + hum


def s_error(seed=0):
    n = ns(0.32)
    t = tt(n)
    x = np.sign(sine(118, n)) * 0.5 + np.sign(sine(177, n)) * 0.3
    gate = ((t < 0.12) | ((t > 0.17) & (t < 0.29))).astype(float)
    return fade(lp(x, 1400) * gate * 0.35, 0.002, 0.02)


def s_city_night(dur, seed=0):
    n = ns(dur)
    t = tt(n)
    rumble = lp(pink(n, seed), 160) * 0.6
    hiss = bp(pink(n, seed + 1), 1200, 0.5) * 0.08 * (0.6 + 0.4 * lp(noise(n, seed + 2), 0.3) * 4)
    cars = np.zeros(n)
    rng = np.random.default_rng(seed)
    for _ in range(int(dur / 3) + 1):
        c0, cd = rng.uniform(0, dur), rng.uniform(2.5, 5.0)
        i, m = ns(c0), ns(cd)
        m = min(m, n - i)
        if m > 100:
            u = np.linspace(-1, 1, m)
            cars[i:i + m] += bp(noise(m, int(rng.integers(0, 9999))), 500 + 300 * (1 - u ** 2), 0.7) * (1 - u ** 2) ** 2 * 0.3
    return (rumble + hiss + cars) * np.clip(t / 0.4, 0, 1) * np.clip((dur - t) / 0.3, 0, 1)


def s_office(dur, seed=0):
    n = ns(dur)
    t = tt(n)
    hvac = lp(pink(n, seed), 300) * 0.35 + sine(60, n) * 0.02
    chat = bp(pink(n, seed + 1), 700, 0.6) * 0.07 * (0.6 + 0.4 * np.sin(2 * np.pi * 0.23 * t + 1))
    return (hvac + chat) * np.clip(t / 0.3, 0, 1) * np.clip((dur - t) / 0.3, 0, 1)


def typing(t0, t1, gain=0.22, pan=0.2, seed=0, rate=(0.05, 0.16)):
    rng = np.random.default_rng(seed)
    tk = t0
    while tk < t1:
        place(tk, s_key_click(int(tk * 1000) + seed), gain=gain * rng.uniform(0.6, 1.0), pan=pan, room=0.15)
        tk += rng.uniform(*rate)


def pad_run(chords, gain, fc=1300, bus='music', hall=0.35, space=0.0, seed=0, attack=0.8):
    for k, (a, b, notes) in enumerate(chords):
        place(a, s_pad(notes, b - a + 1.2, seed + k * 3, fc, attack, 1.2), gain=gain, bus=bus, hall=hall, space=space)


def pulse_run(t0, t1, chords, gain, step=BEAT / 2, seed=0, bright=0.6, grow=0.0):
    tq, k = t0, 0
    while tq < t1 - 1e-6:
        root = next((c[2][0] for c in chords if c[0] <= tq < c[1]), chords[-1][2][0])
        f = hz(root) * (2 if k % 4 == 2 else 1)
        u = (tq - t0) / max(1e-6, t1 - t0)
        place(tq, s_bass_note(f, step * 0.9, seed + k, bright * (0.7 + 0.6 * (k % 2 == 0))), gain=gain * (1 + grow * u),
              bus='music')
        k += 1
        tq += step


# ============================================================================ the film
def build():
    # ---------------------------------------------------------------- OPEN
    l0, l1, l2 = L('open', 0), L('open', 1), L('open', 2)
    t_job, t_ship, t_prove = l0.word('job'), l0.word('shipment'), l2.word('prove')
    stamps = [t_prove, l2.word('Again'), l2.word('again', 1)]
    flurry = [l2.end + 0.10 + k * (0.20 - k * 0.022) for k in range(6)]
    t_black = flurry[-1] + 0.35
    place(0.0, fade(lp(pink(ns(t_black), 1), 700) * 0.02, 0.3, 0.004))                                  # room tone
    drone = A.s_drone(t_black - 0.2)
    place(0.1, fade(drone, 1.0, 0.004), gain=0.3, bus='music', hall=0.25)
    tk, k = 0.4, 0
    while tk < t_black - 0.2:                                                                          # the clock
        place(tk, s_tick(k % 2 == 0, k), gain=0.13 + 0.1 * tk / t_black, pan=-0.2, room=0.3)
        k += 1
        tk += 0.5
    for hb in np.arange(0.6, t_black - 0.3, 1.0):
        place(hb, s_heartbeat(int(hb * 10)), gain=0.35 + 0.25 * hb / t_black, bus='sub')
    place(0.25, s_whoosh(0.9, 300, 1800, 0.8, 11), gain=0.12, hall=0.2)                               # deal
    place(0.9, s_paper(41), gain=0.18, pan=-0.2, room=0.2)
    place(t_job - 0.05, s_arc(t_ship - t_job + 0.1, 12), gain=0.32, pan=0.1, room=0.2)               # job
    place(t_job, s_metal(13, 1.0), gain=0.07, hall=0.3)
    place(t_ship - 0.03, s_ship_horn(2.4), gain=0.32, pan=-0.3, hall=0.4, space=0.3)                 # shipment
    place(t_ship + 0.2, s_metal(14, 1.4) * 0.6, gain=0.06, pan=0.4, hall=0.5)
    place(l1.start + 0.3, s_pen(1.6, 15), gain=0.28, pan=0.1, room=0.2)                                # signing
    for k, ts in enumerate(stamps):
        place(ts - 0.13, s_whoosh(0.13, 400, 2500, 1.0, 55 + k), gain=0.3, room=0.1)
        place(ts + 0.04, s_stamp(), gain=0.7, room=0.4, hall=0.15)
        place(ts, s_sub_drop(0.5, 70, 38), gain=0.35 + 0.1 * k, bus='sub')
    for k, tf in enumerate(flurry):
        place(tf, s_stamp(), gain=0.55 + 0.06 * k, pan=0.3 * math.sin(k * 1.7), room=0.35)
    place(flurry[-1], s_sub_drop(0.9, 60, 30), gain=0.6, bus='sub')

    # ---------------------------------------------------------------- AISHA
    a0, a1, a2, a3 = (L('aisha', i) for i in range(4))
    end_a = L('omar', 0).start
    place(a0.start - 0.4, s_city_night(a1.start - a0.start + 0.6, 20), gain=0.22, room=0.1)
    t_aisha = a0.word('Aisha')
    typing(t_aisha + 0.1, a1.start, 0.16, 0.25, 21)
    place(t_aisha + 1.1, s_ui_confirm(hz('E5'), 22), gain=0.18, pan=0.5, hall=0.3)                   # build complete
    chords_a = [(a0.start, a1.start, ['A2', 'C3', 'E3']), (a1.start, a2.start + 1.5, ['F2', 'A2', 'C3']),
                (a2.start + 1.5, a3.start, ['D2', 'F2', 'A2']), (a3.start, end_a, ['E2', 'G#2', 'B2'])]
    pad_run(chords_a, 0.15, 1100, seed=30)
    pulse_run(a1.start, end_a, chords_a, 0.17, seed=31, grow=0.6)
    # the maze
    for k in range(3):
        place(a1.start + 0.15 + k * 0.45, s_pop(True, 32 + k), gain=0.22, pan=-0.3 + 0.2 * k, room=0.2)
    typing(a1.start + 0.3, a3.start - 0.2, 0.2, -0.1, 33, (0.04, 0.12))
    words = [a2.word('same'), a2.word('office'), a2.word('bank'), a2.end - 0.1]
    for k, tw in enumerate(words):
        place(tw - 0.1, s_glass_in(34 + k), gain=0.25, pan=0.3, hall=0.15)
        if k in (0, 2):
            place(tw + 0.9, s_error(35 + k), gain=0.5, pan=0.3, room=0.2)
    tc, prev = a1.start, 0
    while tc < a3.start:
        u = (tc - a1.start) / (a3.start - a1.start)
        v = 1 + int(96 * u ** 1.6)
        if v != prev:
            place(tc, s_counter_tick(int(tc * 1000)), gain=0.14 + 0.08 * u, pan=0.6, room=0.1)
            prev = v
        tc += 1 / 120
    # the border
    place(a3.start - 0.1, fade(s_crowd(end_a - a3.start + 0.2, 36), 0.1, 0.1), gain=0.26, room=0.3, hall=0.2)
    place(a3.start + 0.2, s_chime(), gain=0.22, pan=0.3, hall=0.6)
    t_again = a3.word('again')
    place(t_again, s_glitch(), gain=0.55, room=0.1)
    place(t_again, s_sub_drop(0.8, 70, 32), gain=0.6, bus='sub')

    # ---------------------------------------------------------------- MARIAM
    o0, o1 = L('omar', 0), L('omar', 1)
    end_o = L('ministry', 0).start
    t_ret, t_rec, t_wait = o1.word('retypes'), o1.word('Re-checks'), o1.word('waits')
    place(o0.start - 0.2, s_whoosh(1.4, 200, 1400, 0.7, 40), gain=0.12, hall=0.4)
    place(o0.word('Mariam') - 0.05, s_office(end_o - o0.word('Mariam') + 0.3, 41), gain=0.35, room=0.2)
    chords_o = [(end_a, o1.start, ['A2', 'C3', 'E3']), (o1.start, t_rec, ['F2', 'A2', 'C3']),
                (t_rec, end_o, ['E2', 'G#2', 'B2'])]
    pad_run(chords_o, 0.16, 1300, seed=42)
    pulse_run(o0.start, end_o, chords_o, 0.18, seed=43, grow=0.5)
    for k in range(3):
        place(o1.start - 0.2 + k * 0.18, s_pop(True, 44 + k), gain=0.2, pan=0.5, room=0.2)
        typing(t_ret + k * 0.35, t_ret + k * 0.35 + 0.9, 0.2, 0.45, 45 + k, (0.03, 0.07))
    place(o1.start + 0.3, s_error(47), gain=0.3, pan=0.5, room=0.2)
    place(o1.start + 0.5, s_error(48), gain=0.25, pan=0.55, room=0.2)
    for k in range(int((t_wait - t_rec) / 0.25)):
        place(t_rec + k * 0.25, s_tick(k % 2 == 0, 49 + k), gain=0.08, pan=0.5)
    place(t_wait - 0.1, s_glass_in(50), gain=0.22, pan=-0.4, hall=0.2)
    for k in range(int((end_o - t_wait) / 0.09)):
        place(t_wait + k * 0.09, s_counter_tick(51 + k), gain=0.08, pan=-0.5)

    # ---------------------------------------------------------------- MINISTRY
    m0, m1 = L('ministry', 0), L('ministry', 1)
    end_m = L('peak', 0).start
    t_econ, t_every = m0.word('economy'), m1.word('Every')
    place(m0.start - 0.2, s_city_night(t_econ - m0.start + 0.4, 52) * 0.7, gain=0.3, hall=0.2)
    place(t_econ - 0.05, fade(s_fluoro(end_m - t_econ, 53), 0.05, 0.1), gain=0.16, room=0.3)
    rng = np.random.default_rng(54)
    for k in range(48):
        ta = t_every - 0.3 + int(rng.permutation(48)[k]) * 0.045
        place(ta, s_chirp(55 + k), gain=0.05 + 0.03 * rng.random(), pan=rng.uniform(-0.9, 0.9), room=0.2)
    for k in range(26):
        tb = t_econ + rng.uniform(0, end_m - t_econ)
        place(tb, s_ui_confirm(hz(['C6', 'D#6', 'F#6', 'A6'][k % 4]), 60 + k), gain=0.04, pan=rng.uniform(-1, 1), room=0.3)
    chords_m = [(end_o, m1.start, ['D2', 'F2', 'A2']), (m1.start, end_m, ['E2', 'G#2', 'B2', 'D3'])]
    pad_run(chords_m, 0.16, 1500, seed=61)
    pulse_run(end_o, end_m, chords_m, 0.2, step=BEAT / 4, seed=62, grow=0.6)

    # ---------------------------------------------------------------- PEAK (then silence)
    p0 = L('peak', 0)
    t_held = p0.word('Held')
    for a_i in range(2):
        place(p0.start + 1.0 + a_i * 0.5, s_error(63 + a_i), gain=0.35, pan=-0.3 + 0.6 * a_i, room=0.2)
    place(p0.start, fade(s_riser(p0.end - p0.start), 0.4, 0.002), gain=0.24, bus='music', hall=0.2)
    pad_run([(p0.start, p0.end, ['F2', 'A2', 'C3', 'E3'])], 0.13, 1800, seed=64)
    cuts, acc, d = [], t_held, 0.42
    while acc < p0.end:
        cuts.append(acc)
        acc += d
        d = max(0.07, d * 0.8)
    for k, tc_ in enumerate(cuts):
        place(tc_, s_kick(65 + k, 0.2), gain=0.2 + 0.2 * k / len(cuts), bus='sub')
        place(tc_, s_zap(66 + k) if k % 3 == 2 else s_stamp() * 0.5, gain=0.15, pan=0.4 * math.sin(k), room=0.2)
    t_cut = p0.end + 0.05

    # ---------------------------------------------------------------- TURN
    u0, u1 = L('turn', 0), L('turn', 1)
    t_rev = L('reveal', 0).word('Mass') - 0.06
    place(u0.start + 0.4, s_bell_tone(hz('A5'), 3.0, 70), gain=0.08, hall=0.6, delay=0.3)
    place(u0.start + 0.4, s_bell_tone(hz('A4'), 3.0, 71), gain=0.05, hall=0.6)
    chords_u = [(u0.start + 0.2, u1.start, ['A2', 'E3', 'A3']), (u1.start, u1.word('Created'), ['F#2', 'A2', 'C#3', 'E3']),
                (u1.word('Created'), u1.word('Trusted'), ['D2', 'A2', 'D3', 'F#3']), (u1.word('Trusted'), t_rev, ['E2', 'B2', 'E3', 'G#3'])]
    pad_run(chords_u, 0.09, 1500, seed=72, attack=1.2, space=0.3)
    place(u1.start, s_glass_in(73), gain=0.22, hall=0.3)
    place(u1.start, s_whoosh(0.7, 500, 4000, 1.0, 74), gain=0.15, hall=0.3)
    for j, nm in enumerate(['C#6', 'E6', 'A6', 'B6']):
        place(u1.word('Created') + j * 0.28, s_ui_confirm(hz(nm), 75 + j), gain=0.06, pan=0.2, hall=0.2)
    for j in range(5):
        place(u1.word('Trusted') + j * 0.12, s_whoosh(0.5, 2000, 9000, 1.6, 80 + j), gain=0.07, pan=-0.8 + 0.4 * j, hall=0.4)
        place(u1.word('Trusted') + j * 0.12 + 0.48, s_bell_tone(hz(['E6', 'G#6', 'B6', 'C#7', 'E7'][j]), 1.2, 85 + j),
              gain=0.035, pan=-0.8 + 0.4 * j, space=0.6)

    # ---------------------------------------------------------------- REVEAL: the sonic logo
    s_sting(t_rev)

    # ---------------------------------------------------------------- DEMO (the three-way)
    T_ = S.demo_times()
    dd = T_['d']
    g0 = dd[0] - 0.6
    t_end_demo = T_['end']
    prog = [['A2', 'C#3', 'E3', 'A3'], ['E2', 'B2', 'E3', 'G#3'], ['F#2', 'C#3', 'F#3', 'A3'], ['D2', 'A2', 'D3', 'F#3']]
    bar = BEAT * 4
    chords_d = []
    tq, k = g0, 0
    while tq < L('network', 0).start:
        chords_d.append((tq, tq + bar * 2, prog[k % 4]))
        tq += bar * 2
        k += 1
    pad_run(chords_d, 0.085, 1700, seed=90, attack=0.4, hall=0.3)
    nbeats = int((L('network', 0).start - g0) / BEAT)
    for i in range(nbeats):
        tb = g0 + i * BEAT
        place(tb, s_kick(100 + i, 0.25), gain=0.32 if i % 2 == 0 else 0.18, bus='sub')
        place(tb + BEAT / 2, s_hat(200 + i), gain=0.07, pan=0.25)
        if i % 4 == 1 or i % 4 == 3:
            place(tb, s_snare(300 + i, 0.09), gain=0.07, room=0.4)
    pulse_run(g0, L('network', 0).start, chords_d, 0.09, step=BEAT / 4, seed=400, bright=0.5, grow=0.4)
    tq, k = g0 + bar * 2, 0
    while tq < L('network', 0).start - 1e-6:                                                      # arpeggio shimmer
        notes = next(c[2] for c in chords_d if c[0] <= tq < c[1])
        place(tq, s_pluck(hz(notes[[1, 2, 3, 2][k % 4]]) * 2, 0.5, 0.5, 500 + k), gain=0.03, pan=0.4 * math.sin(k * 0.9),
              bus='music', delay=0.4)
        k += 1
        tq += BEAT / 2
    ch = S.demo_chat()
    for e in ch.events:
        if e['who'] == 'user':
            place(e['t'], s_pop(True, int(e['t'] * 10)), gain=0.3, pan=0.35, room=0.15)
        else:
            if e.get('typing', True):
                for q in range(3):
                    place(e['t'] - 0.8 + q * 0.25, s_click(1800, 600 + q), gain=0.06, pan=0.35)
            place(e['t'], s_msg_in(int(e['t'] * 10)), gain=0.22, pan=0.35, hall=0.25)
        if e.get('kind') == 'passport':
            place(e['scan'], s_scan(1.0, 610), gain=0.3, pan=0.35, room=0.2)
            place(e['scan'] + 1.0, s_ui_confirm(hz('A5'), 611), gain=0.25, pan=0.35, hall=0.3)
        if e.get('kind') == 'checks':
            for j, (_, ti) in enumerate(e['items']):
                place(ti, s_ui_confirm(hz(['E5', 'A5', 'C#6', 'E6'][j % 4]), 620 + j), gain=0.24, pan=0.35, hall=0.3, delay=0.2)
        if e.get('kind') == 'result':
            for j, (_, ti) in enumerate(e['items']):
                place(ti, s_bell_tone(hz(['A5', 'C#6', 'E6'][j]), 1.4, 630 + j), gain=0.09, pan=0.35, hall=0.4, delay=0.3)
    # camera moves between the three screens
    cams = S.demo_cams()
    for (ta, ca), (tb, cb) in zip(cams, cams[1:]):
        if tb - ta < 1.2 and abs(ca.zoom - cb.zoom) > 0.05:
            place(ta, s_whoosh(tb - ta + 0.15, 400 if cb.zoom < ca.zoom else 900, 3500, 0.9, int(ta * 10)), gain=0.16,
                  pan=0.0, hall=0.2)
    # filing travels to Mariam; she decides; everyone hears back
    place(T_['file'] + 0.9, s_whoosh(0.9, 1200, 6000, 1.4, 640), gain=0.18, pan=-0.2, hall=0.3)
    place(T_['file'] + 1.8, s_msg_in(641), gain=0.24, pan=0.1, hall=0.3)
    for j in range(4):
        place(dd[2] + 0.5 + 0.15 * j, s_ui_confirm(hz(['A5', 'B5', 'C#6', 'E6'][j]), 642 + j), gain=0.14, pan=0.1, hall=0.3)
    place(T_['decide'] - 0.02, s_click(2600, 646), gain=0.35, pan=0.1)
    place(T_['decide'] + 0.12, s_stamp() * 0.55, gain=0.5, room=0.3)                               # the approval seal
    place(T_['decide'] + 0.12, s_sub_drop(0.5, 80, 45), gain=0.35, bus='sub')
    place(T_['decide'] + 0.2, s_bell_tone(hz('A5'), 2.0, 647), gain=0.1, hall=0.5, delay=0.3)
    place(T_['decide'] + 1.0, s_whoosh(0.8, 1500, 7000, 1.4, 648), gain=0.16, pan=0.3, hall=0.3)
    place(dd[4] - 0.5, s_whoosh(0.7, 1500, 7000, 1.4, 649), gain=0.12, pan=0.4, hall=0.3)
    t_mnm = L('demo', 3).end + 0.15
    place(t_mnm, s_tom(70, 650), gain=0.3, bus='sub', hall=0.2)
    place(t_mnm, s_glass_in(651), gain=0.2, hall=0.3)
    place(T_['live'], s_counter_tick(652), gain=0.25, pan=0.3)
    place(T_['live'] + 0.05, s_ui_confirm(hz('E6'), 653), gain=0.2, pan=0.3, hall=0.3)
    place(dd[5] - 0.35, s_glass_in(654), gain=0.22, pan=0.3, hall=0.2)
    place(T_['change'], s_sonar(hz('E5')), gain=0.12, pan=0.3, hall=0.4, delay=0.3)
    place(T_['same'] - 0.1, s_whoosh(1.4, 300, 9000, 0.8, 655, 1.2), gain=0.18, hall=0.35)
    place(T_['same'] - 0.1, s_boom(2.0, 70, 35, 656), gain=0.45, bus='sub')
    for j, nm in enumerate(['A5', 'C#6', 'E6']):
        place(T_['same'] + 0.3 + j * 0.15, s_bell_tone(hz(nm), 1.8, 657 + j), gain=0.06, pan=-0.6 + 0.6 * j, space=0.6)

    # ---------------------------------------------------------------- TRUST
    r0, r1 = L('trust', 0), L('trust', 1)
    place(r0.start - 0.2, s_glass_in(700), gain=0.3, pan=0.3, hall=0.2)
    t_before = r0.word('before')
    for j in range(4):
        tj = r0.start + 0.3 + j * (t_before - r0.start) / 4
        place(tj, s_ui_confirm(hz(['E5', 'G#5', 'B5', 'E6'][j]), 701 + j), gain=0.11, pan=0.35, hall=0.3)
    place(r0.end - 0.1, s_chirp(705), gain=0.2, pan=0.35, hall=0.3)
    place(r0.end - 0.05, s_bell_tone(hz('B5'), 1.2, 706), gain=0.07, pan=0.35, hall=0.4)
    place(r1.start - 0.25, s_whoosh(0.5, 300, 3000, 0.9, 707), gain=0.18, hall=0.3)
    t_infra, t_keys = r1.word('infrastructure'), r1.word('keys')
    for i in range(6):
        ti = r1.start + 0.1 + i * (t_infra - r1.start + 0.6) / 6
        place(ti + 0.18, s_bell_tone(hz(['E5', 'A5', 'C#6', 'E6', 'A6', 'C#7'][i]), 1.2, 710 + i) * 0.6 + 0 * 0, gain=0.14,
              pan=0.45, hall=0.35)
        place(ti + 0.18, s_key_click(716 + i), gain=0.12, pan=0.45)
    place(t_keys - 0.19, s_lock(), gain=0.75, pan=0.3, room=0.3, hall=0.2)

    # ---------------------------------------------------------------- NETWORK
    n0 = L('network', 0)
    tn0 = n0.start - 0.1
    t_close = L('close', 0).start - 0.1
    place(tn0 - 0.6, s_whoosh(0.35, 300, 5000, 0.8, 800, 1.3), gain=0.3, hall=0.2)
    place(tn0 - 0.25, A.s_space_boom(), gain=0.5, bus='sub', space=0.3)
    place(tn0, s_cymbal(4.0, 801), gain=0.1, space=0.6)
    chords_n = [(tn0, L('network', 1).start, ['A2', 'E3', 'A3', 'C#4']), (L('network', 1).start, L('network', 1).word('joins'), ['F#2', 'C#3', 'F#3', 'A3']),
                (L('network', 1).word('joins'), L('network', 2).start, ['D2', 'A2', 'D3', 'F#3']),
                (L('network', 2).start, L('network', 2).word('Together'), ['E2', 'B2', 'E3', 'G#3']),
                (L('network', 2).word('Together'), t_close, ['A2', 'E3', 'A3', 'C#4', 'E4'])]
    pad_run(chords_n, 0.13, 2200, seed=802, attack=1.0, space=0.5)
    t_hub, times, mesh = S.net_schedule()
    place(t_hub, s_sonar(hz('A4')), gain=0.26, space=0.7, delay=0.4)
    place(t_hub, s_sonar(hz('A2')), gain=0.18, space=0.6)
    for k, (nm, ti) in enumerate(sorted(times.items(), key=lambda x: x[1])):
        notes = next((c[2] for c in chords_n if c[0] <= ti < c[1]), chords_n[-1][2])
        f = hz(notes[k % len(notes)]) * (4 if k % 2 == 0 else 2)
        pan = 0.7 * math.sin(k * 1.1)
        place(ti, s_pluck(f, 1.8, 0.9, 810 + k), gain=0.12, pan=pan, bus='music', space=0.45, delay=0.45)
        place(ti, s_bell_tone(f * 2, 1.4, 830 + k), gain=0.03, pan=pan, space=0.5)
        place(ti - 0.55, s_whoosh(0.55, 800, 5000, 1.5, 850 + k), gain=0.06, pan=pan * 0.6, space=0.4)
    for k, (_, _, tm) in enumerate(mesh):
        place(tm + 0.5, s_pluck(hz(['A5', 'C#6', 'E6', 'B5'][k % 4]), 1.2, 0.6, 870 + k), gain=0.05,
              pan=0.6 * math.sin(k * 1.3), bus='music', space=0.5, delay=0.5)
    t_one = L('network', 2).word('Together')
    for i in range(int((t_close - t_one) / BEAT)):
        place(t_one + i * BEAT, s_kick(880 + i, 0.3), gain=0.3 + 0.1 * i, bus='sub')
    place(t_close - 1.4, fade(s_riser(1.35, 890), 0.3, 0.004), gain=0.3, bus='music', hall=0.2)

    # ---------------------------------------------------------------- CLOSE: four hits, then the logo
    c0, c1 = L('close', 0), L('close', 1)
    hits = [c0.word('Formed'), c0.word('Licensed'), c0.word('Banked'), c0.word('Recognised')]
    stabs = [['A2', 'E3', 'A3', 'C#4'], ['C#3', 'G#3', 'C#4', 'E4'], ['D3', 'A3', 'D4', 'F#4'], ['E3', 'B3', 'E4', 'G#4']]
    for k, th in enumerate(hits):
        place(th - 0.32, fade(s_reverse_swell(0.32, 900 + k), 0.05, 0.002), gain=0.1 + 0.02 * k, hall=0.2)
        hit, stab = s_hit(k, stabs[k], 910 + 10 * k)
        place(th, hit, gain=0.7 + 0.08 * k, bus='sub', hall=0.25)
        place(th, stab, gain=0.34 + 0.05 * k, bus='music', hall=0.3)
        place(th, s_metal(950 + k, 1.0 + 0.2 * k), gain=0.03 + 0.01 * k, pan=0.3 * (-1) ** k, hall=0.5)
        place(th - 0.06, s_whoosh(0.14, 5200, 1400, 1.0, 960 + k), gain=0.05, pan=0.35 * (-1) ** k)
    place(hits[0], s_cymbal(2.0, 970), gain=0.08, hall=0.4)
    t_mass = c1.word('Mass') - 0.05
    s_sting(t_mass, big=True)
    place(c1.word('operating'), s_bell_tone(hz('E6'), 2.4, 980), gain=0.03, space=0.6)
    place(c1.end + 0.4, s_bell_tone(hz('A6'), 1.8, 981), gain=0.025, space=0.6)
    return dict(t_black=t_black, t_cut=t_cut, t_rev=t_rev)


# ============================================================================ narration
def load_vo(source):
    """Narration placed at its timeline positions (scratch: one wav per line; final: the single take)."""
    vo = np.zeros(N)
    if source == 'final':
        info = json.load(open(os.path.join(V2, 'out', 'vo_final', 'lines.json')))
        for ln, d in zip(S.TL.lines, info):
            x, fs = sf.read(os.path.join(V2, 'out', 'vo_final', d['file']))
            x = x.mean(1) if x.ndim > 1 else x
            if fs != FS:
                x = signal.resample_poly(x, FS, fs)
            i = int(ln.start * FS)
            m = min(len(x), N - i)
            vo[i:i + m] += x[:m]
        return vo
    d = os.path.join(V2, 'out', 'scratch_vo')
    files = sorted(f for f in os.listdir(d) if f.endswith('.wav'))
    for ln, f in zip(S.TL.lines, files):
        x, fs = sf.read(os.path.join(d, f))
        x = x.mean(1) if x.ndim > 1 else x
        x = signal.resample_poly(x, FS // 100, fs // 50) if fs != FS else x
        i = int(ln.start * FS)
        m = min(len(x), N - i)
        vo[i:i + m] += x[:m]
    return vo


def vo_chain(vo):
    x = hp(vo, 85)
    x = x + 0.25 * bp(x, 3200, 0.8)                                           # presence
    x = x - 0.15 * bp(x, 300, 1.0)                                            # de-mud
    lvl = np.sqrt(lp(x ** 2, 8).clip(1e-12, None))
    over = 20 * np.log10(lvl + 1e-9) + 22
    gr = np.where(over > 0, -over * (1 - 1 / 3.0), 0.0)
    x = x * db(lp(gr, 30))
    # speech sits at -20 dBFS RMS (measured over the spoken lines only)
    spoken = np.concatenate([x[int(ln.start * FS):int(ln.end * FS)] for ln in S.TL.lines])
    return x * db(-20) / (np.sqrt(np.mean(spoken ** 2)) + 1e-9)


def duck_env(vo):
    """1 = no narration, 0 = narration present (30 ms attack, ~300 ms release)."""
    e = np.sqrt(lp(vo ** 2, 12).clip(0, None))
    act = np.clip((20 * np.log10(e + 1e-9) + 42) / 10, 0, 1)
    hold = np.maximum(act, np.concatenate([act[ns(0.12):], np.zeros(ns(0.12))]))   # open slightly early
    return 1 - lp(hold, 2.5).clip(0, 1)


def master(out_path, target=-15.0, source='scratch'):
    marks = build()
    vo = vo_chain(load_vo(source))
    duck = duck_env(vo)
    irs = (make_ir(0.6, 1.2, 1, 0.006, 0.4, 0.8), make_ir(2.4, 4.0, 2, 0.018, 0.45, 1.0),
           make_ir(5.5, 8.0, 3, 0.04, 0.35, 1.2))
    room = convolve_bus(B['room'], irs[0])
    hall = convolve_bus(B['hall'], irs[1])
    space = convolve_bus(B['space'], irs[2])
    dly = pingpong(B['delay'], BEAT * 0.75, 0.38)
    music = B['music'].copy()
    sub = B['sub'].copy()
    for c in range(2):
        sub[:, c] = hp(sub[:, c], 26)
        music[:, c] = hp(music[:, c], 30)
    fx = B['sfx'] + room * 0.28 + hall * 0.24 + space * 0.22 + dly * 0.25
    # Act I ends in silence at the black; the peak cuts to silence before the turn
    gate = np.ones(N)
    for t_gate, t_back in ((marks['t_black'], L('aisha', 0).start - 0.45), (marks['t_cut'], L('turn', 0).start + 0.3)):
        i, j = int(t_gate * FS), int(t_back * FS)
        m = ns(0.01)
        gate[i:i + m] = np.linspace(1, 0, m)
        gate[i + m:j] = 0
        gate[j:j + ns(0.4)] = np.minimum(gate[j:j + ns(0.4)], np.linspace(0, 1, ns(0.4)))
    talk = 1 - duck                                                             # narration present
    bed = (music * 0.9 * db(-10 * talk)[:, None] + sub * db(-3 * talk)[:, None]
           + fx * db(-5 * talk)[:, None]) * gate[:, None] * db(BED_DB)
    mix = bed + pan2(vo, 0.0) * 1.0
    for c in range(2):
        mix[:, c] = hp(mix[:, c], 22)
    mix = A.glue(mix, -14, 1.5)
    import pyloudnorm as pyln
    meter = pyln.Meter(FS)
    g = db(target - meter.integrated_loudness(mix))
    rel = 1 - math.exp(-1 / (0.08 * FS))
    for _ in range(3):
        out = A._limiter(mix * g, db(-1.5), ns(0.004), rel)
        g *= db(target - meter.integrated_loudness(out))
    out = A._limiter(mix * g, db(-1.5), ns(0.004), rel)
    up = signal.resample_poly(out, 4, 1, axis=0)
    tp = np.max(np.abs(up))
    if tp > db(-1.0):
        out = out * db(-1.0) / tp
    out = out[:int(DUR * FS)]
    m = ns(0.5)
    out[-m:] *= np.linspace(1, 0, m)[:, None]
    sf.write(out_path, out.astype(np.float32), FS, subtype='PCM_24')
    tp_db = 20 * np.log10(np.max(np.abs(signal.resample_poly(out, 4, 1, axis=0))))
    print(f'{out_path}: {meter.integrated_loudness(out):.1f} LUFS, true peak ~ {tp_db:.1f} dBTP, {len(out) / FS:.2f}s')
    # stems for checking the balance
    np.save('/tmp/claude-0/stems.npy', np.stack([vo[:int(DUR * FS)] * g, bed[:int(DUR * FS)].mean(1) * g]))
    return out


if __name__ == '__main__':
    src = os.environ.get('MASS_VO', 'scratch')
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(V2, 'out', f'mass_v2_mix_{src}.wav')
    master(out, source=src)
