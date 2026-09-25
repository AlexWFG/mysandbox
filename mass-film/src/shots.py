"""Every shot of the film. frame(t, fi) returns a display-space RGB float32 image."""
import math
import functools

import cv2
import numpy as np
import skia

import timeline as T
from engine import (W, H, FPS, INK, GOLD, TEXT, GREY, LABEL, RED, PAPER, clamp, lerp, ramp, smooth,
                    smoother, ease_out_cubic, ease_in_cubic, ease_in_out_cubic, ease_out_expo,
                    ease_in_expo, ease_out_back, window, u8_to_lin, lin_to_srgb, srgb_to_lin, luma,
                    soft_clip, grade, load_photo, Wobble, camera, cam_matrix, map_pt, gblur, frosted_path,
                    lens_blur, bloom, halation, vignette, chroma_aberration, grain, letterbox,
                    bars_for_aspect, Layer, paint, draw_text, text_width, composite, add_light,
                    frosted, placed_mark, mark_width, mark_paths)
import globe as G

BAR_239 = bars_for_aspect(2.39)            # ~138 px
TOP = BAR_239                               # top of the letterboxed picture
BOT = H - BAR_239                           # bottom of the letterboxed picture

# ----------------------------------------------------------------------------- looks
LOOKS = {
    # warm tungsten, green-teal shadows, dense blacks
    'paper': dict(lift=(0.018, 0.020, 0.024), gain=(1.02, 0.96, 0.86), gamma=(1.0, 0.98, 0.94), sat=0.78,
                  contrast=0.28, shadow_tint=(0.44, 0.52, 0.52), high_tint=(0.60, 0.52, 0.40), tint_amt=0.22),
    # sick fluorescent institutional light
    'fluoro': dict(lift=(0.02, 0.025, 0.022), gain=(0.92, 0.98, 0.90), gamma=(0.95, 1.0, 0.95), sat=0.55,
                   contrast=0.22, shadow_tint=(0.44, 0.54, 0.50), high_tint=(0.52, 0.56, 0.44), tint_amt=0.25),
    'customs': dict(lift=(0.02, 0.02, 0.03), gain=(0.92, 0.95, 1.0), gamma=(0.95, 0.98, 1.02), sat=0.5,
                    contrast=0.26, shadow_tint=(0.44, 0.48, 0.58), high_tint=(0.54, 0.54, 0.50), tint_amt=0.25),
    # rich amber for the reveal
    'gold': dict(lift=(0.01, 0.006, 0.012), gain=(1.05, 0.95, 0.80), gamma=(1.0, 0.97, 0.92), sat=1.05,
                 contrast=0.30, shadow_tint=(0.46, 0.44, 0.54), high_tint=(0.62, 0.54, 0.40), tint_amt=0.2),
    # day-for-night teal
    'nightblue': dict(lift=(0.010, 0.016, 0.030), gain=(0.80, 0.92, 1.05), gamma=(0.92, 0.96, 1.02), sat=0.72,
                      contrast=0.30, shadow_tint=(0.40, 0.48, 0.60), high_tint=(0.50, 0.54, 0.58), tint_amt=0.3),
    # blue hour with warm practicals
    'bluehour': dict(lift=(0.012, 0.016, 0.028), gain=(1.0, 0.99, 1.02), gamma=(1.0, 1.0, 1.02), sat=0.95,
                     contrast=0.22, shadow_tint=(0.42, 0.48, 0.60), high_tint=(0.58, 0.52, 0.44), tint_amt=0.22),
    'dusk': dict(lift=(0.012, 0.014, 0.022), gain=(1.02, 0.98, 0.95), gamma=(1.0, 0.99, 1.0), sat=0.92,
                 contrast=0.26, shadow_tint=(0.42, 0.48, 0.58), high_tint=(0.60, 0.52, 0.42), tint_amt=0.24),
    'night': dict(lift=(0.006, 0.008, 0.016), gain=(1.0, 1.0, 1.02), gamma=(0.98, 1.0, 1.02), sat=1.0,
                  contrast=0.30, shadow_tint=(0.42, 0.46, 0.60), high_tint=(0.56, 0.52, 0.46), tint_amt=0.2),
    'neutral': dict(),
}


def finish(lin, look, bloom_amt=0.25, bloom_th=0.72, hal=0.12, vig=0.42, ca=0.0010):
    if bloom_amt:
        lin = bloom(lin, bloom_th, bloom_amt)
    if hal:
        lin = halation(lin, 0.55, hal)
    lin = soft_clip(lin)
    disp = lin_to_srgb(lin)
    if ca:
        disp = chroma_aberration(disp, ca)
    disp = grade(disp, **LOOKS[look])
    if vig:
        disp = vignette(disp, vig)
    return disp


def scrim(lin, cx, cy, rx, ry, amt):
    """Soft elliptical darkening behind text, applied in linear light before grading."""
    xs = (np.arange(W, dtype=np.float32) - cx) / rx
    ys = (np.arange(H, dtype=np.float32) - cy) / ry
    m = np.exp(-(ys[:, None] ** 2 + xs[None, :] ** 2) * 1.6)
    return lin * (1 - amt * m)[..., None]


def radial(cx, cy, r):
    xs = (np.arange(W, dtype=np.float32) - cx) / r
    ys = (np.arange(H, dtype=np.float32) - cy) / r
    return np.exp(-(ys[:, None] ** 2 + xs[None, :] ** 2))


def black():
    return np.zeros((H, W, 3), np.float32) + INK


# ----------------------------------------------------------------------------- type helpers
def word_starts(text):
    idx = [0]
    for i, ch in enumerate(text):
        if ch == ' ':
            idx.append(i + 1)
    return idx


def typed_line(c, text, times, t, x, y, size=50, color=PAPER, seed=0, alpha=1.0):
    """Typewriter line: each word strikes at its time; per-char ink and baseline jitter."""
    starts = word_starts(text)
    rng = np.random.default_rng(seed)
    ink = rng.uniform(0.80, 1.0, len(text))
    jit = rng.uniform(-1.4, 1.4, len(text))
    ca = np.zeros(len(text), np.float32)
    for wi, s in enumerate(starts):
        e = starts[wi + 1] if wi + 1 < len(starts) else len(text)
        tw = times[wi] if wi < len(times) else times[-1]
        if t >= tw:
            ca[s:e] = ink[s:e]
    if ca.max() <= 0:
        return
    draw_text(c, text, x, y + 3, 'typewriter', size, (0, 0, 0), alpha * 0.55, char_alpha=list(np.clip(ca, 0, 1)),
              blur=7, align='center')
    draw_text(c, text, x, y, 'typewriter', size, color, alpha, char_alpha=list(np.clip(ca, 0, 1)),
              char_dy=list(jit), align='center')


def title(c, parts, x, y, t, t_in, t_out=None, size=58, key='display_light', align='left',
          stagger=0.016, rise=16, tracking=-0.012, dur=0.5, shadow=0.45):
    """Per-character rise-and-fade title. parts = [(text, color), ...]."""
    full = ''.join(p for p, _ in parts)
    n = len(full)
    if t < t_in:
        return
    out = 1.0
    drift = 0.0
    if t_out is not None:
        k = smooth(ramp(t, t_out - 0.28, t_out))
        out = 1 - k
        drift = -6 * k
    if out <= 0.002:
        return
    widths = [text_width(p, key, size, tracking) for p, _ in parts]
    total = sum(widths)
    x0 = x - total / 2 if align == 'center' else (x - total if align == 'right' else x)
    ci = 0
    for (txt, col), wdt in zip(parts, widths):
        pa, pdy = [], []
        for j in range(len(txt)):
            i = ci + j
            p = ease_out_cubic(ramp(t, t_in + i * stagger, t_in + i * stagger + dur))
            pa.append(p * out)
            pdy.append((1 - p) * rise + drift)
        if shadow:
            draw_text(c, txt, x0, y + 2, key, size, (0, 0, 0), shadow, tracking=tracking, align='left',
                      char_alpha=pa, char_dy=pdy, blur=10)
        draw_text(c, txt, x0, y, key, size, col, 1.0, tracking=tracking, align='left', char_alpha=pa, char_dy=pdy)
        x0 += wdt
        ci += len(txt)


