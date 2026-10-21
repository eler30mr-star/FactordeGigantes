"""El guion BlackBerry puede programarse entero sin inventar ni omitir textos."""
import unittest
from tools import blackberry_voice_schedule as schedule

class VoiceScheduleTests(unittest.TestCase):
    def test_complete_script_all_twelve_scenes_and_exact_words(self):
        original=schedule.DEFAULT_SCRIPT.read_text(encoding="utf-8")
        plan=schedule.make_schedule(original)
        self.assertEqual(plan["scenes_count"],12)
        self.assertGreaterEqual(plan["planned_voice_clips"],36)
        self.assertLessEqual(plan["max_scene_clips"],8)
        self.assertEqual(plan["generated_voice_clips"],0)
        self.assertFalse(plan["youtube_publication_allowed"])
        self.assertFalse(plan["commercial_rights_verified"])
        for (_,_,narration),batch in zip(schedule.all_scene_voices(original),plan["scenes"]):
            self.assertEqual(" ".join(p["text"] for p in batch["parts"]),narration)
            self.assertTrue(all(120<=p["characters"]<=260 for p in batch["parts"]))
            self.assertEqual(batch["render_status"],"blocked_pending_voice_review")

    def test_short_or_incomplete_script_rejected(self):
        with self.assertRaises(ValueError):
            schedule.make_schedule("Dos párrafos inventados")

    def test_dont_cut_words_to_fit_voice_budget(self):
        with self.assertRaises(ValueError):
            schedule.split_scene("A"*270)
        with self.assertRaises(ValueError):
            schedule.split_scene("Frase diminuta.")

if __name__=="__main__":
    unittest.main()
