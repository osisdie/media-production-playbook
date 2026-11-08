#!/usr/bin/env bash
# Build the promo-demo videos: TTS -> narration QA -> Remotion render -> loudness/encode.
#   bash examples/promo-demo/run.sh          # every language
#   bash examples/promo-demo/run.sh zh       # one language
set -euo pipefail
exec "$(cd "$(dirname "$0")/../.." && pwd)/scripts/video/run_example.sh" promo-demo "$@"
