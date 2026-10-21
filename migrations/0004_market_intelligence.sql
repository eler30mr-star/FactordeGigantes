-- Factor de Gigantes · radar de mercado, migración 0004
-- Aditiva; no afecta trabajos, editoriales ni publicaciones existentes.
-- Fuente de verdad para la historia de descubrimiento cuando se despliegue en D1.
CREATE TABLE IF NOT EXISTS market_runs (
  id TEXT PRIMARY KEY NOT NULL,
  collection_day TEXT NOT NULL,
  data_day TEXT NOT NULL,
  source_method TEXT NOT NULL,
  detected_count INTEGER NOT NULL CHECK(detected_count>=0),
  study_complete INTEGER NOT NULL DEFAULT 0 CHECK(study_complete IN (0,1)),
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_market_runs_day
  ON market_runs(collection_day DESC,created_at DESC);

CREATE TABLE IF NOT EXISTS market_entities (
  wikidata_id TEXT PRIMARY KEY NOT NULL,
  title TEXT NOT NULL,
  first_seen TEXT NOT NULL,
  last_seen TEXT NOT NULL,
  official_website_candidate TEXT,
  research_state TEXT NOT NULL DEFAULT 'market_unverified'
    CHECK(research_state IN ('market_unverified','needs_sources','needs_youtube','market_qualified','rejected')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_market_entities_last_seen
  ON market_entities(last_seen DESC);

CREATE TABLE IF NOT EXISTS market_pageview_observations (
  wikidata_id TEXT NOT NULL REFERENCES market_entities(wikidata_id),
  project TEXT NOT NULL,
  observation_day TEXT NOT NULL,
  rank INTEGER NOT NULL CHECK(rank>=1),
  top_day_views INTEGER NOT NULL CHECK(top_day_views>=0),
  source_url TEXT NOT NULL,
  run_id TEXT NOT NULL REFERENCES market_runs(id),
  PRIMARY KEY(wikidata_id,project,observation_day)
);
CREATE INDEX IF NOT EXISTS idx_market_observations_date
  ON market_pageview_observations(observation_day DESC,top_day_views DESC);

CREATE TABLE IF NOT EXISTS market_interest_windows (
  wikidata_id TEXT NOT NULL REFERENCES market_entities(wikidata_id),
  observed_at TEXT NOT NULL,
  source_url TEXT NOT NULL,
  period_start TEXT NOT NULL,
  period_end TEXT NOT NULL,
  views_last_7d INTEGER NOT NULL CHECK(views_last_7d>=0),
  views_previous_7d INTEGER NOT NULL CHECK(views_previous_7d>=0),
  run_id TEXT NOT NULL REFERENCES market_runs(id),
  PRIMARY KEY(wikidata_id,observed_at,source_url)
);
CREATE INDEX IF NOT EXISTS idx_market_interest_recent
  ON market_interest_windows(observed_at DESC);

-- No autorización implícita de producción, ni OAuth, ni YouTube.
CREATE TABLE IF NOT EXISTS market_selection_decisions (
  id TEXT PRIMARY KEY NOT NULL,
  wikidata_id TEXT NOT NULL REFERENCES market_entities(wikidata_id),
  decision_at TEXT NOT NULL DEFAULT (datetime('now')),
  stage TEXT NOT NULL DEFAULT 'awaiting_evidence'
    CHECK(stage IN ('awaiting_evidence','awaiting_youtube','awaiting_editorial','approved_for_research','rejected')),
  reason_json TEXT NOT NULL DEFAULT '{}',
  reviewer_approved INTEGER NOT NULL DEFAULT 0 CHECK(reviewer_approved IN (0,1))
);
