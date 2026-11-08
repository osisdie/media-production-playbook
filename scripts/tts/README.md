# TTS scripts

## `kokoro_synth.py` — Kokoro-82M, CPU only

```bash
.venv/bin/python scripts/tts/kokoro_synth.py examples/course-demo/project.zh.json
.venv/bin/python scripts/tts/kokoro_synth.py examples/course-demo/project.zh.json --only 04   # redo one line
.venv/bin/python scripts/tts/kokoro_synth.py examples/course-demo/project.zh.json --force     # redo all
```

For each line in `lines[]` it writes `build/<lang>/vo/<id>.wav` next to the project file
(mono 24 kHz, leading/trailing silence trimmed, loudness-normalised to **−20 LUFS** with a
−1 dBFS peak ceiling) and `build/<lang>/timing.json` (`[{"id","text","dur"}]`, seconds).
A small `manifest.json` stores a hash of voice + speed + text per line, so editing one line
re-synthesises only that line.

- **Language** comes from the voice prefix: `af_/am_` US English, `bf_/bm_` UK English,
  `zf_/zm_` Mandarin (plus `j`, `e`, `f`, `h`, `i`, `p` for the other Kokoro languages).
- **Mandarin**: write the TTS text in Traditional or Simplified characters; both work.
  English words inside Mandarin text are phonemised by the English G2P.
- **Deterministic**: the same text/voice/speed gives the same audio, so there is no seed.
- **Threads**: uses every CPU core (`torch.set_num_threads(os.cpu_count())`). Run one TTS job
  at a time.

### Writing for TTS (lessons from the examples)

`text` is what the engine reads; `caption` is what the viewer reads. They can differ.

| Problem heard (via ASR) | Fix in `text` |
|---|---|
| Made-up product name read oddly in English ("Verdalo" → "Vertilow") | Spell it by syllables: `Ver-dah-lo` (caption keeps `Verdalo`) |
| Same name inside Mandarin turned into noise | Use a Chinese transliteration in `text` (`維達洛`), keep `Verdalo` in the caption |
| Polyphonic characters in Traditional text: `著` read *zhù* (接著 → 接住), `乾` read *qián* (乾淨 → 前進) | Rephrase: `然後`, `一週又一週`, `清爽` |
| A word misheard in a fixed phrase (`智慧提醒` → `只會提醒`) | Rephrase (`貼心的澆水提醒`) rather than post-processing audio |
| Numbers | Spell them as they should be read (`two hundred forty`, `兩百四十`); numerals go in the caption |

Always re-check rewritten lines with the narration QA (`scripts/vo/verify.py`).

## Other engines

A GPT-SoVITS adapter for a **consented** voice is documented in the playbook docs
(see `docs/consent/` and `docs/playbooks/`). It must write the same `vo/<id>.wav` +
`timing.json` layout so the render step does not change.
