import React from "react";

// Simple original line icons drawn in SVG (no icon font or external assets).
type P = { size: number; color: string; stroke?: number };

const Svg: React.FC<P & { children: React.ReactNode }> = ({ size, color, stroke = 2, children }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={stroke}
       strokeLinecap="round" strokeLinejoin="round">
    {children}
  </svg>
);

export const WaterIcon: React.FC<P> = (p) => (
  <Svg {...p}>
    <path d="M12 3c3.5 4.2 6 7.4 6 10.4A6 6 0 0 1 6 13.4C6 10.4 8.5 7.2 12 3z" />
    <path d="M9.2 14.2a2.9 2.9 0 0 0 2.6 2.7" />
  </Svg>
);

export const LightIcon: React.FC<P> = (p) => (
  <Svg {...p}>
    <circle cx="12" cy="12" r="4" />
    {[0, 45, 90, 135, 180, 225, 270, 315].map((a) => {
      const r = (a * Math.PI) / 180;
      return <line key={a} x1={12 + Math.cos(r) * 7} y1={12 + Math.sin(r) * 7} x2={12 + Math.cos(r) * 9.5} y2={12 + Math.sin(r) * 9.5} />;
    })}
  </Svg>
);

export const CalendarIcon: React.FC<P> = (p) => (
  <Svg {...p}>
    <rect x="3.5" y="5" width="17" height="15" rx="2.5" />
    <line x1="3.5" y1="9.5" x2="20.5" y2="9.5" />
    <line x1="8" y1="3" x2="8" y2="6.5" />
    <line x1="16" y1="3" x2="16" y2="6.5" />
    <circle cx="9" cy="14" r="0.6" fill={p.color} />
    <circle cx="13" cy="14" r="0.6" fill={p.color} />
    <circle cx="9" cy="17" r="0.6" fill={p.color} />
  </Svg>
);

export const CheckIcon: React.FC<P> = (p) => (
  <Svg {...p}>
    <path d="M5 12.5l4.2 4.2L19 7" />
  </Svg>
);

export const LeafIcon: React.FC<P> = (p) => (
  <Svg {...p}>
    <path d="M5 19c0-8 5-13 14-14-1 9-6 14-14 14z" />
    <path d="M5 19l7-7" />
  </Svg>
);

export const CupIcon: React.FC<P> = (p) => (
  <Svg {...p}>
    <path d="M4 9h13v4a6 6 0 0 1-6 6h-1a6 6 0 0 1-6-6V9z" />
    <path d="M17 10.5h1.5a2.5 2.5 0 0 1 0 5H16.5" />
    <path d="M8.5 3.5c-.8 1 .8 1.8 0 3M12.5 3.5c-.8 1 .8 1.8 0 3" />
  </Svg>
);

export const ICONS: Record<string, React.FC<P>> = {
  water: WaterIcon,
  light: LightIcon,
  calendar: CalendarIcon,
  check: CheckIcon,
  leaf: LeafIcon,
  cup: CupIcon,
};
