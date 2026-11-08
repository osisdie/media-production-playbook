import { continueRender, delayRender, staticFile } from "remotion";

// Loads public/fonts/NotoSansTC.ttf (SIL OFL, fetched by the setup script) once,
// and blocks rendering until it is ready so no frame falls back to a system font.
let started = false;

export const ensureFont = (): void => {
  if (started || typeof document === "undefined") return;
  started = true;
  const handle = delayRender("Loading Noto Sans TC");
  const face = new FontFace("Kit Sans", `url(${staticFile("fonts/NotoSansTC.ttf")}) format("truetype")`, {
    weight: "100 900",
  });
  face
    .load()
    .then(() => {
      (document.fonts as unknown as { add: (f: FontFace) => void }).add(face);
      continueRender(handle);
    })
    .catch((err) => {
      console.warn("Font failed to load, falling back to system sans-serif", err);
      continueRender(handle);
    });
};
