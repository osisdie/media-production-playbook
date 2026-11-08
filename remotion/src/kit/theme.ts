export type Theme = {
  bg: [string, string]; // background gradient
  blob: [string, string];
  ink: string; // main text
  inkSoft: string;
  card: string;
  cardInk: string;
  accent: string;
  accent2: string;
  captionBg: string;
  captionInk: string;
};

// Original palettes: fresh greens for the app promo, warm paper/coffee for the course.
export const leaf: Theme = {
  bg: ["#0F2A20", "#16392B"],
  blob: ["#2F8F5B", "#C8E86B"],
  ink: "#F4F1E8",
  inkSoft: "#B9D3C2",
  card: "#F4F1E8",
  cardInk: "#11281E",
  accent: "#7BD389",
  accent2: "#F2B33D",
  captionBg: "rgba(8, 22, 16, 0.78)",
  captionInk: "#FFFFFF",
};

export const coffee: Theme = {
  bg: ["#F6F0E6", "#EADFCC"],
  blob: ["#D9B48A", "#9CC5B5"],
  ink: "#2A1C15",
  inkSoft: "#7A6253",
  card: "#FFFBF4",
  cardInk: "#2A1C15",
  accent: "#B8692F",
  accent2: "#3E8C7A",
  captionBg: "rgba(42, 28, 21, 0.86)",
  captionInk: "#FFFBF4",
};

export const FONT_FAMILY = "'Kit Sans', 'Noto Sans TC', 'Noto Sans', system-ui, sans-serif";