def decode(text, t, t0, dur=0.35, seed=0):
    """Text that resolves from random glyphs, left to right."""
    if t < t0:
        return ''
    p = clamp((t - t0) / dur)
    n = len(text)
    k = int(p * n + 0.5)
    rng = np.random.default_rng(seed + int(t * FPS))
    pool = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#/'
    tail = ''.join(pool[rng.integers(len(pool))] if ch != ' ' else ' ' for ch in text[k:min(n, k + 3)])
    return text[:k] + tail


def lin_from_layer(layer_rgba, gain=1.0):
    """Treat a skia layer as emitted light in linear space."""
    return srgb_to_lin(np.clip(layer_rgba[..., :3], 0, 1)) * gain


# ----------------------------------------------------------------------------- Act I
@functools.lru_cache(maxsize=1)
def dust_field(n=70, seed=11):
    rng = np.random.default_rng(seed)
    return dict(x=rng.uniform(0, W, n), y=rng.uniform(TOP, BOT, n), vx=rng.uniform(-9, 14, n),
                vy=rng.uniform(-16, -3, n), r=rng.uniform(0.9, 3.4, n) ** 1.15,
                ph=rng.uniform(0, 6.28, n), b=rng.uniform(0.25, 1.0, n))


def shaft_mask(t, angle=-58, center=0.38, width=0.16):
    """Soft diagonal light shaft (0..1), slowly breathing."""
    ys, xs = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32)
    a = math.radians(angle)
    d = (xs * 4 * math.cos(a) + ys * 4 * math.sin(a)) / W
    c = center + 0.01 * math.sin(t * 0.9)
    m = np.exp(-((d - c) / width) ** 2)
    m *= 0.85 + 0.15 * np.sin(xs * 0.05 + t * 0.6) * np.cos(ys * 0.07 - t * 0.4)
    return cv2.resize(m, (W, H), interpolation=cv2.INTER_CUBIC)


def draw_dust(t, shaft, intensity=1.0, color=(1.0, 0.8, 0.55)):
    d = dust_field()
    L = Layer()
    c = L.c
    for i in range(len(d['x'])):
        x = (d['x'][i] + d['vx'][i] * t + 18 * math.sin(t * 0.7 + d['ph'][i])) % W
        y = TOP + (d['y'][i] - TOP + d['vy'][i] * t) % (BOT - TOP)
        sx, sy = int(clamp(x, 0, W - 1)), int(clamp(y, 0, H - 1))
        lit = shaft[sy, sx]
        a = d['b'][i] * (0.15 + 0.85 * lit) * intensity * (0.6 + 0.4 * math.sin(t * 2.3 + d['ph'][i]))
        if a < 0.02:
            continue
        c.drawCircle(x, y, d['r'][i], paint(color, clamp(a), blur=d['r'][i] * 0.6 + 0.8))
    return lin_from_layer(L.rgba(), 0.9)


def plate(name, t, t0, t1, c0, c1, z0, z1, r0=0.0, r1=0.0, wob=None, ease=ease_in_out_cubic, shake=(0, 0)):
    u = ease(ramp(t, t0, t1))
    img = load_photo(name)
    wx, wy, wr = wob(t) if wob is not None else (0, 0, 0)
    cx, cy = lerp(c0[0], c1[0], u), lerp(c0[1], c1[1], u)
    z = lerp(z0, z1, u)
    rot = lerp(r0, r1, u) + wr
    frame, M = camera(img, cx, cy, z, rot, (wx + shake[0], wy + shake[1]), return_matrix=True)
    return frame, M


WOB = {k: Wobble(i + 3, amp=a, rot=r) for i, (k, a, r) in enumerate(
    [('s1', 2.2, 0.08), ('s2', 2.6, 0.10), ('s3', 3.0, 0.08), ('s4', 3.6, 0.12), ('s6', 1.5, 0.05),
     ('s7a', 2.0, 0.06), ('s7b', 2.4, 0.10), ('s8', 1.8, 0.05), ('s9', 2.4, 0.08), ('m', 3.0, 0.1)])}

TXT_Y = BOT - 96          # baseline for Act I lines


def shot1(t, fi):
    lin, _ = plate('typewriter_macro', t, T.S1[0], T.S1[1] + 0.3, (0.46, 0.56), (0.52, 0.50), 1.10, 1.24,
                   1.2, 0.3, WOB['s1'], ease=lambda u: u)
    # shallow depth of field: soften top and bottom
    ys = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    dof = np.clip(np.abs(ys - 0.52) * 2.4 - 0.25, 0, 1)
    lin = lin * (1 - dof) + lens_blur(lin, 7) * dof
    sh = shaft_mask(t)
    lin = lin * (0.78 + 0.5 * sh[..., None] * np.array([1.0, 0.86, 0.66], np.float32))
    lin = lin + draw_dust(t, sh, intensity=1.5)
    lin = scrim(lin, W / 2, TXT_Y - 14, 760, 90, 0.55)
    fade = smooth(ramp(t, T.S1[0], T.S1[0] + 0.55))
    disp = finish(lin * fade, 'paper', bloom_amt=0.22, hal=0.16, vig=0.55)
    L = Layer()
    typed_line(L.c, T.LINE1, T.LINE1_T, t, W / 2, TXT_Y, size=50, seed=1)
    return composite(disp, L.rgba())


