// Priorización para investigar; jamás aprueba hechos, guion, render o publicación.
const QID=/^Q[1-9][0-9]*$/,VIDEO=/^[A-Za-z0-9_-]{11}$/;
const CHANNEL=/^UC[A-Za-z0-9_-]{22}$/;
const METHOD='research_market_priority_v1';
function stamp(day){
 if(typeof day!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(day))throw new RangeError('Fecha inválida');
 const t=Date.parse(day+'T00:00:00Z');
 if(!Number.isFinite(t)||new Date(t).toISOString().slice(0,10)!==day)throw new RangeError('Fecha inexistente');
 return t;
}
const median=a=>{const s=[...a].sort((x,y)=>x-y),n=s.length;return n%2?s[n>>1]:(s[n/2-1]+s[n/2])/2;};
const number=n=>Number.isSafeInteger(n)&&n>=0&&n<=1e12;
const round=n=>Math.round(n*100)/100;
export function rankResearchMarket({entities=[],wiki=[],videos=[]},day){
 const now=stamp(day);
 if(entities.length>50||wiki.length>100||videos.length>1000)throw new RangeError('Presupuesto de ranking excedido');
 const rankings=[];
 for(const e of entities){
  if(!QID.test(e.wikidata_id)||typeof e.title!=='string'||e.title.length<3||e.title.length>130)
   throw new RangeError('Entidad de investigación inválida');
  const reasons=[],byVideo=new Map(),regions=new Map(),observed=new Set();
  const rows=videos.filter(v=>v.wikidata_id===e.wikidata_id);
  for(const v of rows){
   if(!['MX','ES'].includes(v.region)||!VIDEO.test(v.video_id)||!number(v.view_count))
    throw new RangeError('Observación YouTube inválida');
   const at=stamp(v.observed_on),published=stamp(v.published_on);
   if(at>now||now-at>7*864e5||published>at||at-published>90*864e5)continue;
   if(v.channel_id!==null&&v.channel_id!==undefined&&!CHANNEL.test(v.channel_id))
    throw new RangeError('Canal inválido');
   observed.add(v.observed_on);
   if(!regions.has(v.region))regions.set(v.region,new Set());
   regions.get(v.region).add(v.video_id);
   const old=byVideo.get(v.video_id);
   // El mismo video devuelto en MX y ES cuenta una sola vez. Si hay dos
   // capturas se conserva la más reciente, sin sumar sus visualizaciones.
   if(!old||v.observed_on>old.observed_on||
       v.observed_on===old.observed_on&&v.view_count>old.view_count)byVideo.set(v.video_id,v);
  }
  const samples=[...byVideo.values()];
  if(samples.length>20)throw new RangeError('Exceso de videos por empresa');
  const regionCount=[...regions.values()].filter(s=>s.size>=3).length;
  const channels=new Set(samples.map(v=>v.channel_id).filter(Boolean));
  if(regionCount<2)reasons.push('need_two_recent_youtube_region_samples');
  if(samples.length<3||channels.size<2)reasons.push('need_three_videos_and_two_channels');
  const windows=wiki.filter(w=>w.wikidata_id===e.wikidata_id&&
      stamp(w.observed_at)<=now&&now-stamp(w.observed_at)<=7*864e5)
      .sort((a,b)=>b.observed_at.localeCompare(a.observed_at));
  const w=windows[0];
  let growth=null;
  if(!w)reasons.push('need_recent_wikipedia_window');
  else{
   if(!number(w.views_last_7d)||!number(w.views_previous_7d)||
      stamp(w.period_end)-stamp(w.period_start)!==13*864e5||
      stamp(w.period_end)>=stamp(w.observed_at))throw new RangeError('Ventana independiente incoherente');
   growth=w.views_previous_7d?w.views_last_7d/w.views_previous_7d:null;
  }
  const velocity=samples.length?median(samples.map(v=>v.view_count/
     Math.max(1,(stamp(v.observed_on)-stamp(v.published_on))/864e5))):null;
  const components=reasons.length?null:{
   youtube_sample_velocity:round(Math.min(100,20*Math.log10(1+velocity))),
   wikipedia_momentum:round(growth===null?50:Math.max(0,Math.min(100,50+25*Math.log2(Math.max(.01,growth))))),
   observed_channel_diversity:Math.min(100,channels.size*10)
  };
  const score=components?round(.6*components.youtube_sample_velocity+
    .3*components.wikipedia_momentum+.1*components.observed_channel_diversity):null;
  rankings.push({wikidata_id:e.wikidata_id,title:e.title,eligible_for_research:!reasons.length,
    market_score:score,reasons,score_components:components,
    youtube_unique_videos:samples.length,youtube_distinct_channels:channels.size,
    youtube_region_samples:regionCount,youtube_observed_days:[...observed].sort(),
    youtube_run_ids:[...new Set(rows.map(v=>v.source_run_id).filter(Boolean))].sort(),
    sampled_video_ids:[...byVideo.keys()].sort(),
    median_daily_views:velocity===null?null:round(velocity),
    wikipedia_growth: growth===null?null:round(growth),
    wikipedia_observed_on:w?.observed_at??null,
    source_discovery_required:true,verified_claims:0,script_authorized:false,
    publication_authorized:false});
 }
 rankings.sort((a,b)=>Number(b.eligible_for_research)-Number(a.eligible_for_research)||
   (b.market_score??-1)-(a.market_score??-1)||a.wikidata_id.localeCompare(b.wikidata_id));
 return {method:METHOD,observed_on:day,rankings,
   qualified_count:rankings.filter(r=>r.eligible_for_research).length,
   proposed_wikidata_id:rankings.find(r=>r.eligible_for_research)?.wikidata_id??null,
   publication_authorized:false,
   warning:'Prioridad heurística entre las empresas muestreadas. MX/ES son parámetros de búsqueda, no geografía de las vistas. No acredita hechos ni predice audiencia.'};
}

