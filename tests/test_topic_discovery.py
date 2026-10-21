"""Ensayos offline del descubridor SIN lista estática de empresas."""
import unittest
from urllib.parse import urlsplit,parse_qs
from tools.topic_discovery import discover,COMPANY_TYPES

DAY="2026-10-21"
QCOMPANY=next(iter(COMPANY_TYPES))

def entities(lang):
    if lang=="es":
        return {"Q101":{"id":"Q101",
                         "claims":{"P31":[{"mainsnak":{"datavalue":{"value":{"id":QCOMPANY}}}}],
                                   "P856":[{"mainsnak":{"datavalue":{"value":"https://company.example/"}}}]},
                         "labels":{"es":{"value":"Compañía Ejemplo"}},
                         "sitelinks":{"eswiki":{"title":"Compañía_Ejemplo"}}},
                "Q200":{"id":"Q200",
                         "claims":{"P31":[{"mainsnak":{"datavalue":{"value":{"id":"Q5"}}}}]},
                         "sitelinks":{"eswiki":{"title":"Celebridad_Ejemplo"}}}}
    return {"Q101":{"id":"Q101",
                    "claims":{"P31":[{"mainsnak":{"datavalue":{"value":{"id":QCOMPANY}}}}]},
                    "sitelinks":{"enwiki":{"title":"Example_Company"}}}}

def fake_fetch(url):
    path=urlsplit(url)
    if path.hostname=="wikimedia.org":
        lang="es" if "es.wikipedia" in path.path else "en"
        title="Compañía_Ejemplo" if lang=="es" else "Example_Company"
        return {"items":[{"articles":[
            {"article":"Main_Page","rank":1,"views":800000},
            {"article":"Celebridad_Ejemplo","rank":2,"views":500000},
            {"article":title,"rank":3,"views":180000 if lang=="es" else 260000}
        ]}]}
    if path.hostname=="www.wikidata.org":
        q=parse_qs(path.query)
        lang=q["sites"][0][:2]
        return {"entities":entities(lang)}
    raise AssertionError("URL externa inesperada: "+path.hostname)

class AutonomousDiscoveryTests(unittest.TestCase):
    def test_discovers_company_without_names_supplied_by_human(self):
        result=discover(today=DAY,fetch=fake_fetch,limit=10)
        self.assertEqual(result["company_candidates_count"],1)
        self.assertEqual(result["wikidata_requests"],2)
        item=result["candidates"][0]
        self.assertEqual(item["wikidata_id"],"Q101")
        self.assertEqual(item["topic"],"Compañía Ejemplo")
        self.assertEqual(len(item["discovery_signals"]),2)
        self.assertEqual(item["official_website_candidate"],"https://company.example/")
        self.assertFalse(item["market_rank_qualified"])
        self.assertFalse(result["market_study_complete"])
        self.assertIsNone(result["selected_automatically_for_research"])

    def test_validated_interest_enrichment_is_not_youtube_demand(self):
        calls=[]
        def interest(title,*,language,now):
            calls.append((title,language,now))
            return {
                "observed_at":"2026-10-21",
                "url":"https://es.wikipedia.org/wiki/Compañía_Ejemplo",
                "views_last_7d":8800,"views_previous_7d":4200,
            }
        result=discover(today=DAY,limit=10,fetch=fake_fetch,
                        enrich_interest=True,interest_collector=interest)
        self.assertEqual(result["wikipedia_interest_measured_count"],1)
        self.assertEqual(result["candidates"][0]["interest_14d_status"],"measured")
        self.assertEqual(result["candidates"][0]["wikipedia_interest"]["views_last_7d"],8800)
        self.assertEqual(len(calls),1)
        self.assertFalse(result["youtube_market_verified"])
        self.assertFalse(result["market_study_complete"])

    def test_unavailable_interest_does_not_fabricate_growth(self):
        def rejected(title,*,language,now):
            raise RuntimeError("Provider is unavailable")
        result=discover(today=DAY,limit=10,fetch=fake_fetch,
                        enrich_interest=True,interest_collector=rejected)
        self.assertEqual(result["wikipedia_interest_measured_count"],0)
        self.assertEqual(result["candidates"][0]["interest_14d_status"],"unavailable")
        self.assertNotIn("wikipedia_interest",result["candidates"][0])

    def test_date_lag_and_capped_request_budget(self):
        urls=[]
        def fetch(url):
            urls.append(url)
            return fake_fetch(url)
        result=discover(today=DAY,fetch=fetch,limit=10,max_requests=1)
        self.assertEqual(result["data_day"],"2026-10-18")
        self.assertEqual(result["wikidata_requests"],1)
        self.assertEqual(sum("wikidata.org" in u for u in urls),1)

    def test_fake_person_page_not_accepted_as_company(self):
        def only_people(url):
            if urlsplit(url).hostname=="wikimedia.org":
                return {"items":[{"articles":[{"article":"Persona","views":7000,"rank":1}]}]}
            return {"entities":{"Q5":{"id":"Q5","claims":{
                "P31":[{"mainsnak":{"datavalue":{"value":{"id":"Q5"}}}}]},
                "sitelinks":{"eswiki":{"title":"Persona"}}}}}
        result=discover(today=DAY,languages=("es",),fetch=only_people)
        self.assertEqual(result["company_candidates_count"],0)
        self.assertFalse(result["ready_for_youtube"])

    def test_non_https_official_link_is_not_trusted(self):
        def unsafe_company(url):
            if urlsplit(url).hostname=="wikimedia.org":
                return {"items":[{"articles":[{"article":"Firma","views":1700,"rank":1}]}]}
            entity={"id":"Q101","claims":{
                "P31":[{"mainsnak":{"datavalue":{"value":{"id":QCOMPANY}}}}],
                "P856":[{"mainsnak":{"datavalue":{"value":"http://127.0.0.1/internal"}}}]},
                "sitelinks":{"eswiki":{"title":"Firma"}}}
            return {"entities":{"Q101":entity}}
        r=discover(today=DAY,languages=("es",),fetch=unsafe_company)
        self.assertEqual(r["candidates"][0]["official_website_candidate"],None)

    def test_unsupported_language_and_broken_wikidata_rejected(self):
        with self.assertRaises(ValueError):
            discover(today=DAY,languages=("fr",),fetch=fake_fetch)
        with self.assertRaises(ValueError):
            discover(today=DAY,limit=1000,fetch=fake_fetch)
        def broken(url):
            if urlsplit(url).hostname=="wikimedia.org":
                return fake_fetch(url)
            return {"errors":["not an entity list"]}
        with self.assertRaises(ValueError):
            discover(today=DAY,limit=10,fetch=broken)

if __name__=="__main__":
    unittest.main()
