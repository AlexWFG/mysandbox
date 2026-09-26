"""Plates: every shot names a plate. A plate is a video clip (frames extracted once at the
clip's native rate), a photo (with a camera move), or a labelled placeholder card while
footage is still being sourced. All return linear-light float32 RGB at 1920x1080."""
import functools
import json
import math
import os
import subprocess
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src'))
from engine import (W, H, INK, GREY, TEXT, GOLD, load_photo, camera, u8_to_lin, srgb_to_lin, lerp, ramp,  # noqa: E402
                    ease_in_out_cubic, Layer, draw_text, paint, Wobble)

V2 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOOTAGE = os.path.join(V2, 'footage')
CACHE = os.path.join(V2, 'footage', 'frames')
MANIFEST = os.path.join(FOOTAGE, 'manifest.json')   # plate name -> {file, start, end, ...}

# Photo fallbacks (v1 plates) while video is sourced; None -> placeholder card
PHOTO_FALLBACK = {
    'cranes': 'hk_containers', 'pen_sign': 'typewriter_message', 'stamp_paper': 'typewriter_message',
    'karachi_night': 'karachi_skyline', 'aisha_night': 'keyboard_macro', 'forms': 'waiting_room',
    'passport_control': 'customs_queue', 'abudhabi_morning': 'abudhabi_dusk', 'ministry_building': 'difc_gate_night',
    'abudhabi_sunset': 'burj_sunset_gold', 'ship': 'suez_canal', 'marina_aerial': 'marina_aerial_night',
    'difc': 'difc_gate_night', 'marina': 'marina_night', 'containers': 'hk_containers', 'typewriter': 'typewriter_macro',
    'aisha_day': 'keyboard_macro', 'omar_day': 'abudhabi_dusk', 'ministry_office': 'difc_gate_night',
    'omar_desk': 'abudhabi_dusk',
}


@functools.lru_cache(maxsize=1)
def manifest():
    if os.path.exists(MANIFEST):
        return json.load(open(MANIFEST))
    return {}


class Clip:
    """Frames of one video clip, extracted once to JPEG at 2560 px wide (room to reframe)."""

    def __init__(self, name, spec):
        self.name = name
        self.spec = spec
        self.dir = os.path.join(CACHE, name)
        self.src = os.path.join(FOOTAGE, spec['file'])
        self.fps = spec.get('fps')
        self.speed = spec.get('speed', 1.0)   # playback speed baked into the pick (e.g. 0.5 on 50p slow-motion)
        self._ensure()

    def _ensure(self):
        done = os.path.join(self.dir, 'done.json')
        if os.path.exists(done):
            d = json.load(open(done))
            self.n, self.fps = d['n'], d['fps']
            return
        os.makedirs(self.dir, exist_ok=True)
        ss, to = self.spec.get('start', 0.0), self.spec.get('end')
        cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-ss', f'{ss:.3f}', '-i', self.src]
        if to is not None:
            cmd += ['-t', f'{to - ss:.3f}']
        cmd += ['-vf', "scale='if(gt(iw/ih,16/9),-2,2560)':'if(gt(iw/ih,16/9),1440,-2)',crop=2560:1440",
                '-q:v', '3', os.path.join(self.dir, 'f%05d.jpg')]
        subprocess.run(cmd, check=True)
        n = len([f for f in os.listdir(self.dir) if f.endswith('.jpg')])
        fps = self.fps
        if fps is None:
            out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                                  'stream=avg_frame_rate', '-of', 'csv=p=0', self.src], capture_output=True, text=True)
            a, b = out.stdout.strip().split('/')
            fps = float(a) / float(b)
        json.dump({'n': n, 'fps': fps}, open(done, 'w'))
        self.n, self.fps = n, fps

    @functools.lru_cache(maxsize=48)
    def frame(self, idx):
        idx = int(min(max(idx, 0), self.n - 1))
        bgr = cv2.imread(os.path.join(self.dir, f'f{idx + 1:05d}.jpg'), cv2.IMREAD_COLOR)
        return u8_to_lin(np.ascontiguousarray(bgr[:, :, ::-1]))

    def at(self, t_local, speed=1.0):
        return self.frame(int(max(0.0, t_local) * speed * self.speed * self.fps))


def prepare_all():
    """Extract every manifest clip once (call before forking render workers)."""
    for name in manifest():
        c = clip(name)
        print(f'  plate {name:18s} {c.n:4d} frames @ {c.fps:.0f} fps', flush=True)


@functools.lru_cache(maxsize=None)
def clip(name):
    spec = manifest().get(name)
    return Clip(name, spec) if spec else None


def placeholder(name, t):
    """A dark card that names the missing plate (animatic only)."""
    img = np.zeros((H, W, 3), np.float32)
    ys = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    img = img + np.array([0.012, 0.011, 0.02], np.float32) * (1.2 - ys)
    L = Layer()
    draw_text(L.c, f'[ {name.replace("_", " ")} ]', W / 2, H / 2 + 10, 'mono', 26, GREY, 0.6, tracking=0.2)
    a = L.rgba()
    return img * (1 - a[..., 3:4]) + srgb_to_lin(a[..., :3]) * 1.0


WOB = {}


def plate(name, t, t0, t1, c0=(0.5, 0.5), c1=(0.5, 0.5), z0=1.05, z1=1.12, speed=1.0, wob=1.0):
    """Linear RGB frame of plate `name` at global time t for a shot spanning [t0, t1]."""
    u = ease_in_out_cubic(ramp(t, t0, t1))
    cx, cy = lerp(c0[0], c1[0], u), lerp(c0[1], c1[1], u)
    z = lerp(z0, z1, u)
    if name not in WOB:
        WOB[name] = Wobble(abs(hash(name)) % 1000, amp=2.0 * wob, rot=0.06 * wob)
    wx, wy, wr = WOB[name](t)
    cl = clip(name)
    if cl is not None:
        src = cl.at(t - t0, speed)
        return camera(src, cx, cy, z, wr, (wx, wy))
    photo = PHOTO_FALLBACK.get(name)
    if photo:
        return camera(load_photo(photo), cx, cy, z, wr, (wx, wy))
    return placeholder(name, t)
