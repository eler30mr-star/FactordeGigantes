-- 0009: rastreo no editorial de sitios oficiales candidatos derivados de Wikidata P856.
CREATE TABLE IF NOT EXISTS market_official_source_runs (
 id TEXT PRIMARY KEY NOT NULL,
 collected_on TEXT NOT NULL,
 provider TEXT NOT NULL CHECK(provider='wikidata_p856_safe_official_fetch_v1'),
 attempted INTEGER NOT NULL CHECK(attempted BETWEEN 0 AND 3),
 readable INTEGER NOT NULL CHECK(readable BETWEEN 0 AND 3),
 facts_verified INTEGER NOT NULL DEFAULT 0 CHECK(facts_verified=0),
 created_at TEXT NOT NULL DEFAULT(datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_market_official_runs_date ON market_official_source_runs(collected_on DESC);
CREATE TABLE IF NOT EXISTS market_official_source_items (
 run_id TEXT NOT NULL REFERENCES market_official_source_runs(id),
 wikidata_id TEXT NOT NULL,
 company TEXT NOT NULL,
 website_candidate TEXT NOT NULL,
 identified_by TEXT NOT NULL CHECK(identified_by IN
  ('wikidata_p856_via_news','wikidata_p856_via_wiki')),
 status TEXT NOT NULL CHECK(status IN
  ('candidate_page_readable','candidate_page_unreadable','candidate_unreachable')),
 resolved_url TEXT,
 content_sha256 TEXT,
 readable_blocks INTEGER NOT NULL CHECK(readable_blocks>=0),
 document_links_json TEXT NOT NULL DEFAULT '[]',
 short_excerpt TEXT,
 source_identity_verified INTEGER NOT NULL DEFAULT 0 CHECK(source_identity_verified=0),
 facts_verified INTEGER NOT NULL DEFAULT 0 CHECK(facts_verified=0),
 rights_verified INTEGER NOT NULL DEFAULT 0 CHECK(rights_verified=0),
 publication_authorized INTEGER NOT NULL DEFAULT 0 CHECK(publication_authorized=0),
 PRIMARY KEY(run_id,wikidata_id)
);
CREATE INDEX IF NOT EXISTS idx_market_official_items_entity ON market_official_source_items(wikidata_id);
