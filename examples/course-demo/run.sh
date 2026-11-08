#!/usr/bin/env bash
# Build the course-demo videos: TTS -> narration QA -> Remotion render -> loudness/encode.
#   bash examples/course-demo/run.sh          # every language
#   bash examples/course-demo/run.sh zh       # one language
set -euo pipefail
exec "$(cd "$(dirname "$0")/../.." && pwd)/scripts/video/run_example.sh" course-demo "$@"
