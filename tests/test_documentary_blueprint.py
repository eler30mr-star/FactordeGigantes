"""Pruebas del paso investigación real -> plan documental NO aprobado."""
import unittest
from tools.documentary_blueprint import inspect_episode

def fixture(independent=True):
    company="Empresa analizada"
    qid="Q100"
    docs=[
      {"id":"E001","wikidata_id":qid,"company":company,
       "url":"https://www.justice.gov/company-report","document_sha256":"a"*64,
       "source_class":"public_authority_candidate"},
      {"id":"E002","wikidata_id":qid,"company":company,
       "url":"https://newspaper.example/study","document_sha256":"b"*64,
       "source_class":"public_document_candidate"}]
    if not independent:
        docs=docs[:1]
    claims=[]
    reviews=[]
    for n in range(1,7):
        claims.append({"statement":f"Investigación empresarial sobre el hecho número {n} pendiente de revisión editorial independiente.",
                       "status":"candidate_unverified","human_verified":False,
                       "evidence_ids":[d["id"] for d in docs]})
        reviews.append({"claim_index":n,"assessment":"supported_by_excerpt",
                        "evidence_ids":[d["id"] for d in docs]})
    quality={"all_claims_verified":False,"ready_for_script":False,
             "claim_gaps":[{"claim_index":n,"gaps":[] if independent else [
                 "only_one_document","no_independent_domain"]} for n in range(1,7)]}
    analysis={"schema":"fdg_ai_pipeline_v1","selected_wikidata_id":qid,"company":company,
              "candidate_claims":claims,"reviews":reviews,"evidence_manifest":docs,
              "source_quality":quality,"publication_authorized":False,
              "ready_for_script":False,"facts_verified_automatically":0}
    market={"selected_wikidata_id":qid,"research_queue":{"wikidata_id":qid,"title":company}}
    return analysis,market

class StoryboardTests(unittest.TestCase):
    def test_single_news_blocks_all_storytelling(self):
        research,market=fixture(False)
        result=inspect_episode(research,market)
        self.assertEqual(result["status"],"blocked_insufficient_corroboration")
        self.assertEqual(result["scenes"],[])
        self.assertIn("at_least_two_original_documents_required",result["blocking_reasons"])
        self.assertFalse(result["ready_for_render"])
        self.assertFalse(result["publication_authorized"])

    def test_two_sources_yield_only_internal_outline_with_connected_citations(self):
        research,market=fixture(True)
        result=inspect_episode(research,market)
        self.assertEqual(result["status"],"source_grounded_outline_unapproved")
        self.assertEqual(len(result["scenes"]),6)
        self.assertEqual(result["scenes"][0]["start_seconds"],0)
        self.assertEqual(result["scenes"][-1]["end_seconds"],660)
        self.assertTrue(all(x["citation_ids"]==["E001","E002"] for x in result["scenes"]))
        self.assertTrue(all(x["narration_text"] is None for x in result["scenes"]))
        self.assertTrue(all(not x["facts_approved"] for x in result["scenes"]))
        self.assertGreater(result["estimated_narration_words"],1400)
        self.assertFalse(result["factual_approval"])
        self.assertFalse(result["publication_authorized"])

    def test_no_selection_creates_explicit_block_not_workflow_failure(self):
        result=inspect_episode({
            "schema":"fdg_ai_pipeline_v1","selected_wikidata_id":None,
            "ready_for_script":False,"publication_authorized":False,
            "facts_verified_automatically":0},
            {"selected_wikidata_id":None,"research_queue":None})
        self.assertEqual(result["status"],"blocked_no_market_selection")
        self.assertEqual(result["scenes"],[])
        self.assertFalse(result["publication_authorized"])

    def test_groq_uncertainty_blocks_outline(self):
        research,market=fixture(True)
        research["reviews"][2]["assessment"]="insufficient_context"
        result=inspect_episode(research,market)
        self.assertEqual(result["scenes"],[])
        self.assertIn("claim_3_lacks_supported_review",result["blocking_reasons"])

    def test_cross_company_or_nonexistent_citation_rejected(self):
        research,market=fixture(True)
        market["research_queue"]["wikidata_id"]="Q200"
        with self.assertRaises(ValueError):
            inspect_episode(research,market)
        research,market=fixture(True)
        research["candidate_claims"][0]["evidence_ids"]=["E999"]
        with self.assertRaises(ValueError):
            inspect_episode(research,market)

    def test_no_claims_and_no_evidence_do_not_emit_fake_scenes(self):
        research,market=fixture(True)
        research["candidate_claims"]=[]
        research["reviews"]=[]
        research["evidence_manifest"]=[]
        research["source_quality"]["claim_gaps"]=[]
        result=inspect_episode(research,market)
        self.assertEqual(result["scenes"],[])
        self.assertIn("insufficient_distinct_claims",result["blocking_reasons"])

    def test_ai_cannot_mark_itself_factually_approved(self):
        research,market=fixture(True)
        research["facts_verified_automatically"]=1
        with self.assertRaises(ValueError):
            inspect_episode(research,market)

if __name__=="__main__":unittest.main()
