"""Join rendered picture pieces into one lossless master by frame ranges.
Each piece: (file, first global frame it contains, first frame to take, last frame to take + 1)."""
import os
import subprocess
import sys

V2 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(V2, 'out')


def frames(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-count_packets', '-select_streams', 'v:0', '-show_entries',
                        'stream=nb_read_packets', '-of', 'csv=p=0', path], capture_output=True, text=True)
    return int(r.stdout.strip())


def assemble(pieces, dest, total):
    args, filt, labels, n = [], [], [], 0
    for k, (path, g0, a, b) in enumerate(pieces):
        args += ['-i', path]
        filt.append(f'[{k}:v]trim=start_frame={a - g0}:end_frame={b - g0},setpts=PTS-STARTPTS[p{k}]')
        labels.append(f'[p{k}]')
        n += b - a
    assert n == total, (n, total)
    filt.append(''.join(labels) + f'concat=n={len(pieces)}:v=1:a=0[v]')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *args, '-filter_complex', ';'.join(filt), '-map', '[v]',
                    '-r', '24', '-c:v', 'libx264', '-preset', 'veryfast', '-qp', '0', '-pix_fmt', 'yuv444p', dest],
                   check=True)
    got = frames(dest)
    print(dest, got, 'frames', 'OK' if got == total else f'MISMATCH (want {total})')


if __name__ == '__main__':
    S, T, F = (os.path.join(OUT, d) for d in ('segments', 'segments_tail', 'segments_fix'))
    pieces = [
        (f'{S}/seg_00.mkv', 0, 0, 825), (f'{S}/seg_01.mkv', 825, 825, 1650),
        (f'{S}/seg_02.mkv', 1650, 1650, 2112), (f'{OUT}/segments_fix/seg_00.mkv', 2112, 2112, 2232),
        (f'{S}/seg_02.mkv', 1650, 2232, 2475), (f'{S}/seg_03.mkv', 2475, 2475, 2644),
        (f'{OUT}/tail.mkv', 2644, 2644, 3299),
    ]
    assemble(pieces, sys.argv[1] if len(sys.argv) > 1 else os.path.join(OUT, 'mass_v2_picture_lossless.mkv'), 3299)
