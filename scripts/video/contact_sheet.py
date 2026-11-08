#!/usr/bin/env python3
"""Frame checks: tile evenly spaced frames of a video into one PNG.

    python scripts/video/contact_sheet.py <video> [--tiles 12] [--cols 4] [--width 480] [--out sheet.png]
    python scripts/video/contact_sheet.py <video> --at 1.0,5.5,12   # specific times (seconds)

Look at the sheet for: captions inside the frame, no clipped or overflowing text,
correct fonts (no tofu boxes), transitions not caught mid-fade on every tile.
Only needs ffmpeg/ffprobe; no Python packages.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path


def probe(video: Path) -> tuple[float, int, int]:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height:format=duration", "-of", "json", str(video)],
        capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    st = j["streams"][0]
    return float(j["format"]["duration"]), int(st["width"]), int(st["height"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("video", type=Path)
    ap.add_argument("--tiles", type=int, default=12)
    ap.add_argument("--cols", type=int, default=0, help="default: 4 for landscape, 6 for portrait")
    ap.add_argument("--width", type=int, default=0, help="tile width in px (default 480 / 270)")
    ap.add_argument("--at", default="", help="comma-separated times in seconds instead of even spacing")
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()

    dur, w, h = probe(a.video)
    portrait = h > w
    cols = a.cols or (6 if portrait else 4)
    tw = a.width or (270 if portrait else 480)
    if a.at:
        times = [float(t) for t in a.at.split(",") if t.strip()]
    else:
        n = a.tiles
        times = [dur * (i + 0.5) / n for i in range(n)]
    rows = math.ceil(len(times) / cols)
    out = a.out or a.video.with_name(a.video.stem + "-sheet.png")

    with tempfile.TemporaryDirectory() as tmp:
        frames = []
        for i, t in enumerate(times):
            f = Path(tmp) / f"f{i:03d}.png"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(a.video),
                            "-frames:v", "1", "-vf", f"scale={tw}:-2", str(f)], check=True)
            frames.append(f)
        # pad to a full grid with the last frame so xstack has every cell
        while len(frames) < rows * cols:
            frames.append(frames[-1])
        inputs = []
        for f in frames:
            inputs += ["-i", str(f)]
        th = round(tw * h / w / 2) * 2
        layout = "|".join(f"{(i % cols) * tw}_{(i // cols) * th}" for i in range(len(frames)))
        subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex",
                        f"xstack=inputs={len(frames)}:layout={layout}:fill=black", str(out)], check=True)
    print(f"{out}  ({len(times)} frames at " + ", ".join(f"{t:.1f}s" for t in times) + ")")
    return 0


if __name__ == "__main__":
    sys.exit(main())
