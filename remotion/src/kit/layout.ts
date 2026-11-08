import { useVideoConfig } from "remotion";

/** Size helpers so one component works in 16:9 and 9:16.
 *  `u` = 1 at a 1080-px short side. Safe areas follow common platform overlays:
 *  vertical video keeps captions above the bottom 23% (y <= 1480 at 1920 px, clear of app UI)
 *  and away from the right edge. */
export const useLayout = () => {
  const { width, height } = useVideoConfig();
  const vertical = height > width;
  const u = Math.min(width, height) / 1080;
  return {
    width,
    height,
    vertical,
    u,
    safe: vertical
      ? { top: height * 0.1, bottom: height * 0.23, left: width * 0.07, right: width * 0.12 }
      : { top: height * 0.06, bottom: height * 0.07, left: width * 0.05, right: width * 0.05 },
  };
};
