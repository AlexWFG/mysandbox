"""A camera over a canvas of screens: the three-way 'one action, three wins' sequence.

Each panel is a full 1920x1080 scene placed on a large canvas. The camera (centre, zoom)
flies between a single panel filling the frame and an overview of all three, with light
pulses travelling between panels. UI is drawn with a canvas transform, so it stays crisp
at every zoom; plates are warped into each panel's screen rectangle."""
import math
import os
import sys

import cv2
import numpy as np
import skia

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src'))
from engine import (W, H, INK, GOLD, TEXT, GREY, clamp, lerp, ramp, smooth, ease_in_out_cubic,  # noqa: E402
                    ease_out_cubic, Layer, paint, draw_text, frosted, composite, gblur)
from ui2 import UIFrame, rr, label, pulse, appear  # noqa: E402

GAP = 240.0          # canvas units between panels
PANEL_R = 46.0       # corner radius (canvas units)


class Cam:
    def __init__(self, cx, cy, zoom):
        self.cx, self.cy, self.zoom = cx, cy, zoom

    def to_screen(self, x, y):
        return (x - self.cx) * self.zoom + W / 2, (y - self.cy) * self.zoom + H / 2

    def matrix(self):
        m = skia.Matrix()
        m.setScaleTranslate(self.zoom, self.zoom, W / 2 - self.cx * self.zoom, H / 2 - self.cy * self.zoom)
        return m


def panel_origin(i):
    """Top-left of panel i on the canvas (panels in a row)."""
    return i * (W + GAP), 0.0


def panel_center(i):
    x, y = panel_origin(i)
    return x + W / 2, y + H / 2


def overview_cam(n=3, margin=1.12):
    x0 = 0
    x1 = (n - 1) * (W + GAP) + W
    cx = (x0 + x1) / 2
    zoom = W / ((x1 - x0) * margin)
    return Cam(cx, H / 2 + 40, zoom)


def focus_cam(i):
    cx, cy = panel_center(i)
    return Cam(cx, cy, 1.0)


def blend_cam(a, b, u):
    """Zoom-aware interpolation: interpolate log-zoom, and centre so the motion feels like a dolly."""
    u = ease_in_out_cubic(u)
    z = math.exp(lerp(math.log(a.zoom), math.log(b.zoom), u))
    # centre interpolation weighted to keep the path smooth in screen space
    k = (1 / z - 1 / a.zoom) / (1 / b.zoom - 1 / a.zoom) if abs(1 / b.zoom - 1 / a.zoom) > 1e-6 else u
    k = clamp(k)
    return Cam(lerp(a.cx, b.cx, k), lerp(a.cy, b.cy, k), z)


def cam_path(t, keys):
    """keys: list of (time, Cam). Holds between keys, moves over each (t0, t1) segment."""
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, c0), (t1, c1) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            return blend_cam(c0, c1, (t - t0) / (t1 - t0)) if t1 > t0 else c1
    return keys[-1][1]


def draw_panels(t, cam, panels, links=(), backdrop=None):
    """panels: list of dicts {plate: fn(t)->display RGB (H,W,3), ui: fn(ui, t) drawing in panel-local coords,
    title: str, sub: str}. Returns the composed display image."""
    img = np.zeros((H, W, 3), np.float32) + INK * 0.6 if backdrop is None else backdrop.copy()
    shadow = Layer()
    sc = shadow.c
    frames = []
    for i, p in enumerate(panels):
        ox, oy = panel_origin(i)
        x0, y0 = cam.to_screen(ox, oy)
        x1, y1 = cam.to_screen(ox + W, oy + H)
        if x1 < 0 or x0 > W or y1 < 0 or y0 > H:
            frames.append(None)
            continue
        frames.append((x0, y0, x1, y1))
        r = PANEL_R * cam.zoom
        sc.drawRRect(rr(x0, y0 + 18 * cam.zoom, x1 - x0, y1 - y0, r), paint((0, 0, 0), 0.6, blur=40 * cam.zoom + 4))
    img = composite(img, shadow.rgba())
    for i, p in enumerate(panels):
        fr = frames[i]
        if fr is None:
            continue
        x0, y0, x1, y1 = fr
        sw, sh = x1 - x0, y1 - y0
        # plate warped into the panel rect
        plate = p['plate'](t)
        M = np.array([[sw / W, 0, x0], [0, sh / H, y0]], np.float32)
        warped = cv2.warpAffine(plate, M, (W, H), flags=cv2.INTER_AREA if sw < W * 0.9 else cv2.INTER_LINEAR,
                                borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
        mask_l = Layer()
        mask_l.c.drawRRect(rr(x0, y0, sw, sh, PANEL_R * cam.zoom), paint((1, 1, 1)))
        m = mask_l.arr[..., 3:4].astype(np.float32) / 255.0
        img = img * (1 - m) + warped * m
        # panel UI in panel-local coordinates
        if p.get('ui'):
            ui = UIFrame()
            ui.set_view(cam.zoom, x0, y0, clip=(x0, y0, sw, sh, PANEL_R * cam.zoom))
            p['ui'](ui, t)
            img = ui.apply(img)
    # borders, titles and links over everything
    top = Layer()
    c = top.c
    for i, p in enumerate(panels):
        fr = frames[i]
        if fr is None:
            continue
        x0, y0, x1, y1 = fr
        hl = p.get('highlight', lambda t: 0.0)(t)
        c.drawRRect(rr(x0, y0, x1 - x0, y1 - y0, PANEL_R * cam.zoom), paint((1, 1, 1), 0.14 + 0.5 * hl, stroke=1.4))
        if hl > 0.01:
            c.drawRRect(rr(x0, y0, x1 - x0, y1 - y0, PANEL_R * cam.zoom), paint(GOLD, 0.5 * hl, stroke=3, blur=6))
        # titles only read in the overview
        ta = clamp((0.62 - cam.zoom) / 0.25)
        if ta > 0.01 and p.get('title'):
            label(c, p['title'].upper(), x0, y0 - 28, 20, TEXT, ta, tracking=0.22)
            if p.get('sub'):
                label(c, p['sub'].upper(), x0, y0 - 56, 15, GOLD, ta, tracking=0.26)
    for (a_i, b_i, t0, dur) in links:
        fa, fb = frames[a_i], frames[b_i]
        ca = cam.to_screen(*panel_center(a_i))
        cb = cam.to_screen(*panel_center(b_i))
        # start/end at the facing panel edges
        pa = (ca[0] + (W / 2) * cam.zoom * (1 if b_i > a_i else -1), ca[1])
        pb = (cb[0] + (W / 2) * cam.zoom * (-1 if b_i > a_i else 1), cb[1])
        pulse(c, t, t0, dur, pa, pb, bend=-0.35, alpha=1.0, size=9)
    return composite(img, top.rgba())
