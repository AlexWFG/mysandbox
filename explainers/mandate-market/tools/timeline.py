"""Lay the narration out on the film clock -> timeline.json (read by film.js and mix.py).

Voice is played at TEMPO (a light atempo in the mix); word times are scaled to match.
Gaps: short inside a chapter, longer at chapter breaks and before stock inserts.
"""
import json, os

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
TEMPO = 1.05
START = 5.4            # first line after the title card
DROP = {'18', '25'}   # generated but cut for length (README)
GAP = 0.75
BREAK = {'04': 1.5, '07': 1.6, '13': 1.8, '15': 1.4, '19': 1.5, '20': 1.4, '24': 1.6, '26': 1.8, '27': 1.1,
         '02': 1.0, '03': 0.9, '08': 1.0, '10': 0.9, '11': 0.9, '12': 0.9, '14': 0.9, '16': 0.9, '17': 0.9, '21': 1.3, '22': 1.3, '23': 1.4, '25': 1.0}
TAIL = 6.5             # end card after the last line

lines = [l for l in json.load(open(os.path.join(HERE, 'audio', 'vo_lines.json'))) if l['id'] not in DROP]
t = START; out = []
for i, l in enumerate(lines):
    if i: t += BREAK.get(l['id'], GAP)
    words = [{'w': w['w'], 't': round(t + w['t0'] / TEMPO, 3), 'e': round(t + w['t1'] / TEMPO, 3)} for w in l['words']]
    out.append({'id': l['id'], 't': round(t, 3), 'end': round(t + l['speech_end'] / TEMPO, 3), 'file': l['file'], 'text': l['text'], 'words': words})
    t = t + l['speech_end'] / TEMPO
total = round(t + TAIL, 2)
json.dump({'tempo': TEMPO, 'duration': total, 'lines': out}, open(os.path.join(HERE, 'timeline.json'), 'w'), indent=0)
for l in out: print(f"{l['id']} {l['t']:7.2f} -> {l['end']:7.2f}  {l['text'][:60]}")
print('duration', total, f'({int(total // 60)}:{total % 60:04.1f})')
