CREATE TABLE IF NOT EXISTS youtube_exports (
 id TEXT PRIMARY KEY,
 source_run_id TEXT NOT NULL,
 artifact_id TEXT NOT NULL,
 archive_sha256 TEXT NOT NULL,
 video_bytes INTEGER NOT NULL,
 episode_json TEXT NOT NULL,
 export_json TEXT NOT NULL,
 metadata_json TEXT NOT NULL,
 state TEXT NOT NULL DEFAULT 'review' CHECK(state IN ('review','approved','queued','initiating','uploading','uploaded','unknown')),
 review_json TEXT NOT NULL DEFAULT '{}',
 target_channel_id TEXT NOT NULL DEFAULT '',
 request_id TEXT UNIQUE,
 session_encrypted TEXT NOT NULL DEFAULT '',
 video_id TEXT NOT NULL DEFAULT '',
 last_error TEXT NOT NULL DEFAULT '',
 created_at TEXT NOT NULL DEFAULT (datetime('now')),
 updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS youtube_export_events (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 export_id TEXT NOT NULL REFERENCES youtube_exports(id),
 action TEXT NOT NULL,
 note TEXT NOT NULL DEFAULT '',
 created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_youtube_export_events ON youtube_export_events(export_id,id DESC);
