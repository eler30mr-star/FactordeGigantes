"""Contrato offline del radar: números de prueba NO son tendencias reales."""
import unittest
from tools.market_radar import rank_market, youtube_signal, pageview_signal

TODAY="2026-10-21"


def candidate(topic="Empresa Alfa", views=100000, current=2000, previous=800,
              published=False, docs=2):
    videos=[
        {"video_id":f"videoid{i:04d}", "url":f"https://www.youtube.com/watch?v=videoid{i:04d}",
         "view_count": views+i*1200, "published_at":"2026-10-15"}
        for i in range(3)
    ]
    return {
        "topic": topic, "category":"historia_empresarial",
        "story_angle":"Historia empresarial y transformación con documentos originales",
        "youtube_market":{
            "observed_at":TODAY,"videos":videos,"sampled_recent_uploads":4,
        },
        "wikipedia_interest":{
            "observed_at":TODAY, "url":"https://es.wikipedia.org/wiki/Ejemplo",
            "views_last_7d":current, "views_previous_7d":previous,
        },
        "primary_documents":[
            {"url":f"https://official{i}.example/reports/2025.pdf","document_type":"report"}
            for i in range(docs)
        ],
    }


class MarketRadarTests(unittest.TestCase):
    def test_choose_demand_from_two_independent_market_signals(self):
        low=candidate(topic="Empresa Beta",views=9000,current=700,previous=850)
        high=candidate(topic="Empresa Alfa",views=120000,current=2000,previous=800)
        result=rank_market([low,high],today=TODAY)
        self.assertEqual(result["candidate_count"],2)
        self.assertEqual(result["qualified_count"],2)
        self.assertEqual(result["selected_for_research"],"Empresa Alfa")
        self.assertGreater(result["ranking"][0]["market_score"],result["ranking"][1]["market_score"])
        self.assertFalse(result["research_automatic"])
        self.assertFalse(result["youtube_publication_authorized"])
        self.assertFalse(result["realtime_verified"])
        self.assertIn("novelty_neutral_pending_channel_analytics",result["ranking"][0]["score_components"])

    def test_absence_of_youtube_data_never_makes_up_trends(self):
        item=candidate()
        item.pop("youtube_market")
        result=rank_market([item],today=TODAY)
        self.assertEqual(result["qualified_count"],0)
        self.assertIsNone(result["selected_for_research"])
        self.assertIsNone(result["ranking"][0]["market_score"])
        self.assertIn("youtube_no_comparable: ValueError",result["ranking"][0]["reasons"])

    def test_stale_data_and_duplicate_topics_are_rejected(self):
        item=candidate()
        item["youtube_market"]["observed_at"]="2026-09-25"
        result=rank_market([item],today=TODAY)
        self.assertFalse(result["ranking"][0]["eligible_for_investigation"])
        duplicate=rank_market([candidate()],today=TODAY,
                               previously_published=["  EMPRESA ALFA "])
        self.assertIsNone(duplicate["selected_for_research"])
        self.assertIn("tema_ya_publicado",duplicate["ranking"][0]["reasons"])

    def test_market_proxy_is_not_a_factual_verified_statement(self):
        result=rank_market([candidate(docs=0)],today=TODAY)
        self.assertIn("sin_fuente_primaria_identificada",result["ranking"][0]["reasons"])
        self.assertEqual(result["qualified_count"],0)
        bad=candidate()
        bad["wikipedia_interest"]["url"]="https://not-wikipedia.example/wiki/Ejemplo"
        self.assertEqual(rank_market([bad],today=TODAY)["qualified_count"],0)

    def test_fake_views_private_non_numeric_and_duplicate_videos_rejected(self):
        item=candidate()
        item["youtube_market"]["videos"][0]["view_count"]=True
        self.assertEqual(rank_market([item],today=TODAY)["qualified_count"],0)
        item=candidate()
        item["youtube_market"]["videos"][0]["url"]="http://127.0.0.1/private"
        self.assertEqual(rank_market([item],today=TODAY)["qualified_count"],0)
        item=candidate()
        item["youtube_market"]["videos"][0]["video_id"]=item["youtube_market"]["videos"][1]["video_id"]
        self.assertEqual(rank_market([item],today=TODAY)["qualified_count"],0)

    def test_no_candidates_has_no_selected_topic(self):
        result=rank_market([],today=TODAY)
        self.assertEqual(result["ranking"],[])
        self.assertIsNone(result["selected_for_research"])


if __name__=="__main__":
    unittest.main()
