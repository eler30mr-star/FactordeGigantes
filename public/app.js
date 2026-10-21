import {mountEditorialEditor} from "./dossier-editor.js";
let adminToken = "";
let editingJobId = null;
let dossierJobId = null;
let dossierJobStatus = null;
let dossierEditor = null;
let dossierDirty = false;
let dossierManifest = null;
const $ = id => document.getElementById(id);
function notice(message) { $("notice").textContent=message; $("notice").classList.add("active"); }
async function request(path, method = "GET", body) {
  const response = await fetch(path, {
    method, headers: {"Authorization":"Bearer "+adminToken, ...(body ? {"Content-Type":"application/json"} : {})},
    ...(body ? {body: JSON.stringify(body)} : {})
  });
  const data = await response.json();
  if (!response.ok) throw Error(data.error || "Error HTTP "+response.status);
  return data;
}
function tag(name, className, text) {
  const el=document.createElement(name);
  if (className) el.className=className;
  el.textContent=text;
  return el;
}
function actionButton(text, action) {
  const b=tag("button","secondary",text);
  b.type="button";
  b.addEventListener("click",async () => {
    if (action === "approve" && !confirm("¿Confirmas que el expediente guardado tiene evidencias y licencias revisadas? El siguiente paso será la autorización de un render de prueba.")) return;
    let body={};
    if(action === "approve") body={confirmed:true};
    if(action === "request-changes") {
      const reason=prompt("Indica el motivo de corrección (mínimo 8 caracteres):");
      if (!reason) return;
      body={note:reason};
    }
    try {
      b.disabled=true;
      const id=b.closest(".job").dataset.id;
      await request("/api/jobs/"+encodeURIComponent(id)+"/"+action,"POST",body);
      notice("Acción completada: "+action);
      await load();
    } catch(e) {notice(e.message);} finally {b.disabled=false;}
  });
  return b;
}

