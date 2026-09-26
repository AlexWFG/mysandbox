"""Interface system for the 2-minute film: the Mass agent chat (Aisha), the licensing
console (Omar), the ministry's live dashboard, the disconnected-systems wall, character
cards, light pulses between screens, and a canvas camera for the three-way sequence.

All UI is vector (Skia) drawn over frosted glass, sized for phone viewing at 1080p."""
import math
import os
import sys
import functools

import numpy as np
import skia

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src'))
from engine import (W, H, INK, GOLD, TEXT, GREY, LABEL, RED, clamp, lerp, ramp, smooth, ease_out_cubic,  # noqa: E402
                    ease_in_out_cubic, ease_out_back, ease_out_expo, Layer, paint, draw_text, text_width,
                    frosted, composite, placed_mark, mark_width, gblur)

GREEN = np.array([0.55, 0.86, 0.66], np.float32)
AMBER = np.array([1.0, 0.72, 0.36], np.float32)
PANEL_TINT = (0.018, 0.016, 0.04)
WHITE = (1.0, 1.0, 1.0)


# --------------------------------------------------------------------------- basics
def rr(x, y, w, h, r):
    return skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r)


def appear(t, t0, dur=0.35):
    """0..1 entrance progress."""
    return ease_out_cubic(ramp(t, t0, t0 + dur))


def wrap(text, key, size, max_w, tracking=0.0):
    words = text.split(' ')
    lines, cur = [], ''
    for wd in words:
        trial = wd if not cur else cur + ' ' + wd
        if text_width(trial, key, size, tracking) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


class UIFrame:
    """Collects frosted-glass regions (screen space) and draws UI on one Skia layer."""

    def __init__(self):
        self.frosts = []
        self.layer = Layer()
        self.c = self.layer.c
        self.s, self.ox, self.oy = 1.0, 0.0, 0.0

    def set_view(self, s, ox, oy, clip=None):
        """Draw in panel-local coordinates scaled by s and offset to (ox, oy) on screen."""
        self.s, self.ox, self.oy = s, ox, oy
        if clip is not None:
            cx, cy, cw, ch, cr = clip
            self.c.clipRRect(rr(cx, cy, cw, ch, cr), skia.ClipOp.kIntersect, True)
        m = skia.Matrix()
        m.setScaleTranslate(s, s, ox, oy)
        self.c.setMatrix(m)

    def glass(self, x, y, w, h, r=26, alpha=1.0, tint_a=0.62, border=0.12, sigma=24):
        if alpha <= 0.003:
            return
        s = self.s
        X, Y = self.ox + x * s, self.oy + y * s
        self.frosts.append(((X, Y, X + w * s, Y + h * s), r * s, alpha, tint_a, max(2.0, sigma * s)))
        self.c.drawRRect(rr(x, y, w, h, r), paint(WHITE, border * alpha, stroke=1.2))

    def apply(self, base):
        for rect, r, alpha, tint_a, sigma in self.frosts:
            base = frosted(base, rect, radius=r, sigma=sigma, tint=PANEL_TINT, tint_a=tint_a, alpha=alpha)
        return composite(base, self.layer.rgba())


def check_icon(c, cx, cy, r, prog, color=GOLD, alpha=1.0, ring=True):
    if ring:
        c.drawCircle(cx, cy, r, paint(color, 0.9 * alpha, stroke=1.6))
    if prog <= 0:
        return
    pts = [(cx - r * 0.45, cy + r * 0.02), (cx - r * 0.1, cy + r * 0.36), (cx + r * 0.5, cy - r * 0.36)]
    p = skia.Path()
    p.moveTo(*pts[0])
    if prog < 0.4:
        q = prog / 0.4
        p.lineTo(lerp(pts[0][0], pts[1][0], q), lerp(pts[0][1], pts[1][1], q))
    else:
        q = (prog - 0.4) / 0.6
        p.lineTo(*pts[1])
        p.lineTo(lerp(pts[1][0], pts[2][0], q), lerp(pts[1][1], pts[2][1], q))
    c.drawPath(p, paint(color, alpha, stroke=max(1.6, r * 0.16)))


def spinner(c, cx, cy, r, t, color=GOLD, alpha=1.0):
    c.drawCircle(cx, cy, r, paint(WHITE, 0.12 * alpha, stroke=1.6))
    a0 = (t * 360 * 1.3) % 360
    c.drawArc(skia.Rect.MakeXYWH(cx - r, cy - r, 2 * r, 2 * r), a0, 100, False, paint(color, alpha, stroke=2.0))


def mark_icon(c, x, y, h, alpha=1.0, color=WHITE):
    for p in placed_mark(x, y, h):
        c.drawPath(p, paint(color, alpha))


def label(c, text, x, y, size=17, color=GREY, alpha=1.0, align='left', tracking=0.18, key='mono_medium'):
    return draw_text(c, text, x, y, key, size, color, alpha, tracking=tracking, align=align)


