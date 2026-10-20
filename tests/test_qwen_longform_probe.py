"""Contratos locales del ensayo largo: sin descargar pesos ni gastar minutos de inferencia."""
import json
import unittest
from unittest.mock import patch

from tools import qwen_longform_probe as probe


class LongformContinuityTests(unittest.TestCase):
    def test_fixed_three_paragraphs_hypothetical(self):
        self.assertTrue(probe.validate_paragraphs(probe.PARAGRAPHS, "referencia distinta"))
        self.assertEqual(len(probe.PARAGRAPHS), 3)
        self.assertIn("hipotética", probe.PARAGRAPHS[2][1])

    def test_reject_unsafe_or_repeated_paragraphs(self):
        baseline = list(probe.PARAGRAPHS)
        defective = [
            baseline[:2],
            baseline + baseline[:1],
            [(baseline[0][0], baseline[0][1] + "\n")] + baseline[1:],
            [(baseline[0][0], baseline[0][1].strip() + " ")] + baseline[1:],
            [("01_otra", baseline[0][1])] + baseline[1:],
            [(baseline[0][0], "corto")] + baseline[1:],
            [baseline[0], (baseline[1][0], baseline[0][1]), baseline[2]],
        ]
        for item in defective:
            with self.subTest(item=item):
                with self.assertRaises(ValueError):
                    probe.validate_paragraphs(item, "referencia distinta")
        with self.assertRaises(ValueError):
            probe.validate_paragraphs(baseline, baseline[0][1])

    def test_report_never_grants_publication(self):
        clips = [{"id": name, "auditory_approval": "pending"}
                 for name, _ in probe.PARAGRAPHS]
        result = probe.report_result("expected_hash", clips, {"not_for_publication": True}, 10)
        self.assertTrue(result["text_is_hypothetical"])
        self.assertFalse(result["ready_for_documentary_render"])
        self.assertFalse(result["owner_approved_new_clips"])
        self.assertFalse(result["commercial_rights_verified"])
        self.assertFalse(result["youtube_publication_enabled"])
        self.assertEqual(result["human_identity_review"], "pending")
        with self.assertRaises(ValueError):
            probe.report_result("hash", clips[:2], {}, 10)
        with self.assertRaises(ValueError):
            probe.report_result("hash", [*clips[:2], {"auditory_approval": "approved"}], {}, 10)

    def test_probe_rejects_wrong_audio_codec(self):
        bad_json = json.dumps({"streams": [{"codec_name": "aac", "sample_rate": "48000",
                                              "channels": 1}],
                               "format": {"duration": "12.0"}})
        with patch.object(probe.subprocess, "check_output", return_value=bad_json):
            with self.assertRaises(RuntimeError):
                probe.probe_mp3("test.mp3")

    def test_probe_accepts_one_mp3_mono(self):
        correct_json = json.dumps({"streams": [{"codec_name": "mp3", "sample_rate": "48000",
                                                  "channels": 1}],
                                   "format": {"duration": "12.34567"}})
        with patch.object(probe.subprocess, "check_output", return_value=correct_json):
            self.assertEqual(probe.probe_mp3("test.mp3"), 12.346)


if __name__ == "__main__":
    unittest.main()
