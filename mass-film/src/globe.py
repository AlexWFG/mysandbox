"""Earth at night: NASA Black Marble on a ray-traced sphere, with atmosphere,
an orbital-sunrise crescent, stars, and projected corridor arcs."""
import math
import functools

import cv2
import numpy as np

from engine import W, H, load_texture, luma


def ll_to_vec(lat, lon):
    la, lo = math.radians(lat), math.radians(lon)
    return np.array([math.cos(la) * math.sin(lo), math.sin(la), math.cos(la) * math.cos(lo)], np.float64)


def normalize(v):
    return v / np.linalg.norm(v)


def slerp(a, b, s):
    om = math.acos(np.clip(np.dot(a, b), -1, 1))
    if om < 1e-6:
        return a
    return (math.sin((1 - s) * om) * a + math.sin(s * om) * b) / math.sin(om)


@functools.lru_cache(maxsize=1)
def textures():
    """Split the Black Marble into moonlit terrain and city lights; linear float32."""
    night = load_texture('earth-night.jpg')              # linear RGB
    day = load_texture('earth-blue-marble.jpg')
    warm = np.clip(night[..., 0] - night[..., 2] * 0.9, 0, None)
    lights_mask = np.clip(warm * 9.0, 0, 1) ** 0.8
    lights = night * lights_mask[..., None]
    terrain = night * (1 - lights_mask[..., None])
    # terrain toward deep navy, lights toward sodium gold
    t_l = luma(terrain)[..., None]
    terrain = t_l * np.array([0.30, 0.55, 1.0], np.float32) * 0.55
    l_l = luma(lights)[..., None]
    lights = l_l * np.array([1.0, 0.72, 0.38], np.float32) * 3.2
    ocean = (day[..., 2] > day[..., 0] * 1.4).astype(np.float32)
    return (np.ascontiguousarray(terrain.astype(np.float32)),
            np.ascontiguousarray(lights.astype(np.float32)),
            np.ascontiguousarray(day.astype(np.float32)),
            np.ascontiguousarray(ocean))


class Cam:
    def __init__(self, pos, target, up=(0, 1, 0), fov_v=36.0, roll=0.0, w=W, h=H):
        self.pos = np.asarray(pos, np.float64)
        f = normalize(np.asarray(target, np.float64) - self.pos)
        r = normalize(np.cross(f, np.asarray(up, np.float64)))
        u = np.cross(r, f)
        if roll:
            a = math.radians(roll)
            r, u = r * math.cos(a) + u * math.sin(a), -r * math.sin(a) + u * math.cos(a)
        self.f, self.r, self.u = f, r, u
        self.w, self.h = w, h
        self.focal = (h / 2) / math.tan(math.radians(fov_v) / 2)

    def project(self, p):
        d = np.asarray(p, np.float64) - self.pos
        z = np.dot(d, self.f)
        if z <= 1e-6:
            return None
        x = np.dot(d, self.r) / z * self.focal + self.w / 2
        y = -np.dot(d, self.u) / z * self.focal + self.h / 2
        return x, y, z

    def occluded(self, p):
        """True if the unit sphere blocks the line of sight to p."""
        d = np.asarray(p, np.float64) - self.pos
        L = np.linalg.norm(d)
        D = d / L
        b = np.dot(self.pos, D)
        c = np.dot(self.pos, self.pos) - 1.0
        disc = b * b - c
        if disc <= 0:
            return False
        t = -b - math.sqrt(disc)
        return 0 < t < L - 1e-4


@functools.lru_cache(maxsize=2)
def _pixel_grid(w, h):
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    return xs + 0.5, ys + 0.5


@functools.lru_cache(maxsize=1)
def starfield(w=W * 2, h=H * 2, seed=7):
    rng = np.random.default_rng(seed)
    img = np.zeros((h, w, 3), np.float32)
    n = 5200
    xs = rng.uniform(0, w, n)
    ys = rng.uniform(0, h, n)
    mag = rng.pareto(2.2, n) * 0.08 + 0.015
    mag = np.clip(mag, 0, 2.5)
    temp = rng.uniform(0, 1, n)
    for x, y, m, tt in zip(xs, ys, mag, temp):
        col = np.array([0.85 + 0.3 * tt, 0.9, 1.15 - 0.3 * tt], np.float32)
        xi, yi = int(x), int(y)
        if 1 <= xi < w - 1 and 1 <= yi < h - 1:
            img[yi, xi] += col * m
            if m > 0.25:
                img[yi - 1:yi + 2, xi - 1:xi + 2] += col * m * 0.18
    img = cv2.GaussianBlur(img, (0, 0), 0.6)
    # a faint, smooth milky band
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    band = np.exp(-((yy - 0.30 * h - 0.22 * (xx - w / 2)) / (0.20 * h)) ** 2)
    img += (band * 0.006)[..., None] * np.array([0.65, 0.72, 1.0], np.float32)
    return img


