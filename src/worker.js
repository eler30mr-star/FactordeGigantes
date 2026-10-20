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
  const text = await request.text();
  if (text.length > 250000) throw Error("Solicitud demasiado grande");
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
const dto = row => ({id:row.id, title:row.title, format:row.format, status:row.status,
   manifest:JSON.parse(row.manifest_json), review_note:row.review_note, last_error:row.last_error,
   created_at:row.created_at, updated_at:row.updated_at});
async function setStatus(env,id,status, action, extra = {}) {
  await env.DB.prepare("UPDATE jobs SET status=?, review_note=?,last_error=?, updated_at=datetime('now') WHERE id=?")
    .bind(status, extra.review_note ?? "", extra.last_error ?? "",id).run();
  await record(env,id,action,extra.review_note || extra.last_error || "");
}
async function handle(request,env) {
  const url = new URL(request.url);
  if (url.pathname === "/health" && request.method === "GET") return json({ok:true,product:"Factor de Gigantes",version:"0.1.0"});
  if (!url.pathname.startsWith("/api/")) return env.ASSETS.fetch(request);
  const parts=url.pathname.split("/").filter(Boolean);
  const method=request.method;
  const renderer=parts[1] === "renderer";
  if (!guard(request,env,renderer ? "RENDERER_TOKEN" : "ADMIN_TOKEN")) return err("Acceso no autorizado",401);
  if (!env.DB) return err("D1 no configurado",503);
  if (renderer) {
    if (parts[2] !== "jobs" || !parts[3]) return err("Ruta no encontrada",404);
    const id=parts[3];
    const row=await find(env,id);
    if (!row) return err("Trabajo inexistente",404);
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
  if (parts.length === 3 && method === "GET") {
    const e=await env.DB.prepare("SELECT action,note,created_at FROM events WHERE job_id=? ORDER BY id DESC LIMIT 40").bind(id).all();
    return json({job:dto(row),events:e.results});
  }
  if (parts.length !== 4 || method !== "POST") return err("Ruta no encontrada",404);
  const action=parts[3];
  if (action === "submit" && row.status === "draft") {
    await setStatus(env,id,"review","submitted_for_review"); return json({ok:true});
  }
  if (action === "approve" && row.status === "review") {
    const data=await parseBody(request);
    if (data.confirmed !== true) return err("Se requiere aprobación humana explícita");
    validateManifest(JSON.parse(row.manifest_json));
    await setStatus(env,id,"approved","approved_by_editor"); return json({ok:true});
  }
  if (action === "request-changes" && ["review","approved","failed"].includes(row.status)) {
    const data=await parseBody(request);
    const note=String(data.note || "").trim();
    if (note.length < 8 || note.length > 500) return err("Indica una razón de 8 a 500 caracteres");
    await setStatus(env,id,"draft","changes_requested",{review_note:note}); return json({ok:true});
  }
  if (action === "dispatch" && row.status === "approved") {
    if (!env.GITHUB_DISPATCH_TOKEN || !env.GITHUB_REPO) return err("Acceso GitHub sin configurar",503);
    const repo=env.GITHUB_REPO;
    if (!/^[\w.-]+\/[\w.-]+$/.test(repo)) return err("Repositorio GitHub inválido",503);
    const workflow=env.GITHUB_WORKFLOW || "render.yml";
    const endpoint="https://api.github.com/repos/"+repo+"/actions/workflows/"+encodeURIComponent(workflow)+"/dispatches";
    const response=await fetch(endpoint,{method:"POST",headers:{
      "Authorization":"Bearer "+env.GITHUB_DISPATCH_TOKEN, "Accept":"application/vnd.github+json",
      "X-GitHub-Api-Version":"2022-11-28","User-Agent":"FactorDeGigantes-Worker",
      "Content-Type":"application/json"
    },body:JSON.stringify({ref:"main", inputs:{job_id:id}})});
    if (!response.ok) return err("GitHub rechazó el render (HTTP "+response.status+")",502);
    await setStatus(env,id,"queued","render_dispatched"); return json({ok:true});
  }
  return err("Acción no válida para este estado",409);
}
export default {
  async fetch(request,env) {
    try { return await handle(request,env); }
    catch(e) {
      if (e instanceof SyntaxError || e instanceof TypeError || String(e.message).includes("Solicitud demasiado grande"))
        return err("Solicitud incorrecta: "+String(e.message).slice(0,150),400);
      // Fail closed: no filtrar secretos o trazas al cliente.
      console.error("worker error",e?.name || "Error");
      return err("Error interno; revisar logs",500);
    }
  }
};