# --------------------------------------------------------------------------- character card
def lower_third(ui, t, t0, name, role, place, x=120, y=H - 170, t1=None):
    """Name card: a gold rule draws in, the name rises, role and place follow."""
    p = appear(t, t0, 0.5)
    out = 1.0 if t1 is None else 1 - smooth(ramp(t, t1 - 0.3, t1))
    a = p * out
    if a <= 0.003:
        return
    c = ui.c
    ln = 64 * ease_out_expo(ramp(t, t0, t0 + 0.6))
    c.drawRect(skia.Rect.MakeXYWH(x, y - 58, ln, 2), paint(GOLD, a))
    c.drawRect(skia.Rect.MakeXYWH(x - 30, y - 110, 760, 170), paint((0, 0, 0), 0.30 * a, blur=40))
    draw_text(c, name, x, y + (1 - p) * 14, 'display_semibold', 50, TEXT, a, tracking=-0.01, align='left')
    pr = appear(t, t0 + 0.18, 0.45) * out
    label(c, role.upper(), x, y + 40, 18, GOLD, pr, tracking=0.24)
    label(c, place.upper(), x, y - 78, 17, GREY, pr, tracking=0.28)


# --------------------------------------------------------------------------- chat
class Chat:
    """A scripted conversation. events: list of dicts with keys
    who ('user'|'agent'), t (appear time), kind ('text'|'passport'|'checks'|'result'), text, ..."""

    def __init__(self, events, width=820, text_size=31):
        self.events = events
        self.width = width
        self.ts = text_size
        self.pad = 26
        self.lh = int(text_size * 1.36)

    def block_height(self, ev):
        k = ev.get('kind', 'text')
        if k == 'text':
            lines = wrap(ev['text'], 'text', self.ts, self.width * 0.74 - 2 * self.pad)
            return len(lines) * self.lh + 2 * self.pad - 10
        if k == 'passport':
            return 250
        if k == 'checks':
            return 64 + 58 * len(ev['items'])
        if k == 'result':
            return 300
        return 80

    def draw(self, ui, t, x, y, w, h, alpha=1.0):
        """Draw inside the panel rect; messages are bottom-anchored and scroll up."""
        c = ui.c
        c.save()
        c.clipRect(skia.Rect.MakeXYWH(x, y, w, h), skia.ClipOp.kIntersect, True)
        gap = 22
        vis = [e for e in self.events if t >= e['t'] - (0.9 if e['who'] == 'agent' and e.get('typing', True) else 0)]
        # target stack height (typing indicator counts as a small block)
        heights = []
        for e in vis:
            if e['who'] == 'agent' and e.get('typing', True) and t < e['t']:
                heights.append(64)
            else:
                heights.append(self.block_height(e))
        total = sum(heights) + gap * max(0, len(heights) - 1)
        # smooth scroll: interpolate from previous total
        prev_total = total
        if vis:
            last = vis[-1]
            t_last = last['t'] - (0.9 if last['who'] == 'agent' and last.get('typing', True) else 0)
            k = ease_in_out_cubic(ramp(t, t_last, t_last + 0.45))
            prev_total = total - (heights[-1] + gap) * (1 - k)
        cy = y + h - 30 - prev_total
        for e, bh in zip(vis, heights):
            self._draw_event(ui, e, t, x, cy, w, bh, alpha)
            cy += bh + gap
        c.restore()

    def _draw_event(self, ui, e, t, x, y, w, bh, alpha):
        c = ui.c
        user = e['who'] == 'user'
        if e['who'] == 'agent' and e.get('typing', True) and t < e['t']:
            # typing indicator
            p = appear(t, e['t'] - 0.9, 0.25)
            bx, by = x + 86, y
            c.drawRRect(rr(bx, by, 110, 58, 29), paint(WHITE, 0.07 * alpha * p))
            for i in range(3):
                ph = math.sin((t * 6.5) - i * 0.9) * 0.5 + 0.5
                c.drawCircle(bx + 32 + i * 23, by + 29 - ph * 5, 6, paint(TEXT, (0.35 + 0.55 * ph) * alpha * p))
            self._avatar(c, x + 30, y + 29, alpha * p)
            return
        p = appear(t, e['t'], 0.38)
        dy = (1 - p) * 18
        a = alpha * p
        k = e.get('kind', 'text')
        if k == 'text':
            lines = wrap(e['text'], 'text', self.ts, self.width * 0.74 - 2 * self.pad)
            tw = max(text_width(s, 'text', self.ts) for s in lines)
            bw = tw + 2 * self.pad
            bx = x + w - bw - 24 if user else x + 86
            by = y + dy
            if user:
                c.drawRRect(rr(bx, by, bw, bh, 26), paint(GOLD, 0.16 * a))
                c.drawRRect(rr(bx, by, bw, bh, 26), paint(GOLD, 0.42 * a, stroke=1.2))
            else:
                c.drawRRect(rr(bx, by, bw, bh, 26), paint(WHITE, 0.075 * a))
                self._avatar(c, x + 30, by + 30, a)
            # agent text streams in; user text lands whole
            n_chars = sum(len(s) for s in lines)
            # agent text streams at ~48 chars/s; user text lands whole
            shown = n_chars if user else int(clamp((t - e['t']) / max(0.35, n_chars / 48.0)) * n_chars)
            cnt = 0
            for i, s in enumerate(lines):
                vis = s if cnt + len(s) <= shown else s[:max(0, shown - cnt)]
                cnt += len(s)
                if vis:
                    draw_text(c, vis, bx + self.pad, by + self.pad + 26 + i * self.lh - 6, 'text', self.ts, TEXT, a,
                              align='left')
            return
        if k == 'passport':
            self._passport(c, t, e, x + w - 520 - 24, y + dy, 520, 230, a)
            return
        if k == 'checks':
            self._checks(c, t, e, x + 86, y + dy, w * 0.74, bh, a)
            self._avatar(c, x + 30, y + dy + 30, a)
            return
        if k == 'result':
            self._result(c, t, e, x + 86, y + dy, w * 0.78, bh, a)
            self._avatar(c, x + 30, y + dy + 30, a)

    def _avatar(self, c, cx, cy, a):
        c.drawCircle(cx, cy, 24, paint(WHITE, 0.10 * a))
        c.drawCircle(cx, cy, 24, paint(GOLD, 0.5 * a, stroke=1.0))
        h = 20
        mark_icon(c, cx - mark_width() * h / 2, cy - h / 2, h, a, TEXT)

    def _passport(self, c, t, e, x, y, w, h, a):
        c.drawRRect(rr(x, y, w, h, 20), paint((0.10, 0.12, 0.16), 0.92 * a))
        c.drawRRect(rr(x, y, w, h, 20), paint(WHITE, 0.16 * a, stroke=1.2))
        # photo block
        c.drawRRect(rr(x + 24, y + 26, 118, 150, 10), paint((0.24, 0.26, 0.32), a))
        c.drawCircle(x + 83, y + 82, 30, paint((0.42, 0.44, 0.52), a))
        c.drawRRect(rr(x + 42, y + 118, 82, 58, 28), paint((0.42, 0.44, 0.52), a))
        label(c, 'PASSPORT', x + 166, y + 52, 17, GREY, a, tracking=0.3)
        draw_text(c, e.get('name', 'AISHA KHAN'), x + 166, y + 92, 'text_semibold', 26, TEXT, a, align='left')
        label(c, e.get('meta', 'NATIONALITY · PAK'), x + 166, y + 128, 16, GREY, a, tracking=0.2)
        mrz = e.get('mrz', ['P<PAKKHAN<<AISHA<<<<<<<<<<<<<<<<<<<<<<<<<<', 'AB1234567<8PAK9203114F3010021<<<<<<<<<<<<<04'])
        label(c, mrz[0][:40], x + 24, y + 212, 13, (0.6, 0.62, 0.68), a, tracking=0.06)
        # scan sweep then verified
        ts = e.get('scan', e['t'] + 0.35)
        sp = ramp(t, ts, ts + 1.0)
        if 0 < sp < 1:
            sy = y + 10 + sp * (h - 20)
            c.drawRect(skia.Rect.MakeXYWH(x + 6, sy - 1.5, w - 12, 3), paint(GOLD, 0.9 * a))
            c.drawRect(skia.Rect.MakeXYWH(x + 6, sy - 26, w - 12, 26), paint(GOLD, 0.12 * a))
        vp = appear(t, ts + 1.0, 0.3)
        if vp > 0:
            c.drawRRect(rr(x + w - 204, y + 150, 180, 36, 18), paint(GREEN, 0.18 * a * vp))
            check_icon(c, x + w - 180, y + 168, 10, ramp(t, ts + 1.0, ts + 1.3), GREEN, a * vp, ring=False)
            label(c, 'VERIFIED', x + w - 160, y + 174, 16, GREEN, a * vp, tracking=0.24)

    def _checks(self, c, t, e, x, y, w, h, a):
        c.drawRRect(rr(x, y, w, h, 22), paint(WHITE, 0.07 * a))
        label(c, e.get('title', 'PREPARING YOUR FILING'), x + 26, y + 40, 16, GREY, a, tracking=0.24)
        for i, (txt, ti) in enumerate(e['items']):
            ry = y + 88 + i * 58
            if t < ti:
                spinner(c, x + 42, ry - 9, 13, t, GOLD, a * 0.9)
                draw_text(c, txt, x + 74, ry, 'text', 27, GREY, a * 0.8, align='left')
            else:
                k = ramp(t, ti, ti + 0.3)
                check_icon(c, x + 42, ry - 9, 13, k, GOLD, a)
                draw_text(c, txt, x + 74, ry, 'text', 27, TEXT, a, align='left')

    def _result(self, c, t, e, x, y, w, h, a):
        c.drawRRect(rr(x, y, w, h, 24), paint(GOLD, 0.10 * a))
        c.drawRRect(rr(x, y, w, h, 24), paint(GOLD, 0.45 * a, stroke=1.3))
        label(c, 'LIVE RECORD', x + 28, y + 42, 16, GOLD, a, tracking=0.28)
        pulse = 0.6 + 0.4 * math.sin(t * 7)
        c.drawCircle(x + w - 40, y + 36, 6, paint(GOLD, a))
        c.drawCircle(x + w - 40, y + 36, 13, paint(GOLD, 0.35 * a * pulse, blur=5))
        draw_text(c, e.get('company', 'Aisha Trading LLC'), x + 28, y + 96, 'display_semibold', 38, TEXT, a, align='left')
        for i, (txt, ti) in enumerate(e['items']):
            k = ramp(t, ti, ti + 0.3)
            ry = y + 150 + i * 46
            check_icon(c, x + 42, ry - 8, 12, k, GOLD, a * (0.3 + 0.7 * (t >= ti)))
            draw_text(c, txt, x + 70, ry, 'text', 26, TEXT, a * (0.35 + 0.65 * (t >= ti)), align='left')
        te = e.get('elapsed_t', e['items'][-1][1] + 0.3)
        pe = appear(t, te, 0.4)
        if pe > 0:
            label(c, e.get('elapsed', '4 MIN 12 S'), x + w - 28, y + h - 28, 18, GOLD, a * pe, align='right',
                  tracking=0.22)


