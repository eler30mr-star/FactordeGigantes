"""Contratos offline: muestra YouTube ficticia, nunca se publica como mercado real."""
from datetime import date,timedelta
import unittest
import io
from urllib.error import HTTPError
from tools.youtube_market_study import study,choose_candidates,MAX_QUERY_PAIRS,QUOTA_CAP

TODAY=date(2026,10,21)
def discovery():
    return {"method":"wikimedia_wikidata_company_discovery_v1","candidates":[
      {"wikidata_id":"Q16956307","topic":"Compañía de laboratorio",
       "discovery_signals":[{"source":"wikimedia_daily_top_plus_wikidata_p31",
         "url":"https://en.wikipedia.org/wiki/Example"}]},
      {"wikidata_id":"Q221062","topic":"Empresa de materiales",
       "discovery_signals":[{"source":"wikimedia_daily_top_plus_wikidata_p31",
         "url":"https://es.wikipedia.org/wiki/Ejemplo"}]}
    ]}
def fake(topic,*,api_key,region,now):
    assert api_key=="x"*24
    return {"origin":"youtube_data_api_v3_search_plus_videos",
       "observed_at":now.isoformat(),"sampled_recent_uploads":3,
       "videos":[{"video_id":"videoid000"+str(i),
          "url":"https://www.youtube.com/watch?v=videoid000"+str(i),
          "view_count":1000*i,"published_at":(now-timedelta(days=4)).isoformat(),
          "channel_id":"UC"+str(i)*22} for i in (1,2,3)]}

class YoutubeStudyTests(unittest.TestCase):
    def test_google_error_diagnostic_does_not_expose_key_or_remote_message(self):
        from tools.market_sources import collect_youtube,YoutubeApiError
        secret='DO_NOT_PRINT_THIS_API_KEY'
        def unavailable(url):
            body=('{"error":{"message":"'+secret+'",'
                  '"errors":[{"reason":"accessNotConfigured"}]}}').encode()
            raise HTTPError(url,403,secret,{},io.BytesIO(body))
        with self.assertRaises(YoutubeApiError) as cm:
            collect_youtube('Empresa de prueba',api_key=secret,now=TODAY,request=unavailable)
        self.assertEqual(cm.exception.category,'accessNotConfigured')
        self.assertEqual(cm.exception.http_status,403)
        self.assertNotIn(secret,str(cm.exception))
        self.assertNotIn('https://',str(cm.exception))

    def test_http_failure_stops_both_company_loops(self):
        from tools.market_sources import YoutubeApiError
        calls=[]
        def denied(*args,**kwargs):
            calls.append(1)
            raise YoutubeApiError('search',403,'quotaExceeded')
        r=study(discovery(),api_key='x'*24,now=TODAY,collector=denied)
        self.assertEqual(len(calls),1)
        self.assertEqual(r['queries'][0]['http_status'],403)
        self.assertEqual(r['queries'][0]['error_category'],'quotaExceeded')

    def test_budget_and_real_candidate_selection_with_two_regions(self):
        calls=[]
        def observe(topic,**kwargs):
            calls.append((topic,kwargs["region"]))
            return fake(topic,**kwargs)
        r=study(discovery(),api_key="x"*24,now=TODAY,collector=observe)
        self.assertEqual(r["queries_attempted"],4)
        self.assertEqual(r["quota_units_max"],QUOTA_CAP)
        self.assertEqual(r["complete_comparisons"],4)
        self.assertEqual(r["state"],"measured")
        self.assertEqual(len(calls),MAX_QUERY_PAIRS)
        self.assertEqual(r["queries"][0]["median_daily_views"],500.)
        self.assertEqual(r["queries"][0]["distinct_channels"],3)
        self.assertFalse(r["market_study_complete"])
        self.assertFalse(r["automatic_publication_allowed"])
        self.assertEqual({q["region"] for q in r["queries"]},{"MX","ES"})

    def test_missing_api_key_never_touches_collector(self):
        with self.assertRaises(RuntimeError):
            study(discovery(),api_key="",now=TODAY,
                  collector=lambda *args,**kwargs:self.fail("Unexpected API call"))

    def test_failure_is_visible_and_aborts_remaining_quota(self):
        calls=[]
        def deny(*args,**kwargs):
            calls.append(1)
            raise RuntimeError("provider unavailable")
        r=study(discovery(),api_key="x"*24,now=TODAY,collector=deny)
        self.assertEqual(len(calls),1)
        self.assertEqual(r["state"],"partial")
        self.assertEqual(r["complete_comparisons"],0)
        self.assertEqual(r["queries"][0]["sample_size"],0)
        self.assertIsNone(r["queries"][0]["median_daily_views"])
        self.assertEqual(r["queries"][0]["error_type"],"RuntimeError")

    def test_no_topic_list_and_source_necessary(self):
        d=discovery()
        d["candidates"].insert(0,{"wikidata_id":"Q123","topic":"Without provenance"})
        self.assertEqual(len(choose_candidates(d)),2)
        self.assertEqual(choose_candidates(d)[0]["wikidata_id"],"Q16956307")

if __name__=="__main__":
    unittest.main()

