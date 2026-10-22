"""Regresiones: GDELT libre y anti-consumo duplicado de investigación."""
import json
import unittest
from urllib.parse import urlsplit,parse_qs

from tools.ai_source_discovery import gdelt_articles
from tools.ai_research_pipeline import gate_duplicate_research

def example(n, url="https://news.example.org/company"):
    return {"id":f"E{n:03d}","url":url,"document_sha256":"a"*64,
            "page":None,"excerpt":"La empresa informa sus resultados mediante un documento verificable."}

class NewsSourceTests(unittest.TestCase):
    def test_gdelt_free_one_bounded_json_query_and_original_urls(self):
        calls=[]
        def mock_fetch(url,timeout):
            calls.append((url,timeout))
            args=parse_qs(urlsplit(url).query)
            self.assertEqual(urlsplit(url).hostname,"api.gdeltproject.org")
            self.assertEqual(args["query"],['"Empresa Ejemplo"'])
            self.assertEqual(args["maxrecords"],["20"])
            self.assertEqual(args["timespan"],["1y"])
            return (json.dumps({"articles":[
                {"url":"https://news.example.org/report","title":"Empresa Ejemplo anunció resultados","seendate":"20261021T000000Z"},
                {"url":"http://legacy.example.org/no-tls","title":"Título viejo"},
                {"url":"https://localhost/private","title":"Local"},
                {"url":"https://newspaper.example.org/study","title":"Otra investigación"},
            ]}).encode(),url,"application/json")
        rows=gdelt_articles("Empresa Ejemplo",fetcher=mock_fetch)
        self.assertEqual(len(calls),1)
        self.assertEqual(calls[0][1],12)
        self.assertEqual([r["discovered_by"] for r in rows],["gdelt_doc_artlist"]*2)
        self.assertEqual([r["url"] for r in rows],
          ["https://news.example.org/report","https://newspaper.example.org/study"])

    def test_bad_gdelt_content_is_not_presented_as_news(self):
        def invalid(url,timeout):
            return b"<html>too many requests</html>",url,"text/html"
        with self.assertRaises(ValueError):
            gdelt_articles("Empresa Ejemplo",fetcher=invalid)
        with self.assertRaises(ValueError):
            gdelt_articles("Empresa Ejemplo\nmalicious",fetcher=invalid)

class ResearchFreshness(unittest.TestCase):
    def test_prior_citations_only_block_identical_documents(self):
        a=example(1)
        doc={"prior_evidence_manifest":[a]}
        evidence,status=gate_duplicate_research(doc,[dict(a,id="E003")])
        self.assertEqual(evidence,[])
        self.assertEqual(status["reason"],"unchanged_documentary_sources")
        self.assertEqual(status["new_unique_passages"],0)

    def test_different_paragraph_same_document_does_not_burn_tokens(self):
        old=example(1)
        changed={**old,"id":"E002",
                 "excerpt":"Otro fragmento del mismo fichero descargado y mismo hash no aporta una fuente independiente para volver a consultar al modelo."}
        context,status=gate_duplicate_research(
            {"prior_evidence_manifest":[old]},[changed])
        self.assertEqual(context,[])
        self.assertEqual(status["new_unique_passages"],0)
        self.assertEqual(status["reason"],"unchanged_documentary_sources")

    def test_any_new_verified_hash_or_source_allows_new_analysis_candidate(self):
        a=example(1)
        b=example(2,url="https://other.example.org/new")
        evidence,status=gate_duplicate_research(
            {"prior_evidence_manifest":[a]},[a,b])
        self.assertEqual(len(evidence),2)
        self.assertEqual(status["reason"],"new_documentary_sources")
        self.assertEqual(status["new_unique_passages"],1)

    def test_without_prior_sources_research_still_can_start(self):
        evidence,status=gate_duplicate_research({},[example(1)])
        self.assertEqual(len(evidence),1)
        self.assertEqual(status["reason"],"first_observation_or_missing_history")

    def test_history_payload_is_bounded(self):
        with self.assertRaises(ValueError):
            gate_duplicate_research({"prior_evidence_manifest":[{}]*5},[example(1)])

if __name__=="__main__":unittest.main()
