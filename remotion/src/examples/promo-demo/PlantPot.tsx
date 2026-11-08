import React from "react";
import { useCurrentFrame } from "remotion";

/** 2D stylised pot with leaves; used when the Blender opening is not rendered. */
export const PlantPot: React.FC<{ size: number }> = ({ size }) => {
  const frame = useCurrentFrame();
  const sway = (i: number) => Math.sin(frame / 22 + i * 1.3) * 3;
  const leaves = [
    { a: -38, l: 1.0, c: "#58B86F" },
    { a: -12, l: 1.18, c: "#3E9C5A" },
    { a: 14, l: 1.08, c: "#6CCB7E" },
    { a: 40, l: 0.92, c: "#469F5F" },
    { a: -62, l: 0.75, c: "#7AD48A" },
    { a: 64, l: 0.72, c: "#5DBA70" },
  ];
  return (
    <svg width={size} height={size * 1.2} viewBox="0 0 200 240">
      <ellipse cx="100" cy="228" rx="70" ry="8" fill="rgba(0,0,0,0.25)" />
      {leaves.map((lf, i) => (
        <g key={i} transform={`translate(100 140) rotate(${lf.a + sway(i)})`}>
          <path d={`M0 0 C ${-22 * lf.l} ${-40 * lf.l}, ${-16 * lf.l} ${-95 * lf.l}, 0 ${-112 * lf.l} C ${16 * lf.l} ${-95 * lf.l}, ${22 * lf.l} ${-40 * lf.l}, 0 0 Z`} fill={lf.c} />
          <path d={`M0 -6 L0 ${-100 * lf.l}`} stroke="rgba(255,255,255,0.35)" strokeWidth="2" />
        </g>
      ))}
      <path d="M48 138 H152 L140 222 H60 Z" fill="#D9774A" />
      <rect x="42" y="128" width="116" height="22" rx="6" fill="#E88A5C" />
    </svg>
  );
};
