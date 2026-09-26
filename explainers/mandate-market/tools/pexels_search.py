"""Search Pexels once per shot slot and build a contact sheet of candidates.

The API key is injected by the environment's proxy, so no key is needed here.
Each slot costs exactly ONE API call (budget-conscious: the account is shared).
Results cache to film/stock/search/<slot>.json and are never re-fetched.

python3 film/tools/pexels_search.py            # all slots without a cache
python3 film/tools/pexels_search.py slot1 ...  # specific slots
"""
import json, sys, os, io, urllib.request, urllib.parse
from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(__file__), '..')
SLOTS = json.load(open(os.path.join(ROOT, 'stock', 'slots.json')))
OUT = os.path.join(ROOT, 'stock', 'search')
os.makedirs(OUT, exist_ok=True)


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'propchain-reel/1.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read(), dict(r.headers)


def search(slot):
    q = SLOTS[slot]['query']
    url = 'https://api.pexels.com/videos/search?' + urllib.parse.urlencode({'query': q, 'per_page': 12, 'orientation': 'landscape', 'size': 'medium'})
    body, hdr = get(url)
    data = json.loads(body)
    json.dump(data, open(os.path.join(OUT, slot + '.json'), 'w'))
    print(f"{slot}: '{q}' -> {len(data.get('videos', []))} results  (remaining {hdr.get('X-Ratelimit-Remaining')})")
    return data


def sheet(slot, data):
    vids = data.get('videos', [])[:12]
    W, H = 400, 225
    im = Image.new('RGB', (4 * W, 3 * H), (12, 12, 12))
    d = ImageDraw.Draw(im)
    for i, v in enumerate(vids):
        try:
            pic = v['video_pictures'][min(4, len(v['video_pictures']) - 1)]['picture']
            b, _ = get(pic)
            t = Image.open(io.BytesIO(b)).convert('RGB')
            t = t.resize((W, int(W * t.height / t.width)))
            im.paste(t.crop((0, 0, W, H)), ((i % 4) * W, (i // 4) * H))
        except Exception as e:
            print('thumb fail', e)
        d.rectangle([(i % 4) * W, (i // 4) * H, (i % 4) * W + 150, (i // 4) * H + 22], fill=(0, 0, 0))
        d.text(((i % 4) * W + 4, (i // 4) * H + 4), f"{i} {v['duration']}s {v['width']}p", fill=(255, 190, 6))
    im.save(os.path.join(OUT, slot + '.jpg'), quality=80)


if __name__ == '__main__':
    todo = sys.argv[1:] or [s for s in SLOTS if not os.path.exists(os.path.join(OUT, s + '.json'))]
    for s in todo:
        p = os.path.join(OUT, s + '.json')
        data = json.load(open(p)) if os.path.exists(p) else search(s)
        sheet(s, data)
