// Editor guiado específico de Factor de Gigantes: ningún control certifica hechos automáticamente.
// El servidor vuelve a validar todo y exige acreditación humana aparte.
const kinds=["imagen","video","musica","voz","grafico"];
const states=["pendiente","verificada","rechazada"];
const rights=["pendiente","verificado","rechazado"];

export const cloneDossier = value => JSON.parse(JSON.stringify(value));

export function nextEditorialId(rows,prefix) {
  const used=new Set(rows.map(row=>row.id));
  for(let i=1;i<=999;i++) {
    const id=prefix+String(i).padStart(2,"0");
    if(!used.has(id))return id;
  }
  throw Error("Se alcanzó el máximo de identificadores de expediente");
}

export function addEditorialClaim(dossier,segmentIndex) {
  if(!Number.isInteger(segmentIndex) || segmentIndex < 1 || dossier.claims.length>=50)
    throw Error("No se puede añadir otra afirmación");
  const source=dossier.sources[0];
  if(!source)throw Error("Añade primero las fuentes documentales");
  const claim={
    id:nextEditorialId(dossier.claims,"C"),
    segment_index:segmentIndex,
    text:"Describe una afirmación concreta comprobable de esta escena.",
    evidence:[{source_id:source.id,locator:"Página o sección exacta pendiente",status:"pendiente"}],
    reviewed_by:""
  };
  dossier.claims.push(claim);
  return claim;
}
export function deleteEditorialClaim(dossier,id) {
  const i=dossier.claims.findIndex(c=>c.id===id);
  if(i<0)throw Error("Afirmación no encontrada");
  const segment=dossier.claims[i].segment_index;
  if(dossier.claims.filter(c=>c.segment_index===segment).length===1)
    throw Error("Cada escena necesita por lo menos una afirmación con evidencia");
  dossier.claims.splice(i,1);
}
export function addEditorialEvidence(dossier,claim) {
  if(claim.evidence.length>=5)throw Error("Máximo cinco evidencias por afirmación");
  const chosen=dossier.sources.find(s=>!claim.evidence.some(e=>e.source_id===s.id));
  if(!chosen)throw Error("No quedan fuentes diferentes disponibles");
  claim.evidence.push({source_id:chosen.id,locator:"Página o sección exacta pendiente",status:"pendiente"});
}
export function addEditorialAsset(dossier) {
  if(dossier.assets.length>=40)throw Error("Máximo cuarenta recursos por expediente");
  const asset={kind:"imagen",description:"Recurso audiovisual pendiente de acreditar",rights_status:"pendiente"};
  dossier.assets.push(asset);
  return asset;
}
export function deleteEditorialAsset(dossier,index) {
  const asset=dossier.assets[index];
  if(!asset)throw Error("Recurso inexistente");
  if(asset.kind==="voz" && dossier.assets.filter(a=>a.kind==="voz").length===1)
    throw Error("No puedes quitar la única voz declarada del documental");
  dossier.assets.splice(index,1);
}
export function deleteEditorialSource(dossier,id,manifestSources=[]) {
  const source=dossier.sources.find(s=>s.id===id);
  if(!source)throw Error("Fuente no encontrada");
  if(manifestSources.includes(source.url))
    throw Error("La fuente pertenece al guion; edítala desde el borrador");
  if(dossier.claims.some(c=>c.evidence.some(e=>e.source_id===id)))
    throw Error("Esta fuente está vinculada a una afirmación; desvincúlala primero");
  dossier.sources=dossier.sources.filter(s=>s.id!==id);
}

function node(tag,css="",text="") {
  const element=document.createElement(tag);
  if(css)element.className=css;
  if(text)element.textContent=text;
  return element;
}
function textField(parent,title,value,onChange,{multiline=false,readonly=false,type="text",hint=""}={}) {
  const wrapper=node("label","editorial-field");
  wrapper.append(node("span","",title));
  const control=node(multiline?"textarea":"input");
  if(!multiline)control.type=type;
  else control.rows=3;
  control.value=value??"";
  control.disabled=readonly;
  if(hint)control.placeholder=hint;
  control.addEventListener("input",()=>onChange(control.value));
  wrapper.append(control);
  parent.append(wrapper);
  return control;
}
function choice(parent,title,value,options,onChange,readonly) {
  const wrapper=node("label","editorial-field");
  wrapper.append(node("span","",title));
  const control=node("select");
  const existing=options.map(o=>typeof o==="string"?{value:o,label:o}:o);
  if(!existing.some(o=>o.value===value))
    existing.unshift({value,label:"Fuente no encontrada: "+value});
  for(const option of existing) {
    const el=node("option","",option.label);
    el.value=option.value;
    control.append(el);
  }
  control.value=value;
  control.disabled=readonly;
  control.addEventListener("change",()=>onChange(control.value));
  wrapper.append(control);
  parent.append(wrapper);
  return control;
}
function button(parent,label,fn,readonly=false) {
  const el=node("button","secondary",label);
  el.type="button";
  el.disabled=readonly;
  el.addEventListener("click",fn);
  parent.append(el);
  return el;
}
function group(root,title,help) {
  const section=node("section","editorial-group");
  section.append(node("h3","",title));
  if(help)section.append(node("p","muted",help));
  root.append(section);
  return section;
}
function editorCard(root,title,detail) {
  const article=node("article","editorial-record");
  article.append(node("strong","",title));
  if(detail)article.append(node("p","muted",detail));
  root.append(article);
  return article;
}
function action(fn,notify) {
  try {fn();} catch(e) {notify(e.message);}
}

