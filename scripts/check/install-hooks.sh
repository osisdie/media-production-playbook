#!/usr/bin/env bash
# Install a pre-commit hook: gitleaks (staged) + private-term scan.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
cat > .git/hooks/pre-commit <<'HOOK'
#!/usr/bin/env bash
set -e
if command -v gitleaks >/dev/null; then
  gitleaks git --staged --no-banner --redact
else
  echo "warning: gitleaks not installed — skipping secret scan" >&2
fi
scripts/check/scan-private.sh --all
HOOK
chmod +x .git/hooks/pre-commit
echo "pre-commit hook installed"
