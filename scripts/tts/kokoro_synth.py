#!/usr/bin/env python3
"""Synthesize narration lines with Kokoro-82M (CPU) from a project file.

    python scripts/tts/kokoro_synth.py examples/<example>/project.<lang>.json [--force] [--only 03,04]

Output (next to the project file):
    build/<lang>/vo/<id>.wav    mono 24 kHz, silence-trimmed, loudness -20 LUFS
    build/<lang>/timing.json    [{"id", "text", "dur"}]  (dur in seconds)
    build/<lang>/vo/manifest.json  per-line hash so unchanged lines are reused

Kokoro is deterministic for the same text/voice/speed, so no seed is needed.
Only Kokoro's built-in synthetic voices are used.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf

SR = 24000
TARGET_LUFS = -20.0
PEAK_CEILING = 10 ** (-1.0 / 20)  # -1 dBFS sample peak safety
TRIM_DB = -45.0  # frames quieter than this (relative to full scale) count as silence
PAD_S = 0.04     # keep a little air at both ends after trimming

# Kokoro picks its G2P from the voice prefix: a=US English, b=UK English,
# z=Mandarin, j=Japanese, e=Spanish, f=French, h=Hindi, i=Italian, p=Portuguese.
LANG_FROM_PREFIX = {"a", "b", "z", "j", "e", "f", "h", "i", "p"}


def log(msg: str) -> None:
    print(msg, flush=True)


def progress(repo_root: Path, msg: str) -> None:
    """Append a short line to build/PROGRESS.log at the repo root (best effort)."""
    try:
        p = repo_root / "build" / "PROGRESS.log"
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%H:%M')}] {msg}\n")
    except OSError:
        pass


def find_repo_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / ".git").exists() or (p / "scripts" / "tts").is_dir():
            return p
    return start


def trim_silence(audio: np.ndarray) -> np.ndarray:
    frame = int(0.01 * SR)
    if len(audio) < frame * 3:
        return audio
    n = len(audio) // frame
    rms = np.sqrt(np.mean(audio[: n * frame].reshape(n, frame) ** 2, axis=1) + 1e-12)
    db = 20 * np.log10(rms)
    voiced = np.where(db > TRIM_DB)[0]
    if len(voiced) == 0:
        return audio
    pad = int(PAD_S * SR)
    start = max(0, voiced[0] * frame - pad)
    end = min(len(audio), (voiced[-1] + 1) * frame + pad)
    return audio[start:end]


def normalize(audio: np.ndarray) -> tuple[np.ndarray, float]:
    import pyloudnorm as pyln

    meter = pyln.Meter(SR)
    loud = meter.integrated_loudness(audio)
    if not np.isfinite(loud):
        return audio, loud
    out = pyln.normalize.loudness(audio, loud, TARGET_LUFS)
    peak = float(np.max(np.abs(out)))
    if peak > PEAK_CEILING:
        # Rare for speech at -20 LUFS; scale down rather than clip.
        out = out * (PEAK_CEILING / peak)
    return out.astype(np.float32), loud


def line_hash(engine_cfg: dict, text: str) -> str:
    key = json.dumps({"tts": engine_cfg, "text": text, "v": 2}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]


def make_pipeline(voice: str):
    import torch
    from kokoro import KPipeline

    torch.set_num_threads(os.cpu_count() or 4)
    lang = voice[0]
    if lang not in LANG_FROM_PREFIX:
        sys.exit(f"Cannot infer Kokoro language from voice '{voice}'")
    if lang == "z":
        # misaki's zh G2P ignores en_callable for the v1.0 model (legacy path): Latin letters
        # reach the model as raw symbols. Lines with Latin words go through mixed_phonemes()
        # instead; pure-Chinese lines keep the stock pipeline path.
        en = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M", model=False)

        def en_callable(word: str) -> str:
            return next(en(word)).phonemes

        pipeline = KPipeline(lang_code="z", repo_id="hexgrad/Kokoro-82M", en_callable=en_callable)
        pipeline.en_g2p = en_callable
        return pipeline
    return KPipeline(lang_code=lang, repo_id="hexgrad/Kokoro-82M")


LATIN = re.compile(r"[A-Za-z][A-Za-z'-]*(?:\s+[A-Za-z][A-Za-z'-]*)*")


def mixed_phonemes(zh_g2p, en_g2p, text: str, lexicon: dict | None = None) -> str:
    """Phonemes for Mandarin text with Latin words: Chinese runs via the zh G2P, each Latin
    run via `lexicon` (exact phoneme override, e.g. {"Verdalo": "vɜɹdˈɑlO"}) or the English G2P."""
    lexicon = lexicon or {}
    parts, pos = [], 0
    for m in LATIN.finditer(text):
        parts.append(zh_g2p(text[pos:m.start()]))
        word = m.group(0)
        parts.append(lexicon.get(word) or en_g2p(word))
        pos = m.end()
    parts.append(zh_g2p(text[pos:]))
    return " ".join(p.strip() for p in parts if p and p.strip())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project", type=Path)
    ap.add_argument("--force", action="store_true", help="re-synthesize every line")
    ap.add_argument("--only", default="", help="comma-separated line ids to (re)synthesize")
    args = ap.parse_args()

    project_path = args.project.resolve()
    proj = json.loads(project_path.read_text(encoding="utf-8"))
    tts = proj["tts"]
    if tts.get("engine", "kokoro") != "kokoro":
        sys.exit(f"This script only handles engine 'kokoro' (got {tts.get('engine')!r})")
    voice, speed = tts["voice"], float(tts.get("speed", 1.0))
    lexicon = tts.get("lexicon") or {}  # optional {"LatinWord": "phonemes"} for zh voices

    out_dir = project_path.parent / "build" / proj["lang"]
    vo_dir = out_dir / "vo"
    vo_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = vo_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    only = {s.strip() for s in args.only.split(",") if s.strip()}
    repo_root = find_repo_root(project_path.parent)

    pipeline = None
    timing = []
    t0 = time.time()
    for i, line in enumerate(proj["lines"], 1):
        lid, text = line["id"], line["text"]
        wav = vo_dir / f"{lid}.wav"
        mixed = voice[0] == "z" and bool(LATIN.search(text))
        cfg = {"voice": voice, "speed": speed}
        if mixed:  # new G2P path for these lines only; pure-Chinese hashes stay unchanged
            cfg.update(g2p="mixed-v1", lexicon={k: v for k, v in lexicon.items() if k in text})
        h = line_hash(cfg, text)
        reuse = wav.exists() and manifest.get(lid) == h and not args.force and (not only or lid not in only)
        if not reuse:
            if pipeline is None:
                log(f"loading Kokoro (voice {voice}, {os.cpu_count()} CPU threads)")
                pipeline = make_pipeline(voice)
            if mixed:
                ps = mixed_phonemes(lambda t: pipeline.g2p(t)[0], pipeline.en_g2p, text, lexicon)
                results = pipeline.generate_from_tokens(ps, voice=voice, speed=speed)
            else:
                results = pipeline(text, voice=voice, speed=speed, split_pattern=r"\n+")
            chunks = [np.asarray(r.audio, dtype=np.float32) for r in results if r.audio is not None]
            if not chunks:
                sys.exit(f"line {lid}: Kokoro returned no audio")
            audio = trim_silence(np.concatenate(chunks))
            audio, raw_lufs = normalize(audio)
            sf.write(wav, audio, SR, subtype="PCM_16")
            manifest[lid] = h
            log(f"  [{i}/{len(proj['lines'])}] {lid}: {len(audio)/SR:.2f}s (raw {raw_lufs:.1f} LUFS -> {TARGET_LUFS})")
        else:
            log(f"  [{i}/{len(proj['lines'])}] {lid}: unchanged, reused")
        dur = sf.info(wav).frames / SR
        timing.append({"id": lid, "text": text, "dur": round(dur, 3)})

    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (out_dir / "timing.json").write_text(json.dumps(timing, ensure_ascii=False, indent=2), encoding="utf-8")
    total = sum(t["dur"] for t in timing)
    log(f"done: {len(timing)} lines, {total:.1f}s of speech, {time.time()-t0:.0f}s wall -> {out_dir/'timing.json'}")
    progress(repo_root, f"tts {proj['id']} done ({total:.1f}s speech)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
