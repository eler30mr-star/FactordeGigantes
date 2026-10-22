import unittest
from tools.ai_research_pipeline import evidence_gaps

def e(eid,url,kind="public_document_candidate"):
    return {"id":eid,"url":url,"source_class":kind}

class CorroborationGates(unittest.TestCase):
    def test_same_publisher_three_passages_are_one_document(self):
        sources=[e("E001","https://example.org/news/story"),
                 e("E002","https://example.org/news/story"),
                 e("E003","https://example.org/news/story")]
        claims=[{"evidence_ids":["E001","E002","E003"]}]
        result=evidence_gaps(sources,claims)
        self.assertEqual(result["unique_documents"],1)
        self.assertEqual(result["independent_domains"],1)
        self.assertEqual(result["claims_requiring_review"],1)
        self.assertEqual(result["claim_gaps"][0]["cited_documents"],1)
        self.assertIn("no_independent_domain",result["claim_gaps"][0]["gaps"])
        self.assertFalse(result["all_claims_verified"])

    def test_two_domains_still_require_review_and_regulatory_primary(self):
        result=evidence_gaps([
            e("E001","https://publisher.example/article"),
            e("E002","https://company.example/annual"),
        ],[{"evidence_ids":["E001","E002"]}])
        self.assertEqual(result["independent_domains"],2)
        self.assertNotIn("no_independent_domain",result["claim_gaps"][0]["gaps"])
        self.assertIn("no_regulatory_primary_document",result["claim_gaps"][0]["gaps"])
        self.assertFalse(result["ready_for_script"])

    def test_even_a_regulator_and_independent_report_is_not_automatically_verified(self):
        result=evidence_gaps([
            e("E001","https://www.justice.gov/filing","public_authority_candidate"),
            e("E002","https://reporter.example/article")
        ],[{"evidence_ids":["E001","E002"]}])
        self.assertEqual(result["claim_gaps"][0]["gaps"],[])
        self.assertTrue(result["claim_gaps"][0]["regulatory_primary_cited"])
        self.assertEqual(result["claim_gaps"][0]["verification_state"],"requires_corroboration")
        self.assertFalse(result["all_claims_verified"])
        self.assertFalse(result["ready_for_script"])

if __name__=="__main__":unittest.main()
