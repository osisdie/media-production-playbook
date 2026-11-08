import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { FONT_FAMILY, ICONS, Theme } from "../../kit";

const TEXT: Record<string, Record<string, string>> = {
  en: {
    water: "Time to water", amount: "200 ml · room temp",
    done: "Mark as done", reading: "Bright, indirect", week: "This week", days: "M,T,W,T,F,S,S", plants: "4 plants on track",
  },
  zh: {
    water: "該澆水了", amount: "200 ml・常溫水",
    done: "標記完成", reading: "明亮散射光", week: "本週", days: "一,二,三,四,五,六,日", plants: "4 盆植物都照顧到了",
  },
};

/** A simple phone frame with three original app screens (water / light / calendar).
 *  Text inside is kept to a few words at >= 28 px in the 1080-wide frame (34 design units at 400 px). */
export const PhoneMock: React.FC<{ theme: Theme; lang: string; screen: string; width: number }> = ({ theme, lang, screen, width }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = TEXT[lang] ?? TEXT.en;
  const s = width / 480; // design at 480 px wide
  const pop = spring({ frame: frame - 4, fps, config: { damping: 14, mass: 0.7 } });
  const card: React.CSSProperties = { background: "#FFFFFF", borderRadius: 26 * s, padding: 26 * s, boxShadow: "0 6px 20px rgba(0,0,0,0.08)" };
  const Water = ICONS.water;
  const Light = ICONS.light;
  const Check = ICONS.check;

  let body: React.ReactNode = null;
  if (screen === "water") {
    const fill = interpolate(frame, [10, 50], [0, 0.72], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    body = (
      <>
        <div style={{ ...card, transform: `translateY(${(1 - pop) * -60 * s}px)`, opacity: pop, display: "flex", gap: 18 * s, alignItems: "center" }}>
          <div style={{ width: 70 * s, height: 70 * s, borderRadius: 20 * s, background: "#DDEFFC", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <Water size={44 * s} color="#2F7FC0" />
          </div>
          <div style={{ fontSize: 36 * s, fontWeight: 800 }}>{t.water}</div>
        </div>
        <div style={{ ...card, marginTop: 24 * s, display: "flex", flexDirection: "column", alignItems: "center", gap: 18 * s }}>
          <div style={{ width: 170 * s, height: 250 * s, borderRadius: `${85 * s}px ${85 * s}px ${30 * s}px ${30 * s}px`, border: `${5 * s}px solid #2F7FC0`, position: "relative", overflow: "hidden" }}>
            <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: `${fill * 100}%`, background: "linear-gradient(#7CC3F2, #3A90D0)" }} />
          </div>
          <div style={{ fontSize: 34 * s, fontWeight: 700 }}>{t.amount}</div>
          <div style={{ background: theme.accent, borderRadius: 999, padding: `${12 * s}px ${30 * s}px`, fontSize: 34 * s, fontWeight: 800 }}>{t.done}</div>
        </div>
      </>
    );
  } else if (screen === "light") {
    const needle = interpolate(frame, [8, 40], [-70, 28], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const ok = frame > 40 ? 1 : 0;
    body = (
      <>
        <div style={{ borderRadius: 26 * s, height: 430 * s, background: "linear-gradient(160deg, #F7E7B8, #CFE8C9 60%, #8FC59A)", position: "relative", overflow: "hidden" }}>
          <div style={{ position: "absolute", left: 30 * s, right: 30 * s, top: 30 * s, bottom: 30 * s, border: `${3 * s}px dashed rgba(255,255,255,0.9)`, borderRadius: 20 * s }} />
          <div style={{ position: "absolute", right: 40 * s, top: 40 * s }}><Light size={70 * s} color="#E6A21A" /></div>
          <svg style={{ position: "absolute", left: 140 * s, top: 150 * s }} width={140 * s} height={220 * s} viewBox="0 0 140 220">
            <path d="M40 150h60l-8 60H48z" fill="#D9774A" />
            <path d="M70 150C30 120 30 70 50 40 60 80 68 110 70 150zM70 150c40-30 40-80 20-110-10 40-18 70-20 110z" fill="#3E9C5A" />
          </svg>
        </div>
        <div style={{ ...card, marginTop: 24 * s, display: "flex", flexDirection: "column", alignItems: "center" }}>
          <svg width={300 * s} height={160 * s} viewBox="0 0 300 160">
            <path d="M30 150 A120 120 0 0 1 270 150" stroke="#E7E2D6" strokeWidth="22" fill="none" strokeLinecap="round" />
            <path d="M30 150 A120 120 0 0 1 270 150" stroke={theme.accent2} strokeWidth="22" fill="none" strokeLinecap="round" strokeDasharray="377" strokeDashoffset={377 * (1 - (needle + 90) / 180)} />
            <g transform={`translate(150 150) rotate(${needle})`}><line x1="0" y1="0" x2="0" y2="-104" stroke="#11281E" strokeWidth="6" strokeLinecap="round" /></g>
            <circle cx="150" cy="150" r="10" fill="#11281E" />
          </svg>
          <div style={{ fontSize: 36 * s, fontWeight: 800, display: "flex", alignItems: "center", gap: 10 * s, opacity: 0.4 + 0.6 * ok }}>
            {t.reading} <Check size={34 * s} color={theme.cardInk} stroke={3} />
          </div>
        </div>
      </>
    );
  } else {
    const days = t.days.split(",");
    body = (
      <div style={{ ...card }}>
        <div style={{ fontSize: 36 * s, fontWeight: 800, marginBottom: 20 * s }}>{t.week}</div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(7, minmax(0, 1fr))", gap: 4 * s }}>
          {days.map((d, i) => {
            const on = frame > 8 + i * 5;
            const kind = [0, 2, 4, 6].includes(i) ? "water" : i === 3 ? "light" : "";
            const Icon = kind ? ICONS[kind] : null;
            return (
              <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 10 * s }}>
                <div style={{ fontSize: 34 * s, opacity: 0.6, fontWeight: 700 }}>{d}</div>
                <div style={{ width: 40 * s, height: 40 * s, borderRadius: 12 * s, display: "flex", alignItems: "center", justifyContent: "center",
                              background: on && Icon ? (kind === "water" ? "#DDEFFC" : "#FBEFC9") : "#F2F0EA", transform: `scale(${on ? 1 : 0.8})` }}>
                  {Icon && on ? <Icon size={26 * s} color={kind === "water" ? "#2F7FC0" : "#C98A0E"} /> : null}
                </div>
              </div>
            );
          })}
        </div>
        {["#58B86F", "#3E9C5A", "#6CCB7E", "#469F5F"].map((c, i) => {
          const p = spring({ frame: frame - 20 - i * 5, fps, config: { damping: 200 } });
          return (
            <div key={c} style={{ display: "flex", alignItems: "center", gap: 16 * s, marginTop: 18 * s, opacity: p, transform: `translateX(${(1 - p) * 30 * s}px)` }}>
              <div style={{ width: 40 * s, height: 40 * s, borderRadius: "50%", background: c }} />
              <div style={{ flex: 1, height: 14 * s, borderRadius: 7 * s, background: "#EEF3EC" }}>
                <div style={{ width: `${[85, 60, 95, 70][i]}%`, height: "100%", borderRadius: 7 * s, background: c }} />
              </div>
              <Check size={30 * s} color={c} stroke={3} />
            </div>
          );
        })}
        <div style={{ marginTop: 22 * s, fontSize: 34 * s, fontWeight: 700, opacity: 0.75 }}>{t.plants}</div>
      </div>
    );
  }

  return (
    <div style={{ width, height: width * 2.02, borderRadius: 64 * s, background: "#0B1712", padding: 14 * s, boxSizing: "border-box",
                  boxShadow: `0 ${30 * s}px ${80 * s}px rgba(0,0,0,0.45)`, fontFamily: FONT_FAMILY, color: "#11281E" }}>
      <div style={{ width: "100%", height: "100%", borderRadius: 52 * s, background: "#F5F3EC", overflow: "hidden", padding: `${70 * s}px ${26 * s}px ${26 * s}px`, boxSizing: "border-box", position: "relative" }}>
        <div style={{ position: "absolute", top: 18 * s, left: "50%", width: 120 * s, height: 32 * s, marginLeft: -60 * s, borderRadius: 16 * s, background: "#0B1712" }} />
        {body}
      </div>
    </div>
  );
};
