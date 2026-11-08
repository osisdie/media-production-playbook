import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import type { Theme } from "./theme";
import { FONT_FAMILY } from "./theme";
import { enter, rise } from "./anim";
import { useLayout } from "./layout";

export const TitleCard: React.FC<{ theme: Theme; eyebrow?: string; title: string; subtitle?: string; icon?: React.ReactNode }> = ({
  theme, eyebrow, title, subtitle, icon,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { u, vertical } = useLayout();
  const p = [0, 6, 12, 18].map((d) => enter(frame, fps, d));
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", fontFamily: FONT_FAMILY, color: theme.ink, textAlign: "center", paddingBottom: (vertical ? 300 : 140) * u }}>
      {icon ? <div style={{ ...rise(p[0], 30 * u), marginBottom: 28 * u }}>{icon}</div> : null}
      {eyebrow ? (
        <div style={{ ...rise(p[1], 24 * u), fontSize: 30 * u, fontWeight: 700, letterSpacing: 6 * u, textTransform: "uppercase", color: theme.accent, marginBottom: 18 * u }}>
          {eyebrow}
        </div>
      ) : null}
      <div style={{ ...rise(p[2], 40 * u), fontSize: (vertical ? 96 : 110) * u, fontWeight: 800, lineHeight: 1.1, maxWidth: (vertical ? 900 : 1500) * u, whiteSpace: "pre-line", textWrap: "balance" } as React.CSSProperties}>
        {title}
      </div>
      {subtitle ? (
        <div style={{ ...rise(p[3], 24 * u), marginTop: 28 * u, fontSize: 40 * u, fontWeight: 500, color: theme.inkSoft }}>{subtitle}</div>
      ) : null}
    </AbsoluteFill>
  );
};
