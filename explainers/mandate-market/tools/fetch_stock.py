"""Download picked Pexels clips (CDN only, no API calls) and extract 30fps frame sequences.

python3 film/tools/fetch_stock.py
Writes film/stock/clips/<id>/f_0000.jpg ... and film/stock/manifest.json (with credits).
"""
import json, os, subprocess, urllib.request
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stock')
picks = json.load(open(os.path.join(ROOT, 'picks.json')))
man_path = os.path.join(ROOT, 'manifest.json')
manifest = json.load(open(man_path)) if os.path.exists(man_path) else {}
os.makedirs(os.path.join(ROOT, 'raw'), exist_ok=True)

for cid, p in picks.items():
    v = json.load(open(os.path.join(ROOT, 'search', p['slot'] + '.json')))['videos'][p['i']]
    files = sorted([f for f in v['video_files'] if f['file_type'] == 'video/mp4' and f['width'] and f['width'] >= 1920],
                   key=lambda f: f['width'])
    f = files[0] if files else max(v['video_files'], key=lambda f: f['width'] or 0)
    raw = os.path.join(ROOT, 'raw', f"{v['id']}.mp4")
    if not os.path.exists(raw):
        subprocess.run(['curl', '-sSL', '--fail', '-A', 'Mozilla/5.0', '-o', raw + '.part', f['link']], check=True)
        os.rename(raw + '.part', raw)
    out = os.path.join(ROOT, 'clips', cid)
    key = f"{v['id']}:{p['from']}:{p['dur']}"
    if manifest.get(cid, {}).get('key') != key:
        os.makedirs(out, exist_ok=True)
        for x in os.listdir(out):
            os.remove(os.path.join(out, x))
        dur = min(p['dur'], max(1.0, v['duration'] - p['from'] - 0.2))
        subprocess.run([FF, '-y', '-loglevel', 'error', '-ss', str(p['from']), '-t', str(dur), '-i', raw,
                        '-vf', 'fps=30,scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080',
                        '-q:v', '3', os.path.join(out, 'f_%04d.jpg')], check=True)
    n = len([x for x in os.listdir(out) if x.endswith('.jpg')])
    manifest[cid] = {'key': key, 'frames': n, 'fps': 30, 'pexels_id': v['id'], 'author': v['user']['name'], 'url': v['url']}
    print(f"{cid:12s} {n:4d} frames  {f['width']}p  by {v['user']['name']}")
json.dump(manifest, open(man_path, 'w'), indent=1)
