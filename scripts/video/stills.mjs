#!/usr/bin/env node
// Quick layout check without a full render: one PNG per shot (taken just after the
// voice ends, when every element has animated in) into build/<lang>/stills/.
//
//   node scripts/video/stills.mjs --project examples/<example>/project.<lang>.json [--frames 12,240] [--scale 0.5]
//
// Works before TTS too (uses estimated durations, no audio needed).
import { mkdirSync } from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { bundleAndSelect, loadRemotion, parseArgs, prepareInputs, remotionDir, repo } from "./lib.mjs";

const { opt } = parseArgs(process.argv.slice(2));
const projectArg = opt("--project");
if (!projectArg) {
  console.error("usage: node scripts/video/stills.mjs --project examples/<example>/project.<lang>.json [--frames a,b] [--scale 0.5]");
  process.exit(2);
}
// Stills never need audio; timing.json is still used when present so frames match the real render.
const { project, buildDir, inputProps } = prepareInputs(projectArg, { silent: true });

const { serveUrl, composition } = await bundleAndSelect(project, inputProps);
const { renderStill } = await loadRemotion("@remotion/renderer");

// Default frames: each shot's end minus 8 frames (everything has animated in, the caption is
// still up). Shot boundaries come from the same pacing module the compositions use.
const { computeShots } = await import(pathToFileURL(path.join(remotionDir, "src", "kit", "pacing.mjs")).href);
let frames;
if (opt("--frames")) {
  frames = opt("--frames").split(",").map(Number);
} else {
  const { shots } = computeShots(project.lines, inputProps.timing, composition.fps);
  frames = shots.map((s) => Math.min(s.from + s.duration - 8, composition.durationInFrames - 1));
}
const outDir = path.join(buildDir, "stills");
mkdirSync(outDir, { recursive: true });
const scale = Number(opt("--scale") ?? 0.5);
for (const frame of frames) {
  const output = path.join(outDir, `frame-${String(frame).padStart(5, "0")}.png`);
  await renderStill({ serveUrl, composition, inputProps, frame, output, scale, overwrite: true });
  console.log(path.relative(repo, output));
}
