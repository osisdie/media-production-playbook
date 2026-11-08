#!/usr/bin/env bash
# Short preview GIF for READMEs (~6 s, 480 px wide, palettegen, <= 2 MB).
#   scripts/video/make_preview_gif.sh <video.mp4> <out.gif> [start_seconds] [length_seconds]
# If the GIF is over 2 MB it is re-made at a lower frame rate, then a smaller width.
set -euo pipefail
IN="${1:?usage: make_preview_gif.sh <video> <out.gif> [start] [length]}"
OUT="${2:?usage: make_preview_gif.sh <video> <out.gif> [start] [length]}"
START="${3:-0}"
LEN="${4:-6}"
MAX_BYTES=2000000
TMPD="$(mktemp -d 2>/dev/null || mktemp -d -t gif)"
PAL="$TMPD/palette.png"
trap 'rm -rf "$TMPD"' EXIT
mkdir -p "$(dirname "$OUT")"

size_of() { wc -c < "$1" | tr -d ' '; }

make() { # $1 fps, $2 width
  local f="fps=$1,scale=$2:-1:flags=lanczos"
  ffmpeg -v error -y -ss "$START" -t "$LEN" -i "$IN" -vf "$f,palettegen=max_colors=128:stats_mode=diff" "$PAL"
  ffmpeg -v error -y -ss "$START" -t "$LEN" -i "$IN" -i "$PAL" \
    -lavfi "$f [x]; [x][1:v] paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle" -loop 0 "$OUT"
}

for try in "12 480" "10 480" "8 480" "8 400" "6 360"; do
  # shellcheck disable=SC2086
  make $try
  bytes=$(size_of "$OUT")
  echo "  fps/width $try -> $bytes bytes"
  if [ "$bytes" -le "$MAX_BYTES" ]; then break; fi
done
echo "-> $OUT"
