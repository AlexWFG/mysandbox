"""Contact sheet of rendered stills: python3 tools/sheet.py out.jpg [cols] (reads out/stills/*.jpg)."""
import glob, os, sys
from PIL import Image, ImageDraw
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
fs = sorted(glob.glob(os.path.join(HERE, 'out', 'stills', 't_*.jpg')), key=lambda f: float(os.path.basename(f)[2:-4]))
cols = int(sys.argv[2]) if len(sys.argv) > 2 else 3; W, H = 640, 360
rows = (len(fs) + cols - 1) // cols; S = Image.new('RGB', (cols * W, rows * H), (0, 0, 0)); d = ImageDraw.Draw(S)
for i, f in enumerate(fs):
    S.paste(Image.open(f).resize((W, H)), ((i % cols) * W, (i // cols) * H))
    d.rectangle([(i % cols) * W, (i // cols) * H, (i % cols) * W + 80, (i // cols) * H + 18], fill=(0, 0, 0))
    d.text(((i % cols) * W + 4, (i // cols) * H + 3), os.path.basename(f)[2:-4], fill=(255, 190, 6))
S.save(sys.argv[1], quality=85); print(len(fs), 'stills')
