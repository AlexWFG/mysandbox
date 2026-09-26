"""Builds audio/timeline.json: which narration lines are used, when they start (film seconds),
and word timings, after the pitch-preserving tempo factor applied in the mix."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__)); AUD = os.path.join(HERE, '..', 'audio')
TEMPO = 1.075
DROP = {'v18', 'v22'}
START = 1.4                      # first line under the title
PRE = {  # silence before each line (seconds); default 0.3
    'v02': 1.0, 'v06': 1.2, 'v12': 1.3, 'v13': 0.6, 'v14': 0.5, 'v17': 1.2, 'v19': 0.9, 'v23': 1.2,
    'v29': 0.8, 'v30': 1.2, 'v31': 0.7, 'v32': 0.7, 'v33': 1.1, 'v11': 0.6, 'v10': 0.8, 'v24': 0.5, 'v04': 0.5,
}
TAIL = 4.2                        # end card after the last line
L = [l for l in json.load(open(os.path.join(AUD, 'vo_lines.json'))) if l['id'] not in DROP]
t = START; out = []
for i, l in enumerate(L):
    if i: t += PRE.get(l['id'], 0.3)
    d = l['speech_end'] / TEMPO
    out.append({'id': l['id'], 't': round(t, 3), 'dur': round(d, 3), 'file': l['file'], 'text': l['text'],
                'words': [[w, round(t + a / TEMPO, 3), round(t + b / TEMPO, 3)] for w, a, b in l['words']]})
    t += d
total = round(t + TAIL, 2)
json.dump({'tempo': TEMPO, 'total': total, 'lines': out}, open(os.path.join(AUD, 'timeline.json'), 'w'), indent=0)
for o in out: print(o['id'], o['t'], round(o['t'] + o['dur'], 2))
print('total', total, '=', int(total // 60), 'min', round(total % 60, 1))
