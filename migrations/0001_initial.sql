CREATE TABLE IF NOT EXISTS jobs (
 id TEXT PRIMARY KEY,
 title TEXT NOT NULL,
 format TEXT NOT NULL CHECK(format IN ('short','long')),
 status TEXT NOT NULL DEFAULT 'draft'
  CHECK(status IN ('draft','review','approved','queued','rendering','ready','failed')),
 manifest_json TEXT NOT NULL,
 review_note TEXT NOT NULL DEFAULT '',
 last_error TEXT NOT NULL DEFAULT '',
 created_at TEXT NOT NULL DEFAULT (datetime('now')),
 updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_jobs_updated ON jobs(updated_at DESC);
CREATE TABLE IF NOT EXISTS events (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 job_id TEXT NOT NULL,
 action TEXT NOT NULL,
 note TEXT NOT NULL DEFAULT '',
 created_at TEXT NOT NULL DEFAULT (datetime('now')),
 FOREIGN KEY (job_id) REFERENCES jobs(id)
);
CREATE INDEX IF NOT EXISTS idx_events_job ON events(job_id, id DESC);
