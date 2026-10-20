import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.subtitles import make_srt, split_lines, timestamp
from tools.voice import MODEL_SHA256, ensure_voice, sha256, synthesize

class SubtitleTests(unittest.TestCase):
    def test_srt_starts_at_zero_and_second_scene_is_offset(self):
        srt=make_srt([
            {"voiceover":"Una decisión cambió la historia de las empresas."},
            {"voiceover":"La siguiente escena descubre la consecuencia."}
        ],[3.0,4.0])
        self.assertIn("00:00:00,000 -->",srt)
        self.assertIn("00:00:03,000 -->",srt)
    def test_long_text_wrap(self):
        chunks=split_lines("Las decisiones de las empresas cambiaron la historia de la industria. "*4)
        self.assertTrue(len(chunks)>1)
        self.assertTrue(all(len(x)<=42 for p in chunks for x in p.split("\n")))
    def test_bad_input(self):
        with self.assertRaises(ValueError):
            make_srt([{"voiceover":"Hola"}],[])
        with self.assertRaises(ValueError):
            make_srt([{"voiceover":"Hola"}],[0])
        self.assertEqual(timestamp(3661.042),"01:01:01,042")

class VoiceTests(unittest.TestCase):
    def test_sha_pin(self):
        self.assertEqual(len(MODEL_SHA256),64)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"f"
            p.write_bytes(b"abc")
            self.assertEqual(sha256(p),"ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
    def test_corrupt_download_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with patch("tools.voice._download",side_effect=lambda u,p,n:p.write_bytes(b"fake")):
                with self.assertRaisesRegex(RuntimeError,"Checksum"):
                    ensure_voice(d)
    def test_no_silent_fallback(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                synthesize("Hola",Path(d)/"out.wav","other",d)
            with self.assertRaises(ValueError):
                synthesize(" ",Path(d)/"out.wav","piper",d)

if __name__=="__main__":
    unittest.main()
