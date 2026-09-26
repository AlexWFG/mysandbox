"""Cherry-pick and crop the press pack into film-ready frames.

python3 film/tools/crop_press.py <press_pack_dir>
Writes film/press/pk_<name>.jpg (1600x925, the press window's aspect) and
film/press/pk_highlights.json with highlight rects in 1280x740 window space.
Source coordinates are pixels in the pack's screenshots (NN_outlet_*.png).
"""
import json, os, sys
from PIL import Image

SRC = os.path.join(sys.argv[1] if len(sys.argv) > 1 else '/tmp/pp/x/propchain_press_pack', 'screenshots')
OUT = os.path.join(os.path.dirname(__file__), '..', 'press')
AR = 1280 / 740

# name: (file, crop box x0,y0,x1 (y1 derived from aspect), [highlight rects in source px])
CROPS = {
    'cnbc24':     ('04_cnbc_detail.png',        (0, 0, 1304),   [(446, 445, 728, 480), (159, 485, 548, 520)]),
    'cnbc25':     ('12_cnbc_hero.png',          (0, 0, 1304),   [(148, 648, 834, 702)]),
    'dubai':      ('14_dubailanddept_detail.png', (0, 120, 1304), [(366, 500, 848, 538)]),
    'deloitte':   ('13_coindesk_hero.png',      (0, 0, 1304),   []),
    'bloomberg':  ('10_bloomberg_detail.png',   (0, 150, 1304), [(596, 466, 749, 503), (183, 509, 759, 548), (183, 552, 299, 592)]),
    'detroit1':   ('16_outliermedia_hero.png',  (0, 0, 1304),   []),
    'detroit2':   ('18_outliermedia_hero.png',  (0, 0, 1304),   []),
    'forbes':     ('19_forbes_hero.png',        (0, 0, 1126),   []),
    'forbes2':    ('19_forbes_detail.png',      (0, 190, 820),   [(233, 315, 399, 350), (33, 349, 453, 384), (33, 532, 496, 567), (33, 566, 104, 600)]),
}

meta = {}
for name, (f, (x0, y0, x1), hls) in CROPS.items():
    im = Image.open(os.path.join(SRC, f)).convert('RGB')
    w = x1 - x0; h = round(w / AR); y1 = min(im.height, y0 + h)
    if y1 - y0 < h:  # pad bottom with page background if the capture is short
        pad = Image.new('RGB', (w, h), im.getpixel((w - 5, im.height - 5)))
        pad.paste(im.crop((x0, y0, x1, y1)), (0, 0)); crop = pad
    else:
        crop = im.crop((x0, y0, x1, y1))
    crop.resize((1600, 925), Image.LANCZOS).save(os.path.join(OUT, f'pk_{name}.jpg'), quality=92)
    k = 1280 / w
    meta[name] = [[round((a - x0) * k), round((b - y0) * k), round((c - a) * k), round((d - b) * k)] for a, b, c, d in hls]
    print(name, f, 'crop', (x0, y0, x1, y0 + h), 'hl', meta[name])
json.dump(meta, open(os.path.join(OUT, 'pk_highlights.json'), 'w'), indent=1)
