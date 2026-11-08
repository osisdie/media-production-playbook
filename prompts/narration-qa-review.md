# Prompt: review a narration QA report

```
Below is QA.md / qa.json from scripts/vo/verify.py for one narration, plus the script.
For each flagged line decide one action and say why:
- REWRITE  (the text itself is hard for TTS: leading short clause, rare acronym, number format),
- RESYNTH  (non-deterministic engine: try more seeds/takes),
- PROCESS  (adjust/undo post-processing; re-check on the final file),
- ACCEPT   (ASR noise or a harmless homophone — quote the transcript as evidence).
Flag transcripts where a key word became a different, meaning-changing word even if the
error rate is low. List what the automatic checks cannot judge (tone, accent, emotional
flow) as items for a human listening pass.
```