export async function selectResearchFromD1(db,now=new Date()){
 const day=now.toISOString().slice(0,10),old=new Date(now.getTime()-7*864e5).toISOString().slice(0,10);
 const [entities,wiki,videos]=await Promise.all([
  db.prepare('SELECT wikidata_id,title FROM market_entities ORDER BY last_seen DESC,wikidata_id LIMIT 50').all(),
  db.prepare('SELECT wikidata_id,observed_at,period_start,period_end,views_last_7d,views_previous_7d FROM market_interest_windows i WHERE observed_at>=? AND rowid=(SELECT i2.rowid FROM market_interest_windows i2 WHERE i2.wikidata_id=i.wikidata_id ORDER BY observed_at DESC,rowid DESC LIMIT 1) LIMIT 100').bind(old).all(),
  db.prepare("SELECT q.wikidata_id,q.region,q.observed_on,q.run_id AS source_run_id,v.video_id,v.published_on,v.view_count,v.channel_id FROM market_youtube_queries q JOIN market_youtube_videos v ON v.run_id=q.run_id AND v.wikidata_id=q.wikidata_id AND v.region=q.region WHERE q.evidence_state='observed_sample' AND q.observed_on>=? AND q.run_id=(SELECT q2.run_id FROM market_youtube_queries q2 WHERE q2.wikidata_id=q.wikidata_id AND q2.region=q.region AND q2.evidence_state='observed_sample' ORDER BY observed_on DESC,rowid DESC LIMIT 1) ORDER BY q.wikidata_id,q.region,v.video_id LIMIT 1000").bind(old).all()
 ]);
 const snapshot=rankResearchMarket({entities:entities.results||[],wiki:wiki.results||[],videos:videos.results||[]},day);
 const bytes=new TextEncoder().encode(JSON.stringify(snapshot));
 const digest=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(x=>x.toString(16).padStart(2,'0')).join('');
 const id='selection-'+digest.slice(0,28),chosen=snapshot.rankings.find(x=>x.eligible_for_research);
 const writes=[db.prepare('INSERT OR IGNORE INTO market_research_selection_runs(id,observed_on,method,candidate_count,qualified_count,ranked_snapshot_json) VALUES (?,?,?,?,?,?)')
    .bind(id,day,METHOD,snapshot.rankings.length,snapshot.qualified_count,JSON.stringify(snapshot))];
 if(chosen)writes.push(db.prepare("INSERT OR IGNORE INTO market_research_queue(id,wikidata_id,title,selection_run_id,market_score) SELECT ?,?,?,?,? WHERE NOT EXISTS (SELECT 1 FROM market_research_queue WHERE state IN ('awaiting_sources','researching','review')) AND NOT EXISTS (SELECT 1 FROM market_research_queue WHERE wikidata_id=? AND created_at>=datetime('now','-90 days'))")
    .bind('rq-'+digest.slice(0,28),chosen.wikidata_id,chosen.title,id,chosen.market_score,chosen.wikidata_id));
 await db.batch(writes);
 const queue=await db.prepare("SELECT id,wikidata_id,title,state,market_score,selection_run_id FROM market_research_queue WHERE state IN ('awaiting_sources','researching','review') ORDER BY created_at LIMIT 1").first();
 // Si la última investigación sólo encontró una fuente, usar el histórico D1
 // para NO gastar en las mismas cuatro páginas. El histórico está protegido
 // por el contrato original de report_json y se limita a siete días.
 let prior_attempted_urls=[],prior_evidence_manifest=[];
 if(queue?.state==='awaiting_sources'){
  const previous=await db.prepare(
   "SELECT report_json FROM market_ai_pipeline_runs WHERE wikidata_id=? AND collected_on>=? ORDER BY created_at DESC,rowid DESC LIMIT 1"
  ).bind(queue.wikidata_id,old).first();
  if(previous){
   const record=JSON.parse(previous.report_json);
   if(record.selected_wikidata_id===queue.wikidata_id){
    const attempted=record.retrieval_budget?.attempted_urls||
      (record.source_documents||[]).map(v=>v.url);
    prior_attempted_urls=attempted
      .filter(v=>typeof v==='string'&&v.startsWith('https://')).slice(0,8);
    prior_evidence_manifest=(record.evidence_manifest||[])
      .filter(v=>v.wikidata_id===queue.wikidata_id&&
        typeof v.url==='string'&&v.url.startsWith('https://')&&
        typeof v.excerpt==='string'&&v.excerpt.length>=90&&
        typeof v.document_sha256==='string'&&/^[0-9a-f]{64}$/.test(v.document_sha256))
      .slice(0,4);
   }
  }
 }
 return {ok:true,stored_in:'d1',run_id:id,...snapshot,
   selected_wikidata_id:queue?.wikidata_id??null,research_queue:queue??null,
   prior_attempted_urls,prior_evidence_manifest,
   automatic_publication_allowed:false,script_authorized:false};
}

export async function readResearchQueue(db){
 try{
  const [runs,queue]=await Promise.all([
   db.prepare('SELECT id,observed_on,ranked_snapshot_json FROM market_research_selection_runs ORDER BY created_at DESC,rowid DESC LIMIT 1').all(),
   db.prepare('SELECT id,wikidata_id,title,state,market_score,selection_run_id,created_at FROM market_research_queue ORDER BY created_at DESC LIMIT 20').all()
  ]);
  return {ok:true,latest_selection:runs.results?.[0]?JSON.parse(runs.results[0].ranked_snapshot_json):null,
    queue:queue.results||[],automatic_publication_allowed:false};
 }catch(e){
  if(/no such table:\s*market_research_(selection|queue)/i.test(String(e?.message||'')))
    return {error:'Falta migración 0012_market_research_queue.sql',status:503};
  throw e;
 }
}
