import {triageNewsLeads} from "./news-triage.mjs";
// Titulares auxiliares de Google News RSS; NUNCA hechos o demanda verificados.
// Ingesta solo desde el workflow de GitHub autenticado por OIDC.
const CATEGORY = new Set(["empresas","innovacion","tecnologia","industria"]);
const ID = /^news-[a-f0-9]{32}$/;
function timestamp(s) {
  if(typeof s!=="string" || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(s))
    throw new RangeError("Fecha UTC incorrecta");
  const t=Date.parse(s);
  if(!Number.isFinite(t) || new Date(t).toISOString().replace(".000Z","Z")!==s)
    throw new RangeError("Fecha UTC inexistente");
  return t;
}
function aggregatedURL(s) {
  if(typeof s!=="string" || s.length>1600) throw new RangeError("URL agregador inválida");
  let u;
  try {u=new URL(s);} catch {throw new RangeError("URL inválida");}
  if(u.protocol!=="https:" || !["news.google.com","www.google.com"].includes(u.hostname) ||
     !["/rss/articles/","/articles/","/read/"].some(p=>u.pathname.startsWith(p)) ||
     u.username || u.password || u.port || u.hash) throw new RangeError("Solo agregador Google News HTTPS");
  return u.href;
}
export function validateNewsReport(r) {
  if(!r || typeof r!=="object" || Array.isArray(r) || r.provider!=="google_news_rss" ||
     r.market_study_complete!==false || r.ready_for_youtube!==false ||
     r.ready_for_script!==false || r.youtube_market_verified!==false ||
     r.source_verification_complete!==false) throw new RangeError("Reporte de noticias no preliminar");
  const collected=timestamp(r.collected_at);
  if(collected>Date.now()+600000 || collected<Date.now()-604800000)
    throw new RangeError("Reporte demasiado viejo o futuro");
  if(!Array.isArray(r.feeds) || r.feeds.length<1 || r.feeds.length>4 ||
     r.feeds_succeeded!==r.feeds.length || r.feeds_attempted!==4 ||
     !Array.isArray(r.leads) || r.leads.length>100 || r.lead_count!==r.leads.length)
    throw new RangeError("Tamaño del radar de noticias inválido");
  const categories=new Set();
  for(const f of r.feeds){
    if(!f || !CATEGORY.has(f.category) || categories.has(f.category) ||
       !["en","es"].includes(f.language) || !["PE","MX","US"].includes(f.region) ||
       !Number.isSafeInteger(f.items_accepted) || f.items_accepted<0 || f.items_accepted>25)
      throw new RangeError("Feed incoherente");
    const u=new URL(f.feed_url);
    if(u.protocol!=="https:" || u.hostname!=="news.google.com" ||
       u.pathname!=="/rss/search" || !u.searchParams.has("q") || u.username || u.password ||
       u.port || u.hash) throw new RangeError("Feed no admitido");
    categories.add(f.category);
  }
  const rows=[], ids=new Set();
  for(const lead of r.leads) {
    if(!lead || typeof lead!=="object" || Array.isArray(lead) ||
       typeof lead.id!=="string" || !ID.test(lead.id) || ids.has(lead.id) ||
       !categories.has(lead.category) ||
       typeof lead.headline!=="string" || lead.headline.trim().length<12 ||
       lead.headline.length>280 || /[\r\n\0]/.test(lead.headline) ||
       typeof lead.source_label!=="string" || lead.source_label.trim().length<2 ||
       lead.source_label.length>120 || lead.verification_state!=="unverified" ||
       lead.youtube_demand_verified!==false || lead.editorial_authorized!==false)
      throw new RangeError("Titular no verificable o ya autorizado");
    const date=timestamp(lead.published_at);
    if(date<collected-72*3600000 || date>collected+10*60000)
      throw new RangeError("Titular fuera de ventana actual");
    const link=aggregatedURL(lead.aggregator_url);
    rows.push([lead.id,lead.headline,link,lead.source_label,lead.category,lead.published_at,
      r.collected_at,r.collected_at]);
    ids.add(lead.id);
  }
  return rows;
}
export async function storeNewsReport(db,report) {
  const rows=validateNewsReport(report);
  const data=new TextEncoder().encode(JSON.stringify({
    collected_at:report.collected_at, ids:rows.map(r=>r[0]).sort()
  }));
  const hash=[...new Uint8Array(await crypto.subtle.digest("SHA-256",data))]
    .map(x=>x.toString(16).padStart(2,"0")).join("").slice(0,24);
  const id="newsrun-"+hash;
  const statements=[
    db.prepare("INSERT OR IGNORE INTO market_news_runs(id,collected_at,provider,feed_count,lead_count) VALUES (?,?,?,?,?)")
      .bind(id,report.collected_at,"google_news_rss",report.feeds_succeeded,rows.length),
    ...rows.map(row=>db.prepare(
      "INSERT INTO market_news_leads(id,headline,aggregator_url,source_label,category,published_at,first_seen_at,last_seen_at,latest_run_id) "+
      "VALUES (?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET last_seen_at=MAX(last_seen_at,excluded.last_seen_at),"+
      "latest_run_id=excluded.latest_run_id"
    ).bind(...row,id))
  ];
  await db.batch(statements);
  return {ok:true,stored_in:"d1",run_id:id,leads_seen:rows.length,
    source_verification_complete:false,youtube_market_verified:false,
    market_study_complete:false,automatic_publication_allowed:false};
}
export async function readNewsLeads(db,url) {
  const raw=url.searchParams.get("limit")||"30";
  if(!/^\d{1,3}$/.test(raw) || Number(raw)<1 || Number(raw)>100)
    return {error:"Límite entre 1 y 100",status:400};
  try {
    const [rows,runs]=await Promise.all([
      db.prepare("SELECT id,headline,aggregator_url,source_label,category,published_at,verification_state FROM market_news_leads ORDER BY published_at DESC,id LIMIT ?").bind(Number(raw)).all(),
      db.prepare("SELECT id,collected_at,feed_count,lead_count FROM market_news_runs ORDER BY collected_at DESC LIMIT 10").all()
    ]);
    const leads=rows.results||[];
    const screening=triageNewsLeads(leads).slice(0,10);
    return {ok:true,leads,runs:runs.results||[],preliminary_screening:screening,
      source_verification_complete:false,youtube_market_verified:false,
      automatic_publication_allowed:false,warning:"Titulares agregados no son hechos verificados ni demanda YouTube."};
  } catch(e) {
    if(/no such table:\s*market_news_/i.test(String(e?.message||"")))
      return {error:"Falta migración 0005_news_leads.sql",status:503};
    throw e;
  }
}
