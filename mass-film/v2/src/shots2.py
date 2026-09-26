"""The 2-minute film, shot by shot. Every cut and animation is keyed to the narration via
timeline2 (scratch or final take). Frames are display-space RGB float32, 1920x1080."""
import functools
import math
import os
import sys

import cv2
import numpy as np
import skia

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), 'src'))

from engine import (W, H, INK, GOLD, TEXT, GREY, LABEL, RED, PAPER, clamp, lerp, ramp, smooth,  # noqa: E402
                    ease_out_cubic, ease_in_cubic, ease_in_out_cubic, ease_out_expo, ease_in_expo, ease_out_back,
                    lin_to_srgb, srgb_to_lin, soft_clip, grade, load_photo, camera, gblur, lens_blur, bloom,
                    vignette, grain, letterbox, bars_for_aspect, Layer, paint, draw_text, text_width, composite,
                    frosted, placed_mark, mark_width)
import shots as V1  # noqa: E402  (v1 looks, stamp, reveal, globe helpers)
import globe as G  # noqa: E402
from timeline2 import Timeline  # noqa: E402
from plates import plate  # noqa: E402
from ui2 import (UIFrame, Chat, chat_panel, licensing_console, ministry_dashboard, systems_wall,  # noqa: E402
                 lower_third, pulse, rr, label, check_icon, spinner, appear, mark_icon, seal, GREEN, AMBER)
import canvas as CV  # noqa: E402

TL = Timeline(os.environ.get('MASS_VO', 'scratch'))
DUR = TL.duration
BAR = bars_for_aspect(2.39)


def L(sec, i):
    return TL[(sec, i)]


def disp(lin, look='neutral', **kw):
    return V1.finish(lin, look, **kw)


def lin_layer(layer):
    return V1.lin_from_layer(layer.rgba())