def chat_panel(ui, t, chat, x, y, w, h, title='Mass Agent', status='ONLINE', clock='10:31', alpha=1.0):
    ui.glass(x, y, w, h, 30, alpha, tint_a=0.66)
    c = ui.c
    mark_icon(c, x + 32, y + 30, 26, alpha)
    draw_text(c, title, x + 32 + mark_width() * 26 + 16, y + 52, 'text_semibold', 24, TEXT, alpha, align='left')
    cw_ = text_width(clock, 'mono_medium', 16, 0.14)
    sw_ = text_width(status, 'mono_medium', 15, 0.24)
    label(c, clock, x + w - 32, y + 50, 16, GREY, alpha, align='right', tracking=0.14)
    label(c, status, x + w - 32 - cw_ - 28, y + 50, 15, GOLD, alpha, align='right', tracking=0.24)
    c.drawCircle(x + w - 32 - cw_ - 28 - sw_ - 14, y + 45, 5, paint(GOLD, alpha))
    c.drawRect(skia.Rect.MakeXYWH(x + 1, y + 84, w - 2, 1), paint(WHITE, 0.08 * alpha))
    chat.draw(ui, t, x, y + 86, w, h - 86 - 90, alpha)
    # composer
    c.drawRRect(rr(x + 24, y + h - 72, w - 48, 50, 25), paint(WHITE, 0.06 * alpha))
    label(c, 'Message Mass', x + 52, y + h - 40, 18, LABEL, alpha, key='text', tracking=0.0)
    c.drawCircle(x + w - 50, y + h - 47, 16, paint(GOLD, 0.9 * alpha))


