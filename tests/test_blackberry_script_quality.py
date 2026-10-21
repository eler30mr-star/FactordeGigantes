"""QA del borrador BlackBerry: estructura, duración, trazabilidad, no publicación."""
import json
from pathlib import Path
import unittest
from tools.blackberry_script_quality import inspect_script

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"research/blackberry/GUION_DOCUMENTAL_11MIN_NO_APROBADO.md"
SOURCES=ROOT/"research/blackberry/FUENTES_GUION_10MIN.json"


class ScriptQualityTests(unittest.TestCase):
    def read(self):
        return SCRIPT.read_text(encoding="utf-8"),json.loads(SOURCES.read_text(encoding="utf-8"))

    def test_full_draft_has_twelve_scenes_and_sources(self):
        text,src=self.read()
        result=inspect_script(text,src)
        self.assertTrue(result["structural_gate_passed"],result["flags"])
        self.assertEqual(result["scene_count"],12)
        self.assertGreaterEqual(result["total_words"],1500)
        self.assertGreaterEqual(result["timeline_seconds"],600)
        self.assertLessEqual(result["timeline_seconds"],840)
        self.assertGreaterEqual(result["distinct_sources_used"],5)
        self.assertFalse(result["factual_gate_passed"])
        self.assertFalse(result["render_authorized"])
        self.assertFalse(result["youtube_publication_authorized"])

    def test_missing_source_id_is_rejected(self):
        text,src=self.read()
        text=text.replace("[F25]","[Z999]",1)
        report=inspect_script(text,src)
        self.assertFalse(report["structural_gate_passed"])
        self.assertTrue(any("citas_validas" in flag for flag in report["flags"]))

    def test_broken_scene_timeline_is_rejected(self):
        text,src=self.read()
        text=text.replace("(02:50–03:45)","(02:55–03:45)",1)
        report=inspect_script(text,src)
        self.assertFalse(report["structural_gate_passed"])
        self.assertTrue(any("corte_no_contiguo" in flag for flag in report["flags"]))

    def test_missing_approval_banners_is_rejected(self):
        text,src=self.read()
        text=text.replace("NO APROBADO","BORRADOR",1)
        report=inspect_script(text,src)
        self.assertIn("faltan_bloqueos_editoriales",report["flags"])

    def test_duplicate_source_id_in_manifest_is_rejected(self):
        text,src=self.read()
        src["citations"].append(dict(src["citations"][0]))
        with self.assertRaisesRegex(ValueError,"duplicado"):
            inspect_script(text,src)


if __name__=="__main__":
    unittest.main()
