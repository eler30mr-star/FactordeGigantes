"""Colectores de mercado: todas las respuestas son fixtures, no mercado actual."""
from datetime import date, timedelta
from urllib.parse import urlsplit, parse_qs
import unittest
from tools.market_sources import collect_youtube, collect_wikipedia
from tools.market_radar import rank_market

TODAY=date(2026,10,21)


class MarketSourcesTests(unittest.TestCase):
    def test_youtube_two_calls_and_only_public_video_statistics(self):
        called=[]
        ids=["marketvideo1","marketvideo2","marketvideo3"]
        self.assertTrue(all(len(s)==12 for s in ids))
        ids=["videoid0001","videoid0002","videoid0003"]
        def fetch(url):
            parsed=urlsplit(url)
            self.assertEqual(parsed.hostname,"www.googleapis.com")
            q=parse_qs(parsed.query)
            self.assertEqual(q["key"][0],"x"*24)
            called.append(parsed.path)
            if parsed.path.endswith("/search"):
                self.assertEqual(q["maxResults"],["10"])
                return {"items":[{"id":{"videoId":i}} for i in ids]}
            if parsed.path.endswith("/videos"):
                self.assertEqual(len(q["id"][0].split(",")),3)
                return {"items":[{"id":i,
                    "statistics":{"viewCount":str((n+1)*15000)},
                    "snippet":{"publishedAt":"2026-10-15T12:00:00Z"}}
                    for n,i in enumerate(ids)]}
            self.fail("Unexpected network call")
        result=collect_youtube("Empresa de innovación",api_key="x"*24,
                               now=TODAY,region="MX",request=fetch)
        self.assertEqual(len(called),2)
        self.assertEqual(result["sample_size"],3)
        self.assertEqual(result["sampled_recent_uploads"],3)
        self.assertEqual(result["videos"][0]["view_count"],15000)
        self.assertNotIn("x"*24,str(result))

    def test_youtube_needs_secret_and_no_sample_fabrication(self):
        with self.assertRaises(RuntimeError):
            collect_youtube("Innovación",api_key="",now=TODAY)
        def no_data(url):
            return {"items":[]}
        with self.assertRaisesRegex(ValueError,"insuficiente"):
            collect_youtube("Innovación",api_key="a"*24,now=TODAY,request=no_data)

    def test_wikimedia_14_complete_days_exact_windows(self):
        start=TODAY-timedelta(days=14)
        items=[]
        for i in range(14):
            day=start+timedelta(days=i)
            items.append({"timestamp":day.strftime("%Y%m%d")+"00","views":100 if i<7 else 300})
        def fetch(url):
            self.assertEqual(urlsplit(url).hostname,"wikimedia.org")
            self.assertIn("/es.wikipedia/",url)
            return {"items":items}
        obj=collect_wikipedia("Empresa_ejemplo",now=TODAY,request=fetch)
        self.assertEqual(obj["views_previous_7d"],700)
        self.assertEqual(obj["views_last_7d"],2100)
        self.assertEqual(obj["source_period_end"],"2026-10-20")
        self.assertTrue(obj["url"].startswith("https://es.wikipedia.org/wiki/"))

    def test_wikimedia_missing_days_rejected(self):
        with self.assertRaises(ValueError):
            collect_wikipedia("Ejemplo",now=TODAY,
                              request=lambda url:{"items":[]})
        with self.assertRaises(ValueError):
            collect_wikipedia("../private",now=TODAY,request=lambda url:{"items":[]})

    def test_combined_collected_signals_rank_without_calling_ai(self):
        videos=["videoid0001","videoid0002","videoid0003"]
        yt={
            "observed_at":"2026-10-21",
            "sampled_recent_uploads":3,
            "videos":[{"video_id":i,"url":"https://www.youtube.com/watch?v="+i,
                       "view_count":20000,"published_at":"2026-10-15"} for i in videos]
        }
        wiki={"observed_at":"2026-10-21",
              "url":"https://es.wikipedia.org/wiki/Empresa_ejemplo",
              "views_last_7d":2100,"views_previous_7d":700}
        result=rank_market([{
            "topic":"Empresa ejemplo",
            "category":"historia_empresarial",
            "story_angle":"Crecimiento empresarial a través de documentos de la empresa",
            "youtube_market":yt,"wikipedia_interest":wiki,
            "primary_documents":[{"url":"https://company.example/annual-report.pdf",
                                  "document_type":"report"}]
        }],today=TODAY)
        self.assertEqual(result["selected_for_research"],"Empresa ejemplo")
        self.assertFalse(result["video_completed"])
        self.assertFalse(result["youtube_publication_authorized"])


if __name__=="__main__":
    unittest.main()
