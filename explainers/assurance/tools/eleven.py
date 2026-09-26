"""ElevenLabs narration / music / SFX for the assurance explainer, cached on disk.

Adapted from propchain-reel/film/tools/eleven.py. The API key is injected by the proxy.
Every request is cached by a hash of its parameters, so re-running never spends credits twice.

python3 tools/eleven.py vo | music | sfx | credits
"""
import hashlib, json, os, subprocess, sys, urllib.request

API = 'https://api.elevenlabs.io/v1'
AUD = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'audio')
LOG = os.path.join(AUD, 'spend.json')


def post(path, body, out):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode(), headers={'Content-Type': 'application/json', 'Accept': 'audio/mpeg'})
    with urllib.request.urlopen(req, timeout=900) as r:
        open(out, 'wb').write(r.read())


def dur(path):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path], capture_output=True, text=True).stdout)


def credits():
  try:
    with urllib.request.urlopen(API + '/user/subscription', timeout=30) as r:
        s = json.loads(r.read())
    return s['character_count']
  except Exception as e:
    return f'unavailable ({e})'


def cached(kind, key_obj, fetch):
    os.makedirs(os.path.join(AUD, kind), exist_ok=True)
    h = hashlib.sha1(json.dumps(key_obj, sort_keys=True).encode()).hexdigest()[:10]
    out = os.path.join(AUD, kind, f"{key_obj.get('id', 'x')}_{h}.mp3")
    if not os.path.exists(out):
        fetch(out)
        log = json.load(open(LOG)) if os.path.exists(LOG) else []
        log.append({'kind': kind, 'file': os.path.basename(out), 'chars': len(key_obj.get('text', ''))})
        json.dump(log, open(LOG, 'w'), indent=1)
        print('  generated', os.path.basename(out))
    return out


def vo():
    cfg = json.load(open(os.path.join(AUD, 'narration.json')))
    lines = cfg['lines']; res = []
    for i, ln in enumerate(lines):
        body = {'text': ln['text'], 'model_id': cfg['model'], 'voice_settings': cfg['settings'],
                'previous_text': ln.get('prev', lines[i - 1]['text'] if i else None), 'next_text': ln.get('next', lines[i + 1]['text'] if i < len(lines) - 1 else None)}
        key = {'id': ln['id'], 'voice': cfg['voice'], **body}
        out = cached('vo', key, lambda o: post(f"/text-to-speech/{cfg['voice']}?output_format=mp3_44100_192", body, o))
        d = dur(out); res.append({'id': ln['id'], 'text': ln['text'], 'file': os.path.relpath(out, AUD), 'dur': round(d, 3)})
        print(f"{ln['id']:5s} {d:5.2f}s  {ln['text'][:70]}")
    json.dump(res, open(os.path.join(AUD, 'vo_durations.json'), 'w'), indent=1)
    print('total VO', round(sum(r['dur'] for r in res), 1), 's')


def music():
    cfg = json.load(open(os.path.join(AUD, 'music.json')))
    for cue in cfg['cues']:
        body = {k: v for k, v in cue.items() if k in ('prompt', 'music_length_ms', 'composition_plan', 'force_instrumental', 'model_id')}
        out = cached('music', {'id': cue['id'], **body}, lambda o: post('/music?output_format=mp3_44100_192', body, o))
        print(cue['id'], os.path.basename(out), round(dur(out), 2), 's')


def sfx():
    cfg = json.load(open(os.path.join(AUD, 'sfx.json')))
    for fx in cfg['fx']:
        body = {'text': fx['text'], 'duration_seconds': fx['dur'], 'prompt_influence': fx.get('influence', 0.5)}
        out = cached('sfx', {'id': fx['id'], **body}, lambda o: post('/sound-generation?output_format=mp3_44100_192', body, o))
        print(fx['id'], os.path.basename(out), round(dur(out), 2), 's')


if __name__ == '__main__':
    if sys.argv[1] != 'credits':
        {'vo': vo, 'music': music, 'sfx': sfx}[sys.argv[1]]()
    print('account credits used', credits())
