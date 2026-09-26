#!/usr/bin/env bash
# frames + mix -> mandate-market-1080p.mp4 (<95 MB) and mandate-market-preview.mp4 (<29 MB), two-pass x264.
set -e
cd "$(dirname "$0")/.."
FR=out/frames/f_%05d.jpg; A=out/mix.wav; P=out/x264pass
ffmpeg -y -v error -framerate 30 -i $FR -vf "hqdn3d=1.5:1.5:4:4,format=yuv420p" -c:v libx264 -preset slow -b:v 2900k -pass 1 -passlogfile $P -an -f mp4 /dev/null
ffmpeg -y -v error -framerate 30 -i $FR -i $A -vf "hqdn3d=1.5:1.5:4:4,format=yuv420p" -c:v libx264 -preset slow -b:v 2900k -pass 2 -passlogfile $P \
  -c:a aac -b:a 192k -movflags +faststart -shortest mandate-market-1080p.mp4
ffmpeg -y -v error -framerate 30 -i $FR -vf "hqdn3d=2:2:5:5,scale=1280:720:flags=lanczos,format=yuv420p" -c:v libx264 -preset slow -b:v 750k -pass 1 -passlogfile $P -an -f mp4 /dev/null
ffmpeg -y -v error -framerate 30 -i $FR -i $A -vf "hqdn3d=2:2:5:5,scale=1280:720:flags=lanczos,format=yuv420p" -c:v libx264 -preset slow -b:v 750k -pass 2 -passlogfile $P \
  -c:a aac -b:a 160k -movflags +faststart -shortest mandate-market-preview.mp4
ls -la mandate-market-*.mp4
