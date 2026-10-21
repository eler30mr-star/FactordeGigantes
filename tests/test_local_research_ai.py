"""Comprobar límites del redactor Qwen sin cargar pesos ni GPU."""
import unittest
from tools.local_research_ai import build_messages, result_metadata, audit_numeric_support


def report(matches=True):
    return {
        "topic": "BlackBerry: historia pendiente de verificación",
        "production_ready": False, "facts_verified_automatically": 0,
        "candidate_claims": [
            {"id":"C01", "proposition":"BlackBerry cambió de actividad en 2016.",
             "candidate_passages":[{"source_id":"S01","url":"https://www.blackberry.com/",
              "excerpt":"BlackBerry announced its transition to software in 2016."}] if matches else []}
        ]
    }


class LocalResearchAITests(unittest.TestCase):
    def test_prompt_has_evidence_and_safety_instructions(self):
        messages=build_messages(report())
        self.assertEqual(messages[0]["role"],"system")
        self.assertIn("No inventes", messages[0]["content"])
        self.assertIn("[S01]", messages[1]["content"])
        self.assertIn("BlackBerry", messages[1]["content"])

    def test_absent_sources_must_not_generate_story(self):
        with self.assertRaises(ValueError):
            build_messages(report(matches=False))

    def test_no_approved_input(self):
        x=report()
        x["production_ready"]=True
        with self.assertRaises(ValueError):
            build_messages(x)
        x["production_ready"]=False
        x["facts_verified_automatically"]=1
        with self.assertRaises(ValueError):
            build_messages(x)

    def test_model_output_cannot_be_marked_verified_or_publishable(self):
        text="Apertura: investigar el cambio de negocio de BlackBerry [S01]. "+(
            "Este es solo un borrador que requiere confirmar las fuentes y evidencias. " * 2
        )
        metadata=result_metadata(report(),text,model_id="Qwen/Qwen3-0.6B",seconds=2.3)
        self.assertFalse(metadata["approved_for_render"])
        self.assertFalse(metadata["approved_for_youtube"])
        self.assertFalse(metadata["claim_verification_automatic"])
        self.assertEqual(metadata["source_markers_in_output"],["[S01]"])
        self.assertFalse(metadata["unsupported_source_ids"])

    def test_catches_fabricated_date_from_real_blackberry_passage(self):
        historical = report()
        historical["candidate_claims"][0]["candidate_passages"][0]["excerpt"] = (
            "Research In Motion's IPO on the Toronto Stock Exchange was October 28, 1997."
        )
        fake = "La salida a bolsa ocurrió el 10 de octubre de 1997 [S01]."
        flags = audit_numeric_support(historical, fake)
        self.assertEqual(len(flags), 1)
        self.assertIn("10", flags[0]["numeric_tokens_not_in_passages"])
        meta = result_metadata(historical, fake + " Pendiente de contrastar la documentación primaria."*2,
                               model_id="Qwen/Qwen3-0.6B", seconds=1)
        self.assertFalse(meta["grounding_quality_gate_passed"])
        self.assertEqual(len(meta["numeric_claims_without_passage_support"]), 1)

    def test_supported_date_still_does_not_equal_fact_verification(self):
        historical = report()
        historical["candidate_claims"][0]["candidate_passages"][0]["excerpt"] = (
            "Research In Motion IPO was on October 28, 1997."
        )
        flags = audit_numeric_support(historical, "Según la fuente, ocurrió el 28 de octubre de 1997 [S01].")
        self.assertEqual(flags, [])

    def test_unsupported_citations_are_flagged_not_silently_accepted(self):
        text="Un texto de prueba que menciona [S99] sin soporte y [S01] con pasaje. "*3
        metadata=result_metadata(report(),text,model_id="Qwen/Qwen3-0.6B",seconds=1)
        self.assertEqual(metadata["unsupported_source_ids"],["[S99]"])


if __name__ == "__main__":
    unittest.main()
