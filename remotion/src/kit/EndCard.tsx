import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import type { Theme } from "./theme";
import { FONT_FAMILY } from "./theme";
import { enter, rise } from "./anim";
import { useLayout } from "./layout";

/** Closing card: big title or wordmark, tagline and an optional call-to-action pill. */
export const EndCard: React.FC<{ theme: Theme; title: React.ReactNode; tagline?: string; cta?: string }> = ({ theme, title, tagline, cta }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { u, vertical } = useLayout();
  const p = [0, 8, 16].map((d) => enter(frame, fps, d));
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", textAlign: "center", fontFamily: FONT_FAMILY, color: theme.ink, paddingBottom: (vertical ? 320 : 140) * u }}>
      <div style={{ ...rise(p[0], 30 * u), transform: `scale(${0.9 + 0.1 * p[0]})` }}>{title}</div>
      {tagline ? <div style={{ ...rise(p[1], 24 * u), marginTop: 26 * u, fontSize: (vertical ? 50 : 46) * u, fontWeight: 600, color: theme.inkSoft, maxWidth: 900 * u }}>{tagline}</div> : null}
      {cta ? (
        <div style={{ ...rise(p[2], 24 * u), marginTop: 46 * u, padding: `${20 * u}px ${48 * u}px`, borderRadius: 999, background: theme.accent2, color: "#1A1A1A", fontSize: 40 * u, fontWeight: 800 }}>
          {cta}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};
