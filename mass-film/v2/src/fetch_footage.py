"""Download the chosen Pexels renditions (1440p when offered) and write footage/manifest.json."""
import json
import os
import sys
import time

import requests

os.environ.setdefault('REQUESTS_CA_BUNDLE', '/root/.ccr/ca-bundle.crt')
sys.argv = sys.argv[:1]
import pexels_preview as PP  # noqa: E402

V2 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOOT = os.path.join(V2, 'footage')

# plate -> (pexels id, start s, end s, playback speed)
PICKS = {
    'handshake': (8069057, 0.3, 7.0, 0.8), 'welder': (32243438, 0.8, 7.0, 0.5), 'cranes': (13378859, 10.0, 22.0, 1.0),
    'pen_sign': (7578633, 0.0, 6.0, 0.7),
    'karachi_night': (11016391, 4.0, 14.0, 1.0), 'aisha_night': (7983117, 0.0, 12.0, 1.0),
    'forms': (7983125, 1.0, 14.0, 1.0), 'aisha_tired': (7983322, 0.0, 12.0, 1.0),
    'passport_control': (36679174, 0.0, 8.0, 0.6), 'abudhabi_morning': (11336420, 1.0, 16.0, 1.0),
    'omar_desk': (10341378, 28.0, 45.0, 1.0), 'omar_day': (10341378, 44.0, 64.0, 1.0),
    'officers_papers': (10347444, 5.0, 25.0, 1.0), 'ministry_building': (11336050, 0.0, 15.0, 1.0),
    'ministry_room': (38779095, 0.0, 10.0, 1.0), 'abudhabi_sunset': (11258028, 2.0, 7.0, 0.6),
    'aisha_day': (8503286, 0.0, 12.0, 1.0), 'aisha_coffee': (8503285, 3.0, 13.0, 1.0),
    'ministry_office': (38779108, 0.0, 14.0, 1.0), 'flag': (15546303, 2.0, 22.0, 1.0),
    'card_tap': (8421360, 1.5, 8.0, 1.0), 'ship': (3840442, 4.0, 30.0, 1.0),
}


def pick_file(v):
    fs = [f for f in v['files'] if f['w'] and f['h']]
    q = [f for f in fs if f['h'] == 1440]
    if q:
        return q[0]
    return max([f for f in fs if f['h'] <= 2160], key=lambda f: f['h'])


def fetch(i):
    v = PP.meta(i)
    f = pick_file(v)
    path = os.path.join(FOOT, f'pexels_{i}_{f["h"]}p.mp4')
    if os.path.exists(path) and os.path.getsize(path) > 100000:
        return path, v, f
    for attempt in range(4):
        try:
            with requests.get(f['link'], stream=True, timeout=300) as r:
                r.raise_for_status()
                tmp = path + '.part'
                with open(tmp, 'wb') as fh:
                    for ch in r.iter_content(1 << 20):
                        fh.write(ch)
                os.replace(tmp, path)
            return path, v, f
        except Exception as e:  # noqa: BLE001
            print('retry', i, e, flush=True)
            time.sleep(2 ** (attempt + 1))
    raise RuntimeError(f'failed {i}')


if __name__ == '__main__':
    man, credits = {}, {}
    for name, (i, s, e, sp) in PICKS.items():
        path, v, f = fetch(i)
        man[name] = dict(file=os.path.basename(path), start=s, end=e, speed=sp, pexels_id=i)
        credits[str(i)] = dict(url=v['url'], user=v['user'], plates=credits.get(str(i), {}).get('plates', []) + [name])
        print(f'{name:17s} {os.path.basename(path)}  {os.path.getsize(path) / 1e6:.0f} MB', flush=True)
    json.dump(man, open(os.path.join(FOOT, 'manifest.json'), 'w'), indent=1)
    json.dump(credits, open(os.path.join(FOOT, 'pexels_credits.json'), 'w'), indent=1)
    print('manifest written', len(man))
