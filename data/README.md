# data

Narration scripts live inside each example's project file
(`examples/<example>/project.<lang>.json`, field `lines[]`), because text, captions and
on-screen visuals are edited together. `project-template.json` here is a starting point for
a new production: copy it to `examples/<new>/project.<lang>.json` and fill it in.

Field reference:

| Field | Meaning |
|---|---|
| `id` | unique id, e.g. `my-video-en` (also the folder name under `remotion/public/generated/`) |
| `tts.engine` / `voice` / `speed` | `kokoro`, a built-in voice id, 1.0 = normal |
| `video.composition` | Remotion composition id registered in `remotion/src/Root.tsx` |
| `lines[].text` | what the TTS engine reads — short clauses, numbers spelled out |
| `lines[].caption` | 1–2 caption lines the viewer reads (may use numerals) |
| `lines[].scene` | a note for whoever edits the visuals |
| `lines[].visual` | optional layout data the composition understands (`kind` + fields) |
| `design` | optional per-video settings (stage names, brand, 3D opening path) |
