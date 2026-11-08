// Remotion CLI config (used by `npm run studio`). Programmatic renders go
// through scripts/video/render.mjs, which sets the same options explicitly.
import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setConcurrency(1);
Config.setOverwriteOutput(true);
