# Prompt: write a TTS-friendly narration script

Use with any LLM. Fill in the brackets.

```
You are writing narration that will be read by a text-to-speech voice, not a human.
Topic: [topic]. Audience: [audience]. Format: [promo 30 s / course intro 60 s].
Language: [English / Traditional Chinese]. Tone: [calm teacher / energetic promo].

Rules:
1. 6–8 lines; one line = one shot. Each line 1–2 short sentences
   (Chinese: 25–45 characters; English: 12–22 words).
2. Never start a line with a short word followed by a comma or colon ("Step four, ..."):
   some TTS engines swallow the whole clause. Write "In step four we ..." instead.
3. Write numbers, units and symbols the way they should be spoken
   ("ninety-three degrees", not "93°C"); keep numerals only in the on-screen captions.
4. Avoid rare acronyms and mixed-language words. If a foreign product name is needed,
   introduce it ("an app called X") so the voice has a run-up.
5. Use punctuation to mark pauses; no parentheses, slashes, emoji or markdown.
6. The last line should hand over to what comes next (next lesson / call to action).
7. Output JSON: [{"id":"01","text":"<spoken text>","caption":["line 1","line 2"],"scene":"<shot idea>"}]
   Captions may use numerals and shorter wording than the spoken text; max ~16 CJK chars or ~38 Latin chars per caption line.
```

After synthesis, run `scripts/vo/verify.py` and rewrite any flagged line rather than over-processing the audio.
