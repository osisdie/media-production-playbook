"""Unit tests for the mixed Mandarin/English phoneme splitter in kokoro_synth.py (no models needed)."""
import os
import sys
import types
import unittest

# kokoro_synth imports numpy/soundfile at module level; CI runs without them and these tests don't need them.
for _mod in ("numpy", "soundfile"):
    try:
        __import__(_mod)
    except ImportError:
        sys.modules[_mod] = types.ModuleType(_mod)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts", "tts"))
from kokoro_synth import LATIN, mixed_phonemes  # noqa: E402


def zh(t):
    return "".join("Z" for c in t if "一" <= c <= "鿿")


def en(w):
    return f"<{w.lower()}>"


class MixedPhonemes(unittest.TestCase):
    def test_pure_chinese_has_no_latin_run(self):
        self.assertIsNone(LATIN.search("每天替植物澆水的好幫手。"))

    def test_latin_word_goes_to_english_g2p(self):
        self.assertEqual(mixed_phonemes(zh, en, "讓 Verdalo 來提醒。"), "Z <verdalo> ZZZ")

    def test_lexicon_overrides_english_g2p(self):
        self.assertEqual(mixed_phonemes(zh, en, "讓 Verdalo 來提醒。", {"Verdalo": "vɜɹdˈɑlO"}),
                         "Z vɜɹdˈɑlO ZZZ")

    def test_multiword_and_hyphen_stay_one_run(self):
        self.assertEqual(mixed_phonemes(zh, en, "用 Plant Care 和 Ver-dah-lo"), "Z <plant care> Z <ver-dah-lo>")


if __name__ == "__main__":
    unittest.main()