# --------------------------------------------------------------------------- shared pieces
@functools.lru_cache(maxsize=16)
def stamp_tex(word, sub):
    w, h = 1000, 420
    Lr = Layer(w, h)
    c = Lr.c
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(22, 22, 956, 376), 30, 30), paint((1, 1, 1), 1, stroke=18))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(50, 50, 900, 320), 16, 16), paint((1, 1, 1), 1, stroke=5))
    size = 196 if len(word) <= 7 else int(196 * 7 / len(word))
    draw_text(c, word, 500, 250, 'typewriter_bold', size, (1, 1, 1), tracking=0.05)
    draw_text(c, sub, 500, 334, 'typewriter_bold', 30, (1, 1, 1), tracking=0.10)
    a = Lr.arr[..., 3].astype(np.float32) / 255
    rng = np.random.default_rng(len(word) * 7 + len(sub))
    n1 = cv2.resize(rng.random((h // 50 + 1, w // 50 + 1)).astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC)
    n2 = cv2.resize(rng.random((h // 8, w // 8)).astype(np.float32), (w, h), interpolation=cv2.INTER_LINEAR)
    n3 = rng.random((h, w)).astype(np.float32)
    dens = np.clip(0.45 + 0.55 * n1 + 0.3 * n2, 0, 1)
    holes = (cv2.GaussianBlur(n3, (0, 0), 1.2) > 0.43).astype(np.float32) * 0.35 + 0.65
    return cv2.GaussianBlur(np.clip(a * dens * holes * 1.1, 0, 1), (0, 0), 0.7)


def stamp_on(lin, t, t_hit, word, sub, cx=W * 0.52, cy=H * 0.5, ang=-7.0, scale=0.9, col=(0.5, 0.035, 0.03)):
    """Composite an ink stamp landing at t_hit (screen space), with the approach shadow."""
    dt = t - t_hit
    if dt < -0.14:
        return lin
    tex = stamp_tex(word, sub)
    sh, sw = tex.shape
    if dt < 0:
        k = 1 + dt / 0.14
        s = scale * (1.3 - 0.3 * k)
        A = cv2.getRotationMatrix2D((sw / 2, sh / 2), -ang, s)
        A[:, 2] += (cx - sw / 2, cy - sh / 2)
        box = cv2.warpAffine(np.ones((sh, sw), np.float32), A, (W, H))
        return lin * (1 - 0.5 * k * gblur(box, 30 * (1 - k) + 10)[..., None])
    s = scale * (1 + 0.02 * math.exp(-dt * 12))
    A = cv2.getRotationMatrix2D((sw / 2, sh / 2), -ang, s)
    A[:, 2] += (cx - sw / 2, cy - sh / 2)
    ink = gblur(cv2.warpAffine(tex, A, (W, H)), 1.4 * math.exp(-dt * 6) + 0.4)
    a = np.clip(ink * 0.92, 0, 1)[..., None]
    return lin * (1 - a) + lin * a * np.asarray(col, np.float32) * 1.6


DOCS = [
    ('REGISTRY OF COMPANIES', 'APPLICATION FOR INCORPORATION', 'FORM 0047/26',
     [('Proposed name of company', 'NOOR LOGISTICS LLC'), ('Registered office', 'Unit 4, Block 7, Industrial Area'),
      ('Shareholder(s)', 'S. RAHMAN (60%)   A. MALIK (40%)'), ('Nature of business', 'Freight forwarding'),
      ('Share capital', '250,000'), ('Certified copies attached', 'Passport, proof of address')]),
    ('LICENSING AUTHORITY', 'TRADE LICENCE APPLICATION', 'FORM B',
     [('Licence type', 'General trading'), ('Office lease (attested)', 'Ref. 88213 / notarised'),
      ('No-objection letter', 'Pending from sponsor'), ('Activity code', '4690.01'),
      ('Manager', 'F. HADDAD'), ('Previous applications', '2 (returned)')]),
    ('COMMERCIAL BANK', 'BUSINESS ACCOUNT OPENING · KYC', 'REF KYC-2291',
     [('Legal name', 'KHAN TEXTILES (PVT) LTD'), ('Source of funds', 'Retained earnings'),
      ('Ultimate beneficial owner', 'R. KHAN'), ('Board resolution', 'Attached (certified)'),
      ('Proof of address', 'Utility bill, < 3 months'), ('Expected monthly volume', '1,200,000')]),
]


@functools.lru_cache(maxsize=3)
def paper_doc(v):
    """A close-up of a paper form (linear RGB, 2560x1440) for the stamps to land on."""
    w, h = 2560, 1440
    rng = np.random.default_rng(40 + v)
    n1 = cv2.resize(rng.random((9, 16)).astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC)
    n2 = cv2.GaussianBlur(rng.random((h, w)).astype(np.float32), (0, 0), 0.8)
    fib = cv2.GaussianBlur(rng.random((h // 2, w // 8)).astype(np.float32), (0, 0), 0.6)
    fib = cv2.resize(fib, (w, h), interpolation=cv2.INTER_LINEAR)
    base = np.array([0.93, 0.895, 0.815], np.float32) * (0.96 + 0.06 * n1[..., None] + 0.025 * n2[..., None]
                                                          + 0.02 * fib[..., None])
    Lr = Layer(w, h)
    c = Lr.c
    ink = (0.16, 0.15, 0.14)
    org, title, form, fields = DOCS[v]
    draw_text(c, org, 260, 250, 'typewriter_bold', 64, ink, 0.92, align='left', tracking=0.08)
    draw_text(c, title, 260, 330, 'typewriter', 46, ink, 0.85, align='left', tracking=0.06)
    draw_text(c, form, w - 260, 250, 'typewriter_bold', 46, ink, 0.8, align='right', tracking=0.06)
    c.drawRect(skia.Rect.MakeXYWH(260, 372, w - 520, 4), paint(ink, 0.8))
    for j, (lab, val) in enumerate(fields):
        y = 500 + j * 150
        draw_text(c, f'{j + 1}.  {lab.upper()}', 260, y, 'typewriter', 34, ink, 0.7, align='left', tracking=0.04)
        c.drawRect(skia.Rect.MakeXYWH(260, y + 70, w - 520, 2), paint(ink, 0.45))
        draw_text(c, val, 330, y + 58, 'typewriter_bold', 44, (0.08, 0.1, 0.22), 0.88, align='left', tracking=0.03)
    a = Lr.rgba()
    ink_a = cv2.GaussianBlur(a[..., 3], (0, 0), 0.9) * (0.85 + 0.15 * n2)
    lin = base * (1 - ink_a[..., None]) + srgb_to_lin(a[..., :3]) * ink_a[..., None]
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    light = 1.05 - 0.35 * ((xs / w - 0.25) ** 2 + (ys / h - 0.15) ** 2)
    lin = lin * light[..., None]
    lin = srgb_to_lin(np.clip(lin, 0, 1)) * 0.85
    # shallow depth of field toward the top and bottom
    dof = np.clip(np.abs(ys / h - 0.5) * 2.2 - 0.35, 0, 1)[..., None]
    return (lin * (1 - dof) + gblur(lin, 5) * dof).astype(np.float32)


def shake(t, t_hit, amp=14.0):
    dt = t - t_hit
    if dt < 0:
        return (0.0, 0.0)
    e = math.exp(-dt * 9)
    return (amp * 0.35 * e * math.sin(dt * 57), amp * e * math.sin(dt * 69))


def loc_card(c, t, t0, text, x=120, y=None, size=20, color=TEXT, alpha=1.0, t1=None):
    """Mono location/time card that decodes in."""
    y = BAR + 92 if y is None else y
    if t < t0:
        return
    out = 1.0 if t1 is None else 1 - smooth(ramp(t, t1 - 0.3, t1))
    s = V1.decode(text, t, t0, 0.45, sum(map(ord, text)) % 97)
    label(c, s, x, y, size, color, alpha * out, tracking=0.3)
    ln = 48 * ease_out_expo(ramp(t, t0, t0 + 0.5))
    c.drawRect(skia.Rect.MakeXYWH(x, y + 16, ln, 2), paint(GOLD, alpha * out))


def window(c, x, y, w, h, title, alpha=1.0, accent=None):
    """A generic 'legacy portal' window chrome."""
    c.drawRRect(rr(x, y, w, h, 14), paint((0.09, 0.09, 0.12), 0.94 * alpha))
    c.drawRRect(rr(x, y, w, h, 14), paint((1, 1, 1), 0.16 * alpha, stroke=1.0))
    c.drawRect(skia.Rect.MakeXYWH(x + 1, y + 1, w - 2, 40), paint((1, 1, 1), 0.05 * alpha))
    for k in range(3):
        c.drawCircle(x + 20 + k * 16, y + 21, 5, paint((1, 1, 1), 0.22 * alpha))
    label(c, title, x + 76, y + 27, 14, accent if accent is not None else TEXT, alpha, tracking=0.18)


def upload_dialog(c, t, t0, x, y, org, alpha=1.0, fail_at=None):
    """'Upload your passport' again: dropzone, progress, then 'resubmit'."""
    p = appear(t, t0, 0.3)
    if p <= 0:
        return
    a = alpha * p
    w, h = 440, 250
    y = y + (1 - p) * 20
    window(c, x, y, w, h, org, a)
    draw_text(c, 'Upload your passport', x + 28, y + 90, 'text_semibold', 26, TEXT, a, align='left')
    label(c, 'CERTIFIED COPY · NOTARISED · MAX 2 MB', x + 28, y + 122, 13, GREY, a, tracking=0.16)
    dz = skia.Paint(AntiAlias=True, Color4f=skia.Color4f(1, 1, 1, 0.3 * a), Style=skia.Paint.kStroke_Style,
                    StrokeWidth=1.4)
    dz.setPathEffect(skia.DashPathEffect.Make([8.0, 6.0], 0.0))
    c.drawRRect(rr(x + 28, y + 144, w - 56, 60, 10), dz)
    prog = clamp((t - t0 - 0.3) / 1.2)
    c.drawRect(skia.Rect.MakeXYWH(x + 28, y + 222, (w - 56), 4), paint((1, 1, 1), 0.12 * a))
    c.drawRect(skia.Rect.MakeXYWH(x + 28, y + 222, (w - 56) * prog, 4), paint(GOLD, 0.9 * a))
    if fail_at is not None and t >= fail_at:
        fa = appear(t, fail_at, 0.2)
        c.drawRRect(rr(x + 28, y + 150, w - 56, 48, 10), paint(RED, 0.18 * a * fa))
        label(c, 'DOCUMENT REJECTED · PLEASE RESUBMIT', x + 44, y + 180, 14, (1.0, 0.45, 0.4), a * fa, tracking=0.14)


# --------------------------------------------------------------------------- OPEN
def seg_open(t, fi):
    l0, l1, l2 = L('open', 0), L('open', 1), L('open', 2)
    t_job, t_ship = l0.word('job'), l0.word('shipment')
    t_prove = l2.word('prove')
    t_again1, t_again2 = l2.word('Again'), l2.word('again', 1)
    stamps = [(t_prove, 'PENDING', 'REGISTRY OFFICE · FILE 0047/26'),
              (t_again1, 'RETURNED', 'LICENSING · INCOMPLETE'),
              (t_again2, 'RESUBMIT', 'BANK · COMPLIANCE REVIEW')]
    flurry = [l2.end + 0.10 + k * (0.20 - k * 0.022) for k in range(6)]
    flurry_words = [('REJECTED', 'CUSTOMS'), ('PENDING', 'NOTARY'), ('RECEIVED', 'ZONE 07'), ('RETURNED', 'CHAMBER'),
                    ('PENDING', 'TAX'), ('ON HOLD', 'VISAS')]
    end = L('aisha', 0).start
    if t < t_job:
        lin = plate('handshake', t, 0, t_job, (0.5, 0.52), (0.52, 0.5), 1.06, 1.16)
        lin = lin * smooth(ramp(t, 0.1, 1.2))
        return disp(lin, 'gold', bloom_amt=0.2, hal=0.12, vig=0.5)
    if t < t_ship:
        return disp(plate('welder', t, t_job, t_ship, (0.5, 0.5), (0.5, 0.48), 1.08, 1.14), 'gold', bloom_amt=0.35,
                    hal=0.2, vig=0.5)
    if t < l1.start:
        return disp(plate('cranes', t, t_ship, l1.start, (0.5, 0.55), (0.54, 0.52), 1.05, 1.12), 'dusk',
                    bloom_amt=0.2, vig=0.45)
    if t < t_prove - 0.14:
        return disp(plate('pen_sign', t, l1.start, t_prove, (0.52, 0.5), (0.5, 0.46), 1.12, 1.24), 'paper',
                    bloom_amt=0.2, hal=0.15, vig=0.55)
    # stamps: each a new document, landing on the words
    hits = [(s[0], s[1], s[2]) for s in stamps] + [(tf, w_, s_) for tf, (w_, s_) in zip(flurry, flurry_words)]
    k = max(i for i, h in enumerate(hits) if t >= h[0] - 0.14 or i == 0)
    th, word, sub = hits[k]
    t_next = hits[k + 1][0] - 0.14 if k + 1 < len(hits) else end
    if t >= flurry[-1] + 0.35:
        return np.zeros((H, W, 3), np.float32)
    sx, sy = shake(t, th, 16 if k < 3 else 10)
    rng = np.random.default_rng(k * 13 + 5)
    cx0, cy0 = rng.uniform(0.40, 0.62), rng.uniform(0.38, 0.62)
    u_ = ease_in_out_cubic(ramp(t, th - 0.14, t_next))
    z_ = lerp(1.25 + 0.1 * (k % 3), 1.32 + 0.1 * (k % 3), u_)
    lin = camera(paper_doc(k % 3), cx0 + 0.01 * u_, cy0 - 0.01 * u_, z_, rng.uniform(-3, 3))
    lin = np.roll(lin, (int(sy), int(sx)), axis=(0, 1)) if (sx or sy) else lin
    lin = stamp_on(lin, t, th, word, sub, cx=W * rng.uniform(0.44, 0.58), cy=H * rng.uniform(0.42, 0.58),
                   ang=rng.uniform(-12, 8), scale=0.95 if k < 3 else 0.8)
    return disp(lin, 'paper', bloom_amt=0.18, hal=0.14, vig=0.6)


# --------------------------------------------------------------------------- AISHA
PORTALS = [('COMPANY REGISTRY · NEW ENTITY', ['Proposed name', 'Shareholders', 'Registered address', 'Activity code']),
           ('LICENSING · APPLICATION FORM B', ['Licence type', 'Office lease (attested)', 'No-objection letter']),
           ('BANK · BUSINESS ACCOUNT', ['Source of funds', 'Proof of address', 'Board resolution'])]


def seg_aisha(t, fi):
    l0, l1, l2, l3 = L('aisha', 0), L('aisha', 1), L('aisha', 2), L('aisha', 3)
    t_aisha = l0.word('Aisha')
    t_again = l3.word('again')
    end = L('omar', 0).start
    if t < t_aisha:
        lin = plate('karachi_night', t, l0.start, t_aisha + 0.4, (0.5, 0.58), (0.52, 0.56), 1.06, 1.12)
        if 'karachi_night' not in _clips():
            ys = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
            lin = lin * (0.28 + 0.12 * ys) * np.array([0.78, 0.9, 1.0], np.float32)
        d = disp(lin, 'nightblue', bloom_amt=0.2, vig=0.55)
        Lr = Layer()
        loc_card(Lr.c, t, l0.start + 0.05, 'KARACHI · 02:14')
        return composite(d, Lr.rgba())
    if t < l1.start:
        lin = plate('aisha_night', t, t_aisha, l1.start + 0.3, (0.5, 0.5), (0.52, 0.48), 1.08, 1.16)
        if 'aisha_night' not in _clips():
            lin = lin * 0.3 * np.array([0.8, 0.9, 1.05], np.float32)
        d = disp(lin, 'nightblue', bloom_amt=0.2, vig=0.55)
        ui = UIFrame()
        lower_third(ui, t, t_aisha, 'Aisha', 'Founder', 'Karachi · 02:14', y=H - BAR - 90)
        # her product is done
        ta = t_aisha + 0.9
        p = appear(t, ta, 0.4)
        if p > 0:
            ui.glass(W - 620, BAR + 70, 500, 104, 22, p, tint_a=0.6)
            check_icon(ui.c, W - 580, BAR + 122, 14, ramp(t, ta + 0.2, ta + 0.5), GREEN, p)
            draw_text(ui.c, 'Build complete · v1.0', W - 550, BAR + 116, 'text_semibold', 24, TEXT, p, align='left')
            label(ui.c, 'READY TO SELL', W - 550, BAR + 148, 14, GREEN, p, tracking=0.22)
        return ui.apply(d)
    if t < l3.start:
        # the paperwork maze: portals pile up, the same passport upload again and again, days climb
        lin = plate('forms', t, l1.start, l3.start, (0.5, 0.5), (0.5, 0.52), 1.1, 1.18)
        d = disp(lin * 0.55, 'fluoro', bloom_amt=0.1, vig=0.6)
        ui = UIFrame()
        c = ui.c
        for k, (title_, fields) in enumerate(PORTALS):
            tk = l1.start + 0.15 + k * 0.45
            p = appear(t, tk, 0.3)
            if p <= 0:
                continue
            x, y = 180 + k * 210, BAR + 90 + k * 60
            window(c, x, y, 600, 330, title_, p)
            for j, f in enumerate(fields):
                fy = y + 84 + j * 56
                label(c, f.upper(), x + 28, fy, 13, GREY, p, tracking=0.16)
                c.drawRRect(rr(x + 28, fy + 10, 544, 30, 6), paint((1, 1, 1), 0.06 * p))
                if (j + k) % 3 == 1 and t > tk + 0.6:
                    label(c, 'REQUIRED', x + 480, fy, 12, (1.0, 0.45, 0.4), p, tracking=0.16)
        orgs = ['COMPANY REGISTRY', 'LICENSING OFFICE', 'BANK · ONBOARDING', 'SECOND BANK · KYC']
        words = ['same', 'office', 'bank', 'bank']
        for k, (org, wd) in enumerate(zip(orgs, words)):
            try:
                tw = l2.word(wd, 1 if (wd == 'bank' and k == 3) else 0)
            except KeyError:
                tw = l2.start + k * 0.8
            if k == 3:
                tw = l2.end - 0.1
            upload_dialog(c, t, tw - 0.1, 980 + (k % 2) * 60 - k * 20, BAR + 150 + k * 95, org, 1.0,
                          fail_at=tw + 0.9 if k in (0, 2) else None)
        Lr = ui.layer
        days = 1 + int(96 * ramp(t, l1.start, l3.start) ** 1.6)
        V1.day_counter(c, t, days, 1440, H - BAR - 150, 1.0, prog=0.03 + 0.02 * ramp(t, l1.start, l3.start), fi=fi)
        return ui.apply(d)
    # the border: back to zero
    glitch = 1.0 if 0 <= t - t_again < 0.26 else 0.0
    lin = plate('passport_control', t, l3.start, end, (0.5, 0.66), (0.5, 0.63), 1.24, 1.32)
    if glitch:
        rng = np.random.default_rng(fi)
        lin = lin.copy()
        for _ in range(7):
            y0 = int(rng.uniform(0, H - 60))
            hgt = int(rng.uniform(8, 60))
            lin[y0:y0 + hgt] = np.roll(lin[y0:y0 + hgt], int(rng.uniform(-60, 60)), axis=1)
        lin[..., 0] = np.roll(lin[..., 0], 9, axis=1)
        lin[..., 2] = np.roll(lin[..., 2], -9, axis=1)
    d = disp(lin * 0.9, 'customs', bloom_amt=0.2, vig=0.55)
    Lr = Layer()
    c = Lr.c
    if t < t_again:
        V1.day_counter(c, t, 97 + int((t - l3.start) * 7), 150, BAR + 196, 1.0, prog=0.05, fi=fi)
    else:
        V1.day_counter(c, t, 0, 150, BAR + 196, 1.0, status='START AGAIN', status_col=RED, glitch=glitch, prog=0.0, fi=fi)
    loc_card(c, t, l3.start + 0.1, 'NEXT COUNTRY · NEW REGISTRY', x=W - 700, color=TEXT)
    out = composite(d, Lr.rgba())
    return out * (1 - smooth(ramp(t, end - 0.25, end)))


@functools.lru_cache(maxsize=1)
def _clips():
    import plates as P
    return set(P.manifest().keys())


# --------------------------------------------------------------------------- OMAR
def seg_omar(t, fi):
    l0, l1 = L('omar', 0), L('omar', 1)
    t_omar = l0.word('Mariam')
    t_ret, t_rec, t_wait = l1.word('retypes'), l1.word('Re-checks'), l1.word('waits')
    end = L('ministry', 0).start
    if t < t_omar:
        lin = plate('abudhabi_morning', t, l0.start - 0.2, t_omar + 0.3, (0.46, 0.44), (0.5, 0.42), 1.08, 1.14)
        d = disp(V1.sky_grad(lin, 0.6, 0.6), 'bluehour', bloom_amt=0.2, vig=0.5)
        Lr = Layer()
        loc_card(Lr.c, t, l0.start + 0.05, 'ABU DHABI · FREE ZONE · 09:12')
        return composite(d, Lr.rgba())
    lin = plate('omar_desk', t, t_omar, end, (0.5, 0.5), (0.53, 0.5), 1.08, 1.16)
    if 'omar_desk' not in _clips():
        lin = lin * 0.45
    d = disp(lin, 'dusk', bloom_amt=0.15, vig=0.55)
    ui = UIFrame()
    c = ui.c
    lower_third(ui, t, t_omar, 'Mariam', 'Licensing officer', 'Abu Dhabi free zone', y=H - BAR - 90)
    if t >= l1.start - 0.2:
        # three systems that don't talk to each other, stacked right of her
        systems = ['REGISTRY', 'BANK PORTAL', 'MINISTRY UPLOAD']
        fields = [('Company name', 'Aisha Trading LLC'), ('Owner', 'Aisha Khan'), ('Passport no.', 'AB1234567'),
                  ('Activity', 'Commodity trading')]
        x, ww, hh = 1170, 620, 196
        ys = [BAR + 34, BAR + 34 + hh + 48, BAR + 34 + 2 * (hh + 48)]
        for k, nm in enumerate(systems):
            p = appear(t, l1.start - 0.2 + k * 0.18, 0.3)
            if p <= 0:
                continue
            y = ys[k]
            window(c, x, y, ww, hh, nm, p)
            for j, (f, val) in enumerate(fields):
                fx, fy = x + 24 + (j % 2) * 298, y + 76 + (j // 2) * 58
                label(c, f.upper(), fx, fy, 12, GREY, p, tracking=0.16)
                c.drawRRect(rr(fx, fy + 8, 274, 30, 6), paint((1, 1, 1), 0.06 * p))
                tt0 = t_ret + k * 0.35 + j * 0.12
                n = int(len(val) * clamp((t - tt0) / 0.5))
                if n > 0:
                    draw_text(c, val[:n], fx + 10, fy + 29, 'mono', 16, TEXT, p, align='left')
                    if n < len(val) and int(t * 6) % 2 == 0:
                        c.drawRect(skia.Rect.MakeXYWH(fx + 12 + text_width(val[:n], 'mono', 16), fy + 14, 2, 18),
                                   paint(GOLD, p))
            # status strip: retyped, re-checked, waiting
            sy = y + 27
            if t >= t_wait - 0.1:
                label(c, f'WAITING ON {3 - k if k < 2 else 2} SYSTEMS', x + ww - 24, sy, 12, AMBER, p, align='right',
                      tracking=0.18)
            elif t >= t_rec:
                spinner(c, x + ww - 44 - text_width(f'RE-CHECKING · ATTEMPT {3 + k}', 'mono_medium', 12, 0.18), sy - 5, 7,
                        t + k * 0.3, AMBER, p)
                label(c, f'RE-CHECKING · ATTEMPT {3 + k}', x + ww - 24, sy, 12, AMBER, p, align='right', tracking=0.18)
            if k < 2:
                # a link that never connects
                xm, ya, yb = x + ww / 2, y + hh + 6, ys[k + 1] - 6
                c.drawLine(xm, ya, xm, ya + (yb - ya) * 0.3, paint(RED, 0.8 * p, stroke=1.6))
                c.drawLine(xm, ya + (yb - ya) * 0.7, xm, yb, paint(RED, 0.8 * p, stroke=1.6))
                cy_ = (ya + yb) / 2
                c.drawLine(xm - 7, cy_ - 7, xm + 7, cy_ + 7, paint(RED, p, stroke=2))
                c.drawLine(xm - 7, cy_ + 7, xm + 7, cy_ - 7, paint(RED, p, stroke=2))
        # the queue only grows
        if t >= t_wait - 0.1:
            p = appear(t, t_wait - 0.1, 0.3)
            q = 1284 + int(max(0.0, t - t_wait) * 11)
            ui.glass(120, BAR + 34, 330, 132, 18, p, tint_a=0.66)
            label(c, 'IN REVIEW', 146, BAR + 72, 14, GREY, p, tracking=0.24)
            draw_text(c, f'{q:,}', 146, BAR + 138, 'display_light', 52, TEXT, p, align='left')
            label(c, '↑', 146 + text_width(f'{q:,}', 'display_light', 52) + 14, BAR + 132, 22, AMBER, p)
    return ui.apply(d)


# --------------------------------------------------------------------------- MINISTRY
def seg_ministry(t, fi):
    l0, l1 = L('ministry', 0), L('ministry', 1)
    end = L('peak', 0).start
    t_econ, t_every = l0.word('economy'), l1.word('Every')
    if t < t_econ:
        lin = plate('ministry_building', t, l0.start - 0.2, t_econ, (0.5, 0.52), (0.5, 0.5), 1.06, 1.12)
        d = disp(lin * 1.1, 'night', bloom_amt=0.3, vig=0.5)
        Lr = Layer()
        loc_card(Lr.c, t, l0.start + 0.05, 'THE MINISTRY · 18:40')
        return composite(d, Lr.rgba())
    # the real room: a wall of screens that never agree
    room = plate('ministry_room', t, t_econ, end, (0.46, 0.42), (0.42, 0.36), 1.04, 1.34)
    if t < t_every - 0.3:
        return disp(room, 'night', bloom_amt=0.25, vig=0.55)
    # match cut: the screens become the graphic wall, pulling back to dozens of stale systems
    u = ease_in_out_cubic(ramp(t, t_every - 0.3, end - 0.3))
    zoom = lerp(2.6, 0.82, u)
    mix = smooth(ramp(t, t_every - 0.3, t_every + 0.2))
    base = lens_blur(room, 6 * mix) * lerp(1.0, 0.18, mix)
    base = disp(base, 'night', bloom_amt=0.2, vig=0.6)
    ui = UIFrame()
    systems_wall(ui, t, t_every - 0.3, zoom=zoom, cx=W / 2 + lerp(380, 0, u), cy=H / 2 + lerp(160, 0, u), alpha=mix)
    return ui.apply(base)


# --------------------------------------------------------------------------- PEAK
def seg_peak(t, fi):
    l0 = L('peak', 0)
    t_held = l0.word('Held')
    if t >= l0.end + 0.05:
        return np.zeros((H, W, 3), np.float32)
    if t < t_held:
        # three worlds side by side, links failing between them
        cam = CV.blend_cam(CV.Cam(CV.overview_cam().cx, CV.overview_cam().cy, CV.overview_cam().zoom * 1.12),
                           CV.overview_cam(), ramp(t, l0.start, t_held))
        panels = [dict(plate=lambda tt, n=n, lk=lk: disp(plate(n, tt, l0.start, t_held + 1, z0=1.05, z1=1.1) *
                                                         (0.45 if n not in _clips() else 1.0), lk, vig=0.4),
                       title=tl, sub=sb)
                  for n, lk, tl, sb in (('aisha_tired', 'nightblue', 'Aisha', 'Founder · Karachi'),
                                        ('officers_papers', 'dusk', 'Mariam', 'Licensing officer · Abu Dhabi'),
                                        ('ministry_room', 'night', 'The ministry', 'Economy · Abu Dhabi'))]
        img = CV.draw_panels(t, cam, panels)
        Lr = Layer()
        c = Lr.c
        for a_i in range(2):
            pa = cam.to_screen(CV.panel_origin(a_i)[0] + W, H / 2)
            pb = cam.to_screen(CV.panel_origin(a_i + 1)[0], H / 2)
            tk = l0.start + 0.5 + a_i * 0.5
            u = clamp((t - tk) / 0.5)
            if u > 0:
                mx = lerp(pa[0], pb[0], 0.5 * u)
                c.drawLine(pa[0], pa[1], mx, pa[1], paint(RED if u >= 1 else GOLD, 0.9, stroke=2))
                if u >= 1:
                    c.drawCircle(mx, pa[1], 6, paint(RED, 1.0))
        return composite(img, Lr.rgba())
    # accelerating intercut of everything that holds them back
    memories = [('open', L('open', 2).word('prove') + 0.3), ('aisha', L('aisha', 2).start + 1.2),
                ('omar', L('omar', 1).word('retypes') + 0.8), ('aisha', L('aisha', 3).word('again') + 0.05),
                ('ministry', L('ministry', 1).start + 1.5), ('open', L('open', 2).word('again', 1) + 0.2),
                ('omar', L('omar', 1).word('waits') + 0.5), ('aisha', L('aisha', 1).start + 0.8)]
    span = l0.end - t_held
    # cut lengths shrink geometrically
    cuts, acc, d = [], t_held, 0.42
    while acc < l0.end:
        cuts.append(acc)
        acc += d
        d = max(0.07, d * 0.8)
    k = max(i for i, c0 in enumerate(cuts) if t >= c0)
    seg, tm = memories[k % len(memories)]
    tt = tm + (t - cuts[k])
    img = SEG_FN[seg](tt, fi)
    z = 1.0 + 0.08 * ramp(t, t_held, l0.end)
    M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, z)
    img = cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    g = img.mean(-1, keepdims=True)
    img = img * 0.6 + g * 0.4
    return img * (1 + 0.25 * math.exp(-(t - cuts[k]) * 20))


# --------------------------------------------------------------------------- TURN
RECORD_FIELDS = [('Owners', 'Aisha Khan · 100%'), ('Licence', 'General trading · active'),
                 ('Bank account', 'Open'), ('Compliance', '23 of 23 checks')]
TRUST_POINTS = [('REGISTRY', -0.72, -0.62), ('BANK', 0.74, -0.58), ('REGULATOR', -0.8, 0.55), ('CUSTOMS', 0.8, 0.6),
                ('PARTNER NATION', 0.0, 0.9)]


def seg_turn(t, fi):
    l0, l1 = L('turn', 0), L('turn', 1)
    t_created, t_trusted = l1.word('Created'), l1.word('Trusted')
    end = L('reveal', 0).start - 0.2
    lin = np.zeros((H, W, 3), np.float32)
    Lr = Layer()
    c = Lr.c
    cx, cy = W / 2, H / 2
    # a point of light
    pp = appear(t, l0.start + 0.4, 0.8)
    card = ease_out_cubic(ramp(t, l1.start, l1.start + 0.7))
    collapse = ease_in_expo(ramp(t, end - 0.45, end))
    breathe = 0.85 + 0.15 * math.sin(t * 3.2)
    r = (6 + 3 * breathe) * (1 - card) * pp
    if r > 0.3:
        c.drawCircle(cx, cy, r, paint((1, 0.96, 0.86), 1.0))
        c.drawCircle(cx, cy, r * 6, paint(GOLD, 0.35 * pp, blur=20))
    if card > 0:
        cw, ch = lerp(40, 760, card), lerp(40, 470, card)
        cw, ch = lerp(cw, 30, collapse), lerp(ch, 30, collapse)
        a = card * (1 - collapse)
        x, y = cx - cw / 2, cy - ch / 2
        c.drawRRect(rr(x, y, cw, ch, 28), paint((0.04, 0.035, 0.07), 0.9 * a))
        c.drawRRect(rr(x, y, cw, ch, 28), paint(GOLD, 0.6 * a, stroke=1.6))
        c.drawRRect(rr(x, y, cw, ch, 28), paint(GOLD, 0.25 * a, stroke=6, blur=10))
        if card > 0.9 and collapse < 0.2:
            fa = a * clamp((card - 0.9) * 10)
            label(c, 'COMPANY RECORD · LIVE', x + 40, y + 60, 16, GOLD, fa, tracking=0.3)
            pulse_ = 0.6 + 0.4 * math.sin(t * 7)
            c.drawCircle(x + cw - 50, y + 54, 6, paint(GOLD, fa))
            c.drawCircle(x + cw - 50, y + 54, 14, paint(GOLD, 0.35 * fa * pulse_, blur=5))
            draw_text(c, 'Aisha Trading LLC', x + 40, y + 124, 'display_semibold', 44, TEXT, fa, align='left')
            for j, (k_, v_) in enumerate(RECORD_FIELDS):
                tj = t_created + j * 0.28
                pj = appear(t, tj, 0.3) * fa
                if pj <= 0:
                    continue
                ry = y + 196 + j * 62
                check_icon(c, x + 56, ry - 8, 13, ramp(t, tj, tj + 0.3), GOLD, pj)
                draw_text(c, k_, x + 88, ry, 'text', 27, GREY, pj, align='left')
                draw_text(c, v_, x + cw - 40, ry, 'text_medium', 27, TEXT, pj, align='right')
        # trusted everywhere: lines out to the institutions
        if t >= t_trusted and collapse < 1:
            for j, (nm, px, py) in enumerate(TRUST_POINTS):
                tj = t_trusted + j * 0.12
                u = ease_out_cubic(ramp(t, tj, tj + 0.5)) * (1 - collapse)
                if u <= 0:
                    continue
                ex, ey = cx + px * 860, cy + py * 470
                sx, sy = cx + px * cw / 2 * 0.98, cy + py * ch / 2 * 0.98
                c.drawLine(sx, sy, lerp(sx, ex, u), lerp(sy, ey, u), paint(GOLD, 0.7 * u, stroke=1.4))
                if u > 0.95:
                    c.drawCircle(ex, ey, 5, paint(GOLD, u))
                    c.drawCircle(ex, ey, 16, paint(GOLD, 0.3 * u, blur=6))
                    label(c, nm, ex, ey + (36 if py > 0 else -20), 19, TEXT, u, align='center', tracking=0.24)
    lin = lin + lin_layer(Lr) * 1.2
    return disp(lin, 'neutral', bloom_amt=0.4, bloom_th=0.5, hal=0.0, vig=0.3, ca=0.0)


# --------------------------------------------------------------------------- REVEAL
def seg_reveal(t, fi):
    t0 = L('reveal', 0).word('Mass') - 0.06          # the strike lands on "Mass"
    t1 = L('demo', 0).start - 0.3
    if t < t0:
        # "This is —": the collapsed record, a point of light gathering itself
        Lr = Layer()
        c = Lr.c
        u = ramp(t, L('reveal', 0).start - 0.2, t0)
        r = 5 + 3 * math.sin(t * 9) * (1 - u) + 10 * u ** 3
        c.drawCircle(W / 2, H / 2, r, paint((1, 0.96, 0.86), 1.0))
        c.drawCircle(W / 2, H / 2, r * (5 + 6 * u ** 2), paint(GOLD, 0.25 + 0.35 * u ** 2, blur=14 + 30 * u))
        lin = lin_layer(Lr) * 1.3
        return disp(lin, 'neutral', bloom_amt=0.5, bloom_th=0.4, hal=0.0, vig=0.3, ca=0.0)
    dt = max(0.0, t - t0 - 0.16)                      # flash once the third stroke lands
    lin = plate('abudhabi_sunset', t, t0, t1 + 0.5, (0.5, 0.5), (0.51, 0.48), 1.18, 1.28)
    bg = smooth(ramp(t, t0 + 0.35, t0 + 1.35))
    lin = lens_blur(lin, lerp(14, 5, ramp(t, t0 + 0.2, t0 + 1.8))) * (0.42 * bg)
    Lr = Layer()
    c = Lr.c
    mh = 128
    mx = W / 2 - mark_width() * mh / 2
    my = 318
    V1.mark_layer(c, mx, my, mh, t, [t0, t0 + 0.08, t0 + 0.16], fill_col=(1.0, 0.985, 0.96),
                  sweep_t=ramp(t, t0 + 0.62, t0 + 1.25), glow=0.0)
    pw = ease_out_cubic(ramp(t, t0 + 0.42, t0 + 1.2))
    if pw > 0:
        draw_text(c, 'MASS', W / 2, 560, 'display_medium', 50, TEXT, pw, tracking=lerp(0.95, 0.52, pw))
    ps = ease_out_cubic(ramp(t, t0 + 0.8, t0 + 1.35))
    if ps > 0:
        draw_text(c, 'MANAGED ADMINISTRATIVE & SOVEREIGN SERVICES', W / 2, 616, 'mono', 18, GOLD, ps * 0.95,
                  tracking=lerp(0.5, 0.3, ps))
    lay = Lr.rgba()
    glow = gblur(lay[..., 3], 40) * 0.12 + gblur(lay[..., 3], 120) * 0.10
    lin = lin + glow[..., None] * np.array([1.0, 0.78, 0.45], np.float32)
    burst = math.exp(-dt / 0.09) * (t >= t0 + 0.16)
    cy_ = my + mh * 0.55
    lin = lin + V1.radial(W / 2, cy_, 260)[..., None] * np.array([1.0, 0.78, 0.45], np.float32) * burst * 1.1
    lin = V1.anamorphic_streak(lin, W / 2, cy_, 0.9 * math.exp(-dt * 3.2) * (t >= t0 + 0.16) + 0.03)
    d = disp(lin, 'gold', bloom_amt=0.35, bloom_th=0.6, hal=0.1, vig=0.5, ca=0.0)
    out = composite(d, lay)
    return out * (1 - smooth(ramp(t, t1 - 0.25, t1)))


# --------------------------------------------------------------------------- DEMO (three-way)
def demo_times():
    d = [L('demo', i).start for i in range(6)]
    return dict(d=d, file=L('demo', 1).word('filing'), decide=L('demo', 2).word('decides'),
                live=L('demo', 4).word('live'), change=L('demo', 5).word('changes'), same=L('demo', 5).word('same'),
                end=L('trust', 0).start - 0.2, start=L('demo', 0).start - 0.3)


@functools.lru_cache(maxsize=1)
def demo_chat():
    T_ = demo_times()
    d0 = T_['d'][0]
    tf = T_['file']
    d3 = T_['d'][3]
    return Chat([
        dict(who='user', t=d0 + 0.1, text="I'm launching an AI trading company. Can you set it up in Abu Dhabi?"),
        dict(who='agent', t=d0 + 1.7, text="On it. I'll form the company, apply for your licence and open a bank account. Who owns it?"),
        dict(who='user', t=d0 + 4.0, text="Just me. Here's my passport."),
        dict(who='user', t=d0 + 4.5, kind='passport', scan=d0 + 4.8),
        dict(who='agent', t=tf - 2.2, kind='checks', title='PREPARING YOUR FILING',
             items=[('Ownership recorded', tf - 1.8), ('Documents complete', tf - 1.3), ('23 compliance checks passed', tf - 0.7),
                    ('Filed with Abu Dhabi free zone', tf)]),
        dict(who='agent', t=d3 + 0.25, kind='result', typing=False, company='Aisha Trading LLC',
             items=[('Company formed', d3 + 0.5), ('Licence issued', d3 + 0.8), ('Bank account open', d3 + 1.1)],
             elapsed='4 MIN 12 S'),
    ])


def demo_cams():
    T_ = demo_times()
    f0, f1, f2, ov = CV.focus_cam(0), CV.focus_cam(1), CV.focus_cam(2), CV.overview_cam()
    d = T_['d']
    return [(T_['start'], f0), (T_['file'] + 0.35, f0), (T_['file'] + 1.25, ov), (d[2] - 0.45, ov), (d[2] + 0.45, f1),
            (T_['decide'] + 0.75, f1), (T_['decide'] + 1.55, ov), (d[3] - 0.25, ov), (d[3] + 0.55, f0),
            (d[4] - 0.55, f0), (d[4] - 0.05, ov), (d[4] + 0.5, f2), (T_['same'] - 0.1, f2), (T_['same'] + 0.9, ov)]


def seg_demo(t, fi):
    T_ = demo_times()
    d = T_['d']
    chat = demo_chat()
    st_console = dict(arrive=T_['file'] + 1.8, review=d[2] + 0.5, approve=T_['decide'], seal=T_['decide'] + 0.12,
                      cleared=T_['decide'] + 0.5, queue=(1, 0), clock='09:31 GST', avg='3 min')
    st_min = dict(new_company=T_['live'], rule=T_['change'], rule_card=d[5] - 0.35, base=1284)
    arrive_b = T_['file'] + 1.8
    back = T_['decide'] + 1.0

    def hl(ts):
        return lambda tt: max([math.exp(-max(0.0, tt - x) * 3.5) * (tt >= x) for x in ts] + [0.0])

    def aisha_ui(ui, tt):
        chat_panel(ui, tt, chat, 980, 70, 860, 940, clock='10:31')
        lower_third(ui, tt, T_['start'] + 0.2, 'Aisha', 'Founder', 'Karachi · 10:31', y=H - 110)
        t_mnm = L('demo', 3).word('business') - 0.1
        ma = appear(tt, t_mnm, 0.5)
        if ma > 0:
            V1.title(ui.c, [('Minutes. ', TEXT), ('Not months.', GOLD)], 120, 250, tt, t_mnm, None,
                     size=76, key='display_semibold', tracking=-0.02)

    def omar_ui(ui, tt):
        licensing_console(ui, tt, 1000, 80, 820, 920, st_console)
        lower_third(ui, tt, d[2] - 0.2, 'Mariam', 'Licensing officer', 'Abu Dhabi free zone · 09:31', y=H - 110)

    def ministry_ui(ui, tt):
        ministry_dashboard(ui, tt, 960, 70, 880, 940, st_min)
        lower_third(ui, tt, d[4] - 0.4, 'The ministry', 'Economy, live', 'Abu Dhabi · 09:35', y=H - 110)

    def pl(name, look, dark=0.55):
        return lambda tt: disp(plate(name, tt, T_['start'], T_['end'], (0.42, 0.5), (0.45, 0.5), 1.06, 1.12) *
                               (dark if name not in _clips() else 0.62), look, bloom_amt=0.15, vig=0.55)

    panels = [dict(plate=pl('aisha_day', 'dusk'), ui=aisha_ui, title='Aisha', sub='Founder · Karachi',
                   highlight=hl([back + 0.8, T_['same'] + 0.6])),
              dict(plate=pl('omar_day', 'bluehour'), ui=omar_ui, title='Mariam', sub='Licensing officer · Abu Dhabi',
                   highlight=hl([arrive_b, T_['same'] + 0.45])),
              dict(plate=pl('ministry_office', 'night'), ui=ministry_ui, title='The ministry', sub='Economy · live',
                   highlight=hl([back + 0.8, T_['same']]))]
    links = [(0, 1, T_['file'] + 0.9, 0.9), (1, 0, back, 0.8), (1, 2, back, 0.8), (0, 2, d[4] - 0.5, 0.7)]
    cam = CV.cam_path(t, demo_cams())
    img = CV.draw_panels(t, cam, panels, links)
    # the rule ripples out of the ministry across every panel
    if t >= T_['same'] - 0.1:
        Lr = Layer()
        u = t - (T_['same'] - 0.1)
        cxs, cys = cam.to_screen(*CV.panel_center(2))
        r = u * 2600 * cam.zoom
        a = clamp(1 - u / 1.6)
        if a > 0:
            Lr.c.drawCircle(cxs, cys, r, paint(GOLD, 0.8 * a, stroke=3.0))
            Lr.c.drawCircle(cxs, cys, r, paint(GOLD, 0.3 * a, stroke=14, blur=10))
            img = composite(img, Lr.rgba())
    fade_in = smooth(ramp(t, T_['start'], T_['start'] + 0.35))
    return img * fade_in


# --------------------------------------------------------------------------- TRUST
PAY_CHECKS = ['Sanctions screening', 'Licence covers this trade', 'Payment limits', 'Beneficiary verified']
LAYERS = ['REGISTRY', 'LICENCES & RULES', 'BANKING', 'ZONES', 'CORRIDORS', 'MARKETS']


def seg_trust(t, fi):
    l0, l1 = L('trust', 0), L('trust', 1)
    end = L('network', 0).start - 0.1
    if t < l1.start - 0.15:
        lin = plate('aisha_day', t, l0.start - 0.2, l1.start, (0.40, 0.30), (0.42, 0.31), 1.03, 1.07)
        d = disp(lens_blur(lin, 4) * (0.5 if 'aisha_day' not in _clips() else 0.7), 'dusk', vig=0.5)
        ui = UIFrame()
        c = ui.c
        x, y, w, h = W - 120 - 860, 150, 860, 700
        p = appear(t, l0.start - 0.2, 0.4)
        ui.glass(x, y, w, h, 30, p, tint_a=0.7)
        label(c, 'PAYMENT · AISHA TRADING LLC', x + 40, y + 60, 16, GREY, p, tracking=0.24)
        draw_text(c, 'Karachi Steel Co.', x + 40, y + 130, 'display_semibold', 44, TEXT, p, align='left')
        draw_text(c, 'AED 48,000', x + w - 40, y + 130, 'display_light', 44, TEXT, p, align='right')
        c.drawRect(skia.Rect.MakeXYWH(x + 1, y + 170, w - 2, 1), paint((1, 1, 1), 0.08 * p))
        label(c, 'CHECKED BEFORE IT MOVES', x + 40, y + 222, 15, GOLD, p, tracking=0.26)
        t_before = l0.word('before')
        for j, nm in enumerate(PAY_CHECKS):
            tj = l0.start + 0.3 + j * (t_before - l0.start) / len(PAY_CHECKS)
            ry = y + 286 + j * 62
            if t < tj:
                V1_spin = spinner(c, x + 58, ry - 9, 13, t, GOLD, p * 0.9)
                draw_text(c, nm, x + 92, ry, 'text', 28, GREY, p, align='left')
            else:
                check_icon(c, x + 58, ry - 9, 13, ramp(t, tj, tj + 0.3), GOLD, p)
                draw_text(c, nm, x + 92, ry, 'text', 28, TEXT, p, align='left')
        ts = l0.end - 0.1
        ps = appear(t, ts, 0.35)
        if ps > 0:
            c.drawRRect(rr(x + 40, y + h - 130, w - 80, 88, 20), paint(GOLD, 0.12 * p * ps))
            c.drawRRect(rr(x + 40, y + h - 130, w - 80, 88, 20), paint(GOLD, 0.5 * p * ps, stroke=1.2))
            draw_text(c, 'Sent', x + 74, y + h - 74, 'text_semibold', 30, TEXT, p * ps, align='left')
            label(c, 'PROOF 7F3A·91C2·E04B · VERIFIABLE BY ANY AUTHORITY', x + w - 70, y + h - 78, 14, GOLD, p * ps,
                  align='right', tracking=0.16)
        return ui.apply(d)
    # sovereign by design: the stack locks under the nation's keys
    lin = plate('flag', t, l1.start - 0.2, end, (0.42, 0.45), (0.46, 0.43), 1.08, 1.16)
    xs_ = np.linspace(0, 1, W, dtype=np.float32)[None, :, None]
    lin = lin * (0.9 - 0.45 * np.clip((xs_ - 0.5) * 2.5, 0, 1))
    lin = V1.scrim(lin, 520, H - 210, 640, 160, 0.5)
    d = disp(lin, 'bluehour', bloom_amt=0.25, bloom_th=0.62, hal=0.08, vig=0.5)
    ui = UIFrame()
    c = ui.c
    t_infra, t_keys = l1.word('infrastructure'), l1.word('keys')
    bx, by, wdt, hgt, gap = 1160, 850, 560, 48, 80
    sl = 0.403
    for i, nm in enumerate(LAYERS):
        ti = l1.start + 0.1 + i * (t_infra - l1.start + 0.6) / len(LAYERS)
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
        d = frosted_path_local(d, path, p)
        c.drawLine(bx + sl * hgt, y - hgt, bx + wdt + sl * hgt, y - hgt, paint(GOLD, 0.95 * p, stroke=1.3))
        c.drawLine(bx, y, bx + wdt, y, paint((1, 1, 1), 0.22 * p, stroke=1.0))
        draw_text(c, f'0{i + 1}', bx + 34, y - 14, 'mono_medium', 18, GOLD, p, tracking=0.1, align='left')
        draw_text(c, nm, bx + 90, y - 14, 'text_medium', 21, TEXT, p, tracking=0.16, align='left')
    kp = ease_out_cubic(ramp(t, t_keys - 0.35, t_keys))
    if kp > 0:
        kx, ky = bx + wdt / 2 + 10, by + 70
        c.drawCircle(kx, ky, 26, paint((0.02, 0.02, 0.05), 0.55 * kp))
        c.drawArc(skia.Rect.MakeXYWH(kx - 26, ky - 26, 52, 52), -90, 360 * kp, False, paint(GOLD, 0.95, stroke=1.6))
        shk = 7 * (1 - ease_out_back(ramp(t, t_keys - 0.08, t_keys + 0.1)))
        c.drawRRect(rr(kx - 9, ky - 1, 18, 13, 3), paint(GOLD, kp))
        sp_ = skia.Path()
        sp_.moveTo(kx - 6, ky - 1)
        sp_.lineTo(kx - 6, ky - 6 - shk)
        sp_.arcTo(skia.Rect.MakeXYWH(kx - 6, ky - 12 - shk, 12, 12), 180, 180, False)
        sp_.lineTo(kx + 6, ky - 1 - shk * 0.4)
        c.drawPath(sp_, paint(GOLD, kp, stroke=2.2))
        fl = math.exp(-(t - t_keys) * 6) if t >= t_keys else 0
        if fl > 0.01:
            c.drawCircle(kx, ky, 26 + 40 * (1 - fl), paint(GOLD, 0.8 * fl, stroke=1.6))
        label(c, V1.decode('GOVERNMENT NODE · NATIONAL KEYS', t, t_keys - 0.1, 0.35, 9), kx, ky + 62, 15, GOLD, kp,
              align='center', tracking=0.26)
    return ui.apply(d)


def frosted_path_local(base, path, alpha):
    from engine import frosted_path
    return frosted_path(base, path, sigma=10, tint=(0.02, 0.03, 0.07), tint_a=0.55, alpha=alpha)


# --------------------------------------------------------------------------- NETWORK
NET_NODES = [  # name, lat, lon, label
    ('KARACHI', 24.86, 67.00, 'PAKISTAN'), ('MUMBAI', 19.08, 72.88, 'INDIA'), ('RIYADH', 24.71, 46.68, 'SAUDI ARABIA'),
    ('ISTANBUL', 41.01, 28.98, 'TÜRKIYE'), ('CAIRO', 30.04, 31.24, 'EGYPT'), ('DHAKA', 23.81, 90.41, 'BANGLADESH'),
    ('JAKARTA', -6.21, 106.85, 'INDONESIA'), ('HO CHI MINH CITY', 10.82, 106.63, 'VIETNAM'),
    ('LONDON', 51.51, -0.13, 'UNITED KINGDOM'), ('KUALA LUMPUR', 3.14, 101.69, 'MALAYSIA'),
    ('MANILA', 14.60, 120.98, 'PHILIPPINES'), ('SHANGHAI', 31.23, 121.47, 'CHINA'), ('SEOUL', 37.57, 126.98, 'KOREA')]
HUB = (24.45, 54.38)


def net_schedule():
    l0, l1, l2 = L('network', 0), L('network', 1), L('network', 2)
    t_hub = l0.start + 0.8
    t_kar = l1.word('joins')
    words = [l2.word('laws'), l2.word('data'), l2.word('keys')]
    times = {'KARACHI': t_kar + 0.5}
    rest = [n[0] for n in NET_NODES[1:]]
    for k, nm in enumerate(rest):
        grp = min(2, k // 4)
        times[nm] = words[grp] + 0.12 * (k % 4) + 0.3
    mesh_t = l2.word('Together')
    mesh = [('LONDON', 'ISTANBUL'), ('ISTANBUL', 'CAIRO'), ('RIYADH', 'CAIRO'), ('DHAKA', 'JAKARTA'),
            ('JAKARTA', 'HO CHI MINH CITY'), ('MANILA', 'SEOUL'), ('SEOUL', 'SHANGHAI'), ('MUMBAI', 'DHAKA'),
            ('KUALA LUMPUR', 'MANILA'), ('KARACHI', 'MUMBAI')]
    return t_hub, times, [(a, b, mesh_t + 0.08 * i) for i, (a, b) in enumerate(mesh)]


@functools.lru_cache(maxsize=1)
def net_arcs():
    t_hub, times, mesh = net_schedule()
    ll = {n[0]: (n[1], n[2]) for n in NET_NODES}
    arcs = [dict(b=nm, t0=times[nm] - 0.55, t1=times[nm], pts=G.arc_points(HUB, ll[nm], 90), mesh=False) for nm in times]
    arcs += [dict(b=b, t0=tm, t1=tm + 0.5, pts=G.arc_points(ll[a], ll[b], 70), mesh=True) for a, b, tm in mesh]
    return arcs


def seg_network(t, fi):
    l0 = L('network', 0)
    t0, t1 = l0.start - 0.1, L('close', 0).start - 0.1
    u = ramp(t, t0, t1)
    cam = V1.earth_cam(u)
    lin, hit = G.render_earth(cam, sun_dir=V1.earth_sun(), terrain_gain=0.78, lights_gain=3.2,
                              star_shift=(u * -60, u * 40))
    t_hub, times, mesh = net_schedule()
    Lr = Layer()
    c = Lr.c
    # corridors
    for k, arc in enumerate(net_arcs()):
        dp = ease_in_out_cubic(ramp(t, arc['t0'], arc['t1']))
        if dp <= 0:
            continue
        proj = []
        for p in arc['pts']:
            pr = cam.project(p)
            proj.append(pr if (pr is not None and not cam.occluded(p)) else None)
        n = len(proj)
        m = max(1, int(dp * (n - 1)))
        base_a = 0.42 if arc['mesh'] else 0.62
        for i in range(m):
            a_, b_ = proj[i], proj[i + 1]
            if a_ is None or b_ is None:
                continue
            s = i / (n - 1)
            al = base_a * (0.55 + 0.45 * math.sin(math.pi * s))
            c.drawLine(a_[0], a_[1], b_[0], b_[1], paint(GOLD, al * 0.35, stroke=4.0, blur=3.0))
            c.drawLine(a_[0], a_[1], b_[0], b_[1], paint((1.0, 0.9, 0.7), al, stroke=1.3))
        if dp >= 1:
            ph = ((t - arc['t1']) * 0.5 + k * 0.137) % 1.0
            pp = proj[int(ph * (n - 1))]
            if pp is not None:
                c.drawCircle(pp[0], pp[1], 2.4, paint((1, 0.97, 0.88), 0.95))
    # nodes
    items = [('ABU DHABI', HUB[0], HUB[1], t_hub, 'UAE')] + [(n, la, lo, times[n], lab) for n, la, lo, lab in NET_NODES]
    lit = 0
    for name, la, lo, ti, lab in items:
        if t < ti:
            continue
        lit += 1
        p = G.ll_to_vec(la, lo) * 1.002
        pr = cam.project(p)
        if pr is None or cam.occluded(p):
            continue
        x, y = pr[0], pr[1]
        dt = t - ti
        hub = name == 'ABU DHABI'
        core = 3.8 if hub else 2.8
        c.drawCircle(x, y, core * 3.2, paint(GOLD, 0.35, blur=core * 2.2))
        c.drawCircle(x, y, core, paint((1, 0.97, 0.9), 1.0))
        c.drawCircle(x, y, core + 4.5, paint(GOLD, 0.75, stroke=1.0))
        rip = (dt % 1.6) / 1.6 if hub else min(1.0, dt / 0.9)
        ra = (1 - rip) * 0.85
        if ra > 0.02:
            c.drawCircle(x, y, core + 6 + rip * (46 if hub else 30), paint(GOLD, ra, stroke=1.2))
        if hub or name == 'KARACHI' or name in ('ISTANBUL', 'LONDON', 'JAKARTA', 'SEOUL', 'CAIRO', 'MUMBAI'):
            la_ = ease_out_cubic(ramp(t, ti + 0.05, ti + 0.35))
            col = GOLD if hub else TEXT
            label(c, V1.decode(lab, t, ti, 0.3, len(lab)), x + 20, y - 18, 16 if hub else 14, col, 0.9 * la_,
                  tracking=0.22)
    # Aisha's company recognised at home (roadmap framing lives in the narration: "imagine")
    tk = times['KARACHI']
    if tk <= t < t1:
        pk = appear(t, tk + 0.2, 0.4) * (1 - smooth(ramp(t, L('network', 2).start + 1.2, L('network', 2).start + 1.7)))
        pr = cam.project(G.ll_to_vec(24.86, 67.0) * 1.002)
        if pk > 0 and pr is not None:
            x, y = pr[0] + 40, pr[1] + 30
            c.drawRRect(rr(x, y, 400, 96, 18), paint((0.03, 0.03, 0.06), 0.8 * pk))
            c.drawRRect(rr(x, y, 400, 96, 18), paint(GOLD, 0.6 * pk, stroke=1.2))
            draw_text(c, 'Aisha Trading LLC', x + 24, y + 42, 'text_semibold', 24, TEXT, pk, align='left')
            check_icon(c, x + 32, y + 68, 9, ramp(t, tk + 0.4, tk + 0.7), GOLD, pk, ring=False)
            label(c, 'RECOGNISED · NO RE-FILING', x + 48, y + 74, 13, GOLD, pk, tracking=0.2)
    lin = lin + V1.lin_from_layer(Lr.rgba(), 1.35)
    lin = lin * (0.25 + 0.75 * smooth(ramp(t, t0, t0 + 0.3)))
    d = disp(lin, 'neutral', bloom_amt=0.42, bloom_th=0.62, hal=0.05, vig=0.35, ca=0.0012)
    Hd = Layer()
    t_one = L('network', 2).word('one', 0) if False else L('network', 2).word('Together')
    V1.title(Hd.c, [('One ', TEXT), ('economy.', GOLD)], W / 2, H - 120, t, t_one + 0.35, t1 + 0.1, size=64,
             align='center')
    return composite(d, Hd.rgba())


# --------------------------------------------------------------------------- CLOSE
CLOSE_SHOTS = [('aisha_coffee', 'Formed.', (0.42, 0.5), 'dusk'), ('omar_day', 'Licensed.', (0.36, 0.5), 'bluehour'),
               ('card_tap', 'Banked.', (0.5, 0.5), 'dusk'), ('ship', 'Recognised.', (0.5, 0.55), 'gold')]


def seg_close(t, fi):
    l0, l1 = L('close', 0), L('close', 1)
    hits = [l0.word('Formed'), l0.word('Licensed'), l0.word('Banked'), l0.word('Recognised')]
    t_mass = l1.word('Mass')
    if t < t_mass - 0.05:
        if t < hits[0]:
            return np.zeros((H, W, 3), np.float32)
        i = max(k for k, h in enumerate(hits) if t >= h)
        t0 = hits[i]
        t1_ = hits[i + 1] if i + 1 < len(hits) else t_mass
        name, word, ctr, look = CLOSE_SHOTS[i]
        lin = plate(name, t, t0, t1_, (ctr[0] - 0.01, ctr[1]), (ctr[0] + 0.01, ctr[1] - 0.01), 1.10, 1.2)
        hit = math.exp(-(t - t0) * 16)
        lin = V1.scrim(lin * (0.55 + 0.9 * hit), W / 2, H / 2 + 40, 640, 200, 0.55)
        d = disp(lin, look, bloom_amt=0.3, bloom_th=0.65, hal=0.1, vig=0.55)
        Lr = Layer()
        c = Lr.c
        p = ease_out_expo(ramp(t, t0, t0 + 0.18))
        draw_text(c, word, W / 2, H / 2 + 50 + (1 - p) * 14, 'display_semibold', 150, (0, 0, 0), 0.4 * p,
                  tracking=-0.03, blur=18)
        draw_text(c, word, W / 2, H / 2 + 50 + (1 - p) * 14, 'display_semibold', 150, TEXT, p, tracking=-0.03)
        out = composite(d, Lr.rgba())
        if t > t_mass - 0.3:
            out = out * (1 - smooth(ramp(t, t_mass - 0.3, t_mass - 0.05)))
        return out
    return end_card(t, t_mass - 0.05, l1.word('operating'), l1.end + 0.4)


def end_card(t, t0, t_tag, t_url):
    dt = t - t0
    lin = V1.end_background().copy()
    x, y, col, size, b, ph, vx, vy = V1.dust_band()
    Lr = Layer()
    c = Lr.c
    reveal_x = lerp(-200, W + 200, ease_out_cubic(ramp(t, t0 - 0.1, t0 + 1.4)))
    for i in range(len(x)):
        if x[i] > reveal_x:
            continue
        a = b[i] * (0.6 + 0.4 * math.sin(t * 1.9 + ph[i])) * clamp((reveal_x - x[i]) / 240)
        if a < 0.02:
            continue
        c.drawCircle(x[i] + vx[i] * dt, y[i] + vy[i] * dt, size[i], paint(col[i], clamp(a)))
    dust = V1.lin_from_layer(Lr.rgba(), 1.0)
    lin = lin + dust * 1.6 + gblur(dust, 5) * 2.4 + gblur(dust, 26) * 3.0
    burst = math.exp(-max(0.0, dt - 0.16) / 0.08) * (dt >= 0.16)
    mh_, ws_ = 96, 58
    tot_ = mark_width() * mh_ + mh_ * 0.62 + text_width('MASS', 'display_medium', ws_, 0.52)
    mcx, mcy = W / 2 - tot_ / 2 + mark_width() * mh_ / 2, 360 + mh_ * 0.5
    lin = lin + V1.radial(mcx, mcy, 150)[..., None] * np.array([1.0, 0.8, 0.5], np.float32) * burst * 0.9
    lin = V1.anamorphic_streak(lin, mcx, mcy, 0.7 * math.exp(-max(0.0, dt - 0.16) * 3.5) * (dt >= 0.16), length=700)
    d = disp(lin, 'neutral', bloom_amt=0.3, bloom_th=0.35, hal=0.0, vig=0.35, ca=0.0)
    L2 = Layer()
    c2 = L2.c
    mw = mark_width() * mh_
    ww = text_width('MASS', 'display_medium', ws_, 0.52)
    gap = mh_ * 0.62
    x0 = W / 2 - (mw + gap + ww) / 2
    V1.mark_layer(c2, x0, 360, mh_, t, [t0 + 0.02, t0 + 0.08, t0 + 0.14], fill_col=(1, 1, 1),
                  sweep_t=ramp(t, t0 + 0.7, t0 + 1.4), glow=0.0)
    pw = ease_out_cubic(ramp(t, t0 + 0.2, t0 + 0.9))
    if pw > 0:
        draw_text(c2, 'MASS', x0 + mw + gap, 360 + mh_ * 0.5 + ws_ * 0.36, 'display_medium', ws_, TEXT, pw,
                  tracking=lerp(0.8, 0.52, pw), align='left')
    V1.title(c2, [('The operating system for ', TEXT), ('sovereign economies.', GOLD)], W / 2, 596, t, t_tag, None,
             size=48, align='center', stagger=0.012, shadow=0.0)
    pu = ease_out_cubic(ramp(t, t_url, t_url + 0.5))
    if pu > 0:
        draw_text(c2, 'mass.inc', W / 2, 676, 'mono', 21, TEXT, 0.72 * pu, tracking=0.3)
    lay = L2.rgba()
    d = d + gblur(lay[..., 3], 30)[..., None] * 0.05 * np.array([1.0, 0.85, 0.6], np.float32)
    out = composite(d, lay)
    return out * (1 - smooth(ramp(t, DUR - 0.9, DUR - 0.05)))


# --------------------------------------------------------------------------- dispatcher
SEG_FN = {'open': seg_open, 'aisha': seg_aisha, 'omar': seg_omar, 'ministry': seg_ministry, 'peak': seg_peak,
          'turn': seg_turn, 'reveal': seg_reveal, 'demo': seg_demo, 'trust': seg_trust, 'network': seg_network,
          'close': seg_close}


def segments():
    b = [('open', 0.0), ('aisha', L('aisha', 0).start - 0.05), ('omar', L('omar', 0).start - 0.2),
         ('ministry', L('ministry', 0).start - 0.2), ('peak', L('peak', 0).start - 0.1), ('turn', L('turn', 0).start - 0.3),
         ('reveal', L('reveal', 0).start - 0.2), ('demo', L('demo', 0).start - 0.3), ('trust', L('trust', 0).start - 0.2),
         ('network', L('network', 0).start - 0.1), ('close', L('close', 0).start - 0.1)]
    return b


GRAIN = {'open': 0.045, 'aisha': 0.04, 'omar': 0.036, 'ministry': 0.03, 'peak': 0.05, 'turn': 0.018, 'reveal': 0.03,
         'demo': 0.022, 'trust': 0.026, 'network': 0.02, 'close': 0.03}


def bar_px(t):
    t_open = L('turn', 0).start
    if t < t_open:
        return BAR
    return BAR * (1 - ease_in_out_cubic(ramp(t, t_open, t_open + 1.6)))


def frame(t, fi):
    segs = segments()
    name = segs[0][0]
    for nm, t0 in segs:
        if t >= t0:
            name = nm
    img = SEG_FN[name](t, fi)
    img = grain(img, fi, amount=GRAIN[name])
    img = letterbox(img, bar_px(t), color=(0, 0, 0))
    return np.clip(img, 0, 1)
