#!/usr/bin/env bash
# One-time setup for macOS (Apple Silicon or Intel). Works with the system bash 3.2.
# Creates .venv (Kokoro TTS + faster-whisper), installs Remotion,
# fetches the Noto Sans TC font and pre-downloads models.
#   bash scripts/setup/setup-macos.sh
#   SKIP_MODELS=1 bash scripts/setup/setup-macos.sh
set -euo pipefail
. "$(dirname "$0")/common.sh"

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ffmpeg not found. Install with Homebrew:  brew install ffmpeg" >&2
  exit 1
fi
if ! command -v python3.12 >/dev/null 2>&1 && ! command -v python3.11 >/dev/null 2>&1 \
   && ! command -v python3.10 >/dev/null 2>&1 && [ -z "${PYTHON:-}" ]; then
  echo "Kokoro needs Python 3.10-3.12. Install with:  brew install python@3.12" >&2
  echo "(or set PYTHON=/path/to/python3.12)" >&2
  exit 1
fi

# On macOS the default PyPI torch wheel is CPU/MPS and small enough; no extra index.
run_all ""
