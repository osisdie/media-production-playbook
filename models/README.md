# Models

Nothing in this folder is committed except this file. Models are downloaded on first use
(or ahead of time by `scripts/setup/prefetch_models.py`, which the setup scripts run) into
the Hugging Face cache, **not** into the repo.

| What | Used by | Size (approx.) | License |
|---|---|---|---|
| [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) weights `kokoro-v1_0.pth` + `config.json` | `scripts/tts/kokoro_synth.py` | ~330 MB | Apache-2.0 |
| Kokoro voices used by the examples: `af_heart`, `am_michael`, `zf_xiaoxiao`, `zm_yunxi` (`voices/*.pt`) | same | ~0.5 MB each | Apache-2.0 |
| [faster-whisper `small`](https://huggingface.co/Systran/faster-whisper-small) (CTranslate2 conversion of Whisper small) | `scripts/vo/verify.py` (narration QA) | ~480 MB | MIT |
| spaCy `en_core_web_sm` (installed into `.venv` by misaki on the first English synthesis) | English G2P | ~13 MB | MIT |

Kokoro voices are **synthetic built-in voices**. This playbook never clones or imitates a real
person's voice; see the consent docs before using any voice-cloning engine.

## Where the cache lives

| OS | Default location | Override |
|---|---|---|
| Linux / WSL | `~/.cache/huggingface/hub/` | `HF_HOME=/path` |
| macOS | `~/.cache/huggingface/hub/` | `HF_HOME=/path` |

To work fully offline after the first download, set `HF_HUB_OFFLINE=1`.
To free space, delete `models--hexgrad--Kokoro-82M` / `models--Systran--faster-whisper-small`
from the cache folder; they are fetched again when needed.

## Other runtimes and their licenses

- **misaki** (Kokoro's G2P, Apache-2.0). Its English fallback for unknown words uses
  **espeak-ng** (GPL-3.0), shipped as a separate library by the `espeakng-loader` package; no
  system install is needed.
- **Remotion** is *not* MIT: it uses the Remotion License. It is free for individuals, small
  for-profit teams (up to 3 people) and non-profits; larger companies need a company license.
  Check <https://www.remotion.dev/license> before using it commercially.
- **Blender** is GPL. It is only invoked as an external tool; the renders you make with it are
  yours and are not GPL-encumbered.
- **Noto Sans TC** (font used in the videos) is under the SIL Open Font License 1.1 and is
  downloaded by the setup script into `remotion/public/fonts/` (not committed).
- **Chrome Headless Shell** is downloaded by Remotion on the first render (~100 MB) into
  `.remotion/` at the repository root (gitignored).

## Optional components (not installed by the setup scripts)

| Component | Used by | License | Notes |
|---|---|---|---|
| UTMOS (`tarepan/SpeechMOS` v1.2.0) | `scripts/vo/verify.py --utmos` | see that repository | Fetched with `torch.hub.load(..., trust_repo=True)`: this **downloads and runs remote Python code** from that repository on first use. Only use `--utmos` if you are fine with that; the default QA does not need it. |
| `praat-parselmouth` | `scripts/vo/prosody.py` only | GPL-3.0 | Not in `requirements.txt`. Install it yourself if you need prosody analysis: `.venv/bin/pip install praat-parselmouth`. |
