"""Compositing engine for the Mass film.

Photos are composited in linear light (so glows and blooms behave like light),
tone-mapped with a soft shoulder, then graded in display space, where
typography and UI are laid on crisp. Film grain and letterbox come last.
"""
import os
import math
import functools

import cv2
import numpy as np
import skia
import uharfbuzz as hb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, 'assets')
W, H = 1920, 1080
FPS = 24

cv2.setNumThreads(1)  # we parallelise across processes instead


# --------------------------------------------------------------------------- palette
def hexrgb(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)], np.float32)


INK = hexrgb('07040E')
GOLD = hexrgb('FFD88A')
TEXT = hexrgb('E8E8EC')
GREY = hexrgb('8A8A94')
LABEL = hexrgb('5A5A62')
RED = hexrgb('B8322A')
PAPER = hexrgb('F1E6D0')


# --------------------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, t):
    return a + (b - a) * t


def ramp(t, t0, t1):
    if t1 == t0:
        return 1.0 if t >= t1 else 0.0
    return clamp((t - t0) / (t1 - t0))


def smooth(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def smoother(t):
    t = clamp(t)
    return t * t * t * (t * (t * 6 - 15) + 10)


def ease_out_cubic(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_in_cubic(t):
    t = clamp(t)
    return t ** 3


def ease_in_out_cubic(t):
    t = clamp(t)
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def ease_out_expo(t):
    t = clamp(t)
    return 1.0 if t >= 1 else 1 - 2 ** (-10 * t)


def ease_in_expo(t):
    t = clamp(t)
    return 0.0 if t <= 0 else 2 ** (10 * t - 10)


def ease_in_out_expo(t):
    t = clamp(t)
    if t <= 0 or t >= 1:
        return t
    return 2 ** (20 * t - 10) / 2 if t < 0.5 else (2 - 2 ** (-20 * t + 10)) / 2


def ease_out_back(t, s=1.4):
    t = clamp(t) - 1
    return t * t * ((s + 1) * t + s) + 1


def window(t, t0, t1, fin=0.25, fout=0.25):
    """1 inside [t0, t1] with smooth fades at both ends."""
    return smooth(ramp(t, t0, t0 + fin)) * (1 - smooth(ramp(t, t1 - fout, t1)))


# --------------------------------------------------------------------------- colour
_S2L = np.array([((i / 255) / 12.92) if (i / 255) <= 0.04045 else (((i / 255) + 0.055) / 1.055) ** 2.4
                 for i in range(256)], np.float32)


def u8_to_lin(img_u8):
    return _S2L[img_u8]


def lin_to_srgb(x):
    x = np.clip(x, 0.0, 1.0)
    return np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055).astype(np.float32)


def srgb_to_lin(x):
    x = np.clip(x, 0.0, 1.0)
    return np.where(x <= 0.04045, x / 12.92, np.power((x + 0.055) / 1.055, 2.4)).astype(np.float32)


def luma(img):
    return img[..., 0] * 0.2126 + img[..., 1] * 0.7152 + img[..., 2] * 0.0722


def soft_clip(lin, knee=0.72):
    """Filmic highlight shoulder in linear light: identity below knee, asymptotic to 1."""
    out = lin.copy()
    m = lin > knee
    span = 1.0 - knee
    out[m] = knee + span * (1 - np.exp(-(lin[m] - knee) / span))
    return out


def grade(img, lift=(0, 0, 0), gamma=(1, 1, 1), gain=(1, 1, 1), sat=1.0, contrast=0.0,
          shadow_tint=None, high_tint=None, tint_amt=0.0, pivot=0.42):
    """Display-space grade: lift/gamma/gain, S-curve contrast, saturation, split tone."""
    x = img
    lift = np.asarray(lift, np.float32)
    gain = np.asarray(gain, np.float32)
    gamma = np.asarray(gamma, np.float32)
    x = x * (gain - lift) + lift
    x = np.clip(x, 0, None)
    if np.any(gamma != 1):
        x = np.power(x, 1.0 / gamma)
    if contrast:
        # smooth S-curve around the pivot
        k = 1 + contrast
        x = np.clip(x, 0, 1)
        lo = pivot * np.power(np.clip(x / pivot, 0, None), k)
        hi = 1 - (1 - pivot) * np.power(np.clip((1 - x) / (1 - pivot), 0, None), k)
        x = np.where(x < pivot, lo, hi)
    if sat != 1.0:
        y = luma(x)[..., None]
        x = y + (x - y) * sat
    if tint_amt and (shadow_tint is not None or high_tint is not None):
        y = np.clip(luma(x), 0, 1)[..., None]
        if shadow_tint is not None:
            x = x + (np.asarray(shadow_tint, np.float32) - 0.5) * tint_amt * (1 - y) ** 2
        if high_tint is not None:
            x = x + (np.asarray(high_tint, np.float32) - 0.5) * tint_amt * y ** 2
    return np.clip(x, 0, 1.2).astype(np.float32)


# --------------------------------------------------------------------------- images
@functools.lru_cache(maxsize=None)
def load_photo(name, scale=2.0, denoise=3):
    """Load a plate, lightly de-block the JPEG, upscale, sharpen, return linear float32 RGB."""
    path = os.path.join(ASSETS, 'photos', name + '.jpg')
    bgr = cv2.imread(path, cv2.IMREAD_COLOR)
    if denoise:
        bgr = cv2.fastNlMeansDenoisingColored(bgr, None, denoise, denoise, 5, 15)
    if scale != 1:
        bgr = cv2.resize(bgr, None, fx=scale, fy=scale, interpolation=cv2.INTER_LANCZOS4)
        blur = cv2.GaussianBlur(bgr, (0, 0), 1.6)
        bgr = cv2.addWeighted(bgr, 1.45, blur, -0.45, 0)
    rgb = np.ascontiguousarray(bgr[:, :, ::-1])
    return u8_to_lin(rgb)


@functools.lru_cache(maxsize=None)
def load_texture(name):
    path = os.path.join(ASSETS, 'earth', name)
    bgr = cv2.imread(path, cv2.IMREAD_COLOR)
    return u8_to_lin(np.ascontiguousarray(bgr[:, :, ::-1]))


class Wobble:
    """Smooth pseudo-handheld motion (px, px, degrees)."""

    def __init__(self, seed, amp=3.0, rot=0.12, speed=1.0):
        rng = np.random.default_rng(seed)
        self.f = rng.uniform(0.18, 0.75, (3, 4)) * speed
        self.p = rng.uniform(0, 2 * np.pi, (3, 4))
        self.w = np.array([0.55, 0.28, 0.12, 0.05])
        self.a = np.array([amp, amp, rot])

    def __call__(self, t):
        v = (np.sin(2 * np.pi * self.f * t + self.p) * self.w).sum(1)
        return v * self.a


def cam_matrix(shape, cx, cy, zoom=1.0, rot=0.0, shake=(0.0, 0.0), out=(W, H)):
    """Affine (2x3) mapping plate pixels to frame pixels. (cx, cy) is the normalised plate
    point placed at frame centre; zoom=1 is the smallest scale that covers the frame. The
    centre is clamped so the frame never shows past the plate edge."""
    h, w = shape[:2]
    ow, oh = out
    s0 = max(ow / w, oh / h)
    a = math.radians(rot)
    ca, sa = math.cos(a), math.sin(a)
    s = s0 * zoom * (1 + 0.5 * abs(sa) * max(ow, oh) / min(ow, oh) if rot else 1.0)
    hx, hy = ow / (2 * s), oh / (2 * s)
    Cx = clamp(cx * w, hx, w - hx) if w > 2 * hx else w / 2
    Cy = clamp(cy * h, hy, h - hy) if h > 2 * hy else h / 2
    Ox, Oy = ow / 2 + shake[0], oh / 2 + shake[1]
    return np.array([[s * ca, -s * sa, Ox - s * (ca * Cx - sa * Cy)],
                     [s * sa, s * ca, Oy - s * (sa * Cx + ca * Cy)]], np.float32)


def camera(img, cx, cy, zoom=1.0, rot=0.0, shake=(0.0, 0.0), out=(W, H), interp=cv2.INTER_CUBIC,
           return_matrix=False):
    M = cam_matrix(img.shape, cx, cy, zoom, rot, shake, out)
    frame = cv2.warpAffine(img, M, out, flags=interp, borderMode=cv2.BORDER_REFLECT_101)
    return (frame, M) if return_matrix else frame


def map_pt(M, x, y):
    return (float(M[0, 0] * x + M[0, 1] * y + M[0, 2]), float(M[1, 0] * x + M[1, 1] * y + M[1, 2]))


def resize(img, size, interp=cv2.INTER_AREA):
    return cv2.resize(img, size, interpolation=interp)


def gblur(img, sigma):
    if sigma <= 0.05:
        return img
    return cv2.GaussianBlur(img, (0, 0), sigma)


@functools.lru_cache(maxsize=64)
def _disk(r):
    n = int(math.ceil(r))
    y, x = np.mgrid[-n:n + 1, -n:n + 1]
    d = np.sqrt(x * x + y * y)
    k = np.clip(r + 0.5 - d, 0, 1).astype(np.float32)
    return k / k.sum()


def lens_blur(img, r):
    """Disk (bokeh) blur; large radii done at reduced resolution."""
    if r < 0.6:
        return img
    if r <= 6:
        return cv2.filter2D(img, -1, _disk(round(r * 2) / 2))
    f = r / 6.0
    h, w = img.shape[:2]
    small = cv2.resize(img, (max(1, int(w / f)), max(1, int(h / f))), interpolation=cv2.INTER_AREA)
    small = cv2.filter2D(small, -1, _disk(6.0))
    return cv2.resize(small, (w, h), interpolation=cv2.INTER_LINEAR)


def bloom(lin, threshold=0.75, strength=0.35, size=1.0, tint=(1, 1, 1)):
    y = luma(lin)
    k = np.clip((y - threshold) / max(1e-4, 1 - threshold), 0, None)
    bright = lin * k[..., None]
    h, w = lin.shape[:2]
    small = cv2.resize(bright, (w // 4, h // 4), interpolation=cv2.INTER_AREA)
    b = (cv2.GaussianBlur(small, (0, 0), 3 * size) * 0.45 +
         cv2.GaussianBlur(small, (0, 0), 10 * size) * 0.35 +
         cv2.GaussianBlur(small, (0, 0), 28 * size) * 0.20)
    b = cv2.resize(b, (w, h), interpolation=cv2.INTER_LINEAR)
    return lin + strength * b * np.asarray(tint, np.float32)


def halation(lin, threshold=0.6, strength=0.25, size=1.0):
    """Film halation: warm red-orange fringe around bright edges."""
    return bloom(lin, threshold, strength, size * 0.6, tint=(1.0, 0.32, 0.12))


@functools.lru_cache(maxsize=4)
def _vignette_mask(w, h, strength, roundness):
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    nx = (x - w / 2) / (w / 2)
    ny = (y - h / 2) / (h / 2) * roundness
    r = np.sqrt(nx * nx + ny * ny)
    return (1 - strength * np.clip(r - 0.35, 0, None) ** 1.6).clip(0, 1).astype(np.float32)


def vignette(img, strength=0.45, roundness=0.75):
    h, w = img.shape[:2]
    return img * _vignette_mask(w, h, strength, roundness)[..., None]


def chroma_aberration(img, amt=0.0012):
    """Radial lateral CA: red scaled out, blue scaled in."""
    if amt <= 0:
        return img
    h, w = img.shape[:2]
    out = img.copy()
    for ch, s in ((0, 1 + amt), (2, 1 - amt)):
        M = np.array([[s, 0, (1 - s) * w / 2], [0, s, (1 - s) * h / 2]], np.float32)
        out[..., ch] = cv2.warpAffine(img[..., ch], M, (w, h), flags=cv2.INTER_LINEAR,
                                      borderMode=cv2.BORDER_REFLECT_101)
    return out


def grain(img, frame_idx, amount=0.035, size=1.4, chroma=0.25):
    """Luminance-weighted film grain, deterministic per frame."""
    h, w = img.shape[:2]
    rng = np.random.default_rng(1000 + frame_idx)
    sh, sw = int(h / size), int(w / size)
    n = rng.standard_normal((sh, sw, 3)).astype(np.float32)
    n = cv2.resize(n, (w, h), interpolation=cv2.INTER_LINEAR)
    mono = n[..., :1]
    n = mono * (1 - chroma) + n * chroma
    y = np.clip(luma(img), 0, 1)[..., None]
    weight = 0.35 + 2.6 * y * (1 - y)
    return img + n * amount * weight


def letterbox(img, bar_px, color=(0, 0, 0)):
    if bar_px <= 0.01:
        return img
    b = bar_px
    h = img.shape[0]
    out = img
    ib = int(math.floor(b))
    frac = b - ib
    c = np.asarray(color, np.float32)
    out[:ib] = c
    out[h - ib:] = c
    if frac > 0 and ib < h // 2:
        out[ib] = out[ib] * (1 - frac) + c * frac
        out[h - ib - 1] = out[h - ib - 1] * (1 - frac) + c * frac
    return out


def bars_for_aspect(aspect):
    """Letterbox bar height (px) for a target picture aspect on a 16:9 frame."""
    ph = W / aspect
    return max(0.0, (H - ph) / 2)


# --------------------------------------------------------------------------- vector / type
FONT_FILES = {
    'typewriter': os.path.join(ASSETS, 'fonts', 'CourierPrime-Regular.ttf'),
    'typewriter_bold': os.path.join(ASSETS, 'fonts', 'CourierPrime-Bold.ttf'),
    'display_light': '/usr/share/fonts/opentype/inter/InterDisplay-Light.otf',
    'display': '/usr/share/fonts/opentype/inter/InterDisplay-Regular.otf',
    'display_medium': '/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf',
    'display_semibold': '/usr/share/fonts/opentype/inter/InterDisplay-SemiBold.otf',
    'display_bold': '/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf',
    'text': '/usr/share/fonts/opentype/inter/Inter-Regular.otf',
    'text_medium': '/usr/share/fonts/opentype/inter/Inter-Medium.otf',
    'text_semibold': '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf',
    'mono': '/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf',
    'mono_medium': '/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Medium.ttf',
    'mono_light': '/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Light.ttf',
}


@functools.lru_cache(maxsize=None)
def typeface(key):
    return skia.Typeface.MakeFromFile(FONT_FILES[key])


@functools.lru_cache(maxsize=None)
def hb_font(key):
    blob = hb.Blob.from_file_path(FONT_FILES[key])
    face = hb.Face(blob)
    f = hb.Font(face)
    return f, face.upem


@functools.lru_cache(maxsize=4096)
def shape(text, key, size, tracking=0.0):
    """HarfBuzz-shaped glyph run: (glyph ids, x positions, cluster->char idx, total width)."""
    f, upem = hb_font(key)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(f, buf, {'kern': True, 'liga': True})
    sc = size / upem
    gids, xs, clusters = [], [], []
    x = 0.0
    n = len(buf.glyph_infos)
    for i, (info, pos) in enumerate(zip(buf.glyph_infos, buf.glyph_positions)):
        gids.append(info.codepoint)
        xs.append(x + pos.x_offset * sc)
        clusters.append(info.cluster)
        x += pos.x_advance * sc
        if i < n - 1:
            x += tracking * size
    return tuple(gids), tuple(xs), tuple(clusters), x


def text_width(text, key, size, tracking=0.0):
    return shape(text, key, size, tracking)[3]


class Layer:
    """RGBA8 premultiplied skia canvas backed by numpy; convert with .rgba()."""

    def __init__(self, w=W, h=H):
        self.arr = np.zeros((h, w, 4), np.uint8)
        self.surface = skia.Surface(self.arr, colorType=skia.kRGBA_8888_ColorType,
                                    alphaType=skia.kPremul_AlphaType)
        self.c = self.surface.getCanvas()

    def rgba(self):
        return self.arr.astype(np.float32) * (1.0 / 255.0)


def paint(color, alpha=1.0, stroke=None, blur=0.0, aa=True, blend=None, cap='round'):
    r, g, b = [float(v) for v in color[:3]]
    p = skia.Paint(AntiAlias=aa, Color4f=skia.Color4f(r, g, b, float(clamp(alpha))))
    if stroke is not None:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(float(stroke))
        p.setStrokeCap(skia.Paint.kRound_Cap if cap == 'round' else skia.Paint.kButt_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur > 0:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, float(blur)))
    if blend == 'plus':
        p.setBlendMode(skia.BlendMode.kPlus)
    return p


def draw_text(canvas, text, x, y, key, size, color=TEXT, alpha=1.0, tracking=0.0, align='center',
              char_alpha=None, char_dy=None, blur=0.0, glow=0.0, glow_color=None, glow_alpha=0.5):
    """Draw kerned text. char_alpha: optional per-character alpha multipliers (by char index).
    char_dy: optional per-character vertical offsets. Returns (x_start, width)."""
    if alpha <= 0.002 or not text:
        return x, 0
    gids, xs, clusters, width = shape(text, key, size, tracking)
    if align == 'center':
        x0 = x - width / 2
    elif align == 'right':
        x0 = x - width
    else:
        x0 = x
    font = skia.Font(typeface(key), size)
    font.setSubpixel(True)
    font.setEdging(skia.Font.Edging.kAntiAlias)
    font.setHinting(skia.FontHinting.kNone)

    def run(p, dx=0.0, dy=0.0):
        if char_alpha is None and char_dy is None:
            b = skia.TextBlobBuilder()
            b.allocRunPos(font, list(gids), [skia.Point(x0 + xx + dx, y + dy) for xx in xs])
            canvas.drawTextBlob(b.make(), 0, 0, p)
            return
        base = p.getColor4f()
        for g, xx, cl in zip(gids, xs, clusters):
            a = char_alpha[cl] if char_alpha is not None else 1.0
            if a <= 0.002:
                continue
            ddy = char_dy[cl] if char_dy is not None else 0.0
            q = skia.Paint(p)
            q.setColor4f(skia.Color4f(base.fR, base.fG, base.fB, base.fA * a))
            b = skia.TextBlobBuilder()
            b.allocRunPos(font, [g], [skia.Point(x0 + xx + dx, y + dy + ddy)])
            canvas.drawTextBlob(b.make(), 0, 0, q)

    if glow > 0:
        gc = glow_color if glow_color is not None else color
        run(paint(gc, alpha * glow_alpha, blur=glow))
    run(paint(color, alpha, blur=blur))
    return x0, width


def composite(base, layer_rgba, opacity=1.0):
    """Premultiplied 'over' of a layer onto a display-space RGB image."""
    a = layer_rgba[..., 3:4] * opacity
    return base * (1 - a) + layer_rgba[..., :3] * opacity


def add_light(base, layer_rgba, gain=1.0):
    """Additive (screen-like) light from a premultiplied layer."""
    return base + layer_rgba[..., :3] * gain


def frosted(base, rect, radius=18, sigma=18, tint=(0.03, 0.03, 0.06), tint_a=0.55, alpha=1.0):
    """Frosted-glass panel: blur what's under a rounded rect and tint it."""
    x0, y0, x1, y1 = [int(round(v)) for v in rect]
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(base.shape[1], x1), min(base.shape[0], y1)
    if x1 <= x0 or y1 <= y0 or alpha <= 0:
        return base
    pad = int(sigma * 2)
    X0, Y0 = max(0, x0 - pad), max(0, y0 - pad)
    X1, Y1 = min(base.shape[1], x1 + pad), min(base.shape[0], y1 + pad)
    region = cv2.GaussianBlur(base[Y0:Y1, X0:X1], (0, 0), sigma)[y0 - Y0:y1 - Y0, x0 - X0:x1 - X0]
    region = region * (1 - tint_a) + np.asarray(tint, np.float32) * tint_a
    arr = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
    s = skia.Surface(arr, colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kPremul_AlphaType)
    s.getCanvas().drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeWH(x1 - x0, y1 - y0), radius, radius),
                            paint((1, 1, 1)))
    m = arr[..., 3:4].astype(np.float32) / 255.0 * alpha
    out = base.copy()
    out[y0:y1, x0:x1] = out[y0:y1, x0:x1] * (1 - m) + region * m
    return out


