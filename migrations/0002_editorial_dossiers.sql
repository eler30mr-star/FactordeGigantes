-- Factor de Gigantes: expediente editorial por documental.
-- Aplicar con Wrangler a D1 antes de desplegar el Worker que lo usa.
-- La tabla original jobs/events permanece intacta.
CREATE TABLE IF NOT EXISTS editorial_dossiers (
  job_id TEXT PRIMARY KEY NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
  dossier_json TEXT NOT NULL,
  editor_attested INTEGER NOT NULL DEFAULT 0 CHECK(editor_attested IN (0,1)),
  editor_name TEXT NOT NULL DEFAULT '',
  attested_at TEXT,
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_editorial_dossiers_attested
  ON editorial_dossiers(editor_attested, updated_at DESC);
