import {storeAiReport} from './ai-research-team.mjs';
import {prepareEditorialDraft} from './autonomous-script-drafts.mjs';
const UUID=/^[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}$/;
const fail=(status,error)=>({ok:false,status,error});
const valid=id=>typeof id==='string'&&UUID.test(id);
export async function dispatchChannelResearch(env,episodeId,fetcher=fetch){
 if(!valid(episodeId))throw new RangeError('Episodio inválido');
 if(env.FINAL_AI_INTEGRATION_ENABLED!=='1')return {ok:true,started:false,reason:'research_paused'};
 if(env.GITHUB_REPO!=='eler30mr-star/FactordeGigantes'||typeof env.GITHUB_DISPATCH_TOKEN!=='string'||env.GITHUB_DISPATCH_TOKEN.length<24)
  return fail(503,'Acceso Actions no configurado');
 const id=crypto.randomUUID();
 const created=await env.DB.prepare(`INSERT OR IGNORE INTO channel_episode_research(id,episode_id,state)
 SELECT ?,?,'reserved' WHERE EXISTS(SELECT 1 FROM channel_episodes WHERE id=? AND state='selected')
 AND (SELECT count(*) FROM channel_episode_research WHERE created_at>=date('now'))<4`)
 .bind(id,episodeId,episodeId).run();
 if(created.meta?.changes!==1)return {ok:true,started:false,reason:'already_running_or_daily_limit'};
 let response;
 try{response=await fetcher('https://api.github.com/repos/eler30mr-star/FactordeGigantes/actions/workflows/topic-discovery-smoke.yml/dispatches',{
  method:'POST',redirect:'manual',signal:AbortSignal.timeout(10000),headers:{Authorization:'Bearer '+env.GITHUB_DISPATCH_TOKEN,
   'Content-Type':'application/json',Accept:'application/vnd.github+json','User-Agent':'FactorDeGigantes-Episode'},
  body:JSON.stringify({ref:'main',inputs:{phase:'episode',episode_id:episodeId,episode_request_id:id}})});
 }catch{
  await env.DB.prepare("UPDATE channel_episode_research SET state='unknown',note='Despacho incierto; revisar Actions antes de repetir' WHERE id=? AND state='reserved'").bind(id).run();
  return {ok:true,started:false,reason:'dispatch_unknown',request_id:id};
 }
 if(response.status!==204){
  await env.DB.prepare("UPDATE channel_episode_research SET state='rejected',note='Actions rechazó la solicitud' WHERE id=? AND state='reserved'").bind(id).run();
  return fail(502,'Actions rechazó la investigación del episodio');
 }
 await env.DB.batch([
  env.DB.prepare("UPDATE channel_episode_research SET state='sent' WHERE id=? AND state='reserved'").bind(id),
  env.DB.prepare("UPDATE channel_episodes SET state='researching',updated_at=datetime('now') WHERE id=? AND state='selected'").bind(episodeId)
 ]);
 return {ok:true,started:true,request_id:id};
}
export async function channelResearchContext(env,body){
 if(!body||!valid(body.request_id))throw new RangeError('Solicitud inválida');
 const r=await env.DB.prepare(`SELECT r.id,r.state,e.id AS episode_id,e.company,e.topic,e.origin FROM channel_episode_research r
 JOIN channel_episodes e ON e.id=r.episode_id WHERE r.id=? AND e.state IN ('selected','researching')`).bind(body.request_id).first();
 if(!r)return fail(404,'Episodio no reservado');
 return {ok:true,allowed:env.FINAL_AI_INTEGRATION_ENABLED==='1'&&['reserved','sent','unknown'].includes(r.state),episode:r};
}
export async function storeChannelResearch(env,body){
 const context=await channelResearchContext(env,body);if(!context.ok)return context;
 const episode=context.episode;
 if(!context.allowed)return fail(409,'Investigación pausada o solicitud ya terminada');
 if(body.blocked===true){
  await env.DB.batch([
   env.DB.prepare("UPDATE channel_episode_research SET state='blocked',note='Identidad o fuentes insuficientes; revisar antes de reintentar' WHERE id=? AND state IN ('reserved','sent','unknown')").bind(body.request_id),
   env.DB.prepare("UPDATE channel_episodes SET state='selected',updated_at=datetime('now') WHERE id=? AND state IN ('selected','researching')").bind(episode.episode_id)
  ]);return {ok:true,state:'blocked'};
 }
 if(body.report?.editorial_topic!==episode.topic||body.report?.selected_episode_id!==episode.episode_id||
    body.report?.company!==episode.company)throw new RangeError('La investigación no corresponde al episodio elegido');
 const stored=await storeAiReport(env.DB,body.report,{updateLegacyQueue:false});
 await env.DB.prepare('UPDATE channel_episode_research SET research_run_id=? WHERE id=? AND state IN (\'reserved\',\'sent\',\'unknown\')')
  .bind(stored.run_id,body.request_id).run();
 return {...stored,episode_id:episode.episode_id};
}
export async function storeChannelScript(env,body){
 const context=await channelResearchContext(env,body);if(!context.ok)return context;
 if(!context.allowed)return fail(409,'Investigación pausada o solicitud terminada');
 const run=await env.DB.prepare('SELECT research_run_id FROM channel_episode_research WHERE id=?').bind(body.request_id).first();
 if(!run?.research_run_id)return fail(409,'Falta investigación del episodio');
 const parent=await env.DB.prepare('SELECT report_json FROM market_ai_pipeline_runs WHERE id=?').bind(run.research_run_id).first();
 const report=JSON.parse(parent.report_json),s=body.script;
 const bundle=await prepareEditorialDraft(report,s,run.research_run_id);
 const id=crypto.randomUUID();
 // Work + dossier + trace + episode transition are committed together.
 const done=await env.DB.batch([
  env.DB.prepare(`INSERT INTO jobs(id,title,format,status,manifest_json) SELECT ?,?,'long','draft',?
   WHERE EXISTS(SELECT 1 FROM channel_episode_research WHERE id=? AND state IN ('reserved','sent','unknown') AND job_id IS NULL)`)
   .bind(id,bundle.manifest.title,JSON.stringify(bundle.manifest),body.request_id),
  env.DB.prepare(`INSERT INTO autonomous_script_drafts(research_run_id,job_id,wikidata_id,script_sha256,source_evidence_sha256,script_json)
   SELECT ?,?,?,?,?,? WHERE EXISTS(SELECT 1 FROM jobs WHERE id=?)`)
   .bind(run.research_run_id,id,report.selected_wikidata_id,bundle.script_sha256,s.source_evidence_sha256,JSON.stringify(s),id),
  env.DB.prepare('INSERT INTO editorial_dossiers(job_id,dossier_json) SELECT ?,? WHERE EXISTS(SELECT 1 FROM jobs WHERE id=?)').bind(id,JSON.stringify(bundle.dossier),id),
  env.DB.prepare("INSERT INTO events(job_id,action,note) SELECT ?,'autonomous_draft_created','Episodio elegido; fuentes y derechos pendientes de revisión' WHERE EXISTS(SELECT 1 FROM jobs WHERE id=?)").bind(id,id),
  env.DB.prepare("UPDATE channel_episode_research SET job_id=?,state='review',note='Guion listo para revisión',updated_at=datetime('now') WHERE id=? AND EXISTS(SELECT 1 FROM jobs WHERE id=?)").bind(id,body.request_id,id),
  env.DB.prepare("UPDATE channel_episodes SET state='review',updated_at=datetime('now') WHERE id=? AND EXISTS(SELECT 1 FROM jobs WHERE id=?)").bind(context.episode.episode_id,id)
 ]);
 const saved=await env.DB.prepare('SELECT job_id FROM channel_episode_research WHERE id=?').bind(body.request_id).first();
 return saved?.job_id?{ok:true,job_id:saved.job_id,created:done[0].meta?.changes===1,publication_authorized:false}:fail(409,'La investigación cambió antes de guardar el guion');
}
export async function channelResearchStatus(env,episodeId){
 if(!valid(episodeId))throw new RangeError('Episodio inválido');
 const result=await env.DB.prepare('SELECT r.id,r.state,r.note,r.research_run_id,r.job_id,r.created_at,j.status AS job_status FROM channel_episode_research r LEFT JOIN jobs j ON j.id=r.job_id WHERE r.episode_id=? ORDER BY r.created_at DESC,r.rowid DESC LIMIT 1').bind(episodeId).first();
 return {ok:true,run:result??null};
}
