// Guion IA -> trabajo y expediente PENDIENTES. Ninguna aprobación de hechos/voz.
import {readScriptContext,validateAiReport} from './ai-research-team.mjs';
import {validateDossier} from './editorial.mjs';
import voiceReference from '../assets/voice/approved/reference.json' with {type:'json'};

const digest=async text=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(text)))]
 .map(x=>x.toString(16).padStart(2,'0')).join('');
const canonical=value=>JSON.stringify(value===null||typeof value!=='object'?value:
 Array.isArray(value)?value.map(v=>JSON.parse(canonical(v))):
 Object.fromEntries(Object.keys(value).sort().map(k=>[k,JSON.parse(canonical(value[k]))])));
const countWords=text=>(text.match(/[\p{L}\p{N}_]+/gu)||[]).length;
const primary=new Set(['public_authority_candidate','potential_official_primary','potential_official_pdf']);
const fail=message=>{throw new RangeError(message);};
const within=(v,min,max)=>typeof v==='string'&&v.trim().length>=min&&v.length<=max;
const FALSE_FLAGS=new Set(['publication_authorized','ready_for_render','factual_approval',
 'voice_license_verified','visual_rights_verified','facts_approved','rights_verified','human_verified']);

export async function evidenceLinkSha256(research){
 const fields=['id','url','document_sha256','page','excerpt','source_class'];
 return digest(canonical({wikidata_id:research.selected_wikidata_id,
  evidence:research.evidence_manifest.map(e=>Object.fromEntries(fields.map(k=>[k,e[k]??null]))),
  claims:research.candidate_claims.map(c=>({statement:c.statement,evidence_ids:c.evidence_ids}))}));
}
function noApprovals(value,depth=0){
 if(depth>12)fail('Estructura excesiva');
 if(value&&typeof value==='object')for(const [key,child] of Object.entries(value)){
  if(FALSE_FLAGS.has(key)&&child!==false)fail('El guionista no concede permisos');
  noApprovals(child,depth+1);
 }
}
function researchGate(r){
 validateAiReport(r);
 if(r.candidate_claims.length<6||!r.source_quality||r.source_quality.claim_gaps.some(g=>g.gaps.length)||
    r.reviews.length!==r.candidate_claims.length||r.reviews.some(x=>x.assessment!=='supported_by_excerpt'))
  fail('Investigación todavía insuficiente');
 const byId=new Map(r.evidence_manifest.map(e=>[e.id,e]));
 for(const [i,c] of r.candidate_claims.entries()){
  const review=r.reviews.find(row=>row.claim_index===i+1);
  if(c.evidence_ids.some(id=>!review.evidence_ids.includes(id)))fail('Citas fuera de revisión');
  const refs=c.evidence_ids.map(id=>byId.get(id));
  if(new Set(refs.map(e=>e.url)).size<2||new Set(refs.map(e=>new URL(e.url).hostname)).size<2||
     new Set(refs.map(e=>e.document_sha256)).size<2||!refs.some(e=>primary.has(e.source_class)))
   fail('Cada hecho requiere contraste y original');
 }
}
function chunks(text){
 const out=[];let active='';
 for(const word of text.split(/\s+/u)){
  if(word.length>900)fail('Palabra fuera de límite');
  const next=active?active+' '+word:word;
  if(next.length>900){out.push(active);active=word;}else active=next;
 }
 if(active)out.push(active);
 if(out.at(-1)?.length<20&&out.length>1){
  const tail=out.pop(),last=out.pop().split(' ');let moved='';
  while((moved+' '+tail).trim().length<20&&last.length>1)moved=last.pop()+(moved?' '+moved:'');
  out.push(last.join(' '),(moved+' '+tail).trim());
 }
 return out;
}

