#!/usr/bin/env bash
# Print the command to run Blender, or exit 1 if none is found.
# Search order:
#   1. $BLENDER
#   2. macOS app bundle /Applications/Blender.app/Contents/MacOS/Blender
#   3. `blender` on PATH
#   4. WSL only: a portable Windows install %USERPROFILE%\tools\blender-*\blender.exe (newest)
#   5. WSL only: the Microsoft Store alias %LOCALAPPDATA%\Microsoft\WindowsApps\blender-launcher.exe
#      (it detaches from the console: use run_blender.sh, which waits for a done-marker)
# Portable bash (macOS 3.2 OK).
set -u

if [ -n "${BLENDER:-}" ]; then echo "$BLENDER"; exit 0; fi

mac="/Applications/Blender.app/Contents/MacOS/Blender"
if [ -x "$mac" ]; then echo "$mac"; exit 0; fi

if command -v blender >/dev/null 2>&1; then command -v blender; exit 0; fi

if grep -qi microsoft /proc/version 2>/dev/null && command -v cmd.exe >/dev/null 2>&1; then
  winvar() { (cd /mnt/c 2>/dev/null && cmd.exe /c "echo %$1%" 2>/dev/null | tr -d '\r'); }
  prof=$(winvar USERPROFILE)
  if [ -n "$prof" ]; then
    tools="$(wslpath -u "$prof")/tools"
    # Newest portable build first: version-sort the folder *names* only, so a "-" elsewhere
    # in the path cannot confuse the sort. (WSL-only branch, so GNU sort -V is available.)
    newest=$(for d in "$tools"/blender-*; do [ -f "$d/blender.exe" ] && echo "${d##*/}"; done | sort -V -r | head -n 1 || true)
    if [ -n "$newest" ]; then echo "$tools/$newest/blender.exe"; exit 0; fi
  fi
  lad=$(winvar LOCALAPPDATA)
  if [ -n "$lad" ]; then
    launcher="$(wslpath -u "$lad")/Microsoft/WindowsApps/blender-launcher.exe"
    if [ -e "$launcher" ]; then echo "$launcher"; exit 0; fi
  fi
fi
exit 1
