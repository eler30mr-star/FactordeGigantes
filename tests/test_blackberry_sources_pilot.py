"""BlackBerry: PDFs oficiales, páginas y valores sin inventar hechos.

Fixtures simulan la extracción textual; la descarga real se prueba separadamente
en GitHub Actions y nunca se confunde con estos tests.
"""
import unittest
from tools import blackberry_sources_pilot as pilot

RAW=b"%PDF-1.5\nfixture"
def reader(_, **kwargs):
    return [
        "Full Year Fiscal 2024 Financial Highlights. Total company revenue was $853 million, including $218 million relating to the sale of legacy patent portfolio in Q1.",
        "Full Year Fiscal 2025 Financial Highlights. Total company revenue for the full fiscal year was $534.9 million. QNX revenue for the full fiscal year grew 10% year-over-year and hit the top-end of guidance at $236.0 million.",
        "Adjusted EBITDA $84.2 $141.7. Revenue $534.9 $759.1. Adjusted operating income.",
    ],[2,2,16],19

class PilotTest(unittest.TestCase):
    def test_candidate_values_and_pages_from_two_docs(self):
        source_files={s["id"]:(RAW,s["url"],"application/pdf") for s in pilot.SOURCES}
        def source_reader(raw):
            if reader(raw)[2]!=19:raise AssertionError()
            blocks,pages,total=reader(raw)
            return blocks,pages,total
        # One 2024 page and two 2025 pages. Same URL/document length is not a validation flag.
        def expected_reader(raw):
            return source_reader(raw)
        result=pilot.scan(source_files,reader=expected_reader)
        self.assertEqual(result["facts_located"],5)
        self.assertEqual(result["verified_by_human"],0)
        self.assertFalse(result["ready_for_youtube"])
        self.assertFalse(result["filming_rights_verified"])
        self.assertTrue(all(not f["human_verified"] for f in result["facts"]))
        self.assertEqual(set(f["pdf_page"] for f in result["facts"]),{2,16})

    def test_missing_documents_never_yield_facts(self):
        result=pilot.scan({},reader=lambda raw: (_ for _ in ()).throw(AssertionError()))
        self.assertEqual(result["facts_located"],0)
        self.assertEqual(len(result["missing_evidence_ids"]),len(pilot.FACTS))
        self.assertTrue(all(s["download_status"]=="unavailable" for s in result["documents"]))

    def test_wrong_url_or_html_type_rejected(self):
        s=pilot.SOURCES[0]
        result=pilot.scan({s["id"]:(RAW,"https://example.net/fake.pdf","application/pdf")},reader=reader)
        self.assertEqual(result["facts_located"],0)
        result=pilot.scan({s["id"]:(RAW,s["url"],"text/html")},reader=reader)
        self.assertEqual(result["facts_located"],0)

    def test_2024_recast_number_not_confused_with_original_number(self):
        s=pilot.SOURCES[1]
        result=pilot.scan({s["id"]:(RAW,s["url"],"application/pdf")},reader=reader)
        facts={f["id"]:f for f in result["facts"]}
        self.assertEqual(facts["BB24_REV_RECAST"]["value_millions_usd"],"759.1")
        self.assertNotIn("BB24_REV_ORIGINAL",facts)
        self.assertIn("different reporting scopes",result["comparability_warning"])

if __name__=="__main__":
    unittest.main()
