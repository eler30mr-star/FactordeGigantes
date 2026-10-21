"""Fixtures de Wikidata/news: no se declaran oportunidades reales."""
import unittest
from tools.news_entity_discovery import (
    names_from_headline,discover_news_entities,MAX_HEADLINES,MAX_SEARCHES
)
from urllib.parse import urlsplit,parse_qs

def report():
    return {"provider":"google_news_rss","collected_at":"2026-10-21T20:00:00Z",
       "lead_count":2,"leads":[
       {"id":"news-"+("a"*32),"headline":"Toyota anuncia una transformación industrial - Medio Uno",
        "source_label":"Medio Uno","published_at":"2026-10-21T18:00:00Z",
        "category":"empresas","aggregator_url":"https://news.google.com/rss/articles/ONE",
        "verification_state":"unverified"},
       {"id":"news-"+("b"*32),"headline":"Toyota opens a new manufacturing laboratory - Medio Dos",
        "source_label":"Medio Dos","published_at":"2026-10-21T16:00:00Z",
        "category":"tecnologia","aggregator_url":"https://news.google.com/rss/articles/TWO",
        "verification_state":"unverified"}]}
def fetch(url):
    q=parse_qs(urlsplit(url).query)
    if q.get("action")==["wbsearchentities"]:
        return {"search":[{"id":"Q53268","label":"Toyota"}]}
    assert q.get("action")==["wbgetentities"]
    return {"entities":{"Q53268":{
      "labels":{"en":{"value":"Toyota"},"es":{"value":"Toyota"}},
      "claims":{"P31":[{"mainsnak":{"datavalue":{"value":{"id":"Q783794"}}}}],
        "P856":[{"mainsnak":{"datavalue":{"value":"https://global.toyota/"}}}]}
    }}}

class NewsEntityTests(unittest.TestCase):
    def test_extracts_terms_without_manual_company_dictionary(self):
        self.assertIn("Toyota",names_from_headline(report()["leads"][0]["headline"]))
        self.assertNotIn("Medio Uno",names_from_headline(report()["leads"][0]["headline"]))

    def test_wikidata_p31_exact_label_and_candidate_status(self):
        calls=[]
        def get(url):
            calls.append(url)
            return fetch(url)
        result=discover_news_entities(report(),fetch=get)
        self.assertGreaterEqual(result["candidate_count"],1)
        self.assertTrue(all(x["wikidata_id"]=="Q53268" for x in result["candidates"]))
        self.assertTrue(all(x["official_website_candidate"]=="https://global.toyota/" for x in result["candidates"]))
        self.assertFalse(result["market_study_complete"])
        self.assertTrue(all(not x["identity_verified_in_article"] for x in result["candidates"]))
        self.assertLessEqual(result["wikidata_searches"],MAX_SEARCHES)
        self.assertLessEqual(result["headlines_examined"],MAX_HEADLINES)
        self.assertEqual(len([x for x in calls if "wbgetentities" in x]),1)

    def test_rejects_unverified_company_types_and_ambiguous_labels(self):
        def other(url):
            data=fetch(url)
            if "wbgetentities" in url:
                data["entities"]["Q53268"]["claims"]["P31"]=[]
            return data
        self.assertEqual(discover_news_entities(report(),fetch=other)["candidate_count"],0)
        def misleading(url):
            data=fetch(url)
            if "wbgetentities" in url:
                data["entities"]["Q53268"]["labels"]={"en":{"value":"Other Company"}}
            return data
        self.assertEqual(discover_news_entities(report(),fetch=misleading)["candidate_count"],0)

    def test_no_web_success_leaves_zero_candidates_and_error_visible(self):
        result=discover_news_entities(report(),fetch=lambda url:(_ for _ in ()).throw(OSError("offline")))
        self.assertEqual(result["candidate_count"],0)
        self.assertGreater(result["lookup_errors"],0)

if __name__=="__main__":unittest.main()
