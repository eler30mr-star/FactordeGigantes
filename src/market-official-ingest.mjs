// Trazabilidad de páginas candidatas P856: hash/extracto, jamás hechos certificados.
const QID=/^Q[1-9][0-9]*$/,DAY=/^\d{4}-\d{2}-\d{2}$/,SHA=/^[a-f0-9]{64}$/;
const sources=new Set(["wikidata_p856_via_news","wikidata_p856_via_wiki"]);
const statuses=new Set(["candidate_unreachable","candidate_page_readable","candidate_page_unreadable"]);
function validUrl(v,nullable=false){
 if(nullable&&(v===null||v===undefined))return null;
 if(typeof v!=="string"||v.length<12||v.length>1000)throw new RangeError("URL inválida");
 const u=new URL(v);
 if(u.protocol!=="https:"||!u.hostname||u.username||u.password||u.port||u.hash)throw new RangeError("Fuente no HTTPS");
 if(/^(localhost|127\.|0\.|169\.254\.|10\.|192\.168\.|172\.|\[?::1)/i.test(u.hostname)||
    u.hostname.endsWith(".internal")||u.hostname.endsWith(".local"))throw new RangeError("Dominio reservado");
 return u.href;
}
export function validateOfficialEvidence(report,now=Date.now()){
 const r=report;
 if(!r||typeof r!=="object"||r.provider!=="wikidata_p856_safe_official_fetch_v1"||
    !DAY.test(r.collected_on)||r.market_study_complete!==false||
    r.research_automatic!==false||r.ready_for_script!==false||
    r.ready_for_youtube!==false||r.primary_facts_verified!==0||
    !Array.isArray(r.evidence)||r.evidence.length>3||r.attempted!==r.evidence.length||
    !Number.isSafeInteger(r.readable)||r.readable<0||r.readable>3)
    throw new RangeError("Informe de páginas no preliminar");
 const at=Date.parse(r.collected_on+"T00:00:00Z");
 if(!Number.isFinite(at)||new Date(at).toISOString().slice(0,10)!==r.collected_on ||
    at>now+86400000||at<now-7*86400000)throw new RangeError("Fecha no válida");
 const keys=new Set(),rows=[];
 for(const e of r.evidence){
  if(!e||typeof e!=="object"||!QID.test(e.wikidata_id)||keys.has(e.wikidata_id)||
     typeof e.company!=="string"||e.company.length<4||e.company.length>130||
     !sources.has(e.identified_by)||!statuses.has(e.status)||
     !Number.isSafeInteger(e.readable_blocks)||e.readable_blocks<0||e.readable_blocks>450||
     e.source_identity_verified!==false||e.facts_verified!==0||
     e.rights_verified!==false||e.publication_authorized!==false)
    throw new RangeError("Sitio sin procedencia o con aprobación indebida");
  keys.add(e.wikidata_id);
  const site=validUrl(e.official_website_candidate);
  const resolved=validUrl(e.resolved_url,true);
  if(e.status==="candidate_unreachable"){
   if(resolved!==null||e.content_sha256!==null||e.readable_blocks!==0||
      e.short_excerpt!==null||!Array.isArray(e.document_link_candidates)||
      e.document_link_candidates.length!==0)throw new RangeError("Fallo remoto no puede certificar documento");
  }else{
   if(!resolved||typeof e.content_sha256!=="string"||!SHA.test(e.content_sha256)||
      (e.status==="candidate_page_readable")!==(e.readable_blocks>0))
      throw new RangeError("Página sin hash o lectura válida");
  }
  if(!Array.isArray(e.document_link_candidates)||e.document_link_candidates.length>4)
   throw new RangeError("Exceso de documentos");
  const docs=e.document_link_candidates.map(d=>{
   if(!d||d.document_fetched!==false||d.ownership_verified!==false)
    throw new RangeError("Documento no contrastado");
   return {url:validUrl(d.url),document_fetched:false,ownership_verified:false};
  });
  if(e.short_excerpt!==null&&(typeof e.short_excerpt!=="string"||e.short_excerpt.length>300))
   throw new RangeError("Extracto no acotado");
  rows.push([e.wikidata_id,e.company,site,e.identified_by,e.status,resolved,
    e.content_sha256,e.readable_blocks,JSON.stringify(docs),e.short_excerpt]);
 }
 if(r.readable!==r.evidence.filter(e=>e.status==="candidate_page_readable").length)
  throw new RangeError("Conteo de páginas legibles no coincide");
 return rows;
}
export async function storeOfficialEvidence(db,r){
 const rows=validateOfficialEvidence(r);
 const bytes=new TextEncoder().encode(JSON.stringify(r));
 const hash=[...new Uint8Array(await crypto.subtle.digest("SHA-256",bytes))]
   .map(v=>v.toString(16).padStart(2,"0")).join("");
 const id="official-"+hash.slice(0,24);
 const stmts=[db.prepare("INSERT OR IGNORE INTO market_official_source_runs(id,collected_on,provider,attempted,readable,facts_verified) VALUES (?,?,?,?,?,0)")
   .bind(id,r.collected_on,r.provider,r.attempted,r.readable),
   ...rows.map(e=>db.prepare(
     "INSERT OR IGNORE INTO market_official_source_items(run_id,wikidata_id,company,website_candidate,identified_by,status,resolved_url,content_sha256,readable_blocks,document_links_json,short_excerpt) VALUES (?,?,?,?,?,?,?,?,?,?,?)")
      .bind(id,...e))
 ];
 await db.batch(stmts);
 return {ok:true,stored_in:"d1",run_id:id,pages_attempted:rows.length,
   pages_readable:r.readable,primary_facts_verified:0,automatic_publication_allowed:false};
}
export async function readOfficialEvidence(db,url){
 const raw=url.searchParams.get("limit")??"20";
 if(!/^\d{1,2}$/.test(raw)||Number(raw)<1||Number(raw)>50)
  return {error:"Límite entre 1 y 50",status:400};
 try {
  const [runs,items]=await Promise.all([
   db.prepare("SELECT id,collected_on,attempted,readable,facts_verified FROM market_official_source_runs ORDER BY created_at DESC LIMIT 10").all(),
   db.prepare("SELECT wikidata_id,company,website_candidate,status,resolved_url,content_sha256,readable_blocks,document_links_json FROM market_official_source_items ORDER BY rowid DESC LIMIT ?").bind(Number(raw)).all()
  ]);
  return {ok:true,runs:runs.results||[],items:items.results||[],
   primary_facts_verified:0,automatic_publication_allowed:false,
   warning:"Una página corporativa accesible no certifica hechos, derechos ni resultados de mercado."};
 }catch(e){
  if(/no such table:\s*market_official_/i.test(String(e?.message||"")))
   return {error:"D1 requiere migración 0009_official_evidence.sql",status:503};
  throw e;
 }
}
