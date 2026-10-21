"""Contratos de animación: planos cambian dentro de cada clip y no se finge QA humano."""
import hashlib
import unittest
from tools.render_blackberry_scene01 import moving_frame,MIN_AUDIO_SECONDS,W,H
from tools.qwen_blackberry_scene01 import get_cases

class ChapterOneMotionTests(unittest.TestCase):
    def test_moving_camera_within_each_shot(self):
        for a,b in ((.55,1.7),(5.6,7.2),(10.8,12.7),(15.4,17.1)):
            image_a=moving_frame(a,80)
            image_b=moving_frame(b,80)
            self.assertEqual(image_a.size,(W,H))
            self.assertEqual(image_b.size,(W,H))
            self.assertNotEqual(hashlib.sha256(image_a.tobytes()).digest(),
                                hashlib.sha256(image_b.tobytes()).digest())

    def test_changing_shot_and_transition(self):
        hashes=[
            hashlib.sha256(moving_frame(t,80).tobytes()).hexdigest()
            for t in (1,6,11,15.1,21)
        ]
        self.assertEqual(len(set(hashes)),5)

    def test_invalid_times_rejected(self):
        with self.assertRaises(ValueError):
            moving_frame(-1,80)
        with self.assertRaises(ValueError):
            moving_frame(90,80)
        with self.assertRaises(ValueError):
            moving_frame(1,MIN_AUDIO_SECONDS-2)

    def test_scene_script_is_real_not_a_placeholder(self):
        cases=get_cases()
        self.assertEqual(len(cases),4)
        self.assertTrue(cases[0][1].startswith("Durante mucho tiempo"))
        self.assertTrue(cases[-1][1].startswith("Vamos a seguir documentos"))

if __name__=="__main__":
    unittest.main()
