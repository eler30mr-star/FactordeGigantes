let adminToken = "";
let editingJobId = null;
let dossierJobId = null;
let dossierJobStatus = null;
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
  if (!data.summary) return "Expediente aún no guardado.";
  const s=data.summary;
  return "Afirmaciones verificadas: "+s.verified_claims+"/"+s.claim_count+
    ". Recursos con derechos pendientes: "+s.pending_assets+
    ". Revisión humana: "+(data.attested ? "confirmada" : "pendiente")+".";
}
async function openDossier(job) {
  dossierJobId=job.id; dossierJobStatus=job.status;
  const data=await request("/api/jobs/"+encodeURIComponent(job.id)+"/dossier");
  $("dossier-json").value=JSON.stringify(data.dossier || blankDossier(job),null,2);
  $("dossier-heading").textContent=job.title+" · "+(data.attested?"Revisado":"Revisión pendiente");
  $("dossier-status").textContent=dossierSummary(data);
  const editable=["draft","review"].includes(job.status);
  $("dossier-json").readOnly=!editable;
  $("dossier-save").disabled=!editable;
  $("dossier-attest").disabled=job.status!=="review" || !data.dossier || data.attested;
  $("dossier-panel").hidden=false;
  $("dossier-panel").scrollIntoView({behavior:"smooth"});
}
$("dossier-close").addEventListener("click",()=>{$("dossier-panel").hidden=true;dossierJobId=null;});
$("dossier-save").addEventListener("click",async () => {
  if (!dossierJobId || !["draft","review"].includes(dossierJobStatus)) return;
  try {
    const data=JSON.parse($("dossier-json").value);
    $("dossier-save").disabled=true;
    const saved=await request("/api/jobs/"+encodeURIComponent(dossierJobId)+"/dossier","PUT",data);
    $("dossier-status").textContent=dossierSummary(saved);
    $("dossier-attest").disabled=dossierJobStatus!=="review";
    notice("Expediente guardado. Guardar no equivale a verificar.");
  } catch(e) {notice(e.message);} finally {$("dossier-save").disabled=false;}
});
$("dossier-attest").addEventListener("click",async () => {
  if (!dossierJobId || dossierJobStatus!=="review") return;
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
$("connect").addEventListener("click",async () => {
  const proposed=$("token").value.trim();
  if (!proposed) return notice("Introduce el token ADMIN_TOKEN");
  adminToken=proposed; $("token").value="";
  try {
    await load();
    $("workspace").hidden=false;
    $("indicator").textContent="Conectado";
    notice("Conexión privada establecida");
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