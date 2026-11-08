import React from "react";
import { AbsoluteFill, Audio, interpolate, Sequence, staticFile, useCurrentFrame } from "remotion";
import type { Shot } from "./timeline";
import { TRANSITION_FRAMES } from "./timeline";
import type { Theme } from "./theme";
import { CaptionBar } from "./CaptionBar";

const FadeIn: React.FC<{ enabled: boolean; children: React.ReactNode }> = ({ enabled, children }) => {
  const frame = useCurrentFrame();
  const opacity = enabled ? interpolate(frame, [0, TRANSITION_FRAMES], [0, 1], { extrapolateRight: "clamp" }) : 1;
  return <AbsoluteFill style={{ opacity }}>{children}</AbsoluteFill>;
};

/** Lays out shots back to back with a 6-frame crossfade, plays each line's
 *  narration at its audioFrom and draws the caption on top. */
export const Shots: React.FC<{
  shots: Shot[];
  theme: Theme;
  audioBase: string | null;
  renderShot: (shot: Shot) => React.ReactNode;
}> = ({ shots, theme, audioBase, renderShot }) => (
  <>
    {shots.map((s, i) => {
      const last = i === shots.length - 1;
      return (
        <Sequence key={s.line.id} from={s.from} durationInFrames={s.duration + (last ? 0 : TRANSITION_FRAMES)} name={`shot ${s.line.id}`}>
          <FadeIn enabled={i > 0}>
            {renderShot(s)}
            <CaptionBar lines={s.line.caption} theme={theme} from={s.audioFrom - s.from} to={s.audioFrom - s.from + s.audioFrames} />
          </FadeIn>
        </Sequence>
      );
    })}
    {audioBase
      ? shots.map((s) => (
          <Sequence key={`a${s.line.id}`} from={s.audioFrom} durationInFrames={s.audioFrames + 2} name={`vo ${s.line.id}`}>
            <Audio src={staticFile(`${audioBase}/${s.line.id}.wav`)} />
          </Sequence>
        ))
      : null}
  </>
);
