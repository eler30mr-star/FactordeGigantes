import unittest
from tools.qwen_consistency import validate_text,EDITORIAL_TEXT
from tools.approved_voice import approved_reference

class FixedNarratorTests(unittest.TestCase):
    def test_reference_persisted_and_verified(self):
        path,meta=approved_reference()
        self.assertEqual(path.stat().st_size,247245)
        self.assertIn("Blákberri",meta["reference_text"])
        self.assertIn("BlackBerry",meta["editorial_text"])
    def test_excerpt_valid(self):
        self.assertEqual(validate_text(EDITORIAL_TEXT),EDITORIAL_TEXT)
    def test_input_limits_and_no_pitch_hacks(self):
        for bad in ("","Hola","a"*231,"Durante años, algo cambió.\nUna nueva decisión que cambió el mundo."):
            with self.assertRaises(ValueError):
                validate_text(bad)
    def test_brand_lexicon_is_only_for_synthesis(self):
        text="Durante años, BlackBerry cambió el panorama tecnológico para muchas empresas."
        self.assertIn("Blákberri",validate_text(text))
        self.assertIn("BlackBerry",text)
