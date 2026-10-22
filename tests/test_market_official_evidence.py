"""Fixtures de página corporativa: texto sintético, sin atribuirle realidad."""
import unittest
from unittest.mock import patch
from tools.market_official_evidence import collect_official_evidence,candidates_from_reports
def reports():
    w={"method":"wikimedia_wikidata_company_discovery_v1","collected_on":"2026-10-21",
       "candidates":[{"wikidata_id":"Q221062","topic":"Empresa documental de prueba",
       "official_website_candidate":"https://www.example.org/"}]}
    n={"provider":"wikidata_news_company_resolution_v1","collected_on":"2026-10-21",
       "candidates":[{"wikidata_id":"Q53268","matched_name":"Toyota",
       "official_website_candidate":"https://global.toyota/"}]}
    return w,n
class OfficialEvidence(unittest.TestCase):
    def test_collects_bounded_official_candidate_without_validating_claims(self):
        w,n=reports()
        calls=[]
        def fetch(url,*,timeout):
            calls.append((url,timeout))
            return (b'<html><p>Official example text for an invented annual operations '
                    b'report and general business activities.</p>'
                    b'<a href="/investors/report.pdf">Annual report</a></html>',url,"text/html")
        result=collect_official_evidence(w,n,fetcher=fetch)
        self.assertEqual(result["attempted"],2)
        self.assertEqual(result["readable"],2)
        self.assertTrue(all(x["content_sha256"] for x in result["evidence"]))
        self.assertTrue(all(x["facts_verified"]==0 for x in result["evidence"]))
        self.assertTrue(all(x["source_identity_verified"] is False for x in result["evidence"]))
        self.assertTrue(all(not x["publication_authorized"] for x in result["evidence"]))
        self.assertEqual(len(calls),2)
        self.assertTrue(all(timeout==12 for _,timeout in calls))
    def test_substantive_excerpt_beats_navigation_from_realistic_html(self):
        w,n=reports()
        text="El informe institucional recoge hechos empresariales que deben corroborarse " \
             "con otros documentos y con el contexto histórico antes de narrarlos."
        with patch("tools.market_official_evidence.extract_blocks",
                   return_value=["Aviso de cookies",text]):
            result=collect_official_evidence(w,n,
                fetcher=lambda url,timeout:(b"<html><body>Ejemplo</body></html>",url,"text/html"))
        self.assertEqual(result["readable"],2)
        self.assertEqual(result["evidence"][0]["short_excerpt"],text)
        self.assertFalse(result["evidence"][0]["source_identity_verified"])

    def test_filters_cookie_banners_and_prefers_business_events(self):
        from tools.market_official_evidence import select_documentary_excerpt
        promo="Accept cookies and subscribe to our newsletter to discover our services, advertising and privacy policy details on this site."
        substantive="In 2024 the manufacturing company published its annual report describing acquisition operations and revenue at production sites."
        excerpt,quality=select_documentary_excerpt([promo,substantive])
        self.assertEqual(excerpt,substantive)
        self.assertEqual(quality,"documentary_candidate")
        missing,quality=select_documentary_excerpt(["Cookies"])
        self.assertEqual(quality,"insufficient_context")
        self.assertEqual(missing,"Cookies")

    def test_rejects_ssrf_urls_and_dedupes_by_canonical_entity(self):
        w,n=reports()
        n["candidates"][0]["official_website_candidate"]="http://localhost/"
        self.assertEqual(len(candidates_from_reports(w,n)),1)
        n["candidates"][0]["official_website_candidate"]="https://global.toyota/"
        w["candidates"].append({"wikidata_id":"Q53268","topic":"Other alias",
          "official_website_candidate":"https://global.toyota/"})
        self.assertEqual(len(candidates_from_reports(w,n)),2)
    def test_remote_failure_is_visible_not_a_made_up_source(self):
        w,n=reports()
        result=collect_official_evidence(w,n,
                 fetcher=lambda u,**kw:(_ for _ in ()).throw(TimeoutError("fixture")))
        self.assertEqual(result["readable"],0)
        self.assertTrue(all(x["content_sha256"] is None for x in result["evidence"]))
        self.assertTrue(all(x["status"]=="candidate_unreachable" for x in result["evidence"]))
    def test_no_candidates_stays_empty(self):
        w,n=reports();w["candidates"]=[];n["candidates"]=[]
        result=collect_official_evidence(w,n,
             fetcher=lambda *args,**kw:self.fail("No hay URL que consultar"))
        self.assertEqual(result["attempted"],0)
        self.assertEqual(result["readable"],0)
if __name__=="__main__":unittest.main()
