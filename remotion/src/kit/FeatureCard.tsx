import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import type { Theme } from "./theme";
import { FONT_FAMILY } from "./theme";
import { enter, rise } from "./anim";
import { ICONS } from "./Icons";
import { useLayout } from "./layout";

/** Icon + title + one-line body on a rounded card. */
export const FeatureCard: React.FC<{ theme: Theme; icon: string; title: string; body: string; delay?: number }> = ({
  theme, icon, title, body, delay = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { u } = useLayout();
  const p = enter(frame, fps, delay);
  const Icon = ICONS[icon] ?? ICONS.leaf;
  return (
    <div style={{ ...rise(p, 40 * u), display: "flex", alignItems: "center", gap: 28 * u, background: theme.card, color: theme.cardInk,
                  borderRadius: 36 * u, padding: `${30 * u}px ${38 * u}px`, boxShadow: `0 ${20 * u}px ${60 * u}px rgba(0,0,0,0.25)`, fontFamily: FONT_FAMILY }}>
      <div style={{ width: 104 * u, height: 104 * u, borderRadius: 28 * u, background: theme.accent, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
        <Icon size={62 * u} color={theme.cardInk} stroke={1.8} />
      </div>
      <div>
        <div style={{ fontSize: 48 * u, fontWeight: 800, lineHeight: 1.15 }}>{title}</div>
        <div style={{ fontSize: 32 * u, fontWeight: 500, opacity: 0.72, marginTop: 6 * u }}>{body}</div>
      </div>
    </div>
  );
};
