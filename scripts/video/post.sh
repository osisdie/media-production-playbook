#!/usr/bin/env bash
# Final delivery encode for a Remotion render.
#   scripts/video/post.sh <render.mp4> <final.mp4> [narration.mp3]
# - two-pass EBU R128 loudnorm to I=-14 LUFS, true peak -1.5 dBTP (web/social level)
# - H.264 High, yuv420p, BT.709 tags, +faststart; AAC 48 kHz stereo 192 kb/s
# - optional: the normalised soundtrack as MP3 (narration-only for these examples)
# Portable bash (macOS 3.2 OK); JSON parsing is done by Python.
set -euo pipefail
IN="${1:?usage: post.sh <render.mp4> <final.mp4> [narration.mp3]}"
OUT="${2:?usage: post.sh <render.mp4> <final.mp4> [narration.mp3]}"
MP3="${3:-}"
I=-14; TP=-1.5; LRA=11
PY="${PYTHON:-python3}"

mkdir -p "$(dirname "$OUT")"
echo "loudnorm pass 1 (measure) ..."
measure=$(ffmpeg -hide_banner -nostats -i "$IN" -vn -af "loudnorm=I=$I:TP=$TP:LRA=$LRA:print_format=json" -f null - 2>&1 |
  "$PY" -c 'import json,sys; t=sys.stdin.read(); j=json.loads(t[t.rindex("{"):t.rindex("}")+1]);
print("measured_I={input_i}:measured_TP={input_tp}:measured_LRA={input_lra}:measured_thresh={input_thresh}:offset={target_offset}".format(**j))')
echo "  $measure"

echo "loudnorm pass 2 + H.264 encode ..."
ffmpeg -hide_banner -loglevel error -y -i "$IN" \
  -af "loudnorm=I=$I:TP=$TP:LRA=$LRA:$measure:linear=true,aresample=48000" \
  -c:v libx264 -profile:v high -preset medium -crf 18 -pix_fmt yuv420p \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv \
  -c:a aac -b:a 192k -ar 48000 -ac 2 -movflags +faststart "$OUT"
echo "  -> $OUT"

if [ -n "$MP3" ]; then
  ffmpeg -hide_banner -loglevel error -y -i "$OUT" -vn -c:a libmp3lame -b:a 192k "$MP3"
  echo "  -> $MP3"
fi
