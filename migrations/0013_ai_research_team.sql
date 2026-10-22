-- Aditiva: no reconstruye tablas ni altera trabajos/expedientes anteriores.
CREATE TABLE IF NOT EXISTS ai_budget_reservations (
 id TEXT PRIMARY KEY,
 provider TEXT NOT NULL CHECK(provider IN ('tavily','exa','gemini','groq','mistral','openrouter','cloudflare')),
 reserved_day TEXT NOT NULL,
 reserved_month TEXT NOT NULL,
 created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_ai_budget_period ON ai_budget_reservations(provider,reserved_month,reserved_day);
CREATE TABLE IF NOT EXISTS market_ai_pipeline_runs (
 id TEXT PRIMARY KEY,
 collected_on TEXT NOT NULL,
 wikidata_id TEXT,
 status TEXT NOT NULL CHECK(status IN ('skipped_no_documentary_evidence','sources_only','candidate_claims_generated')),
 analysis_provider TEXT CHECK(analysis_provider IN ('gemini','qwen','mistral','openrouter')),
 evidence_count INTEGER NOT NULL CHECK(evidence_count BETWEEN 0 AND 10),
 claims_count INTEGER NOT NULL CHECK(claims_count BETWEEN 0 AND 8),
 report_json TEXT NOT NULL CHECK(json_valid(report_json)),
 verified_claim_count INTEGER NOT NULL DEFAULT 0 CHECK(verified_claim_count=0),
 script_authorized INTEGER NOT NULL DEFAULT 0 CHECK(script_authorized=0),
 publication_authorized INTEGER NOT NULL DEFAULT 0 CHECK(publication_authorized=0),
 created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_ai_pipeline_recent ON market_ai_pipeline_runs(created_at DESC);