@functools.lru_cache(maxsize=1)
def stamp_texture():
    w, h = 1000, 420
    L = Layer(w, h)
    c = L.c
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(22, 22, 956, 376), 30, 30), paint((1, 1, 1), 1, stroke=18))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(50, 50, 900, 320), 16, 16), paint((1, 1, 1), 1, stroke=5))
    draw_text(c, 'PENDING', 500, 262, 'typewriter_bold', 196, (1, 1, 1), tracking=0.05)
    draw_text(c, 'REGISTRY OFFICE  ·  FILE 0047/26', 500, 334, 'typewriter_bold', 30, (1, 1, 1), tracking=0.10)
    a = L.arr[..., 3].astype(np.float32) / 255
    rng = np.random.default_rng(5)
    n1 = cv2.resize(rng.random((h // 50 + 1, w // 50 + 1)).astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC)
    n2 = cv2.resize(rng.random((h // 8, w // 8)).astype(np.float32), (w, h), interpolation=cv2.INTER_LINEAR)
    n3 = rng.random((h, w)).astype(np.float32)
    dens = np.clip(0.45 + 0.55 * n1 + 0.3 * n2, 0, 1)
    holes = (cv2.GaussianBlur(n3, (0, 0), 1.2) > 0.43).astype(np.float32) * 0.35 + 0.65
    ink = np.clip(a * dens * holes * 1.1, 0, 1)
    rough = cv2.GaussianBlur(rng.random((h, w)).astype(np.float32), (0, 0), 1.5)
    ink = np.where(a < 0.5, ink * (rough > 0.5), ink)
    return cv2.GaussianBlur(ink, (0, 0), 0.7)


def shot2(t, fi):
    th = T.STAMP
    dt = t - th
    shake = (0.0, 0.0)
    punch = 1.0
    if dt >= 0:
        env = math.exp(-dt * 9)
        shake = (5 * env * math.sin(dt * 2 * math.pi * 9 + 1), 15 * env * math.sin(dt * 2 * math.pi * 11))
        punch = 1 + 0.025 * math.exp(-dt * 7)
    lin, M = plate('typewriter_message', t, T.S2[0], T.S2[1] + 0.2, (0.52, 0.47), (0.53, 0.45), 1.16 * punch,
                   1.30 * punch, -0.6, 0.4, WOB['s2'], shake=shake)
    # the approaching stamp's shadow, then the impression
    sw, sh_ = 1000, 420
    cx, cy, ang, sc = 1090, 646, -8.0, 0.72     # plate coords (2x plate), degrees, scale
    if dt > -0.14:
        if dt < 0:
            k = 1 - (-dt / 0.14)
            s = sc * (1.25 - 0.25 * k)
            a_sh = 0.55 * k
            A = cv2.getRotationMatrix2D((sw / 2, sh_ / 2), -ang, s)
            A[:, 2] += (cx - sw / 2, cy - sh_ / 2)
            A3 = np.vstack([A, [0, 0, 1]])
            M3 = np.vstack([M, [0, 0, 1]])
            box = np.ones((sh_, sw), np.float32)
            shadow = cv2.warpAffine(box, (M3 @ A3)[:2], (W, H), flags=cv2.INTER_LINEAR)
            shadow = gblur(shadow, 40 * (1 - k) + 12)
            lin = lin * (1 - a_sh * shadow[..., None])
        else:
            s = sc * (1 + 0.02 * math.exp(-dt * 12))
            A = cv2.getRotationMatrix2D((sw / 2, sh_ / 2), -ang, s)
            A[:, 2] += (cx - sw / 2, cy - sh_ / 2)
            A3 = np.vstack([A, [0, 0, 1]])
            M3 = np.vstack([M, [0, 0, 1]])
            ink = cv2.warpAffine(stamp_texture(), (M3 @ A3)[:2], (W, H), flags=cv2.INTER_LINEAR)
            ink = gblur(ink, 1.6 * math.exp(-dt * 6) + 0.4)
            ink_col = np.array([0.50, 0.035, 0.03], np.float32)
            a = np.clip(ink * 0.92, 0, 1)[..., None]
            lin = lin * (1 - a) + lin * a * ink_col * 1.6
            # impact flash of dust
            lin = lin * (1 - 0.10 * math.exp(-dt * 14))
    lin = scrim(lin, W / 2, TXT_Y - 14, 820, 95, 0.72)
    disp = finish(lin, 'paper', bloom_amt=0.2, hal=0.16, vig=0.55)
    L = Layer()
    typed_line(L.c, T.LINE2, T.LINE2_T, t, W / 2, TXT_Y, size=48, seed=2)
    return composite(disp, L.rgba())


def day_counter(c, t, value, x, y, alpha, status='PENDING', status_col=RED, glitch=0.0, prog=0.03, fi=0):
    if alpha <= 0.01:
        return
    c.drawRect(skia.Rect.MakeXYWH(x - 60, y - 150, 560, 280), paint((0, 0, 0), 0.38 * alpha, blur=60))
    draw_text(c, 'DAY', x + 2, y - 86, 'mono_medium', 21, GREY, alpha, tracking=0.4, align='left')
    s = f'{value:03d}'
    dx = 0.0
    if glitch > 0:
        rng = np.random.default_rng(fi * 7 + 1)
        s = ''.join(str(rng.integers(10)) for _ in range(3))
        dx = float(np.random.default_rng(fi).uniform(-14, 14))
        draw_text(c, s, x + dx + 7, y, 'mono_light', 104, (1, 0.1, 0.2), alpha * 0.6, tracking=0.02, align='left')
        draw_text(c, s, x + dx - 7, y, 'mono_light', 104, (0.1, 0.6, 1), alpha * 0.6, tracking=0.02, align='left')
    draw_text(c, s, x + dx, y, 'mono_light', 104, TEXT, alpha, tracking=0.02, align='left')
    lbl = 'APPLICATION STATUS  '
    draw_text(c, lbl, x + 2, y + 48, 'mono', 20, GREY, alpha, tracking=0.2, align='left')
    lw = text_width(lbl, 'mono', 20, 0.2)
    draw_text(c, status, x + 2 + lw, y + 48, 'mono_medium', 20, status_col, alpha, tracking=0.2, align='left')
    c.drawRect(skia.Rect.MakeXYWH(x + 2, y + 76, 460, 2), paint(GREY, alpha * 0.4))
    c.drawRect(skia.Rect.MakeXYWH(x + 2, y + 76, 460 * prog, 2), paint(TEXT, alpha * 0.95))


def counter_value(t):
    u = ramp(t, T.COUNTER[0], T.COUNTER[1])
    return 1 + int(round((T.COUNTER_MAX - 1) * (u ** 2.2)))


def shot3(t, fi):
    flick = 1.0
    for tf in (4.93, 5.62, 5.70):
        if 0 <= t - tf < 0.09:
            flick = 0.72
    lin, _ = plate('waiting_room', t, T.S3[0], T.S3[1] + 0.2, (0.42, 0.56), (0.56, 0.54), 1.14, 1.20, 0, 0,
                   WOB['s3'], ease=lambda u: u)
    lin = scrim(lin, W / 2, TXT_Y - 14, 700, 90, 0.5)
    disp = finish(lin * 0.92 * flick, 'fluoro', bloom_amt=0.15, hal=0.06, vig=0.5)
    L = Layer()
    c = L.c
    a = smooth(ramp(t, T.COUNTER[0] - 0.12, T.COUNTER[0] + 0.1))
    day_counter(c, t, counter_value(t), 150, TOP + 196, a, prog=0.03 + 0.01 * ramp(t, 4.5, 6.2), fi=fi)
    typed_line(c, T.LINE3, T.LINE3_T, t, W / 2, TXT_Y, size=50, seed=3)
    return composite(disp, L.rgba())


def shot4(t, fi):
    lin, _ = plate('customs_queue', t, T.S4[0], T.S4[1] + 0.2, (0.5, 0.60), (0.5, 0.58), 1.02, 1.12, 0.5, -0.3,
                   WOB['s4'], ease=lambda u: u)
    g = 0.0
    if 0 <= t - T.RESET < 0.26:
        g = 1.0
    if g:
        # RGB split and slice displacement on the plate itself
        rng = np.random.default_rng(fi)
        lin = lin.copy()
        for _ in range(7):
            y0 = int(rng.uniform(0, H - 60))
            hgt = int(rng.uniform(8, 60))
            lin[y0:y0 + hgt] = np.roll(lin[y0:y0 + hgt], int(rng.uniform(-60, 60)), axis=1)
        lin[..., 0] = np.roll(lin[..., 0], 9, axis=1)
        lin[..., 2] = np.roll(lin[..., 2], -9, axis=1)
    lin = scrim(lin, W / 2, TXT_Y - 14, 760, 90, 0.5)
    disp = finish(lin * 0.95, 'customs', bloom_amt=0.2, hal=0.1, vig=0.5)
    L = Layer()
    c = L.c
    if t < T.RESET:
        val = T.COUNTER_MAX + int((t - T.S4[0]) * 9)
        day_counter(c, t, val, 150, TOP + 196, 1.0, prog=0.045, fi=fi)
    else:
        day_counter(c, t, 0, 150, TOP + 196, 1.0, status='REFILE EVERYTHING', status_col=RED, glitch=g, prog=0.0, fi=fi)
    typed_line(c, T.LINE4, T.LINE4_T, t, W / 2, TXT_Y, size=50, seed=4)
    return composite(disp, L.rgba())


def shot5(t, fi):
    disp = np.zeros((H, W, 3), np.float32)
    L = Layer()
    c = L.c
    t0, t1 = T.UNTIL_NOW
    p = ease_out_cubic(ramp(t, t0, t0 + 0.45))
    out = 1 - smooth(ramp(t, t1 - 0.22, t1))
    a = p * out
    if a > 0:
        draw_text(c, 'Until now.', W / 2, H / 2 + 14, 'display_light', 46, TEXT, a, tracking=0.01,
                  blur=(1 - p) * 9)
        ln = 150 * ease_out_expo(ramp(t, t0 + 0.25, t0 + 0.8))
        c.drawRect(skia.Rect.MakeXYWH(W / 2 - ln / 2, H / 2 + 52, ln, 1.2), paint(GOLD, 0.8 * out))
    return composite(disp, L.rgba())


# ----------------------------------------------------------------------------- Act II
def mark_layer(c, x, y, h, t, starts, fill_col=(1, 1, 1), sweep_t=None, alpha=1.0, glow=0.0):
    """Mass mark with a light wipe down each stroke (starts: reveal time per shape)."""
    paths = placed_mark(x, y, h)
    for i, p in enumerate(paths):
        prog = ease_out_cubic(ramp(t, starts[i], starts[i] + 0.38)) if starts is not None else 1.0
        if prog <= 0:
            continue
        b = p.getBounds()
        y0, y1 = b.top(), b.bottom()
        yy = lerp(y0 - 0.2 * h, y1 + 0.02 * h, prog)
        cols = [skia.Color4f(fill_col[0], fill_col[1], fill_col[2], alpha).toColor(),
                skia.Color4f(fill_col[0], fill_col[1], fill_col[2], alpha).toColor(),
                skia.Color4f(1, 1, 1, 0).toColor()]
        shader = skia.GradientShader.MakeLinear([skia.Point(0, y0 - 1), skia.Point(0, max(yy, y0 + 1) + 0.12 * h)],
                                                cols, [0.0, 0.88, 1.0])
        pt = skia.Paint(AntiAlias=True)
        pt.setShader(shader)
        if glow:
            c.drawPath(p, paint(GOLD, glow * alpha * prog, blur=h * 0.12))
        c.drawPath(p, pt)
        if prog < 1:
            # bright leading edge
            c.save()
            c.clipPath(p, skia.ClipOp.kIntersect, True)
            c.drawRect(skia.Rect.MakeLTRB(b.left() - 4, yy - 0.05 * h, b.right() + 4, yy + 0.05 * h),
                       paint((1.0, 0.95, 0.8), 0.9 * alpha, blur=0.04 * h))
            c.restore()
    if sweep_t is not None and 0 < sweep_t < 1:
        # specular sweep across the whole mark
        mw = mark_width() * h
        sx = lerp(x - 0.4 * h, x + mw + 0.4 * h, sweep_t)
        c.save()
        clip = skia.Path()
        for p in paths:
            clip.addPath(p)
        c.clipPath(clip, skia.ClipOp.kIntersect, True)
        pts = [skia.Point(sx - 0.3 * h, y), skia.Point(sx + 0.3 * h, y + h)]
        sh = skia.GradientShader.MakeLinear(pts, [skia.Color4f(1, 0.9, 0.6, 0).toColor(),
                                                  skia.Color4f(1, 0.92, 0.7, 0.85 * alpha).toColor(),
                                                  skia.Color4f(1, 0.9, 0.6, 0).toColor()], [0.35, 0.5, 0.65])
        pp = skia.Paint(AntiAlias=True)
        pp.setShader(sh)
        c.drawRect(skia.Rect.MakeXYWH(x - h, y - h * 0.2, mw + 2 * h, h * 1.4), pp)
        c.restore()


def anamorphic_streak(lin, x, y, strength, length=900, color=(1.0, 0.72, 0.38)):
    """Horizontal anamorphic flare streak (linear light)."""
    if strength <= 0.003:
        return lin
    xs = np.arange(W, dtype=np.float32)
    ys = np.arange(H, dtype=np.float32)
    fx = np.exp(-np.abs(xs - x) / length) * 0.85 + np.exp(-((xs - x) / 60) ** 2) * 0.6
    fy = np.exp(-((ys - y) / 2.2) ** 2) + 0.25 * np.exp(-((ys - y) / 14) ** 2)
    return lin + (fy[:, None] * fx[None, :])[..., None] * np.asarray(color, np.float32) * strength


def reveal_scene(t, fi):
    t0 = T.REVEAL
    lin, _ = plate('burj_sunset_gold', t, t0, T.S6[1], (0.50, 0.50), (0.51, 0.48), 1.18, 1.30, 0, 0, WOB['s6'],
                   ease=lambda u: u)
    bg = smooth(ramp(t, t0 + 0.35, t0 + 1.35))
    lin = lens_blur(lin, lerp(14, 5, ramp(t, t0 + 0.2, t0 + 1.8))) * (0.42 * bg)
    dt = max(0.0, t - t0)
    L = Layer()
    c = L.c
    mh = 128
    mx = W / 2 - mark_width() * mh / 2
    my = 318
    sweep = ramp(t, t0 + 0.62, t0 + 1.25)
    mark_layer(c, mx, my, mh, t, T.MARK_STROKES, fill_col=(1.0, 0.985, 0.96), sweep_t=sweep, glow=0.0)
    pw = ease_out_cubic(ramp(t, t0 + 0.42, t0 + 1.2))
    if pw > 0:
        draw_text(c, 'MASS', W / 2, 560, 'display_medium', 50, TEXT, pw, tracking=lerp(0.95, 0.52, pw))
    ps = ease_out_cubic(ramp(t, t0 + 0.8, t0 + 1.35))
    if ps > 0:
        draw_text(c, 'MANAGED ADMINISTRATIVE & SOVEREIGN SERVICES', W / 2, 616, 'mono', 18, GOLD, ps * 0.95,
                  tracking=lerp(0.5, 0.3, ps))
    lay = L.rgba()
    # the mark emits a soft glow into the scene (light, not a sticker)
    glow = gblur(lay[..., 3], 40) * 0.12 + gblur(lay[..., 3], 120) * 0.10
    lin = lin + glow[..., None] * np.array([1.0, 0.78, 0.45], np.float32)
    burst = math.exp(-dt / 0.09) * (t >= t0)
    cy_ = my + mh * 0.55
    lin = lin + radial(W / 2, cy_, 260)[..., None] * np.array([1.0, 0.78, 0.45], np.float32) * burst * 1.1
    lin = lin + radial(W / 2, cy_, 700)[..., None] * np.array([1.0, 0.7, 0.4], np.float32) * burst * 0.12
    lin = anamorphic_streak(lin, W / 2, cy_, 0.9 * math.exp(-dt * 3.2) * (t >= t0) + 0.03)
    disp = finish(lin, 'gold', bloom_amt=0.35, bloom_th=0.6, hal=0.1, vig=0.5, ca=0.0)
    return composite(disp, lay)


def shot6(t, fi):
    t0, t1 = T.FLYTHROUGH
    if t < t0:
        return reveal_scene(t, fi)
    # fly through the mark: zoom about a point inside the middle bar, with zoom blur
    u = ramp(t, t0, t1)
    base = reveal_scene(t, fi)
    mh = 128
    mx = W / 2 - mark_width() * mh / 2
    fx, fy = mx + mh * 0.95, 318 + mh * 0.55
    acc = np.zeros_like(base)
    n = 6
    for k in range(n):
        uu = clamp(u - k * 0.018)
        z = math.exp(ease_in_expo(uu) * math.log(16))
        M = np.array([[z, 0, fx - z * fx + (W / 2 - fx) * uu], [0, z, fy - z * fy + (H / 2 - fy) * uu]], np.float32)
        acc += cv2.warpAffine(base, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    out = acc / n
    white = ease_in_cubic(ramp(t, t1 - 0.12, t1))
    return out * (1 - white) + np.array([1.0, 0.96, 0.88], np.float32) * white


def agent_panel(disp, t, fi):
    a = ease_out_cubic(ramp(t, T.S7_CUT + 0.02, T.S7_CUT + 0.3))
    if a <= 0:
        return disp
    x0, y0, x1, y1 = 1044, 262 + (1 - a) * 24, 1764, 772 + (1 - a) * 24
    disp = frosted(disp, (x0, y0, x1, y1), radius=22, sigma=22, tint=(0.02, 0.02, 0.045), tint_a=0.62, alpha=a)
    L = Layer()
    c = L.c
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x0, y0, x1, y1), 22, 22), paint((1, 1, 1), 0.14 * a, stroke=1.2))
    px = x0 + 40
    c.drawCircle(px + 4, y0 + 44, 4.5, paint(GOLD, a))
    c.drawCircle(px + 4, y0 + 44, 9, paint(GOLD, 0.35 * a, blur=5))
    draw_text(c, 'MASS AGENT', px + 22, y0 + 49, 'mono_medium', 14, TEXT, 0.85 * a, tracking=0.28, align='left')
    draw_text(c, '02:14:07', x1 - 40, y0 + 49, 'mono', 14, GREY, 0.9 * a, tracking=0.12, align='right')
    c.drawRect(skia.Rect.MakeLTRB(x0 + 1, y0 + 80, x1 - 1, y0 + 81), paint((1, 1, 1), 0.08 * a))
    # the request, typed
    req = 'Form my trading company in Abu Dhabi.'
    k = int(len(req) * ramp(t, *T.AGENT_TYPE))
    draw_text(c, '›', px, y0 + 142, 'display_light', 30, GOLD, a, align='left')
    draw_text(c, req[:k], px + 30, y0 + 142, 'display', 29, TEXT, a, tracking=-0.005, align='left')
    if k < len(req) or (int(t * 4) % 2 == 0 and t < T.CHECKS[0]):
        cw = text_width(req[:k], 'display', 29, -0.005)
        c.drawRect(skia.Rect.MakeXYWH(px + 32 + cw, y0 + 118, 2, 30), paint(GOLD, 0.9 * a))
    rows = [('Company formed', 'Abu Dhabi', '00:03:41'), ('Licence issued', '', '00:03:58'),
            ('Bank account opened', '', '00:04:09'), ('Screened', '23 compliance domains', '00:04:12')]
    for i, (lab, sub, tm) in enumerate(rows):
        tr = T.CHECKS[i]
        p = ease_out_cubic(ramp(t, tr, tr + 0.28))
        if p <= 0:
            continue
        ry = y0 + 222 + i * 66
        cx_, cy_ = px + 12, ry - 9
        c.drawCircle(cx_, cy_, 13, paint(GOLD, 0.9 * p * a, stroke=1.5))
        ck = ease_out_cubic(ramp(t, tr + 0.04, tr + 0.24))
        path = skia.Path()
        pts = [(cx_ - 6, cy_), (cx_ - 1.5, cy_ + 4.5), (cx_ + 6.5, cy_ - 5)]
        path.moveTo(*pts[0])
        if ck < 0.4:
            q = ck / 0.4
            path.lineTo(lerp(pts[0][0], pts[1][0], q), lerp(pts[0][1], pts[1][1], q))
        else:
            q = (ck - 0.4) / 0.6
            path.lineTo(*pts[1])
            path.lineTo(lerp(pts[1][0], pts[2][0], q), lerp(pts[1][1], pts[2][1], q))
        if ck > 0:
            c.drawPath(path, paint(GOLD, a, stroke=2.2))
        flash = math.exp(-(t - tr) * 10)
        c.drawCircle(cx_, cy_, 13 + 16 * (1 - flash), paint(GOLD, 0.5 * flash * a, stroke=1.2))
        dx = (1 - p) * 18
        draw_text(c, lab, px + 44 + dx, ry, 'display', 25, TEXT, p * a, align='left')
        if sub:
            lw = text_width(lab, 'display', 25)
            draw_text(c, '  ·  ' + sub, px + 44 + dx + lw, ry, 'display', 25, GREY, p * a, align='left')
        draw_text(c, tm, x1 - 40, ry, 'mono', 15, GREY, p * a, tracking=0.08, align='right')
    # live record strip
    pl = ease_out_cubic(ramp(t, T.CHECKS[-1] + 0.12, T.CHECKS[-1] + 0.4))
    if pl > 0:
        c.drawRect(skia.Rect.MakeLTRB(x0 + 1, y1 - 70, x1 - 1, y1 - 69), paint((1, 1, 1), 0.08 * a))
        pulse = 0.6 + 0.4 * math.sin(t * 9)
        c.drawCircle(px + 4, y1 - 36, 4, paint(GOLD, pl * a))
        c.drawCircle(px + 4, y1 - 36, 10, paint(GOLD, 0.4 * pl * a * pulse, blur=5))
        draw_text(c, 'LIVE RECORD  ·  AISHA TRADING LTD', px + 22, y1 - 31, 'mono_medium', 13, GOLD, pl * a * 0.95,
                  tracking=0.22, align='left')
    return composite(disp, L.rgba())


def shot7(t, fi):
    if t < T.S7_CUT:
        lin, _ = plate('karachi_skyline', t, T.S7[0], T.S7_CUT + 0.2, (0.5, 0.62), (0.52, 0.60), 1.08, 1.16, 0, 0,
                       WOB['s7a'], ease=lambda u: u)
        # day for night: pull exposure down, darken the sky's top
        ys = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
        lin = lin * (0.30 + 0.12 * ys) * np.array([0.78, 0.9, 1.0], np.float32)
        disp = finish(lin, 'nightblue', bloom_amt=0.12, hal=0.05, vig=0.55)
        L = Layer()
        c = L.c
        s1 = decode('KARACHI  ·  02:14', t, T.S7[0] + 0.12, 0.3, 3)
        s2 = decode('AISHA  —  FOUNDER', t, T.S7[0] + 0.25, 0.3, 4)
        draw_text(c, s1, 150, TOP + 96, 'mono_medium', 21, TEXT, 0.95, tracking=0.3, align='left')
        draw_text(c, s2, 150, TOP + 134, 'mono', 18, GOLD, 0.92, tracking=0.3, align='left')
        out = composite(disp, L.rgba())
    else:
        lin, _ = plate('keyboard_macro', t, T.S7_CUT, T.S7[1] + 0.2, (0.46, 0.44), (0.50, 0.42), 1.12, 1.22, -2.0, -1.2,
                       WOB['s7b'], ease=lambda u: u)
        ys = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
        screen_glow = np.exp(-ys * 2.6)[..., 0][..., None] * np.array([0.55, 0.62, 0.9], np.float32)
        lin = lin * 0.16 * np.array([0.8, 0.9, 1.05], np.float32) + lin * screen_glow * 0.55
        lin = lin * (1 + 0.25 * math.sin(t * 17) * 0.05)
        disp = finish(lin, 'nightblue', bloom_amt=0.12, hal=0.04, vig=0.5)
        disp = agent_panel(disp, t, fi)
        L = Layer()
        title(L.c, [('A company, ', GREY), ('born in minutes.', TEXT)], 150, BOT - 150, t, T.CHECKS[0] - 0.02, None,
              size=60)
        out = composite(disp, L.rgba())
    # flash carried over from the fly-through
    fl = math.exp(-max(0.0, t - T.S7[0]) * 11)
    return out * (1 - fl) + np.array([1.0, 0.96, 0.88], np.float32) * fl


LAYER_NAMES = ['REGISTRY', 'LICENCES & RULES', 'BANKING', 'ZONES', 'CORRIDORS', 'MARKETS']


def layer_geom(t, bx=1296, by=690, wdt=420, hgt=34, gap=58):
    sl = 0.403
    out = []
    for i, name in enumerate(LAYER_NAMES):
        ti = T.LAYERS[i]
        p = ease_out_cubic(ramp(t, ti, ti + 0.34))
        if p <= 0:
            continue
        y = by - i * gap - (1 - p) * 36
        path = skia.Path()
        path.moveTo(bx + sl * hgt, y - hgt)
        path.lineTo(bx + wdt + sl * hgt, y - hgt)
        path.lineTo(bx + wdt, y)
        path.lineTo(bx, y)
        path.close()
        out.append((i, name, ti, p, y, path))
    return out


def draw_layer_stack(disp, t, bx=1296, by=690, wdt=420, hgt=34, gap=58):
    sl = 0.403
    geo = layer_geom(t, bx, by, wdt, hgt, gap)
    for i, name, ti, p, y, path in geo:
        disp = frosted_path(disp, path, sigma=10, tint=(0.02, 0.03, 0.07), tint_a=0.55, alpha=p)
    L = Layer()
    c = L.c
    n = len(LAYER_NAMES)
    top_p = ease_out_cubic(ramp(t, T.LAYERS[0], T.LAYERS[-1] + 0.3))
    if geo:
        spine_top = by - (n - 1) * gap * top_p - hgt
        c.drawLine(bx - 30, by + 40, bx - 30, spine_top, paint(GOLD, 0.5, stroke=1.0))
    for i, name, ti, p, y, path in geo:
        c.drawLine(bx + sl * hgt, y - hgt, bx + wdt + sl * hgt, y - hgt, paint(GOLD, 0.95 * p, stroke=1.3))
        c.drawLine(bx, y, bx + wdt, y, paint((1, 1, 1), 0.22 * p, stroke=1.0))
        c.drawLine(bx + wdt, y, bx + wdt + sl * hgt, y - hgt, paint((1, 1, 1), 0.22 * p, stroke=1.0))
        c.drawLine(bx, y, bx + sl * hgt, y - hgt, paint((1, 1, 1), 0.22 * p, stroke=1.0))
        fl = math.exp(-(t - ti - 0.2) * 9) if t > ti + 0.2 else 0
        if fl > 0.01:
            c.drawLine(bx + sl * hgt, y - hgt, bx + wdt + sl * hgt, y - hgt, paint((1, 0.95, 0.8), fl, stroke=3, blur=4))
        draw_text(c, f'0{i + 1}', bx + 30, y - 11, 'mono_medium', 14, GOLD, p, tracking=0.1, align='left')
        draw_text(c, name, bx + 76, y - 11, 'text_medium', 16, TEXT, p, tracking=0.16, align='left')
        c.drawCircle(bx - 30, y - hgt / 2, 3, paint(GOLD, p))
    kp = ease_out_cubic(ramp(t, T.KEY_LOCK - 0.3, T.KEY_LOCK))
    if kp > 0:
        kx, ky = bx - 30, by + 62
        r = 20
        c.drawCircle(kx, ky, r, paint((0.02, 0.02, 0.05), 0.55 * kp))
        c.drawArc(skia.Rect.MakeXYWH(kx - r, ky - r, 2 * r, 2 * r), -90, 360 * kp, False, paint(GOLD, 0.95, stroke=1.4))
        sh = 6 * (1 - ease_out_back(ramp(t, T.KEY_LOCK - 0.08, T.KEY_LOCK + 0.1)))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(kx - 7, ky - 1, 14, 10), 2, 2), paint(GOLD, kp))
        shackle = skia.Path()
        shackle.moveTo(kx - 4.5, ky - 1)
        shackle.lineTo(kx - 4.5, ky - 5 - sh)
        shackle.arcTo(skia.Rect.MakeXYWH(kx - 4.5, ky - 9.5 - sh, 9, 9), 180, 180, False)
        shackle.lineTo(kx + 4.5, ky - 1 - sh * 0.4)
        c.drawPath(shackle, paint(GOLD, kp, stroke=1.8))
        fl = math.exp(-(t - T.KEY_LOCK) * 6) if t >= T.KEY_LOCK else 0
        if fl > 0.01:
            c.drawCircle(kx, ky, r + 30 * (1 - fl), paint(GOLD, 0.8 * fl, stroke=1.5))
            c.drawCircle(kx, ky, r, paint(GOLD, 0.35 * fl, blur=12))
        draw_text(c, decode('GOVERNMENT-HELD KEYS', t, T.KEY_LOCK - 0.05, 0.3, 9), kx + 40, ky + 5, 'mono_medium', 14,
                  GOLD, kp, tracking=0.26, align='left')
    return composite(disp, L.rgba())


def sky_grad(lin, top=0.62, until=0.55):
    """Graduated ND: darken the top of frame."""
    ys = np.linspace(0, 1, H, dtype=np.float32)
    g = top + (1 - top) * smooth_arr(np.clip(ys / until, 0, 1))
    return lin * g[:, None, None]


def smooth_arr(x):
    return x * x * (3 - 2 * x)


def shot8(t, fi):
    lin, _ = plate('abudhabi_dusk', t, T.S8[0], T.S8[1] + 0.2, (0.46, 0.43), (0.50, 0.42), 1.10, 1.17, 0, 0, WOB['s8'],
                   ease=lambda u: u)
    lin = sky_grad(lin * 0.92, 0.55, 0.6)
    lin = scrim(lin, 520, BOT - 150, 620, 150, 0.5)
    disp = finish(lin, 'bluehour', bloom_amt=0.25, bloom_th=0.62, hal=0.08, vig=0.5)
    disp = draw_layer_stack(disp, t)
    L2 = Layer()
    title(L2.c, [('Every rule runs as code.', TEXT)], 150, BOT - 178, t, T.LAYERS[0] - 0.02, None, size=58)
    title(L2.c, [('Governments hold the keys.', GOLD)], 150, BOT - 104, t, T.KEY_LOCK - 0.3, None, size=58)
    return composite(disp, L2.rgba())


SUEZ_TAGS = [((1180, 925), 'BILL OF LADING', 'VERIFIED', (-40, -250)),
             ((1540, 845), 'INVOICE #4471', 'SETTLED', (-60, -300)),
             ((1860, 1060), 'AED → PKR', 'SETTLED', (-300, -250))]


def shot9(t, fi):
    lin, M = plate('suez_canal', t, T.S9[0], T.S9[1] + 0.2, (0.55, 0.56), (0.54, 0.54), 1.06, 1.18, 0, 0, WOB['s9'],
                   ease=lambda u: u)
    disp = finish(lin * 0.95, 'dusk', bloom_amt=0.18, hal=0.08, vig=0.45)
    L = Layer()
    c = L.c
    # corridor along the canal to the horizon (plate coords are the 2x plate)
    near, far = map_pt(M, 800, 1366), map_pt(M, 1008, 678)
    dp = ease_out_cubic(ramp(t, T.S9[0] + 0.1, T.S9[0] + 0.75))
    if dp > 0:
        n = 60
        for k in range(n):
            s0, s1 = k / n, (k + 1) / n
            if s1 > dp:
                break
            xa, ya = lerp(near[0], far[0], s0), lerp(near[1], far[1], s0)
            xb, yb = lerp(near[0], far[0], s1), lerp(near[1], far[1], s1)
            wdt = lerp(3.2, 0.5, s0 ** 0.7)
            c.drawLine(xa, ya, xb, yb, paint(GOLD, 0.30, stroke=wdt * 4, blur=wdt * 2.2))
            c.drawLine(xa, ya, xb, yb, paint((1, 0.93, 0.75), 0.80, stroke=wdt * 0.55))
        for j in range(5):
            s = ((t - T.S9[0]) * 0.55 + j / 5) % 1.0
            if s > dp:
                continue
            s = s ** 1.6
            x, y = lerp(near[0], far[0], s), lerp(near[1], far[1], s)
            rr = lerp(5.5, 1.0, s)
            c.drawCircle(x, y, rr * 2.4, paint(GOLD, 0.35, blur=rr * 1.6))
            c.drawCircle(x, y, rr * 0.8, paint((1, 0.97, 0.88), 0.95))
    lay = L.rgba()
    disp = disp + lay[..., :3] * 0.9   # additive light over the plate
    # record tags pinned to the containers
    L2 = Layer()
    c2 = L2.c
    for i, ((px, py), a_txt, b_txt, off) in enumerate(SUEZ_TAGS):
        tt = T.TAGS[i]
        p = ease_out_cubic(ramp(t, tt, tt + 0.3))
        if p <= 0:
            continue
        ax, ay = map_pt(M, px, py)
        tw1 = text_width(a_txt, 'mono_medium', 14, 0.18)
        tw2 = text_width('✓ ' + b_txt, 'mono_medium', 14, 0.18)
        bw = tw1 + tw2 + 56
        lx, ly = ax + off[0], ay + off[1]
        ly = max(ly, TOP + 230)
        lx = min(lx, W - 60 - (bw - 16))
        c2.drawCircle(ax, ay, 5, paint(GOLD, p))
        c2.drawCircle(ax, ay, 5 + 14 * (1 - p), paint(GOLD, 0.7 * (1 - p), stroke=1.2))
        yl = lerp(ay, ly + 18, p)
        c2.drawLine(ax, ay, ax + (lx - ax) * p, yl, paint(GOLD, 0.8 * p, stroke=1.1))
        bx0, by0 = lx - 16, ly - 26
        disp = frosted(disp, (bx0, by0, bx0 + bw, by0 + 44), radius=10, sigma=14, tint=(0.02, 0.02, 0.05),
                       tint_a=0.55, alpha=p)
        c2.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(bx0, by0, bw, 44), 10, 10),
                     paint((1, 1, 1), 0.18 * p, stroke=1.0))
        draw_text(c2, decode(a_txt, t, tt, 0.3, i), lx, ly + 2, 'mono_medium', 14, TEXT, p, tracking=0.18, align='left')
        draw_text(c2, '✓ ' + b_txt, lx + tw1 + 24, ly + 2, 'mono_medium', 14, GOLD, p * ramp(t, tt + 0.25, tt + 0.35),
                  tracking=0.18, align='left')
    disp = composite(disp, L2.rgba())
    L3 = Layer()
    title(L3.c, [('Trade flows on ', TEXT), ('one live record.', GOLD)], 150, TOP + 118, t, T.S9[0] + 0.18, None, size=58)
    return composite(disp, L3.rgba())


