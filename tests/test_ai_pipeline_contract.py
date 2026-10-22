"""Cruza descubrimiento Python, análisis y validador JS real sin red ni IA paga."""
import json
import unittest
from unittest.mock import patch

from tools.ai_clients import FreeClients
from tools.ai_source_discovery import discover_sources
from tools.ai_research_pipeline import (
    analyze_sources, gate_duplicate_research, source_report, validate_report_locally,
)


class PipelineContractTests(unittest.TestCase):
    def test_government_repositories_do_not_gain_regulatory_authority(self):
        from tools.ai_source_discovery import regulatory_host
        for host in ("pubmed.ncbi.nlm.nih.gov", "www.ncbi.nlm.nih.gov", "id.loc.gov",
                     "sec.gov.attacker.example", "notsec.gov"):
            self.assertFalse(regulatory_host(host))
        self.assertTrue(regulatory_host("www.justice.gov"))
        sources, clients = self.discover()
        prior = {**sources["evidence_manifest"][0],
                 "url": "https://pubmed.ncbi.nlm.nih.gov/27018593",
                 "source_class": "public_authority_candidate"}
        selection = {"selected_wikidata_id": "Q100", "research_queue": {
            "wikidata_id": "Q100", "title": "Empresa Ejemplo"},
            "prior_evidence_manifest": [prior]}
        with patch("tools.ai_source_discovery.wikipedia_links", return_value=[{
                "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4855945",
                "title": "Empresa Ejemplo", "discovered_by": "wikipedia_external_links"}]):
            result = discover_sources(selection, clients=clients,
                document_fetcher=lambda url, **_: (
                    ("<p>" + prior["excerpt"] + "</p>").encode(), url, "text/html"))
        self.assertEqual(len(result["evidence_manifest"]), 2)
        self.assertTrue(all(e["source_class"] == "public_document_candidate"
                            for e in result["evidence_manifest"]))
        self.assertEqual(result["retrieval_budget"]["public_authority_domains_with_text"], 0)
        validate_report_locally(source_report(result))

    def discover(self):
        title = "Empresa Ejemplo"
        selection = {"selected_wikidata_id": "Q100", "research_queue": {
            "wikidata_id": "Q100", "title": title}}
        clients = FreeClients(env={}, reserve=lambda *_: self.fail("Reserva inesperada"))
        urls = ["https://www.justice.gov/empresa-ejemplo",
                "https://reporter.example/empresa-ejemplo"]

        def wiki(url, **_):
            return json.dumps({"parse": {"externallinks": urls[:1]}}).encode(), url, "application/json"

        def gdelt(url, **_):
            return json.dumps({"articles": [{"url": urls[1], "title": title}]}).encode(), url, "application/json"

        def document(url, **_):
            text = ("Empresa Ejemplo comunicó en 2018 que sus operaciones estaban sujetas "
                    "a investigación y revisión documental de las autoridades competentes.")
            return ("<main><p>" + text + "</p></main>").encode(), url, "text/html"

        sources = discover_sources(selection, clients=clients, wiki_fetcher=wiki,
                                   gdelt_fetcher=gdelt, document_fetcher=document)
        sources["evidence_manifest"], sources["research_freshness"] = gate_duplicate_research(
            selection, sources["evidence_manifest"])
        return sources, clients

    def test_discovery_to_analysis_is_accepted_by_real_worker_contract(self):
        sources, clients = self.discover()
        validate_report_locally(source_report(sources))
        text = json.dumps({"claims": [{"statement": "Empresa Ejemplo comunicó una investigación de sus operaciones.",
                                       "evidence_ids": ["E001", "E002"]}], "missing_questions": []})
        report = analyze_sources(sources, clients=clients, local_generate=lambda _: text)
        validate_report_locally(report)
        self.assertEqual(report["analysis_provider"], "qwen")
        self.assertEqual(report["research_freshness"], sources["research_freshness"])
        self.assertTrue(any(s["provider"] == "gdelt" for s in report["stages"]))
        self.assertTrue(any(s["provider"] == "d1_history" for s in report["stages"]))
        self.assertFalse(report["ready_for_script"])
        self.assertFalse(report["publication_authorized"])

    def test_duplicate_gate_keeps_retrieval_audit_without_loading_models(self):
        sources, clients = self.discover()
        prior = {"prior_evidence_manifest": list(sources["evidence_manifest"])}
        sources["evidence_manifest"], sources["research_freshness"] = gate_duplicate_research(
            prior, sources["evidence_manifest"])
        self.assertGreater(sources["retrieval_budget"]["new_fragments"], 0)
        report = analyze_sources(sources, clients=clients,
                                 local_generate=lambda _: self.fail("Inferencia duplicada"))
        validate_report_locally(report)
        self.assertEqual(report["status"], "skipped_no_documentary_evidence")
        self.assertEqual(report["research_freshness"]["reason"], "unchanged_documentary_sources")

    def test_new_discovery_providers_cannot_impersonate_analyzers(self):
        sources, _ = self.discover()
        report = source_report(sources)
        next(s for s in report["stages"] if s["provider"] == "gdelt")["role"] = "analyze"
        with self.assertRaises(ValueError):
            validate_report_locally(report)

    def test_cli_rejects_contract_before_inference_or_persistence(self):
        import tempfile
        from pathlib import Path
        from tools.ai_research_pipeline import main
        sources, _ = self.discover()
        sources["stages"].append({"provider": "unknown", "role": "discover", "status": "success"})
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as folder:
            path = Path(folder) / "sources.json"
            path.write_text(json.dumps(sources), encoding="utf-8")
            with patch("sys.argv", ["pipeline", "analyze", "--sources", str(path),
                                    "--out", str(Path(folder) / "out.json")]), \
                 patch("tools.ai_research_pipeline.ControlClient") as control, \
                 patch("tools.ai_research_pipeline.analyze_sources") as analyze:
                with self.assertRaises(ValueError):
                    main()
                analyze.assert_not_called()
                control.return_value.reserve.assert_not_called()
                control.return_value.persist.assert_not_called()


if __name__ == "__main__":
    unittest.main()
