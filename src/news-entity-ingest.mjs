// Candidatas corporativas Wikidata a partir de titulares reales RSS.
// Nunca confirma el artículo original, hechos, derechos ni demanda YouTube.
const QID=/^Q[1-9][0-9]*$/, NEWS=/^news-[a-f0-9]{32}$/, DAY=/^\d{4}-\d{2}-\d{2}$/;
const canon=s=>s.normalize("NFKD").toLowerCase().replace(/[\u0300-\u036f]/g,"")
  .replace(/[^a-z0-9]+/g," ").trim();
function date(s){
 if(typeof s!=="string"||!DAY.test(s))throw new RangeError("Día no válido");
 const t=Date.parse(s+"T00:00:00Z");
 if(!Number.isFinite(t)||new Date(t).toISOString().slice(0,10)!==s)
  throw new RangeError("Día inexistente");
 return t;
}
function https(s,{hosts=null,mandatory=true}={}){
 if((s===null||s===undefined)&&!mandatory)return null;
 if(typeof s!=="string"||s.length>1300)throw new RangeError("Fuente inválida");
 const u=new URL(s);
 if(u.protocol!=="https:"||!u.hostname||u.username||u.password||u.port||u.hash||
    (hosts&&!hosts.includes(u.hostname)))throw new RangeError("Fuente HTTPS inválida");
 return u.href;
}
export function validateNewsEntities(report,now=Date.now()){
 const r=report;
 if(!r||typeof r!=="object"||r.provider!=="wikidata_news_company_resolution_v1"||
    r.market_study_complete!==false||r.ready_for_script!==false||r.ready_for_youtube!==false||
    !Number.isSafeInteger(r.headlines_examined)||r.headlines_examined<0||r.headlines_examined>8||
    !Number.isSafeInteger(r.wikidata_searches)||r.wikidata_searches<0||r.wikidata_searches>16||
    !Number.isSafeInteger(r.lookup_errors)||r.lookup_errors<0||r.lookup_errors>17||
    r.wikidata_requests_max!==17||!Array.isArray(r.candidates)||r.candidates.length>16||
    r.candidate_count!==r.candidates.length)throw new RangeError("Informe de entidades no válido");
 const observed=date(r.collected_on);
 if(observed>now+86400000||observed<now-7*86400000)throw new RangeError("Informe caducado");
 const keys=new Set(),rows=[];
 for(const c of r.candidates){
  if(!c||typeof c!=="object"||!QID.test(c.wikidata_id)||!NEWS.test(c.news_id)||
     typeof c.matched_name!=="string"||c.matched_name.trim().length<4||c.matched_name.length>130||
     typeof c.article_headline!=="string"||c.article_headline.length<12||c.article_headline.length>280||
     typeof c.source_label!=="string"||c.source_label.length<2||c.source_label.length>120||
     c.evidence_method!=="wikidata_p31_and_exact_label_in_headline_v1"||
     c.identity_verified_in_article!==false||c.primary_source_verified!==false||
     c.youtube_market_verified!==false||c.editorial_authorized!==false)
   throw new RangeError("Candidata sin evidencia corporativa");
  const name=canon(c.matched_name),headline=canon(c.article_headline);
  if(!name||!(" "+headline+" ").includes(" "+name+" "))throw new RangeError("Nombre no mencionado");
  const source=https(c.news_url,{hosts:["news.google.com"]});
  const entity=https(c.wikidata_url,{hosts:["www.wikidata.org"]});
  if(entity!=="https://www.wikidata.org/wiki/"+c.wikidata_id)
   throw new RangeError("ID Wikidata no corresponde");
  const official=https(c.official_website_candidate,{mandatory:false});
  const key=c.news_id+"|"+c.wikidata_id;
  if(keys.has(key))throw new RangeError("Entidad duplicada");
  keys.add(key);
  rows.push([c.news_id,c.wikidata_id,c.matched_name,c.article_headline,source,
     c.source_label,entity,official,c.evidence_method,r.collected_on]);
 }
 return rows;
}
export async function storeNewsEntities(db,r){
 const rows=validateNewsEntities(r);
 const bytes=new TextEncoder().encode(JSON.stringify(r));
 const hash=[...new Uint8Array(await crypto.subtle.digest("SHA-256",bytes))]
   .map(v=>v.toString(16).padStart(2,"0")).join("");
 const id="wdnews-"+hash.slice(0,24);
 const stmts=[db.prepare(
   "INSERT OR IGNORE INTO market_news_entity_runs(id,collected_on,provider,headlines_examined,wikidata_searches,lookup_errors,candidate_count) VALUES (?,?,?,?,?,?,?)")
   .bind(id,r.collected_on,r.provider,r.headlines_examined,r.wikidata_searches,r.lookup_errors,rows.length),
   ...rows.map(c=>db.prepare(
    "INSERT INTO market_news_entity_candidates(news_id,wikidata_id,matched_name,article_headline,news_url,source_label,wikidata_url,official_website_candidate,evidence_method,first_run_id,latest_run_id,last_seen_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?) "+
    "ON CONFLICT(news_id,wikidata_id) DO UPDATE SET latest_run_id=excluded.latest_run_id,last_seen_at=MAX(last_seen_at,excluded.last_seen_at)")
    .bind(...c.slice(0,9),id,id,c[9]))
 ];
 await db.batch(stmts);
 return {ok:true,stored_in:"d1",run_id:id,candidates_seen:rows.length,
   primary_sources_verified:false,automatic_publication_allowed:false};
}
