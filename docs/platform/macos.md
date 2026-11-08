# macOS (Apple Silicon or Intel)

> Status: scripts are written to be portable (bash 3.2-compatible, logic in Python/Node) and are exercised by CI on `macos-latest`. The example renders in this repo were produced on WSL; please open an issue if a step differs on your Mac.

## Setup
```bash
brew install ffmpeg node python@3.12   # python 3.10–3.12 for Kokoro
bash scripts/setup/setup-macos.sh
python3 scripts/setup/check_env.py
```

## Tips
- Blender: install the regular app into `/Applications`; `scripts/blender/find_blender.sh` finds `/Applications/Blender.app/Contents/MacOS/Blender`. Set `BLENDER=/path/to/Blender` if it lives elsewhere.
- Apple Silicon: PyTorch uses the CPU by default in these scripts (portable and predictable). Kokoro is fast enough on CPU; MPS can be tried but is not required.
- macOS ships bash 3.2 — the repo's scripts avoid bash 4 features. If you add scripts, avoid associative arrays, `sed -i` without a suffix, and `readlink -f`.
- Fonts: Remotion loads its own fonts from `remotion/public/fonts/`, so system fonts don't matter.