function blankDossier(job) {
  const sources = job.manifest.sources.map((url,i) => ({
    id:"S"+String(i+1).padStart(2,"0"), url,
    publisher:"Por identificar", accessed_on:new Date().toISOString().slice(0,10),
    type:"secundaria"
  }));
  return {
    title:job.title,
    thesis:(job.manifest.angle.length >= 25 ? job.manifest.angle : "Enfoque de investigación: "+job.manifest.angle),
    publication_authorized:false,
    sources,
    claims:job.manifest.segments.map((segment,i)=>({
      id:"C"+String(i+1).padStart(2,"0"),segment_index:i+1,
      text:segment.voiceover,
      evidence:[{source_id:"S01",locator:"Sección y página por identificar",status:"pendiente"}],
      reviewed_by:""
    })),
    assets:[{kind:"voz",description:"Voz del documental: derechos comerciales por comprobar",
      rights_status:"pendiente"}]
  };
}
function dossierSummary(data) {
  if (data.validation_error) return "Expediente requiere corrección: "+data.validation_error;
  if (!data.summary) return "Expediente aún no guardado.";
  const s=data.summary;
  return "Afirmaciones verificadas: "+s.verified_claims+"/"+s.claim_count+
    ". Recursos con derechos pendientes: "+s.pending_assets+
    ". Revisión humana: "+(data.attested ? "confirmada" : "pendiente")+".";
}
function setDossierDirty() {
  if (!["draft","review"].includes(dossierJobStatus)) return;
  dossierDirty=true;
  $("dossier-attest").disabled=true;
  $("dossier-status").textContent="Hay cambios sin guardar; guárdalos y revisa el estado antes de acreditar.";
}
function showDossierEditor(dossier, editable) {
  dossierEditor=mountEditorialEditor($("dossier-form"),dossier,{
    editable,manifest:dossierManifest,notify:notice,onChange:setDossierDirty
  });
  $("dossier-json").value=JSON.stringify(dossier,null,2);
}
async function openDossier(job) {
  if (dossierDirty && !confirm("Hay cambios sin guardar. ¿Descartarlos para abrir otro expediente?")) return;
  // Evitar que una respuesta antigua desplace otro expediente al cambiar de trabajo.
  const openingJobId=job.id;
  const data=await request("/api/jobs/"+encodeURIComponent(openingJobId)+"/dossier");
  dossierJobId=openingJobId; dossierJobStatus=job.status; dossierManifest=job.manifest;
  dossierDirty=false;
  const editable=["draft","review"].includes(job.status);
  showDossierEditor(data.dossier || blankDossier(job),editable);
  $("dossier-heading").textContent=job.title+" · "+(data.attested?"Revisado":"Revisión pendiente");
  $("dossier-status").textContent=dossierSummary(data);
  $("dossier-json").readOnly=!editable;
  $("dossier-import-json").disabled=!editable;
  $("dossier-save").disabled=!editable;
  $("dossier-attest").disabled=job.status!=="review" || !data.dossier || data.attested || !!data.validation_error;
  $("dossier-panel").hidden=false;
  $("dossier-panel").scrollIntoView({behavior:"smooth"});
}
$("dossier-close").addEventListener("click",()=>{
  if(dossierDirty && !confirm("Los cambios del expediente no se han guardado. ¿Descartarlos?"))return;
  $("dossier-panel").hidden=true;dossierJobId=null;dossierEditor=null;dossierDirty=false;
});
$("dossier-import-json").addEventListener("click",()=>{
  if (!dossierEditor || !["draft","review"].includes(dossierJobStatus))return;
  try {
    const data=JSON.parse($("dossier-json").value);
    if(!data || typeof data!=="object" || Array.isArray(data))throw Error("Se requiere un objeto JSON");
    showDossierEditor(data,true);
    setDossierDirty();
    notice("JSON importado al formulario. Revisa los cambios y guárdalos.");
  }catch(e){notice("No se pudo importar JSON: "+e.message);}
});
$("dossier-save").addEventListener("click",async () => {
  if (!dossierJobId || !["draft","review"].includes(dossierJobStatus)) return;
  try {
    const data=dossierEditor.getValue();
    $("dossier-save").disabled=true;
    const saved=await request("/api/jobs/"+encodeURIComponent(dossierJobId)+"/dossier","PUT",data);
    dossierDirty=false;
    $("dossier-json").value=JSON.stringify(data,null,2);
    $("dossier-status").textContent=dossierSummary(saved);
    $("dossier-attest").disabled=dossierJobStatus!=="review" || !saved.summary?.structurally_complete;
    notice("Expediente guardado. Guardar no equivale a verificar.");
  } catch(e) {notice(e.message);} finally {$("dossier-save").disabled=false;}
});
$("dossier-attest").addEventListener("click",async () => {
  if (!dossierJobId || dossierJobStatus!=="review" || dossierDirty) return;
  if(!confirm("¿Has leído las fuentes originales, verificado TODAS las afirmaciones y confirmado los derechos de cada recurso declarado?")) return;
  const reviewer=prompt("Identificación del responsable de la revisión editorial:");
  if(!reviewer) return;
  const button=$("dossier-attest"); button.disabled=true;
  try {
    const data=await request("/api/jobs/"+encodeURIComponent(dossierJobId)+"/dossier/attest","POST",
      {confirmed:true,reviewer:reviewer.trim()});
    $("dossier-status").textContent=dossierSummary(data);
    notice("Revisión editorial registrada. Aún se requiere aprobar el guion.");
    await load();
  } catch(e){notice(e.message);button.disabled=false;}
});

