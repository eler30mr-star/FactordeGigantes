// Historial IA del radar: evidencias con hash y citas; ninguna verificación factual.
const QID=/^Q[1-9][0-9]*$/,SHA=/^[a-f0-9]{64}$/,DAY=/^\d{4}-\d{2}-\d{2}$/;
const STATES=new Set(["skipped_no_documentary_evidence","skipped_free_tier_not_authorized",
  "research_provider_failure","candidate_claims_generated"]);
const PROVIDERS=new Set(["gemini_free","qwen_local"]);
const numericTokens=s=>[...new Set((s.match(/(?<![A-Za-z0-9])\d+(?:[.,]\d+)*(?![A-Za-z0-9])/g)||[]))];
function urlHttps(v){
 if(typeof v!=="string"||v.length<12||v.length>1200)throw new RangeError("URL documental inválida");
 const u=new URL(v);
 if(u.protocol!=="https:"||!u.hostname||u.username||u.password||u.port||u.hash)
   throw new RangeError("Solo URL pública HTTPS");
 if(/^(localhost|127\.|10\.|0\.|192\.168\.|169\.254\.)/i.test(u.hostname)||
    u.hostname.endsWith(".internal")||u.hostname.endsWith(".local")||
    u.hostname==="[::1]")throw new RangeError("Host documental no público");
 return u.href;
}
export function validateMarketResearch(report,now=Date.now()){
 const r=report;
 if(!r||typeof r!=="object"||Array.isArray(r)||
   r.source_provider!=="market_official_and_pdf_v1"||!STATES.has(r.status)||
   r.facts_verified_automatically!==0||r.ready_for_script!==false||
   r.ready_for_youtube!==false||r.publication_authorized!==false||
   r.production_ready===true||r.script_authorized===true||
   !DAY.test(r.source_report_day)||!Array.isArray(r.evidence_manifest)||
   r.evidence_manifest.length>10||r.evidence_count!==r.evidence_manifest.length||
   !Array.isArray(r.candidate_claims)||r.candidate_claims.length>8||
   !Array.isArray(r.missing_questions)||r.missing_questions.length>8)
     throw new RangeError("Investigación no verificable o autorizada indebidamente");
 const d=Date.parse(r.source_report_day+"T00:00:00Z");
 if(!Number.isFinite(d)||new Date(d).toISOString().slice(0,10)!==r.source_report_day||
    d>now+86400000||d<now-7*86400000)throw new RangeError("Investigación fuera de fecha");
 if(r.status==="skipped_no_documentary_evidence"&&r.evidence_count!==0)
   throw new RangeError("No puede omitirse por falta de fuentes con fuentes presentes");
 if(r.status==="skipped_free_tier_not_authorized"&&r.evidence_count===0)
   throw new RangeError("Omisión de cuota con expediente vacío");
 if(r.status!=="candidate_claims_generated" &&
     (r.candidate_claims.length||r.missing_questions.length||r.provider!==null&&r.provider!==undefined))
   throw new RangeError("Modelo no invocado no puede afirmar ni citar");
 if(r.status==="candidate_claims_generated"&&
    (!PROVIDERS.has(r.provider)||!SHA.test(r.prompt_sha256)||typeof r.model!=="string"||
     !/^[a-zA-Z0-9_./-]{5,100}$/.test(r.model)))
   throw new RangeError("Modelo real sin identidad y huella del prompt");
 const evidence=[],known=new Map();
 for(let i=0;i<r.evidence_manifest.length;i++){
  const e=r.evidence_manifest[i],id="E"+String(i+1).padStart(3,"0");
  if(!e||typeof e!=="object"||e.id!==id||!QID.test(e.wikidata_id)||
    typeof e.company!=="string"||e.company.length<4||e.company.length>130||
    typeof e.excerpt!=="string"||e.excerpt.length<90||e.excerpt.length>320||
    !SHA.test(e.document_sha256)||
    !["potential_official_primary","potential_official_pdf"].includes(e.source_class))
    throw new RangeError("Evidencia sin huella o fuente válida");
  const url=urlHttps(e.url);
  const pdf=e.source_class==="potential_official_pdf";
  if(pdf?(!Number.isSafeInteger(e.page)||e.page<1||e.page>350):e.page!==null)
    throw new RangeError("Página PDF no vinculada a documento");
  known.set(id,e);
  evidence.push([id,e.wikidata_id,e.company,url,e.document_sha256,
     pdf?"corporate_pdf_candidate":"corporate_page_candidate",e.page,e.excerpt]);
 }
 const claims=[],citations=[];
 for(let i=0;i<r.candidate_claims.length;i++){
  const c=r.candidate_claims[i];
  if(!c||typeof c.statement!=="string"||c.statement.trim().length<10||
     c.statement.length>650||!Array.isArray(c.evidence_ids)||
     c.evidence_ids.length<1||c.evidence_ids.length>8||
     c.status!=="candidate_unverified"||c.human_verified!==false)
    throw new RangeError("Afirmación sin referencia no aprobada");
  const ids=[...new Set(c.evidence_ids)];
  if(ids.length!==c.evidence_ids.length||ids.some(id=>!known.has(id)))
    throw new RangeError("Cita inexistente o repetida");
  const numbers=numericTokens(c.statement);
  const supported=new Set(ids.flatMap(id=>numericTokens(known.get(id).excerpt)));
  const state=!numbers.length?"no_numeric_assertion":
    numbers.every(n=>supported.has(n))?"numbers_appear_in_cited_excerpts":"unsupported_numbers_need_review";
  claims.push([i+1,c.statement,state]);
  for(const id of ids)citations.push([i+1,id]);
 }
 const questions=[];
 for(let i=0;i<r.missing_questions.length;i++){
  const q=r.missing_questions[i];
  if(typeof q!=="string"||q.trim().length<8||q.length>220)
    throw new RangeError("Pregunta investigadora inválida");
  questions.push([i+1,q.trim()]);
 }
 return {evidence,claims,citations,questions,provider:r.provider??null,
   model:r.model??null,prompt:r.prompt_sha256??null};
}
export async function storeMarketResearch(db,r){
 const v=validateMarketResearch(r);
 const bytes=new TextEncoder().encode(JSON.stringify(r));
 const digest=[...new Uint8Array(await crypto.subtle.digest("SHA-256",bytes))]
   .map(x=>x.toString(16).padStart(2,"0")).join("");
 const id="research-"+digest.slice(0,28);
 const stmts=[
  db.prepare("INSERT OR IGNORE INTO market_research_runs(id,collected_on,source_provider,status,model_provider,model_id,prompt_sha256,evidence_count,claims_count,questions_count) VALUES (?,?,?,?,?,?,?,?,?,?)")
   .bind(id,r.source_report_day,r.source_provider,r.status,v.provider,v.model,v.prompt,
     v.evidence.length,v.claims.length,v.questions.length),
  ...v.evidence.map(e=>db.prepare("INSERT OR IGNORE INTO market_research_evidence(run_id,evidence_id,wikidata_id,company,source_url,document_sha256,source_kind,pdf_page,excerpt) VALUES (?,?,?,?,?,?,?,?,?)").bind(id,...e)),
  ...v.claims.map(c=>db.prepare("INSERT OR IGNORE INTO market_research_claims(run_id,claim_index,statement,numeric_support_state) VALUES (?,?,?,?)").bind(id,...c)),
  ...v.citations.map(c=>db.prepare("INSERT OR IGNORE INTO market_research_claim_evidence(run_id,claim_index,evidence_id) VALUES (?,?,?)").bind(id,...c)),
  ...v.questions.map(q=>db.prepare("INSERT OR IGNORE INTO market_research_questions(run_id,question_index,question) VALUES (?,?,?)").bind(id,...q))
 ];
 await db.batch(stmts);
 return {ok:true,stored_in:"d1",run_id:id,status:r.status,
   evidence_count:v.evidence.length,candidate_claim_count:v.claims.length,
   open_question_count:v.questions.length,verified_claim_count:0,
   automatic_publication_allowed:false};
}
export async function readMarketResearch(db,url){
 const raw=url.searchParams.get("limit")??"20";
 if(!/^\d{1,2}$/.test(raw)||Number(raw)<1||Number(raw)>50)
   return {error:"Límite entre 1 y 50",status:400};
 try{
  const [runs,evidence,claims,refs,questions]=await Promise.all([
   db.prepare("SELECT id,collected_on,status,model_provider,model_id,evidence_count,claims_count,questions_count,verified_claim_count FROM market_research_runs ORDER BY created_at DESC, rowid DESC LIMIT 10").all(),
   db.prepare("SELECT evidence_id,wikidata_id,company,source_url,document_sha256,source_kind,pdf_page,excerpt FROM market_research_evidence WHERE run_id=(SELECT id FROM market_research_runs ORDER BY created_at DESC,rowid DESC LIMIT 1) ORDER BY evidence_id LIMIT ?").bind(Number(raw)).all(),
   db.prepare("SELECT claim_index,statement,numeric_support_state,review_state FROM market_research_claims WHERE run_id=(SELECT id FROM market_research_runs ORDER BY created_at DESC,rowid DESC LIMIT 1) ORDER BY claim_index LIMIT ?").bind(Number(raw)).all(),
   db.prepare("SELECT claim_index,evidence_id FROM market_research_claim_evidence WHERE run_id=(SELECT id FROM market_research_runs ORDER BY created_at DESC,rowid DESC LIMIT 1) ORDER BY claim_index,evidence_id LIMIT 50").all(),
   db.prepare("SELECT question_index,question FROM market_research_questions WHERE run_id=(SELECT id FROM market_research_runs ORDER BY created_at DESC,rowid DESC LIMIT 1) ORDER BY question_index LIMIT 8").all()
  ]);
  return {ok:true,runs:runs.results||[],evidence:evidence.results||[],
    claims:claims.results||[],citations:refs.results||[],questions:questions.results||[],
    verified_claim_count:0,automatic_publication_allowed:false,
    warning:"Informe de IA y fuentes candidatas. No son hechos corroborados, guion aprobado ni autorización comercial."};
 }catch(e){
  if(/no such table:\s*market_research_/i.test(String(e?.message||"")))
   return {error:"Falta migración 0011_market_research.sql",status:503};
  throw e;
 }
}
