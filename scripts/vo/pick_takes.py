#!/usr/bin/env python3
"""Pick the best take per line when the TTS engine is non-deterministic (e.g. GPT-SoVITS: one take per seed).

    python scripts/vo/pick_takes.py examples/<example>/project.<lang>.json [--model small] [--only 03,05]

Reads   build/<lang>/takes/<id>-<tag>.wav   (any number of takes per line; <tag> is e.g. s42 for seed 42)
Writes  build/<lang>/takes/choose.json      and copies the winner to build/<lang>/vo/<id>.wav

Ranking — the same ruler as verify.py, so a picked take is not flagged again by the final QA:
  1. number of QA flags (drag, error above the limit)
  2. drag score (seconds over the limit)
  3. error rate (rounded to 0.02 so ASR noise doesn't decide)
  4. distance from the median take length (a stalled/repeating take is much longer than its siblings)
Lines marked "manual": true in choose.json are kept. When the top two are close, read both transcripts:
error rate cannot tell a harmless homophone from a word that changes the meaning.
If every take is flagged, synthesise more seeds before reaching for audio processing.

Pick on the final processed audio when you post-process (prosody.py, EQ, loudness): ASR results can flip
after processing, so judging the raw take is not enough.
"""
import argparse
import glob
import json
import os
import shutil
import statistics
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from drag import drags, score as drag_score  # noqa: E402
from textnorm import error_rate  # noqa: E402

ERR_FLAG = {"zh": 0.08, "en": 0.10}
SR = 16000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--model", default="small")
    ap.add_argument("--model-path", default="")
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    from faster_whisper import WhisperModel, decode_audio

    proj = json.load(open(a.project, encoding="utf-8"))
    lang = proj["lang"]
    base = os.path.join(os.path.dirname(os.path.abspath(a.project)), "build", lang)
    tdir, vo_dir = os.path.join(base, "takes"), os.path.join(base, "vo")
    os.makedirs(vo_dir, exist_ok=True)
    cp = os.path.join(tdir, "choose.json")
    choose = json.load(open(cp, encoding="utf-8")) if os.path.exists(cp) else {}
    only = set(filter(None, a.only.split(",")))
    model = WhisperModel(a.model_path or a.model, device="cpu", compute_type="int8", cpu_threads=os.cpu_count() or 4)
    asr_lang = "zh" if lang.startswith("zh") else lang
    limit = ERR_FLAG.get(lang[:2], 0.10)

    for line in proj["lines"]:
        lid = line["id"]
        if (only and lid not in only) or choose.get(lid, {}).get("manual"):
            continue
        takes = sorted(glob.glob(os.path.join(tdir, f"{lid}-*.wav")))
        if not takes:
            continue
        rows = []
        for path in takes:
            wav = decode_audio(path, sampling_rate=SR)
            x = np.concatenate([np.zeros(int(0.4 * SR), dtype=wav.dtype), wav, np.zeros(int(0.2 * SR), dtype=wav.dtype)])
            segs, _ = model.transcribe(x, language=asr_lang, beam_size=5, vad_filter=False, condition_on_previous_text=False,
                                       word_timestamps=True, temperature=0.0, max_new_tokens=200)
            segs = list(segs)
            hyp = ("" if asr_lang == "zh" else " ").join(s.text.strip() for s in segs).strip()
            words = [[w.start - 0.4, w.end - 0.4, w.word] for s in segs for w in s.words]
            rows.append({"take": os.path.basename(path)[:-4], "dur": len(wav) / SR, "hyp": hyp,
                         "error": round(error_rate(line.get("qa_text", line["text"]), hyp, lang), 3),
                         "drag": drags(words, line.get("qa_text", line["text"])), "drag_score": drag_score(words, line.get("qa_text", line["text"]))})
        med = statistics.median(r["dur"] for r in rows)
        best = min(rows, key=lambda r: (bool(r["drag"]) + (r["error"] > limit), r["drag_score"],
                                        round(r["error"] / 0.02), abs(r["dur"] - med)))
        choose[lid] = {k: best[k] for k in ("take", "error", "hyp", "drag")}
        shutil.copyfile(os.path.join(tdir, best["take"] + ".wav"), os.path.join(vo_dir, f"{lid}.wav"))
        for r in rows:
            mark = "→" if r is best else " "
            print(f"{mark} {r['take']:12s} err {r['error']:.3f}  len×{r['dur'] / med:.2f}  drag {r['drag'] or '-'}  {r['hyp']}")
    json.dump(choose, open(cp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
