# promo-demo — "Verdalo" app promo (9:16, ~30 s)

A punchy vertical promo for **Verdalo**, a fictional plant-care app (watering reminders,
light check with the phone camera, care calendar).

| File | Voice (Kokoro) | Output |
|---|---|---|
| `project.en.json` | `am_michael` (male, US English) | `out/promo-demo-en.mp4`, `out/promo-demo-en-vo.mp3` |
| `project.zh.json` | `zf_xiaoxiao` (female, Mandarin; Traditional characters) | `out/promo-demo-zh.mp4`, `out/promo-demo-zh-vo.mp3` |

```bash
bash examples/promo-demo/run.sh        # both languages
bash examples/promo-demo/run.sh zh     # one language
```

Pipeline: `scripts/tts/kokoro_synth.py` → `scripts/vo/verify.py` (QA report in `build/<lang>/QA.md`)
→ `scripts/video/render.mjs` → `scripts/video/post.sh` (−14 LUFS, H.264). Composition:
`remotion/src/examples/promo-demo/`.

**Opening shot.** If `examples/blender-demo/out/verdalo-turntable-9x16.webm` exists (run
`examples/blender-demo/run.sh` first), the first shot uses that transparent 3D turntable.
Otherwise it falls back to a 2D illustrated pot — no Blender needed.

**Notes on the script.** The brand name is spelled `Ver-dah-lo` in the English TTS text and
transliterated as `維達洛` in the Mandarin TTS text; captions and on-screen text always show
`Verdalo`. Captions sit above the bottom 20 % of the frame, clear of app overlays.

## QA notes

Narration QA (`scripts/vo/verify.py`, faster-whisper `small`) was used as a "listen by proxy".
Lines were rewritten instead of post-processing audio:

| Line | Before | After | Why |
|---|---|---|---|
| en 02, 04, 06 | `Verdalo` | `Ver-dah-lo` (+ `qa_text: "… Verdalo …"`) | The made-up name is not in the English G2P lexicon; the fallback read it as "Vertilow". Syllable spelling is heard as "Verdalo". `qa_text` tells QA what the line should sound like. |
| en 06 | `Happy plants, less guessing.` | `Happy plants. No more guessing.` | The short comma pause sounded like "plantless guessing"; with a full stop ASR heard "let's guessing". "No more guessing" cannot be misheard. |
| zh 02, 06 | `Verdalo` inside Mandarin | `維達洛` | The English word inside Mandarin text came out as noise (ASR heard "任10A大樓"). A transliteration is read cleanly; captions still show `Verdalo`. |
| zh 03 | `智慧提醒` | `貼心的澆水提醒` | Heard as `只會提醒` with a dragged first syllable. |
| zh 05 | `一週接著一週` | `一週又一週` | `著` is polyphonic in Traditional text and was read *zhù* (`接住`). |

Accepted as-is: ASR hearing `維` as `为`/`维` (homophones), and small speaking-rate outliers.
