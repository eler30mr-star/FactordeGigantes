import hashlib
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from io import BytesIO

from tools.ai_clients import FreeClients, ProviderError, FLAGS, KEYS, post_json
from tools.ai_control import ControlClient
from tools.ai_source_discovery import discover_sources, selection_identity
from tools.ai_research_pipeline import analyze_sources, parse_review, combine_evidence


TITLE = "Empresa Ejemplo"
TEXT = "Empresa Ejemplo comunicó en 2018 que sus operaciones estaban sujetas a investigación y revisión documental de las autoridades competentes."
SELECTION = {"selected_wikidata_id": "Q100", "research_queue": {"wikidata_id": "Q100", "title": TITLE}}


def evidence():
    return [{"id": "E001", "wikidata_id": "Q100", "company": TITLE,
             "url": "https://www.justice.gov/example", "document_sha256": "a" * 64,
             "source_class": "public_authority_candidate", "page": None,
             "excerpt": TEXT}]


def sources():
    return {"collected_on": "2026-10-22", "selected_wikidata_id": "Q100", "company": TITLE,
            "source_documents": [], "evidence_manifest": evidence(), "stages": []}


def candidate(statement=TEXT, ref="E001"):
    return json.dumps({"claims": [{"statement": statement, "evidence_ids": [ref]}],
                       "missing_questions": ["¿Cuál fue el resultado posterior de la investigación?"]})


def configured(*providers):
    return {k: v for p in providers for k, v in ((KEYS[p], "not-a-real-key-for-tests"), (FLAGS[p], "1"))}


class ClientsTests(unittest.TestCase):
    def test_missing_keys_or_unconfirmed_free_never_reserve_or_call(self):
        for env in ({}, {KEYS["gemini"]: "present-but-not-confirmed"}):
            client = FreeClients(env=env, reserve=lambda *_: self.fail("reservó sin configuración"),
                                 transport=lambda *_: self.fail("llamada sin configuración"))
            with self.assertRaises(ProviderError):
                client.generate("gemini", "JSON")

    def test_budget_denial_and_provider_429_stop_before_retry(self):
        calls = []
        def transport(*args):
            calls.append(args)
            raise ProviderError("quota_exhausted", 429)
        client = FreeClients(env=configured("tavily"), reserve=lambda *_: True, transport=transport)
        for _ in range(2):
            with self.assertRaises(ProviderError):
                client.search("tavily", "tema")
        self.assertEqual(len(calls), 1)
        client = FreeClients(env=configured("exa"), reserve=lambda *_: False,
                             transport=lambda *_: self.fail("superó presupuesto"))
        with self.assertRaisesRegex(ProviderError, "budget_denied"):
            client.search("exa", "tema")

    def test_search_has_no_answers_raw_pages_or_research_agents(self):
        calls = []
        def transport(url, body, headers):
            calls.append((url, body, headers))
            return {"results": [{"url": "https://example.com/document", "title": "Original",
                                 "content": "Esto no debe convertirse en evidencia"}]}
        clients = FreeClients(env=configured("tavily", "exa"), reserve=lambda *_: True, transport=transport)
        for p in ("tavily", "exa"):
            result = clients.search(p, "Empresa")
            self.assertNotIn("content", result[0])
        self.assertEqual(calls[0][1]["search_depth"], "basic")
        self.assertFalse(calls[0][1]["include_answer"])
        self.assertNotIn("contents", calls[1][1])

    def test_openrouter_cannot_route_to_paid_model_or_plugin(self):
        def transport(url, body, headers):
            self.assertEqual(url, "https://openrouter.ai/api/v1/chat/completions")
            self.assertEqual(body["model"], "openrouter/free")
            self.assertEqual(body["provider"]["max_price"], {"prompt": 0, "completion": 0})
            self.assertNotIn("tools", body)
            self.assertNotIn("plugins", body)
            return {"choices": [{"message": {"content": candidate()}}]}
        client = FreeClients(env=configured("openrouter"), reserve=lambda *_: True, transport=transport)
        client.generate("openrouter", "JSON")

    def test_http_failure_does_not_expose_remote_body_or_key(self):
        class Opener:
            def open(self, req, timeout):
                raise HTTPError(req.full_url, 429, "secret-in-message", {},
                                BytesIO(b'{"error":"key=very-secret-value"}'))
        with patch("tools.ai_clients.build_opener", return_value=Opener()):
            with self.assertRaises(ProviderError) as error:
                post_json("https://api.tavily.com/search", {}, {"Authorization": "secret"})
        self.assertEqual(str(error.exception), "quota_exhausted")
        self.assertNotIn("secret", str(error.exception))

    def test_control_only_fixed_worker_and_reserved_request_identity(self):
        with self.assertRaises(ValueError):
            ControlClient(base_url="https://evil.example", token="x" * 50)
        calls = []
        def transport(url, body, headers):
            calls.append((url, body))
            return {"ok": True, "allowed": True}
        control = ControlClient(base_url="https://factor-de-gigantes.martin30-eler.workers.dev",
                                token="x" * 20 + "." + "y" * 20 + "." + "z" * 20, transport=transport)
        self.assertTrue(control.reserve("gemini", "analyze"))
        self.assertTrue(control.reserve("gemini", "analyze"))
        self.assertNotEqual(calls[0][1]["request_id"], calls[1][1]["request_id"])


