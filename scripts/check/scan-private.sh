#!/usr/bin/env bash
# Scan tracked + staged files for private terms listed in the local, gitignored .private-denylist.
# Usage: scripts/check/scan-private.sh [--all]   (--all also scans untracked, non-ignored files)
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
LIST=.private-denylist
if [ ! -f "$LIST" ]; then
  echo "No $LIST found — create one (one regex per line) to enable the private-term scan." >&2
  exit 0
fi
PATTERNS=$(mktemp)
trap 'rm -f "$PATTERNS"' EXIT
grep -vE '^\s*(#|$)' "$LIST" > "$PATTERNS"
if [ "${1:-}" = "--all" ]; then
  FILES=$(git ls-files --cached --others --exclude-standard)
else
  FILES=$(git ls-files --cached)
fi
[ -z "$FILES" ] && { echo "nothing to scan"; exit 0; }
# shellcheck disable=SC2086
if echo "$FILES" | tr '\n' '\0' | xargs -0 grep -nIiE -f "$PATTERNS" -- 2>/dev/null; then
  echo "✗ private terms found (see above)" >&2
  exit 1
fi
echo "✓ no private terms found in $(echo "$FILES" | wc -l | tr -d ' ') files"
