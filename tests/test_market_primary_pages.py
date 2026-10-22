"""Pruebas del salto página P856 -> páginas de inversores, sin red real."""
import hashlib
import unittest
from unittest.mock import patch
from tools.market_primary_pages import eligible_pages,collect_primary_pages

def report():
    return {"provider":"wikidata_p856_safe_official_fetch_v1","collected_on":"2026-10-21",
      "primary_facts_verified":0,"ready_for_youtube":False,
      "evidence":[{"wikidata_id":"Q53268","company":"Empresa ejemplo",
        "status":"candidate_page_readable",
        "resolved_url":"https://global.example.org/",
        "document_link_candidates":[
          {"url":"https://global.example.org/investors/financial-results",
           "document_fetched":False,"ownership_verified":False},
          {"url":"https://elsewhere.example/investors/annual",
           "document_fetched":False,"ownership_verified":False},
          {"url":"https://global.example.org/annual.pdf",
           "document_fetched":False,"ownership_verified":False}]}]}

class PrimaryPageTests(unittest.TestCase):
    def test_only_observed_non_pdf_same_hostname(self):
        candidates=eligible_pages(report())
        self.assertEqual(len(candidates),1)
        self.assertEqual(candidates[0]["url"],
                         "https://global.example.org/investors/financial-results")

    def test_extracts_documentary_paragraph_hash_and_company(self):
        body=b"<html><p>Source fixture only</p></html>"
        useful=("The manufacturing company released its 2024 annual report on acquisition "
                "operations and financial results, which still require independent verification.")
        with patch("tools.market_primary_pages.extract_blocks",return_value=[
            "Accept cookies and view privacy policy information",
            useful
        ]):
            result=collect_primary_pages(report(),fetcher=lambda url,timeout:(body,url,"text/html"))
        self.assertEqual(result["attempted"],1)
        self.assertEqual(result["usable"],1)
        item=result["pages"][0]
        self.assertEqual(item["wikidata_id"],"Q53268")
        self.assertEqual(item["short_excerpt"],useful)
        self.assertEqual(item["content_sha256"],hashlib.sha256(body).hexdigest())
        self.assertFalse(item["facts_verified"])
        self.assertFalse(item["rights_verified"])

    def test_cross_domain_redirect_is_refused(self):
        result=collect_primary_pages(report(),fetcher=lambda url,timeout:(
            b"<html><p>una pagina comercial</p></html>",
            "https://evil.example.org/redirected","text/html"))
        self.assertEqual(result["usable"],0)
        self.assertEqual(result["pages"][0]["status"],"unreachable")
        self.assertIsNone(result["pages"][0]["content_sha256"])

    def test_no_unverified_links_or_empty_sources(self):
        data=report()
        data["evidence"][0]["document_link_candidates"][0]["ownership_verified"]=True
        self.assertEqual(eligible_pages(data),[])
        out=collect_primary_pages(data,fetcher=lambda *args,**kwargs:
                                  self.fail("Not allowed to fetch unverified links"))
        self.assertEqual(out["pages"],[])
        self.assertEqual(out["attempted"],0)

if __name__=="__main__":
    unittest.main()
