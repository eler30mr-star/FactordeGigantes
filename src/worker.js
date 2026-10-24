import {storeAutonomousDraft,hasAutonomousOrigin,readEditorialScriptContext} from './autonomous-script-drafts.mjs';
import {verifyMarketOIDC} from "./github-oidc.mjs";
import {reserveAiBudget,storeAiReport,readAiReports,classifyWithCloudflare,readScriptContext} from "./ai-research-team.mjs";
import {selectResearchFromD1,readResearchQueue} from "./market-research-selection.mjs";
import {storeNewsEntities} from "./news-entity-ingest.mjs";
import {storeOfficialEvidence,readOfficialEvidence} from "./market-official-ingest.mjs";
import {storePdfEvidence,readPdfEvidence} from "./market-pdf-ingest.mjs";
import {storeMarketResearch,readMarketResearch} from "./market-research-ingest.mjs";
import {assessMarketFromD1,readMarketAssessments} from "./market-assessment.mjs";
import {persistYoutubeStudy,readYoutubeMarket} from "./youtube-market.mjs";
import {storeEntityNewsJoin,readEntityNewsJoin} from "./market-cross-signals.mjs";
import {storeNewsReport,readNewsLeads} from "./news-ingest.mjs";
import {readMarketRadar} from "./market-radar.mjs";
import {persistMarketReport} from "./market-ingest.mjs";
import {validateDossier} from "./editorial.mjs";
import {launchResearch,listResearchRequests} from "./research-control.mjs";
import {systemReadiness} from "./system-readiness.mjs";
// Factor de Gigantes — backend de aprobación y orquestación.
// Tokens secretos configurados con 'wrangler secret put'; no hay publicación directa.
const json = (data, status = 200) => new Response(JSON.stringify(data), {
  status, headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff" }
});
const err = (message, status = 400) => json({error: message}, status);
function token(req) { const a=req.headers.get("Authorization") || ""; return a.startsWith("Bearer ") ? a.slice(7) : ""; }
function guard(req, env, kind = "ADMIN_TOKEN") {
  const expected = env[kind];
  return !!expected && expected.length >= 24 && token(req) === expected;
}
async function parseBody(request) {
  if (Number(request.headers.get("content-length") || 0) > 250000) throw Error("Solicitud demasiado grande");
  const reader=request.body?.getReader();
  if(!reader)throw new RangeError("Falta cuerpo JSON");
  const chunks=[];let size=0;
  while(true){
    const {done,value}=await reader.read();if(done)break;
    size+=value.byteLength;
    if(size>250000){await reader.cancel();throw new RangeError("Solicitud demasiado grande");}
    chunks.push(value);
  }
  const bytes=new Uint8Array(size);let offset=0;
  for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.byteLength;}
  const text=new TextDecoder().decode(bytes);
  return JSON.parse(text);
}
function validateManifest(m) {
  if (!m || typeof m !== "object" || Array.isArray(m)) throw Error("Guion no válido");
  const clean = {
    title: String(m.title || "").trim(),
    angle: String(m.angle || "").trim(),
    format: m.format,
    sources: m.sources,
    segments: m.segments
  };
  if (clean.title.length < 8 || clean.title.length > 150) throw Error("Título entre 8 y 150 caracteres");
  if (clean.angle.length < 15 || clean.angle.length > 700) throw Error("Enfoque entre 15 y 700 caracteres");
  if (!["short","long"].includes(clean.format)) throw Error("Formato incorrecto");
  if (!Array.isArray(clean.sources) || clean.sources.length < 2 || clean.sources.length > 20)
    throw Error("Se requieren entre 2 y 20 fuentes documentales");
  clean.sources = clean.sources.map(s => {
    const u = new URL(typeof s === "string" ? s : s.url);
    if (u.protocol !== "https:") throw Error("Las fuentes deben ser HTTPS");
    return u.href;
  });
  if (!Array.isArray(clean.segments) || clean.segments.length < 2 || clean.segments.length > 18)
    throw Error("Se requieren entre 2 y 18 segmentos");
  clean.segments = clean.segments.map(s => {
    const heading=String(s.headline || "").trim();
    const voiceover=String(s.voiceover || "").trim();
    if (!heading || heading.length > 110 || voiceover.length < 15 || voiceover.length > 900)
      throw Error("Cada segmento necesita título (máx 110) y voz entre 15 y 900 caracteres");
    return {headline: heading, voiceover};
  });
  return clean;
}
async function record(env, id, action, note = "") {
  await env.DB.prepare("INSERT INTO events (job_id,action,note) VALUES (?,?,?)").bind(id, action, String(note).slice(0,600)).run();
}
async function find(env,id) {
  return env.DB.prepare("SELECT * FROM jobs WHERE id=?").bind(id).first();
}
async function getDossier(env,id) {
  try {
    return await env.DB.prepare("SELECT dossier_json, editor_attested, editor_name, attested_at, updated_at FROM editorial_dossiers WHERE job_id=?").bind(id).first();
  } catch(e) {
    if (/no such table.*editorial_dossiers/i.test(String(e?.message || e)))
      throw new Error("EDITORIAL_MIGRATION_PENDING");
    throw e;
  }
}
async function editorialGate(env,id,manifest) {
  const stored = await getDossier(env,id);
  if (!stored || stored.editor_attested !== 1 || !stored.editor_name)
    return {ok:false, reason:"Falta expediente editorial revisado y confirmado por el editor"};
  try {
    const summary = validateDossier(JSON.parse(stored.dossier_json),manifest);
    if (!summary.structurally_complete)
      return {ok:false, reason:"Existen afirmaciones sin verificar o recursos sin derechos acreditados"};
    return {ok:true, summary};
  } catch {
    return {ok:false, reason:"Expediente no corresponde al guion o contiene datos incompletos"};
  }
}
const dto = row => ({id:row.id, title:row.title, format:row.format, status:row.status,
   manifest:JSON.parse(row.manifest_json), review_note:row.review_note, last_error:row.last_error,
   created_at:row.created_at, updated_at:row.updated_at});
