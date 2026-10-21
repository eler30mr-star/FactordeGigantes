-- 0007: unión explicable de noticias y empresas detectadas; sin hechos aprobados.
CREATE TABLE IF NOT EXISTS market_entity_news_runs (
 id TEXT PRIMARY KEY NOT NULL,
 collected_on TEXT NOT NULL,
 provider TEXT NOT NULL CHECK(provider='wikimedia_rss_headline_join_v1'),
 company_count INTEGER NOT NULL CHECK(company_count BETWEEN 0 AND 24),
 news_count INTEGER NOT NULL CHECK(news_count BETWEEN 0 AND 100),
 match_count INTEGER NOT NULL CHECK(match_count BETWEEN 0 AND 100),
 created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_market_entity_news_runs_date ON market_entity_news_runs(collected_on DESC);
CREATE TABLE IF NOT EXISTS market_entity_news_links (
 wikidata_id TEXT NOT NULL REFERENCES market_entities(wikidata_id),
 news_id TEXT NOT NULL REFERENCES market_news_leads(id),
 matched_alias TEXT NOT NULL,
 match_method TEXT NOT NULL CHECK(match_method='exact_normalized_headline_v1'),
 match_status TEXT NOT NULL DEFAULT 'candidate_needs_entity_confirmation'
   CHECK(match_status IN ('candidate_needs_entity_confirmation','confirmed','rejected')),
 first_run_id TEXT NOT NULL REFERENCES market_entity_news_runs(id),
 last_run_id TEXT NOT NULL REFERENCES market_entity_news_runs(id),
 first_seen_at TEXT NOT NULL,
 last_seen_at TEXT NOT NULL,
 PRIMARY KEY(wikidata_id,news_id)
);
CREATE INDEX IF NOT EXISTS idx_market_entity_news_links_date ON market_entity_news_links(last_seen_at DESC);