# ----------------------------------------------------------------------------- Act III: Earth
EARTH_P = dict(s_sub=(16, 55), s_d=1.75, s_tg=(24.4, 54.4), s_tm=1.0, s_fov=40, s_roll=-4,
               e_sub=(-8, 64), e_d=2.25, e_tg=(34, 66), e_tm=0.80, e_fov=38, e_roll=-3)


def earth_cam(u):
    P = EARTH_P
    e = ease_in_out_cubic(u) * 0.7 + ease_out_cubic(u) * 0.3
    pos = G.normalize(lerp(G.ll_to_vec(*P['s_sub']), G.ll_to_vec(*P['e_sub']), e)) * lerp(P['s_d'], P['e_d'], e)
    tgt = lerp(G.ll_to_vec(*P['s_tg']) * P['s_tm'], G.ll_to_vec(*P['e_tg']) * P['e_tm'], e)
    return G.Cam(pos, tgt, fov_v=lerp(P['s_fov'], P['e_fov'], e), roll=lerp(P['s_roll'], P['e_roll'], e))


@functools.lru_cache(maxsize=1)
def earth_sun():
    ce = earth_cam(1.0)
    return G.normalize(ce.r * 0.80 + ce.f * 0.50 + ce.u * 0.25)


@functools.lru_cache(maxsize=1)
def corridors():
    hub = (T.HUB[1], T.HUB[2])
    by_name = {n[0]: (n[1], n[2]) for n in T.NODES}
    by_name[T.HUB[0]] = hub
    arcs = []
    for name, la, lo, ti, _ in T.NODES:
        arcs.append(dict(a=hub, b=(la, lo), t0=ti - T.ARC_TRAVEL, t1=ti, pts=G.arc_points(hub, (la, lo), 90), mesh=False))
    for a, b, ti in T.MESH:
        arcs.append(dict(a=by_name[a], b=by_name[b], t0=ti, t1=ti + 0.5,
                         pts=G.arc_points(by_name[a], by_name[b], 70), mesh=True))
    return arcs


