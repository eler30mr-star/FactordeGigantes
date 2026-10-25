// Explicit human authorization only. Never called by cron, research, or upload callbacks.
import {youtubeConnectionStatus,youtubeAccessToken} from './youtube-connection.mjs';
import {boundedUploadJson} from './youtube-exports.mjs';
const HASH=/^[a-f0-9]{64}$/,UUID=/^[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}$/;
const checks=['watched_video','voice_approved','facts_checked','rights_verified','visuals_captions_approved','metadata_approved'];
const fail=(status,error)=>({ok:false,status,error});
const API='https://www.googleapis.com/youtube/v3/videos';
const view=r=>r?{request_id:r.request_id,mode:r.mode,publish_at:r.publish_at,state:r.state,last_error:r.last_error,video_url:'https://www.youtube.com/watch?v='+r.video_id}:null;
export async function publicationStatus(env,id){
 if(!HASH.test(id))return fail(400,'Exportación inválida');
 const row=await env.DB.prepare('SELECT * FROM youtube_publications WHERE export_id=?').bind(id).first();
 return {ok:true,publication:view(row)};
}
export function publicationIntent(body,now=new Date()){
 if(!body||body.confirmed!==true||body.publication_authorized!==true||!UUID.test(body.request_id)||
  !HASH.test(body.video_sha256)||typeof body.reviewer!=='string'||body.reviewer.trim().length<3||body.reviewer.length>80||
  /[\x00-\x1f<>]/.test(body.reviewer)||!['public','scheduled'].includes(body.mode))throw new RangeError('Autoriza expresamente este video e identifica al responsable');
 let at=null;
 if(body.mode==='scheduled'){
  if(typeof body.publish_at!=='string'||!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z$/.test(body.publish_at))throw new RangeError('Indica una fecha UTC válida');
  const t=Date.parse(body.publish_at);
  if(!Number.isFinite(t)||new Date(t).toISOString().slice(0,19)!==body.publish_at.slice(0,19)||t-now.getTime()<600000||t-now.getTime()>365*86400000)throw new RangeError('Programa entre diez minutos y un año en el futuro');
  at=new Date(t).toISOString();
 }else if(body.publish_at)throw new RangeError('Publicación inmediata no admite fecha');
 return {mode:body.mode,publish_at:at,reviewer:body.reviewer.trim()};
}
function reviewed(row,id){
 try{const r=JSON.parse(row.review_json),m=JSON.parse(row.metadata_json);
  return row.state==='uploaded'&&r.video_sha256===id&&checks.every(k=>r[k]===true)&&typeof m.madeForKids==='boolean'&&
   typeof m.containsSyntheticMedia==='boolean'&&/^[-\w]{11}$/.test(row.video_id);
 }catch{return false;}
}
async function video(env,token,id,fetcher){
 const response=await fetcher(API+'?part=snippet,status&id='+id,{headers:{Authorization:'Bearer '+token},redirect:'manual',signal:AbortSignal.timeout(12000)});
 if(!response.ok)throw Error('Video lookup failed');return (await boundedUploadJson(response)).items?.[0];
}
const matches=(r,v)=>v?.id===r.video_id&&v.snippet?.channelId===r.channel_id&&
 (r.mode==='public'?v.status?.privacyStatus==='public':v.status?.privacyStatus==='private'&&
  Date.parse(v.status?.publishAt)===Date.parse(r.publish_at));
