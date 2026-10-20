"""Pruebas puramente locales; no descargan modelos ni consumen GPU."""
import unittest

from tools import qwen_voice_continuity_batch as batch
from tools.approved_voice import approved_reference


class ContinuityBatchTests(unittest.TestCase):
    def test_fixed_prompts_bounded_and_distinct(self):
        _, manifest = approved_reference()
        self.assertTrue(batch.validate_cases(batch.CASES, manifest["reference_text"]))
        self.assertEqual(len({p for _, p in batch.CASES}), 2)

    def test_rejects_reused_reference_or_duplicate_prompt(self):
        _, manifest = approved_reference()
        a, b = batch.CASES
        with self.assertRaises(ValueError):
            batch.validate_cases((a, (b[0], a[1])), manifest["reference_text"])
        with self.assertRaises(ValueError):
            batch.validate_cases(((a[0], manifest["reference_text"]), b), manifest["reference_text"])

    def test_rejects_oversized_and_unsafe_inputs(self):
        a, b = batch.CASES
        for sample in (((a[0], "a" * 191), b), (("../01", a[1]), b),
                       ((a[0], a[1] + "\n"), b), (a,),
                       (("03_wrong", a[1]), b)):
            with self.subTest(sample=sample):
                with self.assertRaises(ValueError):
                    batch.validate_cases(sample, "referencia diferente")

    def test_generated_report_never_confers_permission(self):
        sample = [
            {"id": "01_decision", "auditory_approval": "pending"},
            {"id": "02_transformacion", "auditory_approval": "pending"},
        ]
        report = batch.make_report("hash_de_prueba", sample, 12.5)
        self.assertFalse(report["generated_clips_owner_approved"])
        self.assertFalse(report["voice_identity_verified_by_human"])
        self.assertFalse(report["commercial_rights_verified"])
        self.assertFalse(report["production_ready"])
        self.assertFalse(report["youtube_publication_enabled"])
        self.assertEqual(report["human_review"]["status"], "pending")
        with self.assertRaises(ValueError):
            batch.make_report("hash_de_prueba", sample[:1], 1)


if __name__ == "__main__":
    unittest.main()
