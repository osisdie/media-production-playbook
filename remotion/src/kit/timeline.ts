import type { Line, TimingEntry } from "./types";
// Shared with Node scripts (scripts/video/stills.mjs), hence plain JS (.mjs).
import { computeShots, DEFAULT_PACING as PACING, estimate as estimateJs, TRANSITION_FRAMES as TF } from "./pacing.mjs";

export const TRANSITION_FRAMES: number = TF;

export type Shot = {
  line: Line;
  index: number;
  from: number; // first frame of the shot
  duration: number; // frames until the next shot starts
  audioFrom: number; // absolute frame where the narration starts
  audioFrames: number;
};

export type Pacing = {
  lead: number; // seconds of picture before the voice starts
  tail: number; // breathing room after the voice ends
  firstLead: number; // extra lead-in on the first shot
  lastHold: number; // extra hold on the final shot (end card)
};

export const DEFAULT_PACING: Pacing = PACING;
export const estimate: (text: string) => number = estimateJs;

/** Shot length = line duration + breathing room; see pacing.mjs. */
export function buildShots(lines: Line[], timing: TimingEntry[] | null, fps: number,
                           pacing: Pacing = DEFAULT_PACING): { shots: Shot[]; total: number } {
  const { shots, total } = computeShots(lines, timing, fps, pacing);
  return { shots: shots.map((s) => ({ ...s, line: lines[s.index] })), total };
}