def draw_network(c, cam, t):
    arcs = corridors()
    for k, arc in enumerate(arcs):
        dp = ease_in_out_cubic(ramp(t, arc['t0'], arc['t1']))
        if dp <= 0:
            continue
        pts = arc['pts']
        n = len(pts)
        proj = []
        for p in pts:
            pr = cam.project(p)
            proj.append(pr if (pr is not None and not cam.occluded(p)) else None)
        m = max(1, int(dp * (n - 1)))
        base_a = 0.42 if arc['mesh'] else 0.6
        for i in range(m):
            a_, b_ = proj[i], proj[i + 1]
            if a_ is None or b_ is None:
                continue
            s = i / (n - 1)
            head = math.exp(-((dp - s) * 9) ** 2) if dp < 1 else 0
            al = base_a * (0.55 + 0.45 * math.sin(math.pi * s)) + head * 0.6
            c.drawLine(a_[0], a_[1], b_[0], b_[1], paint(GOLD, al * 0.35, stroke=4.0, blur=3.0))
            c.drawLine(a_[0], a_[1], b_[0], b_[1], paint((1.0, 0.9, 0.7), al, stroke=1.25))
        if dp < 1:
            hp = proj[m]
            if hp is not None:
                c.drawCircle(hp[0], hp[1], 3.2, paint((1, 0.96, 0.85), 1.0))
                c.drawCircle(hp[0], hp[1], 10, paint(GOLD, 0.6, blur=6))
        else:
            # flows: pulses travel both ways along live corridors
            speed = 0.55 if not arc['mesh'] else 0.45
            for j in range(2):
                ph = ((t - arc['t1']) * speed + j * 0.5 + k * 0.137) % 1.0
                if j == 1:
                    ph = 1 - ph
                idx = int(ph * (n - 1))
                pp = proj[idx]
                if pp is None:
                    continue
                c.drawCircle(pp[0], pp[1], 2.4, paint((1, 0.97, 0.88), 0.95))
                c.drawCircle(pp[0], pp[1], 7, paint(GOLD, 0.45, blur=4))


