CREATE TABLE IF NOT EXISTS youtube_oauth_flows (
 state_sha256 TEXT PRIMARY KEY,
 cookie_sha256 TEXT NOT NULL,
 payload_encrypted TEXT NOT NULL,
 expires_at INTEGER NOT NULL,
 claimed_at INTEGER,
 outcome TEXT NOT NULL DEFAULT 'pending'
);
CREATE INDEX IF NOT EXISTS idx_youtube_oauth_expiry ON youtube_oauth_flows(expires_at);
CREATE TABLE IF NOT EXISTS youtube_connections (
 id TEXT PRIMARY KEY CHECK(id='primary'),
 channel_id TEXT NOT NULL,
 channel_title TEXT NOT NULL,
 credentials_encrypted TEXT NOT NULL,
 scopes TEXT NOT NULL,
 token_expires_at INTEGER NOT NULL,
 connected_at INTEGER NOT NULL,
 updated_at INTEGER NOT NULL
);
