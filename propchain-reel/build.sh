#!/usr/bin/env bash
# Full pipeline: score -> 60fps frames -> 30fps with 180° shutter blur -> MP4.
set -euo pipefail
cd "$(dirname "$0")"
FFMPEG=${FFMPEG:-$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")}

python3 audio.py
node render.mjs frames --workers "${WORKERS:-4}" --fps 60 --to 1800

"$FFMPEG" -y -framerate 60 -i out/frames/f_%05d.jpg -i out/score.wav \
  -filter_complex "[0:v]tmix=frames=2:weights='1 1',fps=30,format=yuv420p[v]" \
  -map "[v]" -map 1:a -c:v libx264 -preset slow -crf 15 -profile:v high -tune film \
  -c:a aac -b:a 320k -movflags +faststart -shortest out/propchain-reel.mp4
echo "-> out/propchain-reel.mp4"
