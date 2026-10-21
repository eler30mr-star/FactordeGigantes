-- 0008: entidades halladas por titulares y evaluaciones automáticas fundamentadas.
-- Solo amplía la base. No crea trabajo editorial aprobado ni selecciona sin evidencias.
CREATE TABLE IF NOT EXISTS market_news_entity_runs (
  id TEXT PRIMARY KEY NOT NULL,
  collected_on TEXT NOT NULL,
  provider TEXT NOT NULL CHECK(provider='wikidata_news_company_resolution_v1'),
  headlines_examined INTEGER NOT NULL CHECK(headlines_examined BETWEEN 0 AND 8),
  wikidata_searches INTEGER NOT NULL CHECK(wikidata_searches BETWEEN 0 AND 16),
  lookup_errors INTEGER NOT NULL CHECK(lookup_errors BETWEEN 0 AND 17),
  candidate_count INTEGER NOT NULL CHECK(candidate_count BETWEEN 0 AND 16),
  created_at TEXT NOT NULL DEFAULT(datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_market_news_entity_runs_date ON market_news_entity_runs(collected_on DESC);

CREATE TABLE IF NOT EXISTS market_news_entity_candidates (
  news_id TEXT NOT NULL REFERENCES market_news_leads(id),
  wikidata_id TEXT NOT NULL,
  matched_name TEXT NOT NULL,
  article_headline TEXT NOT NULL,
  news_url TEXT NOT NULL,
  source_label TEXT NOT NULL,
  wikidata_url TEXT NOT NULL,
  official_website_candidate TEXT,
  evidence_method TEXT NOT NULL CHECK(evidence_method='wikidata_p31_and_exact_label_in_headline_v1'),
  identity_state TEXT NOT NULL DEFAULT 'needs_original_article'
    CHECK(identity_state IN ('needs_original_article','identity_confirmed','rejected')),
  primary_source_verified INTEGER NOT NULL DEFAULT 0 CHECK(primary_source_verified=0),
  youtube_market_verified INTEGER NOT NULL DEFAULT 0 CHECK(youtube_market_verified=0),
  first_run_id TEXT NOT NULL REFERENCES market_news_entity_runs(id),
  latest_run_id TEXT NOT NULL REFERENCES market_news_entity_runs(id),
  last_seen_at TEXT NOT NULL,
  PRIMARY KEY(news_id,wikidata_id)
);
CREATE INDEX IF NOT EXISTS idx_market_news_entity_candidates_entity ON market_news_entity_candidates(wikidata_id,last_seen_at DESC);

CREATE TABLE IF NOT EXISTS market_assessment_runs (
 id TEXT PRIMARY KEY NOT NULL,
 assessment_day TEXT NOT NULL,
 method TEXT NOT NULL CHECK(method='market_evidence_gate_v1'),
 candidates_evaluated INTEGER NOT NULL CHECK(candidates_evaluated BETWEEN 0 AND 50),
 qualified_count INTEGER NOT NULL DEFAULT 0 CHECK(qualified_count=0),
 selected_wikidata_id TEXT,
 created_at TEXT NOT NULL DEFAULT(datetime('now')),
 CHECK(selected_wikidata_id IS NULL)
);
CREATE INDEX IF NOT EXISTS idx_market_assessment_runs_date ON market_assessment_runs(assessment_day DESC,created_at DESC);

CREATE TABLE IF NOT EXISTS market_assessments (
 run_id TEXT NOT NULL REFERENCES market_assessment_runs(id),
 wikidata_id TEXT NOT NULL,
 title TEXT NOT NULL,
 wiki_observation_count INTEGER NOT NULL CHECK(wiki_observation_count>=0),
 news_mention_count INTEGER NOT NULL CHECK(news_mention_count>=0),
 youtube_region_samples INTEGER NOT NULL CHECK(youtube_region_samples>=0),
 primary_sources_verified INTEGER NOT NULL DEFAULT 0 CHECK(primary_sources_verified=0),
 readiness TEXT NOT NULL CHECK(readiness IN ('awaiting_youtube_and_primary','awaiting_youtube','awaiting_primary','insufficient_evidence')),
 reasons_json TEXT NOT NULL,
 research_authorized INTEGER NOT NULL DEFAULT 0 CHECK(research_authorized=0),
 publication_authorized INTEGER NOT NULL DEFAULT 0 CHECK(publication_authorized=0),
 PRIMARY KEY(run_id,wikidata_id)
);
CREATE INDEX IF NOT EXISTS idx_market_assessments_readiness ON market_assessments(readiness);
