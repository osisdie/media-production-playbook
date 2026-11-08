#!/usr/bin/env bash
# Shared setup steps, sourced by setup-linux-wsl.sh and setup-macos.sh.
# Written for bash 3.2 (macOS default): no associative arrays, no GNU-only flags.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV="$REPO_ROOT/.venv"
FONT_DIR="$REPO_ROOT/remotion/public/fonts"
FONT_URL="https://github.com/google/fonts/raw/main/ofl/notosanstc/NotoSansTC%5Bwght%5D.ttf"

log() { printf '\n==> %s\n' "$*"; }

# Pick a Python that Kokoro supports (3.10-3.12). Honours $PYTHON if set.
find_python() {
  if [ -n "${PYTHON:-}" ]; then echo "$PYTHON"; return 0; fi
  for v in 3.12 3.11 3.10; do
    # A pyenv shim can exist on PATH without being runnable, so actually run it.
    if command -v "python$v" >/dev/null 2>&1 && "python$v" -c 'import venv' >/dev/null 2>&1; then
      command -v "python$v"; return 0
    fi
    if command -v pyenv >/dev/null 2>&1; then
      p="$(pyenv root)/versions"
      # newest installed patch release of this minor version
      cand=$(ls -d "$p/$v".* 2>/dev/null | sort -t. -k3 -n | tail -n 1)
      if [ -n "$cand" ] && [ -x "$cand/bin/python$v" ]; then echo "$cand/bin/python$v"; return 0; fi
    fi
  done
  return 1
}

setup_python() {
  # $1 = extra pip args (e.g. CPU torch index on Linux)
  local extra="${1:-}"
  local py
  if ! py=$(find_python); then
    echo "No Python 3.10-3.12 found. Install one (e.g. 'pyenv install 3.12') or set PYTHON=/path/to/python3.12." >&2
    return 1
  fi
  log "Python: $py ($("$py" -V 2>&1))"
  if [ ! -x "$VENV/bin/python" ]; then
    "$py" -m venv "$VENV"
  fi
  "$VENV/bin/python" -m pip install --upgrade pip wheel >/dev/null
  log "Installing Python packages into .venv (first run downloads PyTorch, a few minutes)"
  # shellcheck disable=SC2086
  "$VENV/bin/python" -m pip install $extra -r "$REPO_ROOT/scripts/setup/requirements.txt"
}

setup_node() {
  if ! command -v npm >/dev/null 2>&1; then
    echo "npm not found. Install Node.js 18+ (https://nodejs.org) and re-run." >&2
    return 1
  fi
  log "Installing Remotion (npm ci in remotion/)"
  (cd "$REPO_ROOT/remotion" && if [ -f package-lock.json ]; then npm ci; else npm install; fi)
}

setup_fonts() {
  mkdir -p "$FONT_DIR"
  if [ -f "$FONT_DIR/NotoSansTC.ttf" ]; then
    log "Font already present: remotion/public/fonts/NotoSansTC.ttf"
    return 0
  fi
  log "Downloading Noto Sans TC (SIL Open Font License) into remotion/public/fonts/"
  curl -fL --retry 3 -o "$FONT_DIR/NotoSansTC.ttf.part" "$FONT_URL" &&
    mv "$FONT_DIR/NotoSansTC.ttf.part" "$FONT_DIR/NotoSansTC.ttf"
}

prefetch_models() {
  log "Pre-downloading Kokoro-82M and faster-whisper 'small' (see models/README.md)"
  "$VENV/bin/python" "$REPO_ROOT/scripts/setup/prefetch_models.py"
}

run_all() {
  local extra="${1:-}"
  setup_python "$extra"
  setup_node
  setup_fonts
  if [ "${SKIP_MODELS:-0}" != "1" ]; then prefetch_models; fi
  log "Environment report"
  "$VENV/bin/python" "$REPO_ROOT/scripts/setup/check_env.py"
}
