#!/usr/bin/env bash
# One-time setup for Linux and Windows WSL2 (Ubuntu/Debian).
# Creates .venv (Kokoro TTS + faster-whisper, CPU only), installs Remotion,
# fetches the Noto Sans TC font and pre-downloads models.
#   bash scripts/setup/setup-linux-wsl.sh            # full setup
#   SKIP_MODELS=1 bash scripts/setup/setup-linux-wsl.sh
set -euo pipefail
. "$(dirname "$0")/common.sh"

missing=""
for bin in ffmpeg ffprobe curl; do
  command -v "$bin" >/dev/null 2>&1 || missing="$missing $bin"
done
if [ -n "$missing" ]; then
  echo "Missing system tools:$missing" >&2
  echo "Install them with:  sudo apt-get update && sudo apt-get install -y ffmpeg curl" >&2
  exit 1
fi

# Remotion's headless Chrome needs a few shared libraries on minimal distros.
# They are usually present on Ubuntu desktop/WSL; if a render fails with
# "error while loading shared libraries", install them with:
#   sudo apt-get install -y libnss3 libatk-bridge2.0-0 libgbm1 libxkbcommon0 libasound2

# CPU-only PyTorch wheels: avoids downloading ~2 GB of CUDA libraries.
run_all "--extra-index-url https://download.pytorch.org/whl/cpu"
