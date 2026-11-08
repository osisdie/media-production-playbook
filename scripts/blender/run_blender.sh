#!/usr/bin/env bash
# Run a bpy script headless with whichever Blender find_blender.sh finds.
#   scripts/blender/run_blender.sh <script.py> <output_dir> [script args...]
# The script must accept `--out <dir>` and write <dir>/.done (or <dir>/.failed) when finished.
# Native Blender (macOS/Linux) runs in the foreground and fails fast without .done. A Windows
# blender.exe on WSL is polled for the marker (the Store launcher returns immediately).
# On WSL, paths handed to a Windows blender are converted with `wslpath -w`.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="${1:?usage: run_blender.sh <script.py> <output_dir> [args...]}"
OUTDIR="${2:?usage: run_blender.sh <script.py> <output_dir> [args...]}"
shift 2
TIMEOUT="${BLENDER_TIMEOUT:-3600}"

if ! BL="$("$here/find_blender.sh")"; then
  echo "Blender not found. Install it (https://www.blender.org/download/) or set BLENDER=/path/to/blender." >&2
  exit 3
fi
mkdir -p "$OUTDIR"
OUTDIR="$(cd "$OUTDIR" && pwd)"
rm -f "$OUTDIR/.done" "$OUTDIR/.failed" "$OUTDIR"/frame_*.png  # no stale frames from older runs

script_arg="$(cd "$(dirname "$SCRIPT")" && pwd)/$(basename "$SCRIPT")"
out_arg="$OUTDIR"
case "$BL" in
  *.exe)
    script_arg="$(wslpath -w "$script_arg")"
    out_arg="$(wslpath -w "$OUTDIR")"
    cd /mnt/c  # Windows programs warn when started from a \\wsl$ cwd
    ;;
esac

echo "blender: $BL"
case "$BL" in
  *.exe)
    # Windows Blender from WSL. The Store launcher returns immediately and keeps rendering in
    # the background, so its exit code means nothing: poll for the marker file instead.
    # (A portable blender.exe blocks until done, so the loop below then ends at once.)
    "$BL" -b --factory-startup -P "$script_arg" -- --out "$out_arg" "$@" || true
    waited=0
    while [ ! -f "$OUTDIR/.done" ] && [ ! -f "$OUTDIR/.failed" ]; do
      if [ "$waited" -ge "$TIMEOUT" ]; then echo "timed out after ${TIMEOUT}s waiting for $OUTDIR/.done" >&2; exit 4; fi
      sleep 5; waited=$((waited + 5))
      if [ $((waited % 60)) -eq 0 ]; then
        n=0; for f in "$OUTDIR"/frame_*.png; do [ -e "$f" ] && n=$((n + 1)); done
        echo "  ... ${waited}s, $n frames so far"
      fi
    done
    ;;
  *)
    # Native Blender (macOS/Linux) runs in the foreground: no polling. If it exits without
    # writing .done (crash, bad script, killed), fail right away instead of waiting.
    status=0
    "$BL" -b --factory-startup -P "$script_arg" -- --out "$out_arg" "$@" || status=$?
    if [ ! -f "$OUTDIR/.done" ] && [ ! -f "$OUTDIR/.failed" ]; then
      echo "Blender exited (status $status) without writing $OUTDIR/.done" >&2
      exit 5
    fi
    ;;
esac
if [ -f "$OUTDIR/.failed" ]; then
  echo "Blender script failed:" >&2; cat "$OUTDIR/.failed" >&2; exit 5
fi
cat "$OUTDIR/.done"; echo