def draw_nodes(c, cam, t, label_alpha=1.0):
    items = [(T.HUB[0], T.HUB[1], T.HUB[2], T.HUB_IGNITE, True, True)] + [(n, la, lo, ti, lb, False) for n, la, lo, ti, lb in T.NODES]
    lit = 0
    for name, la, lo, ti, show, hub in items:
        if t < ti:
            continue
        lit += 1
        p = G.ll_to_vec(la, lo)
        pr = cam.project(p * 1.002)
        if pr is None or cam.occluded(p * 1.002):
            continue
        x, y = pr[0], pr[1]
        dt = t - ti
        core = 3.6 if hub else 2.6
        c.drawCircle(x, y, core * 3.2, paint(GOLD, 0.35, blur=core * 2.2))
        c.drawCircle(x, y, core, paint((1, 0.97, 0.9), 1.0))
        c.drawCircle(x, y, core + 4.5, paint(GOLD, 0.75, stroke=1.0))
        rip = (dt % 1.6) / 1.6 if hub else min(1.0, dt / 0.9)
        ra = (1 - rip) * (0.9 if hub else 0.8)
        if ra > 0.02:
            c.drawCircle(x, y, core + 6 + rip * (46 if hub else 30), paint(GOLD, ra, stroke=1.2))
        fl = math.exp(-dt * 8)
        if fl > 0.02:
            c.drawCircle(x, y, 18, paint((1, 0.95, 0.8), 0.9 * fl, blur=10))
        if show and label_alpha > 0.01:
            la_ = label_alpha * ease_out_cubic(ramp(t, ti + 0.05, ti + 0.35))
            txt = decode(name, t, ti + 0.02, 0.32, sum(map(ord, name)) % 97)
            size = 17 if hub else 15
            col = GOLD if hub else TEXT
            c.drawLine(x + 7, y - 7, x + 16, y - 16, paint(col, 0.6 * la_, stroke=1.0))
            draw_text(c, txt, x + 20, y - 18, 'mono_medium', size, col, 0.9 * la_, tracking=0.22, align='left')
    return lit


