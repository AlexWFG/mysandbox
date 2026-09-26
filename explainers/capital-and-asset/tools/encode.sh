#!/bin/bash
# Two-pass H.264 encodes from out/frames + out/mix.wav
set -e
cd "$(dirname "$0")/.."
FF=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
IN="-framerate 30 -i out/frames/f_%05d.jpg -i out/mix.wav"
enc() { # name vbitrate maxrate vf
  $FF -y -loglevel error $IN -c:v libx264 -preset slow -b:v $2 -maxrate $3 -bufsize $3 -vf "$4" -pix_fmt yuv420p -pass 1 -passlogfile out/x264_$1 -an -f mp4 /dev/null
  $FF -y -loglevel error $IN -c:v libx264 -preset slow -b:v $2 -maxrate $3 -bufsize $3 -vf "$4" -pix_fmt yuv420p -pass 2 -passlogfile out/x264_$1 -c:a aac -b:a 160k -movflags +faststart -shortest capital-and-asset-$1.mp4
  ls -la capital-and-asset-$1.mp4
}
enc preview 720k 1500k "scale=1920:1080,hqdn3d=1.5:1.5:4:4"
enc 1080p 2900k 5000k "hqdn3d=1:1:3:3"
