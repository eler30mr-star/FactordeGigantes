-- Control persistente del canal y episodios elegidos; no modifica trabajos anteriores.
CREATE TABLE IF NOT EXISTS channel_control (
 channel TEXT PRIMARY KEY CHECK(channel='factor-de-gigantes'),
 automatic_enabled INTEGER NOT NULL DEFAULT 0 CHECK(automatic_enabled IN (0,1)),
 revision INTEGER NOT NULL DEFAULT 0 CHECK(revision>=0),
 pending_company TEXT NOT NULL DEFAULT '',
 pending_instruction TEXT NOT NULL DEFAULT '',
 last_operation TEXT NOT NULL DEFAULT '',
 updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
INSERT OR IGNORE INTO channel_control(channel) VALUES ('factor-de-gigantes');
CREATE TABLE IF NOT EXISTS channel_episodes (
 id TEXT PRIMARY KEY,
 channel TEXT NOT NULL REFERENCES channel_control(channel),
 origin TEXT NOT NULL CHECK(origin IN ('chat','automatic')),
 company TEXT NOT NULL CHECK(length(company) BETWEEN 2 AND 100),
 topic TEXT NOT NULL CHECK(length(topic) BETWEEN 5 AND 300),
 instruction TEXT NOT NULL,
 state TEXT NOT NULL DEFAULT 'selected' CHECK(state IN ('selected','researching','producing','review','completed','cancelled')),
 created_at TEXT NOT NULL DEFAULT (datetime('now')),
 updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE UNIQUE INDEX IF NOT EXISTS channel_episode_active ON channel_episodes(channel)
 WHERE state NOT IN ('completed','cancelled');
CREATE TABLE IF NOT EXISTS channel_control_events (
 request_id TEXT PRIMARY KEY,
 channel TEXT NOT NULL REFERENCES channel_control(channel),
 kind TEXT NOT NULL CHECK(kind IN ('mode','chat')),
 payload_json TEXT NOT NULL,
 result_json TEXT NOT NULL,
 actor TEXT NOT NULL DEFAULT 'authenticated_owner',
 created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS channel_control_history ON channel_control_events(channel,created_at);
