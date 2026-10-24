-- Guiones automáticos pendientes de revisión; no altera trabajos anteriores.
CREATE TABLE IF NOT EXISTS autonomous_script_drafts (
 research_run_id TEXT PRIMARY KEY REFERENCES market_ai_pipeline_runs(id),
 job_id TEXT NOT NULL UNIQUE REFERENCES jobs(id),
 wikidata_id TEXT NOT NULL,
 script_sha256 TEXT NOT NULL CHECK(length(script_sha256)=64),
 source_evidence_sha256 TEXT NOT NULL CHECK(length(source_evidence_sha256)=64),
 script_json TEXT NOT NULL CHECK(json_valid(script_json)),
 automatic_factual_approval INTEGER NOT NULL DEFAULT 0 CHECK(automatic_factual_approval=0),
 automatic_render_approval INTEGER NOT NULL DEFAULT 0 CHECK(automatic_render_approval=0),
 publication_authorized INTEGER NOT NULL DEFAULT 0 CHECK(publication_authorized=0),
 created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_autonomous_drafts_company ON autonomous_script_drafts(wikidata_id);
