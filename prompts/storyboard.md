# Prompt: storyboard from a narration script

```
Here is a narration script as JSON lines (id, text, caption, scene).
Target: [1920×1080 course intro / 1080×1920 promo], 30 fps.
For each line propose one shot:
- layout (what is on screen, where; keep content above the caption band),
- the reusable component it maps to (title card, step list, feature card, mock screen, end card),
- what animates and when, tied to caption segments (not to absolute seconds — shot length
  comes from the narration duration),
- any asset needed (procedural 3D, icon, mock UI) and a fallback if it's missing.
Rules: no real brands, people, prices or personal data; mock screens use fictional values;
API keys are always masked; text must fit without single-character last lines.
Output a table: id | component | layout | animation | assets.
```
