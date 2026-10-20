import unittest,tempfile,json,hashlib
from pathlib import Path
from unittest.mock import patch
from tools import approved_voice as v
class ApprovedVoiceTests(unittest.TestCase):
    def test_missing_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):v.approved_reference(d)
    def test_reject_modified_audio(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            (p/v.FILE_NAME).write_bytes(b"not an approved MP3")
            (p/"reference.json").write_text(json.dumps({"status":"approved_by_owner_for_editorial_reference","file":v.FILE_NAME,"sha256":v.SHA,"reference_text":v.TRANSCRIPT}))
            with self.assertRaises(RuntimeError):v.approved_reference(d)
    def test_match_fixture(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);b=b"synthetic unit test content"
            (p/v.FILE_NAME).write_bytes(b)
            h=hashlib.sha256(b).hexdigest()
            (p/"reference.json").write_text(json.dumps({"status":"approved_by_owner_for_editorial_reference","file":v.FILE_NAME,"sha256":h,"reference_text":v.TRANSCRIPT}))
            with patch.object(v,"SHA",h),patch.object(v,"BYTES",len(b)):
                audio,_=v.approved_reference(p)
            self.assertEqual(audio.read_bytes(),b)
