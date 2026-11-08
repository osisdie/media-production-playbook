#!/usr/bin/env python3
"""Delivery check for final videos: format and loudness.

    python scripts/video/check_output.py examples/*/out/*.mp4 [--fps 30] [--lufs -14] [--tp -1.5]

Checks: H.264 High, yuv420p, BT.709 tags, expected fps; if there is audio, AAC 48 kHz, integrated loudness
within ±1 LU of the target and true peak at or below the ceiling (+0.1 dB tolerance), measured
with ffmpeg's ebur128 filter. Exits 1 if any file fails. Needs only ffmpeg/ffprobe.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys


def probe(path: str) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def loudness(path: str) -> tuple[float, float]:
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-vn",
                          "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    summary = err[err.rfind("Summary:"):]
    i = float(re.search(r"I:\s+(-?[\d.]+) LUFS", summary).group(1))
    tp = float(re.search(r"Peak:\s+(-?[\d.]+|-inf) dBFS", summary).group(1))
    return i, tp


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--fps", type=float, default=30)
    ap.add_argument("--lufs", type=float, default=-14)
    ap.add_argument("--tp", type=float, default=-1.5)
    a = ap.parse_args()
    ok_all = True
    for f in a.files:
        j = probe(f)
        v = next(s for s in j["streams"] if s["codec_type"] == "video")
        au = next((s for s in j["streams"] if s["codec_type"] == "audio"), None)
        num, den = (int(x) for x in v["r_frame_rate"].split("/"))
        fps = num / den
        silent = au is None  # e.g. the Blender loop: no audio checks
        i, tp = (float("nan"), float("nan")) if silent else loudness(f)
        checks = {
            "h264 High": v["codec_name"] == "h264" and v.get("profile") == "High",
            "yuv420p": v.get("pix_fmt") == "yuv420p",
            "bt709": v.get("color_primaries") == "bt709" and v.get("color_transfer") == "bt709",
            f"{a.fps:g} fps": abs(fps - a.fps) < 0.01,
        }
        if not silent:
            checks["aac 48k"] = au["codec_name"] == "aac" and au.get("sample_rate") == "48000"
            checks[f"I {a.lufs:g}±1"] = abs(i - a.lufs) <= 1.0
            checks[f"TP<={a.tp:g}"] = tp <= a.tp + 0.1
        ok = all(checks.values())
        ok_all &= ok
        dur = float(j["format"]["duration"])
        print(f"{'PASS' if ok else 'FAIL'}  {f}")
        print(f"      {v['width']}x{v['height']} {fps:g} fps {v['codec_name']} {v.get('profile')} {v.get('pix_fmt')} "
              f"{v.get('color_primaries')} | {au['codec_name'] if au else '-'} {au.get('sample_rate') if au else ''} Hz | "
              f"{dur:.1f} s | " + ("no audio" if silent else f"I {i:.1f} LUFS, TP {tp:.1f} dBTP"))
        bad = [k for k, val in checks.items() if not val]
        if bad:
            print("      failed: " + ", ".join(bad))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
