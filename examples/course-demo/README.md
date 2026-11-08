# course-demo — "Pour-Over Coffee at Home" (16:9, ~42 s)

A calm teaching video for a fictional mini-course in three stages: the gear, ratio & grind,
the pour.

| File | Voice (Kokoro) | Output |
|---|---|---|
| `project.zh.json` | `zm_yunxi` (male, Mandarin; Traditional characters) | `out/course-demo-zh.mp4`, `out/course-demo-zh-vo.mp3` |
| `project.en.json` | `af_heart` (female, US English) | `out/course-demo-en.mp4`, `out/course-demo-en-vo.mp3` |

```bash
bash examples/course-demo/run.sh       # both languages
bash examples/course-demo/run.sh en    # one language
```

Each line's `visual` picks a layout: `title`, `stage` (checklist `items` or one `big`
number), `end`. `design.stages` names the stages shown in the step list. Composition:
`remotion/src/examples/course-demo/`.

**Notes on the script.** Numbers are spelled out in the TTS text (`fifteen grams`,
`十五公克`) and shown as numerals in captions (`15 g`). Two Mandarin phrases were rewritten
after ASR showed polyphonic characters being misread (`乾淨` → `清爽`, `接著` → `然後`).

## QA notes

Narration QA (`scripts/vo/verify.py`, faster-whisper `small`) was used as a "listen by proxy".
Lines were rewritten instead of post-processing audio:

| Line | Before | After | Why |
|---|---|---|---|
| zh 01 | `沖出一杯乾淨的好咖啡` | `沖出一杯清爽的好咖啡` | `乾` is polyphonic (*gān* / *qián*); it was read *qián* (ASR: `前進`). |
| zh 04 | `大約像鹽巴一樣` | `顆粒大約像食鹽` | `鹽巴` was heard as `研發`. |
| zh 06 | `接著慢慢地…` | `然後慢慢地…` | `著` was read *zhù* (`接住`). |

Accepted as-is, because the audio is right and only the written form differs:
homophones in the ASR transcript (`濾`→`绿`, `秤`→`称`, `度`→`杜`, `細`→`系`, `畫`→`化`,
all the same syllable), numbers transcribed as digits (`兩百四十` → `240`), and mild
speaking-rate outliers on lines dense with numbers (zh 02 slow, zh 03 fast). The English
narration passed with no flags.
