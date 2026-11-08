import React from "react";
import { FONT_FAMILY } from "../../kit";

/** Fictional brand mark for "Verdalo": a round leaf badge + lowercase-friendly wordmark. */
export const Wordmark: React.FC<{ size: number; color: string; badge: string; leaf: string }> = ({ size, color, badge, leaf }) => (
  <div style={{ display: "flex", alignItems: "center", gap: size * 0.28, fontFamily: FONT_FAMILY }}>
    <svg width={size * 1.05} height={size * 1.05} viewBox="0 0 48 48">
      <circle cx="24" cy="24" r="23" fill={badge} />
      <path d="M14 33c0-11 7-18 21-19-1 13-8 19-21 19z" fill={leaf} />
      <path d="M14 33l11-11" stroke={badge} strokeWidth="2.4" strokeLinecap="round" />
    </svg>
    <div style={{ fontSize: size, fontWeight: 800, letterSpacing: -size * 0.02, color, lineHeight: 1 }}>Verdalo</div>
  </div>
);
