"""EDL seguro: cronología contigua, 12 escenas y bloqueos de producción."""
import json
from pathlib import Path
import unittest
from tools.blackberry_edl import make_edl

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"research/blackberry/GUION_DOCUMENTAL_11MIN_NO_APROBADO.md"
SOURCES=ROOT/"research/blackberry/FUENTES_GUION_10MIN.json"


class EDLTest(unittest.TestCase):
    def test_all_scenes_are_contiguous_and_not_exportable(self):
        data=make_edl(SCRIPT.read_text(encoding="utf-8"),
                      json.loads(SOURCES.read_text(encoding="utf-8")))
        self.assertEqual(len(data["scenes"]),12)
        self.assertEqual(data["timeline_duration_ms"],710000)
        self.assertFalse(data["upload_to_youtube"])
        self.assertFalse(data["ready_for_commercial_export"])
        self.assertFalse(data["voice_commercial_rights_verified"])
        self.assertEqual(data["scenes"][0]["start_ms"],0)
        self.assertEqual(data["scenes"][-1]["end_ms"],710000)
        for a,b in zip(data["scenes"],data["scenes"][1:]):
            self.assertEqual(a["end_ms"],b["start_ms"])
            self.assertFalse(a["footage_attached"])
            self.assertFalse(a["render_allowed"])
        self.assertTrue(all(item["source_ids"] for item in data["scenes"]))

    def test_missing_visual_is_not_silently_replaced(self):
        text=SCRIPT.read_text(encoding="utf-8")
        text=text.replace("**VISUAL PROPUESTO, SIN LICENCIA PRESUPUESTA:**", "**NO VISUAL:**",1)
        with self.assertRaisesRegex(ValueError,"no tiene visual"):
            make_edl(text,json.loads(SOURCES.read_text(encoding="utf-8")))

if __name__=="__main__":
    unittest.main()
