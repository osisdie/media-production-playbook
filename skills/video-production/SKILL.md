---
name: video-production
description: Use when making a 16:9 course video or a 9:16 promo with Remotion on a low-resource machine — narration-driven shot timing, hard-coded captions in a safe area, mock UI instead of screen recordings, optional Blender 3D shots, ffmpeg loudness post-processing (−14 LUFS, TP −1.5) and a still-frame review.
---

# Video production (Remotion + optional Blender)

Playbooks: `docs/playbooks/course-video.md`, `docs/playbooks/promo-video.md`, `docs/playbooks/blender-in-pipeline.md`, `docs/playbooks/beat-synced-launch-video.md` (beat grid shared by music, edit and 3D). Working examples: `examples/course-demo`, `examples/promo-demo`, `examples/blender-demo`.

1. Write a TTS-friendly script (`prompts/tts-script-writing.md`) as `project.<lang>.json`.
2. Synthesise and QA the narration first (skill: narration-qa). Shot lengths come from the narration.
3. Build shots from reusable components in `remotion/src/kit/`; captions as fixed line arrays, content above the caption band.
4. Render one composition at a time (`concurrency: 1`), then `scripts/video/post.sh`.
5. Check: ffprobe spec, ebur128 loudness, a contact sheet of stills (captions, clipped text, single-character lines, masked secrets), and the narration QA list.

Rules: no real brands/people/prices in mock screens; API keys always masked; one heavy job at a time; re-render only what changed but re-check stills of every video that shares a changed component.
