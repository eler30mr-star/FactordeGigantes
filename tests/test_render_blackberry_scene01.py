"""Contratos de animación: planos cambian dentro de cada clip y no se finge QA humano."""
import hashlib
import unittest
import json
from pathlib import Path
import tempfile
from unittest.mock import patch
from tools import render_blackberry_scene01 as chapter
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

    def test_source_checksums_and_pending_approval_required(self):
        from tools.approved_voice import approved_reference
        _,meta=approved_reference()
        with tempfile.TemporaryDirectory() as folder:
            out=Path(folder)
            clips=[]
            for i,(name,paragraph) in enumerate(get_cases()):
                raw=(name.encode()+b"----"*80)
                (out/(name+".mp3")).write_bytes(raw)
                clips.append({"id":name,"text":paragraph,"sha256":hashlib.sha256(raw).hexdigest(),
                              "auditory_approval":"pending"})
            (out/"05_escena01_unida.mp3").write_bytes(b"temporary fake preview")
            report={
                "canonical_reference_sha256":meta["sha256"],
                "owner_approved_new_takes":False,
                "commercial_rights_verified":False,
                "clips":clips,"preview_mp3":{"duration_seconds":78.0}
            }
            manifest=out/"ESTADO_ESCENA01_VOZ.json"
            manifest.write_text(json.dumps(report),encoding="utf-8")
            with patch.object(chapter,"probe_mp3",return_value=78.0):
                _,seconds,_=chapter.source_validation(out)
                self.assertEqual(seconds,78.0)
                report["clips"][1]["sha256"]="f"*64
                manifest.write_text(json.dumps(report),encoding="utf-8")
                with self.assertRaises(RuntimeError):
                    chapter.source_validation(out)
                report["clips"][1]["sha256"]=clips[1]["sha256"]
                report["owner_approved_new_takes"]=True
                manifest.write_text(json.dumps(report),encoding="utf-8")
                with self.assertRaises(RuntimeError):
                    chapter.source_validation(out)

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