# --------------------------------------------------------------------------- licensing console
def seal(c, cx, cy, r, prog, t, alpha=1.0, text='APPROVED'):
    """A digital seal stamping down: gold ring, Mass mark, text on the ring."""
    if prog <= 0:
        return
    s = lerp(1.35, 1.0, ease_out_back(prog, 1.8))
    a = alpha * clamp(prog * 2)
    rr_ = r * s
    c.drawCircle(cx, cy, rr_, paint(GOLD, 0.14 * a))
    c.drawCircle(cx, cy, rr_, paint(GOLD, a, stroke=3.0))
    c.drawCircle(cx, cy, rr_ * 0.82, paint(GOLD, 0.7 * a, stroke=1.2))
    h = rr_ * 0.62
    mark_icon(c, cx - mark_width() * h / 2, cy - h * 0.62, h, a, GOLD)
    draw_text(c, text, cx, cy + rr_ * 0.48, 'mono_medium', max(10, rr_ * 0.16), GOLD, a, tracking=0.2)


def licensing_console(ui, t, x, y, w, h, st, alpha=1.0):
    """st: dict with times: arrive, review (checks tick), approve (button), seal, cleared."""
    ui.glass(x, y, w, h, 30, alpha, tint_a=0.68)
    c = ui.c
    label(c, 'LICENSING · ABU DHABI FREE ZONE', x + 32, y + 50, 16, GREY, alpha, tracking=0.24)
    label(c, st.get('clock', '09:31 GST'), x + w - 32, y + 50, 16, GREY, alpha, align='right', tracking=0.14)
    c.drawRect(skia.Rect.MakeXYWH(x + 1, y + 80, w - 2, 1), paint(WHITE, 0.08 * alpha))
    # queue counter
    q0, q1 = st.get('queue', (1, 0))
    qk = ease_in_out_cubic(ramp(t, st['cleared'], st['cleared'] + 0.6))
    label(c, 'IN REVIEW', x + 32, y + 124, 15, GREY, alpha, tracking=0.24)
    draw_text(c, f'{round(lerp(q0, q1, qk)):d}', x + 32, y + 178, 'display_light', 54, TEXT, alpha, align='left')
    label(c, 'AVG. DECISION TIME', x + 250, y + 124, 15, GREY, alpha, tracking=0.24)
    draw_text(c, st.get('avg', '3 min'), x + 250, y + 178, 'display_light', 54, TEXT, alpha, align='left')
    # the application card
    pa = appear(t, st['arrive'], 0.45)
    if pa <= 0:
        return
    cx, cy, cw, ch = x + 28, y + 214 + (1 - pa) * 30, w - 56, h - 214 - 28
    a = alpha * pa
    c.drawRRect(rr(cx, cy, cw, ch, 24), paint(WHITE, 0.06 * a))
    c.drawRRect(rr(cx, cy, cw, ch, 24), paint(GOLD, (0.25 + 0.5 * math.exp(-max(0, t - st['arrive']) * 3)) * a,
                                              stroke=1.4))
    label(c, 'NEW APPLICATION · PREPARED BY MASS AGENT', cx + 28, cy + 44, 15, GOLD, a, tracking=0.2)
    draw_text(c, st.get('company', 'Aisha Trading LLC'), cx + 28, cy + 100, 'display_semibold', 40, TEXT, a, align='left')
    label(c, st.get('activity', 'AI-DRIVEN COMMODITY TRADING'), cx + 28, cy + 138, 16, GREY, a, tracking=0.2)
    rows = st.get('rows', [('Owner identity verified', 0.0), ('Documents complete', 0.15), ('23 of 23 checks passed', 0.3),
                           ('Bank account ready to open', 0.45)])
    for i, (txt, dt) in enumerate(rows):
        ti = st['review'] + dt
        ry = cy + 206 + i * 52
        k = ramp(t, ti, ti + 0.3)
        check_icon(c, cx + 42, ry - 8, 12, k, GOLD, a * (0.3 + 0.7 * (t >= ti)))
        draw_text(c, txt, cx + 70, ry, 'text', 26, TEXT, a * (0.35 + 0.65 * (t >= ti)), align='left')
    # approve button
    bx, by, bw, bh = cx + 28, cy + ch - 92, 250, 64
    press = math.exp(-max(0.0, t - st['approve']) * 9) * (t >= st['approve'])
    done = t >= st['approve']
    c.drawRRect(rr(bx + 3 * press, by + 3 * press, bw - 6 * press, bh - 6 * press, 32),
                paint(GOLD, (0.95 if not done else 0.25) * a))
    draw_text(c, 'Approve' if not done else 'Approved', bx + bw / 2, by + 42, 'text_semibold', 26,
              INK if not done else GOLD, a, align='center')
    if not done:
        label(c, 'RECOMMENDED', bx + bw + 24, by + 40, 15, GREY, a, tracking=0.24)
    # the seal
    sp = ramp(t, st['seal'], st['seal'] + 0.28)
    seal(c, cx + cw - 150, cy + ch - 170, 108, sp, t, a)
    if t >= st['seal']:
        fl = math.exp(-(t - st['seal']) * 5)
        c.drawCircle(cx + cw - 150, cy + ch - 170, 108 + 70 * (1 - fl), paint(GOLD, 0.8 * fl * a, stroke=2))


