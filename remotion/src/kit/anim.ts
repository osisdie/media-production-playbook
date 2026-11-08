import { interpolate, spring } from "remotion";

/** Spring-in progress 0..1 starting at `delay` frames. */
export const enter = (frame: number, fps: number, delay = 0) =>
  spring({ frame: frame - delay, fps, config: { damping: 200, mass: 0.6 } });

/** Common "rise and fade in" style. */
export const rise = (p: number, dist: number) => ({
  opacity: p,
  transform: `translateY(${interpolate(p, [0, 1], [dist, 0])}px)`,
});
