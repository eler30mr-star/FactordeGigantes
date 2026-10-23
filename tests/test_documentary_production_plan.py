"""Puente real del guionista a producción; sin sintetizar ni aprobar fixtures."""
import copy
import hashlib
import json
import unittest

from test_documentary_blueprint import fixture
from test_documentary_script import narrative
from tools.ai_clients import FreeClients
from tools.approved_voice import SHA
from tools.documentary_production_plan import prepare_production, segment_text
from tools.documentary_script import write_script


class ProductionPlanTests(unittest.TestCase):
    def draft(self):
        research, selection = fixture()
        clients = FreeClients(env={"GEMINI_API_KEY": "fixture-not-a-real-key",
                                   "GEMINI_RESEARCH_FREE_CONFIRMED": "1"},
            reserve=lambda *_: True,
            transport=lambda *_: {"candidates": [{"content": {"parts": [{"text": json.dumps(narrative())}]}}]})
        return write_script(research, selection, clients=clients)

    def test_script_to_scene_tasks_retains_every_character_and_citation(self):
        draft = self.draft()
        original = copy.deepcopy(draft)
        plan = prepare_production(draft)
        self.assertEqual(draft, original)
        self.assertEqual(plan["status"], "production_plan_unapproved")
        self.assertEqual(plan["canonical_voice"]["sha256"], SHA)
        self.assertFalse(plan["canonical_voice"]["reference_file_checked"])
        self.assertFalse(plan["canonical_voice"]["substitution_allowed"])
        self.assertEqual(plan["source_research_sha256"], draft["source_research_sha256"])
        self.assertEqual(len(plan["scenes"]), 6)
        for scene, source in zip(plan["scenes"], draft["scenes"]):
            for pnum, paragraph in enumerate(source["paragraphs"], 1):
                takes = [t for t in scene["voice_takes"] if t["paragraph_id"] == f'S{scene["scene_number"]:02d}_P{pnum:02d}']
                self.assertEqual("".join(t["text"] for t in takes), paragraph["text"])
                for take in takes:
                    self.assertLessEqual(len(take["text"]), 260)
                    self.assertEqual(take["evidence_ids"], paragraph["evidence_ids"])
                    self.assertEqual(take["text"], paragraph["text"][take["character_start"]:take["character_end"]])
                    self.assertEqual(take["text_sha256"], hashlib.sha256(take["text"].encode()).hexdigest())
            self.assertTrue(all(v["assets"] == [] and not v["rights_verified"] for v in scene["visual_requests"]))
        self.assertEqual(plan["generated_voice_takes"], 0)
        self.assertFalse(plan["ready_for_render"])
        self.assertFalse(plan["publication_authorized"])

    def test_blocked_script_keeps_reasons_and_never_schedules_voice(self):
        plan = prepare_production({"schema": "fdg_documentary_script_v1",
            "status": "blocked_insufficient_research", "blocking_reasons": ["source_gaps"],
            "scenes": [], "ready_for_render": False, "publication_authorized": False})
        self.assertEqual(plan["blocking_reasons"], ["source_gaps"])
        self.assertEqual(plan["planned_voice_takes"], 0)
        self.assertEqual(plan["scenes"], [])

    def test_tampered_script_approvals_timing_or_citations_are_rejected(self):
        for mutate in (
            lambda d: d.update(publication_authorized=True),
            lambda d: d.update(ready_for_render=True),
            lambda d: d.update(source_research_sha256="missing"),
            lambda d: d.update(estimated_duration_seconds=660),
            lambda d: d["scenes"][0].update(narration_text="Texto sustituido"),
            lambda d: d["scenes"][0].update(start_seconds_estimated=1),
            lambda d: d["scenes"][0]["paragraphs"][0].update(evidence_ids=["E999"]),
            lambda d: d["scenes"][0]["paragraphs"][0].update(claim_indices=[True]),
            lambda d: d["scenes"][0]["paragraphs"][0].update(human_verified=True),
        ):
            draft = self.draft()
            mutate(draft)
            with self.assertRaises(ValueError):
                prepare_production(draft)

    def test_segmentation_keeps_accents_punctuation_and_whitespace(self):
        text = ("¿Qué decidió la compañía?\nConservó su investigación, sus cifras y su contexto. " * 15).strip()
        self.assertEqual("".join(p[2] for p in segment_text(text)), text)
        with self.assertRaises(ValueError):
            segment_text("x" * 300)

    def test_changing_one_word_changes_package_identity(self):
        a = self.draft()
        b = copy.deepcopy(a)
        b["title"] += " — revisión"
        self.assertNotEqual(prepare_production(a)["source_script_sha256"],
                            prepare_production(b)["source_script_sha256"])


if __name__ == "__main__":
    unittest.main()
