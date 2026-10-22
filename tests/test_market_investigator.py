"""Investigador conectado al radar, pruebas sin modelo ni gasto."""
import unittest
from tools.market_investigator import prepare_evidence,run_investigation

def report(has_fragments=True):
    text=("An original-looking but purely synthetic corporate annual report text "
      "for the testing of provenance, pagination, claims and quality gates.")
    return {"provider":"official_pdf_evidence_v1","verified_claim_count":0,
      "publication_authorized":False,"documents":[
      {"wikidata_id":"Q53268","company":"Empresa de prueba",
       "state":"text_extracted" if has_fragments else "fetch_failed",
       "resolved_url":"https://www.example.org/report.pdf" if has_fragments else None,
       "sha256":"a"*64 if has_fragments else None,
       "fragments":[{"page":3,"excerpt":text,"verification_state":"uncorroborated"}] if has_fragments else []}]}

class InvestigatorTests(unittest.TestCase):
    def test_evidence_passes_url_hash_page_and_same_identifier(self):
        evidence=prepare_evidence(report())
        self.assertEqual(len(evidence),1)
        self.assertEqual(evidence[0]["id"],"E001")
        self.assertEqual(evidence[0]["page"],3)
        self.assertEqual(evidence[0]["document_sha256"],"a"*64)

    def test_never_invokes_provider_without_pdf_or_explicit_free_tier(self):
        def must_not_call(*args,**kwargs):self.fail("Provider accessed without clearance")
        result=run_investigation(report(False),runner=must_not_call,
          free_confirmed=True,api_key="x"*20)
        self.assertEqual(result["status"],"skipped_no_documentary_evidence")
        result=run_investigation(report(),runner=must_not_call,
          free_confirmed=False,api_key="x"*20)
        self.assertEqual(result["status"],"skipped_free_tier_not_authorized")
        self.assertFalse(result["ready_for_script"])

    def test_corporate_homepage_fallback_when_pdf_is_unavailable(self):
        official={"provider":"wikidata_p856_safe_official_fetch_v1",
          "primary_facts_verified":0,"ready_for_youtube":False,
          "evidence":[{"wikidata_id":"Q53268","company":"Toyota",
            "status":"candidate_page_readable",
            "resolved_url":"https://global.toyota/",
            "content_sha256":"b"*64,
            "short_excerpt":"This is synthetic corporate homepage evidence of a business activity "
             "and does not certify its factual content for a video."}]}
        evidence=prepare_evidence(report(False),official_report=official)
        self.assertEqual(len(evidence),1)
        self.assertEqual(evidence[0]["id"],"E001")
        self.assertIsNone(evidence[0]["page"])
        self.assertEqual(evidence[0]["source_class"],"potential_official_primary")
        self.assertEqual(evidence[0]["document_sha256"],"b"*64)
        called=[]
        def stub(*a,**kw):
            called.append(1)
            return {}
        result=run_investigation(report(False),official_report=official,
          free_confirmed=False,api_key=None,runner=stub)
        self.assertEqual(result["status"],"skipped_free_tier_not_authorized")
        self.assertFalse(called)

    def test_researches_one_company_without_mixing_topics(self):
        pdf=report()
        pdf["documents"].append({"wikidata_id":"Q221062","company":"Otra empresa",
          "state":"text_extracted","resolved_url":"https://example.org/other.pdf",
          "sha256":"b"*64,
          "fragments":[{"page":1,"verification_state":"uncorroborated",
            "excerpt":"An original-looking synthetic annual operations narrative for a different company, which must not be attributed to the other company."}]})
        from tools.market_investigator import select_one_company
        all_sources=prepare_evidence(pdf)
        selected,deferred=select_one_company(all_sources)
        chosen=selected[0]["wikidata_id"]
        self.assertIn(chosen,{"Q221062","Q53268"})
        self.assertEqual({e["wikidata_id"] for e in selected},{chosen})
        self.assertEqual(set(deferred),{"Q221062","Q53268"}-{chosen})
        self.assertEqual(selected[0]["id"],"E001")
        def no_external(*args,**kwargs):self.fail("Paid or unauthorized model")
        outcome=run_investigation(pdf,free_confirmed=False,runner=no_external)
        self.assertEqual(outcome["selected_wikidata_id"],chosen)
        self.assertEqual(outcome["deferred_wikidata_ids"],deferred)
        self.assertEqual(len(outcome["evidence_manifest"]),1)

    def test_generic_promotional_excerpt_is_not_used_as_factual_evidence(self):
        official={"provider":"wikidata_p856_safe_official_fetch_v1",
          "primary_facts_verified":0,"ready_for_youtube":False,
          "evidence":[{"wikidata_id":"Q53268","company":"Toyota",
            "status":"candidate_page_readable",
            "resolved_url":"https://global.toyota/",
            "content_sha256":"b"*64,"excerpt_quality":"generic_candidate",
            "short_excerpt":"Discover our brand and read corporate advertising information that is too superficial for a professional documentary investigation."}]}
        sources=prepare_evidence(report(False),official_report=official)
        self.assertEqual(sources,[])
        def must_not_call(*args,**kwargs):self.fail("Never invoke the model for advertising")
        outcome=run_investigation(report(False),official_report=official,
          free_confirmed=True,api_key="x"*20,runner=must_not_call)
        self.assertEqual(outcome["status"],"skipped_no_documentary_evidence")

    def test_investor_report_pages_feed_same_company_evidence_without_api(self):
        secondary={"provider":"official_investor_pages_v1",
          "collected_on":report(False).get("collected_on"),
          "facts_verified":0,"rights_verified":False,"ready_for_youtube":False,
          "pages":[{"wikidata_id":"Q53268","company":"Empresa de prueba",
            "status":"excerpt_candidate","excerpt_quality":"documentary_candidate",
            "resolved_url":"https://example.org/investors/results",
            "origin_url":"https://example.org/",
            "content_sha256":"c"*64,
            "short_excerpt":"In 2024 the company announced annual manufacturing operations and an acquisition, reported in its corporate investor announcement, pending external corroboration."}]}
        # El informe PDF original de tests no tiene fecha; marcar la fecha
        # de ambos informes observados sin inventar datos de mercado.
        pdf=report(False)
        pdf["collected_on"]="2026-10-21"
        secondary["collected_on"]="2026-10-21"
        sources=prepare_evidence(pdf,primary_pages_report=secondary)
        self.assertEqual(len(sources),1)
        self.assertEqual(sources[0]["id"],"E001")
        self.assertEqual(sources[0]["document_sha256"],"c"*64)
        self.assertEqual(sources[0]["wikidata_id"],"Q53268")
        def forbidden(*args,**kwargs):
            self.fail("No Gemini call without free tier")
        result=run_investigation(pdf,primary_pages_report=secondary,
                                  free_confirmed=False,runner=forbidden)
        self.assertEqual(result["status"],"skipped_free_tier_not_authorized")
        self.assertEqual(result["evidence_count"],1)

    def test_valid_candidate_output_propagates_only_unverified_statements(self):
        def model(topic,evidence,**kw):
            self.assertEqual(topic,"Empresa de prueba")
            self.assertEqual(evidence[0]["id"],"E001")
            self.assertTrue(kw["free_tier_confirmed"])
            return {"provider":"gemini_free","candidate_claims":[
              {"statement":"Texto de prueba sin validar","evidence_ids":["E001"],
               "status":"candidate_unverified"}],
              "facts_verified_automatically":0,"ready_for_script":False,
              "ready_for_youtube":False}
        out=run_investigation(report(),free_confirmed=True,api_key="x"*20,runner=model)
        self.assertEqual(out["status"],"candidate_claims_generated")
        self.assertFalse(out["publication_authorized"])
        self.assertNotIn("excerpt",out["input_evidence"][0])

    def test_rejects_false_verified_ai_results(self):
        def bad(*args,**kw):
            return {"facts_verified_automatically":1,"ready_for_script":True,
                    "ready_for_youtube":True}
        with self.assertRaises(ValueError):
            run_investigation(report(),free_confirmed=True,api_key="x"*20,runner=bad)

if __name__=="__main__":unittest.main()