# --------------------------------------------------------------------------- ministry dashboard
@functools.lru_cache(maxsize=1)
def company_dots(n=900, seed=3):
    """Abstract economy map: clusters of company dots (cities) on a dark field (normalised 0..1)."""
    rng = np.random.default_rng(seed)
    centres = [(0.30, 0.62, 0.9), (0.62, 0.40, 1.3), (0.70, 0.30, 0.6), (0.78, 0.26, 0.5), (0.46, 0.55, 0.5),
               (0.86, 0.20, 0.35), (0.58, 0.72, 0.3)]
    pts = []
    for cx, cy, wgt in centres:
        k = int(n * wgt / 4.45)
        r = rng.normal(0, 0.05 * math.sqrt(wgt), (k, 2))
        pts.append(np.stack([cx + r[:, 0], cy + r[:, 1] * 0.8], 1))
    p = np.concatenate(pts, 0)
    p = p[(p[:, 0] > 0.03) & (p[:, 0] < 0.97) & (p[:, 1] > 0.05) & (p[:, 1] < 0.95)]
    return p.astype(np.float32), rng.uniform(0, 6.28, len(p)).astype(np.float32)


def ministry_dashboard(ui, t, x, y, w, h, st, alpha=1.0):
    """st: new_company (time a +1 lands), rule (time rule publishes), base count."""
    ui.glass(x, y, w, h, 30, alpha, tint_a=0.7)
    c = ui.c
    label(c, 'NATIONAL ECONOMY · LIVE', x + 32, y + 50, 16, GREY, alpha, tracking=0.24)
    rw_ = text_width('REAL TIME', 'mono_medium', 15, 0.24)
    c.drawCircle(x + w - 32 - rw_ - 14, y + 45, 5, paint(GOLD, alpha))
    label(c, 'REAL TIME', x + w - 32, y + 50, 15, GOLD, alpha, align='right', tracking=0.24)
    c.drawRect(skia.Rect.MakeXYWH(x + 1, y + 80, w - 2, 1), paint(WHITE, 0.08 * alpha))
    # KPIs
    base = st.get('base', 1284)
    k1 = t >= st['new_company']
    label(c, 'NEW COMPANIES TODAY', x + 32, y + 124, 15, GREY, alpha, tracking=0.24)
    draw_text(c, f'{base + (1 if k1 else 0):,}', x + 32, y + 184, 'display_light', 60, TEXT, alpha, align='left')
    if k1:
        pk = appear(t, st['new_company'], 0.5)
        fade = 1 - smooth(ramp(t, st['new_company'] + 1.4, st['new_company'] + 2.0))
        draw_text(c, '+1', x + 32 + text_width(f'{base + 1:,}', 'display_light', 60) + 18, y + 184 - 20 * pk,
                  'display_semibold', 34, GOLD, alpha * pk * fade, align='left')
    label(c, 'AVG. FORMATION', x + 340, y + 124, 15, GREY, alpha, tracking=0.24)
    draw_text(c, st.get('avg', '4 min'), x + 340, y + 184, 'display_light', 60, TEXT, alpha, align='left')
    # map: the UAE outline with company dots clustered on the cities
    mx, my, mw, mh = x + 28, y + 220, w - 56, h - 220 - 176
    c.drawRRect(rr(mx, my, mw, mh, 22), paint(WHITE, 0.035 * alpha))
    c.save()
    c.clipRRect(rr(mx, my, mw, mh, 22), skia.ClipOp.kIntersect, True)
    proj = uae_projection(mx + 20, my + 20, mw - 40, mh - 40)
    outline = uae_path(proj)
    c.drawPath(outline, paint(WHITE, 0.05 * alpha))
    c.drawPath(outline, paint(WHITE, 0.28 * alpha, stroke=1.3))
    pts, ph = uae_dots()
    tr = st['rule']
    ripple_r = (t - tr) * 900 if t >= tr else -1
    rc = proj(54.38, 24.47)  # Abu Dhabi
    for (lon, lat), p0 in zip(pts, ph):
        sx, sy = proj(lon, lat)
        a = 0.35 + 0.25 * math.sin(t * 1.3 + p0)
        col = TEXT
        if ripple_r > 0:
            d = math.hypot(sx - rc[0], sy - rc[1])
            if d < ripple_r:
                a = min(1.0, a + 0.5 * math.exp(-(ripple_r - d) / 80))
                col = GOLD
        c.drawCircle(sx, sy, 1.8, paint(col, a * alpha))
    if 0 < ripple_r < 1400:
        c.drawCircle(rc[0], rc[1], ripple_r, paint(GOLD, alpha * 0.8 * (1 - ripple_r / 1400), stroke=2.0))
    for name, lon, lat in (('ABU DHABI', 54.38, 24.47), ('DUBAI', 55.27, 25.20), ('SHARJAH', 55.41, 25.35),
                           ('AL AIN', 55.74, 24.21), ('RAS AL KHAIMAH', 55.97, 25.79)):
        px_, py_ = proj(lon, lat)
        if name != 'ABU DHABI' or t < st['new_company']:
            label(c, name, px_ + 10, py_ + 5, 12, GREY, alpha * 0.8, tracking=0.2)
    if t >= st['new_company'] - 0.01:
        pk = appear(t, st['new_company'], 0.4)
        c.drawCircle(rc[0], rc[1], 6, paint(GOLD, alpha * pk))
        rp = ((t - st['new_company']) % 1.4) / 1.4
        c.drawCircle(rc[0], rc[1], 8 + 34 * rp, paint(GOLD, alpha * (1 - rp) * pk, stroke=1.4))
        pin = st.get('pin', 'AISHA TRADING LLC · FORMED')
        pw_ = text_width(pin, 'mono_medium', 15, 0.2)
        lx_ = rc[0] + 18 if rc[0] + 18 + pw_ < mx + mw - 16 else rc[0] - 18 - pw_
        label(c, pin, lx_, rc[1] - 14, 15, GOLD, alpha * pk, tracking=0.2)
    c.restore()
    # rule card
    rx, ry, rw, rh = x + 28, y + h - 150, w - 56, 124
    pr = appear(t, st.get('rule_card', tr - 1.6), 0.4)
    if pr > 0:
        a = alpha * pr
        c.drawRRect(rr(rx, ry, rw, rh, 20), paint(WHITE, 0.07 * a))
        label(c, 'RULE UPDATE', rx + 24, ry + 34, 14, GREY, a, tracking=0.24)
        draw_text(c, st.get('rule_text', 'AI trading licence · minimum capital'), rx + 24, ry + 72, 'text', 25, TEXT, a,
                  align='left')
        old, new = st.get('rule_values', ('AED 150,000', 'AED 50,000'))
        vx = rx + rw - 24
        if t < tr:
            label(c, old, vx, ry + 72, 22, TEXT, a, align='right', key='mono', tracking=0.04)
        else:
            k = appear(t, tr, 0.3)
            label(c, new, vx, ry + 72, 22, GOLD, a * k, align='right', key='mono', tracking=0.04)
            label(c, 'PUBLISHED · APPLIES TO EVERY COMPANY TODAY', rx + 24, ry + 106, 14, GOLD, a * k, tracking=0.2)


