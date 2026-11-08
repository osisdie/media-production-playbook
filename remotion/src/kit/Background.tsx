import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import type { Theme } from "./theme";
import { useLayout } from "./layout";

/** Soft gradient with two slowly drifting blurred blobs. */
export const Background: React.FC<{ theme: Theme }> = ({ theme }) => {
  const frame = useCurrentFrame();
  const { width, height, u } = useLayout();
  const t = frame / 30;
  const blob = (color: string, x: number, y: number, r: number, phase: number) => (
    <div
      style={{
        position: "absolute",
        left: x + Math.sin(t * 0.35 + phase) * 60 * u - r,
        top: y + Math.cos(t * 0.28 + phase) * 50 * u - r,
        width: r * 2,
        height: r * 2,
        borderRadius: "50%",
        background: color,
        opacity: 0.32,
        filter: `blur(${120 * u}px)`,
      }}
    />
  );
  return (
    <AbsoluteFill style={{ background: `linear-gradient(160deg, ${theme.bg[0]}, ${theme.bg[1]})`, overflow: "hidden" }}>
      {blob(theme.blob[0], width * 0.15, height * 0.2, 420 * u, 0)}
      {blob(theme.blob[1], width * 0.85, height * 0.78, 360 * u, 2)}
    </AbsoluteFill>
  );
};
