const labels={review:'Pendiente de revisión',approved:'Revisión aprobada',queued:'Subida solicitada',initiating:'Iniciando sesión privada',
 uploading:'Transferencia privada en curso',uploaded:'Subido como privado',unknown:'Resultado incierto: revisar antes de repetir'};
const checks={watched_video:'He visto el video completo',voice_approved:'Apruebo la identidad, dicción y ritmo de la voz',
 facts_checked:'He contrastado las afirmaciones y sus fuentes',rights_verified:'He comprobado los derechos comerciales de voz y recursos',
 visuals_captions_approved:'Apruebo gráficos y subtítulos',metadata_approved:'He revisado título, descripción y audiencia'};
function el(name,text='',cls=''){const n=document.createElement(name);n.textContent=text;if(cls)n.className=cls;return n;}
function link(text,url){
 if(!/^https:\/\/(?:github\.com\/eler30mr-star\/FactordeGigantes\/actions\/runs\/\d+\/artifacts\/\d+|www\.youtube\.com\/watch\?v=[\w-]{11})$/.test(url))throw Error('Enlace inválido');
 const a=el('a',text);a.href=url;a.target='_blank';a.rel='noopener noreferrer';return a;
}
export function mountYoutubeReviews(root,rows,{request,notify,refresh}){
 root.replaceChildren();
 if(!rows.length){root.append(el('p','Todavía no hay exportaciones registradas para revisión.','muted'));return;}
 for(const row of rows){
  const card=el('article','','job');card.append(el('h3',row.title),el('p',labels[row.state]||row.state,'muted'));
  card.append(el('p',row.origin==='codex_development_research'?'Material de desarrollo preparado por Codex':'Borrador del guionista autónomo','muted micro'));
  card.append(link('Descargar video, guion y fuentes',row.source_url));
  if(row.video_url)card.append(link('Abrir video privado en YouTube',row.video_url));
  if(row.last_error)card.append(el('p',row.last_error,'muted'));
  if(['queued','uploading'].includes(row.state)){
   const b=el('button','Reanudar la misma subida','secondary');b.type='button';card.append(b);
   b.addEventListener('click',async()=>{b.disabled=true;try{await request('/api/youtube/exports/'+row.id+'/resume','POST',{confirmed:true});notify('Continuación solicitada para la misma sesión.');await refresh();}catch(e){notify(e.message);}finally{b.disabled=false;}});
  }
  if(row.state==='review'||row.state==='approved'){
   const form=el('form','','youtube-review-form'),m=row.metadata,fields={};
   const input=(label,name,value,kind='input')=>{const l=el('label',label),n=el(kind);n.name=name;n.value=value;n.required=true;l.append(n);form.append(l);fields[name]=n;return n;};
   input('Título', 'title',m.title).maxLength=100;
   const desc=input('Descripción y capítulos','description',m.description,'textarea');desc.rows=8;desc.maxLength=5000;
   const audience=input('Audiencia declarada','audience','','select');
   for(const [value,text] of [['','Selecciona una opción'],['false','Contenido general, no dirigido a niños'],['true','Dirigido a niños']]){const o=el('option',text);o.value=value;audience.append(o);}
   audience.value=typeof m.madeForKids==='boolean'?String(m.madeForKids):'';
   const reviewer=input('Responsable de la revisión','reviewer','');reviewer.minLength=3;reviewer.maxLength=80;
   const boxes={};for(const [name,label] of Object.entries(checks)){
    const l=el('label',label,'review-check'),b=el('input');b.type='checkbox';b.required=true;b.checked=false;l.prepend(b);form.append(l);boxes[name]=b;
   }
   form.append(el('p','La revisión se vincula a esta versión exacta del video. Guardarla no inicia una subida.','muted micro'));
   const save=el('button','Guardar revisión y metadatos');save.type='submit';form.append(save);
   form.addEventListener('submit',async event=>{
    event.preventDefault();if(!['true','false'].includes(audience.value))return notify('Declara la audiencia antes de aprobar.');
    save.disabled=true;
    try{
     await request('/api/youtube/exports/'+row.id+'/review','POST',{confirmed:true,reviewer:reviewer.value,
      ...Object.fromEntries(Object.entries(boxes).map(([k,b])=>[k,b.checked])),
      metadata:{...m,title:fields.title.value,description:desc.value,madeForKids:audience.value==='true',privacyStatus:'private'}});
     await refresh();notify('Revisión guardada. Puedes autorizar la subida privada por separado.');
    }catch(e){notify(e.message);}finally{save.disabled=false;}
   });
   if(row.state==='approved'){
    const upload=el('button','Subir como privado');upload.type='button';card.append(upload);
    upload.addEventListener('click',async()=>{upload.disabled=true;try{await request('/api/youtube/exports/'+row.id+'/upload','POST',{confirmed:true});await refresh();notify('Subida privada solicitada.');}catch(e){notify(e.message);}finally{upload.disabled=false;}});
    const details=el('details'),summary=el('summary','Revisar de nuevo o cambiar metadatos');details.append(summary,form);card.append(details);
    form.addEventListener('input',()=>{upload.disabled=true;});
   }else card.append(form);
  }
  root.append(card);
 }
}