async function load() {
  const data=await request("/api/jobs");
  const jobs=data.jobs;
  $("total").textContent=jobs.length;
  $("review").textContent=jobs.filter(j=>j.status==="review").length;
  $("ready").textContent=jobs.filter(j=>j.status==="ready").length;
  const list=$("jobs"); list.replaceChildren();
  if (!jobs.length) {list.append(tag("p","empty","Sin trabajos. Crea un guion para comenzar."));return;}
  for(const j of jobs) {
    const card=tag("article","job","");
    card.dataset.id=j.id;
    const top=tag("div","jobtop","");
    top.append(tag("strong","",j.title),tag("span","tag",j.status));
    card.append(top,tag("small","",j.format==="short"?"Short 9:16":"Documental 16:9"));
    if(j.review_note) card.append(tag("p","muted","Correcciones: "+j.review_note));
    if(j.last_error) card.append(tag("p","muted","Error: "+j.last_error));
    const actions=tag("div","actions","");
    const evidence=tag("button","secondary","Fuentes y licencias");
    evidence.type="button";
    evidence.addEventListener("click",()=>openDossier(j).catch(e=>notice(e.message)));
    actions.append(evidence);
    if (j.status==="draft") {
      const edit=tag("button","secondary","Editar");
      edit.type="button";
      edit.addEventListener("click",()=>{
        editingJobId=j.id;
        $("title").value=j.manifest.title;
        $("angle").value=j.manifest.angle;
        $("format").value=j.manifest.format;
        $("sources").value=j.manifest.sources.join("\n");
        $("segments").value=j.manifest.segments.map(s=>s.headline+" | "+s.voiceover).join("\n");
        $("save").textContent="Actualizar borrador";
        $("create").scrollIntoView({behavior:"smooth"});
      });
      actions.append(edit,actionButton("Enviar a revisión","submit"));
    }
    if (j.status==="review") actions.append(actionButton("Aprobar","approve"),actionButton("Pedir cambios","request-changes"));
    if (j.status==="approved") actions.append(actionButton("Generar prueba","dispatch"),actionButton("Pedir cambios","request-changes"));
    if (j.status==="failed") actions.append(actionButton("Rehacer guion","request-changes"));
    if (["queued","rendering"].includes(j.status)) actions.append(tag("span","muted","Render en curso. Ver GitHub Actions."));
    if (j.status==="ready") actions.append(tag("span","muted","Prueba disponible en GitHub Actions. No publicada."));
    card.append(actions);list.append(card);
  }
}
// Diagnóstico privado de solo lectura. No interpreta un secreto presente como permiso válido.
async function loadSystemStatus() {
  const data=await request("/api/system/status");
  const missing=Object.entries(data.production_d1 || {})
    .filter(([,present])=>!present).map(([name])=>name);
  const parts=[
    data.database_complete ? "D1: tablas completas" : "D1: faltan "+missing.join(", "),
    data.github_repository_configured ? "Repositorio: correcto" : "Repositorio: revisar configuración",
    data.github_dispatch_secret_present ?
      "Token de despacho: presente (permisos sin comprobar)" : "Token de despacho: ausente",
    data.research_prerequisites_present ?
      "Investigación: requisitos locales presentes" : "Investigación: requisitos incompletos",
    "Publicación en YouTube: no autorizada"
  ];
  $("system-status").textContent=parts.join(" · ");
}
$("system-refresh").addEventListener("click",()=>loadSystemStatus().catch(e=>{
  $("system-status").textContent=e.message;
}));