class DiscoveryTests(unittest.TestCase):
    def clients(self):
        return FreeClients(env={}, reserve=lambda *_: self.fail("No hay claves"))

    def test_closed_company_uses_observed_regulator_link_and_downloads_original(self):
        payload = ("<p>" + TEXT + "</p>").encode()
        def wiki(*args, **kwargs):
            return json.dumps({"parse": {"externallinks": [
                "https://127.0.0.1/private", "https://www.justice.gov/example"]}}).encode(), "https://en.wikipedia.org/w/api.php", "application/json"
        fetched = []
        def document(url, **kwargs):
            fetched.append(url)
            return payload, url, "text/html"
        out = discover_sources(SELECTION, clients=self.clients(), wiki_fetcher=wiki, document_fetcher=document)
        self.assertEqual(fetched, ["https://www.justice.gov/example"])
        self.assertEqual(len(out["evidence_manifest"]), 1)
        e = out["evidence_manifest"][0]
        self.assertEqual(e["document_sha256"], hashlib.sha256(payload).hexdigest())
        self.assertEqual(e["source_class"], "public_authority_candidate")
        self.assertFalse(out["ready_for_script"])
        self.assertEqual(out["stages"][1]["status"], "missing_key")

    def test_search_snippet_never_becomes_evidence_if_download_fails(self):
        def transport(*args):
            return {"results": [{"url": "https://example.com/original", "content": TEXT}]}
        clients = FreeClients(env=configured("tavily"), reserve=lambda *_: True, transport=transport)
        def unavailable(*args, **kwargs):
            raise OSError("unavailable")
        out = discover_sources(SELECTION, clients=clients, wiki_fetcher=unavailable, document_fetcher=unavailable)
        self.assertEqual(out["evidence_manifest"], [])
        self.assertEqual(out["status"], "skipped_no_documentary_evidence")

    def test_authority_link_after_160_results_is_not_lost_before_ranking(self):
        links = [f"https://example.com/story/{i}" for i in range(200)] + ["https://www.justice.gov/empresa-ejemplo"]
        def wiki(*args, **kwargs):
            return json.dumps({"parse": {"externallinks": links}}).encode(), "https://en.wikipedia.org/w/api.php", "application/json"
        fetched = []
        def document(url, **kwargs):
            fetched.append(url)
            return ("<p>" + TEXT + "</p>").encode(), url, "text/html"
        out = discover_sources(SELECTION, clients=self.clients(), wiki_fetcher=wiki, document_fetcher=document)
        self.assertEqual(fetched[0], "https://www.justice.gov/empresa-ejemplo")
        self.assertLessEqual(len(fetched), 8)
        self.assertTrue(out["evidence_manifest"])

    def test_no_selection_does_not_call_any_provider(self):
        result = discover_sources({"selected_wikidata_id": None}, clients=self.clients(),
                                  wiki_fetcher=lambda *_: self.fail("sin selección"))
        self.assertEqual(result["status"], "skipped_no_selection")
        with self.assertRaises(ValueError):
            selection_identity({**SELECTION, "research_queue": {"wikidata_id": "Q200", "title": TITLE}})

    def test_blocked_authorities_do_not_exhaust_all_document_slots(self):
        links = [f"https://agency{i}.gov/empresa-ejemplo" for i in range(6)] + ["https://reporter.example/empresa-ejemplo"]
        def wiki(*args, **kwargs):
            return json.dumps({"parse": {"externallinks": links}}).encode(), "https://en.wikipedia.org/w/api.php", "application/json"
        fetched = []
        def document(url, **kwargs):
            fetched.append(url)
            if ".gov/" in url:
                return b"<!DOCTYPE html><html>Access challenge</html>", url, "text/html"
            return ("<p>" + TEXT + "</p>").encode(), url, "text/html"
        out = discover_sources(SELECTION, clients=self.clients(), wiki_fetcher=wiki, document_fetcher=document)
        self.assertIn("https://reporter.example/empresa-ejemplo", fetched)
        self.assertLessEqual(sum(".gov/" in u for u in fetched), 5)
        self.assertGreaterEqual(sum(".gov/" in u for u in fetched), 3)
        self.assertTrue(out["evidence_manifest"])
        self.assertTrue(any(row["status"]=="text_extracted"
                            for row in out["source_documents"]))
        # El límite compacto de cuatro entradas prefiere páginas que
        # sí contienen texto, sin confundirlo con verificación factual.
        self.assertLessEqual(len(out["source_documents"]),4)

    def test_history_prevents_repeating_failed_urls_and_merges_only_new_evidence(self):
        previous={**evidence()[0],"id":"E001","company":TITLE}
        selection={**SELECTION,
                   "prior_attempted_urls":["https://blocked.gov/empresa-ejemplo",
                                           "https://reporter.example/old-story"],
                   "prior_evidence_manifest":[previous]}
        urls=["https://blocked.gov/empresa-ejemplo",
              "https://reporter.example/old-story",
              "https://fresh.example/empresa-ejemplo-new-study"]
        def wiki(*a,**kw):
            return (json.dumps({"parse":{"externallinks":urls}}).encode(),
                    "https://en.wikipedia.org/w/api.php","application/json")
        fetched=[]
        def document(url,**kwargs):
            fetched.append(url)
            return ("<p>"+TEXT+"</p>").encode(),url,"text/html"
        result=discover_sources(selection,clients=self.clients(),
                                wiki_fetcher=wiki,document_fetcher=document)
        self.assertEqual(fetched,["https://fresh.example/empresa-ejemplo-new-study"])
        self.assertEqual(result["retrieval_budget"]["new_fragments"],1)
        self.assertEqual(result["retrieval_budget"]["attempted"],1)
        self.assertEqual({e["url"] for e in result["evidence_manifest"]},
                         {previous["url"],"https://fresh.example/empresa-ejemplo-new-study"})
        self.assertEqual([e["id"] for e in result["evidence_manifest"]],["E001","E002"])
        self.assertEqual(result["status"],"sources_collected")

    def test_same_document_not_resubmitted_to_ai_without_new_sources(self):
        prior={**evidence()[0],"id":"E001","company":TITLE}
        selection={**SELECTION,
                   "prior_attempted_urls":["https://www.justice.gov/example"],
                   "prior_evidence_manifest":[prior]}
        def wiki(*a,**kw):
            return (json.dumps({"parse":{"externallinks":[
                    "https://www.justice.gov/example"]}}).encode(),
                    "https://en.wikipedia.org/w/api.php","application/json")
        result=discover_sources(selection,clients=self.clients(),
          wiki_fetcher=wiki,
          document_fetcher=lambda *_args,**_kw:self.fail("Se repite fuente antigua"))
        self.assertEqual(result["status"],"skipped_no_documentary_evidence")
        self.assertEqual(result["evidence_manifest"],[])
        self.assertEqual(result["retrieval_budget"]["new_fragments"],0)
        self.assertEqual(result["retrieval_budget"]["attempted"],0)

    def test_more_requests_continue_past_blocked_authorities(self):
        links=[f"https://agency{i}.gov/empresa-ejemplo" for i in range(6)]
        links+=["https://independent1.example/empresa-ejemplo",
                "https://independent2.example/empresa-ejemplo"]
        def wiki(*a,**kw):
            return (json.dumps({"parse":{"externallinks":links}}).encode(),
                    "https://en.wikipedia.org/w/api.php","application/json")
        fetched=[]
        def document(url,**kw):
            fetched.append(url)
            if "agency" in url:
                raise OSError("Fuente bloqueada")
            return ("<p>"+TEXT+"</p>").encode(),url,"text/html"
        result=discover_sources(SELECTION,clients=self.clients(),
            wiki_fetcher=wiki,document_fetcher=document)
        self.assertEqual(result["retrieval_budget"]["attempted"],len(fetched))
        self.assertLessEqual(len(fetched),8)
        self.assertLessEqual(len(result["source_documents"]),4)
        self.assertEqual(result["retrieval_budget"]["attempted_urls"],fetched)
        self.assertEqual(result["retrieval_budget"]["attempted"],len(fetched))
        self.assertGreaterEqual(len({e["url"] for e in result["evidence_manifest"]}),2)
        self.assertEqual(result["retrieval_budget"]["independent_domains_with_text"],2)
        self.assertFalse(result["ready_for_script"])
        self.assertEqual(result["facts_verified_automatically"],0)

    def test_cross_company_evidence_is_not_reused(self):
        s = sources()
        s["evidence_manifest"].append({**evidence()[0], "wikidata_id": "Q200"})
        self.assertEqual(len(combine_evidence(s, None, None, None, "Q100")), 1)


