import React from "react";
import { AbsoluteFill, OffthreadVideo, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import {
  Background, buildShots, EndCard, ensureFont, enter, ExampleProps, FeatureCard, FONT_FAMILY, leaf,
  ProgressDots, rise, Shot, Shots, useLayout,
} from "../../kit";
import { PhoneMock } from "./PhoneMock";
import { PlantPot } from "./PlantPot";
import { Wordmark } from "./Wordmark";

const theme = leaf;

const Hook: React.FC<{ headline: string; opening3d: string | null }> = ({ headline, opening3d }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { u, safe } = useLayout();
  const p = enter(frame, fps, 4);
  return (
    <AbsoluteFill>
      {opening3d ? (
        // Transparent turntable rendered by scripts/blender (VP9 + alpha).
        <OffthreadVideo src={staticFile(opening3d)} transparent muted
                        style={{ width: "100%", height: "100%", transform: `translateY(${-90 * u}px) scale(0.92)` }} />
      ) : (
        <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", paddingBottom: 60 * u }}>
          <div style={{ ...rise(enter(frame, fps, 0), 60 * u) }}>
            <PlantPot size={560 * u} />
          </div>
        </AbsoluteFill>
      )}
      <div style={{ position: "absolute", top: safe.top, left: safe.left, right: safe.left, textAlign: "center", fontFamily: FONT_FAMILY,
                    color: theme.ink, fontSize: 92 * u, fontWeight: 800, lineHeight: 1.12, whiteSpace: "pre-line", ...rise(p, 40 * u) }}>
        {headline}
      </div>
    </AbsoluteFill>
  );
};

const Brand: React.FC<{ tagline: string }> = ({ tagline }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { u } = useLayout();
  const p = [0, 8, 14].map((d) => enter(frame, fps, d));
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", paddingBottom: 260 * u, fontFamily: FONT_FAMILY }}>
      <div style={{ ...rise(p[2], 50 * u), marginBottom: 50 * u }}><PlantPot size={360 * u} /></div>
      <div style={{ ...rise(p[0], 40 * u) }}><Wordmark size={130 * u} color={theme.ink} badge={theme.accent} leaf={theme.bg[0]} /></div>
      <div style={{ ...rise(p[1], 30 * u), marginTop: 30 * u, color: theme.inkSoft, fontSize: 48 * u, fontWeight: 600, textAlign: "center", maxWidth: 860 * u }}>{tagline}</div>
    </AbsoluteFill>
  );
};

const Feature: React.FC<{ v: Record<string, string>; lang: string; step: number }> = ({ v, lang, step }) => {
  const { u, safe, width } = useLayout();
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", top: safe.top - 20 * u, left: safe.left, right: safe.left, display: "flex", flexDirection: "column", alignItems: "center", gap: 30 * u }}>
        <ProgressDots theme={theme} count={3} current={step} />
        <FeatureCard theme={theme} icon={v.icon} title={v.title} body={v.body} />
      </div>
      <div style={{ position: "absolute", top: safe.top + 215 * u, left: 0, width, display: "flex", justifyContent: "center" }}>
        <PhoneMock theme={theme} lang={lang} screen={v.screen} width={400 * u} />
      </div>
    </AbsoluteFill>
  );
};

export const PromoDemo: React.FC<ExampleProps> = ({ project, timing, audioBase, opening3d }) => {
  ensureFont();
  const { fps } = useVideoConfig();
  const { u } = useLayout();
  const { shots } = buildShots(project.lines, timing, fps);
  const featureIds = project.lines.filter((l) => l.visual?.kind === "feature").map((l) => l.id);

  const renderShot = (s: Shot) => {
    const v = (s.line.visual ?? { kind: "hook" }) as Record<string, string>;
    switch (v.kind) {
      case "hook":
        return <Hook headline={v.headline ?? s.line.caption.join(" ")} opening3d={opening3d} />;
      case "brand":
        return <Brand tagline={v.tagline} />;
      case "feature":
        return <Feature v={v} lang={project.lang} step={featureIds.indexOf(s.line.id)} />;
      default:
        return (
          <EndCard theme={theme} tagline={v.tagline} cta={v.cta}
                   title={<Wordmark size={140 * u} color={theme.ink} badge={theme.accent} leaf={theme.bg[0]} />} />
        );
    }
  };

  return (
    <AbsoluteFill style={{ fontFamily: FONT_FAMILY }}>
      <Background theme={theme} />
      <Shots shots={shots} theme={theme} audioBase={audioBase} renderShot={renderShot} />
    </AbsoluteFill>
  );
};
