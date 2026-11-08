---
name: narration-qa
description: Use when producing or checking TTS / voice-clone narration (courses, promos, product demos; Mandarin, English, Taiwanese Hokkien/Taigi) — picking takes, catching drags/repeats/rate outliers that CER misses, prosody post-processing, and producing a "listen to these lines" list. Works CPU-only on WSL/Linux/macOS.
---

# Narration QA

Full playbook: `docs/playbooks/narration-qa.md` (engines: `docs/playbooks/voice-production.md`; Taiwanese Hokkien / Taigi TTS & ASR: `docs/playbooks/taiwanese-taigi.md`).

1. Synthesise per line into `examples/<example>/build/<lang>/vo/<id>.wav` (non-deterministic engines: several takes into `build/<lang>/takes/<id>-<tag>.wav`, then `python3 scripts/vo/pick_takes.py <project.json>`).
2. Run `python3 scripts/vo/verify.py <project.json>` **on the final processed files** → `QA.md`.
3. For each flagged line: rewrite the text, try more seeds, or undo processing — then re-run verify. Never stretch a word that already drags.
4. Rank candidates with the same ruler as the final QA (number of flags first, then drag, then error).
5. Deliver the QA list with the video; say which aspects were *not* verified (tone, accent, likeness).

Rules: CER ≠ good reading; ASR flips on tens of ms (pad silence, beam 5, temperature 0, token cap); UTMOS is relative only; only consented voices may be cloned, and never committed.