def frosted_path(base, path, sigma=14, tint=(0.03, 0.03, 0.06), tint_a=0.5, alpha=1.0):
    """Frosted glass under an arbitrary skia path."""
    if alpha <= 0:
        return base
    b = path.getBounds()
    pad = int(sigma * 2) + 2
    x0, y0 = max(0, int(b.left()) - 1), max(0, int(b.top()) - 1)
    x1, y1 = min(base.shape[1], int(b.right()) + 2), min(base.shape[0], int(b.bottom()) + 2)
    if x1 <= x0 or y1 <= y0:
        return base
    X0, Y0 = max(0, x0 - pad), max(0, y0 - pad)
    X1, Y1 = min(base.shape[1], x1 + pad), min(base.shape[0], y1 + pad)
    region = cv2.GaussianBlur(base[Y0:Y1, X0:X1], (0, 0), sigma)[y0 - Y0:y1 - Y0, x0 - X0:x1 - X0]
    region = region * (1 - tint_a) + np.asarray(tint, np.float32) * tint_a
    arr = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
    s = skia.Surface(arr, colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kPremul_AlphaType)
    cv_ = s.getCanvas()
    cv_.translate(-x0, -y0)
    cv_.drawPath(path, paint((1, 1, 1)))
    m = arr[..., 3:4].astype(np.float32) / 255.0 * alpha
    out = base.copy()
    out[y0:y1, x0:x1] = out[y0:y1, x0:x1] * (1 - m) + region * m
    return out


