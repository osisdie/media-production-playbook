#!/usr/bin/env node
// Render one example/language with Remotion.
//
//   node scripts/video/render.mjs --project examples/<example>/project.<lang>.json [--silent] [--frames 0-90]
//
// 1. copies build/<lang>/vo/*.wav into remotion/public/generated/<project id>/vo/ (gitignored)
// 2. copies the Blender opening (if the project asks for one and it has been rendered)
// 3. bundles remotion/src and renders the composition named in project.video.composition
//    with concurrency 1 (low-resource friendly) to examples/<example>/build/<lang>/render.mp4
// scripts/video/post.sh then does loudness normalisation and the final encode.
import { mkdirSync } from "node:fs";
import path from "node:path";
import { bundleAndSelect, loadRemotion, parseArgs, prepareInputs, progressLog, repo } from "./lib.mjs";

const { opt, flag } = parseArgs(process.argv.slice(2));
const projectArg = opt("--project");
if (!projectArg) {
  console.error("usage: node scripts/video/render.mjs --project examples/<example>/project.<lang>.json [--silent] [--frames a-b]");
  process.exit(2);
}

let prepared;
try {
  prepared = prepareInputs(projectArg, { silent: flag("--silent") });
} catch (e) {
  console.error(e.message);
  process.exit(1);
}
const { project, buildDir, inputProps } = prepared;
const { serveUrl, composition } = await bundleAndSelect(project, inputProps);
const { renderMedia } = await loadRemotion("@remotion/renderer");

const framesArg = opt("--frames");
const frameRange = framesArg ? framesArg.split("-").map(Number) : null;
mkdirSync(buildDir, { recursive: true });
const outputLocation = path.join(buildDir, "render.mp4");
console.log(`rendering ${composition.id}: ${composition.width}x${composition.height} @ ${composition.fps} fps, ` +
  `${composition.durationInFrames} frames (${(composition.durationInFrames / composition.fps).toFixed(1)} s)`);
progressLog(`render ${project.id} start (${composition.durationInFrames} frames)`);

let lastStep = -1;
const started = Date.now();
await renderMedia({
  serveUrl,
  composition,
  inputProps,
  codec: "h264",
  crf: 16,
  audioCodec: "aac",
  pixelFormat: "yuv420p",
  colorSpace: "bt709",
  concurrency: 1,
  frameRange: frameRange ? [frameRange[0], frameRange[1]] : null,
  outputLocation,
  overwrite: true,
  onProgress: ({ progress }) => {
    const step = Math.floor(progress * 10);
    if (step !== lastStep) {
      lastStep = step;
      console.log(`  ${step * 10}%`);
      if (step > 0 && step < 10) progressLog(`render ${project.id} ${step * 10}%`);
    }
  },
});
const secs = ((Date.now() - started) / 1000).toFixed(0);
console.log(`done in ${secs}s -> ${path.relative(repo, outputLocation)}`);
progressLog(`render ${project.id} done (${secs}s)`);