def shot10(t, fi):
    t0, t1 = T.S10
    u = ramp(t, t0, t1)
    cam = earth_cam(u)
    lin, hit = G.render_earth(cam, sun_dir=earth_sun(), terrain_gain=0.78, lights_gain=3.2,
                              star_shift=(u * -60, u * 40))
    # the world wakes: overall lights swell as the network grows
    L = Layer()
    c = L.c
    draw_network(c, cam, t)
    lit = draw_nodes(c, cam, t, label_alpha=1.0 - 0.5 * smooth(ramp(t, 22.4, 23.3)))
    lay = L.rgba()
    lin = lin + lin_from_layer(lay, 1.35)
    intro = smooth(ramp(t, t0, t0 + 0.25))
    lin = lin * (0.25 + 0.75 * intro)
    disp = finish(lin, 'neutral', bloom_amt=0.42, bloom_th=0.62, hal=0.05, vig=0.35, ca=0.0012)
    # HUD
    H2 = Layer()
    h = H2.c
    ha = smooth(ramp(t, t0 + 0.6, t0 + 1.0)) * (1 - smooth(ramp(t, 23.2, 23.5)))
    if ha > 0:
        bar = bar_px(t)
        draw_text(h, 'SOVEREIGN NODES', 150, bar + 84, 'mono', 15, GREY, ha, tracking=0.28, align='left')
        draw_text(h, f'{lit:02d}', 150, bar + 134, 'mono_light', 44, TEXT, ha, tracking=0.04, align='left')
        live = sum(1 for a in corridors() if t >= a['t1'])
        draw_text(h, 'CORRIDORS', 470, bar + 84, 'mono', 15, GREY, ha, tracking=0.28, align='left')
        draw_text(h, f'{live:02d}', 470, bar + 134, 'mono_light', 44, TEXT, ha, tracking=0.04, align='left')
    title(h, [('Every nation, ', TEXT), ('a sovereign node.', GOLD)], W / 2, H - 118, t, T.EARTH_TITLE1[0],
          T.EARTH_TITLE1[1], size=60, align='center')
    title(h, [('Connected into ', TEXT), ('one economy.', GOLD)], W / 2, H - 118, t, T.EARTH_TITLE2[0],
          T.EARTH_TITLE2[1], size=60, align='center')
    return composite(disp, H2.rgba())


# ----------------------------------------------------------------------------- montage + end
MONTAGE = [('marina_aerial_night', 'Formed.', 'DOMAIN · 01  FORMATION', (0.5, 0.52), 'night'),
           ('difc_gate_night', 'Licensed.', 'DOMAIN · 02  LICENSING', (0.52, 0.45), 'night'),
           ('marina_night', 'Banked.', 'DOMAIN · 03  BANKING', (0.5, 0.55), 'night'),
           ('hk_containers', 'Recognised.', 'DOMAIN · 04  CORRIDORS', (0.55, 0.55), 'dusk')]


