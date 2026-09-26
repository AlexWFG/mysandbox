"""Scratch narration (offline piper voice) for timing the edit before the final take.
Writes out/scratch_vo/NN_section_i.wav and durations.json."""
import json
import os
import wave

from piper import PiperVoice, SynthesisConfig

import script

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), 'out', 'scratch_vo')
MODEL = '/tmp/claude-0/-home-user-mysandbox/1b21b23b-0ece-5e0e-b532-58456d6ab310/scratchpad/piper/en_GB-alan-medium.onnx'

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith('.wav'):
            os.remove(os.path.join(OUT, f))
    voice = PiperVoice.load(MODEL)
    cfg = SynthesisConfig(length_scale=1.0, noise_scale=0.6, noise_w_scale=0.7)
    durs = []
    for n, ((sec, i), txt) in enumerate(script.keyed()):
        path = os.path.join(OUT, f'{n:02d}_{sec}_{i}.wav')
        with wave.open(path, 'wb') as wf:
            voice.synthesize_wav(txt, wf, syn_config=cfg)
        with wave.open(path) as wf:
            durs.append(round(wf.getnframes() / wf.getframerate(), 3))
    json.dump(durs, open(os.path.join(OUT, 'durations.json'), 'w'))
    print(len(durs), 'lines', round(sum(durs), 2), 's of speech')
