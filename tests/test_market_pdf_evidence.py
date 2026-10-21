"""Fixtures PDF: ningún extracto se considera hecho ni página real del mercado."""
import unittest,hashlib
from unittest.mock import patch
from tools.market_pdf_evidence import select_pdf_candidates,extract_document_evidence

def report():
    return {"provider":"wikidata_p856_safe_official_fetch_v1",
      "collected_on":"2026-10-21","primary_facts_verified":0,
      "ready_for_youtube":False,"evidence":[
       {"wikidata_id":"Q53268","company":"Toyota",
        "status":"candidate_page_readable","resolved_url":"https://global.toyota/",
        "document_link_candidates":[
         {"url":"https://global.toyota/reports/annual-report.pdf",
          "document_fetched":False,"ownership_verified":False},
         {"url":"https://other.example/annual-report.pdf",
          "document_fetched":False,"ownership_verified":False}]}]}

class PdfEvidence(unittest.TestCase):
    def test_only_same_host_pdf_with_unfetched_rights(self):
        selected=select_pdf_candidates(report())
        self.assertEqual(len(selected),1)
        self.assertEqual(selected[0]["wikidata_id"],"Q53268")
        self.assertEqual(selected[0]["document_url"],"https://global.toyota/reports/annual-report.pdf")

    def test_physical_page_citation_and_hash_are_observed_not_verified(self):
        source=b"%PDF-FAKE-TEST-FIXTURE"
        analysis={"type":"pdf","total_pages":10,"blocks":[
          "Company operations and business reporting under the mock annual report. "
          "This passage exists only in a fixture and is not factual evidence."],
          "page_map":[4]}
        with patch("tools.market_pdf_evidence.analyze_document",return_value=analysis):
            out=extract_document_evidence(report(),fetcher=lambda url,timeout=14:
                (source,url,"application/pdf"))
        self.assertEqual(out["text_extracted"],1)
        doc=out["documents"][0]
        self.assertEqual(doc["sha256"],hashlib.sha256(source).hexdigest())
        self.assertEqual(doc["fragments"][0]["page"],4)
        self.assertEqual(doc["fragments"][0]["block_index"],0)
        self.assertEqual(doc["fragments"][0]["locator"],"PDF página 4, bloque 1")
        self.assertEqual(doc["fragments"][0]["verification_state"],"uncorroborated")
        self.assertEqual(out["verified_claim_count"],0)
        self.assertFalse(out["publication_authorized"])

    def test_network_failure_creates_no_evidence(self):
        out=extract_document_evidence(report(),fetcher=lambda *_args,**_kw:
            (_ for _ in ()).throw(TimeoutError("not reached")))
        self.assertEqual(out["text_extracted"],0)
        self.assertEqual(out["documents"][0]["state"],"fetch_failed")
        self.assertIsNone(out["documents"][0]["sha256"])
        self.assertFalse(out["documents"][0]["fragments"])

    def test_no_official_pdf_is_valid_observation(self):
        data=report();data["evidence"][0]["document_link_candidates"]=[]
        out=extract_document_evidence(data,fetcher=lambda *_args,**_kw:
            self.fail("Unexpected download"))
        self.assertEqual(out["attempted"],0)
        self.assertEqual(out["documents"],[])

if __name__=="__main__":unittest.main()
