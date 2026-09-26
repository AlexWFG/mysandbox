"""Delivery encodes: 2-pass H.264 + AAC from the lossless picture and the mix.
  share  : 1280x720, fits the 30 MB phone-delivery limit (review copies)
  master : 1920x1080 high bitrate, under GitHub's 100 MB per-file limit"""
import os
import subprocess
import sys

V2 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(V2, 'out')
PRESETS = {
    'share': dict(vf='scale=1280:720:flags=lanczos,hqdn3d=1.2:1.2:3:3', kbps=1550, akbps=128, tune='film'),
    'master': dict(vf='null', kbps=5200, akbps=256, tune='grain'),
}


def encode(picture, audio, dest, preset):
    p = PRESETS[preset]
    common = ['-i', picture, '-i', audio, '-map', '0:v', '-map', '1:a', '-vf', p['vf'], '-c:v', 'libx264',
              '-preset', 'slow', '-tune', p['tune'], '-aq-mode', '3', '-b:v', f"{p['kbps']}k", '-pix_fmt', 'yuv420p',
              '-passlogfile', f'/tmp/claude-0/x264_{preset}']
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *common, '-pass', '1', '-an', '-f', 'null', '/dev/null'],
                   check=True)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *common, '-pass', '2', '-c:a', 'aac', '-b:a',
                    f"{p['akbps']}k", '-shortest', '-movflags', '+faststart', dest], check=True)
    print(f'{dest}: {os.path.getsize(dest) / 2 ** 20:.1f} MiB')


if __name__ == '__main__':
    preset = sys.argv[1] if len(sys.argv) > 1 else 'share'
    picture = sys.argv[2] if len(sys.argv) > 2 else os.path.join(OUT, 'mass_v2_picture.mkv')
    audio = sys.argv[3] if len(sys.argv) > 3 else os.path.join(OUT, 'mass_v2_mix_scratch.wav')
    dest = sys.argv[4] if len(sys.argv) > 4 else os.path.join(OUT, f'MASS_v2_{preset}.mp4')
    encode(picture, audio, dest, preset)
