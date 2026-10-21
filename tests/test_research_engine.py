"""Pruebas offline del investigador; ninguna petición a sitios externos."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from tools import research_engine as engine

ROOT = Path(__file__).resolve().parents[1]
DOSSIER = json.loads((ROOT / "research/blackberry/expediente_preliminar.json").read_text(encoding="utf-8"))
HTML = """<!doctype html><html><head><script>ignore this</script></head><body>
<p>Research In Motion was founded in 1984 by Mike Lazaridis and Douglas Fregin in Canada.</p>
<p>BlackBerry announced in 2016 that the company had completed its transition to software.</p>
<p>On January 4, 2022 BlackBerry discontinued its legacy services for older operating systems.</p>
</body></html>"""


def fake_fetch(url):
    return HTML.encode(), url, "text/html; charset=utf-8"


class ResearchEngineTests(unittest.TestCase):
    def test_defends_public_only_https(self):
        for bad in (
            "http://example.com", "https://localhost/", "https://127.0.0.1/",
            "https://10.0.0.1/", "https://192.168.1.2/", "https://example.local/",
            "https://user:password@example.com/", "https://example.com:8080/x",
            "file:///etc/passwd",
        ):
            with self.subTest(url=bad), self.assertRaises(ValueError):
                engine.validate_url(bad)
        self.assertEqual(engine.validate_url("https://investors.blackberry.com/faq"),
                         "https://investors.blackberry.com/faq")

    def test_no_private_ips_after_dns_lookup(self):
        from unittest.mock import patch
        fake = [(None, None, None, None, ("127.0.0.1", 443))]
        with patch.object(engine.socket, "getaddrinfo", return_value=fake):
            with self.assertRaisesRegex(ValueError, "privada"):
                engine.check_public_dns("example.com")

    def test_html_parser_removes_scripts_and_keeps_paragraphs(self):
        blocks = engine.extract_blocks(HTML.encode(), "text/html")
        self.assertEqual(len(blocks), 3)
        self.assertTrue(all("ignore this" not in b for b in blocks))
        matches = engine.excerpts_for_claim("Research In Motion fue fundada en 1984 por Mike Lazaridis", blocks)
        self.assertGreaterEqual(len(matches), 1)
        self.assertEqual(matches[0]["verification_status"], "candidate_unchecked")
        self.assertLessEqual(len(matches[0]["excerpt"]), engine.MAX_EXCERPT_CHARS)

    def test_real_dossier_structure_without_automatic_approval(self):
        original = copy.deepcopy(DOSSIER)
        result = engine.research_dossier(DOSSIER, fetcher=fake_fetch, max_requests=4)
        self.assertEqual(result["fetched_count"], 4)
        self.assertEqual(result["request_count"], 4)
        self.assertEqual(result["facts_verified_automatically"], 0)
        self.assertFalse(result["production_ready"])
        self.assertFalse(result["youtube_publication_authorized"])
        self.assertEqual(result["rights_verified_automatically"], 0)
        self.assertEqual(DOSSIER, original)
        self.assertEqual(len(result["candidate_claims"]), 8)
        self.assertTrue(all(x["verification_status"] == "pending_human"
                            for x in result["candidate_claims"]))
        with tempfile.TemporaryDirectory() as tmp:
            engine.save_report(result, Path(tmp))
            p = json.loads((Path(tmp) / "reporte_investigacion.json").read_text())
            self.assertEqual(p["fetched_count"], 4)
            self.assertIn("SIN PASAJES ENCONTRADOS", (Path(tmp) / "evidencia_para_ia.txt").read_text())

    def test_unavailable_sources_do_not_fabricate_matching_text(self):
        def broken(url):
            raise TimeoutError()
        result = engine.research_dossier(DOSSIER, fetcher=broken, max_requests=2)
        self.assertEqual(result["fetched_count"], 0)
        self.assertTrue(all(not claim["candidate_passages"] for claim in result["candidate_claims"]))
        self.assertTrue(all(s["status"] == "blocked_or_unavailable" for s in result["sources"]))

    def test_discovery_does_not_claim_primary_sources(self):
        response = json.dumps({"query":{"search":[{"title":"BlackBerry"},{"title":"Teléfono inteligente"}]}})
        def mock_api(_url):
            return response.encode(), "https://es.wikipedia.org/w/api.php", "application/json"
        data = engine.discover_wikipedia("BlackBerry", fetcher=mock_api)
        self.assertEqual(len(data), 2)
        self.assertTrue(all(x["type"] == "secundaria" for x in data))
        self.assertEqual(data[0]["verification_status"], "discovery_only")

    def test_dossier_cannot_be_publication_approved(self):
        x = copy.deepcopy(DOSSIER)
        x["publication_authorized"] = True
        with self.assertRaises(ValueError):
            engine.research_dossier(x, fetcher=fake_fetch)

    def test_passage_matching_not_fact_checking(self):
        blocks = ["This is only an unrelated page about green trees and birds for an exhibition."]
        self.assertEqual(engine.excerpts_for_claim("BlackBerry transitioned to software in 2016.",blocks), [])


if __name__ == "__main__":
    unittest.main()
