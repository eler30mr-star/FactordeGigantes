import {manifestSha} from './episode-production.mjs';
import {sourceUrl} from './editorial.mjs';
import reference from '../assets/voice/approved/reference.json' with {type:'json'};
import {youtubeConnectionStatus,youtubeAccessToken,encryptYoutube,decryptYoutube} from './youtube-connection.mjs';
const REPO='eler30mr-star/FactordeGigantes';
const HASH=/^[a-f0-9]{64}$/,NUMBER=/^[1-9]\d{0,15}$/;
const UUID=/^[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}$/;
const sha=value=>typeof value==='string'&&HASH.test(value);
const fail=(status,error)=>({ok:false,status,error});
const required=['watched_video','voice_approved','facts_checked','rights_verified','visuals_captions_approved','metadata_approved'];
export async function boundedUploadJson(response,limit=600000){
 const reader=response.body?.getReader();if(!reader)throw new Error('Respuesta vacía');
 const chunks=[];let size=0;
 while(true){const r=await reader.read();if(r.done)break;size+=r.value.byteLength;if(size>limit){await reader.cancel();throw new Error('Respuesta fuera de límite');}chunks.push(r.value);}
 const result=new Uint8Array(size);let offset=0;for(const c of chunks){result.set(c,offset);offset+=c.byteLength;}
 return JSON.parse(new TextDecoder().decode(result));
}
async function github(env,path,fetcher=fetch){
 if(env.GITHUB_REPO!==REPO||typeof env.GITHUB_DISPATCH_TOKEN!=='string'||env.GITHUB_DISPATCH_TOKEN.length<24)throw new Error('Acceso GitHub no configurado');
 const r=await fetcher('https://api.github.com/repos/'+REPO+path,{redirect:'manual',signal:AbortSignal.timeout(10000),headers:{
  Authorization:'Bearer '+env.GITHUB_DISPATCH_TOKEN,Accept:'application/vnd.github+json','User-Agent':'FactorDeGigantes-Upload','X-GitHub-Api-Version':'2022-11-28'}});
 if(!r.ok)throw new Error('GitHub no confirmó la consulta');return boundedUploadJson(r);
}
function metadataDraft(episode,report){
 const stamp=n=>String(Math.floor(n/60)).padStart(2,'0')+':'+String(Math.floor(n%60)).padStart(2,'0');
 const chapters=report.chapters.map(c=>stamp(c.start_seconds)+' '+c.title).join('\n');
 const sources=episode.sources.map(s=>s.id+' · '+s.url).join('\n');
 const description=episode.central_question+'\n\nCapítulos\n'+chapters+'\n\nFuentes\n'+sources+
  '\n\nNarración sintética y gráficos editoriales originales. Factor de Gigantes.';
 return {title:episode.title.slice(0,100),description:description.slice(0,5000),categoryId:'27',defaultLanguage:'es',
  privacyStatus:'private',madeForKids:null,containsSyntheticMedia:true,tags:['Factor de Gigantes',episode.company.slice(0,50)],
  description_needs_review:description.length>5000};
}
function checkedMetadata(m){
 if(!m||typeof m.title!=='string'||m.title.trim().length<8||m.title.length>100||/[<>]/.test(m.title)||
  typeof m.description!=='string'||m.description.length>5000||/[<>]/.test(m.description)||
  m.privacyStatus!=='private'||typeof m.madeForKids!=='boolean'||typeof m.containsSyntheticMedia!=='boolean'||
  typeof m.categoryId!=='string'||!/^\d{1,3}$/.test(m.categoryId)||!Array.isArray(m.tags)||m.tags.length>10||
  m.tags.some(t=>typeof t!=='string'||t.length<1||t.length>50)||m.tags.join(',').length>450)throw new RangeError('Revisa los metadatos y declara la audiencia. Sólo se admite privado.');
 return {title:m.title.trim(),description:m.description,categoryId:m.categoryId,defaultLanguage:'es',privacyStatus:'private',
  madeForKids:m.madeForKids,containsSyntheticMedia:m.containsSyntheticMedia,tags:m.tags};
}
export function exportView(row,detail=false){
 const p=JSON.parse(row.episode_json),r=JSON.parse(row.export_json);
 return {id:row.id,title:p.title,origin:p.origin,seconds:r.actual_seconds,state:row.state,
  metadata:JSON.parse(row.metadata_json),review:JSON.parse(row.review_json),last_error:row.last_error,
  source_url:'https://github.com/'+REPO+'/actions/runs/'+row.source_run_id+'/artifacts/'+row.artifact_id,
  video_url:row.video_id?'https://www.youtube.com/watch?v='+row.video_id:null,
  ...(detail?{episode:p,report:r}:{}),automatic_publication_allowed:false};
}
export async function listYoutubeExports(env){
 const r=await env.DB.prepare('SELECT * FROM youtube_exports ORDER BY updated_at DESC LIMIT 20').all();
 return {ok:true,exports:r.results.map(r=>exportView(r)),automatic_publication_allowed:false};
}
export async function findYoutubeExport(env,id){
 if(!sha(id))return fail(400,'Identificador de exportación inválido');
 const row=await env.DB.prepare('SELECT * FROM youtube_exports WHERE id=?').bind(id).first();
 return row?{ok:true,export:exportView(row,true),automatic_publication_allowed:false}:fail(404,'Exportación inexistente');
}
export async function registerYoutubeExport(env,body,{githubFetch=fetch}={}){
 const r=body?.report;
 if(!r||r.schema!=='fdg_episode_export_v1'||!sha(r.sha256)||!sha(r.episode_sha256)||
  r.contains_narration!==true||r.voice_kind!=='canonical_qwen_pending_audition'||r.technical_gate_passed!==true||
  r.canonical_reference_sha256!==reference.sha256||r.canonical_reference_unchanged!==true||
  !Number.isFinite(r.actual_seconds)||r.actual_seconds<480||r.actual_seconds>840||
  !Number.isSafeInteger(r.generated_voice_takes)||r.generated_voice_takes<1||r.generated_voice_takes>128||
  ['human_factual_approval','commercial_rights_verified','publication_authorized'].some(k=>r[k]!==false)||
  !NUMBER.test(body.source_run_id)||typeof body.source_run_id!=='string'||!NUMBER.test(body.artifact_id)||typeof body.artifact_id!=='string'||
  !sha(body.archive_sha256)||!Number.isSafeInteger(body.video_bytes)||body.video_bytes<10000||body.video_bytes>2_000_000_000||
  typeof body.episode_canonical_json!=='string'||body.episode_canonical_json.length>100000)throw new RangeError('Exportación narrada inválida');
 if(await manifestSha(body.episode_canonical_json)!==r.episode_sha256)throw new RangeError('La huella del episodio no coincide');
 const p=JSON.parse(body.episode_canonical_json);
 if(p.schema!=='fdg_episode_package_v1'||!['codex_development_research','autonomous_script'].includes(p.origin)||
  typeof p.title!=='string'||p.title.length<10||p.title.length>150||typeof p.company!=='string'||p.company.length<3||
  typeof p.central_question!=='string'||p.central_question.length>500||p.canonical_voice_sha256!==reference.sha256||
  ['human_factual_approval','commercial_rights_verified','publication_authorized'].some(k=>p[k]!==false)||
  !Array.isArray(p.sources)||p.sources.length<2||p.sources.length>30||!Array.isArray(p.scenes)||p.scenes.length<6||p.scenes.length>12||
  !Array.isArray(r.chapters)||r.chapters.length!==p.scenes.length)throw new RangeError('Paquete de fuentes inválido');
 const ids=new Set();for(const s of p.sources){if(!/^S\d{2,3}$/.test(s.id)||ids.has(s.id))throw new RangeError('Fuentes inválidas');sourceUrl(s.url);ids.add(s.id);}
 for(const scene of p.scenes)if(!Array.isArray(scene.paragraphs)||scene.paragraphs.some(t=>typeof t.text!=='string'||!t.text.trim()||
  !Array.isArray(t.source_ids)||!t.source_ids.length||t.source_ids.some(s=>!ids.has(s))))throw new RangeError('Narración sin fuentes');
 let end=0;for(const [i,c] of r.chapters.entries()){
  if(c.id!==p.scenes[i].id||typeof c.title!=='string'||c.title.length>150||!Number.isFinite(c.start_seconds)||!Number.isFinite(c.end_seconds)||
   Math.abs(c.start_seconds-end)>.05||c.end_seconds-c.start_seconds<10)throw new RangeError('Capítulos inválidos');end=c.end_seconds;
 }
 if(Math.abs(end-r.actual_seconds)>.1)throw new RangeError('Duración de capítulos inválida');
 const old=await env.DB.prepare('SELECT * FROM youtube_exports WHERE id=?').bind(r.sha256).first();
 if(old){if(old.episode_json!==body.episode_canonical_json)throw new RangeError('La exportación ya tiene otra procedencia');return {ok:true,reused:true,export:exportView(old),automatic_publication_allowed:false};}
 const [run,artifact]=await Promise.all([
  github(env,'/actions/runs/'+body.source_run_id,githubFetch),github(env,'/actions/artifacts/'+body.artifact_id,githubFetch)]);
 if(run.path!=='.github/workflows/development-episode.yml'||run.head_branch!=='main'||run.event!=='workflow_dispatch'||
  run.repository?.full_name!==REPO||run.status!=='completed'||run.conclusion!=='success'||
  artifact.name!=='fdg-episode-narrated-review'||artifact.expired!==false||String(artifact.workflow_run?.id)!==body.source_run_id||
  artifact.digest!=='sha256:'+body.archive_sha256)throw new RangeError('No es un resultado canónico terminado de main');
 await env.DB.batch([
  env.DB.prepare(`INSERT OR IGNORE INTO youtube_exports(id,source_run_id,artifact_id,archive_sha256,video_bytes,episode_json,export_json,metadata_json)
   VALUES(?,?,?,?,?,?,?,?)`).bind(r.sha256,body.source_run_id,body.artifact_id,body.archive_sha256,body.video_bytes,
    body.episode_canonical_json,JSON.stringify(r),JSON.stringify(metadataDraft(p,r))),
  env.DB.prepare("INSERT INTO youtube_export_events(export_id,action) SELECT ?,'registered_for_review' WHERE changes()=1").bind(r.sha256)
 ]);
 const row=await env.DB.prepare('SELECT * FROM youtube_exports WHERE id=?').bind(r.sha256).first();
 return {ok:true,export:exportView(row),automatic_publication_allowed:false};
}
export async function reviewYoutubeExport(env,id,body){
 if(!sha(id))return fail(400,'Exportación inválida');
 if(body?.confirmed!==true||required.some(k=>body[k]!==true)||typeof body.reviewer!=='string'||body.reviewer.trim().length<3||body.reviewer.length>80)
  return fail(400,'Confirma la revisión del video, fuentes, voz, derechos y metadatos e identifica al responsable.');
 const metadata=checkedMetadata(body.metadata),review={reviewer:body.reviewer.trim(),...Object.fromEntries(required.map(k=>[k,true])),
  video_sha256:id,reviewed_at:new Date().toISOString(),privacyStatus:'private'};
 const r=await env.DB.batch([
  env.DB.prepare("UPDATE youtube_exports SET state='approved',review_json=?,metadata_json=?,last_error='',updated_at=datetime('now') WHERE id=? AND state IN ('review','approved')")
   .bind(JSON.stringify(review),JSON.stringify(metadata),id),
  env.DB.prepare("INSERT INTO youtube_export_events(export_id,action,note) SELECT ?,'human_review',? WHERE changes()=1")
   .bind(id,JSON.stringify({reviewer:review.reviewer,privacyStatus:'private'}))
 ]);
 return r[0].meta?.changes===1?findYoutubeExport(env,id):fail(409,'La exportación ya cambió de estado.');
}
export async function queueYoutubeUpload(env,id,body,{githubFetch=fetch}={}){
 if(!sha(id)||body?.confirmed!==true)return fail(400,'Confirma la subida privada de esta exportación.');
 const connected=await youtubeConnectionStatus(env);if(!connected.connected)return fail(409,'Conecta el canal antes de solicitar la subida.');
 const requestId=crypto.randomUUID();
 const changed=await env.DB.prepare("UPDATE youtube_exports SET state='queued',request_id=?,target_channel_id=?,updated_at=datetime('now') WHERE id=? AND state='approved'")
  .bind(requestId,connected.channel.id,id).run();
 if(changed.meta?.changes!==1)return fail(409,'Falta revisión aprobada o la subida ya está reservada.');
 let r;try{
  r=await githubFetch('https://api.github.com/repos/'+REPO+'/actions/workflows/youtube-upload.yml/dispatches',{method:'POST',redirect:'manual',signal:AbortSignal.timeout(10000),
   headers:{Authorization:'Bearer '+env.GITHUB_DISPATCH_TOKEN,Accept:'application/vnd.github+json','User-Agent':'FactorDeGigantes-Upload','Content-Type':'application/json'},
   body:JSON.stringify({ref:'main',inputs:{request_id:requestId}})});
 }catch{return fail(502,'Envío a Actions incierto. Revisa la ejecución; no repitas la reserva.');}
 if(r.status!==204){
  await env.DB.prepare("UPDATE youtube_exports SET state='approved',request_id=NULL,last_error='GitHub rechazó el despacho' WHERE id=? AND request_id=? AND state='queued'").bind(id,requestId).run();
  return fail(502,'GitHub rechazó el despacho de subida. Revisa permisos Actions.');
 }
 await env.DB.prepare("INSERT INTO youtube_export_events(export_id,action,note) VALUES(?,'private_upload_requested',?)").bind(id,JSON.stringify({request_id:requestId})).run();
 return {ok:true,request_id:requestId,automatic_publication_allowed:false};
}
export async function resumeYoutubeUpload(env,id,body,{githubFetch=fetch}={}){
 if(!sha(id)||body?.confirmed!==true)return fail(400,'Confirma que deseas continuar esta misma subida.');
 const row=await env.DB.prepare('SELECT * FROM youtube_exports WHERE id=?').bind(id).first();
 if(!approved(row)||!['queued','uploading'].includes(row.state)||!row.request_id)return fail(409,'Esta subida no admite reintento automático.');
 const conn=await youtubeConnectionStatus(env);if(!conn.connected||conn.channel.id!==row.target_channel_id)return fail(409,'El canal autorizado cambió.');
 try{
  const r=await githubFetch('https://api.github.com/repos/'+REPO+'/actions/workflows/youtube-upload.yml/dispatches',{method:'POST',redirect:'manual',signal:AbortSignal.timeout(10000),
   headers:{Authorization:'Bearer '+env.GITHUB_DISPATCH_TOKEN,Accept:'application/vnd.github+json','User-Agent':'FactorDeGigantes-Upload','Content-Type':'application/json'},
   body:JSON.stringify({ref:'main',inputs:{request_id:row.request_id}})});
  if(r.status!==204)return fail(502,'No se confirmó el reintento en Actions.');
  return {ok:true,request_id:row.request_id,automatic_publication_allowed:false};
 }catch{return fail(502,'Reintento no confirmado. Consulta Actions antes de repetir.');}
}
async function uploadRow(env,requestId){
 if(typeof requestId!=='string'||!UUID.test(requestId))return null;
 return env.DB.prepare('SELECT * FROM youtube_exports WHERE request_id=?').bind(requestId).first();
}
function approved(row){
 if(!row)return false;try{const review=JSON.parse(row.review_json),m=JSON.parse(row.metadata_json);
  return required.every(k=>review[k]===true)&&review.video_sha256===row.id&&m.privacyStatus==='private'&&typeof m.madeForKids==='boolean';
 }catch{return false;}
}
export async function uploadContext(env,requestId){
 const row=await uploadRow(env,requestId);
 if(!approved(row)||!['queued','uploading','uploaded','unknown'].includes(row.state))return fail(409,'Subida no autorizada.');
 return {ok:true,request_id:requestId,export_id:row.id,source_run_id:row.source_run_id,artifact_id:row.artifact_id,
  archive_sha256:row.archive_sha256,video_bytes:row.video_bytes,state:row.state,metadata:JSON.parse(row.metadata_json),
  video_id:row.video_id||null,automatic_publication_allowed:false};
}
export function validYoutubeSession(value){
 try{const u=new URL(value);return u.protocol==='https:'&&u.hostname==='www.googleapis.com'&&!u.port&&!u.username&&!u.password&&
  u.pathname==='/upload/youtube/v3/videos'&&!u.hash&&!!u.searchParams.get('upload_id')&&value.length<8192;}catch{return false;}
}
export async function startYoutubeUpload(env,requestId,body,{googleFetch=fetch}={}){
 const row=await uploadRow(env,requestId);
 if(!approved(row)||body?.sha256!==row.id||body?.bytes!==row.video_bytes||!['queued','uploading'].includes(row.state))return fail(409,'Archivo o autorización de subida inválidos.');
 const conn=await youtubeConnectionStatus(env);if(!conn.connected||conn.channel.id!==row.target_channel_id)return fail(409,'El canal autorizado cambió.');
 const token=await youtubeAccessToken(env,{googleFetch});if(!token.ok)return token;
 if(row.state==='uploading'&&row.session_encrypted){
  const s=await decryptYoutube(env,row.session_encrypted,'youtube-upload:'+requestId);
  if(!validYoutubeSession(s.url))return fail(409,'Sesión no válida.');
  return {ok:true,session_ready:true,automatic_publication_allowed:false};
 }
 const reserved=await env.DB.prepare("UPDATE youtube_exports SET state='initiating',updated_at=datetime('now') WHERE id=? AND request_id=? AND state='queued'").bind(row.id,requestId).run();
 if(reserved.meta?.changes!==1)return fail(409,'La sesión ya está reservada; no duplicar videos.insert.');
 try{
  const m=JSON.parse(row.metadata_json),resource={snippet:{title:m.title,description:m.description,tags:m.tags,categoryId:m.categoryId,defaultLanguage:'es'},
   status:{privacyStatus:'private',selfDeclaredMadeForKids:m.madeForKids,containsSyntheticMedia:m.containsSyntheticMedia}};
  const r=await googleFetch('https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status&notifySubscribers=false',{
   method:'POST',redirect:'manual',signal:AbortSignal.timeout(15000),headers:{Authorization:'Bearer '+token.access_token,'Content-Type':'application/json; charset=UTF-8',
    'X-Upload-Content-Type':'video/mp4','X-Upload-Content-Length':String(row.video_bytes)},body:JSON.stringify(resource)});
  const url=r.headers.get('Location');await r.body?.cancel();if(!r.ok||!validYoutubeSession(url))throw new Error('Sesión no confirmada');
  const session=await encryptYoutube(env,{url},'youtube-upload:'+requestId);
  const changed=await env.DB.prepare("UPDATE youtube_exports SET state='uploading',session_encrypted=?,updated_at=datetime('now') WHERE id=? AND request_id=? AND state='initiating'").bind(session,row.id,requestId).run();
  if(changed.meta?.changes!==1)throw new Error('Estado cambió');
  return {ok:true,session_ready:true,automatic_publication_allowed:false};
 }catch{
  await env.DB.prepare("UPDATE youtube_exports SET state='unknown',last_error='Inicio de subida no confirmado; revisar antes de repetir',updated_at=datetime('now') WHERE id=? AND request_id=? AND state='initiating'").bind(row.id,requestId).run();
  return fail(502,'No se confirmó el inicio. No se crea otra sesión automáticamente.');
 }
}
export async function transferYoutubeChunk(env,requestId,request,{googleFetch=fetch}={}){
 const row=await uploadRow(env,requestId);
 if(!approved(row)||row.state!=='uploading'||!row.session_encrypted)return fail(409,'Subida no activa.');
 const range=request.headers.get('Content-Range')||'',length=Number(request.headers.get('Content-Length'));
 const resume=range==='bytes */'+row.video_bytes;
 const match=/^bytes (\d+)-(\d+)\/(\d+)$/.exec(range);
 if(!Number.isSafeInteger(length)||length<0||length>4*1024*1024||
  (resume?length!==0:!match||Number(match[3])!==row.video_bytes||Number(match[1])>Number(match[2])||
   Number(match[2])>=row.video_bytes||Number(match[2])-Number(match[1])+1!==length))return fail(400,'Rango de archivo inválido.');
 const reader=request.body?.getReader(),chunks=[];let total=0;
 if(reader)while(true){const r=await reader.read();if(r.done)break;total+=r.value.byteLength;
  if(total>length){await reader.cancel();return fail(400,'Tamaño de fragmento incorrecto.');}chunks.push(r.value);}
 if(total!==length)return fail(400,'Fragmento incompleto.');
 const conn=await youtubeConnectionStatus(env);if(!conn.connected||conn.channel.id!==row.target_channel_id)return fail(409,'El canal autorizado cambió.');
 const token=await youtubeAccessToken(env,{googleFetch});if(!token.ok)return token;
 const session=await decryptYoutube(env,row.session_encrypted,'youtube-upload:'+requestId);
 if(!validYoutubeSession(session.url))return fail(409,'Sesión no válida.');
 const data=new Uint8Array(total);let offset=0;for(const c of chunks){data.set(c,offset);offset+=c.byteLength;}
 try{
  const r=await googleFetch(session.url,{method:'PUT',redirect:'manual',signal:AbortSignal.timeout(30000),
   headers:{Authorization:'Bearer '+token.access_token,'Content-Type':'video/mp4','Content-Range':range},body:data});
  if(r.status===308){
   const received=r.headers.get('Range'),m=received&&/^bytes=0-(\d+)$/.exec(received),next=received?(m?Number(m[1])+1:NaN):0;
   await r.body?.cancel();if(!Number.isSafeInteger(next)||next<0||next>row.video_bytes)return fail(502,'Google devolvió un rango inválido.');
   return {ok:true,complete:false,next_offset:next,automatic_publication_allowed:false};
  }
  if(r.status===200||r.status===201){
   const body=await boundedUploadJson(r);if(typeof body.id!=='string'||!/^[-\w]{11}$/.test(body.id))return fail(502,'Resultado de video inválido.');
   return {ok:true,complete:true,video_id:body.id,automatic_publication_allowed:false};
  }
  await r.body?.cancel();return fail(502,'Google no confirmó el fragmento; consulta el estado antes de continuar.');
 }catch{return fail(502,'Transferencia no confirmada. Se conserva la sesión para consultar y reanudar.');}
}
export async function finishYoutubeUpload(env,requestId,body,{googleFetch=fetch}={}){
 const row=await uploadRow(env,requestId);
 if(!approved(row)||typeof body?.video_id!=='string'||!/^[-\w]{11}$/.test(body.video_id))return fail(400,'Resultado de subida inválido.');
 if(row.state==='uploaded')return row.video_id===body.video_id?{ok:true,reused:true,automatic_publication_allowed:false}:fail(409,'Ya existe otro resultado.');
 if(row.state!=='uploading')return fail(409,'La subida no está activa.');
 const conn=await youtubeConnectionStatus(env);if(!conn.connected||conn.channel.id!==row.target_channel_id)return fail(409,'El canal autorizado cambió.');
 const token=await youtubeAccessToken(env,{googleFetch});if(!token.ok)return token;
 const r=await googleFetch('https://www.googleapis.com/youtube/v3/videos?part=snippet,status&id='+body.video_id,{redirect:'manual',signal:AbortSignal.timeout(12000),headers:{Authorization:'Bearer '+token.access_token}});
 if(!r.ok)return fail(502,'No se pudo verificar el video en Google.');
 const video=(await boundedUploadJson(r)).items?.[0];
 if(video?.id!==body.video_id||video.snippet?.channelId!==row.target_channel_id||video.status?.privacyStatus!=='private')return fail(409,'Google no confirmó el video privado en el canal autorizado.');
 const result=await env.DB.batch([
  env.DB.prepare("UPDATE youtube_exports SET state='uploaded',video_id=?,session_encrypted='',last_error='',updated_at=datetime('now') WHERE id=? AND request_id=? AND state='uploading'").bind(video.id,row.id,requestId),
  env.DB.prepare("INSERT INTO youtube_export_events(export_id,action,note) SELECT ?,'private_upload_confirmed',? WHERE changes()=1").bind(row.id,JSON.stringify({video_id:video.id,privacy:'private'}))
 ]);
 return result[0].meta?.changes===1?{ok:true,video_id:video.id,automatic_publication_allowed:false}:fail(409,'Estado de subida cambiado.');
}