async function setStatus(env,id,status, action, extra = {}) {
  await env.DB.prepare("UPDATE jobs SET status=?, review_note=?,last_error=?, updated_at=datetime('now') WHERE id=?")
    .bind(status, extra.review_note ?? "", extra.last_error ?? "",id).run();
  await record(env,id,action,extra.review_note || extra.last_error || "");
}
async function reserveRenderDispatch(env,id) {
  // Cambio condicional atómico en D1: evita dos workflow_dispatch para el mismo trabajo.
  const result=await env.DB.prepare(
    "UPDATE jobs SET status='queued', updated_at=datetime('now') "+
    "WHERE id=? AND status='approved' AND EXISTS "+
    "(SELECT 1 FROM editorial_dossiers WHERE job_id=? AND editor_attested=1 AND editor_name<>'')"
  ).bind(id,id).run();
  return result.meta?.changes === 1;
}
async function restoreRejectedDispatch(env,id) {
  // Solo ante rechazo explícito de GitHub; timeout ambiguo conserva queued y exige revisión.
  await env.DB.prepare(
    "UPDATE jobs SET status='approved', updated_at=datetime('now') WHERE id=? AND status='queued'"
  ).bind(id).run();
  await record(env,id,"render_dispatch_rejected","GitHub rechazó el despacho; se permite reintentar tras revisar permisos");
}
async function handle(request,env) {
  const url = new URL(request.url);
  if (url.pathname === "/health" && request.method === "GET") return json({ok:true,product:"Factor de Gigantes",version:"0.1.0"});
  if (!url.pathname.startsWith("/api/")) return env.ASSETS.fetch(request);
  const parts=url.pathname.split("/").filter(Boolean);
  const method=request.method;
  const renderer=parts[1] === "renderer";
  const ingest=parts[1] === "market" && parts[2] === "ingest" && parts.length===3;
  const ingestNews=parts[1] === "market" && parts[2] === "news" && parts[3] === "ingest" && parts.length===4;
  const ingestYoutube=parts[1] === "market" && parts[2] === "youtube" && parts[3] === "ingest" && parts.length===4;
  const ingestCross=parts[1] === "market" && parts[2] === "cross" && parts[3] === "ingest" && parts.length===4;
  const ingestNewsEntities=parts[1]==="market" && parts[2]==="entities" && parts[3]==="ingest" && parts.length===4;
  const runAssessment=parts[1]==="market" && parts[2]==="assess" && parts[3]==="run" && parts.length===4;
  const ingestOfficial=parts[1]==="market" && parts[2]==="official" && parts[3]==="ingest" && parts.length===4;
  const ingestPdf=parts[1]==="market" && parts[2]==="pdf" && parts[3]==="ingest" && parts.length===4;
  const ingestResearch=parts[1]==="market" && parts[2]==="research" && parts[3]==="ingest" && parts.length===4;
  const runResearchSelection=url.pathname==='/api/market/research-selection/run';
  const aiWrite=['/api/market/ai-budget/reserve','/api/market/ai-classify','/api/market/ai-pipeline/ingest','/api/market/ai-pipeline/script-context','/api/market/ai-pipeline/script-ingest'].includes(url.pathname);
  // Radar: autorización OIDC efímera firmada por GitHub; no admite tokens admin/render.
  if (ingest || ingestNews || ingestYoutube || ingestCross || ingestNewsEntities || runAssessment || ingestOfficial || ingestPdf || ingestResearch || runResearchSelection || aiWrite) {
    if (!await verifyMarketOIDC(request)) return err("Acceso no autorizado",401);
  } else if (!guard(request,env,renderer ? "RENDERER_TOKEN" : "ADMIN_TOKEN")) {
    return err("Acceso no autorizado",401);
  }
  if (!env.DB) return err("D1 no configurado",503);
  if(aiWrite||url.pathname==='/api/market/ai-pipeline'){
    if(method!==(aiWrite?'POST':'GET'))return err('Método no admitido',405);
    try{
      if(!aiWrite)return json(await readAiReports(env.DB));
      const body=await parseBody(request);
      if(url.pathname==='/api/market/ai-pipeline/script-ingest'){
        const result=await storeAutonomousDraft(env.DB,body);
        return json(result,result.ok?201:result.status);
      }
      if(url.pathname==='/api/market/ai-pipeline/script-context')return json(await readEditorialScriptContext(env.DB,body.run_id));
      if(url.pathname==='/api/market/ai-budget/reserve')
        return json(await reserveAiBudget(env.DB,body.provider,body.request_id));
      if(url.pathname==='/api/market/ai-classify')return json(await classifyWithCloudflare(env,body));
      return json(await storeAiReport(env.DB,body),201);
    }catch(e){
      if(e instanceof RangeError||e instanceof SyntaxError||e instanceof TypeError)
        return err('Informe o solicitud de IA inválida',400);
      if(/no such table:\s*autonomous_script_drafts/i.test(String(e?.message||'')))
        return err('Falta migración 0014_autonomous_script_drafts.sql',503);
      if(/no such table:\s*(ai_budget_|market_ai_)/i.test(String(e?.message||'')))
        return err('Falta migración 0013_ai_research_team.sql',503);
      throw e;
    }
  }
  if(runResearchSelection){
    if(method!=='POST')return err('Método no admitido',405);
    return json(await selectResearchFromD1(env.DB),201);
  }
  if(url.pathname==='/api/market/research-queue'){
    if(method!=='GET')return err('Método no admitido',405);
    const out=await readResearchQueue(env.DB);
    return out.error?err(out.error,out.status):json(out);
  }
  if (ingest) {
    if (method !== "POST") return err("Método no admitido",405);
    try {return json(await persistMarketReport(env.DB,await parseBody(request)),201);}
    catch(e) {
      if (e instanceof RangeError) return err("Informe de radar rechazado: "+e.message,400);
      if (/no such table:\s*market_/i.test(String(e?.message || "")))
        return err("D1 necesita migración 0004_market_intelligence.sql",503);
      throw e;
    }
  }
  if (ingestNews) {
    if (method !== "POST") return err("Método no admitido",405);
    try { return json(await storeNewsReport(env.DB,await parseBody(request)),201); }
    catch(e) {
      if(e instanceof RangeError) return err("Reporte informativo rechazado: "+e.message,400);
      if(/no such table:\s*market_news_/i.test(String(e?.message||"")))
        return err("D1 necesita migración 0005_news_leads.sql",503);
      throw e;
    }
  }
  if (ingestYoutube) {
    if(method!=="POST") return err("Método no admitido",405);
    try {return json(await persistYoutubeStudy(env.DB,await parseBody(request)),201);}
    catch(e){
      if(e instanceof RangeError) return err("Informe YouTube rechazado: "+e.message,400);
      if(/no such table:\s*market_youtube_/i.test(String(e?.message||"")))
        return err("D1 necesita migración 0006_youtube_observations.sql",503);
      throw e;
    }
  }
  if(!renderer && url.pathname==="/api/market/youtube"){
    if(method!=="GET") return err("Método no admitido",405);
    const report=await readYoutubeMarket(env.DB,url);
    return report.error?err(report.error,report.status):json(report);
  }
  if (ingestCross) {
    if(method!=="POST") return err("Método no admitido",405);
    try{return json(await storeEntityNewsJoin(env.DB,await parseBody(request)),201);}
    catch(e){
      if(e instanceof RangeError)return err("Cruce de noticias rechazado: "+e.message,400);
      if(/no such table:\s*market_entity_news_/i.test(String(e?.message||"")))
        return err("D1 necesita migración 0007_entity_news_links.sql",503);
      throw e;
    }
  }
  if(!renderer && url.pathname==="/api/market/cross"){
    if(method!=="GET")return err("Método no admitido",405);
    const out=await readEntityNewsJoin(env.DB,url);
    return out.error?err(out.error,out.status):json(out);
  }
  if(ingestResearch){
    if(method!=="POST")return err("Método no admitido",405);
    try{return json(await storeMarketResearch(env.DB,await parseBody(request)),201);}
    catch(e){
      if(e instanceof RangeError)return err("Expediente del investigador rechazado: "+e.message,400);
      if(/no such table:\s*market_research_/i.test(String(e?.message||"")))
        return err("D1 necesita migración 0011_market_research.sql",503);
      throw e;
    }
  }
  if(!renderer&&url.pathname==="/api/market/research"){
    if(method!=="GET")return err("Método no admitido",405);
    const out=await readMarketResearch(env.DB,url);
    return out.error?err(out.error,out.status):json(out);
  }
  if(ingestPdf){
    if(method!=="POST")return err("Método no admitido",405);
    try{return json(await storePdfEvidence(env.DB,await parseBody(request)),201);}
    catch(e){
      if(e instanceof RangeError)return err("Evidencia PDF rechazada: "+e.message,400);
      if(/no such table:\s*market_pdf_/i.test(String(e?.message||"")))
        return err("D1 necesita migración 0010_pdf_evidence.sql",503);
      throw e;
    }
  }
  if(!renderer&&url.pathname==="/api/market/pdf"){
    if(method!=="GET")return err("Método no admitido",405);
    const out=await readPdfEvidence(env.DB,url);
    return out.error?err(out.error,out.status):json(out);
  }
  if(ingestOfficial){
    if(method!=="POST")return err("Método no admitido",405);
    try{return json(await storeOfficialEvidence(env.DB,await parseBody(request)),201);}
    catch(e){
      if(e instanceof RangeError)return err("Evidencia corporativa rechazada: "+e.message,400);
      if(/no such table:\s*market_official_/i.test(String(e?.message||"")))
        return err("D1 necesita migración 0009_official_evidence.sql",503);
      throw e;
    }
  }
  if(!renderer && url.pathname==="/api/market/official"){
    if(method!=="GET")return err("Método no admitido",405);
    const result=await readOfficialEvidence(env.DB,url);
    return result.error?err(result.error,result.status):json(result);
  }
  if (ingestNewsEntities) {
    if(method!=="POST")return err("Método no admitido",405);
    try{return json(await storeNewsEntities(env.DB,await parseBody(request)),201);}
    catch(e){
      if(e instanceof RangeError)return err("Candidatas Wikidata rechazadas: "+e.message,400);
      if(/no such table:\s*market_news_entity_/i.test(String(e?.message||"")))
        return err("D1 necesita migración 0008_news_entities_assessments.sql",503);
      throw e;
    }
  }
  if(runAssessment){
    if(method!=="POST")return err("Método no admitido",405);
    try{return json(await assessMarketFromD1(env.DB),201);}
    catch(e){
      if(/no such table:\s*market_assessments?|no such table:\s*market_news_entity_/i.test(String(e?.message||"")))
        return err("D1 necesita migración 0008_news_entities_assessments.sql",503);
      throw e;
    }
  }
  if(!renderer && url.pathname==="/api/market/opportunities"){
    if(method!=="GET")return err("Método no admitido",405);
    const view=await readMarketAssessments(env.DB,url);
    return view.error?err(view.error,view.status):json(view);
  }
  if (!renderer && url.pathname === "/api/market/news") {
    if(method !== "GET") return err("Método no admitido",405);
    const news=await readNewsLeads(env.DB,url);
    return news.error ? err(news.error,news.status) : json(news);
  }
  if (!renderer && url.pathname === "/api/market/radar") {
    if (method !== "GET") return err("Método no admitido",405);
    const radar=await readMarketRadar(env,url);
    return radar.error ? err(radar.error,radar.status) : json(radar);
  }
  // Diagnóstico de solo lectura; disponible exclusivamente para ADMIN_TOKEN.
  if (!renderer && url.pathname === "/api/system/status") {
    if (method !== "GET") return err("Método no admitido",405);
    return json(await systemReadiness(env));
  }
  // El investigador usa un workflow distinto de render.yml; requiere confirmación humana.
  // Se ejecuta tras ADMIN_TOKEN, nunca por el token del renderizador.
  if (!renderer && url.pathname === "/api/research") {
    if (method === "GET") return json(await listResearchRequests(env,{
      includeRuns:url.searchParams.get("runs")==="1"
    }));
    if (method === "POST") {
      const body=await parseBody(request);
      let result;
      try { result=await launchResearch(env,body); }
      catch(e) {
        if (e?.message?.includes("no such table: research_requests")) throw new Error("RESEARCH_MIGRATION_PENDING");
        if (e instanceof RangeError || e?.message?.startsWith("Tema") ||
            e?.message?.startsWith("Escribe") || e?.message?.startsWith("El tema")) return err(e.message,400);
        throw e;
      }
      return result.ok ? json(result,result.status) : err(result.error,result.status);
    }
    return err("Método no admitido",405);
  }
  if (renderer) {
    if (parts[2] !== "jobs" || !parts[3]) return err("Ruta no encontrada",404);
    const id=parts[3];
    const row=await find(env,id);
    if (!row) return err("Trabajo inexistente",404);
    if (await hasAutonomousOrigin(env.DB,id))
      return err("Producción canónica pendiente: este guion no admite el renderizador de previsualización",409);
    if (parts.length === 4 && method === "GET") {
      if (!["queued","rendering"].includes(row.status)) return err("Trabajo no autorizado para render",409);
      if (row.status === "queued") await setStatus(env,id,"rendering","render_started");
      return json({id,manifest:JSON.parse(row.manifest_json)});
    }
    if (parts[4] === "report" && method === "POST") {
      if (!["queued","rendering"].includes(row.status)) return err("Estado no modificable",409);
      const body=await parseBody(request);
      if (!["ready","failed"].includes(body.status)) return err("Estado inválido");
      await setStatus(env,id,body.status,body.status === "ready" ? "render_ready" : "render_failed",
        {last_error:body.status === "failed" ? String(body.detail || "").slice(0,500) : ""});
      return json({ok:true});
    }
    return err("Ruta no encontrada",404);
  }
  if (parts.length === 2 && parts[1] === "jobs" && method === "GET") {
    const result=await env.DB.prepare("SELECT * FROM jobs ORDER BY updated_at DESC LIMIT 100").all();
    return json({jobs:result.results.map(dto)});
  }
  if (parts.length === 2 && parts[1] === "jobs" && method === "POST") {
    const manifest=validateManifest(await parseBody(request));
    const id=crypto.randomUUID();
    await env.DB.prepare("INSERT INTO jobs(id,title,format,status,manifest_json) VALUES (?,?,?,?,?)")
      .bind(id,manifest.title,manifest.format,"draft",JSON.stringify(manifest)).run();
    await record(env,id,"created");
    return json({job: dto(await find(env,id))},201);
  }
  if (parts[1] !== "jobs" || !parts[2]) return err("Ruta no encontrada",404);
  const id=parts[2], row=await find(env,id);
  if (!row) return err("Trabajo inexistente",404);
  if (parts.length === 4 && parts[3] === "dossier") {
    if (method === "GET") {
      const stored=await getDossier(env,id);
      if (!stored) return json({dossier:null, summary:null, attested:false});
      const dossier=JSON.parse(stored.dossier_json);
      let summary=null, validation_error=null;
      try { summary=validateDossier(dossier,JSON.parse(row.manifest_json)); }
      catch(e) { validation_error=String(e.message).slice(0,160); }
      return json({dossier, summary, validation_error,
        attested:stored.editor_attested === 1 && !validation_error && summary?.structurally_complete === true,
        editor_name:stored.editor_name, attested_at:stored.attested_at});
    }
    if (method === "PUT") {
      if (!["draft","review"].includes(row.status))
        return err("El expediente solo se edita en borrador o revisión",409);
      const dossier=await parseBody(request);
      let summary;
      try { summary=validateDossier(dossier,JSON.parse(row.manifest_json)); }
      catch(e) { return err("Expediente inválido: "+String(e.message).slice(0,160)); }
      await env.DB.prepare(
        "INSERT INTO editorial_dossiers(job_id,dossier_json) VALUES (?,?) "+
        "ON CONFLICT(job_id) DO UPDATE SET dossier_json=excluded.dossier_json, "+
        "editor_attested=0, editor_name='', attested_at=NULL, updated_at=datetime('now')"
      ).bind(id,JSON.stringify(dossier)).run();
      await record(env,id,"dossier_saved","Fuentes: "+summary.source_count+"; afirmaciones: "+summary.claim_count);
      return json({ok:true, summary, attested:false});
    }
    return err("Método no admitido",405);
  }
  if (parts.length === 5 && parts[3] === "dossier" && parts[4] === "attest" && method === "POST") {
    if (row.status !== "review") return err("Solo se acredita en estado de revisión",409);
    const body=await parseBody(request);
    if (body.confirmed !== true) return err("Se necesita confirmación editorial explícita");
    const reviewer=typeof body.reviewer === "string" ? body.reviewer.trim() : "";
    if (reviewer.length < 3 || reviewer.length > 100) return err("Identifica al revisor (3-100 caracteres)");
    const stored=await getDossier(env,id);
    if (!stored) return err("Primero guarda el expediente documental",409);
    let summary;
    try { summary=validateDossier(JSON.parse(stored.dossier_json),JSON.parse(row.manifest_json)); }
    catch(e) { return err("Expediente inválido: "+String(e.message).slice(0,160),409); }
    if (!summary.structurally_complete)
      return err("Faltan afirmaciones verificadas por editor o licencias de recursos",409);
    await env.DB.prepare(
      "UPDATE editorial_dossiers SET editor_attested=1, editor_name=?, "+
      "attested_at=datetime('now'), updated_at=datetime('now') WHERE job_id=?"
    ).bind(reviewer,id).run();
    await record(env,id,"dossier_attested","Revisión humana confirmada: "+reviewer);
    return json({ok:true,attested:true,summary});
  }
  if (parts.length === 3 && method === "GET") {
    const e=await env.DB.prepare("SELECT action,note,created_at FROM events WHERE job_id=? ORDER BY id DESC LIMIT 40").bind(id).all();
    return json({job:dto(row),events:e.results});
  }
  if (parts.length === 3 && method === "PUT") {
    if (row.status !== "draft") return err("Solo se editan borradores",409);
    // No mutar el guion si Cloudflare aún no tiene la migración 0002.
    await getDossier(env,id);
    const manifest=validateManifest(await parseBody(request));
    // Si revocar la revisión falla, NO modificar el guion.
    await env.DB.prepare("UPDATE editorial_dossiers SET editor_attested=0, editor_name='', attested_at=NULL WHERE job_id=?").bind(id).run();
    await env.DB.prepare("UPDATE jobs SET title=?,format=?,manifest_json=?,review_note='',updated_at=datetime('now') WHERE id=?")
      .bind(manifest.title,manifest.format,JSON.stringify(manifest),id).run();
    await record(env,id,"edited");
    return json({job:dto(await find(env,id))});
  }
  if (parts.length !== 4 || method !== "POST") return err("Ruta no encontrada",404);
  const action=parts[3];
  if (action === "submit" && row.status === "draft") {
    await setStatus(env,id,"review","submitted_for_review"); return json({ok:true});
  }
  if (action === "approve" && row.status === "review") {
    const data=await parseBody(request);
    if (data.confirmed !== true) return err("Se requiere aprobación humana explícita");
    const manifest=validateManifest(JSON.parse(row.manifest_json));
    const gate=await editorialGate(env,id,manifest);
    if (!gate.ok) return err(gate.reason,409);
    await setStatus(env,id,"approved","approved_by_editor"); return json({ok:true});
  }
  if (action === "request-changes" && ["review","approved","failed"].includes(row.status)) {
    const data=await parseBody(request);
    const note=String(data.note || "").trim();
    if (note.length < 8 || note.length > 500) return err("Indica una razón de 8 a 500 caracteres");
    await env.DB.prepare("UPDATE editorial_dossiers SET editor_attested=0, editor_name='', attested_at=NULL WHERE job_id=?").bind(id).run();
    await setStatus(env,id,"draft","changes_requested",{review_note:note}); return json({ok:true});
  }
  if (action === "dispatch" && row.status === "approved") {
    if (await hasAutonomousOrigin(env.DB,id))
      return err("Integración de voz canónica y recursos por escena pendiente",409);
    const gate=await editorialGate(env,id,validateManifest(JSON.parse(row.manifest_json)));
    if (!gate.ok) return err(gate.reason,409);
    if (!env.GITHUB_DISPATCH_TOKEN || !env.GITHUB_REPO) return err("Acceso GitHub sin configurar",503);
    const repo=env.GITHUB_REPO;
    if (!/^[\w.-]+\/[\w.-]+$/.test(repo)) return err("Repositorio GitHub inválido",503);
    const workflow=env.GITHUB_WORKFLOW || "render.yml";
    const endpoint="https://api.github.com/repos/"+repo+"/actions/workflows/"+encodeURIComponent(workflow)+"/dispatches";
    if (!await reserveRenderDispatch(env,id))
      return err("Render ya reservado, o el estado/aprobación cambió; no duplicar el envío",409);
    let response;
    try {
      response=await fetch(endpoint,{method:"POST",headers:{
        "Authorization":"Bearer "+env.GITHUB_DISPATCH_TOKEN, "Accept":"application/vnd.github+json",
        "X-GitHub-Api-Version":"2022-11-28","User-Agent":"FactorDeGigantes-Worker",
        "Content-Type":"application/json"
      },body:JSON.stringify({ref:"main", inputs:{job_id:id}})});
    } catch {
      // Puede haberse entregado a GitHub pese al timeout: bloquear reintento ciego.
      await record(env,id,"render_dispatch_unknown","Resultado de red indeterminado; revisar Actions antes de reintentar");
      return err("Resultado del envío incierto; revisar GitHub Actions antes de reintentar para evitar duplicados",502);
    }
    if (!response.ok) {
      await restoreRejectedDispatch(env,id);
      // GitHub no devuelve los valores de las credenciales en su campo "message".
      // Exponer solo causas conocidas permite corregir permisos sin filtrar detalles.
      let reason = "";
      try {
        const data = await response.json();
        const message = typeof data?.message === "string" ? data.message : "";
        if (/Resource not accessible by personal access token/i.test(message))
          reason = "El token no tiene acceso suficiente al repositorio. Revisar propietario, selección del repositorio y permiso Actions: Read and write.";
        else if (/Bad credentials/i.test(message))
          reason = "El token de GitHub no es válido o está vencido.";
        else if (/rate limit/i.test(message))
          reason = "GitHub limitó temporalmente las solicitudes.";
        else if (/GitHub Actions is disabled/i.test(message))
          reason = "GitHub Actions está deshabilitado para este repositorio.";
      } catch { /* respuesta sin JSON: mantener código HTTP */ }
      return err("GitHub rechazó el render (HTTP "+response.status+")"+(reason ? ": "+reason : ""),502);
    }
    await record(env,id,"render_dispatched"); return json({ok:true});
  }
  return err("Acción no válida para este estado",409);
}
export default {
  async fetch(request,env) {
    try { return await handle(request,env); }
    catch(e) {
      if (e?.message === "RESEARCH_MIGRATION_PENDING" || /no such table: research_requests/i.test(String(e?.message || "")))
        return err("D1 requiere migración 0003_research_requests.sql antes de investigar",503);
      if (e?.message === "EDITORIAL_MIGRATION_PENDING")
        return err("D1 necesita aplicar la migración 0002_editorial_dossiers.sql antes de usar expedientes",503);
      if (e instanceof SyntaxError || e instanceof TypeError || String(e.message).includes("Solicitud demasiado grande"))
        return err("Solicitud incorrecta: "+String(e.message).slice(0,150),400);
      // Fail closed: no filtrar secretos o trazas al cliente.
      console.error("worker error",e?.name || "Error");
      return err("Error interno; revisar logs",500);
    }
  }
};
