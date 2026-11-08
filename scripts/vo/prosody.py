#!/usr/bin/env python3
"""Pitch-range expansion and word stretching with Praat PSOLA (overlap-add). Optional post-processing for
flat-sounding TTS/voice-clone narration. Needs `praat-parselmouth`.

    python scripts/vo/prosody.py in.wav out.wav --target-std 2.6 [--target-med HZ] [--spans '[[1.2,1.6]]']
    python scripts/vo/prosody.py --measure a.wav b.wav

Pitch:  new = target_med × (f / median)^k,  k = target_std / current semitone std, clamped to [1, k_max].
        k > 1 widens the melody around the median without changing words or timbre. Measure the speaker's own
        recordings first and aim for *their* natural range — over-expanded pitch sounds theatrical, and PSOLA
        costs some naturalness (relative UTMOS typically drops 0.2–0.5).
Spans:  time ranges (seconds, e.g. from ASR word timestamps) to slow down: first 60 % × stretch,
        last 40 % × tail. Useful for foreign words a voice rushes through. Check length *before* stretching —
        never stretch a word the voice already drags.
Always re-run ASR on the processed file (verify.py): processing can turn a clear word into a misheard one.
"""
import argparse
import json
import math

import parselmouth
from parselmouth.praat import call


def pitch_points(manip):
    pt = call(manip, "Extract pitch tier")
    n = call(pt, "Get number of points")
    vals = [call(pt, "Get value at index", i + 1) for i in range(n)]
    return pt, [v for v in vals if v and v > 0]


def st_stats(vals):
    vals = sorted(vals)
    med = vals[len(vals) // 2]
    st = [12 * math.log2(v / med) for v in vals]
    mean = sum(st) / len(st)
    return med, math.sqrt(sum((x - mean) ** 2 for x in st) / len(st))


def measure(path, fmin=60, fmax=400):
    manip = call(parselmouth.Sound(path), "To Manipulation", 0.01, fmin, fmax)
    _, vals = pitch_points(manip)
    med, std = st_stats(vals)
    return {"median_hz": round(med, 1), "st_std": round(std, 2)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--measure", action="store_true")
    ap.add_argument("--target-std", type=float, default=2.6, help="target pitch std in semitones")
    ap.add_argument("--target-med", type=float, default=0, help="target median Hz (0 = keep the input's)")
    ap.add_argument("--k-max", type=float, default=1.4)
    ap.add_argument("--fmin", type=float, default=60)
    ap.add_argument("--fmax", type=float, default=400)
    ap.add_argument("--spans", default="[]")
    ap.add_argument("--stretch", type=float, default=1.0)
    ap.add_argument("--tail", type=float, default=1.0)
    a = ap.parse_args()
    if a.measure:
        for f in a.files:
            print(f, json.dumps(measure(f, a.fmin, a.fmax)))
        return
    src, dst = a.files
    snd = parselmouth.Sound(src)
    manip = call(snd, "To Manipulation", 0.01, a.fmin, a.fmax)
    pt, vals = pitch_points(manip)
    med, std = st_stats(vals)
    k = max(1.0, min(a.k_max, a.target_std / std)) if std > 0 else 1.0
    call(pt, "Formula", f"{a.target_med or med} * (self / {med}) ^ {k}")
    call([pt, manip], "Replace pitch tier")
    dur = snd.get_total_duration()
    dt = call("Create DurationTier", "dt", 0, dur)
    call(dt, "Add point", 0, 1.0)
    eps = 0.005
    for s, e in json.loads(a.spans):
        s, e = max(0.0, s), min(dur, e)
        if e - s < 0.05:
            continue
        mid = s + 0.6 * (e - s)
        for t, v in ((s - eps, 1.0), (s, a.stretch), (mid - eps, a.stretch), (mid, a.tail), (e, a.tail), (e + eps, 1.0)):
            if 0 <= t <= dur:
                call(dt, "Add point", t, v)
    call([dt, manip], "Replace duration tier")
    out = call(manip, "Get resynthesis (overlap-add)")
    out.save(dst, "WAV")
    print(json.dumps({"median_in": round(med, 1), "std_in": round(std, 2), "k": round(k, 3),
                      "dur_in": round(dur, 2), "dur_out": round(out.get_total_duration(), 2), "after": measure(dst, a.fmin, a.fmax)}))


if __name__ == "__main__":
    main()
