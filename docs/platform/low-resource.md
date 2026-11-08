# Low-resource machines (CPU-only, 8 cores, ~16–24 GB RAM)

- **One heavy job at a time.** TTS, ASR, Remotion render and Blender each use all cores; running two doubles the time of both and makes any timing measurement useless.
- **Remotion:** `concurrency: 1`, render one composition at a time, check stills before a full render.
- **TTS:** load the model once and synthesise all lines in one process. Kokoro is light; GPT-SoVITS peaks around 6–7 GB, BreezyVoice around 5–6 GB.
- **ASR:** faster-whisper `small` int8 is enough for QA checks; larger models only for final transcripts.
- **Blender:** EEVEE, low samples, half resolution for drafts; render every 10th frame first.
- **Long jobs:** run in the background and write a log (`... > build/job.log 2>&1 &`); terminals and agent sessions often time out after ~10 minutes.
- **Disk:** models live in caches outside the repo (`~/.cache/huggingface`, etc.) — see [`models/README.md`](../../models/README.md).
