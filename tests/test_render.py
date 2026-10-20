import json
import unittest
from pathlib import Path
from tools.render import validate_manifest

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "documental.json"

class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def test_example_accepted(self):
        self.assertEqual(validate_manifest(self.manifest)["format"], "short")

    def test_requires_sources(self):
        self.manifest["sources"] = []
        with self.assertRaises(ValueError):
            validate_manifest(self.manifest)

    def test_disallows_empty_segment(self):
        self.manifest["segments"][0]["voiceover"] = ""
        with self.assertRaises(ValueError):
            validate_manifest(self.manifest)

    def test_formats(self):
        self.manifest["format"] = "tiktok"
        with self.assertRaises(ValueError):
            validate_manifest(self.manifest)

if __name__ == "__main__":
    unittest.main()
