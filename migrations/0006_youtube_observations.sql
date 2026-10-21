-- 0006: evidencia pública YouTube Data API v3; aditivo y sin autorizaciones editoriales.
-- Muestra parcial obtenida desde search.list + videos.list, NO demanda total ni datos privados.
CREATE TABLE IF NOT EXISTS market_youtube_runs (
 id TEXT PRIMARY KEY NOT NULL,
 collected_on TEXT NOT NULL,
 provider TEXT NOT NULL CHECK(provider='youtube_data_api_v3'),
 region_count INTEGER NOT NULL CHECK(region_count BETWEEN 1 AND 2),
 candidate_count INTEGER NOT NULL CHECK(candidate_count BETWEEN 1 AND 2),
 queries_attempted INTEGER NOT NULL CHECK(queries_attempted BETWEEN 0 AND 4),
 quota_units_max INTEGER NOT NULL CHECK(quota_units_max BETWEEN 0 AND 404),
 state TEXT NOT NULL CHECK(state IN ('partial','measured')),
 market_study_complete INTEGER NOT NULL DEFAULT 0 CHECK(market_study_complete=0),
 created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_market_youtube_runs_day ON market_youtube_runs(collected_on DESC);
CREATE TABLE IF NOT EXISTS market_youtube_queries (
 run_id TEXT NOT NULL REFERENCES market_youtube_runs(id),
 wikidata_id TEXT NOT NULL REFERENCES market_entities(wikidata_id),
 topic TEXT NOT NULL,
 region TEXT NOT NULL CHECK(region IN ('MX','PE','ES','CO','AR','CL')),
 observed_on TEXT NOT NULL,
 sample_size INTEGER NOT NULL CHECK(sample_size BETWEEN 0 AND 10),
 uploads_sampled INTEGER NOT NULL CHECK(uploads_sampled BETWEEN 0 AND 10),
 median_daily_views REAL,
 distinct_channels INTEGER NOT NULL CHECK(distinct_channels BETWEEN 0 AND 10),
 evidence_state TEXT NOT NULL CHECK(evidence_state IN ('observed_sample','insufficient_sample')),
 PRIMARY KEY(run_id,wikidata_id,region)
);
CREATE INDEX IF NOT EXISTS idx_market_youtube_queries_entity ON market_youtube_queries(wikidata_id,observed_on DESC);
CREATE TABLE IF NOT EXISTS market_youtube_videos (
 run_id TEXT NOT NULL,
 wikidata_id TEXT NOT NULL,
 region TEXT NOT NULL,
 video_id TEXT NOT NULL,
 published_on TEXT NOT NULL,
 view_count INTEGER NOT NULL CHECK(view_count>=0),
 channel_id TEXT,
 video_url TEXT NOT NULL,
 FOREIGN KEY(run_id,wikidata_id,region) REFERENCES market_youtube_queries(run_id,wikidata_id,region),
 PRIMARY KEY(run_id,wikidata_id,region,video_id)
);
CREATE INDEX IF NOT EXISTS idx_market_youtube_video_date ON market_youtube_videos(published_on DESC);
