"""Search Pexels for every plate, keep the metadata, and build one thumbnail contact sheet
per plate for picking by eye. Auth header is added by the environment's proxy."""
import concurrent.futures as cf
import io
import json
import os
import sys
import urllib.parse

import requests
from PIL import Image, ImageDraw, ImageFont

os.environ.setdefault('REQUESTS_CA_BUNDLE', '/root/.ccr/ca-bundle.crt')
V2 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(V2, 'footage', 'search')
THUMBS = os.path.join(OUT, 'thumbs')
os.makedirs(THUMBS, exist_ok=True)

QUERIES = {
    'handshake': ['business handshake', 'handshake close up', 'handshake slow motion'],
    'welder': ['welding sparks', 'welder working', 'factory worker sparks'],
    'cranes': ['container port cranes', 'container terminal aerial', 'cargo ship port', 'port cranes night'],
    'pen_sign': ['signing contract', 'signing document pen', 'signature pen close up'],
    'stamp_paper': ['rubber stamp', 'stamping documents', 'paperwork desk', 'documents on desk'],
    'karachi_night': ['karachi', 'karachi night', 'pakistan city night', 'karachi traffic'],
    'aisha_night': ['woman laptop night', 'woman working late night', 'hijab woman laptop', 'south asian woman laptop',
                    'woman coding dark room', 'indian woman working laptop night'],
    'forms': ['filling form', 'paperwork stress', 'waiting room office', 'office paperwork frustrated'],
    'passport_control': ['passport control', 'airport immigration', 'passport stamp', 'airport queue'],
    'abudhabi_morning': ['abu dhabi', 'abu dhabi skyline', 'abu dhabi aerial', 'abu dhabi morning'],
    'omar_desk': ['arab man office', 'man in kandura', 'emirati man', 'arab businessman laptop',
                  'middle eastern man office computer'],
    'ministry_building': ['government building', 'abu dhabi building night', 'modern building night exterior',
                          'office tower night'],
    'abudhabi_sunset': ['abu dhabi sunset', 'dubai skyline sunset', 'dubai aerial sunset', 'sheikh zayed road'],
    'aisha_day': ['woman working laptop morning', 'south asian woman smiling laptop', 'woman laptop home office',
                  'young woman phone smiling'],
    'ministry_office': ['control room screens', 'data analyst screens', 'man looking at data screens',
                        'office dashboard monitors'],
    'close': ['woman celebrating laptop', 'contactless payment', 'card payment terminal', 'container ship aerial',
              'dubai marina aerial night', 'city lights aerial night'],
}


def search(q, per_page=20):
    r = requests.get('https://api.pexels.com/videos/search',
                     params=dict(query=q, orientation='landscape', size='medium', per_page=per_page), timeout=30)
    r.raise_for_status()
    return r.json().get('videos', [])


def slim(v):
    files = [dict(q=f.get('quality'), w=f.get('width'), h=f.get('height'), fps=f.get('fps'), link=f.get('link'))
             for f in v.get('video_files', []) if f.get('file_type') == 'video/mp4']
    return dict(id=v['id'], w=v['width'], h=v['height'], dur=v['duration'], url=v['url'], image=v['image'],
                user=v['user']['name'], user_url=v['user']['url'], files=files,
                pics=[p['picture'] for p in v.get('video_pictures', [])])


def thumb(v):
    p = os.path.join(THUMBS, f"{v['id']}.jpg")
    if not os.path.exists(p):
        u = urllib.parse.urlsplit(v['image'])
        url = urllib.parse.urlunsplit((u.scheme, u.netloc, u.path, 'auto=compress&cs=tinysrgb&fit=crop&h=216&w=384', ''))
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        open(p, 'wb').write(r.content)
    return p


def sheet(name, vids, cols=5):
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15)
    tw, th, pad = 384, 216, 26
    rows = (len(vids) + cols - 1) // cols
    img = Image.new('RGB', (cols * tw, rows * (th + pad)), (18, 18, 22))
    d = ImageDraw.Draw(img)
    for i, v in enumerate(vids):
        x, y = (i % cols) * tw, (i // cols) * (th + pad)
        try:
            im = Image.open(thumb(v)).convert('RGB').resize((tw - 4, th - 4))
            img.paste(im, (x + 2, y + 2))
        except Exception as e:  # noqa: BLE001
            d.text((x + 10, y + 90), f'thumb failed {e}'[:40], fill=(200, 80, 80), font=font)
        d.text((x + 6, y + th + 4), f"{v['id']}  {v['dur']}s  {v['w']}x{v['h']}  {v['user'][:16]}", fill=(230, 230, 230),
               font=font)
    img.save(os.path.join(OUT, f'sheet_{name}.jpg'), quality=82)


def main(only=None):
    allres = {}
    path = os.path.join(OUT, 'results.json')
    if os.path.exists(path):
        allres = json.load(open(path))
    for name, qs in QUERIES.items():
        if only and name not in only:
            continue
        seen, vids = set(), []
        for q in qs:
            for v in search(q):
                if v['id'] in seen:
                    continue
                seen.add(v['id'])
                s = slim(v)
                s['query'] = q
                vids.append(s)
        allres[name] = vids
        with cf.ThreadPoolExecutor(12) as ex:
            list(ex.map(lambda v: thumb(v) if True else None, vids))
        sheet(name, vids[:50])
        print(f'{name:18s} {len(vids):3d} candidates', flush=True)
    json.dump(allres, open(path, 'w'), indent=1)


if __name__ == '__main__':
    main(sys.argv[1:] or None)
