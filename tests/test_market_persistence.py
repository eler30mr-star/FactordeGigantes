"""D1 0004 es aditiva y guarda señales reales sin duplicar ni autorizar videos."""
from datetime import date
import copy
import sqlite3
from pathlib import Path
import unittest

from tools.market_persistence import import_market_report

ROOT=Path(__file__).resolve().parents[1]
SCHEMA=(ROOT/"migrations/0004_market_intelligence.sql").read_text(encoding="utf-8")


def report():
    return {
        "method":"wikimedia_wikidata_company_discovery_v1",
        "collected_on":"2026-10-21",
        "data_day":"2026-10-18",
        "company_candidates_count":1,
        "candidates":[{
            "wikidata_id":"Q16956307",
            "topic":"Theranos",
            "official_website_candidate":None,
            "discovery_signals":[{
                "source":"wikimedia_daily_top_plus_wikidata_p31",
                "project":"en.wikipedia",
                "url":"https://en.wikipedia.org/wiki/Theranos",
                "rank":37,"views":58877,"observed_on":"2026-10-18"
            }],
            "interest_14d_status":"measured",
            "wikipedia_interest":{
                "observed_at":"2026-10-21",
                "url":"https://en.wikipedia.org/wiki/Theranos",
                "views_last_7d":291435,
                "views_previous_7d":55952,
                "source_period_start":"2026-10-07",
                "source_period_end":"2026-10-20"
            }
        }],
    }


class MarketPersistenceTests(unittest.TestCase):
    def db(self):
        db=sqlite3.connect(":memory:")
        db.execute("PRAGMA foreign_keys=ON")
        db.executescript(SCHEMA)
        return db

    def test_reimport_daily_report_is_idempotent(self):
        with self.db() as db:
            first=import_market_report(db,report())
            second=import_market_report(db,report())
            self.assertEqual(first["run_id"],second["run_id"])
            self.assertFalse(first["remote_d1_write_performed"])
            for table in ("market_runs","market_entities",
                          "market_pageview_observations","market_interest_windows"):
                self.assertEqual(db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0],1)
            self.assertEqual(db.execute(
                "SELECT views_last_7d,views_previous_7d FROM market_interest_windows").fetchone(),(291435,55952))
            self.assertEqual(db.execute("SELECT research_state FROM market_entities").fetchone()[0],"market_unverified")

    def test_new_day_retains_old_history_and_same_company(self):
        with self.db() as db:
            original=report()
            import_market_report(db,original)
            later=copy.deepcopy(original)
            later["collected_on"]="2026-10-22"
            later["data_day"]="2026-10-19"
            later["candidates"][0]["discovery_signals"][0]["observed_on"]="2026-10-19"
            later["candidates"][0]["wikipedia_interest"]["observed_at"]="2026-10-22"
            later["candidates"][0]["wikipedia_interest"]["source_period_start"]="2026-10-08"
            later["candidates"][0]["wikipedia_interest"]["source_period_end"]="2026-10-21"
            import_market_report(db,later)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM market_runs").fetchone()[0],2)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM market_entities").fetchone()[0],1)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM market_interest_windows").fetchone()[0],2)
            self.assertEqual(db.execute("SELECT last_seen FROM market_entities").fetchone()[0],"2026-10-22")

    def test_sources_must_match_wikimedia_and_invalid_report_rolls_back(self):
        with self.db() as db:
            bad=report()
            bad["candidates"][0]["discovery_signals"][0]["url"]="https://fake.example/Theranos"
            with self.assertRaises(ValueError):
                import_market_report(db,bad)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM market_runs").fetchone()[0],0)

    def test_schema_additive_preserves_existing_jobs_and_editorials(self):
        db=sqlite3.connect(":memory:")
        db.execute("PRAGMA foreign_keys=ON")
        try:
            for path in ("0001_initial.sql","0002_editorial_dossiers.sql",
                         "0003_research_requests.sql","0004_market_intelligence.sql"):
                db.executescript((ROOT/"migrations"/path).read_text(encoding="utf-8"))
            db.executescript(SCHEMA)  # Reejecución sin alterar esquema.
            db.execute("INSERT INTO jobs(id,title,format,status,manifest_json) VALUES (?,?,?,?,?)",
                       ("j1","Expediente ya existente","short","draft","{}"))
            db.execute("INSERT INTO editorial_dossiers(job_id,dossier_json) VALUES (?,?)",("j1","{}"))
            import_market_report(db,report())
            self.assertEqual(db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0],1)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM editorial_dossiers").fetchone()[0],1)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM market_interest_windows").fetchone()[0],1)
        finally:
            db.close()

    def test_report_cannot_claim_verified_and_bad_window_fails(self):
        with self.db() as db:
            bad=report()
            bad["candidates"][0]["wikipedia_interest"]["source_period_end"]="2026-10-19"
            with self.assertRaises(ValueError):
                import_market_report(db,bad)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM market_entities").fetchone()[0],0)


if __name__=="__main__":
    unittest.main()