def render_earth(cam, sun_dir=None, star_shift=(0.0, 0.0), exposure=1.0, lights_gain=1.0,
                 terrain_gain=1.0, atmo_gain=1.0, rot_lon=0.0):
    """Linear-light render of the night Earth for camera `cam`. Returns (img, hit_mask)."""
    terrain, lights, day, ocean = textures()
    th, tw = terrain.shape[:2]
    w, h = cam.w, cam.h
    xs, ys = _pixel_grid(w, h)
    dx = (xs - w / 2) / cam.focal
    dy = -(ys - h / 2) / cam.focal
    D = (dx[..., None] * cam.r.astype(np.float32) + dy[..., None] * cam.u.astype(np.float32)
         + cam.f.astype(np.float32))
    D /= np.linalg.norm(D, axis=-1, keepdims=True)
    O = cam.pos.astype(np.float32)
    b = D @ O                                   # dot(O, D)
    c = float(O @ O) - 1.0
    disc = b * b - c
    hit = disc > 0
    t = np.where(hit, -b - np.sqrt(np.clip(disc, 0, None)), 0).astype(np.float32)
    hit &= t > 0
    P = O + D * t[..., None]
    N = P  # unit sphere
    lat = np.arcsin(np.clip(N[..., 1], -1, 1))
    lon = np.arctan2(N[..., 0], N[..., 2]) + math.radians(rot_lon)
    u = ((lon / (2 * math.pi) + 0.5) % 1.0) * tw - 0.5
    v = (0.5 - lat / math.pi) * th - 0.5
    u = u.astype(np.float32)
    v = v.astype(np.float32)
    ter = cv2.remap(terrain, u, v, cv2.INTER_CUBIC, borderMode=cv2.BORDER_WRAP)
    lig = cv2.remap(lights, u, v, cv2.INTER_CUBIC, borderMode=cv2.BORDER_WRAP)
    mu = np.clip(-(N * D).sum(-1), 0, 1)
    limb = (0.18 + 0.82 * mu ** 0.55)[..., None]
    surf = ter * terrain_gain * limb + np.clip(lig, 0, None) * lights_gain * (0.35 + 0.65 * mu[..., None])

    img = np.zeros((h, w, 3), np.float32)
    # stars (behind everything)
    sf = starfield()
    sx0 = int(sf.shape[1] / 4 + star_shift[0])
    sy0 = int(sf.shape[0] / 4 + star_shift[1])
    img += sf[sy0:sy0 + h, sx0:sx0 + w] * (~hit)[..., None]

    atmo_col = np.array([0.22, 0.48, 1.0], np.float32)
    warm_col = np.array([1.0, 0.62, 0.30], np.float32)
    if sun_dir is not None:
        S = normalize(np.asarray(sun_dir, np.float64)).astype(np.float32)
        nds = (N * S).sum(-1)
        dayw = np.clip(nds * 3.2 + 0.05, 0, 1) ** 1.5
        dtex = cv2.remap(day, u, v, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
        oc = cv2.remap(ocean, u, v, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
        # specular sun glint on water near the terminator
        R = D - 2 * (D * N).sum(-1, keepdims=True) * N
        spec = np.clip((R * S).sum(-1), 0, 1) ** 60 * oc * 2.5
        surf = surf * (1 - dayw[..., None] * 0.85) + (dtex * 1.1 + spec[..., None] * warm_col) * dayw[..., None] * np.clip(nds, 0, 1)[..., None] * 2.2
    img = np.where(hit[..., None], surf, img)

    # atmosphere: thin rim inside the disc + halo outside; warm where the sun is near
    tc = np.clip(-b, 0, None)
    Pc = O + D * tc[..., None]
    dcen = np.linalg.norm(Pc, axis=-1)
    outside = (~hit) & (b < 0)
    hd = np.clip(dcen - 1, 0, None)
    halo = np.where(outside, np.exp(-hd / 0.010) * 0.55 + np.exp(-hd / 0.045) * 0.16 +
                    np.exp(-hd / 0.20) * 0.05, 0).astype(np.float32)
    rim = np.where(hit, (1 - mu) ** 4.0 * 0.55, 0).astype(np.float32)
    atm = (halo + rim)[..., None] * atmo_col
    if sun_dir is not None:
        Pn = Pc / np.clip(dcen, 1e-6, None)[..., None]
        sw = np.clip((Pn * S).sum(-1) * 1.25 + 0.15, 0, 1) ** 2.2
        atm = atm * (1 - sw[..., None]) + (halo * 1.8 + rim)[..., None] * sw[..., None] * warm_col * 2.6
    img = img + atm * atmo_gain
    return img * exposure, hit


def arc_points(a_ll, b_ll, n=96, lift=None):
    A, B = ll_to_vec(*a_ll), ll_to_vec(*b_ll)
    ang = math.acos(np.clip(np.dot(A, B), -1, 1))
    if lift is None:
        lift = 0.035 + 0.22 * ang / math.pi
    pts = []
    for i in range(n):
        s = i / (n - 1)
        p = slerp(A, B, s)
        pts.append(p * (1 + lift * math.sin(math.pi * s)))
    return pts
