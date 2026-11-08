"""Pure-Python unit tests for the narration QA helpers (no models needed)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts", "vo"))
from drag import drags, score  # noqa: E402
from textnorm import error_rate, num_en, num_zh  # noqa: E402


class TextNorm(unittest.TestCase):
    def test_zh_numbers_and_punctuation(self):
        self.assertEqual(error_rate("每天 3 個任務。", "每天三個任務", "zh"), 0)
        self.assertEqual(num_zh(1005), "一千零五")

    def test_zh_script_folding(self):
        try:
            import opencc  # noqa: F401
        except ImportError:
            self.skipTest("opencc not installed")
        # Simplified ASR output vs a Traditional script, including 沖/冲 (s2t would give 衝) and 2 萬 vs 两万
        self.assertEqual(error_rate("在家手沖咖啡，兩萬公克", "在家手冲咖啡两万公克", "zh"), 0)

    def test_en_wer(self):
        self.assertEqual(error_rate("Brew 2 cups at 93 degrees.", "brew two cups at ninety three degrees", "en"), 0)
        self.assertAlmostEqual(error_rate("pour the water slowly", "pour water slowly", "en"), 0.25)
        self.assertEqual(num_en(1200), "one thousand two hundred")


class Drag(unittest.TestCase):
    def test_flags_held_character(self):
        words = [[0.0, 0.3, "每"], [0.3, 1.0, "天"], [1.0, 1.2, "喝"]]
        self.assertEqual(drags(words, "每天喝"), [("天", 0.7, 0.3)])
        self.assertGreater(score(words, "每天喝"), 0)

    def test_ignores_pause_and_punctuation(self):
        # long token followed by a pause → natural phrase ending
        self.assertEqual(drags([[0.0, 0.8, "好"], [1.2, 1.4, "的"]], "好的"), [])
        # long token next to a comma → Whisper folded the pause into it
        self.assertEqual(drags([[0.0, 0.2, "先"], [0.2, 0.9, "磨"], [0.9, 1.1, "豆"]], "先磨，豆"), [])

    def test_english_limit_scales_with_length(self):
        self.assertEqual(drags([[0.0, 0.9, " temperature"], [0.9, 1.1, " now"]], "temperature now"), [])
        # (the first token of a sentence is skipped, so test a mid-sentence word)
        self.assertEqual(len(drags([[0.0, 0.2, " the"], [0.2, 1.2, " app"], [1.2, 1.4, " now"]], "the app now")), 1)


if __name__ == "__main__":
    unittest.main()
