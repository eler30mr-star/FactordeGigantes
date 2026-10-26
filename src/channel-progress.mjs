import {previewFromEvents} from './episode-production.mjs';
const UUID=/^[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}$/;
const fail=(status,error)=>({ok:false,status,error});

// Read the chosen episode's lineage, never the latest unrelated production run.
export async function channelProgress(env,id){
 if(typeof id!=='string'||!UUID.test(id))throw new RangeError('Episodio inválido');
 const episode=await env.DB.prepare("SELECT id,company,topic,origin,state FROM channel_episodes WHERE id=? AND channel='factor-de-gigantes'").bind(id).first();
 if(!episode)return fail(404,'Episodio inexistente');
 const research=await env.DB.prepare('SELECT id,state,note,research_run_id,job_id FROM channel_episode_research WHERE episode_id=? ORDER BY rowid DESC LIMIT 1').bind(id).first();
 const job=research?.job_id?await env.DB.prepare('SELECT id,title,status,review_note,last_error FROM jobs WHERE id=?').bind(research.job_id).first():null;
 let checkpointStage='script';
 let focusQuestions=[];
 let focusReason=null;
 if(research?.research_run_id&&!job){
  const checkpoint=await env.DB.prepare(`SELECT
   json_array_length(report_json,'$.candidate_claims') AS claims,
   json_array_length(report_json,'$.evidence_manifest') AS passages,
   json_array_length(report_json,'$.reviews') AS reviews,
   json_extract(report_json,'$.editorial_focus_review.status') AS focus_status,
   json_extract(report_json,'$.editorial_focus_review.reason') AS focus_reason,
   json_extract(report_json,'$.editorial_focus_review.research_questions') AS focus_questions,
   EXISTS(SELECT 1 FROM json_each(report_json,'$.source_quality.claim_gaps') WHERE json_array_length(value,'$.gaps')>0) AS missing_sources
   FROM market_ai_pipeline_runs WHERE id=?`).bind(research.research_run_id).first();
  if(checkpoint&&(['misaligned','unavailable'].includes(checkpoint.focus_status)||
      (checkpoint.focus_status==='aligned'&&checkpoint.claims>0&&checkpoint.claims<6))){
   checkpointStage='focus';
   focusReason=checkpoint.focus_reason;
   try{const questions=JSON.parse(checkpoint.focus_questions||'[]');if(Array.isArray(questions))focusQuestions=questions.filter(q=>typeof q==='string'&&q.length<=220).slice(0,4);}catch{}
  }
  else if(checkpoint&&checkpoint.claims===0)checkpointStage=checkpoint.passages>0?'analysis':'corroboration';
  else if(checkpoint?.missing_sources)checkpointStage='corroboration';
  else if(checkpoint&&checkpoint.reviews<checkpoint.claims)checkpointStage='review';
 }
 let dossier=null,preview=null,video=null,publication=null;
 if(job){
  dossier=await env.DB.prepare('SELECT editor_attested,editor_name FROM editorial_dossiers WHERE job_id=?').bind(job.id).first();
  const events=await env.DB.prepare("SELECT action,note FROM events WHERE job_id=? AND action='episode_preview_ready' ORDER BY id DESC LIMIT 1").bind(job.id).all();
  preview=previewFromEvents(events.results);
  if(preview){
   const runId=preview.run_url.split('/').at(-1);
   video=await env.DB.prepare('SELECT id,state,last_error,video_id,target_channel_id FROM youtube_exports WHERE id=? AND source_run_id=?').bind(preview.sha256,runId).first();
   if(video)publication=await env.DB.prepare('SELECT state,mode,publish_at,last_error,video_id,channel_id FROM youtube_publications WHERE export_id=?').bind(video.id).first();
  }
 }
 const paused=env.FINAL_AI_INTEGRATION_ENABLED!=='1';
 const steps=[['selection','Elección'],['research','Investigación'],['script','Guion y revisión'],['production','Voz y montaje'],['video','Video y revisión final'],['publication','Publicación']]
  .map(([id,label])=>({id,label,state:'pending'}));
 steps[0].state='done';
 steps[1].state='current';
 let next='start_research',message='Investigar únicamente la empresa y el enfoque elegidos.';
 if(research){
  const saved=!!research.research_run_id;
  steps[1].state=saved?'done':'current';
  if(saved)steps[2].state='current';
  if(saved&&['corroboration','analysis','focus'].includes(checkpointStage)){steps[1].state='current';steps[2].state='pending';}
  next='wait';message=saved?'La investigación está guardada. Preparando el guion.':'Buscando y contrastando fuentes del episodio.';
  if(['blocked','rejected'].includes(research.state)){
   steps[saved?2:1].state='blocked';next='resume_research';
   message=saved?'El guion se interrumpió. Puedes reanudarlo conservando la investigación.':'La investigación se interrumpió. Puedes reintentar esta misma elección.';
   if(saved&&checkpointStage==='corroboration'){steps[1].state='blocked';steps[2].state='pending';message='La investigación está guardada, pero falta contraste. Puedes completar las fuentes de este mismo episodio.';}
   else if(saved&&checkpointStage==='analysis'){steps[1].state='blocked';steps[2].state='pending';message='Las fuentes están guardadas. Puedes reanudar el análisis sin volver a descargarlas.';}
   else if(saved&&checkpointStage==='focus'){steps[1].state='blocked';steps[2].state='pending';message='Falta comprobar o completar la relación de las afirmaciones con el enfoque elegido. La empresa y el tema se conservan.';}
   if(checkpointStage==='focus'&&focusReason==='budget_denied')message='Se alcanzó un límite configurado de solicitudes IA. Las fuentes y los hechos quedan guardados para reanudar la revisión del enfoque.';
   else if(saved&&checkpointStage==='review')message='Las fuentes están guardadas. Puedes reanudar su revisión sin repetir las búsquedas.';
  }else if(research.state==='unknown'){
   steps[saved?2:1].state='blocked';next='check_dispatch';message='No se confirmó el envío. Revisa Actions antes de repetir para evitar duplicados.';
  }
 }
 if(job){
  steps[1].state='done';steps[2].state='current';
  const states={draft:['submit_script','El guion está listo. Léelo y envíalo a revisión.'],review:['review_dossier','Revisa las fuentes, las afirmaciones y los derechos del guion.'],
   approved:['render','Guion aprobado. Puedes autorizar la narración y el montaje.'],queued:['wait','Producción solicitada. Esperando el inicio del montaje.'],
   rendering:['wait','Generando narración, escenas y montaje del episodio.'],failed:['retry_render','El montaje se interrumpió. Reanuda conservando las escenas válidas.'],
   ready:['wait','Montaje terminado. Registrando el archivo para reproducirlo en el panel.']};
  [next,message]=states[job.status]||['wait','Consulta el estado del trabajo editorial.'];
  if(job.status==='review'&&dossier?.editor_attested===1&&dossier.editor_name){next='approve_script';message='Revisión editorial confirmada. Puedes aprobar este guion.';}
  if(['approved','queued','rendering','failed','ready'].includes(job.status))steps[2].state='done';
  if(['queued','rendering'].includes(job.status))steps[3].state='current';
  if(job.status==='failed')steps[3].state='blocked';
  if(job.status==='ready'){steps[3].state='done';steps[4].state=video?'current':'pending';}
 }
 if(video&&job?.status==='ready'){
  next='review_video';message='El video de este episodio está disponible para reproducir y revisar.';
  if(video.state==='approved'){steps[4].state='done';next='upload_video';message='Revisión final aprobada. Puedes autorizar la subida privada.';}
  if(['queued','initiating','uploading','unknown'].includes(video.state)){
   steps[4].state='done';steps[5].state=video.state==='unknown'?'blocked':'current';next='check_upload';message='Consulta o reanuda la misma subida privada, sin crear otra.';
  }
  if(video.state==='uploaded'){steps[4].state='done';steps[5].state='current';next='publish_video';message='Video subido como privado. Falta autorizar su publicación o programación.';}
  if(publication?.state==='confirmed'&&video.state==='uploaded'&&publication.video_id===video.video_id&&publication.channel_id===video.target_channel_id){steps[5].state='done';next='complete';message=publication.mode==='scheduled'?'Programación confirmada por YouTube.':'Publicación confirmada por YouTube.';}
  else if(publication){next='check_publication';message=publication.state==='unknown'?'Publicación incierta. Comprueba YouTube antes de repetir.':'Consulta el resultado de la autorización de publicación.';if(publication.state==='unknown'||publication.state==='failed')steps[5].state='blocked';}
 }
 const blockedByPause=paused&&['start_research','resume_research'].includes(next);
 if(blockedByPause){steps[research?.research_run_id&&!['corroboration','analysis','focus'].includes(checkpointStage)?2:1].state='blocked';message+=' La investigación sigue pausada; la elección y los resultados se conservan.';}
 return {ok:true,episode,research:research?{id:research.id,state:research.state,checkpoint_available:!!research.research_run_id,checkpoint_stage:checkpointStage,editorial_questions:focusQuestions}:null,
  job,steps,next_step:next,message,research_paused:paused,action_enabled:!blockedByPause,
  preview:video&&job?.status==='ready'?{export_id:video.id,state:video.state}:null,publication,publication_authorized:false};
}

