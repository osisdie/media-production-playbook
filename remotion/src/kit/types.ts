// Shapes shared by every example. They mirror examples/<example>/project.<lang>.json
// and build/<lang>/timing.json (written by scripts/tts/kokoro_synth.py).

export type Visual = Record<string, unknown> & { kind: string };

export type Line = {
  id: string;
  text: string; // what the TTS engine reads
  qa_text?: string; // optional: what ASR should hear, when `text` uses a phonetic spelling
  caption: string[]; // what the viewer reads (may differ from text)
  scene?: string;
  visual?: Visual;
};

export type Project = {
  id: string;
  example: string;
  lang: string;
  tts: { engine: string; voice: string; speed?: number };
  video: { composition: string; width: number; height: number; fps: number };
  design?: Record<string, unknown>;
  lines: Line[];
};

export type TimingEntry = { id: string; text: string; dur: number };

// Props passed to every example composition (by scripts/video/render.mjs).
export type ExampleProps = {
  project: Project;
  timing: TimingEntry[] | null; // null in Studio before TTS has run -> estimated
  audioBase: string | null; // public/ path holding <id>.wav, null = silent preview
  opening3d: string | null; // public/ path of the alpha video, null = 2D fallback
};
