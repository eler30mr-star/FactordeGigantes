"""EDGAR: CIК y metadatos regulatorios; pruebas offline sin consultar SEC."""
import json
import unittest
from tools import edgar_discovery as ed

def fake_fetch(url):
    if "list=search" in url:
        obj={"query":{"search":[{"title":"Apple Inc."}]}}
    elif "prop=pageprops" in url:
        obj={"query":{"pages":[{"pageprops":{"wikibase_item":"Q312"}}]}}
    elif "wbgetentities" in url:
        obj={"entities":{"Q312":{"claims":{"P5531":[
            {"mainsnak":{"datavalue":{"value":"320193"}}}
        ]}}}}
    elif url=="https://data.sec.gov/submissions/CIK0000320193.json":
        obj={"name":"Apple Inc.","filings":{"recent":{
            "form":["10-K","10-Q","NOT-A-FILING","10-K"],
            "accessionNumber":["0000320193-24-000123","0000320193-25-000019","bad","0000320193-23-000106"],
            "primaryDocument":["aapl-20240928.htm","aapl-20241228.htm","bad.pdf","../../etc/passwd"],
            "filingDate":["2024-11-01","2025-01-31","2025-02-01","2023-11-01"]
        }}}
    else:
        raise AssertionError("Unexpected URL "+url)
    return json.dumps(obj).encode("utf-8"),url,"application/json"

class EdgarTests(unittest.TestCase):
    def test_wikidata_identifier_is_candidate_only(self):
        self.assertEqual(ed.sec_cik_candidate("Q312",fake_fetch),"0000320193")
        with self.assertRaises(ValueError):
            ed.sec_cik_candidate("Q312/../../secret",fake_fetch)

    def test_sec_metadata_filters_unsafe_documents_and_formats(self):
        report=ed.sec_filings("0000320193",fake_fetch)
        self.assertEqual(report["company_name_reported"],"Apple Inc.")
        self.assertEqual(len(report["filing_candidates"]),2)
        first=report["filing_candidates"][0]
        self.assertEqual(first["form"],"10-K")
        self.assertEqual(first["filing_date"],"2024-11-01")
        self.assertEqual(first["document_url"],
            "https://www.sec.gov/Archives/edgar/data/320193/000032019324000123/aapl-20240928.htm")
        self.assertFalse(first["document_content_fetched"])
        self.assertEqual(first["facts_verified"],0)

    def test_discover_auto_identifies_sec_leads_without_approving(self):
        r=ed.discover_sec_leads("Apple Inc.",fake_fetch)
        self.assertEqual(r["candidate_ciks"],1)
        self.assertEqual(r["filing_candidates"],2)
        self.assertEqual(r["entities"][0]["wikidata_item"],"Q312")
        self.assertEqual(r["entities"][0]["cik_candidate"],"0000320193")
        self.assertEqual(r["entities"][0]["status"],"sec_filings_listed")
        self.assertFalse(r["automatic_fact_verification"])
        self.assertFalse(r["publication_authorized"])

    def test_sec_403_keeps_identifier_but_no_invented_filings(self):
        def forbidden(url):
            if url.startswith("https://data.sec.gov/"):
                raise OSError("403 Forbidden")
            return fake_fetch(url)
        r=ed.discover_sec_leads("Apple Inc.",forbidden)
        self.assertEqual(r["candidate_ciks"],1)
        self.assertEqual(r["filing_candidates"],0)
        self.assertEqual(r["entities"][0]["fetch_error_type"],"OSError")
        self.assertEqual(r["entities"][0]["status"],"cik_candidate_from_wikidata")

    def test_invalid_ciks_disallowed(self):
        for cik in ["320193","0000/20193","http://x","000000000a","a"*10]:
            with self.assertRaises(ValueError):
                ed.sec_filings(cik,fetcher=fake_fetch)

    def test_no_p5531_no_sec_request(self):
        def no_cik(url):
            if "wbgetentities" in url:
                return json.dumps({"entities":{"Q312":{"claims":{}}}}).encode(),url,"application/json"
            return fake_fetch(url)
        r=ed.discover_sec_leads("Apple Inc.",no_cik)
        self.assertEqual(r["filing_candidates"],0)
        self.assertEqual(r["candidate_ciks"],0)

if __name__=="__main__":
    unittest.main()
