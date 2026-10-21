// Evaluador del mercado: las decisiones se calculan dentro del Worker sobre D1.
// Cero selección/guion/publicación mientras faltan YouTube y fuentes primarias.
const QID=/^Q[1-9][0-9]*$/;
const SCORING_VERSION="market_evidence_gate_v1";
function nonneg(n){return Number.isSafeInteger(n)&&n>=0;}
export function evaluateMarketEvidence({wiki=[],news=[],youtube=[]},assessmentDay){
 if(!/^\d{4}-\d{2}-\d{2}$/.test(assessmentDay))throw new RangeError("Día inválido");
 const all=new Map();
 for(const row of wiki){
  if(!QID.test(row.wikidata_id)||typeof row.title!=="string")throw new RangeError("Wikidata inválida");
  all.set(row.wikidata_id,{wikidata_id:row.wikidata_id,title:row.title,
   wiki_observation_count:row.wikipedia_windows||0,news_mention_count:0,youtube_region_samples:0});
 }
 for(const row of news){
  if(!QID.test(row.wikidata_id)||typeof row.title!=="string")throw new RangeError("Entidad de titular inválida");
  const entry=all.get(row.wikidata_id)||{wikidata_id:row.wikidata_id,title:row.title,
    wiki_observation_count:0,news_mention_count:0,youtube_region_samples:0};
  entry.news_mention_count=row.mentions||0;
  all.set(row.wikidata_id,entry);
 }
 for(const row of youtube){
  const entry=all.get(row.wikidata_id);
  if(entry)entry.youtube_region_samples=row.regions||0;
 }
 if(all.size>50)throw new RangeError("Demasiadas empresas");
 const result=[];
 for(const item of all.values()){
  if(!nonneg(item.wiki_observation_count)||!nonneg(item.news_mention_count)||
     !nonneg(item.youtube_region_samples)||item.youtube_region_samples>2)
     throw new RangeError("Señales de mercado incoherentes");
  const hasYoutube=item.youtube_region_samples>=2;
  // Sin fuente primaria confirmada por investigadores NO autorizar selección.
  const verifiedPrimary=0;
  const status=(!hasYoutube&&!verifiedPrimary)?"awaiting_youtube_and_primary":
    !hasYoutube?"awaiting_youtube":"awaiting_primary";
  const reasons=[];
  if(!hasYoutube)reasons.push("Sin muestras oficiales suficientes de YouTube en dos regiones hispanohablantes");
  if(!verifiedPrimary)reasons.push("Sin fuente primaria contrastada para afirmar los hechos");
  if(!item.wiki_observation_count&&!item.news_mention_count)
   reasons.push("Sin otra señal de mercado independiente y fechada");
  const title=item.title.trim().slice(0,130);
  if(!title)throw new RangeError("Empresa sin título");
  result.push({...item,title,primary_sources_verified:verifiedPrimary,
   readiness:status,reasons,
   // Orden de atención documental, no puntuación de demanda ni "ganador".
   exploration_priority:Math.min(100,item.news_mention_count*10+
       Math.min(30,item.wiki_observation_count*5)+item.youtube_region_samples*12),
   qualified_for_research:false,publication_authorized:false});
 }
 result.sort((a,b)=>b.exploration_priority-a.exploration_priority||
   a.wikidata_id.localeCompare(b.wikidata_id));
 return {method:SCORING_VERSION,assessment_day:assessmentDay,
   candidates_evaluated:result.length,qualified_count:0,selected_wikidata_id:null,
   candidates:result,market_study_complete:false,
   automatic_publication_allowed:false};
}
export async function assessMarketFromD1(db,now=new Date()){
 const day=now.toISOString().slice(0,10);
 // Cada fuente pertenece a una tabla histórica distinta. COALESCE/COUNT respeta observaciones reales.
 const [w,n,y]=await Promise.all([
  db.prepare("SELECT e.wikidata_id,e.title,COUNT(DISTINCT i.observed_at||'|'||i.source_url) AS wikipedia_windows FROM market_entities e LEFT JOIN market_interest_windows i ON i.wikidata_id=e.wikidata_id GROUP BY e.wikidata_id,e.title ORDER BY e.last_seen DESC LIMIT 50").all(),
  db.prepare("SELECT c.wikidata_id,MIN(c.matched_name) AS title,COUNT(DISTINCT c.news_id) AS mentions FROM market_news_entity_candidates c GROUP BY c.wikidata_id ORDER BY mentions DESC LIMIT 50").all(),
  db.prepare("SELECT wikidata_id,COUNT(DISTINCT region) AS regions FROM market_youtube_queries WHERE evidence_state='observed_sample' AND observed_on >= date('now','-7 day') GROUP BY wikidata_id").all()
 ]);
 const report=evaluateMarketEvidence({wiki:w.results||[],news:n.results||[],youtube:y.results||[]},day);
 // Dedupe por día + tabla de evidencia, sin sobrescribir revisiones editoriales.
 const key=new TextEncoder().encode(JSON.stringify(report));
 const sha=[...new Uint8Array(await crypto.subtle.digest("SHA-256",key))]
   .map(b=>b.toString(16).padStart(2,"0")).join("");
 const id="assess-"+sha.slice(0,28);
 const stmts=[db.prepare(
   "INSERT OR IGNORE INTO market_assessment_runs(id,assessment_day,method,candidates_evaluated,qualified_count,selected_wikidata_id) VALUES (?,?,?,?,0,NULL)"
  ).bind(id,day,SCORING_VERSION,report.candidates_evaluated),
  ...report.candidates.map(row=>db.prepare(
    "INSERT OR IGNORE INTO market_assessments(run_id,wikidata_id,title,wiki_observation_count,news_mention_count,youtube_region_samples,primary_sources_verified,readiness,reasons_json,research_authorized,publication_authorized) VALUES (?,?,?,?,?,?,0,?,?,0,0)"
   ).bind(id,row.wikidata_id,row.title,row.wiki_observation_count,row.news_mention_count,
     row.youtube_region_samples,row.readiness,JSON.stringify(row.reasons)))
 ];
 await db.batch(stmts);
 return {ok:true,stored_in:"d1",run_id:id,...report};
}
export async function readMarketAssessments(db,url){
 const raw=url.searchParams.get("limit")??"25";
 if(!/^\d{1,2}$/.test(raw)||Number(raw)<1||Number(raw)>50)
  return {error:"Límite entre 1 y 50",status:400};
 try{
  const [runs,rows]=await Promise.all([
    db.prepare("SELECT id,assessment_day,candidates_evaluated,qualified_count,selected_wikidata_id FROM market_assessment_runs ORDER BY created_at DESC LIMIT 10").all(),
    db.prepare("SELECT a.run_id,a.wikidata_id,a.title,a.wiki_observation_count,a.news_mention_count,a.youtube_region_samples,a.primary_sources_verified,a.readiness,a.reasons_json FROM market_assessments a JOIN market_assessment_runs r ON r.id=a.run_id WHERE r.id=(SELECT id FROM market_assessment_runs ORDER BY created_at DESC LIMIT 1) ORDER BY a.news_mention_count DESC,a.wiki_observation_count DESC LIMIT ?").bind(Number(raw)).all()
  ]);
  return {ok:true,runs:runs.results||[],candidates:rows.results||[],
   selected_for_research:null,market_study_complete:false,
   automatic_publication_allowed:false,
   warning:"La clasificación evidencia bloqueos y no autoriza investigación o publicación sin fuentes primarias y datos YouTube."};
 }catch(e){
  if(/no such table:\s*market_assessments?/i.test(String(e?.message||"")))
   return {error:"Falta migración 0008_news_entities_assessments.sql",status:503};
  throw e;
 }
}