/** Mantiene un borrador en memoria; no persiste nada sin "Guardar expediente". */
export function mountEditorialEditor(root,initial,{editable=true,manifest,notify=()=>{}}) {
  const dossier=cloneDossier(initial);
  let isEditable=editable;
  const manifestSources=(manifest?.sources||[]).map(s=>typeof s==="string"?s:s.url);
  const segments=manifest?.segments||[];

  function draw() {
    root.replaceChildren();
    const general=group(root,"Enfoque editorial","Los campos no equivalen a verificación de hechos.");
    textField(general,"Título de investigación",dossier.title,v=>{dossier.title=v},{readonly:!isEditable});
    textField(general,"Tesis y pregunta del documental",dossier.thesis,v=>{dossier.thesis=v},
      {multiline:true,readonly:!isEditable});

    const sources=group(root,"1 · Fuentes documentales","Identifica la entidad publicadora y la fecha. Los enlaces deben llevar a materiales consultados realmente.");
    for(const source of dossier.sources) {
      const item=editorCard(sources,source.id,"Documento o registro empleado en la investigación");
      textField(item,"URL HTTPS",source.url,v=>{source.url=v},{readonly:!isEditable,type:"url"});
      textField(item,"Entidad publicadora",source.publisher,v=>{source.publisher=v},{readonly:!isEditable});
      textField(item,"Fecha de consulta",source.accessed_on,v=>{source.accessed_on=v},{readonly:!isEditable,type:"date"});
      choice(item,"Tipo",source.type,["primaria","secundaria"],v=>{source.type=v},!isEditable);
      button(item,"Quitar fuente",()=>action(()=>{deleteEditorialSource(dossier,source.id,manifestSources);draw()},notify),!isEditable);
    }
    button(sources,"+ Añadir otra fuente",()=>action(()=>{
      if(dossier.sources.length>=30)throw Error("Máximo 30 fuentes");
      dossier.sources.push({id:nextEditorialId(dossier.sources,"S"),url:"https://",
        publisher:"Por identificar",accessed_on:new Date().toISOString().slice(0,10),type:"secundaria"});
      draw();
    },notify),!isEditable);

    const claims=group(root,"2 · Afirmaciones comprobables","Cada escena necesita su propia evidencia. No cambies una evidencia a «verificada» hasta leer y cotejar la fuente.");
    for(let segmentIndex=1;segmentIndex<=segments.length;segmentIndex++) {
      const segment=segments[segmentIndex-1];
      const section=editorCard(claims,"Escena "+segmentIndex+" · "+segment.headline,
        "Guion: "+segment.voiceover.slice(0,220));
      for(const claim of dossier.claims.filter(c=>c.segment_index===segmentIndex)) {
        const block=node("div","editorial-claim");
        block.append(node("strong","",claim.id));
        textField(block,"Afirmación a demostrar",claim.text,v=>{claim.text=v},
          {multiline:true,readonly:!isEditable});
        for(const evidence of claim.evidence) {
          const evidenceRow=node("div","editorial-evidence");
          choice(evidenceRow,"Fuente",evidence.source_id,
            dossier.sources.map(s=>({value:s.id,label:s.id+" · "+s.publisher})),
            v=>{evidence.source_id=v},!isEditable);
          textField(evidenceRow,"Página / sección / localizador",evidence.locator,v=>{evidence.locator=v},
            {readonly:!isEditable});
          choice(evidenceRow,"Verificación",evidence.status,states,v=>{evidence.status=v},!isEditable);
          button(evidenceRow,"Quitar evidencia",()=>action(()=>{
            if(claim.evidence.length===1)throw Error("La afirmación necesita una evidencia como mínimo");
            claim.evidence=claim.evidence.filter(e=>e!==evidence);draw();
          },notify),!isEditable);
          block.append(evidenceRow);
        }
        button(block,"+ Añadir evidencia",()=>action(()=>{addEditorialEvidence(dossier,claim);draw()},notify),!isEditable);
        textField(block,"Quién verificó esta afirmación",claim.reviewed_by||"",
          v=>{claim.reviewed_by=v},{readonly:!isEditable,hint:"Nombre del responsable editorial"});
        button(block,"Quitar afirmación",()=>action(()=>{deleteEditorialClaim(dossier,claim.id);draw()},notify),!isEditable);
        section.append(block);
      }
      button(section,"+ Añadir afirmación de esta escena",()=>action(()=>{
        addEditorialClaim(dossier,segmentIndex);draw();
      },notify),!isEditable);
    }

    const assets=group(root,"3 · Recursos y licencias",
      "La voz oficial, imágenes, música, clips y gráficos utilizados deben tener procedencia y permisos comprobados.");
    dossier.assets.forEach((asset,index)=>{
      const a=editorCard(assets,"Recurso "+(index+1),"No marques licencia verificada por suposiciones.");
      choice(a,"Tipo",asset.kind,kinds,v=>{asset.kind=v},!isEditable);
      textField(a,"Descripción y procedencia",asset.description,v=>{asset.description=v},
        {multiline:true,readonly:!isEditable});
      choice(a,"Derechos",asset.rights_status,rights,v=>{asset.rights_status=v},!isEditable);
      button(a,"Quitar recurso",()=>action(()=>{deleteEditorialAsset(dossier,index);draw()},notify),!isEditable);
    });
    button(assets,"+ Añadir recurso audiovisual",()=>action(()=>{addEditorialAsset(dossier);draw()},notify),!isEditable);
    root.append(node("p","muted","Guardar el formulario no aprueba los hechos, licencias ni el video. La acreditación exige confirmación humana."));
  }

  draw();
  return {
    getValue:()=>cloneDossier(dossier),
    setEditable:value=>{isEditable=Boolean(value);draw();}
  };
}
