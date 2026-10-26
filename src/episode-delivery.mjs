// Recover registration of an existing export. Never runs research, TTS or render.
import {previewFromEvents} from './episode-production.mjs';
const UUID=/^[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}$/;
const REPO='eler30mr-star/FactordeGigantes';
const fail=(status,error)=>({ok:false,status,error});
async function preview(db,jobId){
 const event=await db.prepare("SELECT action,note FROM events WHERE job_id=? AND action='episode_preview_ready' ORDER BY id DESC LIMIT 1").bind(jobId).first();
 return event?previewFromEvents([event]):null;
}
export async function episodeDeliveryStatus(db,jobId){
 const row=await db.prepare("SELECT note,created_at<datetime('now','-15 minutes') AS stale FROM events WHERE job_id=? AND action='episode_delivery_requested' ORDER BY id DESC LIMIT 1").bind(jobId).first();
 if(!row)return null;
 const note=JSON.parse(row.note);
 const result=await db.prepare(`SELECT action FROM events WHERE job_id=?
  AND action IN ('episode_delivery_failed','episode_delivery_ready','episode_delivery_rejected','episode_delivery_unknown','episode_delivery_sent')
  AND json_extract(note,'$.request_id')=?
  ORDER BY CASE WHEN action IN ('episode_delivery_failed','episode_delivery_ready','episode_delivery_rejected') THEN 0 ELSE 1 END,id DESC LIMIT 1`)
  .bind(jobId,note.request_id).first();
 let state=result?result.action.replace('episode_delivery_',''):'reserved';
 if(row.stale&&['reserved','sent'].includes(state))state='unknown';
 return {...note,state};
}
export async function recoverEpisodeVideo(env,episodeId,fetcher=fetch){
 if(typeof episodeId!=='string'||!UUID.test(episodeId))throw new RangeError('Episodio inválido');
 const job=await env.DB.prepare(`SELECT j.id,j.status FROM channel_episodes e
  JOIN channel_episode_research r ON r.episode_id=e.id JOIN jobs j ON j.id=r.job_id
  WHERE e.id=? AND e.channel='factor-de-gigantes' ORDER BY r.rowid DESC LIMIT 1`).bind(episodeId).first();
 if(!job||job.status!=='ready')return fail(409,'Todavía no existe un montaje terminado de este episodio.');
 const p=await preview(env.DB,job.id);
 if(!p)return fail(409,'Falta la confirmación del montaje; no se elegirá otra ejecución.');
 const runId=p.run_url.split('/').at(-1);
 const existing=await env.DB.prepare('SELECT id FROM youtube_exports WHERE id=? AND source_run_id=?').bind(p.sha256,runId).first();
 if(existing)return {ok:true,reused:true,started:false,automatic_publication_allowed:false};
 if(env.GITHUB_REPO!==REPO||typeof env.GITHUB_DISPATCH_TOKEN!=='string'||env.GITHUB_DISPATCH_TOKEN.length<24)
  return fail(503,'Acceso Actions no configurado.');
 const requestId=crypto.randomUUID(),note=JSON.stringify({request_id:requestId,run_id:runId,export_sha256:p.sha256});
 const reserved=await env.DB.prepare(`INSERT INTO events(job_id,action,note)
  SELECT ?,'episode_delivery_requested',? WHERE EXISTS(SELECT 1 FROM jobs WHERE id=? AND status='ready')
  AND NOT EXISTS(SELECT 1 FROM events a WHERE a.job_id=? AND a.action='episode_delivery_requested'
   AND NOT EXISTS(SELECT 1 FROM events b WHERE b.job_id=a.job_id
    AND b.action IN ('episode_delivery_failed','episode_delivery_rejected','episode_delivery_ready')
    AND json_extract(b.note,'$.request_id')=json_extract(a.note,'$.request_id')))`)
  .bind(job.id,note,job.id,job.id).run();
 if(reserved.meta?.changes!==1)return {ok:true,started:false,reason:'delivery_running',automatic_publication_allowed:false};
 const record=action=>env.DB.prepare('INSERT INTO events(job_id,action,note) VALUES(?,?,?)').bind(job.id,action,note).run();
 let response;
 try{response=await fetcher('https://api.github.com/repos/'+REPO+'/actions/workflows/register-finished-episode.yml/dispatches',{
  method:'POST',redirect:'manual',signal:AbortSignal.timeout(10000),headers:{Authorization:'Bearer '+env.GITHUB_DISPATCH_TOKEN,
   Accept:'application/vnd.github+json','Content-Type':'application/json','User-Agent':'FactorDeGigantes-Delivery'},
  body:JSON.stringify({ref:'main',inputs:{source_run_id:runId,job_id:job.id,delivery_request_id:requestId}})});
 }catch{await record('episode_delivery_unknown');return {ok:true,started:false,reason:'dispatch_unknown',automatic_publication_allowed:false};}
 if(response.status!==204){await record('episode_delivery_rejected');return fail(502,'Actions rechazó la recuperación del video.');}
 await record('episode_delivery_sent');
 return {ok:true,started:true,request_id:requestId,automatic_publication_allowed:false};
}
export async function reportEpisodeDelivery(env,jobId,body){
 if(typeof body?.request_id!=='string'||!UUID.test(body.request_id)||!['ready','failed'].includes(body.status))throw new RangeError('Entrega inválida');
 const current=await episodeDeliveryStatus(env.DB,jobId);
 if(!current||current.request_id!==body.request_id)return fail(409,'Solicitud de entrega sustituida o inexistente.');
 const p=await preview(env.DB,jobId);
 if(!p||p.sha256!==current.export_sha256||p.run_url.split('/').at(-1)!==current.run_id)return fail(409,'El montaje cambió.');
 const registered=await env.DB.prepare('SELECT id FROM youtube_exports WHERE id=? AND source_run_id=?').bind(p.sha256,current.run_id).first();
 if(body.status==='ready'&&!registered)return fail(409,'El video aún no está registrado.');
 if(['ready','failed','rejected'].includes(current.state))return {ok:true,reused:true,automatic_publication_allowed:false};
 const status=registered?'ready':body.status;
 await env.DB.prepare(`INSERT INTO events(job_id,action,note) SELECT ?,?,?
  WHERE NOT EXISTS(SELECT 1 FROM events WHERE job_id=? AND action IN ('episode_delivery_ready','episode_delivery_failed','episode_delivery_rejected') AND json_extract(note,'$.request_id')=?)`)
  .bind(jobId,'episode_delivery_'+status,JSON.stringify(current),jobId,body.request_id).run();
 return {ok:true,automatic_publication_allowed:false};
}
