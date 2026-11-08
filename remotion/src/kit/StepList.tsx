import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import type { Theme } from "./theme";
import { FONT_FAMILY } from "./theme";
import { useLayout } from "./layout";

/** Numbered list of stages; the active one is highlighted, finished ones are dimmed with a tick. */
export const StepList: React.FC<{ theme: Theme; steps: string[]; active: number; label?: string }> = ({ theme, steps, active, label }) => {
  const frame = useCurrentFrame();
  const { u } = useLayout();
  const hl = interpolate(frame, [0, 10], [0, 1], { extrapolateRight: "clamp" });
  return (
    <div style={{ fontFamily: FONT_FAMILY, color: theme.ink, display: "flex", flexDirection: "column", gap: 22 * u }}>
      {label ? <div style={{ fontSize: 26 * u, fontWeight: 700, letterSpacing: 4 * u, textTransform: "uppercase", color: theme.inkSoft, marginBottom: 6 * u }}>{label}</div> : null}
      {steps.map((s, i) => {
        const n = i + 1;
        const isActive = n === active;
        const done = n < active;
        return (
          <div key={s} style={{ display: "flex", alignItems: "center", gap: 22 * u, opacity: isActive ? 1 : done ? 0.55 : 0.4 }}>
            <div style={{ width: 64 * u, height: 64 * u, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center",
                          fontSize: 30 * u, fontWeight: 800, color: isActive ? theme.card : theme.ink,
                          background: isActive ? theme.accent : "transparent", border: `${3 * u}px solid ${isActive ? theme.accent : theme.inkSoft}`,
                          transform: `scale(${isActive ? 1 + 0.08 * hl : 1})` }}>
              {done ? "✓" : n}
            </div>
            <div style={{ fontSize: 40 * u, fontWeight: isActive ? 800 : 600 }}>{s}</div>
          </div>
        );
      })}
    </div>
  );
};
