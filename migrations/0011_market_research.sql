-- 0011: expedientes del investigador autónomo, evidencia/citas/afirmaciones/preguntas.
-- Todo material derivado es CANDIDATO; ninguna tabla otorga verificación ni publicación.
CREATE TABLE IF NOT EXISTS market_research_runs (
  id TEXT PRIMARY KEY NOT NULL,
  collected_on TEXT NOT NULL,
  source_provider TEXT NOT NULL CHECK(source_provider='market_official_and_pdf_v1'),
  status TEXT NOT NULL CHECK(status IN
    ('skipped_no_documentary_evidence','skipped_free_tier_not_authorized',
     'research_provider_failure','candidate_claims_generated')),
  model_provider TEXT CHECK(model_provider IN ('gemini_free','qwen_local') OR model_provider IS NULL),
  model_id TEXT,
  prompt_sha256 TEXT,
  evidence_count INTEGER NOT NULL CHECK(evidence_count BETWEEN 0 AND 10),
  claims_count INTEGER NOT NULL CHECK(claims_count BETWEEN 0 AND 8),
  questions_count INTEGER NOT NULL CHECK(questions_count BETWEEN 0 AND 8),
  verified_claim_count INTEGER NOT NULL DEFAULT 0 CHECK(verified_claim_count=0),
  script_authorized INTEGER NOT NULL DEFAULT 0 CHECK(script_authorized=0),
  publication_authorized INTEGER NOT NULL DEFAULT 0 CHECK(publication_authorized=0),
  created_at TEXT NOT NULL DEFAULT(datetime('now')),
  CHECK(status='candidate_claims_generated' OR claims_count=0)
);
CREATE INDEX IF NOT EXISTS idx_market_research_runs_date ON market_research_runs(collected_on DESC, created_at DESC);

CREATE TABLE IF NOT EXISTS market_research_evidence (
  run_id TEXT NOT NULL REFERENCES market_research_runs(id),
  evidence_id TEXT NOT NULL,
  wikidata_id TEXT NOT NULL,
  company TEXT NOT NULL,
  source_url TEXT NOT NULL,
  document_sha256 TEXT NOT NULL,
  source_kind TEXT NOT NULL CHECK(source_kind IN ('corporate_page_candidate','corporate_pdf_candidate')),
  pdf_page INTEGER,
  excerpt TEXT NOT NULL,
  verification_state TEXT NOT NULL DEFAULT 'uncorroborated' CHECK(verification_state='uncorroborated'),
  PRIMARY KEY(run_id,evidence_id)
);
CREATE INDEX IF NOT EXISTS idx_market_research_evidence_entity ON market_research_evidence(wikidata_id);

CREATE TABLE IF NOT EXISTS market_research_claims (
  run_id TEXT NOT NULL REFERENCES market_research_runs(id),
  claim_index INTEGER NOT NULL CHECK(claim_index BETWEEN 1 AND 8),
  statement TEXT NOT NULL,
  review_state TEXT NOT NULL DEFAULT 'candidate_unverified' CHECK(review_state='candidate_unverified'),
  numeric_support_state TEXT NOT NULL CHECK(numeric_support_state IN
    ('no_numeric_assertion','numbers_appear_in_cited_excerpts','unsupported_numbers_need_review')),
  approved INTEGER NOT NULL DEFAULT 0 CHECK(approved=0),
  PRIMARY KEY(run_id,claim_index)
);
CREATE TABLE IF NOT EXISTS market_research_claim_evidence (
  run_id TEXT NOT NULL,
  claim_index INTEGER NOT NULL,
  evidence_id TEXT NOT NULL,
  PRIMARY KEY(run_id,claim_index,evidence_id),
  FOREIGN KEY(run_id,claim_index) REFERENCES market_research_claims(run_id,claim_index),
  FOREIGN KEY(run_id,evidence_id) REFERENCES market_research_evidence(run_id,evidence_id)
);
CREATE TABLE IF NOT EXISTS market_research_questions (
  run_id TEXT NOT NULL REFERENCES market_research_runs(id),
  question_index INTEGER NOT NULL CHECK(question_index BETWEEN 1 AND 8),
  question TEXT NOT NULL,
  state TEXT NOT NULL DEFAULT 'unanswered' CHECK(state='unanswered'),
  PRIMARY KEY(run_id,question_index)
);