export async function prepareEditorialDraft(research,script,runId){
 researchGate(research);
 if(!script||JSON.stringify(script).length>48000)fail('Guion fuera del presupuesto');
 noApprovals(script);
 if(script.schema!=='fdg_documentary_script_v1'||script.status!=='editorial_draft_unapproved'||
    script.factual_review_required!==true||script.source_research_run_id!==runId||
    script.wikidata_id!==research.selected_wikidata_id||script.company!==research.company||
    script.source_evidence_sha256!==await evidenceLinkSha256(research)||
    !within(script.title,10,150)||!within(script.central_question,25,180)||
    !Array.isArray(script.scenes)||script.scenes.length!==research.candidate_claims.length)
  fail('Guion no corresponde al expediente activo');
 for(const flag of ['publication_authorized','ready_for_render','factual_approval',
   'voice_license_verified','visual_rights_verified'])if(script[flag]!==false)fail('Permiso inválido');
 const evidence=new Map(research.evidence_manifest.map(e=>[e.id,e]));
 const segments=[],links=[];let words=0;
 for(const [index,scene] of script.scenes.entries()){
  if(scene.scene_number!==index+1||scene.facts_approved!==false||scene.rights_verified!==false||
     !Array.isArray(scene.paragraphs)||!scene.paragraphs.length||scene.paragraphs.length>8||
     scene.start_seconds_estimated!==Math.ceil(words*60/138))fail('Escena incompleta');
  const sceneClaims=new Set();
  for(const p of scene.paragraphs){
   if(!within(p.text,40,3500)||p.human_verified!==false||!Array.isArray(p.claim_indices)||
      !p.claim_indices.length||p.claim_indices.length>8||new Set(p.claim_indices).size!==p.claim_indices.length||
      p.claim_indices.some(n=>!Number.isSafeInteger(n)||n<1||n>research.candidate_claims.length)||
      !Array.isArray(p.evidence_ids)||!p.evidence_ids.length||p.evidence_ids.length>8||
      new Set(p.evidence_ids).size!==p.evidence_ids.length||p.evidence_ids.some(id=>!evidence.has(id)))
    fail('Párrafo sin trazabilidad');
   const allowed=new Set(p.claim_indices.flatMap(n=>research.candidate_claims[n-1].evidence_ids));
   if(p.evidence_ids.some(id=>!allowed.has(id))||p.claim_indices.some(n=>
      research.candidate_claims[n-1].evidence_ids.some(id=>!p.evidence_ids.includes(id))))fail('Citas ajenas al hecho');
   p.claim_indices.forEach(n=>sceneClaims.add(n));words+=countWords(p.text);
   for(const text of chunks(p.text)){
    segments.push({headline:`${research.company.slice(0,90)} · Escena ${index+1}`,voiceover:text});
    links.push({segment:segments.length,claims:p.claim_indices});
   }
  }
  if(scene.narration_text!==scene.paragraphs.map(p=>p.text).join('\n\n')||!sceneClaims.has(index+1)||
     scene.end_seconds_estimated!==Math.ceil(words*60/138))fail('Escena alterada');
 }
 const seconds=Math.ceil(words*60/138);
 if(words!==script.narration_word_count||seconds!==script.estimated_duration_seconds||
    seconds<480||seconds>840||script.duration_is_estimate!==true||script.narration_wpm!==138||
    segments.length<2||segments.length>18)fail('Duración o segmentos fuera del contrato editorial');
 const usedIds=new Set(script.scenes.flatMap(s=>s.paragraphs.flatMap(p=>p.evidence_ids)));
 const byUrl=new Map();
 for(const id of usedIds){const e=evidence.get(id);if(!byUrl.has(e.url))byUrl.set(e.url,`S${String(byUrl.size+1).padStart(2,'0')}`);}
 const sources=[...byUrl].map(([url,id])=>({id,url,publisher:new URL(url).hostname,
  accessed_on:research.collected_on,type:[...usedIds].some(key=>evidence.get(key).url===url&&
    primary.has(evidence.get(key).source_class))?'primaria':'secundaria'}));
 const claims=[];
 for(const link of links)for(const number of link.claims){
  const c=research.candidate_claims[number-1],grouped=new Map();
  for(const id of c.evidence_ids){const e=evidence.get(id),sid=byUrl.get(e.url);
   if(!grouped.has(sid))grouped.set(sid,[]);
   grouped.get(sid).push(`${id}, ${e.page?'página '+e.page:'bloque '+((e.block_index??0)+1)}`);
  }
  claims.push({id:`C${String(claims.length+1).padStart(2,'0')}`,segment_index:link.segment,
   text:c.statement.length>=20?c.statement:research.company+': '+c.statement,
   evidence:[...grouped].map(([source_id,locators])=>({source_id,locator:locators.join('; ').slice(0,220),status:'pendiente'})),
   reviewed_by:''});
 }
 const manifest={title:script.title,angle:script.central_question,format:'long',sources:[...byUrl.keys()],segments};
 const dossier={title:script.title,thesis:script.central_question,sources,claims,
  assets:[{kind:'voz',description:'Voz canónica de Factor de Gigantes; tomas y derechos pendientes',
    reference_sha256:voiceReference.sha256,rights_status:'pendiente'},
    ...script.scenes.map(s=>({kind:'grafico',description:`Recursos originales o licenciados de escena ${s.scene_number}`,
                            rights_status:'pendiente'}))],publication_authorized:false};
 if(sources.length>20)fail('Fuentes fuera del contrato editorial');
 try{validateDossier(dossier,manifest);}catch{fail('Expediente fuera del contrato editorial');}
 return {manifest,dossier,script_sha256:await digest(canonical(script))};
}

