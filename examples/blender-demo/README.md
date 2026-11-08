# blender-demo — procedural 3D turntable (optional)

A stylised plant pot with leaves and an extruded **Verdalo** wordmark, built entirely in
code by `scripts/blender/render_scene.py` (no downloaded assets). 6 s seamless loop at
30 fps, transparent background, EEVEE with low samples so it runs on integrated GPUs.

```bash
bash examples/blender-demo/run.sh               # EEVEE, 16 samples
SAMPLES=32 bash examples/blender-demo/run.sh    # smoother
ENGINE=cycles SAMPLES=64 bash examples/blender-demo/run.sh   # CPU path tracing (slow)
```

Outputs (`out/`, gitignored):

| File | What |
|---|---|
| `verdalo-turntable-9x16.webm` | 1080×1920 VP9 **with alpha** — used as the opening shot of `promo-demo` |
| `verdalo-turntable-9x16.mp4` | same, on a solid background, for a quick look |
| `blender-demo-16x9.mp4` | 1920×1080 standalone loop, H.264 |

Set `ALPHA_MOV=1` to also write a ProRes 4444 `.mov` with alpha for desktop editors.

**Finding Blender** (`scripts/blender/find_blender.sh`): `$BLENDER` → macOS
`/Applications/Blender.app` → `blender` on `PATH` → on WSL, a portable Windows build in
`%USERPROFILE%\tools\blender-*\` → the Microsoft Store launcher
`%LOCALAPPDATA%\Microsoft\WindowsApps\blender-launcher.exe`. The Store launcher detaches from
the console, so `scripts/blender/run_blender.sh` waits for a `.done` marker file that the
render script writes. If no Blender is found, `run.sh` exits cleanly and `promo-demo` uses
its 2D opening.
