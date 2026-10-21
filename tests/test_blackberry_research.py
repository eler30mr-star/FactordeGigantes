"""Control del primer expediente investigado: BlackBerry (no publicación)."""
import json
import unittest
from pathlib import Path
from tools.editorial_evidence import validate_dossier

ROOT=Path(__file__).resolve().parents[1]
RESEARCH=ROOT/"research/blackberry/expediente_preliminar.json"


class BlackberryResearchTests(unittest.TestCase):
    def test_pilot_structure_and_safe_review_state(self):
        data=json.loads(RESEARCH.read_text(encoding="utf-8"))
        report=validate_dossier(data)
        self.assertEqual(report["sources_count"],6)
        self.assertEqual(report["claims_count"],8)
        self.assertEqual(report["claims_reviewed_with_sources"],0)
        self.assertEqual(report["claims_pending_or_rejected"],8)
        self.assertGreaterEqual(report["assets_pending_rights"],4)
        self.assertFalse(report["automated_publication_authorized"])
        self.assertFalse(report["can_release_documentary"])
        self.assertEqual(sorted(c["segment_index"] for c in data["claims"]),list(range(1,9)))
        for c in data["claims"]:
            self.assertEqual(c.get("reviewed_by"),"")
            self.assertTrue(all(e["status"]=="pendiente" for e in c["evidence"]))

    def test_all_sources_are_primary_and_no_rights_implied(self):
        data=json.loads(RESEARCH.read_text(encoding="utf-8"))
        self.assertTrue(all(s["type"]=="primaria" for s in data["sources"]))
        self.assertFalse(data["publication_authorized"])
        self.assertTrue(any(a["kind"]=="voz" for a in data["assets"]))
        self.assertTrue(all(a["rights_status"]=="pendiente" for a in data["assets"]))
        self.assertTrue(all(s["url"].startswith("https://") for s in data["sources"]))


if __name__=="__main__":
    unittest.main()
