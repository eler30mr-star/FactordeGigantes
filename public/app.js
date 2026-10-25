import {mountChannelControl} from './channel-control.js';
import {mountEpisodeWorkbench} from './episode-workbench.js';
import {mountEditorialEditor} from "./dossier-editor.js";
import {mountYoutubeReviews} from './youtube-review.js';
let adminToken = "";
let researchPaused = true;
let productionRunId = null;
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
  if (!response.ok) { const error=Error(data.error || "Error HTTP "+response.status); error.status=response.status; throw error; }
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
    if (j.status==="failed") actions.append(actionButton("Reintentar montaje","retry-render"),actionButton("Rehacer guion","request-changes"));
    if (["queued","rendering"].includes(j.status)) actions.append(tag("span","muted","Render en curso. Ver GitHub Actions."));
    if (j.status==="ready") actions.append(tag("span","muted","Prueba disponible en GitHub Actions. No publicada."));
    if(j.status==='ready'){
      const open=tag('button','secondary','Abrir exportación');open.type='button';
      open.addEventListener('click',async()=>{
        try{
          const detail=await request('/api/jobs/'+encodeURIComponent(j.id));
          const url=detail.preview?.run_url;
          if(!url || !/^https:\/\/github\.com\/eler30mr-star\/FactordeGigantes\/actions\/runs\/[0-9]+$/.test(url)){
            notice('Consulta los artefactos de esta prueba en GitHub Actions.');return;
          }
          const link=tag('a','','Ver video y archivos de revisión');link.href=url;link.target='_blank';link.rel='noopener noreferrer';
          open.replaceWith(link);
        }catch(e){notice(e.message);}
      });
      actions.append(open);
    }
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
    data.research_paused ? "Investigadores: pausados durante el desarrollo" : data.research_prerequisites_present ?
      "Investigación: requisitos locales presentes" : "Investigación: requisitos incompletos",
    "Publicación en YouTube: no autorizada"
  ];
  $("system-status").textContent=parts.join(" · ");
}
function productionLink(label,url){
  if(typeof url!=='string'||!/^https:\/\/github\.com\/eler30mr-star\/FactordeGigantes\/actions\/runs\/\d+(?:\/artifacts\/\d+)?$/.test(url))throw Error('Enlace de producción inválido');
  const a=tag('a','',label);a.href=url;a.target='_blank';a.rel='noopener noreferrer';return a;
}
function productionState(stage){
  if(stage.conclusion==='success')return 'Completado';
  if(stage.conclusion==='skipped')return 'No requerido';
  if(stage.status==='completed')return 'Interrumpido: '+String(stage.conclusion||'revisar');
  return stage.status==='in_progress'?'En proceso':'En espera';
}
async function showProductionRun(id){
  productionRunId=id;
  const root=$('production-detail');root.replaceChildren(tag('p','muted','Consultando escenas y archivos…'));
  try{
    const data=await request('/api/production/runs/'+encodeURIComponent(id));
    if(productionRunId!==id)return;
    root.replaceChildren(tag('h3','',data.run.title));
    root.append(tag('p','muted','Preparación: '+productionState(data.preparation)+' · Montaje: '+productionState(data.assembly)));
    if(data.narration.total){
      const n=data.narration;
      root.append(tag('p','','Narración: '+n.completed+' de '+n.total+' escenas completadas'+(n.failed?' · '+n.failed+' pendientes de reintento':'')));
      const list=tag('ul','','');
      for(const scene of n.scenes)list.append(tag('li','','Escena '+Number(scene.scene.slice(2))+': '+productionState(scene)));
      root.append(list);
    }
    for(const result of data.results){
      const p=tag('p','','');p.append(productionLink('Descargar: '+result.label,result.download_url));
      p.append(tag('span','muted',' · '+(result.size_bytes/1e6).toFixed(1)+' MB'+(result.expires_at?' · disponible hasta '+new Date(result.expires_at).toLocaleDateString('es'):'')));
      root.append(p);
    }
    if(!data.results.length)root.append(tag('p','muted',data.run.status==='completed'?'Todavía no hay una exportación válida disponible. Revisa la ejecución.':'La descarga aparecerá cuando el montaje termine correctamente.'));
    root.append(productionLink('Ver ejecución completa',data.run.run_url));
    $('production-status').textContent='Última consulta: '+new Date().toLocaleTimeString('es')+'. Publicación en YouTube no autorizada.';
  }catch(e){if(productionRunId===id){root.replaceChildren();$('production-status').textContent=e.message;}}
}
async function loadProductionRuns(){
  const data=await request('/api/production/runs');
  const root=$('production-runs');root.replaceChildren();
  if(!data.runs.length){productionRunId=null;$('production-detail').replaceChildren();$('production-status').textContent='Aún no hay episodios en producción.';return;}
  for(const run of data.runs){
    const button=tag('button','secondary',run.title+' · '+new Date(run.created_at).toLocaleString('es')+' · '+productionState(run));button.type='button';
    button.addEventListener('click',()=>showProductionRun(run.id));root.append(button);
  }
  const selected=data.runs.find(r=>r.id===productionRunId)||data.runs[0];
  await showProductionRun(selected.id);
}
$('production-refresh').addEventListener('click',async()=>{
  const button=$('production-refresh');button.disabled=true;
  try{await loadProductionRuns();}catch(e){$('production-status').textContent=e.message;}finally{button.disabled=false;}
});
async function loadYoutubeConnection(){
  const data=await request('/api/youtube/connection');
  const status=$('youtube-connection-status');
  status.textContent=data.connected?'Conexión registrada: '+data.channel.title+' · '+data.channel.id+'. No hay publicación automática.':
    !data.configured?'Pendiente de configurar el cliente OAuth del canal. La clave del estudio de YouTube no sustituye esta conexión.':
    data.last_connection_result==='channel_mismatch'?'Google devolvió otro canal. Conecta la cuenta que administra el canal configurado.':'Canal todavía sin conectar.';
  $('youtube-connect').disabled=!data.configured;
  $('youtube-publication-access').hidden=!data.connected||data.publication_scope_granted===true;
  $('youtube-disconnect').hidden=!data.connection_stored;
  $('youtube-connection-config').textContent=(data.missing.length?'Faltan: '+data.missing.join(', ')+'. ':'Configuración presente. ')+
    'URL de retorno para Google: '+data.callback_url;
}
async function loadYoutubeReviews(){
  const data=await request('/api/youtube/exports');
  mountYoutubeReviews($('youtube-review-results'),data.exports,{request,notify:notice,refresh:loadYoutubeReviews,
    fetchArchive:(path,options)=>fetch(path,{...options,headers:{Authorization:'Bearer '+adminToken}})});
  $('youtube-review-status').textContent=data.exports.length+' exportaciones registradas. La revisión y la subida privada son acciones separadas.';
}
async function openEpisodeExport(id){
  const data=await request('/api/youtube/exports/'+encodeURIComponent(id));
  mountYoutubeReviews($('youtube-review-results'),[data.export],{request,notify:notice,refresh:()=>openEpisodeExport(id),
    fetchArchive:(path,options)=>fetch(path,{...options,headers:{Authorization:'Bearer '+adminToken}})});
  $('youtube-review-status').textContent='Revisión del video del episodio elegido.';
  $('youtube-review-results').scrollIntoView({behavior:'smooth'});
}
$('youtube-review-refresh').addEventListener('click',()=>loadYoutubeReviews().catch(e=>{$('youtube-review-status').textContent=e.message;}));
$('youtube-connection-refresh').addEventListener('click',()=>loadYoutubeConnection().catch(e=>{$('youtube-connection-status').textContent=e.message;}));
$('youtube-publication-access').addEventListener('click',async()=>{
  const button=$('youtube-publication-access');button.disabled=true;
  try{const result=await request('/api/youtube/connect','POST',{confirmed:true,publication_access:true});
    window.location.assign(result.authorization_url);
  }catch(e){$('youtube-connection-status').textContent=e.message;button.disabled=false;}
});
$('youtube-connect').addEventListener('click',async()=>{
  const button=$('youtube-connect');button.disabled=true;
  try{
    const data=await request('/api/youtube/connect','POST',{confirmed:true});
    const url=new URL(data.authorization_url);
    if(url.origin!=='https://accounts.google.com'||url.pathname!=='/o/oauth2/v2/auth')throw Error('URL de autorización inválida');
    window.location.assign(url.href);
  }catch(e){$('youtube-connection-status').textContent=e.message;button.disabled=false;}
});
$('youtube-disconnect').addEventListener('click',async()=>{
  const button=$('youtube-disconnect');button.disabled=true;
  try{
    const result=await request('/api/youtube/disconnect','POST',{confirmed:true});
    await loadYoutubeConnection();
    if(!result.revocation_confirmed)notice('Credenciales eliminadas del sistema. Revisa también el acceso de la aplicación en tu cuenta Google.');
  }catch(e){$('youtube-connection-status').textContent=e.message;}finally{button.disabled=false;}
});
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
  researchPaused=data.research_paused===true;
  $("research-start").disabled=researchPaused;
  const container=$("research-history");
  container.replaceChildren();
  if(!data.requests.length) container.append(tag("p","muted","Sin investigaciones solicitadas aún."));
  for(const item of data.requests) container.append(researchRow(item));
  $("research-status").textContent=(researchPaused?"Investigadores pausados hasta la prueba final integrada. ":"")+"Solicitudes registradas: "+data.requests.length+
    (data.run_lookup==="checked" ? ". Estados consultados en GitHub Actions; los registros sin ejecución asociada siguen pendientes de comprobar." :
    data.run_lookup==="unavailable" ? ". GitHub no respondió o faltan permisos de lectura; consulta Actions directamente." :
    ". Pulsa «Actualizar» para consultar las ejecuciones.");
}
// Visualizar exclusivamente observaciones D1 con su procedencia; sin declarar ganador.
async function loadAiTeam(){
  const data=await request('/api/market/ai-pipeline');
  if(!Array.isArray(data.runs))throw Error('No se pudo consultar el equipo de investigación');
  const root=$('ai-team-results');root.replaceChildren();
  const latest=data.runs[0],report=latest?.report;
  $('ai-team-status').textContent=report?
    `${report.company||'Sin selección'} · pasajes: ${report.evidence_manifest.length} · afirmaciones candidatas: ${report.candidate_claims.length} · revisiones: ${report.reviews.length} · hechos aprobados: 0`:
    'Todavía no hay una ejecución registrada del equipo.';
  if(!report)return;
  const statuses={success:'Ejecutado',missing_key:'Falta configurar la clave',
    free_mode_unconfirmed:'Falta confirmar modalidad gratuita',not_needed:'Alternativa no necesaria',
    not_selected:'No seleccionado',not_configured:'Sin configurar',budget_denied:'Límite de uso alcanzado',
    quota_exhausted:'Cuota del proveedor agotada',credentials_rejected:'El proveedor rechazó el acceso',
    source_unavailable:'Fuente no disponible',no_evidence:'Sin pasajes documentales',no_claims:'Sin afirmaciones para revisar',
    no_candidate_claims:'Sin afirmaciones útiles',invalid_output:'Respuesta no válida',local_failure:'Falló la extracción local',
    provider_failure:'Falló el proveedor',network_failure:'Fallo de conexión',disabled:'Desactivado'};
  const roles={discover:'Descubrimiento',classify:'Clasificación',extract:'Extracción local',
    analyze:'Análisis',review:'Revisión',fallback:'Alternativa'};
  for(const stage of report.stages){
    const row=tag('article','job','');
    row.append(tag('strong','',`${stage.provider} · ${roles[stage.role]||stage.role}`),
      tag('p','muted',statuses[stage.status]||stage.status));root.append(row);
  }
  if(report.source_quality){
    const q=report.source_quality;
    const note=tag('article','job','');
    note.append(tag('strong','','Cobertura y corroboración documental'),
      tag('p','muted',
        'Documentos: '+String(q.unique_documents)+
        ' · dominios distintos: '+String(q.independent_domains)+
        ' · dominios regulatorios: '+String(q.regulatory_primary_domains)+
        ' · afirmaciones que requieren contraste: '+String(q.claims_requiring_review)));
    note.append(tag('small','',
      'Varias citas del mismo documento no constituyen corroboración independiente. '+
      'Ninguna coincidencia entre modelos verifica automáticamente los hechos.'));
    root.append(note);
  }
  for(const e of report.evidence_manifest){
    const row=tag('article','job','');
    row.append(tag('strong','',`Fuente ${e.id}${e.page?' · página '+e.page:''}`),tag('p','muted',e.excerpt));
    try{const u=new URL(e.url);if(u.protocol==='https:'){
      const link=tag('a','news-link','Abrir documento original');link.href=u.href;
      link.target='_blank';link.rel='noopener noreferrer';row.append(link);
    }}catch{/* el servidor también valida la URL */}
    root.append(row);
  }
  for(const [index,c] of report.candidate_claims.entries()){
    const row=tag('article','job','');
    row.append(tag('strong','',`Afirmación candidata ${index+1}`),tag('p','muted',c.statement),
      tag('small','',`Citas: ${c.evidence_ids.join(', ')} · pendiente de verificación`));
    const review=report.reviews.find(r=>r.claim_index===index+1);
    if(review)row.append(tag('p','muted','Observación del revisor: '+review.reason));
    root.append(row);
  }
  if(data.budgets?.length)root.append(tag('p','muted','Reservas de uso del mes: '+
    data.budgets.map(b=>`${b.provider}: ${b.reserved_requests}`).join(' · ')+
    '. Incluyen intentos fallidos; no acreditan la facturación de la cuenta.'));
}
$('ai-team-refresh').addEventListener('click',()=>loadAiTeam().catch(e=>{
  $('ai-team-status').textContent=e.message;
}));
async function loadMarketResearch() {
  const data=await request("/api/market/research?limit=20");
  if(!Array.isArray(data.runs)||!Array.isArray(data.evidence)||
     !Array.isArray(data.claims)||!Array.isArray(data.citations)||
     !Array.isArray(data.questions))throw Error("Expediente investigador incompleto");
  const root=$("market-research-results");
  root.replaceChildren();
  const latest=data.runs[0];
  $("market-research-status").textContent="Ejecuciones: "+data.runs.length+
    " · fuentes: "+data.evidence.length+" · afirmaciones candidatas: "+data.claims.length+
    " · preguntas pendientes: "+data.questions.length+" · hechos aprobados: 0"+
    (latest?" · estado: "+String(latest.status):"");
  if(!latest){
    root.append(tag("p","empty","No existe aún un expediente del investigador. No se ha inventado ningún resultado de IA."));
    return;
  }
  if(latest.status!=="candidate_claims_generated")
    root.append(tag("p","muted","El investigador no generó afirmaciones: "+String(latest.status)+
      ". Puede haber fuentes recopiladas, pero la ejecución requiere permisos gratuitos aprobados."));
  for(const e of data.evidence){
    const el=tag("article","job","");
    const heading=tag("div","jobtop","");
    heading.append(tag("strong","",String(e.company||e.wikidata_id)),
       tag("span","tag",String(e.evidence_id)));
    el.append(heading);
    el.append(tag("p","muted","Tipo: "+String(e.source_kind)+
      " · ubicación: "+(e.pdf_page==null?"Página web corporativa":"PDF página "+e.pdf_page)+
      " · SHA-256: "+String(e.document_sha256)));
    el.append(tag("p","muted",String(e.excerpt||"")));
    try{
      const u=new URL(String(e.source_url||""));
      if(u.protocol==="https:"){
        const link=tag("a","news-link","Abrir fuente citada");
        link.href=u.href;link.target="_blank";link.rel="noopener noreferrer";
        el.append(link);
      }
    }catch{/* no enlazar fuente inválida */}
    root.append(el);
  }
  for(const claim of data.claims){
    const el=tag("article","job","");
    el.append(tag("strong","","Afirmación candidata "+String(claim.claim_index)));
    const supporting=data.citations.filter(c=>Number(c.claim_index)===Number(claim.claim_index))
      .map(c=>String(c.evidence_id)).join(", ");
    el.append(tag("p","muted",String(claim.statement||"")));
    el.append(tag("small","", "Citas: "+supporting+
      " · comprobación numérica: "+String(claim.numeric_support_state)+
      " · estado: pendiente de verificación"));
    root.append(el);
  }
  for(const question of data.questions){
    const el=tag("article","job","");
    el.append(tag("strong","","Pregunta pendiente "+String(question.question_index)));
    el.append(tag("p","muted",String(question.question||"")));
    root.append(el);
  }
}
async function loadResearchQueue(){
  const data=await request('/api/market/research-queue');
  if(!Array.isArray(data.queue))throw Error('No se pudo consultar la selección');
  const active=data.queue.find(q=>q.state!=='closed');
  const states={awaiting_sources:'Buscando fuentes',researching:'Investigando',review:'En revisión'};
  $('research-queue-status').textContent=active?
    active.title+' · '+(states[active.state]||'Pendiente de investigación'):
    'Todavía no hay un tema con señales suficientes para investigar.';
  const root=$('research-queue-results');root.replaceChildren();
  const ranking=data.latest_selection?.rankings||[];
  const labels={need_two_recent_youtube_region_samples:'Faltan dos muestras recientes de YouTube',
    need_three_videos_and_two_channels:'Faltan videos o diversidad de canales',
    need_recent_wikipedia_window:'Falta una señal independiente reciente'};
  const numbers=new Intl.NumberFormat('es',{maximumFractionDigits:2});
  for(const item of ranking.filter(x=>x.eligible_for_research||x.youtube_unique_videos).slice(0,10)){
    const card=tag('article','job',''),head=tag('div','jobtop','');
    head.append(tag('strong','',String(item.title)),tag('span','tag',
      item.wikidata_id===active?.wikidata_id?'En investigación':
      item.eligible_for_research?'Candidato medido':'Faltan datos'));
    card.append(head);
    card.append(tag('p','muted',
      'Prioridad comparativa: '+(item.market_score===null?'pendiente':numbers.format(item.market_score)+'/100')+
      ' · videos distintos: '+String(item.youtube_unique_videos)+
      ' · canales: '+String(item.youtube_distinct_channels)+
      ' · mediana de vistas por día de antigüedad: '+(item.median_daily_views===null?'sin muestra':numbers.format(item.median_daily_views))));
    if(item.reasons?.length)card.append(tag('p','muted',item.reasons.map(r=>labels[r]||'Se requieren más datos').join(' · ')));
    root.append(card);
  }
}
$('research-queue-refresh').addEventListener('click',()=>loadResearchQueue().catch(e=>{
  $('research-queue-status').textContent=e.message;
}));
$("market-research-refresh").addEventListener("click",()=>loadMarketResearch().catch(e=>{
  $("market-research-status").textContent=e.message;
}));
async function loadPdfEvidence() {
  const report=await request("/api/market/pdf?limit=20");
  if(!Array.isArray(report.documents)||!Array.isArray(report.fragments)||!Array.isArray(report.runs))
    throw Error("Evidencia PDF incompleta");
  const root=$("pdf-results");
  root.replaceChildren();
  $("pdf-status").textContent="Informes rastreados: "+report.documents.length+
    " · fragmentos paginados: "+report.fragments.length+
    " · afirmaciones verificadas: 0.";
  if(!report.documents.length) {
    root.append(tag("p","empty","No se han encontrado enlaces PDF corporativos elegibles. No se inventan informes ni citas."));
    return;
  }
  for(const doc of report.documents) {
    const el=tag("article","job","");
    const title=tag("div","jobtop","");
    title.append(tag("strong","",String(doc.company||doc.wikidata_id)),
      tag("span","tag","Sin corroborar"));
    el.append(title);
    el.append(tag("p","muted","Estado: "+String(doc.state)+
      " · páginas: "+String(doc.pages_total??"Sin lectura")+
      " · SHA-256: "+String(doc.sha256||"Sin archivo")));
    try {
      const u=new URL(String(doc.document_url||""));
      if(u.protocol==="https:") {
        const link=tag("a","news-link","Consultar documento de referencia");
        link.href=u.href;link.target="_blank";link.rel="noopener noreferrer";
        el.append(link);
      }
    }catch{/* Ignorar enlace inválido */}
    const related=report.fragments.filter(f=>f.wikidata_id===doc.wikidata_id&&
      f.document_url===doc.document_url).slice(0,5);
    for(const fragment of related){
      el.append(tag("small","",String(fragment.locator||"Página sin localizar")));
      el.append(tag("p","muted",String(fragment.excerpt||"")));
    }
    root.append(el);
  }
}
$("pdf-refresh").addEventListener("click",()=>loadPdfEvidence().catch(e=>{
  $("pdf-status").textContent=e.message;
}));
async function loadOfficialEvidence() {
  const data=await request("/api/market/official?limit=20");
  if(!Array.isArray(data.runs)||!Array.isArray(data.items))
    throw Error("Fuentes corporativas inválidas");
  const root=$("official-results");
  root.replaceChildren();
  $("official-status").textContent="Páginas candidatas registradas: "+data.items.length+
    " · hechos aprobados automáticamente: 0.";
  if(!data.items.length){
    root.append(tag("p","empty","El sistema todavía no ha recuperado páginas corporativas candidatas."));
    return;
  }
  for(const source of data.items){
    const card=tag("article","job","");
    const heading=tag("div","jobtop","");
    heading.append(tag("strong","",String(source.company||source.wikidata_id)),
      tag("span","tag","Fuente sin verificar"));
    card.append(heading);
    card.append(tag("p","muted","Estado: "+String(source.status)+
      " · bloques legibles: "+String(source.readable_blocks)+
      " · hash SHA-256: "+String(source.content_sha256||"Sin lectura")));
    try{
      const u=new URL(String(source.website_candidate||""));
      if(u.protocol==="https:"){
        const link=tag("a","news-link","Consultar sitio corporativo candidato");
        link.href=u.href;link.target="_blank";link.rel="noopener noreferrer";
        card.append(link);
      }
    }catch{/* No vincular URL inválida */}
    root.append(card);
  }
}
$("official-refresh").addEventListener("click",()=>loadOfficialEvidence().catch(e=>{
  $("official-status").textContent=e.message;
}));
async function loadOpportunities() {
  const data=await request("/api/market/opportunities?limit=25");
  if(!Array.isArray(data.candidates)||!Array.isArray(data.runs))
    throw Error("El evaluador no devolvió datos verificables");
  const root=$("opportunities-results");
  root.replaceChildren();
  $("opportunities-status").textContent="Evaluaciones históricas: "+data.runs.length+
    " · empresas evaluadas: "+data.candidates.length+
    " · temas autorizados automáticamente: 0.";
  if(!data.candidates.length){
    root.append(tag("p","empty","Todavía no hay una evaluación guardada o las fuentes no produjeron empresas. No se creará un tema ficticio."));
    return;
  }
  for(const c of data.candidates){
    const row=tag("article","job","");
    const head=tag("div","jobtop","");
    head.append(tag("strong","",String(c.title||c.wikidata_id)),
      tag("span","tag","Evidencia insuficiente"));
    row.append(head);
    row.append(tag("small","",
       "ID Wikidata: "+String(c.wikidata_id)+
       " · titulares vinculados: "+String(c.news_mention_count)+
       " · ventanas Wikipedia: "+String(c.wiki_observation_count)+
       " · mercados YouTube medidos: "+String(c.youtube_region_samples)));
    try{
      const reasons=JSON.parse(String(c.reasons_json||"[]"));
      if(Array.isArray(reasons) && reasons.length)
        row.append(tag("p","muted",reasons.filter(r=>typeof r==="string").join(" · ")));
    }catch{row.append(tag("p","muted","Faltan fundamentos auditables para aprobar un documental."));}
    root.append(row);
  }
}
$("opportunities-refresh").addEventListener("click",()=>loadOpportunities().catch(e=>{
  $("opportunities-status").textContent=e.message;
}));
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
async function loadCrossSignals() {
  const data=await request("/api/market/cross?limit=25");
  if(!Array.isArray(data.links)||!Array.isArray(data.runs))
    throw Error("Respuesta de correlación incompleta");
  const root=$("cross-results");
  root.replaceChildren();
  $("cross-status").textContent="Corridas de cruce: "+data.runs.length+
    " · menciones candidatas: "+data.links.length+
    " · identidades y noticias originales por contrastar.";
  if(!data.links.length){
    root.append(tag("p","empty","Sin coincidencias textuales confirmables entre las empresas observadas y los titulares actuales. No se infieren relaciones."));
    return;
  }
  for(const link of data.links) {
    const el=tag("article","job","");
    const head=tag("div","jobtop","");
    head.append(tag("strong","",String(link.company||link.wikidata_id)),
      tag("span","tag","Coincidencia provisional"));
    el.append(head);
    el.append(tag("small","",String(link.source_label||"Medio atribuido")+
      " · "+String(link.published_at||"")));
    el.append(tag("p","muted",String(link.headline||"")));
    el.append(tag("p","micro muted","Término encontrado: "+String(link.matched_alias||"")+
      " · sin fuente original contrastada"));
    root.append(el);
  }
}
$("cross-refresh").addEventListener("click",()=>loadCrossSignals().catch(e=>{
  $("cross-status").textContent=e.message;
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
  if(researchPaused)return notice('Investigadores pausados durante el desarrollo.');
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
  }finally{btn.disabled=researchPaused;}
});

