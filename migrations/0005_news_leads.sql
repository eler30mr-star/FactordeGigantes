-- Factor de Gigantes: señales informativas auxiliares de actualidad (0005)
-- NO equivalen a hechos comprobados, audiencia YouTube ni autorización de investigar/publicar.
CREATE TABLE IF NOT EXISTS market_news_runs (
 id TEXT PRIMARY KEY NOT NULL,
 collected_at TEXT NOT NULL,
 provider TEXT NOT NULL CHECK(provider='google_news_rss'),
 feed_count INTEGER NOT NULL CHECK(feed_count BETWEEN 1 AND 6),
 lead_count INTEGER NOT NULL CHECK(lead_count BETWEEN 0 AND 120),
 created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_market_news_runs_day ON market_news_runs(collected_at DESC);

CREATE TABLE IF NOT EXISTS market_news_leads (
 id TEXT PRIMARY KEY NOT NULL,
 headline TEXT NOT NULL,
 aggregator_url TEXT NOT NULL,
 source_label TEXT NOT NULL,
 category TEXT NOT NULL CHECK(category IN ('empresas','innovacion','tecnologia','industria')),
 published_at TEXT NOT NULL,
 first_seen_at TEXT NOT NULL,
 last_seen_at TEXT NOT NULL,
 latest_run_id TEXT NOT NULL REFERENCES market_news_runs(id),
 verification_state TEXT NOT NULL DEFAULT 'unverified'
   CHECK(verification_state IN ('unverified','needs_original','verified','rejected')),
 youtube_demand_verified INTEGER NOT NULL DEFAULT 0 CHECK(youtube_demand_verified=0),
 editorial_authorized INTEGER NOT NULL DEFAULT 0 CHECK(editorial_authorized=0)
);
CREATE INDEX IF NOT EXISTS idx_market_news_leads_date ON market_news_leads(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_market_news_leads_category ON market_news_leads(category,published_at DESC);
