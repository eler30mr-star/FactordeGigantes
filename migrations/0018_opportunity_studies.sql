CREATE TABLE IF NOT EXISTS channel_opportunity_studies (
 id TEXT PRIMARY KEY,
 channel TEXT NOT NULL REFERENCES channel_control(channel),
 day_utc TEXT NOT NULL,
 mode_revision INTEGER NOT NULL,
 state TEXT NOT NULL DEFAULT 'running' CHECK(state IN ('running','calibration','insufficient','selected','cancelled')),
 report_json TEXT NOT NULL DEFAULT '{}',
 assessment_json TEXT NOT NULL DEFAULT '{}',
 created_at TEXT NOT NULL DEFAULT (datetime('now')),
 updated_at TEXT NOT NULL DEFAULT (datetime('now')),
 UNIQUE(channel,day_utc)
);
