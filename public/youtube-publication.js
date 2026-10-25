export function mountPublication(root,row,{request,notify,documentRef=document}){
 const el=(name,text='')=>{const node=documentRef.createElement(name);node.textContent=text;return node;};
 const block=el('section'),status=el('p'),refresh=el('button','Comprobar publicación en YouTube');
 const form=el('form'),mode=el('select'),date=el('input'),reviewer=el('input'),consent=el('input'),submit=el('button','Autorizar publicación');
 refresh.type='button';submit.type='submit';date.type='datetime-local';date.required=false;date.hidden=true;
 reviewer.required=true;reviewer.minLength=3;reviewer.maxLength=80;consent.type='checkbox';consent.required=true;
 for(const [value,text] of [['public','Publicar ahora'],['scheduled','Programar fecha UTC']]){const option=el('option',text);option.value=value;mode.append(option);}
 mode.value='public';
 const label=(text,node)=>{const l=el('label',text);l.append(node);form.append(l);};
 label('Acción sobre el video privado revisado',mode);label('Fecha y hora UTC',date);label('Responsable',reviewer);
 label('Autorizo hacer público este video exacto, ahora o en la fecha indicada',consent);
 form.append(submit);block.append(el('h4','Publicación del canal'),status,form,refresh);root.append(block);
 let pending=null;
 async function load(){
  const r=await request('/api/youtube/exports/'+row.id+'/publication');
  const p=r.publication;
  if(p?.state==='failed')pending=null;
  status.textContent=p?({reserved:'Solicitud registrada; comprobar resultado',unknown:'Resultado incierto; comprobar antes de repetir',failed:'Google rechazó la operación',confirmed:p.mode==='scheduled'?'Programación confirmada: '+p.publish_at:'Publicación confirmada'}[p.state]||p.state):'Video privado. Publicar requiere esta autorización independiente.';
  form.hidden=!!p&&p.state!=='failed';
 }
 mode.addEventListener('change',()=>{date.hidden=mode.value!=='scheduled';date.required=!date.hidden;});
 form.addEventListener('submit',async event=>{
  event.preventDefault();if(!consent.checked)return;
  const intent={mode:mode.value,publish_at:mode.value==='scheduled'?date.value+':00Z':null,reviewer:reviewer.value.trim()};
  if(!pending||JSON.stringify(pending.intent)!==JSON.stringify(intent))pending={intent,request_id:crypto.randomUUID()};
  submit.disabled=true;
  try{await request('/api/youtube/exports/'+row.id+'/publication','POST',{...pending.intent,request_id:pending.request_id,
    confirmed:true,publication_authorized:true,video_sha256:row.id});pending=null;consent.checked=false;await load();}
  catch(e){notify(e.message);await load().catch(()=>{});}finally{submit.disabled=false;}
 });
 refresh.addEventListener('click',async()=>{refresh.disabled=true;
  try{await request('/api/youtube/exports/'+row.id+'/publication-check','POST',{});await load();}
  catch(e){notify(e.message);}finally{refresh.disabled=false;}
 });
 load().catch(e=>{status.textContent=e.message;});
 return {load};
}
