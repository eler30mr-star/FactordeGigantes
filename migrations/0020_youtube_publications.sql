CREATE TABLE IF NOT EXISTS youtube_publications (
 export_id TEXT PRIMARY KEY REFERENCES youtube_exports(id),
 request_id TEXT NOT NULL UNIQUE,
 video_id TEXT NOT NULL,
 channel_id TEXT NOT NULL,
 mode TEXT NOT NULL CHECK(mode IN ('public','scheduled')),
 publish_at TEXT,
 reviewer TEXT NOT NULL,
 state TEXT NOT NULL CHECK(state IN ('reserved','confirmed','unknown','failed')),
 last_error TEXT NOT NULL DEFAULT '',
 created_at TEXT NOT NULL DEFAULT (datetime('now')),
 updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