# --------------------------------------------------------------------------- Mass mark
# Geometry fitted to the mass.inc header logo (pixel-mask fit at native resolution;
# units are px of a 53 px tall mark). Two parallelogram bars (slant dx/dy = 0.403)
# with generously rounded obtuse corners and near-sharp acute corners, plus a "foot":
# a circle merged with the lower part of a bar.
_BAR = dict(w=23.725, sl=0.403, yt=13.669, yb=66.675, r=9.39, r_acute=0.8)
_BAR_X = (23.275, 58.206)
_FOOT = dict(cx=19.931, cy=56.575, r=10.0, xb=35.0, sl=0.395, rc=9.75)


def _bar_path(x_tl):
    b = _BAR
    y0, y1 = b['yt'], b['yb']
    h = y1 - y0
    TL = (x_tl, y0)
    TR = (x_tl + b['w'], y0)
    BR = (x_tl + b['w'] + b['sl'] * h, y1)
    BL = (x_tl + b['sl'] * h, y1)
    pts = [TL, TR, BR, BL]
    rs = [b['r_acute'], b['r'], b['r_acute'], b['r']]
    p = skia.Path()
    p.moveTo((TL[0] + TR[0]) / 2, y0)
    for i in range(4):
        a = pts[(i + 1) % 4]
        c = pts[(i + 2) % 4]
        p.arcTo(a[0], a[1], c[0], c[1], rs[(i + 1) % 4])
    p.close()
    return p


