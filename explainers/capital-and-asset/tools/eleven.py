"""ElevenLabs narration (with character timestamps), music and SFX — all cached on disk.

Keys are injected by the environment proxy. Every request is cached by a hash of its
parameters, so re-running never spends credits twice. Costs are logged to audio/credits.log.

python3 tools/eleven.py vo | music | sfx
"""
import base64, hashlib, json, os, subprocess, sys, time, urllib.request
import imageio_ffmpeg

API = 'https://api.elevenlabs.io/v1'
HERE = os.path.dirname(os.path.abspath(__file__))
AUD = os.path.join(HERE, '..', 'audio')
FF = imageio_ffmpeg.get_ffmpeg_exe()


def post(path, body, accept='audio/mpeg'):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode(), headers={'Content-Type': 'application/json', 'Accept': accept})
    with urllib.request.urlopen(req, timeout=900) as r:
        data = r.read(); hdr = dict(r.headers)
    cost = hdr.get('character-cost') or hdr.get('x-character-count') or '?'
    with open(os.path.join(AUD, 'credits.log'), 'a') as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}\t{path.split('?')[0]}\tcost={cost}\n")
    return data


def dur(path):
    p = subprocess.run([FF, '-i', path], capture_output=True, text=True).stderr
    h, m, s = p.split('Duration: ')[1].split(',')[0].split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)


def key(kind, obj):
    return os.path.join(AUD, kind, f"{obj.get('id', 'x')}_{hashlib.sha1(json.dumps(obj, sort_keys=True).encode()).hexdigest()[:10]}")


def vo():
    cfg = json.load(open(os.path.join(AUD, 'narration.json')))
    os.makedirs(os.path.join(AUD, 'vo'), exist_ok=True)
    lines = cfg['lines']; res = []
    for i, ln in enumerate(lines):
        body = {'text': ln['text'], 'model_id': cfg['model'], 'voice_settings': cfg['settings'],
                'previous_text': lines[i - 1]['text'] if i else None, 'next_text': lines[i + 1]['text'] if i < len(lines) - 1 else None}
        base = key('vo', {'id': ln['id'], 'voice': cfg['voice'], **body})
        if not os.path.exists(base + '.mp3'):
            data = json.loads(post(f"/text-to-speech/{cfg['voice']}/with-timestamps?output_format=mp3_44100_192", body, 'application/json'))
            open(base + '.mp3', 'wb').write(base64.b64decode(data['audio_base64']))
            json.dump(data['alignment'], open(base + '.json', 'w'))
            print('  generated', os.path.basename(base))
        al = json.load(open(base + '.json'))
        # words with start/end times
        words, cur, st = [], '', None
        for ch, s, e in zip(al['characters'], al['character_start_times_seconds'], al['character_end_times_seconds']):
            if ch.isspace():
                if cur: words.append([cur, st, pe]); cur = ''
                continue
            if not cur: st = s
            cur += ch; pe = e
        if cur: words.append([cur, st, pe])
        d = dur(base + '.mp3')
        res.append({'id': ln['id'], 'text': ln['text'], 'file': os.path.relpath(base + '.mp3', AUD), 'dur': round(d, 3), 'speech_end': round(words[-1][2], 3), 'words': words})
        print(f"{ln['id']} {d:5.2f}s  {ln['text'][:70]}")
    json.dump(res, open(os.path.join(AUD, 'vo_lines.json'), 'w'), indent=0)
    print('total speech', round(sum(r['dur'] for r in res), 1))


def music():
    cfg = json.load(open(os.path.join(AUD, 'music.json')))
    os.makedirs(os.path.join(AUD, 'music'), exist_ok=True)
    for cue in cfg['cues']:
        body = {k: v for k, v in cue.items() if k in ('prompt', 'music_length_ms', 'composition_plan', 'force_instrumental', 'model_id')}
        out = key('music', {'id': cue['id'], **body}) + '.mp3'
        if not os.path.exists(out):
            data = post('/music/stream?output_format=mp3_44100_192', body); open(out, 'wb').write(data); print('  generated', out)
        print(cue['id'], round(dur(out), 2), 's')


def sfx():
    cfg = json.load(open(os.path.join(AUD, 'sfx.json')))
    os.makedirs(os.path.join(AUD, 'sfx'), exist_ok=True)
    for fx in cfg['fx']:
        body = {'text': fx['text'], 'duration_seconds': fx['dur'], 'prompt_influence': fx.get('influence', 0.5)}
        out = key('sfx', {'id': fx['id'], **body}) + '.mp3'
        if not os.path.exists(out):
            data = post('/sound-generation?output_format=mp3_44100_192', body); open(out, 'wb').write(data); print('  generated', out)
        print(fx['id'], round(dur(out), 2), 's')


if __name__ == '__main__':
    {'vo': vo, 'music': music, 'sfx': sfx}[sys.argv[1]]()
