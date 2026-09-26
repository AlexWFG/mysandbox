"""Render the 2-minute film: stills/contact sheets for review, or the full picture in parallel
lossless segments (then muxed with the narration for an animatic)."""
import argparse
import os
import subprocess
import sys
import time
from multiprocessing import Process

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), 'src'))
from engine import W, H, FPS  # noqa: E402

V2 = os.path.dirname(HERE)
OUT = os.path.join(V2, 'out')


def to_u8(img):
    return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)


def n_frames():
    import shots2
    return int(round(shots2.DUR * FPS))


def worker(idx, frames, seg_path):
    import shots2
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
           '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-qp', '0', '-pix_fmt', 'yuv444p',
           seg_path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t_start = time.time()
    for k, fi in enumerate(frames):
        t = (fi + 0.5) / FPS
        p.stdin.write(to_u8(shots2.frame(t, fi)).tobytes())
        if k % 48 == 0:
            el = time.time() - t_start
            print(f'[w{idx}] frame {fi} ({k + 1}/{len(frames)}) {el / (k + 1):.2f}s/frame', flush=True)
    p.stdin.close()
    p.wait()


def render_video(workers, out_path, start=0, end=None):
    import plates
    plates.prepare_all()
    end = end or n_frames()
    seg_dir = os.path.join(OUT, 'segments')
    os.makedirs(seg_dir, exist_ok=True)
    frames = list(range(start, end))
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
        for sg in segs:
            f.write(f"file '{sg}'\n")
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy',
                    out_path], check=True)
    print('wrote', out_path, flush=True)


def still(t):
    import shots2
    return to_u8(shots2.frame(t, int(t * FPS)))


def sheet(times, path, cols=4, scale=0.25, labels=None):
    """Contact sheet of frames at the given times, labelled with time and segment."""
    import shots2
    segs = shots2.segments()
    tiles = []
    for t in times:
        t0 = time.time()
        img = still(t)[..., ::-1]
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        seg = [nm for nm, s0 in segs if t >= s0][-1]
        txt = f'{t:6.2f}s {seg}' + (f'  {labels[len(tiles)]}' if labels else '')
        cv2.putText(img, txt, (6, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(img, txt, (6, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 230, 255), 1, cv2.LINE_AA)
        tiles.append(img)
        print(f'  {t:7.2f}s  {time.time() - t0:5.2f}s', flush=True)
    h, w = tiles[0].shape[:2]
    rows = (len(tiles) + cols - 1) // cols
    out = np.zeros((rows * h, cols * w, 3), np.uint8)
    for k, im in enumerate(tiles):
        out[(k // cols) * h:(k // cols + 1) * h, (k % cols) * w:(k % cols + 1) * w] = im
    cv2.imwrite(path, out, [cv2.IMWRITE_JPEG_QUALITY, 88])
    print('wrote', path)


def mux(picture, audio, dest, kbps=6000):
    """Share encode of an animatic: 2-pass H.264 + AAC."""
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', picture, '-i', audio, '-map', '0:v', '-map', '1:a',
                    '-c:v', 'libx264', '-preset', 'slow', '-b:v', f'{kbps}k', '-pass', '1', '-an', '-f', 'null',
                    '-passlogfile', '/tmp/claude-0/x264pass', '/dev/null'], check=True)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', picture, '-i', audio, '-map', '0:v', '-map', '1:a',
                    '-c:v', 'libx264', '-preset', 'slow', '-b:v', f'{kbps}k', '-pass', '2', '-passlogfile',
                    '/tmp/claude-0/x264pass', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-shortest',
                    '-movflags', '+faststart', dest], check=True)
    print('wrote', dest, f'{os.path.getsize(dest) / 1e6:.1f} MB')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--sheet', type=str, default=None, help='comma-separated times')
    ap.add_argument('--sheet-out', type=str, default=os.path.join(OUT, 'sheet.jpg'))
    ap.add_argument('--cols', type=int, default=4)
    ap.add_argument('--scale', type=float, default=0.25)
    ap.add_argument('--still', type=float, default=None)
    ap.add_argument('--video', type=str, default=None)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--start', type=int, default=0)
    ap.add_argument('--end', type=int, default=None)
    a = ap.parse_args()
    if a.still is not None:
        p = os.path.join(OUT, f'still_{a.still:07.3f}.jpg')
        cv2.imwrite(p, still(a.still)[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 92])
        print('wrote', p)
    if a.sheet:
        sheet([float(x) for x in a.sheet.split(',')], a.sheet_out, a.cols, a.scale)
    if a.video:
        render_video(a.workers, a.video, a.start, a.end)
