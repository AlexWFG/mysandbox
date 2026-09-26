"""Measure speech onset/offset in each VO clip (leading/trailing silence) -> audio/vo_durations.json gets 'in'/'out'."""
import json, os, subprocess
import numpy as np
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); AUD = os.path.join(HERE, 'audio')
SR = 16000
p = os.path.join(AUD, 'vo_durations.json'); V = json.load(open(p))
for v in V:
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(AUD, v['file']), '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
    x = np.abs(np.frombuffer(raw, np.float32)); w = int(SR * .01)
    e = np.sqrt(np.convolve(x ** 2, np.ones(w) / w, 'same')); thr = e.max() * 10 ** (-38 / 20)
    idx = np.where(e > thr)[0]
    sp = e > thr; segs = []; i = 0; n = len(sp); gap = int(SR * .16)
    while i < n:
        if sp[i]:
            j = i
            while True:
                k = j
                while k < n and sp[k]: k += 1
                g = k
                while g < n and not sp[g]: g += 1
                if g < n and g - k < gap: j = g; continue
                break
            if (k - i) / SR > .06: segs.append([round(i / SR, 3), round(k / SR, 3)])
            i = k
        else: i += 1
    v['segs'] = segs
    v['in'] = round(max(0, idx[0] / SR - .04), 3); v['out'] = round(min(len(x) / SR, idx[-1] / SR + .12), 3)
    import re; ph = [x for x in re.split(r'[,.:?!;]\s', v['text']) if x.strip()]
    print(v['id'], v['dur'], '->', round(v['out'] - v['in'], 2), 'segs', len(segs), 'phrases', len(ph))
json.dump(V, open(p, 'w'), indent=1)
print('trimmed total', round(sum(v['out'] - v['in'] for v in V), 1))
