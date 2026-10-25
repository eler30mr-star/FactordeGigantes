// Single configured channel. All mode/chat writes use a revision lease in a D1 batch.
// No provider calls, publication or legacy radar selection is performed here.
const CHANNEL='factor-de-gigantes';
const UUID=/^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const fail=(status,error)=>({ok:false,status,error});
const row=db=>db.prepare('SELECT * FROM channel_control WHERE channel=?').bind(CHANNEL).first();
function clean(value,min,max,label){
 if(typeof value!=='string')throw new RangeError(label+' inválido');
 const text=value.normalize('NFKC').trim().replace(/ +/g,' ');
 if(text.length<min||text.length>max||/[\x00-\x1f\x7f<>]/u.test(text))throw new RangeError(label+' inválido');
 return text;
}
function lease(body){
 if(!body||typeof body!=='object'||Array.isArray(body)||!UUID.test(body.request_id)||
    !Number.isSafeInteger(body.revision)||body.revision<0)throw new RangeError('Solicitud o versión inválida');
}
function gateView(control,env){
 const enabled=control?.automatic_enabled===1;
 const paused=env.FINAL_AI_INTEGRATION_ENABLED!=='1',validated=env.YOUTUBE_SELECTOR_VALIDATED==='1';
 const reason=!enabled?'automatic_off':paused?'research_paused':!validated?'market_calibration_pending':'ready';
 return {ok:true,automatic_enabled:enabled,revision:control?.revision??0,
  allowed:enabled&&!paused&&validated,reason,
  message:!enabled?'Automático apagado. Esperando tu tema y empresa por chat.':paused?
   'Automático encendido. Los investigadores siguen pausados; no se inician búsquedas.':!validated?
   'Automático encendido. Estudio YouTube disponible para calibración; selección automática pendiente de validar con datos reales.':
   'Automático encendido. El sistema puede realizar el estudio comparativo diario.',
  research_paused:paused,publication_authorized:false};
}
export async function automaticGate(env){return gateView(await row(env.DB),env);}
export async function channelStatus(env){
 const [control,episodes,events]=await Promise.all([
  row(env.DB),
  env.DB.prepare("SELECT id,origin,company,topic,state,created_at FROM channel_episodes WHERE channel=? AND state NOT IN ('completed','cancelled') LIMIT 1").bind(CHANNEL).all(),
  env.DB.prepare("SELECT request_id,kind,payload_json,result_json,created_at FROM channel_control_events WHERE channel=? ORDER BY rowid DESC LIMIT 20").bind(CHANNEL).all()
 ]);
 if(!control)return fail(503,'Falta inicializar el control del canal');
 const gate=gateView(control,env);
 return {...gate,revision:control.revision,automatic_enabled:control.automatic_enabled===1,
  updated_at:control.updated_at,episode:episodes.results?.[0]??null,
  conversation:(events.results||[]).reverse().filter(e=>e.kind==='chat').map(e=>{
   const input=JSON.parse(e.payload_json),output=JSON.parse(e.result_json);
   return {request_id:e.request_id,message:input.message,reply:output.reply,created_at:e.created_at};
  }),next_step:episodes.results?.length?'episode_pipeline_pending':'awaiting_selection'};
}
async function replay(db,id,payload){
 const previous=await db.prepare('SELECT payload_json,result_json FROM channel_control_events WHERE request_id=? AND channel=?').bind(id,CHANNEL).first();
 if(!previous)return null;
 return previous.payload_json===payload?{...JSON.parse(previous.result_json),replayed:true}:
  fail(409,'El identificador ya corresponde a otra instrucción');
}
async function commitOperation(env,body,kind,payload,result,updates,episode=null){
 const operation=body.request_id;
 const [enabled,company,instruction]=updates;
 const statements=[env.DB.prepare(
  'UPDATE channel_control SET automatic_enabled=?,pending_company=?,pending_instruction=?,revision=revision+1,last_operation=?,updated_at=datetime(\'now\') WHERE channel=? AND revision=?'
 ).bind(enabled,company,instruction,operation,CHANNEL,body.revision)];
 if(episode)statements.push(env.DB.prepare(
  "INSERT INTO channel_episodes(id,channel,origin,company,topic,instruction) SELECT ?,?,'chat',?,?,? WHERE EXISTS (SELECT 1 FROM channel_control WHERE channel=? AND last_operation=?)"
 ).bind(episode.id,CHANNEL,episode.company,episode.topic,episode.instruction,CHANNEL,operation));
 statements.push(env.DB.prepare(
  'INSERT INTO channel_control_events(request_id,channel,kind,payload_json,result_json) SELECT ?,?,?,?,? WHERE EXISTS (SELECT 1 FROM channel_control WHERE channel=? AND last_operation=?)'
 ).bind(operation,CHANNEL,kind,payload,JSON.stringify(result),CHANNEL,operation));
 try{
  const batch=await env.DB.batch(statements);
  if(batch[0].meta?.changes===1)return result;
 }catch(e){
  const prior=await replay(env.DB,operation,payload);if(prior)return prior;
  if(/UNIQUE constraint failed: channel_episodes.channel/.test(String(e?.message)))
   return fail(409,'Ya hay un episodio activo. Se conserva su trabajo.');
  throw e;
 }
 return await replay(env.DB,operation,payload)||fail(409,'El canal cambió. Actualiza antes de enviar de nuevo.');
}
export async function setAutomaticMode(env,body){
 lease(body);
 if(typeof body.enabled!=='boolean')throw new RangeError('Estado automático inválido');
 const payload=JSON.stringify({enabled:body.enabled});
 const prior=await replay(env.DB,body.request_id,payload);if(prior)return prior;
 const control=await row(env.DB);
 if(!control)return fail(503,'Falta inicializar el control del canal');
 const result={ok:true,revision:body.revision+1,automatic_enabled:body.enabled,
  reply:body.enabled?'Automático encendido. Se respetan la pausa y la validación del estudio antes de elegir.':
   'Automático apagado. Indica por chat qué tema y empresa quieres investigar.'};
 return commitOperation(env,body,'mode',payload,result,[body.enabled?1:0,control.pending_company,control.pending_instruction]);
}
// Conservative interpretation: never guess a company from an ambiguous instruction.
// A short persisted dialogue obtains missing fields without asking for sources or a script.
export function interpretInstruction(message,control){
 const explicit=/^(?:haz|crea|produce)\s+(?:un\s+)?(?:video|documental)\s+(?:sobre|acerca de)\s+(.+?)\s+(?:y|acerca de)\s+(.+)$/iu.exec(message);
 if(explicit)return {company:clean(explicit[1],2,100,'Empresa'),topic:clean(explicit[2],5,300,'Tema'),instruction:message};
 if(control.pending_company)return {company:control.pending_company,topic:clean(message,5,300,'Tema'),instruction:control.pending_instruction+' | '+message};
 if(control.pending_instruction)return {company:clean(message,2,100,'Empresa'),instruction:control.pending_instruction,
  reply:'¿Qué tema o enfoque quieres tratar sobre '+message+'?'};
 return {company:'',instruction:message,reply:'¿Sobre qué empresa quieres hacer el video? Después dime el tema o enfoque.'};
}
export async function receiveChannelInstruction(env,body){
 lease(body);
 const message=clean(body.message,2,600,'Mensaje');
 const payload=JSON.stringify({message});
 const prior=await replay(env.DB,body.request_id,payload);if(prior)return prior;
 const control=await row(env.DB);
 if(!control)return fail(503,'Falta inicializar el control del canal');
 const active=await env.DB.prepare("SELECT id FROM channel_episodes WHERE channel=? AND state NOT IN ('completed','cancelled') LIMIT 1").bind(CHANNEL).first();
 if(active)return fail(409,'Ya hay un episodio activo. No se reemplazará ni se iniciará otro.');
 const parsed=interpretInstruction(message,control);
 const episode=parsed.topic?{id:crypto.randomUUID(),company:parsed.company,topic:parsed.topic,instruction:parsed.instruction}:null;
 const result={ok:true,revision:body.revision+1,episode,
  reply:episode?'Seleccionado: '+episode.company+' — '+episode.topic+'. '+
   (env.FINAL_AI_INTEGRATION_ENABLED!=='1'?'La investigación sigue pausada. ':'')+
   'El episodio está guardado; la conexión del nuevo flujo de producción está pendiente.':parsed.reply,
  state:episode?'selected':'clarification',publication_authorized:false};
 return commitOperation(env,body,'chat',payload,result,[control.automatic_enabled,
  episode?'':parsed.company,episode?'':parsed.instruction],episode);
}
