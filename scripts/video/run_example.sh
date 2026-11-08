#!/usr/bin/env bash
# Full pipeline for one narrated example: synth -> QA (if available) -> render -> post.
#   scripts/video/run_example.sh <example> [lang ...]      e.g. scripts/video/run_example.sh course-demo zh
# Languages default to every examples/<example>/project.<lang>.json.
# Heavy steps run one at a time on purpose (low-resource machines).
set -euo pipefail
repo="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$repo"
EX="${1:?usage: run_example.sh <example> [lang ...]}"
shift
dir="examples/$EX"
[ -d "$dir" ] || { echo "no such example: $dir" >&2; exit 2; }

PY="${PYTHON:-}"
if [ -z "$PY" ]; then
  if [ -x .venv/bin/python ]; then PY=.venv/bin/python; else PY=python3; fi
fi
export PYTHON="$PY"

langs="$*"
if [ -z "$langs" ]; then
  for f in "$dir"/project.*.json; do
    l="${f##*/project.}"; langs="$langs ${l%.json}"
  done
fi
log() { mkdir -p build; echo "[$(date +%H:%M)] $*" | tee -a build/PROGRESS.log; }

for lang in $langs; do
  proj="$dir/project.$lang.json"
  log "$EX-$lang: TTS"
  "$PY" scripts/tts/kokoro_synth.py "$proj"
  if [ -f scripts/vo/verify.py ]; then
    log "$EX-$lang: narration QA"
    # QA is a report ("listen to these lines"), not a gate: keep going and read QA.md.
    "$PY" scripts/vo/verify.py "$proj" || echo "QA reported problems — see $dir/build/$lang/QA.md" >&2
  else
    echo "scripts/vo/verify.py not found — skipping narration QA" >&2
  fi
  log "$EX-$lang: render"
  node scripts/video/render.mjs --project "$proj"
  log "$EX-$lang: post (loudnorm + encode)"
  scripts/video/post.sh "$dir/build/$lang/render.mp4" "$dir/out/$EX-$lang.mp4" "$dir/out/$EX-$lang-vo.mp3"
  log "$EX-$lang: done -> $dir/out/$EX-$lang.mp4"
done
