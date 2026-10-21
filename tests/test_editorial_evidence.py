"""Contratos de evidencia documental: no consultas web ni permisos de publicar."""
import copy
import unittest
from tools.editorial_evidence import validate_dossier

GOOD = {
    "title": "Factor de Gigantes: expediente de investigación",
    "thesis": "Este expediente demuestra el control editorial sin afirmar hechos empresariales externos.",
    "publication_authorized": False,
    "sources": [
        {"id": "S01", "url": "https://www.sec.gov/edgar/search/", "publisher": "SEC",
         "accessed_on": "2026-10-20", "type": "primaria"},
        {"id": "S02", "url": "https://www.wipo.int/", "publisher": "WIPO",
         "accessed_on": "2026-10-20", "type": "secundaria"},
    ],
    "claims": [
        {"id": "C01", "text": "Afirmación hipotética pendiente de atribución a un documento específico.",
         "evidence": [{"source_id": "S01", "locator": "Documento por localizar",
                       "status": "pendiente"}]},
    ],
    "assets": [{"kind": "imagen", "description": "Imagen de prueba, sin licencia acreditada",
                "rights_status": "pendiente"}],
}


class EditorialEvidenceTests(unittest.TestCase):
    def test_pending_dossier_never_allows_publication(self):
        result = validate_dossier(copy.deepcopy(GOOD))
        self.assertFalse(result["automated_publication_authorized"])
        self.assertFalse(result["can_release_documentary"])
        self.assertEqual(result["claims_pending_or_rejected"], 1)
        self.assertEqual(result["assets_pending_rights"], 1)

    def test_even_approved_claim_does_not_publish(self):
        data = copy.deepcopy(GOOD)
        data["claims"][0]["evidence"][0]["status"] = "verificada"
        data["claims"][0]["reviewed_by"] = "Revisión editorial registrada"
        data["assets"][0]["rights_status"] = "verificado"
        result = validate_dossier(data)
        self.assertEqual(result["claims_reviewed_with_sources"], 1)
        self.assertFalse(result["can_release_documentary"])

    def test_blocks_missing_traceability_and_automatic_publication(self):
        variants = []
        d = copy.deepcopy(GOOD)
        d["publication_authorized"] = True
        variants.append(d)
        d = copy.deepcopy(GOOD)
        d["claims"][0]["evidence"][0]["source_id"] = "S99"
        variants.append(d)
        d = copy.deepcopy(GOOD)
        d["sources"][0]["url"] = "http://localhost/admin"
        variants.append(d)
        d = copy.deepcopy(GOOD)
        d["claims"][0]["evidence"] = []
        variants.append(d)
        d = copy.deepcopy(GOOD)
        d["sources"][1]["id"] = "S01"
        variants.append(d)
        for bad in variants:
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    validate_dossier(bad)


if __name__ == "__main__":
    unittest.main()