@functools.lru_cache(maxsize=1)
def uae_rings():
    import json
    return json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uae_outline.json')))


def uae_projection(x, y, w, h):
    """Equirectangular fit of the UAE (lon 51.5–56.5, lat 22.5–26.2) into the rect, aspect kept."""
    lon0, lon1, lat0, lat1 = 51.4, 56.6, 22.5, 26.2
    kx = math.cos(math.radians(24.3))
    sw, sh = (lon1 - lon0) * kx, (lat1 - lat0)
    s = min(w / sw, h / sh)
    ox, oy = x + (w - sw * s) / 2, y + (h - sh * s) / 2

    def proj(lon, lat):
        return ox + (lon - lon0) * kx * s, oy + (lat1 - lat) * s
    return proj


def uae_path(proj):
    p = skia.Path()
    for ring in uae_rings():
        for i, (lon, lat) in enumerate(ring):
            X, Y = proj(lon, lat)
            if i == 0:
                p.moveTo(X, Y)
            else:
                p.lineTo(X, Y)
        p.close()
    return p


@functools.lru_cache(maxsize=1)
def uae_dots(n=1100, seed=3):
    """Company dots clustered on the cities, kept inside the UAE outline."""
    rng = np.random.default_rng(seed)
    cities = [(54.38, 24.47, 1.2), (55.27, 25.20, 1.5), (55.41, 25.35, 0.6), (55.74, 24.21, 0.35),
              (55.97, 25.79, 0.3), (55.55, 25.56, 0.2), (56.33, 25.12, 0.2), (54.60, 24.35, 0.3)]
    tot = sum(c[2] for c in cities)
    path = uae_path(lambda lon, lat: (lon * 100, -lat * 100))
    pts = []
    for lon, lat, wgt in cities:
        k = int(n * wgt / tot)
        r = rng.normal(0, 0.10 * math.sqrt(wgt), (k * 2, 2))
        for dx, dy in r:
            if len(pts) and sum(1 for _ in ()) > 0:
                pass
            lo, la = lon + dx, lat + dy * 0.7
            if path.contains((lo * 100), (-la * 100)):
                pts.append((lo, la))
            if len(pts) >= sum(int(n * cw / tot) for _, _, cw in cities[:cities.index((lon, lat, wgt)) + 1]):
                break
    p = np.array(pts, np.float32)
    return p, rng.uniform(0, 6.28, len(p)).astype(np.float32)