def shot11(t, fi):
    i = min(3, max(0, int((t - T.S11[0]) / 0.5)))
    t0 = T.MONTAGE[i]
    name, word, tag, ctr, look = MONTAGE[i]
    u = ramp(t, t0, t0 + 0.5)
    lin, _ = plate(name, t, t0, t0 + 0.5, (ctr[0] - 0.01, ctr[1]), (ctr[0] + 0.01, ctr[1] - 0.01), 1.10, 1.22, 0, 0,
                   WOB['m'], ease=ease_out_cubic)
    hit = math.exp(-(t - t0) * 16)
    lin = lin * (0.55 + 0.9 * hit)
    lin = scrim(lin, W / 2, H / 2 + 40, 640, 200, 0.55)
    disp = finish(lin, look, bloom_amt=0.3, bloom_th=0.65, hal=0.1, vig=0.55)
    L = Layer()
    c = L.c
    p = ease_out_expo(ramp(t, t0, t0 + 0.18))
    size = 150
    draw_text(c, word, W / 2, H / 2 + 50 + (1 - p) * 14, 'display_semibold', size, (0, 0, 0), 0.4 * p, tracking=-0.03,
              blur=18)
    draw_text(c, word, W / 2, H / 2 + 50 + (1 - p) * 14, 'display_semibold', size, TEXT, p, tracking=-0.03)
    draw_text(c, tag, W / 2, H / 2 + 132, 'mono_medium', 19, GOLD, p * 0.95, tracking=0.32)
    return composite(disp, L.rgba())


@functools.lru_cache(maxsize=1)
def dust_band(n=9000, seed=31):
    """The mass.inc hero motif: a sweeping band of fine dust, gold -> rose -> ice blue."""
    rng = np.random.default_rng(seed)
    u = rng.uniform(-0.08, 1.08, n)                     # position along the band (left -> right)
    x = u * W
    centre = H * 0.80 - 150 * np.sin(u * math.pi * 0.9 + 0.25) + 40 * np.sin(u * 7.0)
    spread = 30 + 70 * np.abs(rng.standard_normal(n)) ** 1.4
    y = centre + rng.standard_normal(n) * spread * 0.55
    gold = np.array([1.0, 0.80, 0.46])
    rose = np.array([1.0, 0.52, 0.62])
    ice = np.array([0.62, 0.78, 1.0])
    k = np.clip(u, 0, 1)[:, None]
    col = np.where(k < 0.5, gold + (rose - gold) * (k / 0.5), rose + (ice - rose) * ((k - 0.5) / 0.5)).astype(np.float32)
    col = col * rng.uniform(0.85, 1.15, (n, 1)).astype(np.float32)
    size = rng.uniform(0.45, 1.15, n)
    bright = rng.pareto(3.0, n) * 0.35 + 0.18
    size[bright > 1.2] *= 1.6
    core = np.exp(-((y - centre) / (spread * 0.6)) ** 2)
    b = np.clip(bright * (0.35 + 0.65 * core), 0, 1.6)
    ph = rng.uniform(0, 6.28, n)
    vx = rng.normal(10, 5, n)
    vy = rng.normal(-2, 3, n)
    return x, y, col, size, b, ph, vx, vy


@functools.lru_cache(maxsize=1)
def end_background():
    xs = (np.arange(W, dtype=np.float32) - W / 2) / 900
    ys = (np.arange(H, dtype=np.float32) - H * 0.46) / 520
    g = np.exp(-(ys[:, None] ** 2 + xs[None, :] ** 2))
    base = srgb_to_lin(INK)
    return base[None, None, :] + g[..., None] * np.array([0.010, 0.007, 0.016], np.float32)


def shot12(t, fi):
    t0 = T.FINAL_HIT
    dt = t - t0
    lin = end_background().copy()
    x, y, col, size, b, ph, vx, vy = dust_band()
    L = Layer()
    c = L.c
    grow = ease_out_expo(ramp(t, t0, t0 + 1.6))
    # the band sweeps in from the left and settles
    reveal_x = lerp(-200, W + 200, ease_out_cubic(ramp(t, t0 - 0.1, t0 + 1.4)))
    for i in range(len(x)):
        if x[i] > reveal_x:
            continue
        px = x[i] + vx[i] * dt
        py = y[i] + vy[i] * dt
        a = b[i] * (0.6 + 0.4 * math.sin(t * 1.9 + ph[i]))
        edge = clamp((reveal_x - x[i]) / 240)
        a *= edge
        if a < 0.02:
            continue
        c.drawCircle(px, py, size[i], paint(col[i], clamp(a)))
    dust = lin_from_layer(L.rgba(), 1.0)
    lin = lin + dust * 1.6 + gblur(dust, 5) * 2.4 + gblur(dust, 26) * 3.0
    # the closing strike echoes the reveal: a brief anamorphic streak and a tight burst at the mark
    burst = math.exp(-max(0.0, dt) / 0.08) * (dt >= 0)
    mh_, ws_ = 96, 58
    tot_ = mark_width() * mh_ + mh_ * 0.62 + text_width('MASS', 'display_medium', ws_, 0.52)
    mcx, mcy = W / 2 - tot_ / 2 + mark_width() * mh_ / 2, 360 + mh_ * 0.5
    lin = lin + radial(mcx, mcy, 150)[..., None] * np.array([1.0, 0.8, 0.5], np.float32) * burst * 0.9
    lin = anamorphic_streak(lin, mcx, mcy, 0.7 * math.exp(-max(0.0, dt) * 3.5) * (dt >= 0), length=700)
    disp = finish(lin, 'neutral', bloom_amt=0.3, bloom_th=0.35, hal=0.0, vig=0.35, ca=0.0)
    # lockup: mark + wordmark, as in the site header
    L2 = Layer()
    c2 = L2.c
    mh = 96
    mw = mark_width() * mh
    word_size = 58
    ww = text_width('MASS', 'display_medium', word_size, 0.52)
    gap = mh * 0.62
    total = mw + gap + ww
    x0 = W / 2 - total / 2
    y0 = 360
    starts = [t0 + 0.02, t0 + 0.08, t0 + 0.14]
    mark_layer(c2, x0, y0, mh, t, starts, fill_col=(1, 1, 1), sweep_t=ramp(t, t0 + 0.7, t0 + 1.4), glow=0.0)
    pw = ease_out_cubic(ramp(t, t0 + 0.2, t0 + 0.9))
    if pw > 0:
        draw_text(c2, 'MASS', x0 + mw + gap, y0 + mh * 0.5 + word_size * 0.36, 'display_medium', word_size, TEXT, pw,
                  tracking=lerp(0.8, 0.52, pw), align='left')
    title(c2, [('The operating system for ', TEXT), ('sovereign economies.', GOLD)], W / 2, 596, t, T.TAGLINE_IN, None,
          size=48, align='center', stagger=0.012, shadow=0.0)
    pu = ease_out_cubic(ramp(t, T.URL_IN, T.URL_IN + 0.5))
    if pu > 0:
        draw_text(c2, 'mass.inc', W / 2, 676, 'mono', 21, TEXT, 0.72 * pu, tracking=0.3)
    lay = L2.rgba()
    glow = gblur(lay[..., 3], 30) * 0.10
    disp = disp + glow[..., None] * np.array([1.0, 0.85, 0.6], np.float32) * 0.5
    disp = composite(disp, lay)
    fade = 1 - smooth(ramp(t, *T.FADE_OUT))
    return disp * fade


# ----------------------------------------------------------------------------- dispatcher
SHOTS = [(T.S1, shot1), (T.S2, shot2), (T.S3, shot3), (T.S4, shot4), (T.S5, shot5), (T.S6, shot6), (T.S7, shot7),
         (T.S8, shot8), (T.S9, shot9), (T.S10, shot10), (T.S11, shot11), (T.S12, shot12)]

GRAIN = [(0.0, 0.050), (8.05, 0.028), (9.5, 0.032), (11.5, 0.038), (17.5, 0.020), (23.5, 0.040), (25.5, 0.016)]


def bar_px(t):
    if t < T.S10[0]:
        return BAR_239
    return BAR_239 * (1 - ease_in_out_cubic(ramp(t, T.S10[0] + 0.1, T.S10[0] + 1.2)))


def grain_amt(t):
    g = GRAIN[0][1]
    for tt, a in GRAIN:
        if t >= tt:
            g = a
    return g


def frame(t, fi):
    img = None
    for (a, b), fn in SHOTS:
        if a <= t < b:
            img = fn(t, fi)
            break
    if img is None:
        img = black()
    img = grain(img, fi, amount=grain_amt(t))
    img = letterbox(img, bar_px(t), color=(0, 0, 0))
    return np.clip(img, 0, 1)
