"""ElevenLabs helpers: narration lines, music cues and sound effects, all cached.

The API key is injected by the environment's proxy, so none is passed here.
Every request is cached on disk by a hash of its parameters, so re-running never
spends credits twice. The account is shared, so keep calls deliberate.

python3 film/tools/eleven.py vo              # narration (film/audio/narration.json)
python3 film/tools/eleven.py music           # music cues (film/audio/music.json)
python3 film/tools/eleven.py sfx             # sound effects (film/audio/sfx.json)
"""
import hashlib, json, os, subprocess, sys, urllib.request
import imageio_ffmpeg

API = 'https://api.elevenlabs.io/v1'
AUD = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'audio')
FF = imageio_ffmpeg.get_ffmpeg_exe()


def post(path, body, out):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode(), headers={'Content-Type': 'application/json', 'Accept': 'audio/mpeg'})
    with urllib.request.urlopen(req, timeout=600) as r:
        data = r.read()
    open(out, 'wb').write(data)


def dur(path):
    p = subprocess.run([FF, '-i', path], capture_output=True, text=True).stderr
    h, m, s = p.split('Duration: ')[1].split(',')[0].split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)


def cached(kind, key_obj, fetch):
    os.makedirs(os.path.join(AUD, kind), exist_ok=True)
    h = hashlib.sha1(json.dumps(key_obj, sort_keys=True).encode()).hexdigest()[:10]
    out = os.path.join(AUD, kind, f"{key_obj.get('id', 'x')}_{h}.mp3")
    if not os.path.exists(out):
        fetch(out)
        print('  generated', os.path.basename(out))
    return out


def vo():
    cfg = json.load(open(os.path.join(AUD, 'narration.json')))
    lines = cfg['lines']; res = []
    for i, ln in enumerate(lines):
        body = {'text': ln['text'], 'model_id': cfg['model'], 'voice_settings': cfg['settings'],
                'previous_text': lines[i - 1]['text'] if i else None, 'next_text': lines[i + 1]['text'] if i < len(lines) - 1 else None}
        key = {'id': ln['id'], 'voice': cfg['voice'], **body}
        out = os.path.join(AUD, ln['pin']) if ln.get('pin') else cached('vo', key, lambda o: post(f"/text-to-speech/{cfg['voice']}?output_format=mp3_44100_192", body, o))
        d = dur(out); res.append({**ln, 'file': os.path.relpath(out, AUD), 'dur': round(d, 2)})
        flag = '  OVER by %.2fs' % (d - ln['slot']) if d > ln['slot'] + 0.05 else ''
        print(f"{ln['id']} t={ln['t']:6.2f} dur={d:5.2f} slot={ln['slot']:4.1f}{flag}  {ln['text'][:60]}")
    json.dump(res, open(os.path.join(AUD, 'vo_timeline.json'), 'w'), indent=1)


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
    {'vo': vo, 'music': music, 'sfx': sfx}[sys.argv[1]]()
    try:
        with urllib.request.urlopen(API + '/user/subscription', timeout=30) as r:
            s = json.loads(r.read()); print(f"credits used {s['character_count']}/{s['character_limit']}")
    except Exception as e:
        print('subscription check failed', e)
