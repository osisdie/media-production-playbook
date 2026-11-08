#!/usr/bin/env python3
"""Narration QA on the exact files the video will use.

    python scripts/vo/verify.py examples/course-demo/project.zh.json [--model small] [--model-path DIR] [--utmos]

Reads   examples/<example>/build/<lang>/vo/<id>.wav  (+ timing.json if present)
Writes  examples/<example>/build/<lang>/qa.json  and  QA.md  (a short "listen to these lines" list)

If the TTS text uses a respelling to get a pronunciation right (e.g. "Ver-dah-lo"), put the real wording in
an optional "qa_text" field of the line; error rate and drag alignment use qa_text when present.

Checks per line
  error   ASR error rate against the script: CER for zh, WER for en (textnorm.py). Averaged over two
          lead-in pads (0.4 s / 0.6 s of silence) because ASR flips on tens of milliseconds.
  drag    a token held too long that runs into the next one (drag.py) — catches TTS stalls/repeats that
          still transcribe correctly.
  rate    speaking rate after removing pauses > 0.15 s; flagged when it is an outlier for this narration
          (robust z-score, needs ≥ 5 lines).
  utmos   (optional, --utmos) predicted naturalness. Only the *relative* value is used: UTMOS is trained on
          studio English, so absolute scores for other languages or styles are not meaningful.

Decoding uses temperature 0 and a token cap: with temperature fallback a single bad take can make Whisper
re-decode six times to the length limit and hang for many minutes. A take that confuses ASR is a bad take —
report it, don't rescue it.
"""
import argparse
import json
import os
import re
import statistics
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from drag import drags  # noqa: E402
from textnorm import error_rate  # noqa: E402

ERR_FLAG = {"zh": 0.08, "en": 0.10}
Z_FLAG = 2.5
PADS = (0.4, 0.6)
SR = 16000


def robust_z(xs):
    med = statistics.median(xs)
    mad = statistics.median(abs(x - med) for x in xs) or 1e-9
    return med, [(x - med) / (1.4826 * mad) for x in xs]


def units(text, lang):
    """Rate units: zh = CJK characters (+2 per Latin word); en = words."""
    if lang.startswith("zh"):
        latin = re.findall(r"[A-Za-z0-9]+", text)
        return len(re.findall(r"[一-鿿]", text)) + 2 * len(latin)
    return len(re.findall(r"[A-Za-z0-9']+", text))


def speech_seconds(y):
    import librosa
    iv = librosa.effects.split(y, top_db=35, frame_length=512, hop_length=128)
    keep, last = 0, None
    for a, b in iv:
        if last is not None and (a - last) / SR <= 0.15:
            keep += a - last
        keep += b - a
        last = b
    return keep / SR


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--model", default="small", help="faster-whisper model name (downloaded on first use)")
    ap.add_argument("--model-path", default="", help="local CTranslate2 model dir (overrides --model)")
    ap.add_argument("--utmos", action="store_true",
                    help="also score relative naturalness (needs torch; downloads and runs tarepan/SpeechMOS code via torch.hub)")
    a = ap.parse_args()

    from faster_whisper import WhisperModel, decode_audio

    proj = json.load(open(a.project, encoding="utf-8"))
    lang = proj["lang"]
    base = os.path.join(os.path.dirname(os.path.abspath(a.project)), "build", lang)
    vo_dir = os.path.join(base, "vo")
    model = WhisperModel(a.model_path or a.model, device="cpu", compute_type="int8", cpu_threads=os.cpu_count() or 4)
    asr_lang = "zh" if lang.startswith("zh") else lang

    mos_model = None
    if a.utmos:
        import torch
        mos_model = torch.hub.load("tarepan/SpeechMOS:v1.2.0", "utmos22_strong", trust_repo=True)

    rows = []
    for line in proj["lines"]:
        path = os.path.join(vo_dir, f"{line['id']}.wav")
        if not os.path.exists(path):
            print(f"missing {path}", file=sys.stderr)
            continue
        wav = decode_audio(path, sampling_rate=SR)
        heard = []
        for pad in PADS:
            n = int(pad * SR)
            x = np.concatenate([np.zeros(n, dtype=wav.dtype), wav, np.zeros(int(0.2 * SR), dtype=wav.dtype)])
            segs, _ = model.transcribe(x, language=asr_lang, beam_size=5, vad_filter=False, condition_on_previous_text=False,
                                       word_timestamps=True, temperature=0.0, max_new_tokens=200)
            segs = list(segs)
            hyp = ("" if asr_lang == "zh" else " ").join(s.text.strip() for s in segs).strip()
            words = [[w.start - pad, w.end - pad, w.word] for s in segs for w in s.words]
            heard.append((hyp, words))
        err = round(sum(error_rate(line.get("qa_text", line["text"]), h, lang) for h, _ in heard) / len(heard), 3)
        dr = drags(heard[0][1], line.get("qa_text", line["text"]))
        row = {"id": line["id"], "text": line["text"], "hyp": heard[0][0], "error": err, "drag": dr,
               "dur": round(len(wav) / SR, 2), "rate": round(units(line.get("qa_text", line["text"]), lang) / max(speech_seconds(wav), 0.1), 2)}
        if mos_model is not None:
            import torch
            with torch.no_grad():
                row["utmos"] = round(float(mos_model(torch.from_numpy(wav).unsqueeze(0), SR).item()), 2)
        rows.append(row)
        print(f"{line['id']}  err {err:.3f}  rate {row['rate']}  drag {dr or '-'}  {row['hyp']}", flush=True)

    keys = ["rate"] + (["utmos"] if mos_model is not None else [])
    if len(rows) >= 5:
        for k in keys:
            _, zs = robust_z([r[k] for r in rows])
            for r, z in zip(rows, zs):
                r[f"z_{k}"] = round(z, 2)

    limit = ERR_FLAG.get(lang[:2], 0.10)
    for r in rows:
        why = []
        if r["error"] > limit:
            why.append(f"ASR error {r['error']:.2f} (heard: {r['hyp']})")
        if r["drag"]:
            why.append("drag " + ", ".join(f"'{w}' {d:.2f}s" for w, d, _ in r["drag"]))
        if abs(r.get("z_rate", 0)) > Z_FLAG:
            why.append(("fast" if r["z_rate"] > 0 else "slow") + f" ({r['rate']} units/s)")
        if r.get("z_utmos", 0) < -Z_FLAG:
            why.append(f"less natural than the rest (UTMOS {r['utmos']:.2f})")
        r["flags"] = why

    json.dump({"project": proj["id"], "rows": rows}, open(os.path.join(base, "qa.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    flagged = [r for r in rows if r["flags"]]
    md = [f"# Narration QA — {proj['id']}", "",
          f"{len(flagged)}/{len(rows)} lines flagged. Listen to the whole narration once, then re-listen to these.", ""]
    md += [f"- **{r['id']}** “{r['text']}” — {'; '.join(r['flags'])}" for r in flagged] or ["No line was flagged by the automatic checks."]
    open(os.path.join(base, "QA.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
