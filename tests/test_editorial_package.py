"""Dossier unificado offline: no aprobación automática ni hechos inventados."""
import json
from pathlib import Path
import tempfile
import unittest
from tools import editorial_package as pack

def fixtures():
    research={
        "topic":"Apple: cambios estratégicos","fetched_count":1,
        "sources":[{"source_id":"S01","status":"fetched"}],
        "candidate_claims":[
            {"id":"C01","proposition":"Una fecha de lanzamiento por comprobar",
             "candidate_passages":[{"source_id":"S01",
              "url":"https://www.apple.com/newsroom/",
              "locator":"Bloque web 3","excerpt":"Una cronología sin cifras."}]},
            {"id":"C02","proposition":"Ingresos de una empresa aún no verificados",
             "candidate_passages":[]},
        ]
    }
    audit={"findings":[
        {"claim_id":"C01","possible_issue_flags":["sin_contraste_de_dos_dominios"]},
        {"claim_id":"C02","possible_issue_flags":["sin_pasaje_rastreable"]},
    ]}
    edgar={"entities":[{"filing_candidates":[{"form":"10-K","facts_verified":0}]}]}
    finance={"status":"retrieved_structured_candidates","analysis":{
        "observation_count":2,"comparison":{"comparisons":[{"classification":"same_period_different_reported_values_review_required"}]}}}
    return research,audit,edgar,finance

class PackageTests(unittest.TestCase):
    def test_all_sources_and_financial_risks_are_marked_pending(self):
        res=pack.summarize(*fixtures())
        self.assertEqual(res["claim_count"],2)
        self.assertEqual(res["sec_candidate_documents"],1)
        self.assertEqual(res["xbrl_observation_count"],2)
        self.assertEqual(res["same_period_discrepancy_candidates"],1)
        self.assertEqual(res["verified_claims"],0)
        self.assertFalse(res["ready_for_render"])
        self.assertFalse(res["voice_rights_verified"])
        self.assertEqual(res["claims"][0]["candidate_evidence"][0]["verification_status"],"candidate_unchecked")
        self.assertIn("licencias", " ".join(res["blockers"]).lower())
        text=pack.to_markdown(res)
        self.assertIn("C02",text)
        self.assertIn("No hay evidencia documental vinculada.",text)
        self.assertIn("No enviar a render",text)

    def test_real_pdf_financial_candidates_appear_with_pages_and_warning(self):
        research,audit,edgar,finance=fixtures()
        originals={
            "facts":[
                {"id":"BB24_REV_ORIGINAL","metric":"total_company_revenue",
                 "source_url":"https://irp.cdn-website.com/2024.pdf","pdf_page":2,
                 "value_millions_usd":"853","period_end":"2024-02-29",
                 "accounting_scope":"old_basis",
                 "machine_matched_original_pdf":True,"human_verified":False},
                {"id":"BB24_REV_RECAST","metric":"total_company_revenue",
                 "source_url":"https://irp.cdn-website.com/2025.pdf","pdf_page":16,
                 "value_millions_usd":"759.1","period_end":"2024-02-29",
                 "accounting_scope":"recast_after_cylance",
                 "machine_matched_original_pdf":True,"human_verified":False}
            ],
            "comparability_warning":"Different reporting scopes: compare only after checking restatements."
        }
        summary=pack.summarize(research,audit,edgar,finance,originals)
        self.assertEqual(len(summary["corporate_pdf_facts_located"]),2)
        self.assertEqual(summary["corporate_pdf_facts_human_verified"],0)
        self.assertFalse(summary["ready_for_render"])
        self.assertFalse(summary["ready_for_youtube"])
        self.assertEqual(summary["corporate_pdf_facts_located"][1]["pdf_page"],16)
        markdown=pack.to_markdown(summary)
        self.assertIn("BB24_REV_RECAST",markdown)
        self.assertIn("ADVERTENCIA DE COMPARABILIDAD",markdown)

    def test_no_sec_or_no_xbrl_never_claim_readiness(self):
        r,a,_,_=fixtures()
        res=pack.summarize(r,a)
        self.assertEqual(res["xbrl_status"],"not_queried")
        self.assertEqual(res["sec_candidate_documents"],0)
        self.assertFalse(res["ready_for_narration"])
        self.assertTrue(any("XBRL" in item for item in res["blockers"]))

    def test_claim_without_audit_does_not_silently_disappear(self):
        r,a,*_=fixtures()
        a["findings"].pop()
        with self.assertRaisesRegex(ValueError,"Cada afirmación"):
            pack.summarize(r,a)

    def test_disk_consolidation_creates_two_documents_and_keeps_sources(self):
        r,a,e,f=fixtures()
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            for name,obj in [("reporte_investigacion.json",r),
                            ("AUDITORIA_EDITORIAL.json",a),
                            ("sec_edgar_documentos_candidatos.json",e),
                            ("METRICAS_SEC_CANDIDATAS_NO_VERIFICADAS.json",f)]:
                (root/name).write_text(json.dumps(obj),encoding="utf-8")
            result=pack.consolidate(root)
            self.assertEqual(result["claim_count"],2)
            self.assertTrue((root/"EXPEDIENTE_PARA_REVISOR.md").is_file())
            report=json.loads((root/"EXPEDIENTE_EDITORIAL_PENDIENTE.json").read_text(encoding="utf-8"))
            self.assertFalse(report["ready_for_youtube"])

if __name__=="__main__":
    unittest.main()