const episodeWorkbench=mountEpisodeWorkbench($('channel-progress'),{request,
 openDossier:async id=>{const data=await request('/api/jobs/'+encodeURIComponent(id));await openDossier(data.job);},
 openExport:openEpisodeExport,
 fetchArchive:(path,options)=>fetch(path,{...options,headers:{Authorization:'Bearer '+adminToken}}),
 refresh:()=>channelControl.load()});
const channelControl=mountChannelControl({request,onEpisode:episode=>episodeWorkbench.load(episode)});

$("connect").addEventListener("click",async () => {
  const proposed=$("token").value.trim();
  if (!proposed) return notice("Introduce el token ADMIN_TOKEN");
  adminToken=proposed; $("token").value="";
  try {
    await load();
    $("workspace").hidden=false;
    $("indicator").textContent="Conectado";
    notice("Conexión privada establecida");
    channelControl.load().catch(e=>{$('channel-status').textContent=e.message;});
    loadResearch().catch(e=>{$("research-status").textContent=e.message;});
    loadSystemStatus().catch(e=>{$("system-status").textContent=e.message;});
    loadProductionRuns().catch(e=>{$('production-status').textContent=e.message;});
    loadYoutubeConnection().catch(e=>{$('youtube-connection-status').textContent=e.message;});
    loadYoutubeReviews().catch(e=>{$('youtube-review-status').textContent=e.message;});

  } catch(e) { adminToken=""; $("workspace").hidden=true; notice(e.message);}
});
$('research-archive').addEventListener('toggle',()=>{
  if(!$('research-archive').open||!adminToken)return;
    loadMarket().catch(e=>{$("market-status").textContent=e.message;});
    loadOpportunities().catch(e=>{$("opportunities-status").textContent=e.message;});
    loadOfficialEvidence().catch(e=>{$("official-status").textContent=e.message;});
    loadPdfEvidence().catch(e=>{$("pdf-status").textContent=e.message;});
    loadMarketResearch().catch(e=>{$("market-research-status").textContent=e.message;});
    loadAiTeam().catch(e=>{$('ai-team-status').textContent=e.message;});
    loadResearchQueue().catch(e=>{$('research-queue-status').textContent=e.message;});
    loadNewsRadar().catch(e=>{$("news-status").textContent=e.message;});
    loadYoutubeMarket().catch(e=>{$("youtube-status").textContent=e.message;});
    loadCrossSignals().catch(e=>{$("cross-status").textContent=e.message;});
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

