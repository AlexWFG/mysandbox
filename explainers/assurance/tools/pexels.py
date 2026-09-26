"""Pexels: one search call per slot (cached), contact sheets, then CDN download + frame extraction.

python3 tools/pexels.py search            # slots in stock/slots.json without a cached search
python3 tools/pexels.py fetch             # download stock/picks.json, extract 30 fps frames, write manifest
"""
import io, json, os, subprocess, sys, urllib.parse, urllib.request
from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stock')
SE = os.path.join(ROOT, 'search'); os.makedirs(SE, exist_ok=True)
CALLS = os.path.join(ROOT, 'api_calls.json')


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read(), dict(r.headers)


def search():
    slots = json.load(open(os.path.join(ROOT, 'slots.json')))
    calls = json.load(open(CALLS)) if os.path.exists(CALLS) else []
    for s, q in slots.items():
        p = os.path.join(SE, s + '.json')
        if not os.path.exists(p):
            body, hdr = get('https://api.pexels.com/videos/search?' + urllib.parse.urlencode({'query': q, 'per_page': 12, 'orientation': 'landscape', 'size': 'medium'}))
            open(p, 'wb').write(body); calls.append({'slot': s, 'query': q})
            json.dump(calls, open(CALLS, 'w'), indent=1)
        vids = json.load(open(p))['videos'][:12]
        W, H = 400, 225; im = Image.new('RGB', (4 * W, 3 * H), (12, 12, 12)); d = ImageDraw.Draw(im)
        for i, v in enumerate(vids):
            try:
                b, _ = get(v['image']); t = Image.open(io.BytesIO(b)).convert('RGB')
                t = t.resize((W, int(W * t.height / t.width))); im.paste(t.crop((0, 0, W, H)), ((i % 4) * W, (i // 4) * H))
            except Exception as e: print('thumb', e)
            d.rectangle([(i % 4) * W, (i // 4) * H, (i % 4) * W + 170, (i // 4) * H + 22], fill=(0, 0, 0))
            d.text(((i % 4) * W + 4, (i // 4) * H + 4), f"{i} {v['duration']}s {v['width']}", fill=(255, 190, 6))
        im.save(os.path.join(SE, s + '.jpg'), quality=80); print(s, len(vids), 'results')
    print('Pexels API calls so far:', len(calls))


def fetch():
    picks = json.load(open(os.path.join(ROOT, 'picks.json')))
    mp = os.path.join(ROOT, 'manifest.json'); man = json.load(open(mp)) if os.path.exists(mp) else {}
    os.makedirs(os.path.join(ROOT, 'raw'), exist_ok=True)
    for cid, p in picks.items():
        v = json.load(open(os.path.join(SE, p['slot'] + '.json')))['videos'][p['i']]
        fs = sorted([f for f in v['video_files'] if f['file_type'] == 'video/mp4' and (f['width'] or 0) >= 1920], key=lambda f: f['width'])
        f = fs[0] if fs else max(v['video_files'], key=lambda f: f['width'] or 0)
        raw = os.path.join(ROOT, 'raw', f"{v['id']}.mp4")
        if not os.path.exists(raw):
            subprocess.run(['curl', '-sSL', '--fail', '-A', 'Mozilla/5.0', '-o', raw, f['link']], check=True)
        out = os.path.join(ROOT, 'clips', cid); key = f"{v['id']}:{p['from']}:{p['dur']}"
        if man.get(cid, {}).get('key') != key or not os.path.isdir(out):
            os.makedirs(out, exist_ok=True)
            for x in os.listdir(out): os.remove(os.path.join(out, x))
            subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(p['from']), '-t', str(p['dur']), '-i', raw,
                            '-vf', 'fps=30,scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080', '-q:v', '3',
                            os.path.join(out, 'f_%04d.jpg')], check=True)
        n = len(os.listdir(out))
        man[cid] = {'key': key, 'frames': n, 'pexels_id': v['id'], 'author': v['user']['name'], 'url': v['url']}
        print(cid, n, 'frames', f['width'], v['user']['name'])
    json.dump(man, open(mp, 'w'), indent=1)


if __name__ == '__main__':
    {'search': search, 'fetch': fetch}[sys.argv[1]]()
