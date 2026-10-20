let adminToken = "";
let editingJobId = null;
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
    if (action === "approve" && !confirm("¿Has verificado hechos, licencias y guion? Se autorizará un render de prueba.")) return;
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