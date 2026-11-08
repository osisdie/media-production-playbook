import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import {
  Background, buildShots, CheckIcon, coffee, CupIcon, EndCard, ensureFont, enter, ExampleProps, FONT_FAMILY, ProgressDots,
  rise, Shot, Shots, StepList, TitleCard, useLayout,
} from "../../kit";


const theme = coffee;

type StageVisual = { stage: number; heading: string; items?: string[]; big?: string; note?: string };

/** Right-hand panel: a checklist or one big number. */
const Panel: React.FC<{ v: StageVisual }> = ({ v }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { u } = useLayout();
  const head = enter(frame, fps, 2);
  return (
    <div style={{ background: theme.card, borderRadius: 44 * u, padding: `${54 * u}px ${64 * u}px`, boxShadow: `0 ${24 * u}px ${70 * u}px rgba(60,40,20,0.16)`,
                  color: theme.cardInk, fontFamily: FONT_FAMILY, width: 820 * u, minHeight: 520 * u, boxSizing: "border-box" }}>
      <div style={{ ...rise(head, 20 * u), fontSize: 30 * u, fontWeight: 700, letterSpacing: 3 * u, color: theme.accent, textTransform: "uppercase" }}>{v.heading}</div>
      {v.big ? (
        <>
          <div style={{ ...rise(enter(frame, fps, 8), 40 * u), fontSize: 210 * u, fontWeight: 800, lineHeight: 1.05, marginTop: 30 * u, letterSpacing: -4 * u }}>{v.big}</div>
          <div style={{ ...rise(enter(frame, fps, 14), 20 * u), fontSize: 40 * u, fontWeight: 500, color: theme.inkSoft, marginTop: 10 * u }}>{v.note}</div>
        </>
      ) : (
        <div style={{ marginTop: 34 * u, display: "flex", flexDirection: "column", gap: 26 * u }}>
          {(v.items ?? []).map((it, i) => {
            const p = enter(frame, fps, 8 + i * 7);
            return (
              <div key={it} style={{ ...rise(p, 24 * u), display: "flex", alignItems: "center", gap: 24 * u, fontSize: 52 * u, fontWeight: 700 }}>
                <div style={{ width: 58 * u, height: 58 * u, borderRadius: 16 * u, background: theme.accent2, display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <CheckIcon size={40 * u} color={theme.card} stroke={3} />
                </div>
                {it}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

const Stage: React.FC<{ v: StageVisual; stages: string[]; course: string }> = ({ v, stages, course }) => {
  const { u, safe } = useLayout();
  return (
    <AbsoluteFill style={{ padding: `${safe.top}px ${safe.left}px`, fontFamily: FONT_FAMILY, color: theme.ink }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16 * u, fontSize: 30 * u, fontWeight: 700 }}>
          <CupIcon size={44 * u} color={theme.accent} />
          {course}
        </div>
        <ProgressDots theme={theme} count={stages.length} current={v.stage - 1} />
      </div>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: 90 * u, paddingLeft: 30 * u }}>
        <StepList theme={theme} steps={stages} active={v.stage} />
        <Panel v={v} />
      </div>
    </AbsoluteFill>
  );
};

export const CourseDemo: React.FC<ExampleProps> = ({ project, timing, audioBase }) => {
  ensureFont();
  const { fps } = useVideoConfig();
  const { u } = useLayout();
  const { shots } = buildShots(project.lines, timing, fps);
  const design = (project.design ?? {}) as { stages?: string[]; course?: string };
  const stages = design.stages ?? [];

  const renderShot = (s: Shot) => {
    const v = (s.line.visual ?? { kind: "title" }) as Record<string, unknown>;
    if (v.kind === "title")
      return <TitleCard theme={theme} eyebrow={v.eyebrow as string} title={v.title as string} subtitle={v.subtitle as string}
                        icon={<CupIcon size={130 * u} color={theme.accent} stroke={1.6} />} />;
    if (v.kind === "stage") return <Stage v={v as unknown as StageVisual} stages={stages} course={design.course ?? ""} />;
    return <EndCard theme={theme} tagline={v.subtitle as string}
                    title={<div style={{ fontSize: 120 * u, fontWeight: 800, fontFamily: FONT_FAMILY }}>{v.title as string}</div>} />;
  };

  return (
    <AbsoluteFill>
      <Background theme={theme} />
      <Shots shots={shots} theme={theme} audioBase={audioBase} renderShot={renderShot} />
    </AbsoluteFill>
  );
};
