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
   line(episode,'Elegido por '+(data.episode.origin==='chat'?'ti':'el sistema')+'. Estado: seleccionado.');
   line(episode,(data.research_paused?'Investigación pausada. ':'')+'El nuevo flujo de producción está pendiente de integración.');
  }
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