// Investigación autónoma desde panel. El servidor impide duplicados y requiere token ADMIN.
function researchRow(item) {
  const article=tag("div","research-item","");
  const state={"sent":"Enviado a GitHub","reserved":"Solicitud reservada","unknown":"Envío incierto: revisar Actions","rejected":"Rechazado por GitHub"}[item.state] || item.state;
  article.append(tag("strong","",item.topic),tag("span","muted",state));
  if(item.run) {
    const runStatus=item.run.status==="queued" ? "En cola" :
      item.run.status==="in_progress" ? "Ejecutándose" :
      item.run.conclusion==="success" ? "Completado correctamente" :
      item.run.conclusion==="failure" ? "Finalizó con errores" :
      "Finalizado: "+String(item.run.conclusion || "sin conclusión");
    article.append(tag("span","muted","GitHub Actions: "+runStatus));
    const link=tag("a","","Ver ejecución y artefactos");
    link.href=item.run.url;
    link.target="_blank";
    link.rel="noopener noreferrer";
    article.append(link);
  } else if(item.state==="sent" || item.state==="unknown") {
    article.append(tag("small","muted","Sin ejecución vinculada todavía; verifica Actions si no aparece."));
  }
  article.append(tag("small","muted",item.created_at || ""));
  return article;
}
async function loadResearch(includeRuns=false) {
  const data=await request(includeRuns?"/api/research?runs=1":"/api/research");
  const container=$("research-history");
  container.replaceChildren();
  if(!data.requests.length) container.append(tag("p","muted","Sin investigaciones solicitadas aún."));
  for(const item of data.requests) container.append(researchRow(item));
  $("research-status").textContent="Solicitudes registradas: "+data.requests.length+
    (data.run_lookup==="checked" ? ". Estados consultados en GitHub Actions; los registros sin ejecución asociada siguen pendientes de comprobar." :
    data.run_lookup==="unavailable" ? ". GitHub no respondió o faltan permisos de lectura; consulta Actions directamente." :
    ". Pulsa «Actualizar» para consultar las ejecuciones.");
}
// Visualizar exclusivamente observaciones D1 con su procedencia; sin declarar ganador.
async function loadMarket() {
  const data=await request("/api/market/radar?limit=30");
  const container=$("market-results");
  container.replaceChildren();
  if(!Array.isArray(data.entities) || !Array.isArray(data.interest_windows) || !Array.isArray(data.runs))
    throw Error("Respuesta de radar incompleta");
  const latest=new Map();
  for(const w of data.interest_windows) {
    if(!latest.has(w.wikidata_id)) latest.set(w.wikidata_id,w);
  }
  $("market-status").textContent="Corridas persistidas mostradas: "+data.runs.length+
    " · Empresas: "+data.entities.length+
    " · Investigación YouTube: pendiente · Selección editorial automática: no autorizada.";
  if(!data.entities.length) {
    container.append(tag("p","empty","Todavía no hay candidatos medidos en la base de producción."));
    return;
  }
  const fmt=new Intl.NumberFormat("es-PE");
  for(const item of data.entities) {
    const row=tag("article","job","");
    const head=tag("div","jobtop","");
    head.append(tag("strong","",String(item.title||item.wikidata_id)),
                tag("span","tag","Señal Wikimedia"));
    row.append(head);
    row.append(tag("small","","ID: "+String(item.wikidata_id)+
      " · Última detección: "+String(item.last_seen||"Sin fecha")));
    const w=latest.get(item.wikidata_id);
    if(w) {
      const last=Number(w.views_last_7d),previous=Number(w.views_previous_7d);
      if(Number.isSafeInteger(last) && last>=0 && Number.isSafeInteger(previous) && previous>=0)
        row.append(tag("p","muted","Visitas al artículo: "+
          fmt.format(last)+" en los últimos 7 días medidos, frente a "+
          fmt.format(previous)+" en los 7 días anteriores. Serie cerrada: "+
          String(w.period_end||"Sin fecha")+" (no son vistas de YouTube)."));
    } else row.append(tag("p","muted","Sin una serie completa de 14 días verificable."));
    container.append(row);
  }
}
$("market-refresh").addEventListener("click",()=>loadMarket().catch(e=>{
  $("market-status").textContent=e.message;
}));
async function loadYoutubeMarket() {
  const result=await request("/api/market/youtube?limit=30");
  const root=$("youtube-results");
  root.replaceChildren();
  if(!Array.isArray(result.runs)||!Array.isArray(result.queries)) throw Error("Estudio YouTube incompleto");
  const observed=result.queries.filter(r=>r.evidence_state==="observed_sample");
  $("youtube-status").textContent="Corridas: "+result.runs.length+
    " · Comparaciones con muestra observada: "+observed.length+
    " · Datos privados de competidores y selección editorial: no disponibles.";
  if(!observed.length) {
    root.append(tag("p","empty","Aún no existen mediciones públicas YouTube persistidas. El sistema necesita clave de API y presupuesto gratuito expresamente habilitado; no simula resultados."));
    return;
  }
  const num=new Intl.NumberFormat("es-PE",{maximumFractionDigits:2});
  const sorted=[...observed].sort((a,b)=>
    Number(b.median_daily_views||0)-Number(a.median_daily_views||0));
  for(const entry of sorted.slice(0,30)){
    const row=tag("article","job","");
    const heading=tag("div","jobtop","");
    heading.append(tag("strong","",String(entry.topic||entry.wikidata_id)),
      tag("span","tag",String(entry.region||"Región desconocida")));
    row.append(heading);
    row.append(tag("p","muted",
      "Mediana de vistas por día de antigüedad en la muestra: "+
      num.format(Number(entry.median_daily_views||0))+
      " · videos medidos: "+String(entry.sample_size)+
      " · canales identificados: "+String(entry.distinct_channels)+
      " · observado: "+String(entry.observed_on)+
      " · sin verificación de fuentes primarias."));
    root.append(row);
  }
}
$("youtube-refresh").addEventListener("click",()=>loadYoutubeMarket().catch(e=>{
  $("youtube-status").textContent=e.message;
}));
async function loadNewsRadar() {
  const result=await request("/api/market/news?limit=30");
  const root=$("news-results");
  root.replaceChildren();
  if(!Array.isArray(result.leads)||!Array.isArray(result.runs)) throw Error("Noticias incompletas");
  $("news-status").textContent="Titulares recientes: "+result.leads.length+
    " · Consultas almacenadas: "+result.runs.length+
    " · Fuentes originales y demanda YouTube: sin verificar.";
  if(!result.leads.length){
    root.append(tag("p","empty","El radar todavía no ha registrado titulares recientes."));
    return;
  }
  const screening=Array.isArray(result.preliminary_screening)?result.preliminary_screening:[];
  const scoreById=new Map(screening.map(x=>[x.id,x]));
  const display=[...result.leads].sort((a,b)=>
    (scoreById.get(b.id)?.editorial_relevance_score??-1)-
    (scoreById.get(a.id)?.editorial_relevance_score??-1));
  for(const article of display) {
    const card=tag("article","job","");
    const head=tag("div","jobtop","");
    head.append(tag("strong","",String(article.headline||"Titular sin texto")),
      tag("span","tag",String(article.category||"noticia")));
    card.append(head);
    const review=scoreById.get(article.id);
    if(review) card.append(tag("small","",
      "Relevancia documental exploratoria: "+review.editorial_relevance_score+
      "/100 · motivos: "+(review.heuristic_reasons||[]).join(", ")+
      " · sin datos competitivos YouTube"));
    card.append(tag("small","",String(article.source_label||"Medio atribuido")+" · "+
      String(article.published_at||"Fecha no disponible")));
    const url=String(article.aggregator_url||"");
    try {
      const parsed=new URL(url);
      if(parsed.protocol==="https:" && parsed.hostname==="news.google.com") {
        const link=tag("a","news-link","Abrir referencia en Google Noticias");
        link.href=parsed.href;
        link.target="_blank";
        link.rel="noopener noreferrer";
        card.append(link);
      }
    } catch { /* URL defectuosa: no generar enlace */ }
    card.append(tag("p","muted micro","Titular informativo pendiente de contrastar; no constituye un documental aprobado."));
    root.append(card);
  }
}
$("news-refresh").addEventListener("click",()=>loadNewsRadar().catch(e=>{
  $("news-status").textContent=e.message;
}));
$("research-refresh").addEventListener("click",()=>loadResearch(true).catch(e=>{
  $("research-status").textContent=e.message;
}));
$("research-form").addEventListener("submit",async event=>{
  event.preventDefault();
  const topic=$("research-topic").value.trim();
  if (!topic) return;
  if (!confirm("¿Iniciar investigación IA de «"+topic+"»? Consume minutos de GitHub Actions. No publica contenido."))return;
  const btn=$("research-start");
  btn.disabled=true;
  try {
    const result=await request("/api/research","POST",{topic,confirmed:true});
    $("research-status").textContent=result.notice;
    notice("GitHub aceptó la solicitud de investigación. Consulta los resultados en Actions.");
    $("research-form").reset();
    await loadResearch(true);
  }catch(e){
    $("research-status").textContent=e.message;
    notice(e.message);
  }finally{btn.disabled=false;}
});

