// Shot timing shared by the Remotion compositions (via timeline.ts) and by Node scripts
// such as scripts/video/stills.mjs. Plain JavaScript (ESM) so both can import it.

export const TRANSITION_FRAMES = 6;

/** Seconds of picture around each narration line. */
export const DEFAULT_PACING = { lead: 0.25, tail: 0.45, firstLead: 0.35, lastHold: 1.4 };

/** Rough speech-rate estimate (seconds) so previews work before TTS has run. */
export const estimate = (text) => {
  const cjk = (text.match(/[㐀-鿿]/g) || []).length;
  const words = text.replace(/[㐀-鿿]/g, " ").split(/\s+/).filter(Boolean).length;
  return Math.max(1.2, cjk / 4.6 + words / 2.7);
};

/** Shot length = line duration + breathing room. Shots butt-join; the 6-frame crossfade is
 *  drawn on top of the next shot's first frames.
 *  @returns {{ shots: {index:number, from:number, duration:number, audioFrom:number, audioFrames:number}[], total:number }} */
export const computeShots = (lines, timing, fps, pacing = DEFAULT_PACING) => {
  const durOf = new Map((timing || []).map((t) => [t.id, t.dur]));
  let cursor = 0;
  const shots = lines.map((line, index) => {
    const dur = durOf.has(line.id) ? durOf.get(line.id) : estimate(line.text);
    const lead = pacing.lead + (index === 0 ? pacing.firstLead : 0);
    const tail = pacing.tail + (index === lines.length - 1 ? pacing.lastHold : 0);
    const audioFrames = Math.ceil(dur * fps);
    const duration = Math.round(lead * fps) + audioFrames + Math.round(tail * fps);
    const shot = { index, from: cursor, duration, audioFrom: cursor + Math.round(lead * fps), audioFrames };
    cursor += duration;
    return shot;
  });
  return { shots, total: cursor };
};
