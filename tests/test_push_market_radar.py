import io
import unittest
from urllib.error import HTTPError
from tools.push_market_radar import upload, HOST

class FakeResponse(io.BytesIO):
    status=201
    def __init__(self):
        super().__init__(b'{"ok":true,"run_id":"market-0123456789","stored_in":"d1","market_study_complete":false,"automatic_publication_allowed":false,"entities_seen":2,"windows_seen":2}')

class UploadTests(unittest.TestCase):
    def setUp(self):
        self.report={"market_study_complete":False,"ready_for_youtube":False}
        self.target="https://"+HOST
        self.token="p"*32

    def test_sends_only_expected_worker_with_token(self):
        calls=[]
        def opener(req,timeout):
            calls.append(req)
            self.assertEqual(timeout,25)
            return FakeResponse()
        result=upload(self.report,base_url=self.target,token=self.token,opener=opener)
        self.assertEqual(result["stored_in"],"d1")
        self.assertEqual(len(calls),1)
        self.assertEqual(calls[0].get_method(),"POST")
        self.assertTrue(calls[0].full_url.endswith("/api/market/ingest"))
        self.assertEqual(calls[0].get_header("Authorization"),"Bearer "+self.token)

    def test_rejects_wrong_host_or_missing_token_without_sending(self):
        def opener(req,timeout):
            self.fail("Request inesperado")
        for base in ("http://"+HOST,"https://evil.example","https://"+HOST+".bad.example",
                     "https://"+HOST+"/other","https://"+HOST+"?query=1"):
            with self.assertRaises(ValueError):
                upload(self.report,base_url=base,token=self.token,opener=opener)
        with self.assertRaises(ValueError):
            upload(self.report,base_url=self.target,token="short",opener=opener)

    def test_non_provisional_report_is_rejected(self):
        with self.assertRaises(ValueError):
            upload({"market_study_complete":True,"ready_for_youtube":False},
                   base_url=self.target,token=self.token)

    def test_http_failures_are_sanitized(self):
        def opener(req,timeout):
            raise HTTPError(req.full_url,401,"Access denied",None,None)
        with self.assertRaisesRegex(RuntimeError,"HTTP 401"):
            upload(self.report,base_url=self.target,token=self.token,opener=opener)

if __name__=="__main__":
    unittest.main()
