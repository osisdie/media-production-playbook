// Shared helpers for render.mjs and stills.mjs.
import { appendFileSync, copyFileSync, existsSync, mkdirSync, readFileSync, rmSync } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
export const repo = path.resolve(here, "..", "..");
export const remotionDir = path.join(repo, "remotion");

export const parseArgs = (argv) => {
  const opt = (name) => {
    const i = argv.indexOf(name);
    return i >= 0 ? argv[i + 1] : undefined;
  };
  return { opt, flag: (name) => argv.includes(name) };
};

/** Append "[HH:MM] msg" to build/PROGRESS.log at the repo root (best effort). */
export const progressLog = (msg) => {
  const t = new Date().toTimeString().slice(0, 5);
  try {
    mkdirSync(path.join(repo, "build"), { recursive: true });
    appendFileSync(path.join(repo, "build", "PROGRESS.log"), `[${t}] ${msg}\n`);
  } catch {
    /* best effort */
  }
};

/** Read the project, copy narration + optional 3D opening into remotion/public/generated,
 *  and return the composition input props. */
export const prepareInputs = (projectArg, { silent = false } = {}) => {
  const projectPath = path.resolve(projectArg);
  const exampleDir = path.dirname(projectPath);
  const project = JSON.parse(readFileSync(projectPath, "utf8"));
  const buildDir = path.join(exampleDir, "build", project.lang);
  // Only this project's folder under public/generated is refreshed; other projects' copies
  // are left alone (they are small, gitignored, and may belong to a render in progress).
  const genDir = path.join(remotionDir, "public", "generated");
  mkdirSync(genDir, { recursive: true });

  let timing = null;
  let audioBase = null;
  const timingPath = path.join(buildDir, "timing.json");
  if (existsSync(timingPath)) {
    timing = JSON.parse(readFileSync(timingPath, "utf8"));
  } else if (!silent) {
    throw new Error(`missing ${path.relative(repo, timingPath)} — run scripts/tts/kokoro_synth.py first (or pass --silent)`);
  }
  if (!silent) {
    const rel = `generated/${project.id}/vo`;
    const dst = path.join(remotionDir, "public", rel);
    rmSync(dst, { recursive: true, force: true });
    mkdirSync(dst, { recursive: true });
    for (const line of project.lines) {
      const src = path.join(buildDir, "vo", `${line.id}.wav`);
      if (!existsSync(src)) throw new Error(`missing narration ${path.relative(repo, src)}`);
      copyFileSync(src, path.join(dst, `${line.id}.wav`));
    }
    audioBase = rel;
  }

  // Optional 3D opening rendered by examples/blender-demo (2D fallback when absent).
  let opening3d = null;
  const wanted = project.design && project.design.opening3d;
  if (wanted) {
    const src = path.join(repo, "examples", "blender-demo", "out", path.basename(wanted));
    if (existsSync(src)) {
      const dst = path.join(genDir, wanted);
      mkdirSync(path.dirname(dst), { recursive: true });
      copyFileSync(src, dst);
      opening3d = `generated/${wanted}`;
      console.log(`3D opening: ${path.relative(repo, src)}`);
    } else {
      console.log("3D opening not rendered — using the 2D opening (run examples/blender-demo/run.sh to add it)");
    }
  }
  return { project, buildDir, inputProps: { project, timing, audioBase, opening3d } };
};

const req = createRequire(path.join(remotionDir, "package.json"));
/** Import a package from remotion/node_modules (this script lives outside that folder). */
export const loadRemotion = async (name) => import(pathToFileURL(req.resolve(name)).href);

export const bundleAndSelect = async (project, inputProps) => {
  const { bundle } = await loadRemotion("@remotion/bundler");
  const { selectComposition } = await loadRemotion("@remotion/renderer");
  console.log(`bundling remotion/src for ${project.video.composition} ...`);
  const serveUrl = await bundle({
    entryPoint: path.join(remotionDir, "src", "index.ts"),
    rootDir: remotionDir,
    publicDir: path.join(remotionDir, "public"),
  });
  const composition = await selectComposition({ serveUrl, id: project.video.composition, inputProps });
  return { serveUrl, composition };
};