export async function reconcilePublication(env,id,{googleFetch=fetch}={}){
 const record=await env.DB.prepare('SELECT * FROM youtube_publications WHERE export_id=?').bind(id).first();
 if(!record)return fail(404,'No hay autorización de publicación registrada');
 const conn=await youtubeConnectionStatus(env);
 if(!conn.connected||conn.channel.id!==record.channel_id)return fail(409,'El canal conectado cambió');
 const token=await youtubeAccessToken(env,{googleFetch});if(!token.ok)return token;
 try{
  const observed=await video(env,token.access_token,record.video_id,googleFetch);
  if(matches(record,observed))await env.DB.batch([
   env.DB.prepare("UPDATE youtube_publications SET state='confirmed',last_error='',updated_at=datetime('now') WHERE export_id=? AND request_id=? AND state<>'confirmed'").bind(id,record.request_id),
   env.DB.prepare("INSERT INTO youtube_export_events(export_id,action,note) SELECT ?,'publication_confirmed',? WHERE changes()=1").bind(id,JSON.stringify({mode:record.mode,publish_at:record.publish_at}))
  ]);
  const status=await publicationStatus(env,id);return {...status,observed_privacy:observed?.status?.privacyStatus??null};
 }catch{return fail(502,'No se pudo comprobar YouTube. No se ha repetido la publicación.');}
}
export async function authorizePublication(env,id,body,{googleFetch=fetch,now=new Date()}={}){
 if(!HASH.test(id))return fail(400,'Exportación inválida');
 const intent=publicationIntent(body,now);
 if(body.video_sha256!==id)return fail(409,'La autorización corresponde a otro archivo');
 const row=await env.DB.prepare('SELECT * FROM youtube_exports WHERE id=?').bind(id).first();
 if(!row||!reviewed(row,id))return fail(409,'Se requiere video subido como privado y revisión completa del archivo exacto');
 const old=await env.DB.prepare('SELECT * FROM youtube_publications WHERE export_id=?').bind(id).first();
 if(old&&old.request_id===body.request_id)return {ok:true,reused:true,publication:view(old)};
 if(old&&old.state!=='failed')return fail(409,'Ya existe una autorización. Comprueba su resultado antes de repetir.');
 const conn=await youtubeConnectionStatus(env);
 if(!conn.connected||conn.channel.id!==row.target_channel_id)return fail(409,'El canal conectado no coincide con la subida');
 if(!conn.publication_scope_granted)return fail(409,'Amplía los permisos de Google para publicar o programar');
 const token=await youtubeAccessToken(env,{googleFetch});if(!token.ok)return token;
 let current;
 try{current=await video(env,token.access_token,row.video_id,googleFetch);}catch{return fail(502,'No se pudo verificar el video antes de publicar');}
 if(current?.id!==row.video_id||current.snippet?.channelId!==row.target_channel_id||current.status?.privacyStatus!=='private'||current.status?.publishAt)
  return fail(409,'El video cambió o ya tiene una publicación programada. Revisa YouTube.');
 const again=await youtubeConnectionStatus(env);if(!again.connected||again.channel.id!==row.target_channel_id)return fail(409,'La conexión cambió');
 const reserve=await env.DB.prepare(`INSERT INTO youtube_publications(export_id,request_id,video_id,channel_id,mode,publish_at,reviewer,state)
 SELECT ?,?,?,?,?,?,?,'reserved' WHERE EXISTS(SELECT 1 FROM youtube_exports WHERE id=? AND state='uploaded' AND review_json=?)
 ON CONFLICT(export_id) DO UPDATE SET request_id=excluded.request_id,mode=excluded.mode,publish_at=excluded.publish_at,
 reviewer=excluded.reviewer,state='reserved',last_error='',updated_at=datetime('now') WHERE youtube_publications.state='failed' AND youtube_publications.request_id<>excluded.request_id`)
 .bind(id,body.request_id,row.video_id,row.target_channel_id,intent.mode,intent.publish_at,intent.reviewer,id,row.review_json).run();
 if(reserve.meta?.changes!==1)return fail(409,'La autorización ya fue reservada o la revisión cambió');
 await env.DB.prepare("INSERT INTO youtube_export_events(export_id,action,note) VALUES(?,'publication_authorized',?)")
  .bind(id,JSON.stringify({...intent,request_id:body.request_id,video_sha256:id})).run();
 const metadata=JSON.parse(row.metadata_json),status={};
 for(const k of ['license','embeddable','publicStatsViewable'])if(current.status[k]!==undefined)status[k]=current.status[k];
 Object.assign(status,{privacyStatus:intent.mode==='public'?'public':'private',selfDeclaredMadeForKids:metadata.madeForKids,containsSyntheticMedia:metadata.containsSyntheticMedia});
 if(intent.publish_at)status.publishAt=intent.publish_at;
 try{
  const headers={Authorization:'Bearer '+token.access_token,'Content-Type':'application/json'};
  if(typeof current.etag==='string'&&current.etag.length<150&&!/[\r\n]/.test(current.etag))headers['If-Match']=current.etag;
  const result=await googleFetch(API+'?part=status',{method:'PUT',headers,redirect:'manual',signal:AbortSignal.timeout(12000),body:JSON.stringify({id:row.video_id,status})});
  if(!result.ok){await result.body?.cancel();await env.DB.prepare("UPDATE youtube_publications SET state='failed',last_error='Google rechazó la operación' WHERE export_id=? AND request_id=?").bind(id,body.request_id).run();return fail(502,'Google rechazó la publicación; revisa permisos y políticas del canal');}
  await result.body?.cancel();
 }catch{
  await env.DB.prepare("UPDATE youtube_publications SET state='unknown',last_error='Resultado incierto; consultar YouTube sin repetir' WHERE export_id=? AND request_id=?").bind(id,body.request_id).run();
  return {ok:true,publication:{...intent,state:'unknown'},notice:'Comprueba el resultado antes de repetir. No se enviará otra publicación.'};
 }
 return reconcilePublication(env,id,{googleFetch});
}
