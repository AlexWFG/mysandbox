"""ElevenLabs helpers for the Mandate Market explainer: narration (with character
timestamps), music and SFX. Everything is cached on disk by a hash of its request,
so re-running never spends credits twice. The key is injected by the proxy.

python3 tools/eleven.py vo      # audio/narration.json -> audio/vo/*.mp3 + *.json (alignment)
python3 tools/eleven.py music   # audio/music.json
python3 tools/eleven.py sfx     # audio/sfx.json
python3 tools/eleven.py credits
"""
import base64, hashlib, json, os, subprocess, sys, urllib.request
import imageio_ffmpeg

API = 'https://api.elevenlabs.io/v1'
AUD = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'audio')
FF = imageio_ffmpeg.get_ffmpeg_exe()


def req(path, body, accept='audio/mpeg'):
    r = urllib.request.Request(API + path, data=json.dumps(body).encode(), headers={'Content-Type': 'application/json', 'Accept': accept})
    with urllib.request.urlopen(r, timeout=600) as rsp:
        return rsp.read()


def dur(path):
    p = subprocess.run([FF, '-i', path], capture_output=True, text=True).stderr
    h, m, s = p.split('Duration: ')[1].split(',')[0].split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)


def key_path(kind, key_obj, ext='mp3'):
    os.makedirs(os.path.join(AUD, kind), exist_ok=True)
    h = hashlib.sha1(json.dumps(key_obj, sort_keys=True).encode()).hexdigest()[:10]
    return os.path.join(AUD, kind, f"{key_obj.get('id', 'x')}_{h}.{ext}")


def words(al):
    """character alignment -> list of {w, t0, t1}"""
    out, cur = [], None
    for ch, a, b in zip(al['characters'], al['character_start_times_seconds'], al['character_end_times_seconds']):
        if ch.isspace():
            if cur: out.append(cur); cur = None
            continue
        if cur is None: cur = {'w': '', 't0': a, 't1': b}
        cur['w'] += ch; cur['t1'] = b
    if cur: out.append(cur)
    return out


def vo():
    cfg = json.load(open(os.path.join(AUD, 'narration.json')))
    lines = cfg['lines']; res = []
    for i, ln in enumerate(lines):
        body = {'text': ln['text'], 'model_id': cfg['model'], 'voice_settings': cfg['settings'],
                'previous_text': lines[i - 1]['text'] if i else None, 'next_text': lines[i + 1]['text'] if i < len(lines) - 1 else None}
        mp3 = key_path('vo', {'id': ln['id'], 'voice': cfg['voice'], **body})
        js = mp3[:-4] + '.json'
        if not os.path.exists(mp3):
            d = json.loads(req(f"/text-to-speech/{cfg['voice']}/with-timestamps?output_format=mp3_44100_192", body, 'application/json'))
            open(mp3, 'wb').write(base64.b64decode(d['audio_base64']))
            json.dump(d.get('normalized_alignment') or d['alignment'], open(js, 'w'))
            print('  generated', os.path.basename(mp3))
        al = json.load(open(js))
        w = words(al)
        res.append({'id': ln['id'], 'text': ln['text'], 'file': os.path.relpath(mp3, AUD), 'dur': round(dur(mp3), 3), 'speech_end': round(w[-1]['t1'], 3), 'words': w})
        print(f"{ln['id']} dur={res[-1]['dur']:5.2f}  {ln['text'][:70]}")
    json.dump(res, open(os.path.join(AUD, 'vo_lines.json'), 'w'), indent=0)
    print('total speech', round(sum(r['dur'] for r in res), 1), 's')


def music():
    cfg = json.load(open(os.path.join(AUD, 'music.json')))
    for cue in cfg['cues']:
        body = {k: v for k, v in cue.items() if k in ('prompt', 'music_length_ms', 'composition_plan', 'force_instrumental', 'model_id')}
        out = key_path('music', {'id': cue['id'], **body})
        if not os.path.exists(out):
            open(out, 'wb').write(req('/music?output_format=mp3_44100_192', body)); print('  generated', os.path.basename(out))
        print(cue['id'], os.path.basename(out), round(dur(out), 2), 's')


def sfx():
    cfg = json.load(open(os.path.join(AUD, 'sfx.json')))
    for fx in cfg['fx']:
        body = {'text': fx['text'], 'duration_seconds': fx['dur'], 'prompt_influence': fx.get('influence', 0.5)}
        out = key_path('sfx', {'id': fx['id'], **body})
        if not os.path.exists(out):
            open(out, 'wb').write(req('/sound-generation?output_format=mp3_44100_192', body)); print('  generated', os.path.basename(out))
        print(fx['id'], os.path.basename(out), round(dur(out), 2), 's')


def credits():
    with urllib.request.urlopen(API + '/user/subscription', timeout=30) as r:
        s = json.loads(r.read()); print(f"account credits used {s['character_count']}/{s['character_limit']}")


if __name__ == '__main__':
    {'vo': vo, 'music': music, 'sfx': sfx, 'credits': credits}[sys.argv[1]]()
    if sys.argv[1] != 'credits':
        try: credits()
        except Exception as e: print('subscription check failed', e)
