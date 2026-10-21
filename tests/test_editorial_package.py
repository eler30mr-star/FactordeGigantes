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
