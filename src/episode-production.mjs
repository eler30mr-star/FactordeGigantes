// Entrega al motor genérico; no concede revisión factual ni publicación.
import {evidenceLinkSha256} from './autonomous-script-drafts.mjs';
import voiceReference from '../assets/voice/approved/reference.json' with {type:'json'};
const SHA=/^[a-f0-9]{64}$/;
export async function manifestSha(text){
 return [...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(text)))]
  .map(x=>x.toString(16).padStart(2,'0')).join('');
}
const normalized=text=>text.replace(/\s+/gu,' ').trim();

export async function readEpisodeInput(db,row){
 const origin=await db.prepare('SELECT research_run_id,script_json FROM autonomous_script_drafts WHERE job_id=?').bind(row.id).first();
 if(!origin)return {ok:false,status:404,reason:'autonomous_episode_required'};
 if(!['queued','rendering'].includes(row.status))return {ok:false,status:409,reason:'approved_dispatch_required'};
 const parent=await db.prepare('SELECT report_json FROM market_ai_pipeline_runs WHERE id=?').bind(origin.research_run_id).first();
 if(!parent)return {ok:false,status:409,reason:'missing_research_lineage'};
 const script=JSON.parse(origin.script_json),research=JSON.parse(parent.report_json),manifest=JSON.parse(row.manifest_json);
 if(script.source_research_run_id!==origin.research_run_id||script.wikidata_id!==research.selected_wikidata_id||
    script.source_evidence_sha256!==await evidenceLinkSha256(research))
  return {ok:false,status:409,reason:'research_lineage_changed'};
 const original=normalized(script.scenes.flatMap(s=>s.paragraphs.map(p=>p.text)).join(' '));
 if(normalized(manifest.segments.map(s=>s.voiceover).join(' '))!==original)
  return {ok:false,status:409,reason:'edited_narration_requires_trace_update'};
 return {ok:true,job_id:row.id,script,research,manifest,
  approved_manifest_sha256:await manifestSha(row.manifest_json),automatic_publication_allowed:false};
}

export function previewFromEvents(events){
 for(const event of events){
  if(event.action!=='episode_preview_ready')continue;
  try{
   const note=JSON.parse(event.note);
   if(typeof note.run_id!=='string'||!/^\d{1,20}$/.test(note.run_id)||
      typeof note.export_sha256!=='string'||!SHA.test(note.export_sha256))return null;
   return {run_url:'https://github.com/eler30mr-star/FactordeGigantes/actions/runs/'+note.run_id,
    sha256:note.export_sha256,seconds:note.seconds,contains_narration:true,publication_authorized:false};
  }catch{return null;}
 }
 return null;
}

export async function acceptEpisodeExport(db,row,body){
 const r=body.export;
 if(body.status!=='ready'||!r||r.schema!=='fdg_episode_export_v1'||
    typeof r.sha256!=='string'||!SHA.test(r.sha256)||typeof r.episode_sha256!=='string'||!SHA.test(r.episode_sha256)||
    r.approved_manifest_sha256!==await manifestSha(row.manifest_json)||
    r.canonical_reference_sha256!==voiceReference.sha256||r.canonical_reference_unchanged!==true||
    r.contains_narration!==true||r.voice_kind!=='canonical_qwen_pending_audition'||
    r.technical_gate_passed!==true||r.publication_authorized!==false||
    r.human_factual_approval!==false||r.commercial_rights_verified!==false||
    !Number.isFinite(r.actual_seconds)||r.actual_seconds<480||r.actual_seconds>840||
    !Number.isSafeInteger(r.generated_voice_takes)||r.generated_voice_takes<1||r.generated_voice_takes>128||
    !Array.isArray(r.resolution)||r.resolution.length!==2||r.resolution.some(n=>!Number.isSafeInteger(n))||
    r.resolution[0]<1280||r.resolution[1]<720||
    r.resolution[0]<=r.resolution[1]||!Number.isFinite(r.fps)||r.fps<12||r.fps>60||
    typeof body.run_id!=='string'||!/^\d{1,20}$/.test(body.run_id))throw new RangeError('Informe de episodio inválido');
 const note=JSON.stringify({export_sha256:r.sha256,manifest_sha256:r.approved_manifest_sha256,
   seconds:r.actual_seconds,run_id:body.run_id,publication_authorized:false});
 if(!['rendering','ready'].includes(row.status))return {ok:false,status:409,reason:'render_not_active'};
 const statements=[
  db.prepare(`UPDATE jobs SET status='ready',last_error='',updated_at=datetime('now')
   WHERE id=? AND status='rendering' AND manifest_json=? AND EXISTS(
    SELECT 1 FROM editorial_dossiers WHERE job_id=? AND editor_attested=1 AND editor_name<>'')`)
   .bind(row.id,row.manifest_json,row.id),
  db.prepare(`INSERT INTO events(job_id,action,note) SELECT ?,'episode_preview_ready',?
   WHERE EXISTS(SELECT 1 FROM jobs WHERE id=? AND status='ready' AND manifest_json=?)
   AND EXISTS(SELECT 1 FROM editorial_dossiers WHERE job_id=? AND editor_attested=1 AND editor_name<>'')
   AND NOT EXISTS(SELECT 1 FROM events WHERE job_id=? AND action='episode_preview_ready')`)
   .bind(row.id,note,row.id,row.manifest_json,row.id,row.id)
 ];
 const result=await db.batch(statements);
 const saved=await db.prepare("SELECT action,note FROM events WHERE job_id=? AND action='episode_preview_ready' ORDER BY id DESC LIMIT 1").bind(row.id).first();
 const preview=saved?previewFromEvents([saved]):null;
 if(!preview||preview.sha256!==r.sha256)return {ok:false,status:409,reason:'episode_state_changed'};
 return {ok:true,reused:result[0].meta?.changes!==1,preview,automatic_publication_allowed:false};
}

export async function failEpisodeExport(db,row,runId){
 if(typeof runId!=='string'||!/^\d{1,20}$/.test(runId))throw new RangeError('Ejecución inválida');
 // Un fallo atrasado no puede revocar un resultado que ya quedó listo.
 const result=await db.batch([
  db.prepare(`UPDATE jobs SET status='failed',last_error='Revisar ejecución del episodio en GitHub Actions',
   updated_at=datetime('now') WHERE id=? AND manifest_json=? AND status IN ('queued','rendering')`)
   .bind(row.id,row.manifest_json),
  db.prepare(`INSERT INTO events(job_id,action,note) SELECT ?,'episode_failed_attempt',? WHERE changes()=1`)
   .bind(row.id,JSON.stringify({run_id:runId}))
 ]);
 return result[0].meta?.changes===1?{ok:true,automatic_publication_allowed:false}:
  {ok:false,status:409,reason:'render_not_active'};
}
