"""Lay narration lines end to end (gap before each) -> audio/timeline.json + film/timeline.js"""
import json, os
H = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
tl = json.load(open(os.path.join(H, 'audio', 'vo_timeline.json')))
t = 0.0; out = {}
for l in tl:
    t += l['gap']
    out[l['id']] = {'t': round(t, 2), 'd': l['dur'], 'file': l['file'], 'text': l['text']}
    t += l['dur']
end = round(t + 4.6, 2)
json.dump({'lines': out, 'end': end}, open(os.path.join(H, 'audio', 'timeline.json'), 'w'), indent=1)
open(os.path.join(H, 'film', 'timeline.js'), 'w').write('window.VO=' + json.dumps({k: [v['t'], v['d'], v['text']] for k, v in out.items()}) + ';window.END=' + str(end) + ';\n')
for k, v in out.items(): print(k, v['t'], v['d'])
print('end', end)
