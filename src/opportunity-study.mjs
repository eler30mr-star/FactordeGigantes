// YouTube-first market study: observable comparisons, no factual investigation.
// Scoring v2 is deliberately conservative and returns no winner on weak evidence.
const DAY=86400000,VIDEO=/^[A-Za-z0-9_-]{11}$/,CHANNEL=/^UC[A-Za-z0-9_-]{22}$/;
const median=values=>{const a=[...values].sort((x,y)=>x-y);return a.length%2?a[a.length>>1]:(a[a.length/2-1]+a[a.length/2])/2;};
const norm=s=>s.normalize('NFKD').replace(/\p{M}/gu,'').toLowerCase();
const stamp=s=>{if(typeof s!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(s))throw new RangeError('Fecha de muestra inválida');const t=Date.parse(s+'T00:00:00Z');if(!Number.isFinite(t)||new Date(t).toISOString().slice(0,10)!==s)throw new RangeError('Fecha inválida');return t;};
const text=(s,min,max)=>typeof s==='string'&&s.trim().length>=min&&s.length<=max&&!/[\x00-\x1f<>]/.test(s);
function video(v,observed){
 if(!v||!VIDEO.test(v.id)||!CHANNEL.test(v.channel_id)||!text(v.title,3,200)||
  !Number.isSafeInteger(v.views)||v.views<0||v.views>1e12||!Number.isSafeInteger(v.duration_seconds)||v.duration_seconds<1||v.duration_seconds>86400)
  throw new RangeError('Métrica YouTube inválida');
 const age=(observed-stamp(v.published_on))/DAY;if(age<0)throw new RangeError('Video publicado en el futuro');
 return {...v,age,average_daily_views:v.views/Math.max(1,age)};
}
export function assessOpportunityStudy(r,now=new Date(),history=[]){
 if(!r||r.schema!=='fdg_youtube_opportunity_study_v2'||r.source!=='youtube_data_api_v3'||
  !Array.isArray(r.queries)||r.queries.length<2||r.queries.length>7||!Array.isArray(r.videos)||r.videos.length>100||
  !Array.isArray(r.baselines)||r.baselines.length>12||!Array.isArray(r.candidates)||r.candidates.length>4||
  !text(r.extraction_provider,3,50))throw new RangeError('Estudio fuera del contrato');
 const observed=stamp(r.observed_on),today=stamp(now.toISOString().slice(0,10));
 if(observed>today||today-observed>DAY)throw new RangeError('Estudio caducado');
 const videos=new Map();for(const v of r.videos){if(videos.has(v.id))throw new RangeError('Videos duplicados');videos.set(v.id,video(v,observed));}
 const queryIds=new Set();
 for(const q of r.queries){if(!text(q.query,4,150)||queryIds.has(norm(q.query))||!Array.isArray(q.video_ids)||q.video_ids.length>30||
  new Set(q.video_ids).size!==q.video_ids.length||q.video_ids.some(id=>!videos.has(id)))throw new RangeError('Consulta sin evidencia');queryIds.add(norm(q.query));}
 if([...videos.keys()].some(id=>!r.queries.some(q=>q.video_ids.includes(id))))throw new RangeError('Video sin consulta de origen');
 const observedRows=[...videos.values()].filter(v=>v.duration_seconds>=300&&v.duration_seconds<=1800&&v.age>=2&&v.age<=90);
 const sampleSummary={observed_videos:videos.size,comparable_long_videos:observedRows.length,
  distinct_channels:new Set(observedRows.map(v=>v.channel_id)).size,recent_examples:observedRows.filter(v=>v.age<=30).length};
 const minimumSampleReasons=[];
 if(sampleSummary.comparable_long_videos<4)minimumSampleReasons.push('need_four_comparable_long_videos');
 if(sampleSummary.distinct_channels<3)minimumSampleReasons.push('need_three_observed_channels');
 if(sampleSummary.recent_examples<2)minimumSampleReasons.push('need_two_recent_examples');
 const baseline=new Map();for(const b of r.baselines){
  if(!CHANNEL.test(b.channel_id)||baseline.has(b.channel_id)||!Array.isArray(b.videos)||b.videos.length>10)throw new RangeError('Comparación de canal inválida');
  const seen=new Set(),rows=[];
  for(const v of b.videos){if(v.channel_id!==b.channel_id||seen.has(v.id))throw new RangeError('Videos de base duplicados o ajenos');seen.add(v.id);rows.push(video(v,observed));}
  baseline.set(b.channel_id,rows);
 }
 const companies=new Set(),rankings=[];
 const recent=new Set(history.map(x=>norm(x)));
 for(const c of r.candidates){
  if(!text(c.company,2,100)||!text(c.topic,5,300)||!text(c.rationale,15,600)||!text(c.niche_reason,15,400)||
   companies.has(norm(c.company))||!Array.isArray(c.video_ids)||c.video_ids.length>20||new Set(c.video_ids).size!==c.video_ids.length||
   c.video_ids.some(id=>!videos.has(id)))throw new RangeError('Candidato inválido');
  companies.add(norm(c.company));
  const rows=c.video_ids.map(id=>videos.get(id)),reasons=[],ratios=[],channels=new Set(),seenQueries=new Set();
  const chosenIds=new Set(c.video_ids);
  let longVideos=0,recentVideos=0;
  for(const v of rows){
   // The company must be visible in the observed title, not invented by the LLM.
   const words=norm(v.title).replace(/[^\p{L}\p{N}]+/gu,' '),name=norm(c.company).replace(/[^\p{L}\p{N}]+/gu,' ').trim();
   if(!(' '+words+' ').includes(' '+name+' '))continue;
   if(v.duration_seconds<300||v.duration_seconds>1800||v.age<2||v.age>90)continue;
   longVideos++;if(v.age<=30)recentVideos++;
   for(const q of r.queries)if(q.video_ids.includes(v.id))seenQueries.add(norm(q.query));
   const comparable=(baseline.get(v.channel_id)||[]).filter(b=>!chosenIds.has(b.id)&&b.duration_seconds>=300&&b.duration_seconds<=1800&&
    b.age>=2&&b.age<=90&&b.duration_seconds/v.duration_seconds>=.5&&b.duration_seconds/v.duration_seconds<=2&&Math.max(1,b.age)/Math.max(1,v.age)>=1/3&&Math.max(1,b.age)/Math.max(1,v.age)<=3);
   if(comparable.length<3)continue;
   const normal=median(comparable.map(b=>b.average_daily_views));
   if(normal<=0)continue;
   channels.add(v.channel_id);ratios.push(Math.min(10,v.average_daily_views/normal));
  }
  if(rows.length<4||longVideos<4)reasons.push('need_four_comparable_long_videos');
  if(channels.size<3||ratios.length<4)reasons.push('need_three_channels_with_three_baselines_each');
  if(seenQueries.size<2)reasons.push('need_independent_search_queries');
  if(recentVideos<2)reasons.push('need_two_recent_examples');
  if(recent.has(norm(c.company)))reasons.push('company_recently_covered');
  const relative=ratios.length?median(ratios):null;
  if(relative===null||relative<1.3)reasons.push('no_consistent_relative_outperformance');
  // No extrapolated CTR/retention, inferred trend or global demand here.
  const score=reasons.length?null:Math.round(100*(.65*Math.min(relative/3,1)+.2*Math.min(channels.size/5,1)+.15*Math.min(recentVideos/4,1))*100)/100;
  rankings.push({company:c.company,topic:c.topic,rationale:c.rationale,niche_reason:c.niche_reason,eligible:reasons.length===0,
   score,reasons,video_ids:c.video_ids,comparable_videos:longVideos,baseline_channels:channels.size,
   median_relative_average_views:relative===null?null:Math.round(relative*100)/100,
   sample_competition_videos:longVideos,recent_examples:recentVideos});
 }
 rankings.sort((a,b)=>(b.score??-1)-(a.score??-1)||a.company.localeCompare(b.company));
 const qualified=rankings.filter(x=>x.eligible);
 // A winner requires a genuine comparison, not a sole measurable candidate.
 const selected=qualified.length>=2?qualified[0]:null;
 return {method:'youtube_comparative_opportunity_v2',observed_on:r.observed_on,rankings,
  sample_summary:sampleSummary,minimum_sample_reasons:minimumSampleReasons,
  selected,reason:selected?'comparative_selection':'insufficient_comparative_evidence',
  limitations:['Muestra de búsquedas, no demanda total','Promedio de visitas por edad, no crecimiento medido',
   'Comparación con hasta diez videos del mismo canal','No incluye CTR ni retención de terceros','Las regiones de búsqueda no identifican el país de los espectadores',
   'Ponderaciones iniciales requieren calibración con estudios reales'],publication_authorized:false};
}
