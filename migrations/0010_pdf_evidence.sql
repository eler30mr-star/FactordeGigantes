-- 0010 Documentos primarios POTENCIALES, sin afirmaciones verificadas ni licencias.
CREATE TABLE IF NOT EXISTS market_pdf_evidence_runs (
 id TEXT PRIMARY KEY NOT NULL,
 collected_on TEXT NOT NULL,
 provider TEXT NOT NULL CHECK(provider='official_pdf_evidence_v1'),
 attempted INTEGER NOT NULL CHECK(attempted BETWEEN 0 AND 2),
 text_extracted INTEGER NOT NULL CHECK(text_extracted BETWEEN 0 AND 2),
 verified_claim_count INTEGER NOT NULL DEFAULT 0 CHECK(verified_claim_count=0),
 created_at TEXT NOT NULL DEFAULT(datetime('now'))
);
CREATE TABLE IF NOT EXISTS market_pdf_evidence_documents (
 run_id TEXT NOT NULL REFERENCES market_pdf_evidence_runs(id),
 wikidata_id TEXT NOT NULL,
 company TEXT NOT NULL,
 source_page TEXT NOT NULL,
 document_url TEXT NOT NULL,
 state TEXT NOT NULL CHECK(state IN ('fetch_failed','text_extracted','pdf_without_usable_text')),
 resolved_url TEXT,
 sha256 TEXT,
 pages_total INTEGER,
 verified_claim_count INTEGER NOT NULL DEFAULT 0 CHECK(verified_claim_count=0),
 copyright_permission_verified INTEGER NOT NULL DEFAULT 0 CHECK(copyright_permission_verified=0),
 PRIMARY KEY(run_id,wikidata_id,document_url)
);
CREATE INDEX IF NOT EXISTS idx_market_pdf_docs_entity ON market_pdf_evidence_documents(wikidata_id);
CREATE TABLE IF NOT EXISTS market_pdf_evidence_fragments (
 run_id TEXT NOT NULL,
 wikidata_id TEXT NOT NULL,
 document_url TEXT NOT NULL,
 page_number INTEGER NOT NULL CHECK(page_number BETWEEN 1 AND 350),
 block_index INTEGER NOT NULL CHECK(block_index BETWEEN 0 AND 20000),
 locator TEXT NOT NULL,
 excerpt TEXT NOT NULL,
 verification_state TEXT NOT NULL DEFAULT 'uncorroborated' CHECK(verification_state='uncorroborated'),
 PRIMARY KEY(run_id,wikidata_id,document_url,block_index),
 FOREIGN KEY(run_id,wikidata_id,document_url)
   REFERENCES market_pdf_evidence_documents(run_id,wikidata_id,document_url)
);