class TeamTests(unittest.TestCase):
    def test_without_keys_qwen_works_and_others_report_missing(self):
        clients = FreeClients(env={}, reserve=lambda *_: self.fail("sin claves"))
        result = analyze_sources(sources(), clients=clients, local_generate=lambda _: candidate())
        self.assertEqual(result["analysis_provider"], "qwen")
        self.assertEqual(result["status"], "candidate_claims_generated")
        self.assertEqual(len(result["preliminary_claims"]), 1)
        self.assertEqual(result["reviews"], [])
        self.assertEqual(next(s for s in result["stages"] if s["provider"] == "groq")["status"], "missing_key")
        self.assertFalse(result["publication_authorized"])

    def test_gemini_analyzes_groq_reviews_and_backups_are_not_called(self):
        called = []
        def transport(url, body, headers):
            called.append(url)
            if "googleapis" in url:
                self.assertNotIn("tools", body)
                return {"candidates": [{"content": {"parts": [{"text": candidate()}]}}]}
            self.assertIn("api.groq.com", url)
            review = {"reviews": [{"claim_index": 1, "assessment": "insufficient_context",
                                    "evidence_ids": ["E001"], "reason": "Hace falta conocer el desenlace posterior.",
                                    "source_assessments":[{"evidence_id":"E001","assessment":"insufficient_context",
                                                           "reason":"Hace falta contexto del desenlace."}]}]}
            return {"choices": [{"message": {"content": json.dumps(review)}}]}
        clients = FreeClients(env=configured("gemini", "groq", "mistral", "openrouter"),
                              reserve=lambda *_: True, transport=transport)
        result = analyze_sources(sources(), clients=clients, local_generate=lambda _: candidate())
        self.assertEqual(len(called), 2)
        self.assertEqual(result["analysis_provider"], "gemini")
        self.assertEqual(len(result["reviews"]), 1)
        self.assertFalse(result["reviews"][0]["human_verified"])

    def test_invented_gemini_citation_falls_back_to_mistral(self):
        def transport(url, body, headers):
            if "googleapis" in url:
                return {"candidates": [{"content": {"parts": [{"text": candidate(ref="E999")} ]}}]}
            return {"choices": [{"message": {"content": candidate()}}]}
        clients = FreeClients(env=configured("gemini", "mistral"), reserve=lambda *_: True, transport=transport)
        result = analyze_sources(sources(), clients=clients, local_generate=lambda _: candidate())
        self.assertEqual(result["analysis_provider"], "mistral")
        self.assertEqual(result["stages"][2]["status"], "invalid_output")

    def test_groq_cannot_invent_references_or_omit_claims(self):
        for reviews in ([], [None], [12], [{"claim_index": 1, "assessment": "supported_by_excerpt",
                             "evidence_ids": ["E999"], "reason": "No existe esta cita"}]):
            with self.assertRaises(ValueError):
                parse_review(json.dumps({"reviews": reviews}), evidence(), [{}])

    def test_no_evidence_or_disabled_never_loads_local_model(self):
        s = sources();s["evidence_manifest"] = []
        clients = FreeClients(env={}, reserve=lambda *_: self.fail("sin evidencia"))
        result = analyze_sources(s, clients=clients, local_generate=lambda _: self.fail("modelo innecesario"))
        self.assertEqual(result["status"], "skipped_no_documentary_evidence")
        clients.env["RESEARCH_PROVIDER"] = "disabled"
        result = analyze_sources(sources(), clients=clients, local_generate=lambda _: self.fail("modelo desactivado"))
        self.assertEqual(result["status"], "sources_only")


if __name__ == "__main__":
    unittest.main()