export async function hasAutonomousOrigin(db,jobId){
 try{return Boolean(await db.prepare('SELECT job_id FROM autonomous_script_drafts WHERE job_id=?').bind(jobId).first());}
 catch(e){if(/no such table.*autonomous_script_drafts/i.test(String(e?.message||e)))return false;throw e;}
}

export async function readEditorialScriptContext(db,runId){
 const context=await readScriptContext(db,runId);
 if(!context.ok)return context;
 const previous=await db.prepare('SELECT job_id,script_json FROM autonomous_script_drafts WHERE research_run_id=?')
  .bind(context.run_id).first();
 if(previous)context.existing_script_draft={job_id:previous.job_id,script:JSON.parse(previous.script_json)};
 return context;
}

export async function storeAutonomousDraft(db,body){
 if(!body||typeof body.research_run_id!=='string'||!/^ai-[a-f0-9]{28}$/.test(body.research_run_id))fail('Falta expediente original');
 const context=await readScriptContext(db,body.research_run_id);
 if(!context.ok)return {ok:false,status:409,reason:'no_active_research',automatic_publication_allowed:false};
 const r=context.research,s=body.script;
 const bundle=await prepareEditorialDraft(r,s,body.research_run_id);
 const previous=await db.prepare('SELECT job_id,script_sha256 FROM autonomous_script_drafts WHERE research_run_id=?')
  .bind(body.research_run_id).first();
 const receipt=(jobId,created)=>({ok:true,stored_in:'d1',job_id:jobId,research_run_id:body.research_run_id,
  created,automatic_factual_approval:false,automatic_render_allowed:false,automatic_publication_allowed:false});
 if(previous)return previous.script_sha256===bundle.script_sha256?receipt(previous.job_id,false):
  {ok:false,status:409,reason:'draft_already_exists_for_research',automatic_publication_allowed:false};
 const id=crypto.randomUUID();
 await db.batch([
  db.prepare(`INSERT INTO jobs(id,title,format,status,manifest_json)
   SELECT ?,?,'long','draft',? WHERE EXISTS (SELECT 1 FROM market_research_queue
    WHERE wikidata_id=? AND state IN ('awaiting_sources','researching'))
   AND NOT EXISTS (SELECT 1 FROM autonomous_script_drafts WHERE research_run_id=?)`)
   .bind(id,bundle.manifest.title,JSON.stringify(bundle.manifest),r.selected_wikidata_id,body.research_run_id),
  db.prepare(`INSERT INTO autonomous_script_drafts(research_run_id,job_id,wikidata_id,script_sha256,source_evidence_sha256,script_json)
   SELECT ?,?,?,?,?,? WHERE EXISTS(SELECT 1 FROM jobs WHERE id=?)`)
   .bind(body.research_run_id,id,r.selected_wikidata_id,bundle.script_sha256,s.source_evidence_sha256,JSON.stringify(s),id),
  db.prepare(`INSERT INTO editorial_dossiers(job_id,dossier_json)
   SELECT ?,? WHERE EXISTS(SELECT 1 FROM jobs WHERE id=?)`).bind(id,JSON.stringify(bundle.dossier),id),
  db.prepare(`INSERT INTO events(job_id,action,note) SELECT ?,'autonomous_draft_created',?
   WHERE EXISTS(SELECT 1 FROM jobs WHERE id=?)`).bind(id,'Guion y fuentes pendientes de revisión humana',id),
  db.prepare(`UPDATE market_research_queue SET state='review',updated_at=datetime('now')
   WHERE wikidata_id=? AND state IN ('awaiting_sources','researching')
   AND EXISTS(SELECT 1 FROM autonomous_script_drafts WHERE job_id=?)`).bind(r.selected_wikidata_id,id)
 ]);
 const stored=await db.prepare('SELECT job_id,script_sha256 FROM autonomous_script_drafts WHERE research_run_id=?')
  .bind(body.research_run_id).first();
 if(!stored)return {ok:false,status:409,reason:'editorial_review_already_open',automatic_publication_allowed:false};
 return stored.script_sha256===bundle.script_sha256?receipt(stored.job_id,stored.job_id===id):
  {ok:false,status:409,reason:'draft_already_exists_for_research',automatic_publication_allowed:false};
}
