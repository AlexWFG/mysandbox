#!/usr/bin/env bash
# Encode rendered frames + mix into the two deliverables (two-pass x264, loudness-normalised AAC).
#   assurance-1080p.mp4   < 95 MB   1920x1080, ~2.7 Mbps, light hqdn3d so the grain doesn't eat the bitrate
#   assurance-preview.mp4 < 29 MB   1280x720,  ~0.76 Mbps (the film is 3:59, so 1.5 Mbps would not fit 29 MB)
set -euo pipefail
cd "$(dirname "$0")"
IN=(-framerate 30 -i out/frames/f_%05d.jpg -i out/mix.wav)
AF="loudnorm=I=-16:TP=-1.5:LRA=11"
p() { ffmpeg -y -v error "${IN[@]}" -map 0:v -map 1:a -c:v libx264 -preset slow -pix_fmt yuv420p -profile:v high "$@"; }

ffmpeg -y -v error -i out/mix.wav -af "$AF" -ar 48000 out/mix_norm.wav
IN=(-framerate 30 -i out/frames/f_%05d.jpg -i out/mix_norm.wav)

VF1="hqdn3d=1.5:1.5:4:4"
p -vf "$VF1" -b:v 2700k -pass 1 -passlogfile out/p1080 -an -f mp4 /dev/null
p -vf "$VF1" -b:v 2700k -maxrate 5000k -bufsize 8000k -pass 2 -passlogfile out/p1080 -c:a aac -b:a 192k -movflags +faststart -shortest assurance-1080p.mp4

VF2="hqdn3d=2:2:5:5,scale=1280:720:flags=lanczos"
p -vf "$VF2" -b:v 760k -pass 1 -passlogfile out/p720 -an -f mp4 /dev/null
p -vf "$VF2" -b:v 760k -maxrate 1500k -bufsize 3000k -pass 2 -passlogfile out/p720 -c:a aac -b:a 160k -movflags +faststart -shortest assurance-preview.mp4

ls -la assurance-*.mp4
