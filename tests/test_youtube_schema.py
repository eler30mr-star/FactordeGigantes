"""Contrato SQLite local de migraciones D1 0001–0006; datos de prueba únicamente."""
import sqlite3
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MIGRATIONS=[ROOT/"migrations"/f"000{i}_{name}.sql" for i,name in [
  (1,"initial"),(2,"editorial_dossiers"),(3,"research_requests"),
  (4,"market_intelligence"),(5,"news_leads"),(6,"youtube_observations")
]]

class YoutubeSchemaTests(unittest.TestCase):
    def test_additive_preserves_records_and_foreign_keys(self):
        with sqlite3.connect(":memory:") as db:
            db.execute("PRAGMA foreign_keys=ON")
            for f in MIGRATIONS:
                db.executescript(f.read_text(encoding="utf-8"))
            db.execute("INSERT INTO jobs(id,title,format,status,manifest_json) VALUES (?,?,?,?,?)",
                       ("job-example","Fixture","long","draft","{}"))
            db.execute("INSERT INTO market_runs(id,collection_day,data_day,source_method,detected_count) VALUES (?,?,?,?,?)",
                       ("r1","2026-10-21","2026-10-18","wikimedia",1))
            db.execute("INSERT INTO market_entities(wikidata_id,title,first_seen,last_seen) VALUES (?,?,?,?)",
                       ("Q16956307","Ejemplo","2026-10-21","2026-10-21"))
            db.execute("INSERT INTO market_youtube_runs(id,collected_on,provider,region_count,candidate_count,queries_attempted,quota_units_max,state) VALUES (?,?,?,?,?,?,?,?)",
                       ("yt-fixture","2026-10-21","youtube_data_api_v3",2,1,2,4,"measured"))
            db.execute("INSERT INTO market_youtube_queries(run_id,wikidata_id,topic,region,observed_on,sample_size,uploads_sampled,median_daily_views,distinct_channels,evidence_state) VALUES (?,?,?,?,?,?,?,?,?,?)",
                       ("yt-fixture","Q16956307","Empresa de ejemplo","MX","2026-10-21",3,3,500,3,"observed_sample"))
            db.execute("INSERT INTO market_youtube_videos(run_id,wikidata_id,region,video_id,published_on,view_count,channel_id,video_url) VALUES (?,?,?,?,?,?,?,?)",
                       ("yt-fixture","Q16956307","MX","videoid0001","2026-10-17",1000,None,
                        "https://www.youtube.com/watch?v=videoid0001"))
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("INSERT INTO market_youtube_videos(run_id,wikidata_id,region,video_id,published_on,view_count,channel_id,video_url) VALUES (?,?,?,?,?,?,?,?)",
                           ("missing","Q16956307","MX","videoid0002","2026-10-17",2000,None,
                            "https://www.youtube.com/watch?v=videoid0002"))
            db.executescript(MIGRATIONS[-1].read_text(encoding="utf-8"))
            self.assertEqual(db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0],1)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM market_youtube_videos").fetchone()[0],1)
            self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(),[])

if __name__=="__main__":unittest.main()
