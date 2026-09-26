#!/usr/bin/env bash
# Architecture explainer: narration layout -> mix -> frames -> MP4s.
# Needs: npm i (playwright, lucide-static); pip install numpy scipy pillow imageio-ffmpeg
set -euo pipefail
cd "$(dirname "$0")"
FF=${FFMPEG:-$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")}
python3 tools/eleven.py vo            # cached: spends nothing unless narration text changed
python3 tools/layout.py
[ -d stock/clips/tower ] || python3 tools/fetch_stock.py
python3 tools/mix.py
FRAMES=$(python3 -c "import json;print(int(round(json.load(open('audio/timeline.json'))['end']*30)))")
[ "${SKIP_FRAMES:-}" ] || node render.mjs frames --page film/index.html --workers "${WORKERS:-4}" --fps 30 --to "$FRAMES"
"$FF" -y -loglevel error -framerate 30 -i film/out/frames/f_%05d.jpg -i out/mix.wav -map 0:v -map 1:a \
  -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -c:a aac -b:a 320k -movflags +faststart -shortest out/master.mp4
enc() { # $1 bitrate  $2 out  $3 extra vf
  "$FF" -y -loglevel error -i out/master.mp4 -vf "$3" -c:v libx264 -preset slow -b:v "$1" -maxrate "$4" -bufsize 6M -pass 1 -passlogfile out/p -an -f mp4 /dev/null
  "$FF" -y -loglevel error -i out/master.mp4 -vf "$3" -c:v libx264 -preset slow -b:v "$1" -maxrate "$4" -bufsize 6M -pass 2 -passlogfile out/p -pix_fmt yuv420p -c:a aac -b:a "$5" -movflags +faststart "$2"
}
# 4:00 at <29 MB leaves ~0.9 Mbps in total, so the preview is 720p
enc 780k architecture-preview.mp4 "hqdn3d=2:2:5:5,scale=1280:720:flags=lanczos" 1400k 128k
enc 2750k architecture-1080p.mp4 "hqdn3d=1:1:3:3" 4500k 160k
ls -la *.mp4
