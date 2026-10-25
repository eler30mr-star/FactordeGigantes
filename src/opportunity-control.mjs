import {assessOpportunityStudy} from './opportunity-study.mjs';
const CHANNEL='factor-de-gigantes',UUID=/^[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}$/;
const fail=(status,error)=>({ok:false,status,error});
export async function beginOpportunityStudy(env,body,now=new Date()){
 if(!body||typeof body.id!=='string'||!UUID.test(body.id))throw new RangeError('Estudio inválido');
 if(env.FINAL_AI_INTEGRATION_ENABLED!=='1')return {ok:true,allowed:false,reason:'research_paused'};
 const control=await env.DB.prepare('SELECT automatic_enabled,revision FROM channel_control WHERE channel=?').bind(CHANNEL).first();
 if(control?.automatic_enabled!==1)return {ok:true,allowed:false,reason:'automatic_off'};
 const day=now.toISOString().slice(0,10);
 const inserted=await env.DB.prepare(`INSERT OR IGNORE INTO channel_opportunity_studies(id,channel,day_utc,mode_revision)
 SELECT ?,?,?,? WHERE EXISTS(SELECT 1 FROM channel_control WHERE channel=? AND automatic_enabled=1 AND revision=?)
 AND NOT EXISTS(SELECT 1 FROM channel_episodes WHERE channel=? AND state NOT IN ('completed','cancelled'))`)
 .bind(body.id,CHANNEL,day,control.revision,CHANNEL,control.revision,CHANNEL).run();
 return {ok:true,allowed:inserted.meta?.changes===1,id:body.id,mode_revision:control.revision,
  reason:inserted.meta?.changes===1?'study_reserved':'already_studied_or_episode_active',
  calibration_only:env.YOUTUBE_SELECTOR_VALIDATED!=='1'};
}
export async function finishOpportunityStudy(env,body,now=new Date()){
 if(!body||typeof body.id!=='string'||!UUID.test(body.id))throw new RangeError('Estudio inválido');
 const run=await env.DB.prepare('SELECT * FROM channel_opportunity_studies WHERE id=? AND channel=?').bind(body.id,CHANNEL).first();
 if(!run)return fail(404,'Estudio no reservado');
 if(run.state!=='running')return {ok:true,replayed:true,state:run.state,assessment:JSON.parse(run.assessment_json)};
 const history=await env.DB.prepare("SELECT company FROM channel_episodes WHERE channel=? AND created_at>=datetime('now','-30 days') AND state<>'cancelled' LIMIT 30").bind(CHANNEL).all();
 const assessment=assessOpportunityStudy(body.report,now,(history.results||[]).map(x=>x.company));
 if(body.report.observed_on!==run.day_utc)throw new RangeError('El estudio no corresponde al día reservado');
 const chosen=assessment.selected;
 const state=env.FINAL_AI_INTEGRATION_ENABLED!=='1'?'cancelled':env.YOUTUBE_SELECTOR_VALIDATED!=='1'?'calibration':chosen?'selected':'insufficient';
 const active="EXISTS(SELECT 1 FROM channel_control WHERE channel=? AND automatic_enabled=1 AND revision=?)";
 const statements=[env.DB.prepare(`UPDATE channel_opportunity_studies SET report_json=?,assessment_json=?,
 state=CASE WHEN ${active} THEN ? ELSE 'cancelled' END,updated_at=datetime('now') WHERE id=? AND state='running'`)
 .bind(JSON.stringify(body.report),JSON.stringify(assessment),CHANNEL,run.mode_revision,state,run.id)];
 if(chosen&&state==='selected'){
  statements.push(env.DB.prepare(`INSERT OR IGNORE INTO channel_episodes(id,channel,origin,company,topic,instruction)
   SELECT ?,?,'automatic',?,?,? WHERE ${active} AND EXISTS(SELECT 1 FROM channel_opportunity_studies WHERE id=? AND state='selected')
   AND NOT EXISTS(SELECT 1 FROM channel_episodes WHERE channel=? AND state NOT IN ('completed','cancelled'))`)
   .bind(run.id,CHANNEL,chosen.company,chosen.topic,chosen.rationale,CHANNEL,run.mode_revision,run.id,CHANNEL));
  statements.push(env.DB.prepare(`UPDATE channel_opportunity_studies SET state='cancelled' WHERE id=? AND state='selected'
   AND NOT EXISTS(SELECT 1 FROM channel_episodes WHERE id=?)`).bind(run.id,run.id));
 }
 await env.DB.batch(statements);
 const saved=await env.DB.prepare('SELECT state,assessment_json FROM channel_opportunity_studies WHERE id=?').bind(run.id).first();
 return {ok:true,state:saved.state,assessment:JSON.parse(saved.assessment_json),publication_authorized:false};
}
export async function latestOpportunityStudy(env){
 const r=await env.DB.prepare('SELECT id,day_utc,state,assessment_json FROM channel_opportunity_studies WHERE channel=? ORDER BY day_utc DESC LIMIT 1').bind(CHANNEL).first();
 return {ok:true,study:r?{id:r.id,observed_on:r.day_utc,state:r.state,...JSON.parse(r.assessment_json)}:null};
}

export async function checkOpportunityStudy(env,body){
 if(!body||typeof body.id!=='string'||!UUID.test(body.id))throw new RangeError('Estudio inválido');
 const current=await env.DB.prepare(`SELECT s.id FROM channel_opportunity_studies s JOIN channel_control c ON c.channel=s.channel
  WHERE s.id=? AND s.state='running' AND s.day_utc=date('now') AND c.automatic_enabled=1 AND c.revision=s.mode_revision
  AND NOT EXISTS(SELECT 1 FROM channel_episodes e WHERE e.channel=s.channel AND e.state NOT IN ('completed','cancelled'))`).bind(body.id).first();
 return {ok:true,allowed:!!current&&env.FINAL_AI_INTEGRATION_ENABLED==='1'};
}

export async function failOpportunityStudy(env,body){
 if(!body||typeof body.id!=='string'||!UUID.test(body.id)||body.reason!=='study_incomplete')throw new RangeError('Fallo de estudio inválido');
 const existing=await env.DB.prepare('SELECT state,assessment_json FROM channel_opportunity_studies WHERE id=? AND channel=?').bind(body.id,CHANNEL).first();
 if(!existing)return fail(404,'Estudio no reservado');
 if(existing.state!=='running')return {ok:true,state:existing.state,replayed:true,assessment:JSON.parse(existing.assessment_json)};
 const assessment={reason:'study_incomplete',rankings:[],selected:null,
  limitations:['No se completó el estudio. Revisar disponibilidad de datos, analista gratuito y cuotas.'],publication_authorized:false};
 await env.DB.prepare(`UPDATE channel_opportunity_studies SET state='insufficient',assessment_json=?,updated_at=datetime('now')
  WHERE id=? AND channel=? AND state='running'`).bind(JSON.stringify(assessment),body.id,CHANNEL).run();
 return {ok:true,state:'insufficient',assessment,publication_authorized:false};
}
