"""Validaciones offline de fuente oficial descubierta. No navega sitios de terceros."""
import json
import unittest
from tools import primary_source_discovery as discovery


class OfficialSourceTests(unittest.TestCase):
    @staticmethod
    def fake_fetch(url):
        if "list=search" in url:
            return json.dumps({"query": {"search": [
                {"title":"BlackBerry"},{"title":"BlackBerry 10"},
            ]}}).encode(), url, "application/json"
        if "prop=pageprops" in url:
            return json.dumps({"query": {"pages": [
                {"title":"BlackBerry","pageprops":{"wikibase_item":"Q1234"}}
            ]}}).encode(), url, "application/json"
        if "wbgetentities" in url:
            return json.dumps({"entities":{"Q1234":{"claims":{"P856":[
                {"mainsnak":{"datavalue":{"value":"https://www.blackberry.com/en"}}},
                {"mainsnak":{"datavalue":{"value":"http://example.com"}}},
                {"mainsnak":{"datavalue":{"value":"https://127.0.0.1/internal"}}}
            ]}}}}}).encode(), url, "application/json"
        if url=="https://www.blackberry.com/en":
            return b"<html><body><p>BlackBerry is a secure software and systems company for industries worldwide.</p></body></html>",url,"text/html"
        raise AssertionError("unexpected URL: "+url)

    def test_discovers_official_p856_without_certifying_truth(self):
        result=discovery.discover_official("BlackBerry",fetcher=self.fake_fetch,max_entities=1)
        self.assertEqual(result["official_candidates"],1)
        self.assertFalse(result["publication_authorized"])
        self.assertFalse(result["automatic_fact_verification"])
        self.assertEqual(result["sources"][0]["status"],"official_page_fetched")
        self.assertEqual(result["sources"][0]["site_url"],"https://www.blackberry.com/en")
        self.assertEqual(result["sources"][0]["wikidata_item"],"Q1234")
        self.assertGreater(result["sources"][0]["readable_blocks"],0)
        self.assertFalse(result["sources"][0]["confirmed_primary"])
        self.assertTrue(result["needs_independent_sources"])

    def test_rejects_internal_and_unencrypted_official_links(self):
        q=discovery.wikidata_official_url("Q1234",fetcher=self.fake_fetch)
        self.assertEqual(q,["https://www.blackberry.com/en"])

    def test_does_not_expose_search_result_as_verified_primary(self):
        def no_p856(url):
            if "list=search" in url:
                return json.dumps({"query":{"search":[{"title":"Random company"}]}}).encode(),url,"application/json"
            if "prop=pageprops" in url:
                return json.dumps({"query":{"pages":[{"title":"Random company","pageprops":{"wikibase_item":"Q88"}}]}}).encode(),url,"application/json"
            return json.dumps({"entities":{"Q88":{"claims":{}}}}).encode(),url,"application/json"
        result=discovery.discover_official("Random company",fetcher=no_p856)
        self.assertEqual(result["official_candidates"],0)
        self.assertEqual(result["sources"][0]["status"],"no_official_link_found")

    def test_official_page_failure_never_fakes_excerpt(self):
        def broken(url):
            if url.startswith("https://www.blackberry.com/"):
                raise TimeoutError("test")
            return self.fake_fetch(url)
        result=discovery.discover_official("BlackBerry",fetcher=broken,max_entities=1)
        self.assertEqual(result["official_candidates"],1)
        row=result["sources"][0]
        self.assertEqual(row["status"],"official_url_candidate")
        self.assertEqual(row["fetch_error_type"],"TimeoutError")
        self.assertNotIn("short_excerpt",row)

    def test_reject_invalid_entity_and_topic(self):
        with self.assertRaises(ValueError):
            discovery.wikidata_official_url("../../../internal",fetcher=self.fake_fetch)
        with self.assertRaises(ValueError):
            discovery.discover_official("A",fetcher=self.fake_fetch)


if __name__=="__main__":
    unittest.main()
