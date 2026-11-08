import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import type { Theme } from "./theme";
import { FONT_FAMILY } from "./theme";
import { useLayout } from "./layout";

/** Burned-in caption for the current line, always inside the safe area.
 *  `from`/`to` are frames relative to the shot (voice start/end). */
export const CaptionBar: React.FC<{ lines: string[]; theme: Theme; from: number; to: number }> = ({
  lines,
  theme,
  from,
  to,
}) => {
  const frame = useCurrentFrame();
  const { vertical, u, safe, width } = useLayout();
  const opacity = interpolate(frame, [from - 4, from + 2, to + 6, to + 12], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const fontSize = (vertical ? 50 : 44) * u;
  return (
    <div
      style={{
        position: "absolute",
        left: safe.left,
        right: vertical ? safe.right : safe.left,
        bottom: safe.bottom,
        display: "flex",
        justifyContent: "center",
        opacity,
        transform: `translateY(${(1 - opacity) * 12 * u}px)`,
      }}
    >
      <div
        style={{
          maxWidth: vertical ? width - safe.left - safe.right : width * 0.8,
          background: theme.captionBg,
          color: theme.captionInk,
          fontFamily: FONT_FAMILY,
          fontWeight: 600,
          fontSize,
          lineHeight: 1.32,
          padding: `${14 * u}px ${28 * u}px`,
          borderRadius: 18 * u,
          textAlign: "center",
          textWrap: "balance",
          boxSizing: "border-box",
        } as React.CSSProperties}
      >
        {lines.map((l, i) => (
          <div key={i}>{l}</div>
        ))}
      </div>
    </div>
  );
};
