# Low-resource machines (CPU-only, 8 cores, ~16–24 GB RAM)

- **One heavy job at a time.** TTS, ASR, Remotion render and Blender each use all cores; running two doubles the time of both and makes any timing measurement useless.
- **Remotion:** `concurrency: 1`, render one composition at a time, check stills before a full render.
- **TTS:** load the model once and synthesise all lines in one process. Kokoro is light; GPT-SoVITS peaks around 6–7 GB, BreezyVoice around 5–6 GB.
- **ASR:** faster-whisper `small` int8 is enough for QA checks; larger models only for final transcripts.
- **Blender:** EEVEE, low samples, half resolution for drafts; render every 10th frame first.
- **Sharing one heavy-job lock** between several jobs or agents (`flock heavy.lock <cmd>`): flock is not first-come-first-served — long renders can grab it back-to-back and starve short critical-path jobs. Let long jobs yield between chunks, or use a reservation marker. Don't run `pgrep -f`/`pkill -f` inline with the pattern you're matching (it matches your own shell). Details: [beat-synced-launch-video](../playbooks/beat-synced-launch-video.md#team-orchestration--多個-agent工作並行時).
- **ACE-Step / bf16 on CPU:** check for AVX512-BF16/AMX first; without it bf16 is emulated and slower than fp32.
- **Long jobs:** run in the background and write a log (`... > build/job.log 2>&1 &`); terminals and agent sessions often time out after ~10 minutes.
- **Disk:** models live in caches outside the repo (`~/.cache/huggingface`, etc.) — see [`models/README.md`](../../models/README.md).
