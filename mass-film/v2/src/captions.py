"""SubRip captions from the narration timeline (re-run after the final take)."""
import os
import sys
import textwrap

from timeline2 import Timeline

V2 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ts(t):
    ms = int(round(t * 1000))
    return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}'


def write(source='scratch', path=None):
    tl = Timeline(source)
    path = path or os.path.join(V2, 'out', f'mass_v2_captions_{source}.srt')
    cues = []
    for ln in tl.lines:
        text = ln.text
        lines = textwrap.wrap(text, 42)
        if len(lines) <= 2:
            cues.append((ln.start, ln.end + 0.25, '\n'.join(lines)))
            continue
        # split long lines at a sentence break near the middle, timed by word position
        sents = [s.strip() + '.' for s in text.replace('?', '?.').split('.') if s.strip()]
        sents = [s[:-1] if s.endswith('?.') else s for s in sents]
        half = len(text) / 2
        acc, a = 0, []
        for s_ in sents:
            if acc and acc + len(s_) / 2 > half:
                break
            a.append(s_)
            acc += len(s_) + 1
        first, second = ' '.join(a), text[len(' '.join(a)):].strip()
        t_mid = ln.word(second.split()[0].strip('.,:;!?'))
        cues.append((ln.start, t_mid - 0.05, '\n'.join(textwrap.wrap(first, 42))))
        cues.append((t_mid, ln.end + 0.25, '\n'.join(textwrap.wrap(second, 42))))
    cues = [(a, min(b, cues[k + 1][0] - 0.04) if k + 1 < len(cues) else b, txt) for k, (a, b, txt) in enumerate(cues)]
    with open(path, 'w') as f:
        for k, (a, b, txt) in enumerate(cues, 1):
            f.write(f'{k}\n{ts(a)} --> {ts(b)}\n{txt}\n\n')
    print('wrote', path, len(cues), 'cues')


if __name__ == '__main__':
    write(sys.argv[1] if len(sys.argv) > 1 else os.environ.get('MASS_VO', 'scratch'))
