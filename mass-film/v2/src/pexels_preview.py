"""Download small renditions of shortlisted clips and tile 6 frames per clip, one sheet per plate."""
import concurrent.futures as cf
import json
import os
import subprocess
import sys

import requests
from PIL import Image, ImageDraw, ImageFont

os.environ.setdefault('REQUESTS_CA_BUNDLE', '/root/.ccr/ca-bundle.crt')
V2 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(V2, 'footage', 'search')
SD = os.path.join(S, 'sd')
os.makedirs(SD, exist_ok=True)
RES = json.load(open(os.path.join(S, 'results.json')))
ALL = {v['id']: v for k in RES for v in RES[k]}


def meta(i):
    if i in ALL:
        return ALL[i]
    r = requests.get(f'https://api.pexels.com/videos/videos/{i}', timeout=30)
    r.raise_for_status()
    v = r.json()
    files = [dict(q=f.get('quality'), w=f.get('width'), h=f.get('height'), fps=f.get('fps'), link=f.get('link'))
             for f in v.get('video_files', []) if f.get('file_type') == 'video/mp4']
    ALL[i] = dict(id=i, w=v['width'], h=v['height'], dur=v['duration'], url=v['url'], user=v['user']['name'], files=files)
    return ALL[i]


def small(i):
    p = os.path.join(SD, f'{i}.mp4')
    if os.path.exists(p) and os.path.getsize(p) > 10000:
        return p
    v = meta(i)
    fs = sorted([f for f in v['files'] if f['w'] and f['w'] >= 500], key=lambda f: f['w'])
    f = fs[0] if fs else v['files'][0]
    with requests.get(f['link'], stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(p, 'wb') as fh:
            for ch in r.iter_content(1 << 20):
                fh.write(ch)
    return p


def strip(i, n=6, tw=320, th=180):
    out = os.path.join(SD, f'{i}_strip.jpg')
    if os.path.exists(out):
        return out
    p = small(i)
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p],
                               capture_output=True, text=True).stdout.strip() or 1)
    img = Image.new('RGB', (n * tw, th), (0, 0, 0))
    for k in range(n):
        t = dur * (k + 0.5) / n
        fp = os.path.join(SD, f'{i}_{k}.jpg')
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', f'{t:.2f}', '-i', p, '-frames:v', '1',
                        '-vf', f'scale={tw}:{th}:force_original_aspect_ratio=increase,crop={tw}:{th}', fp])
        if os.path.exists(fp):
            img.paste(Image.open(fp), (k * tw, 0))
            os.remove(fp)
    img.save(out, quality=85)
    return out


def sheet(name, ids):
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 16)
    with cf.ThreadPoolExecutor(8) as ex:
        strips = list(ex.map(lambda i: (i, strip(i)), ids))
    rowh = 180 + 24
    img = Image.new('RGB', (1920, rowh * len(strips)), (18, 18, 22))
    d = ImageDraw.Draw(img)
    for r, (i, sp) in enumerate(strips):
        img.paste(Image.open(sp), (0, r * rowh + 24))
        v = ALL[i]
        slug = v['url'].rstrip('/').split('/')[-1]
        d.text((6, r * rowh + 3), f"{i}  {v['dur']}s  {v['w']}x{v['h']}  {v['user'][:22]}  {slug[:70]}", fill=(235, 235, 235),
               font=font)
    out = os.path.join(S, f'strips_{name}.jpg')
    img.save(out, quality=82)
    print(out, flush=True)


SHORT = {
    'open': [5311422, 8069057, 7735499, 7646396, 5846591, 6046368, 4159862, 32243438, 31806784, 37325023],
    'open2': [13378859, 13378528, 35907902, 3840442, 10458402, 9831955, 7841671, 7822026, 7578633, 7710490],
    'stamps_border': [6424125, 7593780, 7054942, 27907411, 36679174, 27778672, 3747854, 13244543],
    'karachi': [11016391, 11016337, 9223640, 35844725, 9054910, 11016338],
    'aisha_night': [7983117, 7983120, 7983125, 7983322, 7983323, 7605082, 7606057, 8100340],
    'aisha_day_forms': [8503286, 8503285, 8503287, 7351732, 8836328, 8086201, 8086205, 8836325, 8632780],
    'abudhabi': [11336422, 11336420, 11336556, 11336050, 11258028, 36765789, 32177434, 15546303, 28454582],
    'omar': [10347005, 10341378, 10347444, 10341347, 10347007, 7581241, 7580430],
    'ministry_close': [38779095, 38779103, 38779108, 7579957, 7579945, 8348320, 8421360, 6602062, 26893760],
}

if __name__ == '__main__':
    names = sys.argv[1:] or list(SHORT)
    for nm in names:
        sheet(nm, SHORT[nm])
