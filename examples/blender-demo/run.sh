#!/usr/bin/env bash
# Optional 3D: procedural plant pot + "Verdalo" wordmark turntable (6 s loop, 30 fps).
#   bash examples/blender-demo/run.sh            # both versions
#   SAMPLES=32 bash examples/blender-demo/run.sh # smoother, slower
# Outputs (gitignored):
#   out/verdalo-turntable-9x16.webm   transparent VP9; promo-demo uses it as its opening shot
#   out/verdalo-turntable-9x16.mp4    same on a solid background (for a quick look)
#   out/blender-demo-16x9.mp4         standalone landscape loop
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
repo="$(cd "$here/../.." && pwd)"
cd "$repo"
SAMPLES="${SAMPLES:-16}"
ENGINE="${ENGINE:-eevee}"
log() { echo "[$(date +%H:%M)] $*" | tee -a build/PROGRESS.log; }
mkdir -p build "$here/out"

if ! scripts/blender/find_blender.sh >/dev/null; then
  echo "Blender not found — skipping. promo-demo will use its 2D opening." >&2
  echo "Install Blender 4.2+ or set BLENDER=/path/to/blender, then re-run." >&2
  exit 0
fi

log "blender-demo: portrait 1080x1920 ($ENGINE, $SAMPLES samples)"
scripts/blender/run_blender.sh scripts/blender/render_scene.py "$here/build/frames-9x16" \
  --orientation portrait --width 1080 --height 1920 --samples "$SAMPLES" --engine "$ENGINE"
scripts/blender/frames_to_mp4.sh "$here/build/frames-9x16" "$here/out/verdalo-turntable-9x16" 30

log "blender-demo: landscape 1920x1080"
scripts/blender/run_blender.sh scripts/blender/render_scene.py "$here/build/frames-16x9" \
  --orientation landscape --width 1920 --height 1080 --samples "$SAMPLES" --engine "$ENGINE"
scripts/blender/frames_to_mp4.sh "$here/build/frames-16x9" "$here/build/blender-demo-16x9" 30
mv "$here/build/blender-demo-16x9.mp4" "$here/out/blender-demo-16x9.mp4"

log "blender-demo: done"
ls -la "$here/out"
