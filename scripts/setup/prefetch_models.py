"""Download the models used by the playbook into the Hugging Face cache.

Kokoro-82M (Apache-2.0): weights + the voices used by the examples.
faster-whisper "small" (MIT): used by narration QA.
spaCy en_core_web_sm (MIT): English G2P in misaki.
Cache location: $HF_HOME (default ~/.cache/huggingface). See models/README.md.
"""
from huggingface_hub import hf_hub_download, snapshot_download

KOKORO_REPO = "hexgrad/Kokoro-82M"
VOICES = ["af_heart", "am_michael", "zf_xiaoxiao", "zm_yunxi"]


def main() -> None:
    hf_hub_download(KOKORO_REPO, "config.json")
    hf_hub_download(KOKORO_REPO, "kokoro-v1_0.pth")
    for v in VOICES:
        hf_hub_download(KOKORO_REPO, f"voices/{v}.pt")
    snapshot_download("Systran/faster-whisper-small")
    # misaki's English G2P loads spaCy's small English model; install it now instead of
    # during the first synthesis.
    import importlib.util
    if importlib.util.find_spec("en_core_web_sm") is None:
        import spacy.cli
        spacy.cli.download("en_core_web_sm")
    print("models ready")


if __name__ == "__main__":
    main()
