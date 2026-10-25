// Uses the existing in-memory authenticated request client; never persists tokens.
export function mountChannelControl({request,documentRef=document,uuid=()=>crypto.randomUUID()}){
 const el=id=>documentRef.getElementById(id);
 let state=null,busy=false,pending=null;
 const toggle=el('automatic-toggle'),send=el('channel-send');
 function lock(value){busy=value;toggle.disabled=value||!state;send.disabled=value||!state;}
 function line(root,text){const p=documentRef.createElement('p');p.textContent=text;root.append(p);}
 async function load(){
  const data=await request('/api/channel-control');
  state=data;
  toggle.textContent='Automático: '+(data.automatic_enabled?'encendido':'apagado');
  toggle.setAttribute('aria-checked',String(data.automatic_enabled));
  el('channel-status').textContent=data.message;
  const episode=el('channel-episode');episode.replaceChildren();
  if(data.episode){
   line(episode,data.episode.company+' — '+data.episode.topic);
   line(episode,'Elegido por '+(data.episode.origin==='chat'?'ti':'el sistema')+'. Estado: '+data.episode.state+'.');
   if(data.research_paused)line(episode,'Investigación pausada. Tu elección se conserva.');
   try{const result=await request('/api/channel-control/research?episode_id='+data.episode.id);
    if(result.run){line(episode,result.run.note||'Investigación: '+result.run.state);if(result.run.job_status)line(episode,'Trabajo editorial: '+result.run.job_status);}
   }catch{ /* La selección sigue visible aunque el seguimiento no esté disponible. */ }
   if(data.episode.state==='selected'&&!data.research_paused){
    const start=documentRef.createElement('button');start.type='button';start.textContent='Iniciar investigación del episodio';episode.append(start);
    start.addEventListener('click',async()=>{if(busy)return;lock(true);start.disabled=true;
     try{const r=await request('/api/channel-control/research','POST',{episode_id:data.episode.id});
      el('channel-chat-status').textContent=r.started?'Investigación enviada a Actions.':r.reason==='dispatch_unknown'?'Despacho incierto: revisa Actions antes de repetir.':'Ya hay una solicitud o se alcanzó el límite diario.';await load();
     }catch(e){el('channel-chat-status').textContent=e.message;}finally{lock(false);start.disabled=false;}});
   }
  }
  const study=el('channel-study');study.replaceChildren();
  try{
   const result=await request('/api/market/opportunity-study');
   if(result.study){
    const r=result.study,states={running:'en curso',calibration:'en calibración',insufficient:'sin evidencia suficiente',selected:'episodio elegido',cancelled:'cancelado'};
    const reasons={need_four_comparable_long_videos:'faltan cuatro videos largos comparables',need_three_channels_with_three_baselines_each:'faltan referencias habituales de al menos tres canales',need_independent_search_queries:'faltan consultas independientes',need_two_recent_examples:'faltan ejemplos recientes',company_recently_covered:'empresa ya tratada recientemente',no_consistent_relative_outperformance:'el rendimiento relativo no destaca de forma consistente'};
    line(study,'Último estudio YouTube: '+r.observed_on+' · '+(states[r.state]||r.state));
    for(const candidate of r.rankings||[])line(study,candidate.company+' — '+candidate.topic+
      (candidate.eligible?' · comparación suficiente':' · falta evidencia: '+candidate.reasons.map(reason=>reasons[reason]||'evidencia incompleta').join(', ')));
    if(r.state==='calibration')line(study,'Estudio de calibración. Todavía no se eligió un episodio automáticamente.');
   }
  }catch{line(study,'Estudio de mercado todavía no disponible.');}
  const history=el('channel-chat-history');history.replaceChildren();
  for(const entry of data.conversation){line(history,'Tú: '+entry.message);line(history,'Sistema: '+entry.reply);}
  lock(busy);return data;
 }
 async function perform(kind,payload){
  // Preserve request ID and original revision after an uncertain network result.
  // A retry cannot create a second episode or reverse a later mode change.
  if(!pending||pending.kind!==kind||JSON.stringify(pending.payload)!==JSON.stringify(payload))
   pending={kind,payload,request_id:uuid(),revision:state.revision};
  const result=await request('/api/channel-control/'+kind,'POST',{
   ...pending.payload,request_id:pending.request_id,revision:pending.revision
  });
  pending=null;el('channel-chat-status').textContent=result.reply;await load();return result;
 }
 toggle.addEventListener('click',async()=>{
  if(busy||!state)return;
  const enabled=!state.automatic_enabled;lock(true);
  try{await perform('mode',{enabled});}
  catch(e){if(e.status>=400&&e.status<500)pending=null;el('channel-chat-status').textContent=e.message;await load().catch(()=>{});}
  finally{lock(false);}
 });
 el('channel-chat-form').addEventListener('submit',async event=>{
  event.preventDefault();if(busy||!state)return;
  const message=el('channel-message').value.trim();if(!message)return;
  lock(true);
  try{await perform('chat',{message});el('channel-message').value='';}
  catch(e){if(e.status>=400&&e.status<500)pending=null;el('channel-chat-status').textContent=e.message;await load().catch(()=>{});}
  finally{lock(false);}
 });
 el('channel-refresh').addEventListener('click',async()=>{
  if(busy)return;lock(true);
  try{await load();}catch(e){el('channel-chat-status').textContent=e.message;}finally{lock(false);}
 });
 return {load};
}
