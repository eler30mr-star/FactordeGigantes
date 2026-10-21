// Ingesta de radar Wikimedia en D1. No clasifica demanda YouTube ni autoriza video.
// Validación integral antes de DB.batch: D1 ejecuta el lote de forma atómica.
const METHOD = "wikimedia_wikidata_company_discovery_v1";
const QID = /^Q[1-9][0-9]*$/;
const ISO = /^\d{4}-\d{2}-\d{2}$/;
const own = (o,k)=>Object.prototype.hasOwnProperty.call(o,k);
const nonneg = n=>Number.isSafeInteger(n) && n>=0;
function day(s) {
  if(typeof s!=="string" || !ISO.test(s)) throw new RangeError("Fecha ISO incorrecta");
  const t=Date.parse(s+"T00:00:00Z");
  if(!Number.isFinite(t) || new Date(t).toISOString().slice(0,10)!==s)
    throw new RangeError("Fecha inexistente");
  return t;
}
function pageUrl(s,lang) {
  if(typeof s!=="string" || s.length>1300) throw new RangeError("Fuente inválida");
  let u;
  try {u=new URL(s);} catch {throw new RangeError("Fuente inválida");}
  if(u.protocol!=="https:" || u.hostname!==lang+".wikipedia.org" || !u.pathname.startsWith("/wiki/") ||
     u.username || u.password || u.port || u.hash || u.search) throw new RangeError("Fuente Wikimedia no permitida");
  return u.href;
}
function website(s) {
  if(s===null || s===undefined) return null;
  if(typeof s!=="string" || s.length>1300) throw new RangeError("Sitio inválido");
  let u;
  try {u=new URL(s);} catch {throw new RangeError("Sitio inválido");}
  if(u.protocol!=="https:" || !u.hostname || u.username || u.password || u.port) throw new RangeError("Sitio HTTPS inválido");
  return u.href;
}
function stable(value) {
  if(Array.isArray(value)) return "["+value.map(stable).join(",")+"]";
  if(value && typeof value==="object") return "{"+Object.keys(value).sort().map(k=>JSON.stringify(k)+":"+stable(value[k])).join(",")+"}";
  return JSON.stringify(value);
}
export function validateMarketReport(r) {
  if(!r || typeof r!=="object" || Array.isArray(r) || r.method!==METHOD ||
    r.market_study_complete!==false || r.ready_for_youtube!==false ||
    r.youtube_market_verified!==false || r.ready_for_script!==false)
    throw new RangeError("Informe sin garantías de radar preliminar");
  const collected=day(r.collected_on), observed=day(r.data_day);
  if(observed>collected || collected>Date.now()+86400000) throw new RangeError("Fecha de radar fuera de rango");
  if(!Array.isArray(r.candidates) || r.candidates.length>24 ||
     r.company_candidates_count!==r.candidates.length) throw new RangeError("Cantidad de candidatas inválida");
  if(!nonneg(r.wikidata_requests) || r.wikidata_requests>12 ||
    !nonneg(r.articles_considered) || r.articles_considered>360)
    throw new RangeError("Presupuesto de descubrimiento inválido");
  const entities=[],signals=[],windows=[],seen=new Set();
  for(const c of r.candidates) {
    if(!c || typeof c!=="object" || Array.isArray(c) || !QID.test(c.wikidata_id) ||
       seen.has(c.wikidata_id) || typeof c.topic!=="string" ||
       c.topic.trim().length<3 || c.topic.length>130 || c.market_rank_qualified!==false ||
       c.youtube_data_collected!==false || c.primary_documents_verified!==false ||
       c.research_started!==false || c.youtube_publication_authorized!==false)
      throw new RangeError("Entidad incompleta o autorizada indebidamente");
    seen.add(c.wikidata_id);
    entities.push([c.wikidata_id,c.topic,r.collected_on,r.collected_on,website(c.official_website_candidate)]);
    if(!Array.isArray(c.discovery_signals) || c.discovery_signals.length<1 ||
       c.discovery_signals.length>4) throw new RangeError("Señales ausentes");
    const local=new Set();
    for(const s of c.discovery_signals) {
      if(!s || typeof s!=="object" || !["es.wikipedia","en.wikipedia"].includes(s.project) ||
        s.source!=="wikimedia_daily_top_plus_wikidata_p31" || day(s.observed_on)>collected ||
        !Number.isSafeInteger(s.rank) || s.rank<1 ||
        !nonneg(s.views)) throw new RangeError("Señal no verificable");
      const lang=s.project.split(".")[0];
      const link=pageUrl(s.url,lang);
      const pair=s.project+"|"+s.observed_on;
      if(local.has(pair)) throw new RangeError("Señal repetida");
      local.add(pair);
      signals.push([c.wikidata_id,s.project,s.observed_on,s.rank,s.views,link]);
    }
    if(c.interest_14d_status==="measured") {
      const w=c.wikipedia_interest;
      if(!w || typeof w!=="object" || w.origin!=="wikimedia_pageviews_api") throw new RangeError("Serie inválida");
      const first=day(w.source_period_start),end=day(w.source_period_end),now=day(w.observed_at);
      if(end-first!==13*86400000 || now-end!==86400000 || now!==collected ||
         !nonneg(w.views_last_7d) || !nonneg(w.views_previous_7d))
        throw new RangeError("La serie no cubre 14 días completos");
      const lang=c.discovery_signals[0].project.split(".")[0];
      windows.push([c.wikidata_id,w.observed_at,pageUrl(w.url,lang),w.source_period_start,
        w.source_period_end,w.views_last_7d,w.views_previous_7d]);
    } else if(c.interest_14d_status && c.interest_14d_status!=="unavailable") {
      throw new RangeError("Estado de serie inválido");
    }
  }
  if(r.wikipedia_interest_measured_count!==windows.length)
    throw new RangeError("Conteo de series incompatible");
  return {entities,signals,windows};
}
export async function persistMarketReport(db,report) {
  const {entities,signals,windows}=validateMarketReport(report);
  const payload=new TextEncoder().encode(stable(report));
  const hash=Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256",payload)),
    b=>b.toString(16).padStart(2,"0")).join("");
  const id="market-"+hash.slice(0,24);
  const statements=[
    db.prepare("INSERT OR IGNORE INTO market_runs(id,collection_day,data_day,source_method,detected_count,study_complete) VALUES (?,?,?,?,?,0)")
      .bind(id,report.collected_on,report.data_day,METHOD,entities.length),
    ...entities.map(e=>db.prepare(
      "INSERT INTO market_entities(wikidata_id,title,first_seen,last_seen,official_website_candidate) VALUES (?,?,?,?,?) "+
      "ON CONFLICT(wikidata_id) DO UPDATE SET title=excluded.title,last_seen=MAX(last_seen,excluded.last_seen),"+
      "official_website_candidate=COALESCE(excluded.official_website_candidate,official_website_candidate),updated_at=datetime('now')"
    ).bind(...e)),
    ...signals.map(s=>db.prepare(
      "INSERT OR IGNORE INTO market_pageview_observations(wikidata_id,project,observation_day,rank,top_day_views,source_url,run_id) VALUES (?,?,?,?,?,?,?)"
    ).bind(...s,id)),
    ...windows.map(w=>db.prepare(
      "INSERT OR IGNORE INTO market_interest_windows(wikidata_id,observed_at,source_url,period_start,period_end,views_last_7d,views_previous_7d,run_id) VALUES (?,?,?,?,?,?,?,?)"
    ).bind(...w,id))
  ];
  await db.batch(statements);
  return {ok:true,run_id:id,entities_seen:entities.length,signals_seen:signals.length,
    windows_seen:windows.length,stored_in:"d1",market_study_complete:false,
    youtube_data_verified:false,automatic_publication_allowed:false};
}
