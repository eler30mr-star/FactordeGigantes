CREATE TABLE IF NOT EXISTS channel_episode_research (
 id TEXT PRIMARY KEY,
 episode_id TEXT NOT NULL REFERENCES channel_episodes(id),
 state TEXT NOT NULL CHECK(state IN ('reserved','sent','unknown','rejected','blocked','review')),
 research_run_id TEXT,
 job_id TEXT,
 note TEXT NOT NULL DEFAULT '',
 created_at TEXT NOT NULL DEFAULT (datetime('now')),
 updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE UNIQUE INDEX IF NOT EXISTS episode_research_one_active ON channel_episode_research(episode_id)
 WHERE state IN ('reserved','sent','unknown');
