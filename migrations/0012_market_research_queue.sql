-- Elegir qué INVESTIGAR no verifica hechos ni aprueba un guion/video.
CREATE TABLE IF NOT EXISTS market_research_selection_runs (
 id TEXT PRIMARY KEY NOT NULL,
 observed_on TEXT NOT NULL,
 method TEXT NOT NULL CHECK(method='research_market_priority_v1'),
 candidate_count INTEGER NOT NULL CHECK(candidate_count BETWEEN 0 AND 50),
 qualified_count INTEGER NOT NULL CHECK(qualified_count BETWEEN 0 AND 50),
 ranked_snapshot_json TEXT NOT NULL CHECK(json_valid(ranked_snapshot_json)),
 publication_authorized INTEGER NOT NULL DEFAULT 0 CHECK(publication_authorized=0),
 created_at TEXT NOT NULL DEFAULT(datetime('now'))
);
CREATE TABLE IF NOT EXISTS market_research_queue (
 id TEXT PRIMARY KEY NOT NULL,
 wikidata_id TEXT NOT NULL REFERENCES market_entities(wikidata_id),
 title TEXT NOT NULL,
 selection_run_id TEXT NOT NULL REFERENCES market_research_selection_runs(id),
 market_score REAL NOT NULL CHECK(market_score BETWEEN 0 AND 100),
 state TEXT NOT NULL DEFAULT 'awaiting_sources'
   CHECK(state IN ('awaiting_sources','researching','review','closed')),
 script_authorized INTEGER NOT NULL DEFAULT 0 CHECK(script_authorized=0),
 publication_authorized INTEGER NOT NULL DEFAULT 0 CHECK(publication_authorized=0),
 created_at TEXT NOT NULL DEFAULT(datetime('now')),
 updated_at TEXT NOT NULL DEFAULT(datetime('now'))
);
-- Solo un episodio en investigación: peticiones simultáneas no crean dos trabajos.
CREATE UNIQUE INDEX IF NOT EXISTS idx_research_queue_one_active
 ON market_research_queue((1)) WHERE state IN ('awaiting_sources','researching','review');
CREATE INDEX IF NOT EXISTS idx_research_queue_entity ON market_research_queue(wikidata_id,created_at DESC);
