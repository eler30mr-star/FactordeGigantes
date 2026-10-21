"""Pruebas de movimiento genuino, integridad de voz y límites de uso."""
import hashlib
import json
from pathlib import Path
import unittest

from tools.approved_voice import approved_reference
from tools.render_blackberry_motion_intro import render_frame,VOICE_DURATION,FPS,W,H

class IntroMotionTests(unittest.TestCase):
    def test_approved_reference_is_identical_and_rights_pending(self):
        audio,meta=approved_reference()
        self.assertEqual(meta["status"],"approved_by_owner_for_editorial_reference")
        self.assertEqual(meta["rights_status"],"pending_commercial_verification")
        self.assertEqual(hashlib.sha256(audio.read_bytes()).hexdigest(),meta["sha256"])
        self.assertAlmostEqual(meta["duration_seconds"],VOICE_DURATION,places=2)

    def test_real_frame_motion_not_a_static_text_background(self):
        # Comprueba cambios dentro de cada escena, no solo al cambiar de título.
        for a,b in ((.4,1.2),(3.7,4.4),(6.8,7.5),(9.7,10.4)):
            first=render_frame(a)
            second=render_frame(b)
            self.assertEqual(first.size,(W,H))
            self.assertEqual(second.size,(W,H))
            self.assertNotEqual(hashlib.sha256(first.tobytes()).digest(),
                                hashlib.sha256(second.tobytes()).digest())

    def test_scenes_are_visually_distinct(self):
        first=render_frame(1.2).tobytes()
        second=render_frame(4.2).tobytes()
        third=render_frame(7.8).tobytes()
        fourth=render_frame(11.5).tobytes()
        self.assertEqual(len({
            hashlib.sha256(frame).hexdigest()
            for frame in (first,second,third,fourth)
        }),4)

    def test_invalid_timestamps_are_rejected(self):
        with self.assertRaises(ValueError):
            render_frame(-1)
        with self.assertRaises(ValueError):
            render_frame(VOICE_DURATION+2.0)


if __name__=="__main__":
    unittest.main()
