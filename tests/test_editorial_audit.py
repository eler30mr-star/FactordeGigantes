"""Pruebas offline: auditoría editorial y estructura 10:00."""
import json
from pathlib import Path
import tempfile
import unittest

from tools.editorial_audit import audit_report, build_documentary_beat_sheet, save_audit

def base_report():
    return {
        "topic": "BlackBerry: una transformación que requiere contrastar",
        "engine_version": "0.1",
        "sources": [
            {"source_id": "S01", "source_class": "secondary_discovery_not_primary"},
            {"source_id": "S02", "source_class": "unknown"},
        ],
        "candidate_claims": [
            {"id": "C01", "segment_index": 1, "proposition": "La empresa fue fundada en 1984.",
             "candidate_passages": [
                 {"source_id": "S01", "url": "https://es.wikipedia.org/wiki/BlackBerry",
                  "excerpt": "La empresa, fundada en 1985 según esta referencia, experimentó transformaciones."}
             ]},
            {"id": "C02", "segment_index": 2, "proposition": "En 2016 hizo un cambio significativo.",
             "candidate_passages": [
                 {"source_id": "S02", "url": "https://www.empresa.test/noticias",
                  "excerpt": "En 2016 hizo un cambio significativo y el comunicado explica su dirección."},
                 {"source_id": "S01", "url": "https://es.wikipedia.org/wiki/Historia",
                  "excerpt": "En 2016 el grupo avanzó en una nueva dirección anunciada oficialmente."}
             ]},
            {"id": "C03", "segment_index": 3, "proposition": "Se investigará la evolución sin afirmar fechas.",
             "candidate_passages": []}
        ],
    }

class EditorialAuditTests(unittest.TestCase):
    def test_no_automatic_approval_and_numeric_risk(self):
        audit = audit_report(base_report())
        self.assertEqual(audit["claim_count"], 3)
        self.assertFalse(audit["ready_for_render"])
        self.assertFalse(audit["ready_for_youtube"])
        self.assertEqual(audit["human_verified_claims"],0)
        first = audit["findings"][0]
        self.assertIn("numeros_no_coinciden_en_un_pasaje",first["possible_issue_flags"])
        self.assertIn("anos_de_fuentes_difieren_revisar_contexto",first["possible_issue_flags"])
        self.assertIn("fuente_secundaria_requiere_primaria",first["possible_issue_flags"])
        self.assertFalse(first["numeric_alignment_in_passage"])
        self.assertEqual(audit["findings"][1]["numeric_alignment_in_passage"],True)
        self.assertIn("sin_pasaje_rastreable",audit["findings"][2]["possible_issue_flags"])
        self.assertTrue(all(item["verified"] is False for item in audit["findings"]))

    def test_timing_and_all_claims_present_without_made_up_script(self):
        report=base_report()
        audit=audit_report(report)
        sheet=build_documentary_beat_sheet(report,audit)
        self.assertEqual(sheet.count("### "),12)
        self.assertIn("10:00",sheet)
        self.assertIn("C01",sheet)
        self.assertIn("C03",sheet)
        self.assertNotIn("La empresa fue fundada en 1984",sheet)
        self.assertIn("PENDIENTE",sheet)
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)
            saved=save_audit(report,path)
            self.assertTrue((path/"AUDITORIA_EDITORIAL.json").is_file())
            self.assertTrue((path/"ESCALETA_DOCUMENTAL_10MIN_NO_APROBADA.md").is_file())
            self.assertEqual(json.loads((path/"AUDITORIA_EDITORIAL.json").read_text())["claim_count"],3)
            self.assertFalse(saved["ready_for_youtube"])

    def test_invalid_claim_ids_fail_without_writing_approval(self):
        report=base_report()
        report["candidate_claims"][1]["id"]="C01"
        with self.assertRaisesRegex(ValueError,"repetido"):
            audit_report(report)

    def test_disallow_non_https_excerpts_from_counting_as_evidence(self):
        report=base_report()
        report["candidate_claims"][1]["candidate_passages"]=[{
            "source_id":"S02","url":"http://10.0.0.1/file","excerpt":"En 2016 hizo un cambio."}]
        audit=audit_report(report)
        self.assertIn("sin_pasaje_rastreable",audit["findings"][1]["possible_issue_flags"])
        self.assertEqual(audit["findings"][1]["evidence_source_ids"],[])

    def test_actual_blackberry_research_report_compatible(self):
        path=Path(__file__).resolve().parents[1]/"research"/"blackberry"/"reporte_primera_prueba.json"
        if path.is_file():
            report=json.loads(path.read_text(encoding="utf-8"))
            audit=audit_report(report)
            self.assertEqual(audit["claim_count"],len(report["candidate_claims"]))
            self.assertFalse(audit["ready_for_render"])

if __name__=="__main__":
    unittest.main()
