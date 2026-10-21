"""Pruebas offline: Qwen BlackBerry toma exactamente la escena 01 sin aprobar voz."""
import unittest
from tools import qwen_blackberry_scene01 as pilot

class PilotNarrator(unittest.TestCase):
    def test_four_paragraphs_are_literal_script_without_loss(self):
        original=pilot.scene_one(pilot.ROOT.read_text(encoding="utf-8"))
        pieces=pilot.get_cases()
        self.assertEqual(len(pieces),4)
        self.assertEqual([x[0] for x in pieces],list(pilot.NAMES))
        self.assertEqual(" ".join(piece for _,piece in pieces),original)
        self.assertNotIn("FUENTES POR COMPROBAR",original)
        self.assertTrue(all(150<=len(p)<=260 for _,p in pieces))

    def test_changed_script_fails_not_invents_missing_text(self):
        text=pilot.ROOT.read_text(encoding="utf-8")
        with self.assertRaises(ValueError):
            pilot.scene_one(text.replace("**FUENTES POR COMPROBAR:**","**OTRAS FUENTES:**",1))
        with self.assertRaises(ValueError):
            pilot.split_for_speech("Frase inventada.")

    def test_report_requires_unapproved_four_fragments(self):
        clips=[{"id":name,"auditory_approval":"pending"} for name in pilot.NAMES]
        report=pilot.report_for_review(clips,"hash",95.0,290.0)
        self.assertFalse(report["owner_approved_new_takes"])
        self.assertFalse(report["commercial_rights_verified"])
        self.assertFalse(report["youtube_publication_enabled"])
        self.assertTrue(report["source_text_matches_manuscript"])
        with self.assertRaises(ValueError):
            pilot.report_for_review(clips[:3],"hash",80.0,280.0)

if __name__=="__main__":
    unittest.main()
