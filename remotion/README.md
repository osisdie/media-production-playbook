# Remotion project

One Remotion project for every example. Versions are pinned exactly (`remotion` /
`@remotion/*` 4.0.538, React 18.3.1, TypeScript 5.6) so renders are reproducible.

```
src/
  index.ts / Root.tsx        registers one composition per example language
  kit/                       shared building blocks
    pacing.mjs / timeline.ts shot length = narration + breathing room; 6-frame crossfades
                             (pacing.mjs is plain JS so scripts/video/stills.mjs uses the same math)
    Shots.tsx                lays shots out, plays each line's wav, draws captions
    CaptionBar.tsx           burned-in captions inside the platform safe area
    TitleCard / FeatureCard / StepList / EndCard / ProgressDots / Background / Icons
    theme.ts, layout.ts      palettes; size + safe-area helpers for 16:9 and 9:16
    font.ts                  loads public/fonts/NotoSansTC.ttf before the first frame
  examples/promo-demo/       vertical app promo (phone mock screens, 3D or 2D opening)
  examples/course-demo/      landscape lesson (step list + checklist / big-number panel)
```

Compositions read their content from `examples/<example>/project.<lang>.json` and their
timing from `build/<lang>/timing.json`. Without timing (before TTS) durations are estimated
from text length, so you can design in Studio first:

```bash
cd remotion && npm run studio
```

Renders go through `scripts/video/render.mjs` (copies narration into the gitignored
`public/generated/`, `concurrency: 1`). For quick layout checks without a full render:

```bash
node scripts/video/stills.mjs --project examples/promo-demo/project.zh.json   # one PNG per shot
```

## Adding an example

1. `examples/<new>/project.<lang>.json` with a unique `video.composition` id.
2. A component in `src/examples/<new>/` taking `ExampleProps`; build it from `kit/`.
3. Register it in `Root.tsx` (import the project JSON, add an entry).

Remotion is free for individuals and small teams; larger companies need a license — see
`models/README.md`.