// Closing frees the single-episode slot; it cannot publish or approve anything.
export async function completeChannelEpisode(env,body){
 if(body?.confirmed!==true)return fail(400,'Confirma el cierre del episodio');
 const progress=await channelProgress(env,body.episode_id);if(!progress.ok)return progress;
 if(progress.episode.state==='completed')return {ok:true,reused:true};
 if(progress.next_step!=='complete'||!progress.preview||!progress.job)return fail(409,'Falta publicación o programación confirmada de este episodio');
 const result=await env.DB.batch([
  env.DB.prepare(`UPDATE channel_episodes SET state='completed',updated_at=datetime('now')
   WHERE id=? AND state IN ('review','producing') AND EXISTS(
    SELECT 1 FROM channel_episode_research r JOIN jobs j ON j.id=r.job_id
    JOIN events ev ON ev.job_id=j.id AND ev.action='episode_preview_ready'
    JOIN youtube_exports x ON x.id=json_extract(ev.note,'$.export_sha256')
     AND x.source_run_id=json_extract(ev.note,'$.run_id')
    JOIN youtube_publications p ON p.export_id=x.id AND p.state='confirmed'
     AND p.video_id=x.video_id AND p.channel_id=x.target_channel_id
    WHERE r.episode_id=channel_episodes.id AND j.id=? AND j.status='ready' AND x.state='uploaded' AND x.id=?)`)
   .bind(body.episode_id,progress.job.id,progress.preview.export_id),
  env.DB.prepare("INSERT INTO events(job_id,action,note) SELECT ?,'channel_episode_completed',? WHERE changes()=1")
   .bind(progress.job.id,body.episode_id)
 ]);
 return result[0].meta?.changes===1?{ok:true,reused:false}:fail(409,'El episodio cambió antes de cerrarse');
}
