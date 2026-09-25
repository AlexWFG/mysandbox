"""Mux the lossless picture with the score into the delivery MP4, and build a review
contact sheet from the encoded file."""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'out')


def run(cmd):
    print(' '.join(cmd))
    subprocess.run(cmd, check=True)


def encode(picture, score, dest, kbps=11000):
    """Two-pass H.264 at a fixed budget: grain is costly, so CRF would balloon the file."""
    common = ['-c:v', 'libx264', '-preset', 'slow', '-tune', 'grain', '-profile:v', 'high',
              '-b:v', f'{kbps}k', '-maxrate', f'{int(kbps * 1.6)}k', '-bufsize', f'{kbps * 2}k',
              '-pix_fmt', 'yuv420p', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709']
    log = os.path.join(OUT, 'x264_2pass')
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', picture] + common +
        ['-pass', '1', '-passlogfile', log, '-an', '-f', 'mp4', '/dev/null'])
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', picture, '-i', score, '-map', '0:v:0', '-map', '1:a:0'] + common +
        ['-pass', '2', '-passlogfile', log, '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-shortest',
         '-movflags', '+faststart', dest])
    for f in os.listdir(OUT):
        if f.startswith('x264_2pass'):
            os.remove(os.path.join(OUT, f))


def contact_sheet(video, dest, times):
    tmp = os.path.join(OUT, 'sheet_frames')
    os.makedirs(tmp, exist_ok=True)
    files = []
    for i, t in enumerate(times):
        f = os.path.join(tmp, f'{i:02d}.png')
        run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', f'{t:.3f}', '-i', video, '-frames:v', '1',
             '-vf', "scale=640:-1,drawtext=fontfile=/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf:"
             f"text='{t:05.2f}s':x=10:y=10:fontsize=18:fontcolor=white@0.85", f])
        files.append(f)
    cols = 4
    inputs = []
    for f in files:
        inputs += ['-i', f]
    rows = (len(files) + cols - 1) // cols
    layout = '|'.join(f'{(k % cols) * 640}_{(k // cols) * 360}' for k in range(len(files)))
    run(['ffmpeg', '-y', '-loglevel', 'error'] + inputs +
        ['-filter_complex', f'xstack=inputs={len(files)}:layout={layout}:fill=black', '-frames:v', '1', dest])


if __name__ == '__main__':
    picture = os.path.join(OUT, 'mass_picture_lossless.mkv')
    score = os.path.join(OUT, 'mass_score.wav')
    dest = os.path.join(OUT, 'MASS_OneEconomy_30s_1080p.mp4')
    if '--sheet-only' not in sys.argv:
        encode(picture, score, dest)
    contact_sheet(dest, os.path.join(OUT, 'MASS_contact_sheet.jpg'),
                  [1.2, 3.8, 5.4, 7.0, 8.9, 10.9, 12.0, 13.4, 15.0, 16.9, 18.9, 20.9, 22.9, 24.2, 26.6, 28.5])