# --------------------------------------------------------------------------- disconnected systems wall
SYSTEM_NAMES = ['COMPANY REGISTRY', 'LICENSING 07', 'CUSTOMS', 'BANK KYC', 'FREE ZONE 12', 'CHAMBER', 'STATISTICS',
                'TAX', 'VISAS', 'LABOUR', 'COURTS', 'LAND', 'FREE ZONE 03', 'LICENSING 21', 'TRADE', 'SANCTIONS',
                'PORTS', 'ENERGY', 'HEALTH PERMITS', 'FREE ZONE 31', 'NOTARY', 'MUNICIPALITY', 'FINANCE', 'INSURANCE',
                'LICENSING 14', 'EXPORTS', 'ARCHIVE', 'FREE ZONE 08', 'PROCUREMENT', 'CENTRAL BANK', 'LICENSING 02',
                'IP OFFICE', 'LOGISTICS', 'TOURISM', 'FREE ZONE 19', 'AUDIT', 'LICENSING 33', 'RETAIL PERMITS',
                'FREE ZONE 27', 'IMMIGRATION', 'ECONOMIC ZONE', 'LICENSING 45', 'REGISTRY (LEGACY)', 'SURVEYS',
                'FREE ZONE 40', 'MARITIME', 'AVIATION', 'LICENSING 46']
STATUSES = [('SYNC FAILED', RED), ('LAST UPDATE 14 MONTHS AGO', AMBER), ('EXPORT PENDING', AMBER), ('OFFLINE', RED),
            ('MANUAL ENTRY', AMBER), ('FORMAT NOT SUPPORTED', RED), ('AWAITING SIGNATURE', AMBER), ('NO CONNECTION', RED)]