$("connect").addEventListener("click",async () => {
  const proposed=$("token").value.trim();
  if (!proposed) return notice("Introduce el token ADMIN_TOKEN");
  adminToken=proposed; $("token").value="";
  try {
    await load();
    $("workspace").hidden=false;
    $("indicator").textContent="Conectado";
    notice("Conexión privada establecida");
    loadResearch().catch(e=>{$("research-status").textContent=e.message;});
    loadSystemStatus().catch(e=>{$("system-status").textContent=e.message;});
    loadMarket().catch(e=>{$("market-status").textContent=e.message;});
    loadNewsRadar().catch(e=>{$("news-status").textContent=e.message;});
    loadYoutubeMarket().catch(e=>{$("youtube-status").textContent=e.message;});
  } catch(e) { adminToken=""; $("workspace").hidden=true; notice(e.message);}
});
$("refresh").addEventListener("click",()=>load().catch(e=>notice(e.message)));
$("create").addEventListener("submit",async e => {
  e.preventDefault();
  try {
    const raw=$("segments").value.split("\n").map(s=>s.trim()).filter(Boolean);
    const segments=raw.map(s=> {
      const i=s.indexOf("|");
      if (i === -1) throw Error("Cada segmento necesita «Título | Narración»");
      return {headline:s.slice(0,i).trim(),voiceover:s.slice(i+1).trim()};
    });
    const manifest={
      title:$("title").value,angle:$("angle").value,format:$("format").value,
      sources:$("sources").value.split("\n").map(s=>s.trim()).filter(Boolean),
      segments
    };
    if (editingJobId) {
      await request("/api/jobs/"+encodeURIComponent(editingJobId),"PUT",manifest);
    } else {
      await request("/api/jobs","POST",manifest);
    }
    editingJobId=null;
    $("save").textContent="Guardar borrador";
    $("create").reset();
    notice("Borrador guardado; necesita revisión y aprobación");
    await load();
  } catch(error) { notice(error.message); }
});