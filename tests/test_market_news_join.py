"""Fixtures de correlación: resultados sintéticos, no noticias reales."""
import unittest
from tools.market_news_join import match_company_news,alias_for

def inputs():
    w={"method":"wikimedia_wikidata_company_discovery_v1","collected_on":"2026-10-21",
       "candidates":[{"wikidata_id":"Q221062","topic":"DuPont Corporation",
          "discovery_signals":[{"source":"wikimedia_daily_top_plus_wikidata_p31",
             "url":"https://en.wikipedia.org/wiki/DuPont"}]}]}
    n={"provider":"google_news_rss","collected_at":"2026-10-21T20:00:00Z",
       "leads":[{"id":"news-"+("a"*32),
           "headline":"DuPont announces major industrial transformation in Europe",
           "aggregator_url":"https://news.google.com/rss/articles/CBMiTEST",
           "published_at":"2026-10-21T12:00:00Z",
           "verification_state":"unverified","youtube_demand_verified":False}]}
    return w,n

class MatchTests(unittest.TestCase):
    def test_canonical_company_mention_without_fixed_names(self):
        w,n=inputs()
        result=match_company_news(w,n)
        self.assertEqual(result["match_count"],1)
        self.assertEqual(result["matches"][0]["matched_alias"],"dupont")
        self.assertFalse(result["matches"][0]["source_article_verified"])
        self.assertFalse(result["matches"][0]["editorial_authorized"])
        self.assertFalse(result["ready_for_youtube"])

    def test_substrings_and_ambiguous_aliases_fail_closed(self):
        w,n=inputs()
        n["leads"][0]["headline"]="DuPontx appears in unrelated story"
        self.assertEqual(match_company_news(w,n)["match_count"],0)
        w["candidates"][0]["topic"]="Apple"
        n["leads"][0]["headline"]="Apple shares rise"
        self.assertEqual(match_company_news(w,n)["match_count"],0)
        self.assertIsNone(alias_for("Inc."))

    def test_unverified_source_and_matching_dates_mandatory(self):
        w,n=inputs()
        n["leads"][0]["verification_state"]="verified"
        self.assertEqual(match_company_news(w,n)["match_count"],0)
        n["leads"][0]["verification_state"]="unverified"
        n["leads"][0]["aggregator_url"]="http://localhost/admin"
        self.assertEqual(match_company_news(w,n)["match_count"],0)
        n["collected_at"]="2026-10-20T23:59:00Z"
        with self.assertRaises(ValueError):
            match_company_news(w,n)

if __name__=="__main__":unittest.main()
