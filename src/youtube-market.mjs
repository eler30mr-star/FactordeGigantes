// Evidencia pública YouTube Data API v3, limitada a dos empresas x dos regiones.
// Sin publicación, sin selección de guion y sin confiar en medianas recibidas.
const QID=/^Q[1-9][0-9]*$/;
const VIDEO=/^[A-Za-z0-9_-]{11}$/;
const CHANNEL=/^UC[A-Za-z0-9_-]{22}$/;
const DAY=/^\d{4}-\d{2}-\d{2}$/;
const regions=new Set(["MX","ES"]);
function dateStamp(s) {
 if(typeof s!=="string"||!DAY.test(s))throw new RangeError("Fecha YouTube inválida");
 const t=Date.parse(s+"T00:00:00Z");
 if(!Number.isFinite(t)||new Date(t).toISOString().slice(0,10)!==s)throw new RangeError("Día inexistente");
 return t;
}
function number(n,lo,hi){return Number.isSafeInteger(n)&&n>=lo&&n<=hi;}
function median(values){
 const a=[...values].sort((x,y)=>x-y);const m=Math.floor(a.length/2);
 return a.length%2?a[m]:(a[m-1]+a[m])/2;
}
export function validateYoutubeStudy(r,now=Date.now()){
 if(!r||typeof r!=="object"||r.provider!=="youtube_data_api_v3"||
    !["partial","measured"].includes(r.state) ||r.market_study_complete!==false||
    r.ready_for_youtube!==false||r.ready_for_script!==false||
    r.research_automatic!==false||r.automatic_publication_allowed!==false)
    throw new RangeError("Reporte YouTube sin garantías de revisión");
 const collected=dateStamp(r.collected_on);
 if(collected>now+86400000 || collected<now-7*86400000)throw new RangeError("Reporte caduco");
 if(!number(r.candidate_count,1,2)||r.region_count!==2||
    !number(r.queries_attempted,1,4)||r.quota_units_max!==101*r.queries_attempted||
    !Array.isArray(r.queries)||r.queries.length!==r.queries_attempted)
    throw new RangeError("Presupuesto API inconsistente");
 const pairs=new Set(),topics=new Map(),queries=[],videos=[];
 for(const q of r.queries){
   if(!q||typeof q!=="object"||typeof q.wikidata_id!=="string"||!QID.test(q.wikidata_id)||
      typeof q.topic!=="string"||q.topic.trim().length<4||q.topic.length>130||
      !regions.has(q.region)||q.observed_on!==r.collected_on||
      !["observed_sample","insufficient_sample"].includes(q.evidence_state)||
      !number(q.sample_size,0,10)||!number(q.uploads_sampled,0,10)||
      !number(q.distinct_channels,0,10)||!Array.isArray(q.videos))
      throw new RangeError("Muestra de YouTube malformada");
   const pair=q.wikidata_id+"|"+q.region;
   if(pairs.has(pair))throw new RangeError("Pareja repetida");
   pairs.add(pair);
   if(topics.has(q.wikidata_id)&&topics.get(q.wikidata_id)!==q.topic)
     throw new RangeError("Nombre de empresa inconsistente");
   topics.set(q.wikidata_id,q.topic);
   const channels=new Set(),ids=new Set(),rates=[];
   if(q.evidence_state==="insufficient_sample"){
     if(q.sample_size!==0||q.uploads_sampled!==0||q.distinct_channels!==0||
        q.median_daily_views!==null||q.videos.length!==0)
        throw new RangeError("Muestras faltantes se representan sin valores");
   }else {
     if(q.videos.length!==q.sample_size || q.sample_size<3 ||
        q.uploads_sampled<q.sample_size)throw new RangeError("Insuficiente evidencia");
     for(const v of q.videos){
       if(!v||typeof v!=="object"||!VIDEO.test(v.video_id)||ids.has(v.video_id)||
          v.url!=="https://www.youtube.com/watch?v="+v.video_id||
          !number(v.view_count,0,1000000000000))
          throw new RangeError("Estadística pública inválida");
       const published=dateStamp(v.published_at);
       const age=Math.floor((collected-published)/86400000);
       if(age<0||age>90)throw new RangeError("Fecha de video fuera de muestra");
       if(v.channel_id!==null && v.channel_id!==undefined &&
          (typeof v.channel_id!=="string"||!CHANNEL.test(v.channel_id)))
          throw new RangeError("Canal YouTube inválido");
       if(v.channel_id)channels.add(v.channel_id);
       ids.add(v.video_id);
       rates.push(v.view_count/Math.max(1,age));
       videos.push([q.wikidata_id,q.region,v.video_id,v.published_at,v.view_count,
         v.channel_id||null,v.url]);
     }
     const med=Math.round(median(rates)*100)/100;
     if(typeof q.median_daily_views!=="number"||Math.abs(q.median_daily_views-med)>0.011||
        q.distinct_channels!==channels.size)
       throw new RangeError("Comparación o cantidad de canales no coincide con la evidencia");
   }
   queries.push([q.wikidata_id,q.topic,q.region,q.observed_on,q.sample_size,
     q.uploads_sampled,q.median_daily_views,q.distinct_channels,q.evidence_state]);
 }
 if(topics.size<1 || topics.size>r.candidate_count ||
    r.complete_comparisons!==queries.filter(q=>q[8]==="observed_sample").length ||
    (r.state==="measured")!==(r.complete_comparisons===r.queries_attempted &&
        r.queries_attempted===r.candidate_count*2))
    throw new RangeError("Resumen de muestras inconsistente");
 return {queries,videos};
}
export async function persistYoutubeStudy(db,r){
 const {queries,videos}=validateYoutubeStudy(r);
 const hashData=new TextEncoder().encode(JSON.stringify(r));
 const hash=[...new Uint8Array(await crypto.subtle.digest("SHA-256",hashData))]
  .map(x=>x.toString(16).padStart(2,"0")).join("");
 const id="ytrun-"+hash.slice(0,28);
 const stmts=[
  db.prepare("INSERT OR IGNORE INTO market_youtube_runs(id,collected_on,provider,region_count,candidate_count,queries_attempted,quota_units_max,state) VALUES (?,?,?,?,?,?,?,?)")
   .bind(id,r.collected_on,"youtube_data_api_v3",r.region_count,r.candidate_count,r.queries_attempted,r.quota_units_max,r.state),
  ...queries.map(q=>db.prepare(
    "INSERT OR IGNORE INTO market_youtube_queries(run_id,wikidata_id,topic,region,observed_on,sample_size,uploads_sampled,median_daily_views,distinct_channels,evidence_state) VALUES (?,?,?,?,?,?,?,?,?,?)")
    .bind(id,...q)),
  ...videos.map(v=>db.prepare(
    "INSERT OR IGNORE INTO market_youtube_videos(run_id,wikidata_id,region,video_id,published_on,view_count,channel_id,video_url) VALUES (?,?,?,?,?,?,?,?)")
    .bind(id,...v))
 ];
 await db.batch(stmts);
 return {ok:true,stored_in:"d1",run_id:id,queries_seen:queries.length,
   video_observations:videos.length,market_study_complete:false,
   automatic_publication_allowed:false};
}
export async function readYoutubeMarket(db,url){
 const raw=url.searchParams.get("limit")??"20";
 if(!/^\d{1,2}$/.test(raw)||Number(raw)<1||Number(raw)>50)
  return {error:"Límite entre 1 y 50",status:400};
 try{
  const [runs,queries]=await Promise.all([
    db.prepare("SELECT id,collected_on,queries_attempted,quota_units_max,state FROM market_youtube_runs ORDER BY created_at DESC LIMIT ?").bind(Number(raw)).all(),
    db.prepare("SELECT run_id,wikidata_id,topic,region,observed_on,sample_size,uploads_sampled,median_daily_views,distinct_channels,evidence_state FROM market_youtube_queries ORDER BY observed_on DESC,topic,region LIMIT ?").bind(Number(raw)).all()
  ]);
  return {ok:true,runs:runs.results||[],queries:queries.results||[],
    market_study_complete:false,automatic_publication_allowed:false,
    warning:"Muestra de videos públicos, no universo competitivo ni CTR/retención. Fuentes primarias y verificación editorial pendientes."};
 }catch(e){
  if(/no such table:\s*market_youtube_/i.test(String(e?.message||"")))
   return {error:"D1 requiere migración 0006_youtube_observations.sql",status:503};
  throw e;
 }
}
