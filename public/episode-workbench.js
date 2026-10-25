import {mountVideoPreview} from './video-preview.js';
const stageLabels={done:'completado',current:'en curso',pending:'pendiente',blocked:'requiere atención'};
const jobs={submit_script:['Enviar guion a revisión','submit'],approve_script:['Aprobar este guion','approve'],
 render:['Generar narración y video','dispatch'],retry_render:['Reanudar montaje','retry-render']};
const uploadSteps=new Set(['review_video','upload_video','check_upload','publish_video','check_publication','complete']);

export function mountEpisodeWorkbench(root,{request,openDossier,openExport,fetchArchive,refresh,
 documentRef=document,schedule=setTimeout,cancel=clearTimeout,confirmAction=message=>confirm(message)}){
 const el=(tag,text='')=>{const n=documentRef.createElement(tag);n.textContent=text;return n;};
 const status=el('p'),stages=el('ol'),actions=el('div'),script=el('details'),video=el('div');
 status.setAttribute('role','status');stages.className='episode-stages';actions.className='actions';
 root.replaceChildren(status,stages,actions,script,video);
 let current=null,timer=null,generation=0,busy=false,videoId=null,cleanup=null,scriptJob=null;
 const stop=()=>{if(timer!==null)cancel(timer);timer=null;};
 function button(label,callback,enabled=true){
  const b=el('button',label);b.type='button';b.disabled=!enabled||busy;actions.append(b);
  b.addEventListener('click',async()=>{
   if(busy)return;busy=true;b.disabled=true;stop();
   try{await callback();busy=false;await refresh();}catch(e){status.textContent=e.message;}
   finally{busy=false;b.disabled=!enabled;}
  });return b;
 }
 async function showScript(job){
  if(scriptJob===job.id)return;scriptJob=job.id;
  const summary=el('summary','Leer guion del episodio');script.replaceChildren(summary);script.open=false;
  script.ontoggle=async()=>{
   if(!script.open||script.children.length>1)return;
   const epoch=generation;
   try{const data=await request('/api/jobs/'+encodeURIComponent(job.id));
    if(epoch!==generation||scriptJob!==job.id)return;
    for(const segment of data.job.manifest.segments)script.append(el('h4',segment.headline),el('p',segment.voiceover));
   }catch(e){if(epoch===generation){script.append(el('p',e.message));scriptJob=null;}}
  };
 }
 async function load(episode){
  stop();const epoch=++generation;current=episode;
  if(!episode){status.textContent='Indica una empresa y un tema por chat para comenzar.';stages.replaceChildren();actions.replaceChildren();scriptJob=null;script.replaceChildren();cleanup?.();cleanup=null;videoId=null;video.replaceChildren();return;}
  try{
   const data=await request('/api/channel-control/progress?episode_id='+encodeURIComponent(episode.id));
   if(epoch!==generation)return;
   status.textContent=data.message;stages.replaceChildren();actions.replaceChildren();
   for(const step of data.steps){const item=el('li',step.label+' · '+stageLabels[step.state]);item.dataset.state=step.state;
    if(step.state==='current'||step.state==='blocked')item.setAttribute('aria-current','step');stages.append(item);}
   if(data.job){
    await showScript(data.job);
    button('Revisar fuentes y derechos',()=>openDossier(data.job.id));
   }else{scriptJob=null;script.replaceChildren();}
   if(['start_research','resume_research'].includes(data.next_step))button(
    data.research?.checkpoint_available?'Reanudar desde el guion':'Investigar este episodio',
    async()=>{const result=await request('/api/channel-control/research','POST',{episode_id:episode.id});
     if(!result.started)throw Error(result.reason==='research_paused'?'La investigación sigue pausada.':
      result.reason==='dispatch_unknown'?'Envío incierto. Revisa Actions antes de repetir.':'Ya hay una solicitud activa o se alcanzó el límite diario.');},data.action_enabled);
   if(jobs[data.next_step]){
    const [label,action]=jobs[data.next_step];
    button(label,async()=>{
     if(action==='approve'&&!confirmAction('¿Apruebas el guion con las fuentes, afirmaciones y derechos revisados?'))return;
     if(['dispatch','retry-render'].includes(action)&&!confirmAction('¿Autorizas la narración y el montaje de este episodio con la voz canónica?'))return;
     await request('/api/jobs/'+encodeURIComponent(data.job.id)+'/'+action,'POST',action==='approve'?{confirmed:true}:{});
    });
   }
   if(data.preview){
    if(videoId!==data.preview.export_id){
     const result=await request('/api/youtube/exports/'+data.preview.export_id);
     if(epoch!==generation)return;
     cleanup?.();video.replaceChildren();videoId=data.preview.export_id;
     cleanup=mountVideoPreview(video,result.export,{fetchArchive,documentRef});
    }
    if(uploadSteps.has(data.next_step))button('Abrir revisión y publicación de este video',()=>openExport(data.preview.export_id));
   }else{cleanup?.();cleanup=null;videoId=null;video.replaceChildren();}
   if(data.next_step==='complete'&&data.episode.state!=='completed')button('Cerrar episodio y preparar el siguiente',
    ()=>request('/api/channel-control/complete','POST',{episode_id:episode.id,confirmed:true}));
   if(data.next_step==='wait'&&!busy)timer=schedule(()=>{timer=null;void load(current);},12000);
  }catch(e){if(epoch===generation)status.textContent='No se pudo actualizar el episodio: '+e.message;}
 }
 return {load,dispose(){stop();generation++;cleanup?.();}};
}