def systems_wall(ui, t, t0, cols=8, rows=6, zoom=1.0, cx=W / 2, cy=H / 2, alpha=1.0):
    """A grid of disconnected systems; tiles light up one by one, links try to connect and break."""
    c = ui.c
    tw, th, gap = 230 * zoom, 150 * zoom, 18 * zoom
    gw = cols * tw + (cols - 1) * gap
    gh = rows * th + (rows - 1) * gap
    ox, oy = cx - gw / 2, cy - gh / 2
    rng = np.random.default_rng(12)
    order = rng.permutation(cols * rows)
    for idx in range(cols * rows):
        i, j = idx % cols, idx // cols
        x, y = ox + i * (tw + gap), oy + j * (th + gap)
        rank = int(np.where(order == idx)[0][0])
        ta = t0 + rank * 0.045
        p = appear(t, ta, 0.3)
        if p <= 0 or x > W + 50 or y > H + 50 or x + tw < -50 or y + th < -50:
            continue
        a = alpha * p
        flick = 1.0 if (int(t * 12 + idx * 7) % 23) else 0.55
        c.drawRRect(rr(x, y, tw, th, 12 * zoom), paint((0.06, 0.06, 0.09), 0.9 * a))
        c.drawRRect(rr(x, y, tw, th, 12 * zoom), paint(WHITE, 0.14 * a, stroke=1.0))
        name = SYSTEM_NAMES[idx % len(SYSTEM_NAMES)]
        label(c, name, x + 14 * zoom, y + 28 * zoom, max(9, 13 * zoom), TEXT, a * flick, tracking=0.16)
        # fake content lines (each system looks different)
        style = idx % 4
        for k in range(4):
            ly = y + (48 + k * 18) * zoom
            if style == 0:
                c.drawRect(skia.Rect.MakeXYWH(x + 14 * zoom, ly, (tw - 28 * zoom) * (0.4 + 0.5 * ((idx * 7 + k * 3) % 5) / 5),
                                              6 * zoom), paint(WHITE, 0.10 * a))
            elif style == 1:
                for m in range(4):
                    c.drawRect(skia.Rect.MakeXYWH(x + (14 + m * 50) * zoom, ly, 40 * zoom, 8 * zoom),
                               paint(WHITE, 0.08 * a))
            elif style == 2:
                c.drawRect(skia.Rect.MakeXYWH(x + 14 * zoom, ly, (tw - 28 * zoom), 1.2), paint(WHITE, 0.14 * a))
            else:
                c.drawCircle(x + 20 * zoom, ly + 3 * zoom, 3 * zoom, paint(WHITE, 0.2 * a))
                c.drawRect(skia.Rect.MakeXYWH(x + 30 * zoom, ly, (tw - 60 * zoom) * 0.7, 6 * zoom),
                           paint(WHITE, 0.09 * a))
        st, col = STATUSES[(idx * 5 + 3) % len(STATUSES)]
        sa = appear(t, ta + 0.35, 0.25)
        c.drawRRect(rr(x + 12 * zoom, y + th - 36 * zoom, tw - 24 * zoom, 24 * zoom, 12 * zoom), paint(col, 0.16 * a * sa))
        label(c, st, x + 22 * zoom, y + th - 19 * zoom, max(8, 11 * zoom), col, a * sa, tracking=0.12)
    # links that try to connect and fail
    for k in range(10):
        i1, j1 = (k * 3) % cols, (k * 5) % rows
        i2, j2 = (k * 3 + 2) % cols, (k * 5 + 1) % rows
        x1, y1 = ox + i1 * (tw + gap) + tw / 2, oy + j1 * (th + gap) + th / 2
        x2, y2 = ox + i2 * (tw + gap) + tw / 2, oy + j2 * (th + gap) + th / 2
        tl = t0 + 1.2 + k * 0.22
        if t < tl:
            continue
        u = clamp((t - tl) / 0.5)
        mx_, my_ = lerp(x1, x2, u * 0.55), lerp(y1, y2, u * 0.55)
        broke = t > tl + 0.5
        col = RED if broke else GOLD
        fade = 1 - smooth(ramp(t, tl + 0.5, tl + 1.2))
        c.drawLine(x1, y1, mx_, my_, paint(col, 0.8 * alpha * fade, stroke=1.6))
        if broke:
            c.drawCircle(mx_, my_, 5, paint(RED, alpha * fade))


# --------------------------------------------------------------------------- pulses between screens
def pulse(c, t, t0, dur, p0, p1, bend=0.25, alpha=1.0, size=7):
    """A light pulse travelling along a curve from p0 to p1 over [t0, t0+dur], with a trail."""
    if t < t0 or t > t0 + dur + 0.6:
        return None
    x0, y0 = p0
    x1, y1 = p1
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    nx, ny = -(y1 - y0), (x1 - x0)
    L = math.hypot(nx, ny) + 1e-6
    ctrl = (mx + nx / L * bend * math.hypot(x1 - x0, y1 - y0), my + ny / L * bend * math.hypot(x1 - x0, y1 - y0))

    def bez(u):
        return ((1 - u) ** 2 * x0 + 2 * (1 - u) * u * ctrl[0] + u * u * x1,
                (1 - u) ** 2 * y0 + 2 * (1 - u) * u * ctrl[1] + u * u * y1)
    u = ease_in_out_cubic(clamp((t - t0) / dur))
    # faint path
    path = skia.Path()
    path.moveTo(x0, y0)
    path.quadTo(ctrl[0], ctrl[1], x1, y1)
    fade = 1 - smooth(ramp(t, t0 + dur, t0 + dur + 0.6))
    c.drawPath(path, paint(GOLD, 0.22 * alpha * fade, stroke=1.2))
    if u < 1:
        for k in range(14):
            uu = u - k * 0.012
            if uu < 0:
                break
            px, py = bez(uu)
            c.drawCircle(px, py, size * (1 - k / 14), paint(GOLD, alpha * (1 - k / 14) * 0.9, blur=2 + k * 0.3))
        px, py = bez(u)
        c.drawCircle(px, py, size * 0.55, paint((1, 0.97, 0.9), alpha))
    else:
        fl = math.exp(-(t - t0 - dur) * 6)
        c.drawCircle(x1, y1, 10 + 40 * (1 - fl), paint(GOLD, alpha * fl, stroke=2))
    return bez(u)