def _foot_path():
    f = _FOOT
    circ = skia.Path()
    circ.addCircle(f['cx'], f['cy'], f['r'])
    y0, y1 = f['cy'] - f['r'], _BAR['yb']
    xr_top = f['xb'] - f['sl'] * (y1 - y0)
    quad = skia.Path()
    quad.moveTo(f['cx'], y0)
    quad.arcTo(xr_top, y0, f['xb'], y1, f['rc'])
    quad.lineTo(f['xb'], y1)
    quad.lineTo(f['cx'], y1)
    quad.close()
    return skia.Op(circ, quad, skia.PathOp.kUnion_PathOp)


_MARK_CACHE = {}


def mark_paths():
    """The three shapes of the Mass mark, normalised to height 1, left edge at 0."""
    if 'paths' in _MARK_CACHE:
        return _MARK_CACHE['paths']
    raw = [_foot_path(), _bar_path(_BAR_X[0]), _bar_path(_BAR_X[1])]
    x_min = _FOOT['cx'] - _FOOT['r']
    y_min, y_max = _BAR['yt'], _BAR['yb']
    s = 1.0 / (y_max - y_min)
    m = skia.Matrix()
    m.setScaleTranslate(s, s, -x_min * s, -y_min * s)
    out = []
    for p in raw:
        q = skia.Path(p)
        q.transform(m)
        out.append(q)
    _MARK_CACHE['paths'] = out
    x_max = _BAR_X[1] + _BAR['w'] + _BAR['sl'] * (y_max - y_min)
    _MARK_CACHE['width'] = (x_max - x_min) * s
    return out


def mark_width():
    mark_paths()
    return _MARK_CACHE['width']


def placed_mark(x, y, height):
    """Mark paths scaled to `height`, top-left at (x, y)."""
    out = []
    m = skia.Matrix()
    m.setScaleTranslate(height, height, x, y)
    for p in mark_paths():
        q = skia.Path(p)
        q.transform(m)
        out.append(q)
    return out
