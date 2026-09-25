"""Render the film. Frames are rendered in parallel worker processes, each piping raw
RGB into its own lossless ffmpeg segment; segments are joined and muxed with audio."""
import argparse
import os
import subprocess
import sys
import time
from multiprocessing import Process

import numpy as np
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import W, H, FPS, ROOT  # noqa: E402
import timeline as T  # noqa: E402

N_FRAMES = int(round(T.DURATION * FPS))


def to_u8(img):
    return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)


def worker(idx, frames, seg_path):
    import shots
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
           '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-qp', '0', '-pix_fmt', 'yuv444p',
           seg_path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t_start = time.time()
    for k, fi in enumerate(frames):
        t = (fi + 0.5) / FPS
        img = shots.frame(t, fi)
        p.stdin.write(to_u8(img).tobytes())
        if k % 24 == 0:
            el = time.time() - t_start
            print(f'[w{idx}] frame {fi} ({k + 1}/{len(frames)}) {el / (k + 1):.2f}s/frame', flush=True)
    p.stdin.close()
    p.wait()


def render_video(workers, out_path, start=0, end=N_FRAMES):
    seg_dir = os.path.join(ROOT, 'out', 'segments')
    os.makedirs(seg_dir, exist_ok=True)
    frames = list(range(start, end))
    chunks = [frames[i::1] for i in range(1)]
    # contiguous chunks keep each segment in order
    size = (len(frames) + workers - 1) // workers
    chunks = [frames[i * size:(i + 1) * size] for i in range(workers)]
    procs, segs = [], []
    for i, ch in enumerate(chunks):
        if not ch:
            continue
        seg = os.path.join(seg_dir, f'seg_{i:02d}.mkv')
        segs.append(seg)
        pr = Process(target=worker, args=(i, ch, seg))
        pr.start()
        procs.append(pr)
    for pr in procs:
        pr.join()
    lst = os.path.join(seg_dir, 'list.txt')
    with open(lst, 'w') as f:
        for s in segs:
            f.write(f"file '{s}'\n")
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy',
                    out_path], check=True)
    print('wrote', out_path)


def stills(times, out_dir, scale=1.0):
    import shots
    os.makedirs(out_dir, exist_ok=True)
    for tt in times:
        fi = int(tt * FPS)
        t0 = time.time()
        img = shots.frame(tt, fi)
        u8 = to_u8(img)[..., ::-1]
        if scale != 1.0:
            u8 = cv2.resize(u8, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        path = os.path.join(out_dir, f't{tt:06.3f}.jpg')
        cv2.imwrite(path, u8, [cv2.IMWRITE_JPEG_QUALITY, 90])
        print(f'{path}  {time.time() - t0:.2f}s', flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--stills', type=str, default=None, help='comma-separated times')
    ap.add_argument('--out-dir', type=str, default=os.path.join(ROOT, 'out', 'stills'))
    ap.add_argument('--scale', type=float, default=1.0)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--video', type=str, default=None)
    ap.add_argument('--start', type=int, default=0)
    ap.add_argument('--end', type=int, default=N_FRAMES)
    a = ap.parse_args()
    if a.stills:
        stills([float(x) for x in a.stills.split(',')], a.out_dir, a.scale)
    if a.video:
        render_video(a.workers, a.video, a.start, a.end)
