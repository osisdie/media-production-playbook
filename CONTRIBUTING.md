# Contributing

Thanks for helping! Good contributions: new playbooks (marketing, podcasts, other languages), portability fixes (especially macOS), better QA checks, and new examples.

## Ground rules
- **No real voices.** Examples must use synthetic voices (or voices whose license explicitly allows redistribution). Never commit reference audio of a person.
- **No real brands, people, prices or personal data** in examples, mock screens or docs. Use fictional names.
- **No secrets.** Keys only via environment variables / `.env` (git-ignored).
- **No generated media in git.** Renders go to GitHub Releases; only small preview GIFs (≤ 2 MB) live in `docs/media/`.
- Keep scripts portable: bash 3.2-compatible (macOS), real logic in Python/Node. Split files per OS only when unavoidable.

## Before opening a PR
```bash
bash scripts/check/install-hooks.sh          # once: pre-commit gitleaks + private-term scan
python3 -m unittest discover -s tests
shellcheck scripts/**/*.sh examples/*/run.sh
gitleaks dir --no-banner --redact .
```
Describe what you changed, how you tested it (OS, CPU/GPU), and — for playbooks — the evidence (measurements, before/after).
