#!/usr/bin/env bash
# Turn an RGBA PNG sequence (frame_0001.png ...) into delivery files.
#   scripts/blender/frames_to_mp4.sh <frames_dir> <out_basename> [fps] [bg_hex]
# Writes:
#   <out_basename>.webm  VP9 with alpha (yuva420p) — composite in Remotion with
#                        <OffthreadVideo transparent> (verified: alpha is kept)
#   <out_basename>.mov   ProRes 4444 with alpha — only if ALPHA_MOV=1 (large; for NLEs like Resolve/Premiere)
#   <out_basename>.mp4   H.264 High yuv420p over a solid background (default #0F2A20), no alpha
set -euo pipefail
IN="${1:?usage: frames_to_mp4.sh <frames_dir> <out_basename> [fps] [bg_hex]}"
OUT="${2:?usage: frames_to_mp4.sh <frames_dir> <out_basename> [fps] [bg_hex]}"
FPS="${3:-30}"
BG="${4:-0F2A20}"
mkdir -p "$(dirname "$OUT")"
first=""
for f in "$IN"/frame_*.png; do first="$f"; break; done  # glob is sorted; avoids ls|head SIGPIPE
[ -f "$first" ] || { echo "no frame_*.png in $IN" >&2; exit 1; }
start=$(basename "$first" .png | sed 's/frame_0*//')
[ -z "$start" ] && start=0
SEQ=(-framerate "$FPS" -start_number "$start" -i "$IN/frame_%04d.png")

echo "VP9 + alpha -> $OUT.webm"
ffmpeg -v error -y "${SEQ[@]}" -c:v libvpx-vp9 -pix_fmt yuva420p -b:v 0 -crf 24 -row-mt 1 \
  -deadline good -cpu-used 2 -auto-alt-ref 0 "$OUT.webm"

if [ "${ALPHA_MOV:-0}" = "1" ]; then
  echo "ProRes 4444 + alpha -> $OUT.mov"
  ffmpeg -v error -y "${SEQ[@]}" -c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le -vendor apl0 "$OUT.mov"
fi

echo "H.264 over #$BG -> $OUT.mp4"
size=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 "$first")
ffmpeg -v error -y -f lavfi -i "color=c=0x$BG:s=$size:r=$FPS" "${SEQ[@]}" \
  -filter_complex "[0:v][1:v]overlay=shortest=1,format=yuv420p" \
  -c:v libx264 -profile:v high -preset medium -crf 18 -pix_fmt yuv420p \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv -movflags +faststart "$OUT.mp4"
