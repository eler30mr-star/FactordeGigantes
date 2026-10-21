"""Pruebas sin llamadas a proveedores ni costes para investigador común."""
import json
import unittest
from tools import research_providers as p

REPORT={
    "candidate_claims":[
        {"id":"C01","candidate_passages":[
            {"source_id":"S01","url":"https://blackberry.com/news", "page":2,
             "excerpt":"BlackBerry announced a strategic transition in 2016."}
        ]}
    ]
}

class ProviderTests(unittest.TestCase):
    def test_extract_actual_evidence_and_no_unsupported_source(self):
        evidence=p.collect_evidence(REPORT)
        self.assertEqual(len(evidence),1)
        self.assertEqual(evidence[0]["id"],"E001")
        self.assertEqual(evidence[0]["url"],"https://blackberry.com/news")
        self.assertEqual(evidence[0]["page"],2)
        self.assertRaises(ValueError,p.collect_evidence,{"candidate_claims":[]})

    def test_qwen_contract_blocks_hallucinated_citations(self):
        ev=p.collect_evidence(REPORT)
        good=json.dumps({"claims":[{"statement":"BlackBerry announced a change in 2016.","evidence_ids":["E001"]}],
                         "missing_questions":["What else changed?"]})
        result=p.run_qwen_local("BlackBerry",ev,generate=lambda _:good)
        self.assertEqual(result["candidate_claims"][0]["evidence_ids"],["E001"])
        self.assertEqual(result["provider"],"qwen_local")
        self.assertFalse(result["ready_for_script"])
        self.assertEqual(result["facts_verified_automatically"],0)
        bad=good.replace("E001","E999")
        with self.assertRaises(ValueError):
            p.run_qwen_local("BlackBerry",ev,generate=lambda _:bad)

    def test_gemini_requires_opt_in_and_secret(self):
        ev=p.collect_evidence(REPORT)
        with self.assertRaisesRegex(RuntimeError,"modalidad gratuita"):
            p.run_gemini_free("BlackBerry",ev,api_key="a"*20)
        with self.assertRaisesRegex(RuntimeError,"GEMINI_API_KEY"):
            p.run_gemini_free("BlackBerry",ev,api_key="",free_tier_confirmed=True)
        with self.assertRaises(ValueError):
            p.run_gemini_free("BlackBerry",ev,api_key="a"*20,
                              model="gemini-advanced-paid",free_tier_confirmed=True)

    def test_gemini_rest_contract_and_safe_metadata(self):
        ev=p.collect_evidence(REPORT)
        response_text=json.dumps({
            "claims":[{"statement":"BlackBerry announced a change in 2016.","evidence_ids":["E001"]}],
            "missing_questions":[]
        })
        def mock_request(url,body,headers):
            self.assertEqual(url,p.ENDPOINT+"gemini-2.5-flash:generateContent")
            self.assertEqual(headers["x-goog-api-key"],"a"*24)
            self.assertEqual(body["generationConfig"]["responseMimeType"],"application/json")
            self.assertIn("BlackBerry",body["contents"][0]["parts"][0]["text"])
            return {"candidates":[{"content":{"parts":[{"text":response_text}]}}]}
        result=p.run_gemini_free("BlackBerry",ev,api_key="a"*24,
            free_tier_confirmed=True,transport=mock_request)
        self.assertEqual(result["provider"],"gemini_free")
        self.assertEqual(len(result["prompt_sha256"]),64)
        self.assertFalse(result["ready_for_youtube"])
        self.assertFalse(result["charged_api_calls_verified_free"])
        self.assertNotIn("a"*24,json.dumps(result))

    def test_model_response_must_be_json_and_valid_evidence(self):
        ev=p.collect_evidence(REPORT)
        for text in ("not JSON","{}",'{"claims":[]}', '{"claims":[{"statement":"invented fact","evidence_ids":["E999"]}],"missing_questions":[]}'):
            with self.assertRaises(ValueError):
                p.parse_candidate_output(text,ev,"qwen_local")

if __name__=="__main__":
    unittest.main()
