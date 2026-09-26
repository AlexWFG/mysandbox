"""Lay the measured narration on the film timeline -> timeline.json (read by film.js and mix.py).

Picture is timed to the voice: each line starts after the previous one ends plus a gap.
Lines not listed in ORDER were generated but cut for length (kept in the cache).
"""
import json, os
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
dur = {l['id']: l for l in json.load(open(os.path.join(HERE, 'audio', 'vo_durations.json')))}

TITLE = 4.2          # title card before the first line
GAP = 0.5           # default breath between lines
XS = 0.62          # scale on the per-line pauses (tuned so the film lands under 4:00)
# (chapter, [(line, extra pause AFTER the line)])
ORDER = [
    ('THE PROBLEM', [('n01a', .1), ('n01b', .4), ('n02', .5), ('n03', 1.0)]),
    ('SIX LAYERS', [('n05', .6), ('n06', 1.0)]),
    ('CORROBORATION', [('n07', .3), ('n08', .6), ('n09', .4), ('n10', .8), ('n11', 1.0)]),
    ('THE BOND', [('n12', .5), ('n13', .4), ('n14', .9), ('n15', .5), ('n16', .9), ('n17', 1.2)]),
    ('WHAT CAN BE SLASHED', [('n18a', .2), ('n18b', .3), ('n18c', .3), ('n18d', 1.0)]),
    ('WHO POSTS CAPITAL', [('n20', .5), ('n21', .7), ('n22', .6), ('n23', 1.0)]),
    ('THE INSURER', [('n24b', .8), ('n25', .6), ('n26', 1.0)]),
    ('THE PLAN', [('n27a', .3), ('n27b', 1.6)]),
]
END = 4.8            # end card
CH_PRE = 0.7         # extra lead-in when a chapter starts

t = TITLE; lines = {}; chapters = []
for ci, (name, ls) in enumerate(ORDER):
    if ci: t += CH_PRE
    chapters.append({'n': ci + 1, 'name': name, 't': round(t - (0.6 if ci else 0.4), 3)})
    for lid, extra in ls:
        v = dur[lid]; d = round(v['out'] - v['in'], 3)   # speech only; clip is placed at t - in
        lines[lid] = {'t': round(t, 3), 'dur': d, 'clip_in': v['in'], 'segs': [[round(a - v['in'], 3), round(b - v['in'], 3)] for a, b in v.get('segs', [])], 'file': v['file'], 'text': v['text']}
        t += d + GAP + extra * XS
end = round(t, 3)
total = round(end + END, 2)
json.dump({'title': TITLE, 'lines': lines, 'chapters': chapters, 'end': end, 'total': total}, open(os.path.join(HERE, 'timeline.json'), 'w'), indent=1)
for c in chapters: print(f"{c['t']:7.2f}  {c['n']:02d} {c['name']}")
print('end card', end, 'total', total, f"({int(total // 60)}:{total % 60:04.1f})")
