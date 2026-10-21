// Evidencias PDF: pasajes con localizador real, nunca hechos o derechos aprobados.
const QID=/^Q[1-9][0-9]*$/,SHA=/^[a-f0-9]{64}$/,DAY=/^\d{4}-\d{2}-\d{2}$/;
const STATES=new Set(["fetch_failed","text_extracted","pdf_without_usable_text"]);
function https(input){
 if(typeof input!=="string"||input.length<12||input.length>1000)throw new RangeError("URL no válida");
 const u=new URL(input);
 if(u.protocol!=="https:"||!u.hostname||u.username||u.password||u.port||u.hash)throw new RangeError("HTTPS público necesario");
 if(/^(localhost|127\.|10\.|192\.168\.|169\.254\.|0\.)/i.test(u.hostname)||
   /\.(local|internal)$/.test(u.hostname))throw new RangeError("Host privado prohibido");
 return u;
}
export function validatePdfEvidence(r,now=Date.now()){
 if(!r||typeof r!=="object"||r.provider!=="official_pdf_evidence_v1"||
   !DAY.test(r.collected_on)||r.verified_claim_count!==0||
   r.research_ready!==false||r.script_authorized!==false||r.publication_authorized!==false||
   !Array.isArray(r.documents)||r.documents.length>2||r.attempted!==r.documents.length||
   !Number.isSafeInteger(r.text_extracted)||r.text_extracted<0||r.text_extracted>2)
   throw new RangeError("Informe PDF no preliminar");
 const stamp=Date.parse(r.collected_on+"T00:00:00Z");
 if(!Number.isFinite(stamp)||new Date(stamp).toISOString().slice(0,10)!==r.collected_on||
   stamp>now+86400000||stamp<now-7*86400000)throw new RangeError("Informe PDF caduco");
 const keys=new Set(),docs=[],frags=[];
 for(const d of r.documents){
  if(!d||typeof d!=="object"||!QID.test(d.wikidata_id)||
     typeof d.company!=="string"||d.company.trim().length<4||d.company.length>130||
     !STATES.has(d.state)||d.facts_verified!==0||d.copyright_permission_verified!==false||
     !Array.isArray(d.fragments)||d.fragments.length>5)throw new RangeError("Documento sin procedencia");
  const origin=https(d.source_page),original=https(d.document_url);
  if(!original.pathname.toLowerCase().endsWith(".pdf")||origin.hostname!==original.hostname)
    throw new RangeError("PDF de dominio diferente");
  const id=d.wikidata_id+"|"+original.href;
  if(keys.has(id))throw new RangeError("Documento duplicado");
  keys.add(id);
  let resolved=null;
  if(d.state==="fetch_failed"){
   if(d.resolved_url!==null||d.sha256!==null||d.pages_total!==null||d.fragments.length)
     throw new RangeError("Fallo remoto con fragmentos ficticios");
  }else{
   resolved=https(d.resolved_url);
   if(resolved.hostname!==origin.hostname||!SHA.test(d.sha256)||
      !Number.isSafeInteger(d.pages_total)||d.pages_total<1||d.pages_total>350||
      (d.state==="text_extracted")!==(d.fragments.length>0))
     throw new RangeError("Documento no compatible con citas");
  }
  const indices=new Set();
  for(const fragment of d.fragments){
   if(!fragment||!Number.isSafeInteger(fragment.page)||fragment.page<1||
      fragment.page>d.pages_total||!Number.isSafeInteger(fragment.block_index)||
      fragment.block_index<0||fragment.block_index>20000||
      indices.has(fragment.block_index)||fragment.verification_state!=="uncorroborated"||
      typeof fragment.excerpt!=="string"||fragment.excerpt.length<90||fragment.excerpt.length>320||
      fragment.locator!=="PDF página "+fragment.page+", bloque "+(fragment.block_index+1))
     throw new RangeError("Localizador o texto incoherente");
   indices.add(fragment.block_index);
   frags.push([d.wikidata_id,original.href,fragment.page,fragment.block_index,
      fragment.locator,fragment.excerpt]);
  }
  docs.push([d.wikidata_id,d.company,origin.href,original.href,d.state,
    resolved?.href??null,d.sha256,d.pages_total??null]);
 }
 if(r.text_extracted!==r.documents.filter(d=>d.state==="text_extracted").length)
   throw new RangeError("Cuenta de documentos legibles no coincide");
 return {docs,frags};
}
export async function storePdfEvidence(db,report){
 const {docs,frags}=validatePdfEvidence(report);
 const bytes=new TextEncoder().encode(JSON.stringify(report));
 const h=[...new Uint8Array(await crypto.subtle.digest("SHA-256",bytes))]
  .map(b=>b.toString(16).padStart(2,"0")).join("").slice(0,24);
 const id="pdf-"+h;
 const stmts=[db.prepare("INSERT OR IGNORE INTO market_pdf_evidence_runs(id,collected_on,provider,attempted,text_extracted) VALUES (?,?,?,?,?)")
  .bind(id,report.collected_on,report.provider,report.attempted,report.text_extracted),
  ...docs.map(d=>db.prepare("INSERT OR IGNORE INTO market_pdf_evidence_documents(run_id,wikidata_id,company,source_page,document_url,state,resolved_url,sha256,pages_total) VALUES (?,?,?,?,?,?,?,?,?)").bind(id,...d)),
  ...frags.map(f=>db.prepare("INSERT OR IGNORE INTO market_pdf_evidence_fragments(run_id,wikidata_id,document_url,page_number,block_index,locator,excerpt) VALUES (?,?,?,?,?,?,?)").bind(id,...f))
 ];
 await db.batch(stmts);
 return {ok:true,stored_in:"d1",run_id:id,documents:docs.length,fragments:frags.length,
   verified_claim_count:0,automatic_publication_allowed:false};
}
export async function readPdfEvidence(db,url){
 const raw=url.searchParams.get("limit")??"20";
 if(!/^\d{1,2}$/.test(raw)||Number(raw)<1||Number(raw)>50)
   return {error:"Límite entre 1 y 50",status:400};
 try{
  const [runs,docs,frags]=await Promise.all([
   db.prepare("SELECT id,collected_on,attempted,text_extracted FROM market_pdf_evidence_runs ORDER BY created_at DESC LIMIT 5").all(),
   db.prepare("SELECT wikidata_id,company,document_url,state,sha256,pages_total FROM market_pdf_evidence_documents ORDER BY rowid DESC LIMIT ?").bind(Number(raw)).all(),
   db.prepare("SELECT wikidata_id,document_url,page_number,locator,excerpt FROM market_pdf_evidence_fragments ORDER BY rowid DESC LIMIT ?").bind(Number(raw)).all()
  ]);
  return {ok:true,runs:runs.results||[],documents:docs.results||[],fragments:frags.results||[],
   facts_verified:0,automatic_publication_allowed:false,
   warning:"Fragmentos PDF textuales localizados sin corroboración factual ni autorización comercial."};
 }catch(e){
  if(/no such table:\s*market_pdf_/i.test(String(e?.message||"")))
   return {error:"Falta migración 0010_pdf_evidence.sql",status:503};
  throw e;
 }
}
