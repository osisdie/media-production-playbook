import React from "react";
import type { Theme } from "./theme";
import { useLayout } from "./layout";

/** Row of dots: one per shot or stage, current one stretched into a pill. */
export const ProgressDots: React.FC<{ theme: Theme; count: number; current: number; color?: string }> = ({ theme, count, current, color }) => {
  const { u } = useLayout();
  const c = color ?? theme.accent;
  return (
    <div style={{ display: "flex", gap: 12 * u, alignItems: "center" }}>
      {Array.from({ length: count }, (_, i) => (
        <div key={i} style={{ height: 12 * u, width: (i === current ? 44 : 12) * u, borderRadius: 6 * u,
                              background: i <= current ? c : theme.inkSoft, opacity: i <= current ? 1 : 0.45 }} />
      ))}
    </div>
  );
};
