-- Factor de Gigantes: investigación solicitada explícitamente por el administrador.
-- Sin tareas automáticas, sin publicación; consumo máximo de cuatro solicitudes/día UTC.
-- Solo nueva tabla: preservar jobs, eventos, y expedientes anteriores.
CREATE TABLE IF NOT EXISTS research_requests (
  id TEXT PRIMARY KEY NOT NULL,
  topic TEXT NOT NULL,
  topic_key TEXT NOT NULL,
  day_utc TEXT NOT NULL,
  state TEXT NOT NULL DEFAULT 'reserved'
    CHECK (state IN ('reserved', 'sent', 'unknown', 'rejected')),
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE(topic_key,day_utc)
);
CREATE INDEX IF NOT EXISTS idx_research_requests_date
  ON research_requests(day_utc,created_at DESC);
