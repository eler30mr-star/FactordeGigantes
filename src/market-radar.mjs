// Radar de mercado: acceso administrativo de solo lectura, sin decisiones editoriales.
export async function readMarketRadar(env, url) {
  const limitValue = url.searchParams.get("limit") ?? "30";
  if (!/^[0-9]{1,3}$/.test(limitValue)) return {error:"Límite inválido",status:400};
  const limit=Number(limitValue);
  if (limit<1 || limit>100) return {error:"Límite entre 1 y 100",status:400};
  try {
    const [runs,entities,windows]=await Promise.all([
      env.DB.prepare("SELECT id,collection_day,data_day,source_method,detected_count,study_complete,created_at FROM market_runs ORDER BY collection_day DESC,created_at DESC LIMIT ?").bind(limit).all(),
      env.DB.prepare("SELECT wikidata_id,title,first_seen,last_seen,research_state,official_website_candidate FROM market_entities ORDER BY last_seen DESC,wikidata_id ASC LIMIT ?").bind(limit).all(),
      env.DB.prepare("SELECT wikidata_id,observed_at,source_url,period_start,period_end,views_last_7d,views_previous_7d FROM market_interest_windows ORDER BY observed_at DESC,wikidata_id ASC LIMIT ?").bind(limit).all()
    ]);
    return {ok:true,source:"wikimedia",market_study_complete:false,youtube_data_verified:false,automatic_publication_allowed:false,
      runs:runs.results ?? [],entities:entities.results ?? [],interest_windows:windows.results ?? [],
      warning:"Las visitas Wikipedia no son demanda, búsquedas ni audiencia observada en YouTube"};
  } catch(e) {
    if (/no such table:\s*market_/i.test(String(e?.message || "")))
      return {error:"Falta aplicar la migración 0004_market_intelligence.sql en D1",status:503};
    throw e;
  }
}
