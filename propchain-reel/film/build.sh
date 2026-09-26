#!/usr/bin/env bash
# 2-minute film: score -> frames -> MP4 (+ a <30MB preview)
set -euo pipefail
cd "$(dirname "$0")/.."
FF=${FFMPEG:-$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")}
[ "${SKIP_ASSETS:-}" ] || { python3 film/tools/fetch_stock.py; node film/tools/capture_press.mjs; }
python3 film/score.py
[ "${SKIP_FRAMES:-}" ] || node render.mjs frames --page film/index.html --workers "${WORKERS:-3}" --fps 30 --to 3750
"$FF" -y -loglevel error -framerate 30 -i film/out/frames/f_%05d.jpg -i film/out/score.wav -map 0:v -map 1:a \
  -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -tune film -c:a aac -b:a 320k -movflags +faststart -shortest film/out/propchain-film-hq.mp4
"$FF" -y -loglevel error -i film/out/propchain-film-hq.mp4 -c:v libx264 -preset slow -b:v 1.6M -maxrate 2.4M -bufsize 4M -pass 1 -an -f mp4 /dev/null
"$FF" -y -loglevel error -i film/out/propchain-film-hq.mp4 -c:v libx264 -preset slow -b:v 1.6M -maxrate 2.4M -bufsize 4M -pass 2 -c:a aac -b:a 160k -movflags +faststart film/out/propchain-film-preview.mp4
rm -f ffmpeg2pass*
ls -la film/out/*.mp4
