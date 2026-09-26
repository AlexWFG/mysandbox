"""Edit timing derived from the narration. Every picture cue is expressed relative to a VO
line (or a word inside it), so swapping the scratch voice for the final take re-times the
whole film automatically.

Word timing: the final take carries character-level alignment from the TTS service; the
scratch take falls back to a character-proportional estimate."""
import json
import os

import script

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), 'out')
FPS = 24


class Line:
    def __init__(self, key, text, start, dur, words=None):
        self.key, self.text, self.start, self.dur = key, text, start, dur
        self.end = start + dur
        self.words = words or self._estimate_words()

    def _estimate_words(self):
        """[(word, t0, t1)] spread by character count (scratch fallback)."""
        toks = self.text.split(' ')
        n = sum(len(w) + 1 for w in toks)
        out, acc = [], 0
        for w in toks:
            t0 = self.start + self.dur * acc / n
            acc += len(w) + 1
            out.append((w, t0, self.start + self.dur * acc / n))
        return out

    def word(self, needle, occurrence=0, edge='start'):
        """Time of the n-th word whose letters start with needle (case-insensitive)."""
        k = 0
        for w, t0, t1 in self.words:
            if w.strip('.,:;!?—"').lower().startswith(needle.lower()):
                if k == occurrence:
                    return t0 if edge == 'start' else t1
                k += 1
        raise KeyError(f'{needle!r} not in {self.text!r}')


class Timeline:
    def __init__(self, source='scratch'):
        self.source = source
        keyed = script.keyed()
        if source == 'final':
            info = json.load(open(os.path.join(OUT, 'vo_final', 'lines.json')))
            durs = [d['dur'] for d in info]
            words = [d.get('words') for d in info]
        else:
            durs = json.load(open(os.path.join(OUT, 'scratch_vo', 'durations.json')))
            words = [None] * len(durs)
            info = [{}] * len(durs)
        t = script.LEAD_IN
        self.lines = []
        for (key, text), d, wd in zip(keyed, durs, words):
            # final take: word times in lines.json are relative to the start of each line's file
            ln = Line(key, text, t, d, [(w, t + a, t + b) for w, a, b in wd] if wd else None)
            self.lines.append(ln)
            t = ln.end + script.PAUSE_AFTER.get(key, 0.5) + (info[len(self.lines) - 1].get('pause_adj', 0.0) if source == 'final' else 0.0)
        self.duration = t
        self.by_key = {ln.key: ln for ln in self.lines}

    def __getitem__(self, key):
        return self.by_key[key]

    def section(self, name):
        ls = [ln for ln in self.lines if ln.key[0] == name]
        return ls[0].start, ls[-1].end

    def summary(self):
        rows = []
        for ln in self.lines:
            rows.append(f'{ln.start:6.2f}–{ln.end:6.2f}  {ln.key[0]:8s} {ln.text}')
        rows.append(f'total {self.duration:.2f}s')
        return '\n'.join(rows)


if __name__ == '__main__':
    print(Timeline('scratch').summary())
