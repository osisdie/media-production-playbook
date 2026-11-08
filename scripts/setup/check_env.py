#!/usr/bin/env python3
"""Cross-platform environment report for the media production playbook.

Prints which tools are available (Python, Node, ffmpeg, espeak-ng, Blender,
Python packages, Remotion install, font, cached models). Exits 0 always:
it is a report, not a gate. Use --strict to exit 1 when a required tool is
missing.

    python scripts/setup/check_env.py [--strict]
"""
from __future__ import annotations

import importlib.util
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def run(cmd: list[str]) -> str | None:
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return None
    text = (out.stdout or out.stderr).strip()
    return text.splitlines()[0] if text else ""


def tool(name: str, args: list[str]) -> tuple[bool, str]:
    path = shutil.which(name)
    if not path:
        return False, "not found"
    return True, run([path, *args]) or path


def is_wsl() -> bool:
    try:
        return "microsoft" in Path("/proc/version").read_text().lower()
    except OSError:
        return False


def main() -> int:
    strict = "--strict" in sys.argv
    rows: list[tuple[str, bool, str, bool]] = []  # name, ok, detail, required

    osname = platform.system() + (" (WSL)" if is_wsl() else "")
    print(f"OS: {osname} {platform.release()} | CPU cores: {os.cpu_count()}")

    py_ok = (3, 10) <= sys.version_info[:2] <= (3, 12)
    rows.append(("python (3.10-3.12 for Kokoro)", py_ok, sys.version.split()[0], True))
    rows.append(("node", *tool("node", ["--version"]), True))
    rows.append(("ffmpeg", *tool("ffmpeg", ["-version"]), True))
    rows.append(("ffprobe", *tool("ffprobe", ["-version"]), True))
    rows.append(("espeak-ng (optional; misaki bundles a copy)", *tool("espeak-ng", ["--version"]), False))

    for mod, req in [("kokoro", True), ("misaki", True), ("soundfile", True),
                     ("pyloudnorm", True), ("faster_whisper", False), ("torch", True)]:
        ok = importlib.util.find_spec(mod) is not None
        rows.append((f"python pkg: {mod}", ok, "installed" if ok else "missing", req))

    rem = REPO / "remotion" / "node_modules" / "remotion" / "package.json"
    rows.append(("remotion (npm ci in remotion/)", rem.exists(),
                 "installed" if rem.exists() else "run setup", True))
    font = REPO / "remotion" / "public" / "fonts" / "NotoSansTC.ttf"
    rows.append(("font Noto Sans TC", font.exists(), "present" if font.exists() else "run setup", True))

    hf = Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface")) / "hub"
    for repo, req in [("models--hexgrad--Kokoro-82M", True), ("models--Systran--faster-whisper-small", False)]:
        ok = (hf / repo).exists()
        rows.append((f"model cache: {repo.split('--', 1)[1].replace('--', '/')}", ok,
                     "cached" if ok else "downloads on first use", req))

    blender = REPO / "scripts" / "blender" / "find_blender.sh"
    b_detail = "not found (optional)"
    b_ok = False
    if shutil.which("bash") and blender.exists():
        found = run(["bash", str(blender)])
        if found:
            b_ok, b_detail = True, found
    rows.append(("blender (optional 3D)", b_ok, b_detail, False))

    width = max(len(r[0]) for r in rows)
    missing_required = False
    for name, ok, detail, req in rows:
        mark = "ok " if ok else ("MISSING" if req else "-  ")
        if not ok and req:
            missing_required = True
        print(f"  [{mark:^7}] {name:<{width}}  {detail}")

    if missing_required:
        print("\nSome required items are missing: run scripts/setup/setup-linux-wsl.sh or setup-macos.sh")
    return 1 if (strict and missing_required) else 0


if __name__ == "__main__":
    sys.exit(main())
