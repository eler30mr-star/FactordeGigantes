// Coincidencias de texto, nunca fuentes verificadas ni audiencia YouTube.
const QID=/^Q[1-9][0-9]*$/,NEWS=/^news-[a-f0-9]{32}$/;
const ISO=/^\d{4}-\d{2}-\d{2}$/;
function day(s){
 if(typeof s!=="string"||!ISO.test(s))throw new RangeError("Fecha inválida");
 const t=Date.parse(s+"T00:00:00Z");
 if(!Number.isFinite(t)||new Date(t).toISOString().slice(0,10)!==s)throw new RangeError("Día inválido");
 return t;
}
function canonical(s){return s.normalize("NFKD").toLowerCase().replace(/[\u0300-\u036f]/g,"").replace(/[^a-z0-9]+/g," ").trim();}
export function validateEntityNewsJoin(r,now=Date.now()){
 if(!r||typeof r!=="object"||r.provider!=="wikimedia_rss_headline_join_v1"||
    r.market_study_complete!==false||r.source_article_verified!==false||
    r.ready_for_youtube!==false||r.ready_for_script!==false ||
    !Number.isSafeInteger(r.company_count)||r.company_count<0||r.company_count>24||
    !Number.isSafeInteger(r.news_count)||r.news_count<0||r.news_count>100||
    !Array.isArray(r.matches)||r.matches.length>100||r.match_count!==r.matches.length)
    throw new RangeError("Cruce preliminar inválido");
 const collected=day(r.collected_on);
 if(collected>now+86400000||collected<now-7*86400000)throw new RangeError("Cruce caduco");
 const pairs=new Set(),items=[];
 for(const m of r.matches){
   if(!m||typeof m!=="object"||!QID.test(m.wikidata_id)||
      !NEWS.test(m.news_id)||typeof m.matched_alias!=="string"||
      m.matched_alias.length<6||m.matched_alias.length>130||
      canonical(m.matched_alias)!==m.matched_alias ||
      typeof m.headline!=="string"||m.headline.length<12||m.headline.length>280||
      m.match_status!=="candidate_needs_entity_confirmation"||
      m.method!=="exact_normalized_headline_v1"||
      m.source_article_verified!==false||m.youtube_market_verified!==false||
      m.editorial_authorized!==false)
     throw new RangeError("Vínculo no respaldado");
   const u=new URL(m.aggregator_url);
   if(u.protocol!=="https:"||u.hostname!=="news.google.com"||u.username||u.password||u.port)
     throw new RangeError("Agregador incorrecto");
   const headline=canonical(m.headline);
   if(!(" "+headline+" ").includes(" "+m.matched_alias+" "))throw new RangeError("Empresa no figura en titular");
   const key=m.wikidata_id+"|"+m.news_id;
   if(pairs.has(key))throw new RangeError("Duplicado");
   pairs.add(key);
   items.push([m.wikidata_id,m.news_id,m.matched_alias,m.method,m.match_status]);
 }
 return items;
}
export async function storeEntityNewsJoin(db,r){
 const items=validateEntityNewsJoin(r);
 const payload=new TextEncoder().encode(JSON.stringify(r));
 const hash=[...new Uint8Array(await crypto.subtle.digest("SHA-256",payload))]
   .map(b=>b.toString(16).padStart(2,"0")).join("");
 const id="join-"+hash.slice(0,28);
 const stmts=[db.prepare(
   "INSERT OR IGNORE INTO market_entity_news_runs(id,collected_on,provider,company_count,news_count,match_count) VALUES (?,?,?,?,?,?)"
 ).bind(id,r.collected_on,r.provider,r.company_count,r.news_count,items.length),
 ...items.map(row=>db.prepare(
   "INSERT INTO market_entity_news_links(wikidata_id,news_id,matched_alias,match_method,match_status,first_run_id,last_run_id,first_seen_at,last_seen_at) "+
   "VALUES (?,?,?,?,?,?,?,?,?) ON CONFLICT(wikidata_id,news_id) DO UPDATE SET "+
   "last_run_id=excluded.last_run_id,last_seen_at=MAX(last_seen_at,excluded.last_seen_at)"
 ).bind(...row,id,id,r.collected_on,r.collected_on))
 ];
 await db.batch(stmts);
 return {ok:true,stored_in:"d1",run_id:id,matched_pairs:items.length,
   source_article_verified:false,automatic_publication_allowed:false};
}
export async function readEntityNewsJoin(db,url){
 const raw=url.searchParams.get("limit")??"25";
 if(!/^\d{1,2}$/.test(raw)||Number(raw)<1||Number(raw)>50)
   return {error:"Límite entre 1 y 50",status:400};
 try{
   const [runs,links]=await Promise.all([
     db.prepare("SELECT id,collected_on,company_count,news_count,match_count FROM market_entity_news_runs ORDER BY collected_on DESC LIMIT ?").bind(Number(raw)).all(),
     db.prepare("SELECT l.wikidata_id,e.title AS company,l.news_id,n.headline,n.source_label,n.published_at,l.matched_alias,l.match_status FROM market_entity_news_links l JOIN market_entities e ON e.wikidata_id=l.wikidata_id JOIN market_news_leads n ON n.id=l.news_id ORDER BY l.last_seen_at DESC LIMIT ?").bind(Number(raw)).all()
   ]);
   return {ok:true,runs:runs.results||[],links:links.results||[],
      market_study_complete:false,automatic_publication_allowed:false,
      warning:"Coincidencia literal pendiente de comprobar identidad y fuentes originales"};
 }catch(e){
   if(/no such table:\s*market_entity_news_/i.test(String(e?.message||"")))
     return {error:"Falta migración 0007_entity_news_links.sql",status:503};
   throw e;
 }
}
